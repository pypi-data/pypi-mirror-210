import os
import zipfile
import sqlalchemy
from ..src.logger import ETLLogger as Logger
import pandas as pd
from pytz import timezone
from datetime import datetime
from typing import Union, Dict
from exergenics import exergenics
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from Levenshtein import distance as levenshtein_distance
import regex as re
import dateparser
from collections import Counter
from typing import Tuple
from functools import reduce


from dotenv import load_dotenv
load_dotenv()


EXTENSIONS = ['csv', 'xlsx']
# The length threshold of a string where we consider the string as a point name
LENGTH_THRESHOLD = 10
# The maximum distance between two timestamp column headers that are considered similar
TIMESTAMP_HEADER_DISTANCE = 4
LOG_HEADER = ['timepretty', 'observation', 'datapoint']
TIME, NAME, VALUE = LOG_HEADER
N_COLUMN_LONG_DATA = 3  # The number of columns in a long-format data table
DEFAULT_POSITION_DAY = 0  # The default position of the day of month in timestamps
SUMMARY_COLUMNS = ['count', 'mean', 'std',
                   'min', '25%', '50%', '75%', 'max']


logger = Logger(loggerName='Exergenics-ETL',
                component='python_package', subComponent='exergenics_etl')


def hello(name: str) -> None:
    """Says hello to someone.

    Args:
        name (str): The name of the person to greet.

    Returns:
        None
    """

    print(f"Hello {name}!")

    return


def create_api(environment: str, component_name: str = "") -> exergenics.ExergenicsApi:
    """Creates an authenticated Exergenics API object. Environment variables, EXERGENICS_API_USERNAME
    and EXERGENICS_API_PASSWORD, are required.

    Args:
        environment (str): The environment where the API will be used. Must be either 'staging' or 'production'.
        component_name (str, optional): The name of the component that will be using the API.

    Raises:
        ValueError: If the input environment is not ‘staging’ or ‘production’.
        RuntimeError: If the username or password for API authentication is not found in environment variables.

    Returns:
        exergenics.ExergenicsApi: An authenticated Exergenics API object.
    """

    # Validate input environment
    try:
        assert (environment == 'staging') or (environment == 'production')
    except AssertionError:
        raise ValueError(
            f"Invalid input argument: environment = {environment}")

    # Get credentials from environment variables
    api_username = os.getenv('EXERGENICS_API_USERNAME')
    api_password = os.getenv('EXERGENICS_API_PASSWORD')
    try:
        assert api_username is not None, "EXERGENICS_API_USERNAME not found in environment variables!"
        assert api_password is not None, "EXERGENICS_API_PASSWORD not found in environment variables!"
    except AssertionError as e:
        raise RuntimeError(e)

    if environment == "staging":
        production = False
    elif environment == 'production':
        production = True

    api = exergenics.ExergenicsApi(
        username=api_username, password=api_password, useProductionApi=production)
    if component_name:
        api.setComponentName(component_name)

    if not api.authenticate():
        exit(0)

    return api


def create_sql_engine(databaseName: str, host: str, user: str, password: str) -> sqlalchemy.engine.base.Engine:
    """Formats a URL using the provided credentials
    and creates a connectable MySQL database engine object based on the URL.

    Args:
        databaseName (str): The name of the MySQL database to connect to.
        host (str): The hostname of the MySQL server.
        user (str): The MySQL user to authenticate as.
        password (str): The password for the MySQL user.

    Raises:
        RuntimeError: If the password is missing

    Returns:
        sqlalchemy.engine.base.Engine: A connectable MySQL engine object.
    """

    try:
        url = f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:3306/{databaseName}"
    except TypeError:
        raise TypeError(
            f"Input password is not a string: password = {password}")
    engine = create_engine(url)

    return engine


def get_time_now() -> str:
    """Returns the current date and time in Melbourne the format 'YYYY_MM_DD_HHMM'.

    Returns:
        str: A string representing the current date and time in Melbourne.
    """
    now = datetime.now().astimezone(tz=timezone('Australia/Melbourne'))
    dt_string = now.strftime("%Y_%m_%d_%H%M")
    return dt_string


def structure_slack_message(bCode: str = "", jobId: Union[int, str] = "", message: str = "") -> str:
    """Creates a formatted Slack message string.

    Args:
        bCode (str, optional): The building code associated with the job. Defaults to "".
        jobId (Union[int, str], optional): The job ID. Defaults to "".
        message (str, optional): The message to be sent to a Slack channel. Defaults to "".

    Returns:
        str: A formatted Slack message.
    """

    return f'Time: {get_time_now()}\nBcode: {bCode}\nJob: {jobId}\n{message}'


def create_tmp_folder(tmpFolderName: str = "temp") -> None:
    """Creates a temporary folder with the given name if it does not already exist.

    Args:
        tmpFolderName (str, optional): The name of the temporary folder to create. Defaults to "temp".

    Raises:
        Exception: If the temporary folder was not successfully created.
    """

    if not os.path.exists(tmpFolderName):
        os.makedirs(tmpFolderName)

    try:
        assert os.path.exists(tmpFolderName)
    except AssertionError as e:
        raise Exception(
            f"temp folder doesn't not existing after attempting to make the directory: {e}")

    return


def generate_CSV_name(pointName: str) -> str:
    """Generates a CSV name for the trend log of a given data point name.

    Args:
        pointName (str): The name of a data point

    Returns:
        str: The CSV name for the data point
    """

    # Follow logic from portal-php code to rename file names
    pointName = pointName.replace(" ", "_").replace(
        "/", "-").replace("~", "-").replace("&", "and").replace("%", "-")
    return f'{pointName}.csv'


def strftime_for_NaT(timestamp: Union[pd.Timestamp, pd._libs.tslibs.nattype.NaTType], log_time_format: str = "%d/%m/%Y %H:%M") -> str:
    """Formats a pandas Timestamp object as a string in the specified format.
    Returns an empty string if the type of the timestamp is pandas.NaT.

    Args:
        timestamp (Union[pd.Timestamp, pd._libs.tslibs.nattype.NaTType]: A pandas Timestamp object to format.
        log_time_format (str, optional): the format of the output timestamp string. Defaults to "%d/%m/%Y %H:%M".

    Returns:
        str: A formatted string representing the provided timestamp or an empty string if the timestamp is pandas.NaT.
    """

    if timestamp is pd.NaT:
        return ""
    else:
        try:
            return timestamp.strftime(log_time_format)
        except AttributeError as e:
            raise AttributeError(
                f'Cannot convert this timestamp to its equivalent string: timestamp = {timestamp}, {e}')


def generate_one_manifest_row(pointName: str, dfLog: pd.DataFrame) -> Dict:
    """Generates manifest data for a data point from its trend log.

    Args:
        pointName (str): The name of the data point.
        dfLog (pd.DataFrame): A pandas DataFrame containing the trend log for the data point.

    Returns:
        Dict: A dictionary of manifest data for the data point.
    """

    # Get start/end time for the trend log of the point
    startTime = dfLog[TIME].min()
    endTime = dfLog[TIME].max()

    # Generate manifest fields for the data point
    fileField = generate_CSV_name(pointName)
    rowsField = len(dfLog)
    intervalField = calculate_time_interval(dfLog[TIME])
    fromField, toField, dataFromField, dataToField = [
        strftime_for_NaT(t) for t in [startTime, endTime, startTime, endTime]]

    # Format manifest fields into a dictionary
    metadataDict = {"point": pointName,
                    "file": fileField,
                    "rows": rowsField,
                    "from": fromField,
                    "to": toField,
                    "dataFrom": dataFromField,
                    "dataTo": dataToField,
                    "interval": intervalField}

    return metadataDict


def generate_output_file_path(module: str, extension: str, bCode: str = "", pCode: str = "", category: str = "", jobId: Union[int, str] = "", path: str = "") -> str:
    """Generates a local file path for an output file.

    Args:
        module (str): The name of the module generating the output file, such as, transformation or preheader.
        extension (str): The file extension of the output file.
        bCode (str, optional): The building code associated with the file. Defaults to "".
        pCode (str, optional): The plant code associated with the file. Defaults to "".
        category (str, optional): The category of the output file, such as, zipfile or manifest. Defaults to "".
        jobId (Union[int, str], optional): The job ID associated with the output file. Defaults to "".
        path (str, optional): The directory path where the output file should be saved. Defaults to "".

    Returns:
        str: The file path for the output file.
    """

    # Format individual parts of the output file path string
    timeNow = get_time_now()
    if category:
        category = "_" + category
    if bCode:
        bCode = "_" + bCode
    if pCode:
        pCode = "_" + pCode
    if jobId:
        jobId = "_job" + str(jobId)

    outputFilePath = f"{timeNow}{bCode}{pCode}{jobId}_{module}{category}.{extension}"

    # Append the file path to the end of the directory path if the directory path is provided
    if path:
        if path.endswith('/'):
            outputFilePath = f"{path}{outputFilePath}"
        else:
            outputFilePath = f"{path}/{outputFilePath}"

    return outputFilePath


def get_file_name_list(zf: zipfile.ZipFile) -> list:
    """Open manual zipfile and return a list of unique data files

    Args:
        zf (zipfile.ZipFile): ZipFile object containing CSVs.

    Returns:
        list: A list of file names in the zipfile object input. 
    """

    logger = Logger()

    filesIncluded = [j for extension in EXTENSIONS for j in zf.namelist()
                     if j.endswith(extension) and
                     not j.startswith('__MACOSX') and
                     not ('/~' in j)]

    filesExcluded = list(set(zf.namelist()) - set(filesIncluded))

    logger.info(
        f'Reading {len(filesIncluded)} data files from manual zipfile: {filesIncluded}\n')
    if filesExcluded:
        logger.info(
            f'{len(filesExcluded)} data files in manual zipfile NOT included: {filesExcluded}\n')

    return filesIncluded


class SkipRowsMachine:
    """
    A class to provide automated header rows skipping for Pandas Dataframe.
    Skip non-data rows on top of data files in the format of CSV or Excel.
    """

    def __init__(self, nRowsVerify: int = 10):
        """Constructs all the necessary attributes for the SkipRowsMachine object.

        Args:
            nRowsVerify (int, optional): Numbers of rows to verify in each CSV. Defaults to 10.
        """
        self.logger = Logger()
        self.skiprows = None
        self.nRowsVerify = nRowsVerify

    def validate_headers(self, df0: pd.DataFrame):
        """This function validates the value of skiprows by checking the types of header.
        A header should be a non-nan string only, ideally with a length greater than 5,
        and not a string of numbers.

        Args:
            df0 (pd.DataFrame): Pandas DataFrame for header validation.

        Raises:
            AttributeError: Headers containing numbers cannot be skipped.
        """

        # Drop rows with NA in timestamps (the 1st column)
        df = df0[~pd.isna(df0[df0.columns[0]])]

        # Get all headers
        headers = df.iloc[0]

        # Validate each header
        for v in headers:

            try:
                # Check header is a string but not a string of numbers
                pd.to_numeric(v)
                errorMessage = f"Test Failed: Can do to_numeric on header: {v} of type {type(v)}; \
                    the header can't be numbers, a string of numbers, an empty string, None, np.nan or boolean."
                self.logger.error(errorMessage)
                raise AttributeError(errorMessage)

            except ValueError as e:
                pass

            try:
                assert len(v) > 5, f'Expected the length of header to be ideally greater than 5 \
                    but the actual length of header "{v}" was {len(v)}'
            except AssertionError as e:
                self.logger.warn(e)

        self.logger.info(f'1st verification passed ...')

        return

    def _auto_skiprows_csv(self, fileName: str, zf: zipfile.ZipFile) -> Tuple[pd.DataFrame, int, int]:
        """
        Reads a CSV file from a zip file object and 
        returns a Pandas dataframe, header row index, 
        and number of rows to skip from the beginning of the file.

        Args:
            filepath (str): Absolute path of the CSV file to apply skip rows.
            zf (zipfile.ZipFile): Zipped folder where the file is.

        Returns:
            tuple (pd.DataFrame, int, int): Return a dataframe of the input 
            filepath with rows skipped and header row ID if verification passed and None otherwise.
        """

        # Try reading the file with different numbers of rows to skip
        skiprowsTrials = range(10)

        for skiprowsTrial in skiprowsTrials:
            try:
                # Try reading the CSV file with the current number of rows to skip
                df = pd.read_csv(zf.open(fileName),
                                 skiprows=skiprowsTrial, header=None)
                skiprows = skiprowsTrial
                headerRowID = 0

                self.logger.info(
                    f'Found skiprows value = {skiprowsTrial}')
                return df, skiprows, headerRowID

            except:
                continue

        errorMessage = f"Table in data file should start at the first 10 rows. Faulty file: {fileName}."
        self.logger.error(errorMessage)
        raise Exception(errorMessage)

    def _auto_skiprows_excel(self, fileName: str, zf: zipfile.ZipFile) -> Tuple[pd.DataFrame, int, int]:
        """Skip rows before headers for DataFrame read from an Excel sheet.
        Assume redundant stuffs in excel sheets are in the first column above timestamps.
        That is, the header of a data point is the first non-NA string in that column.
        Verify after skipping rows.

        Args:
            filepath (str): Absolute path of the Excel file to apply skip rows.
            zf (zipfile.ZipFile): Zipped folder where the file is.

        Returns:
            tuple (pd.DataFrame, int): Return a dataframe of the input 
            filepath with rows skipped and header row ID if verification passed and None otherwise.
        """
        df = pd.read_excel(zf.open(fileName), index_col=False, header=None)

        # Find the row ID of header and compute the number of rows to skip
        col1 = df[df.columns[1]]
        headerRowID = col1.dropna().index[0]
        skiprows = headerRowID

        # Skip rows
        df.drop(labels=range(skiprows), inplace=True)

        self.logger.info(f'Found skiprows = {skiprows}')

        return df, skiprows, headerRowID

    def read(self, fileName: str, zf: zipfile.ZipFile = None) -> pd.DataFrame:
        """Reads a data file from a zipped folder while skipping non-data rows on top of the file.

        Args:
            fileName (str): File name of the file to apply skip rows.
            zf (zipfile.ZipFile): Zipped folder where the file is.

        Returns:
            pd.DataFrame: Pandas DataFrame of the input CSV file with skipped rows.  
        """

        # Get the filename extension of the current data file
        extension = [
            extension for extension in EXTENSIONS if fileName.endswith(extension)][0]

        if self.skiprows is None:
            # Find skiprows value to read the data file
            if extension == 'xlsx':
                df, self.skiprows, headerRowId = self._auto_skiprows_excel(fileName, zf)
            elif extension == 'csv':
                df, self.skiprows, headerRowId = self._auto_skiprows_csv(fileName, zf)

        else:
            # Read the data file with the last skiprows value
            if extension == 'csv':
                df = pd.read_csv(zf.open(fileName), skiprows=self.skiprows, header=None)
            elif extension == 'xlsx':
                df = pd.read_excel(zf.open(fileName), skiprows=self.skiprows, header=None)
            
            headerRowId = 0

        # Validate that headers are strings
        self.validate_headers(df)

        # Set header as column names
        df.columns = df.loc[headerRowId].values

        # Remove headers from values
        df.drop(labels=headerRowId, inplace=True)
        df.reset_index(inplace=True, drop=True)  # Replace and reset index

        return df


def convertable_to_float(string: str) -> bool:
    """Checks if a given string can be converted to a float.

    Args:
        string (str): The input string to be checked.

    Returns:
        bool: True if the string can be converted to a float, False otherwise.
    """
    try:
        result = float(string)
        return True
    except ValueError:
        return False
    

class InputValidation:
    """A class to provide automated validation for CSV files.
    """

    def __init__(self, validTimestampHeaders: list, genericColumnHeaders: list):
        """Constructs all the necessary attributes for the InputValidation object.

        Args:
            validTimestampHeaders (list): A list of valid format for timestamp column. 
            genericColumnHeaders (list): A list of generic column header names. 
        """
        self.validTimestampHeaders = validTimestampHeaders
        self.genericColumnHeaders = genericColumnHeaders

    def _validate_timestamp_column_header(self, df: pd.DataFrame) -> bool:
        """Assuming the first column is always timestamps,
        validate auto skiprows by checking if the first header is a valid header for timestamps.

        Raises:
            AssertionError: Cannot find exact match for the timestamp column header.

        Returns:
            bool: True if timestamp is in a correct format. 
        """

        logger = Logger()

        timestampHeader = df.columns[0]

        try:
            assert timestampHeader.lower() in self.validTimestampHeaders
        except AssertionError as e:
            logger.warn(
                f"Cannot find exact match for this timestamp column header: {timestampHeader}.")

            try:
                # Check if the timestamp column header of the current df is similar to any valid timestamp headers
                msg = f"Cannot recognise this timestamp column header: {timestampHeader}. Either auto-skiprows is broken, or we should add this one into Column Header tree."
                assert min([levenshtein_distance(timestampHeader.lower(), validTimestampHeader)
                            for validTimestampHeader in self.validTimestampHeaders]) <= TIMESTAMP_HEADER_DISTANCE, msg
            except AssertionError as e:
                logger.error(
                    f"Cannot find similar match for this timestamp column header: {timestampHeader}.")
                raise AssertionError(e)

        logger.info(
            'Verifying timestamp column header ... Timestamp header is VALID!')
        return True

    def _check_for_wide_format(self, df: pd.DataFrame) -> bool:
        """Method check whether input file is in a wide format.

        Args:
            df (pd.DataFrame): Pandas DataFrame to apply format checking on. 

        Returns:
            bool: True if input is in a wide format.
        """

        # If there are only 3 columns in this data file
        if df.shape[1] == N_COLUMN_LONG_DATA:

            # If none of the values in the 2nd column can be converted to float
            col2 = df[df.columns[1]]
            if not any(col2.apply(convertable_to_float)):

                # If the average length of the strings in the 2nd column is longer than 10
                if col2.apply(lambda x: len(x)).mean() > LENGTH_THRESHOLD:
                    return False  # We think this is a wide format dataset

        return True

    def check_input_dataframe(self, df: pd.DataFrame) -> bool:
        """Validate the format of a dataframe read from a data file.

        Args:
            df (pd.DataFrame): Pandas DataFrame to validate timestamp and 
            wide format. 

        Raises:
            AssertionError: If any validation failed.
            Exception: For unknown errors.

        Returns:
            bool: True if all validations are passed.
        """

        logger = Logger()

        try:
            self._validate_timestamp_column_header(df)
            assert self._check_for_wide_format(
                df), 'This data file looks like in a long format. PreMerged can only accept datasets in a wide format.'
        except AssertionError as e:
            raise AssertionError(e)
        except Exception as e:
            msg = f'Unknown error: {e}'
            logger.error(msg)
            raise Exception(msg)

        return True

    def check_for_generic_header(self, pointName: str, dfSameName: pd.DataFrame, dfNew: pd.DataFrame) -> bool:
        """Check if the point name of a dataframe is from a generic header
        by comparing the time intervals (i.e. the modes of timestamp gaps)
        of the dataframes before and after concatenation.
        If two dataframes of the same point have the same time interval,
        the concatenation of the two should have the same time interval
        as before. Concatenating two dataframes of two points with the same header
        will result in a drop in time interval.

        Args:
            pointName (str): Point name to verify whether it is a generic header.
            dfSameName (pd.DataFrame): Pandas Dataframe in a long format containing values that have the same 
                column header in the original data file as dfNew.
            dfNew (pd.DataFrame): Pandas Dataframe in a long format containing values that have the same 
                column header in the original data file as dfSameName.

        Raises:
            AssertionError: If the point name is considered generic.

        Returns:
            bool: False if the point name is not considered generic.
        """

        logger = Logger()

        # Check if this is a generic column header we have seen before
        assert pointName.lower(
        ) not in self.genericColumnHeaders, f'A generic column header found: "{pointName}"'

        # Check if this could be a generic column header we haven't seen before
        if len(pointName) <= LENGTH_THRESHOLD:

            msg = f'This point name has a length less than 10, which is possibly not a valid point name: "{pointName}"'
            logger.warn(msg)

            # If values are recorded in a similar behaviour in terms of time interval
            oldTimeInterval = calculate_time_interval(dfSameName[TIME])
            newTimeInterval = calculate_time_interval(dfNew[TIME])
            if oldTimeInterval == newTimeInterval:

                # Concatenate the two dataframes with the same point name
                dfConcat = pd.concat([dfSameName, dfNew],
                                     axis=0, ignore_index=True)
                dfConcat.drop_duplicates(inplace=True, ignore_index=True)

                # Check for a drop in time interval
                timeIntervalAfterConcat = calculate_time_interval(
                    dfConcat[TIME])
                if timeIntervalAfterConcat < oldTimeInterval:
                    msg = f'It\'s likely that there are two different points sharing the same column header: "{pointName}".'
                    logger.error(
                        f"{msg} because the time interval dropped after concatenating two dataframes.")
                    raise AssertionError(msg)

        return False


def calculate_time_interval(dtSeries: pd.Series) -> str:
    """Calculate the time interval of a datetime series.

    Args:
        dtSeries (pandas.Series): A pandas series of datetime objects.

    Returns:
        str: A string representing the time interval in minutes, or an empty string
            when there are less than 2 valid datetime objects.
    """

    # Cannot calculate time interval when there are less than 2 non-NA datetimes; return empty string
    if (~dtSeries.isna()).sum() < 2:
        return ''

    else:
        dtSeriesSorted = dtSeries.sort_values(
            ascending=True, ignore_index=True)
        return str(int(dtSeriesSorted.diff().mode()[0].total_seconds()/60))


class DatetimeParser():
    """A class to parse a Panda Series of timestamp strings. 
    """

    def __init__(self, nTests=100):
        """Constructs all the necessary attributes for the DatetimeParser object.

        Args:
            nTests (int, optional): The number of timestamp strings used to find the year position. Defaults to 100.
        """
        self.logger = Logger()
        self.dtSeriesTemp = None
        self.positionYear = None
        self.positionDay = None
        self.isShortYear = False  # Whether 2-digit year is used
        self.nTests = nTests
        self.containsTimeZone = False
        self.dtFinalFormat = None

        # define the bricks
        self.bricks = re.compile(r"""
                (?(DEFINE)
                    (?P<year_def>[12]\d{3}) # 1 or 2 then followed by 3 digits
                    # (?P<year_short_def>\d{2})  
                    (?P<month_def>January|February|March|April|May|June|
                    July|August|September|October|November|December)
                    (?P<month_short_def>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)
                    (?P<month_dec_def>(0?[1-9]|1[012]))  # 01, 1, 12 but not 13
                    (?P<day_def>(?:0[1-9]|[1-9]|[12][0-9]|3[01]))
                    (?P<weekday_def>(?:Mon|Tue|Wednes|Thurs|Fri|Satur|Sun)day)
                    (?P<weekday_short_def>Mon|Tue|Wed|Thu|Fri|Sat|Sun)
                    (?P<hms_def>T?\d{1,2}:\d{2}:\d{2}) # 03:20:10 or 3:20:10
                    (?P<hmsf_def>T?\d{1,2}:\d{2}:\d{2}.\d{1,6})
                    (?P<hm_def>T?\d{1,2}:\d{2})  # T13:20 or 13:20
                    (?P<delim_def>([-/, ]+|(?<=\d|^)T))
                    (?P<ampm_def>am|pm|AM|PM)
                    (?P<timezone_def>[+-]\d{4}) # +HHMM or -HHMM
                    # TODO: complie time zone format +HH:MM and -HH:MM, e.g. -08:00
                    (?P<timezone_name_def>UTC|EST|AEST|AEDT|NZDT|NZST) # TODO: timezone names & Z
                )

                (?P<hmsf>^(?&hmsf_def)$)|(?P<hms>^(?&hms_def)$)|(?P<hm>^(?&hm_def)$)|(?P<year>^(?&year_def)$)|(?P<month>^(?&month_def)$)|
                (?P<month_short>^(?&month_short_def)$)|(?P<month_dec>^(?&month_dec_def)$)|(?P<day>^(?&day_def)$)|
                (?P<weekday>^(?&weekday_def)$)|(?P<weekday_short>^(?&weekday_short_def)$)|(?P<delim>^(?&delim_def)$)|
                (?P<ampm>^(?&ampm_def)$)|(?P<timezone>^(?&timezone_def)$)|(?P<timezone_name>^(?&timezone_name_def)$)
                #|(?P<year_short>^(?&year_short_def)$)|(?P<ms>^(?&ms_def)$)
                """, re.VERBOSE)
        # delim
        self.delim = re.compile(r'([-/, ]+|(?<=\d)T)')

        # formats
        self.formats = {'year': '%Y', 'year_short': '%y', 'month': '%B', 'month_dec': '%m', 'day': '%d', 'weekday': '%A',
                        'hms': '%H:%M:%S', 'hmsf': '%H:%M:%S.%f',
                        'hms_12': '%I:%M:%S', 'hmsf_12': '%I:%M:%S.%f',
                        'hm_12': '%I:%M',
                        'weekday_short': '%a', 'month_short': '%b', 'hm': '%H:%M', 'delim': '',
                        'ampm': '%p', 'timezone': '%z', 'timezone_name': '%Z'}

    def _find_short_year_position(self, dtSeries: pd.Series) -> None:
        """ 
        Find the position of year with or without century 
        based on a series of timestamps. 

        Args:
            dtSeries (pd.Series): Pandas Series containing timestamp strings.

        Returns:
            None
        """

        # SELECT self.nTests timestamps from dtSeries as test cases
        if len(dtSeries) > self.nTests:
            dtTests = dtSeries.sample(n=self.nTests, replace=False)
        else:
            dtTests = dtSeries.copy(deep=True)

        # PARSE the selected timestamps with a magic datetime parser
        dtObjectsTests = dtTests.apply(lambda x: dateparser.parse(str(x)))

        # CONCATENATE the output datetime objects and the original datetime strings into a DataFrame
        dtDf = pd.DataFrame(
            {'Dt Strings': dtTests.astype(str), 'Dt Objects': dtObjectsTests})

        # CREATE a list, positionsShortYears to store positions of short years
        positionsYears = []

        # FOR each datetime object
        for idx in dtDf.index:
            # FIXME: catch None and return errors
            if dtDf.loc[idx]["Dt Objects"] is None:
                self.logger.warn(
                    f"Returned object for {dtDf.loc[idx]['Dt Strings']} is {dtDf.loc[idx]['Dt Objects']}.")
                continue

            # GET its year
            year = str(dtDf.loc[idx]["Dt Objects"].year)

            # SET the last two digits of year as shortYear
            shortYear = str(year)[-2:]

            # SPLIT the corresponding datetime string into chunks of strings by delimiters into a list
            dateParts = self.delim.split(dtDf.loc[idx]['Dt Strings'])

            # GET the position of year in the list
            positions = [i for i, x in enumerate(dateParts) if x == year]

            # If year is not found
            if not positions:

                # GET the position of shortYear in the list
                positions = [i for i, x in enumerate(
                    dateParts) if x == shortYear]

                if not positions:
                    errorMessage = "Can't find year position!"
                    self.logger.warn(errorMessage)
                    raise Exception(errorMessage)

                else:
                    self.isShortYear = True

            # STORE the position to list positionsShortYears
            positionsYears += positions

        # TODO: Check the number of year positions found

        # GET the most common position of short year
        if positionsYears:
            countPositionsYears = Counter(positionsYears)
            self.positionYear = sorted(countPositionsYears.items(),
                                       key=lambda item: item[1], reverse=True)[0][0]
        else:
            errorMessage = f"Cannot find where the position of year is."
            self.logger.error(errorMessage)
            raise AttributeError(errorMessage)

        return

    def _find_day_position(self, dtSeries: pd.Series) -> int:
        """Find 50 timestamps with day > 12 as test cases and
        find the position of day.

        Args:
            dtSeries (pd.Series): Panda Series containing timestamp strings

        Returns:
            int: Position of Day in timestamp
        """
        # CREATE a list, positionsShortYears to store positions of day
        positionsDays = []

        # FIXME: when we can't day >= 12, get the max value of; make it fail if max <= 12!!
        nRuns = 0  # Count the times running the while loop
        maxRuns = len(dtSeries)

        while len(positionsDays) < 50 and nRuns < 200:
            nRuns += 1

            # SELECT 1 timestamp from dtSeries as test case randomly
            dtTest = dtSeries.sample().values[0]

            # PARSE the selected timestamp with a magic datetime parser
            # dtObjectTest = parser.parse(dtTest)
            dtObjectTest = dateparser.parse(str(dtTest))

            day = dtObjectTest.day

            # Don't use timestamps with day <= 12
            if day <= 12:
                continue
            else:
                day = str(day)

            # SPLIT the corresponding datetime string into chunks of strings by delimiters into a list
            dateParts = self.delim.split(str(dtTest))

            # GET the position of day in the list
            positions = [i for i, x in enumerate(dateParts) if x == day]

            # STORE the position to list positionsDays
            positionsDays += positions

        # GET the most common position of year
        if positionsDays:
            countPositionsDays = Counter(positionsDays)
            self.positionDay = sorted(countPositionsDays.items(),
                                      key=lambda item: item[1], reverse=True)[0][0]
        else:
            self.logger.warn(
                f"Not enough timestamps to tell where the position of day is. Setting it to DEFAULT_POSITION_DAY = {DEFAULT_POSITION_DAY}")
            self.positionDay = DEFAULT_POSITION_DAY

        return self.positionDay

    def _correct_format_code_for_AMPM(self, formatCodeList) -> list:
        """
        Correct and replace format code %H with %I if AM/PM is in timestamps.
        """

        if self.formats['ampm'] in formatCodeList:
            # REPLACE %H with %I if %p in format
            try:
                formatCodeList[formatCodeList.index(
                    self.formats['hms'])] = self.formats['hms_12']
            except ValueError:
                try:
                    formatCodeList[formatCodeList.index(
                        self.formats['hm'])] = self.formats['hm_12']
                except ValueError:
                    try:
                        formatCodeList[formatCodeList.index(
                            self.formats['hmsf'])] = self.formats['hmsf_12']
                    except ValueError:
                        errorMessage = 'AM/PM in timestamp but cannot find time!'
                        self.logger.warn(errorMessage)
                        raise ValueError(errorMessage)

        return formatCodeList

    def _guess_one_format(self, datestring: str) -> str:
        """ Guess and return the timestamp format for a timestamp string. 

        Args:
            datestring (str): Input datetime string to identify format.

        Returns:
            str: Identified format of the input datestring.
        """

        # Break timestamp string into parts
        parts = self.delim.split(str(datestring))

        out = []

        # Iterate over the parts and try to match them to a known date brick
        for index, part in enumerate(parts):

            # IF index is equal to positionYear THEN
            if index == self.positionYear:

                # IF short year is in the datestring
                if self.isShortYear:

                    # APPEND the format code of short year to out
                    out.append(self.formats['year_short'])

                # IF long year is in the datestring THEN
                else:

                    # APPEND the format code of long year to out
                    out.append(self.formats['year'])

            # ELSE IF index is equal to positionDay THEN
            elif index == self.positionDay:

                # APPEND the format code of day to out
                out.append(self.formats['day'])

            else:

                # ELSE search for regex brick for the current timestamp part

                # Use the bricks regex to search for a brick in the part
                try:
                    brick = dict(
                        filter(lambda x: x[1] is not None, self.bricks.match(part).groupdict().items()))

                    # Get the key for the first brick found in the part; FIXME: GET all the matching bricks instead, e.g. %m & %d
                    key = next(iter(brick))

                    item = part if key == 'delim' else self.formats[key]

                    # Append the format code for the current timestamp part to output
                    out.append(item)

                except AttributeError:
                    errorMessage = f"Can't find a time part regex brick that matches with {part}"
                    self.logger.error(errorMessage)
                    raise AttributeError(errorMessage)

        out = self._correct_format_code_for_AMPM(out)

        # Check and filter out time zone from datetime format code
        out = self._check_and_remove_time_zone(parts, out)

        return "".join(out)

    def _find_final_format(self, dtSeries: pd.Series) -> str:
        """Get the format for the whole timestamp series. 

        Args:
            dtSeries (pd.Series): Pandas Series containing timestamp strings.

        Raises:
            AttributeError: Unable to find datetime format.

        Returns:
            str: Most common time format as a string.
        """

        # FIND the most common format
        # FIND the positions of year and day
        try:
            self._find_short_year_position(dtSeries)
            self._find_day_position(dtSeries)
        except Exception as e:
            self.logger.error(e)
            raise e

        # SELECT self.nTests timestamps randomly as tests to find the format
        dtTests = dtSeries.sample(n=self.nTests, replace=True)
        try:
            dtFormats = dtTests.apply(lambda x: self._guess_one_format(x))
        except Exception as e:
            errorMessage = f"Finding datetime format failed: {e}"
            self.logger.error(errorMessage)
            raise AttributeError(errorMessage)

        countPossibleFormats = Counter(dtFormats)

        # SAVE the most common format
        self.dtFinalFormat = sorted(countPossibleFormats.items(),
                                    key=lambda item: item[1], reverse=True)[0][0]
        self.logger.info(
            f'Datetime format found: {self.dtFinalFormat}')

        # RETURN the most common format as a string
        return self.dtFinalFormat

    def _check_and_remove_time_zone(self, dateParts: list, out: str) -> str:
        """Check if time zones exist in timestamps. 

        Args:
            dateParts (list): List of date parts.
            out (str): Datetime format code. 

        Returns:
            str: Datetime format code without time zones.
        """

        # Try removing format code for time zones
        try:
            out.remove(self.formats['timezone'])
            self.containsTimeZone = True

        except ValueError:
            try:
                out.remove(self.formats['timezone_name'])
                self.containsTimeZone = True

            except:

                # Try another way to check if time zones exist
                if (len(dateParts[-1]) >= 3 and dateParts[-1].isalpha()):
                    self.containsTimeZone = True
                    self.logger.warn(
                        f'Possible time zone exists but not aligned with the format of %Z or %z: {dateParts}. The containsTimeZone flag set as True')

        return out

    def parse(self, dtSeries: pd.Series) -> pd.Series:
        """Parse input datetime string.

        Args:
            dtSeries (pd.Series): Pandas Seires of Datetime string to apply parsing.

        Raises:
            Exception: Failed datetime parsing.

        Returns:
            pd.Series: Panda Series of parsed datetime objects.
        """
        self.dtSeriesTemp = dtSeries
        self.logger.info(
            f'Showing the first and the last 2 of the timestamps BEFORE parsing: \n{pd.concat([self.dtSeriesTemp.head(2), self.dtSeriesTemp.tail(2)])}')

        # FIND the format
        if self.dtFinalFormat is None:
            self._find_final_format(self.dtSeriesTemp)
        else:
            self.logger.info(
                f'Datetime format has been found before: {self.dtFinalFormat}')

        # PARSE the whole timestamp series using the format found by self._find_final_format()
        try:
            # Try exact match to test the algo
            dtObjects = pd.to_datetime(
                self.dtSeriesTemp, format=self.dtFinalFormat, exact=(not self.containsTimeZone))

        except Exception as e:
            self.logger.warn(f'Parsing failed: {e}')
            try:
                self.logger.warn('Redo finding format ...')

                # Reset variables
                self.positionYear = None
                self.positionDay = None
                self.isShortYear = False
                self.containsTimeZone = False

                self._find_final_format(self.dtSeriesTemp)
                dtObjects = pd.to_datetime(
                    self.dtSeriesTemp, format=self.dtFinalFormat, exact=(not self.containsTimeZone))
                self.logger.info('Second Parsing done')
            except Exception as e:
                errorMessage = f'Second parsing failed: {e}'
                self.logger.error(errorMessage)
                raise Exception(errorMessage)

        # TODO: Check that the numbers of NaN in dtSeries and dtObjects are the same

        if self.containsTimeZone:
            self.logger.warn('Timestamps contain time zones!')

        # RETURN a pd.Series of datetime objects
        self.logger.info(
            f'Showing the first and the last 2 of the timestamps AFTER parsing: \n{pd.concat([dtObjects.head(2), dtObjects.tail(2)])}')

        return dtObjects


def transform_columns_to_long_dataframes(wideDf: pd.DataFrame, filesWithNanColumn: set, fileName: str) -> Tuple[dict, set]:
    """Transform each column in the input dataframe to a new dataframe in long format.

    Args:
        wideDf (pd.DataFrame): Pandas Dataframe of a dataset with wide format.
        filesWithNanColumn (set): Set of files with NaN column.
        fileName (str): Absolute file path of dataset to be processed.

    Returns:
        Tuple[dict, set]: Dictionary of the new dataframe(s) and a set of files with NaN column.
    """

    dfDictFile = {}

    # Loop through all columns (point values) except the first column (where the timestamps should be)
    for point in wideDf.columns[1:]:

        # Get all non-na values for selected column as temp dataframe
        tempDf = wideDf[wideDf[point].notna()][[TIME, point]].rename(
            columns={point: VALUE})

        # Log the file name if the whole column is NaN
        if not wideDf[point].notna().any():
            filesWithNanColumn.add(fileName)

        # Rename and reorder to fit raw data format
        tempDf[NAME] = point  # point for every row
        tempDf = tempDf[LOG_HEADER]  # Reorder the columns

        tempDf.sort_values(TIME, inplace=True, ignore_index=True)

        assert point not in dfDictFile.keys(), f'Duplicate column header in a single data file.'
        dfDictFile[point] = tempDf

    return dfDictFile, filesWithNanColumn


def get_point_summary(point: str, df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary statistics of a point based on its trend log.

    Args:
        point (str): Point name of the data.
        df (pd.DataFrame): Trend log of the point.

    Returns:
        pd.DataFrame: Summary statistics of the given trend log.
    """

    logger = Logger()

    try:

        # Reformat and transform data
        dfNew = df.rename(columns={'datapoint': point})
        dfNew[point] = pd.to_numeric(dfNew[point], errors='coerce')

        # Calculate statistics
        df_summary = dfNew[[point]].describe()
        # df_summary.loc['count'] = df[point].gt(0).sum()
        df_summary = df_summary.transpose().round(3)

        # Drop columns that are not in SUMMARY_COLUMNS
        df_summary = df_summary[df_summary.columns.intersection(
            SUMMARY_COLUMNS)]

        # Replace pd.NaN with empty string
        df_summary.fillna(value="", inplace=True)

    except Exception as e:
        df_summary = pd.DataFrame(
            data={j: "" for j in SUMMARY_COLUMNS}, index=[point])
        msg = f"Exception occurred: {e}. Added empty strings as summary statistics instead."
        logger.warn(msg)

    return df_summary


def get_statistical_summary(dfDict: dict) -> pd.DataFrame:
    """Generate a summary statistics table for the dataframe(s) in the input dictionary.

    Args:
        dfDict (dict): Dictionary of dataframe(s).

    Raises:
        Exception: For unknown errors.

    Returns:
        pd.DataFrame: A summary statistics table.
    """

    logger = Logger()

    try:
        summaryList = []
        for point, df in dfDict.items():
            pointSummary = get_point_summary(point, df)
            summaryList.append(pointSummary)

        statSummaryDf = pd.concat(summaryList)

        # Replace pd.NaN with empty string
        statSummaryDf.fillna(value="", inplace=True)

    except Exception as e:
        msg = f'Unknown error: {e}'
        logger.error(msg)
        raise Exception(msg)

    return statSummaryDf


def merge_long_dataframes(dfList: list, freq: int) -> pd.DataFrame:
    """Merge a list of long dataframes to wide format after rounding timestamp for a given time interval

    Args:
        dfList (list): A list of pandas DataFrames containing the trend log. (length upto 100)
        freq (int): Value of given time interval.

    Returns:
        pd.DataFrame: A wide format pandas DataFrame.
    """
    # Error out if one of dataframe in the list is not a valid long format
    for tmpDf in dfList:
        if len(tmpDf.columns) != 3:
            raise ValueError(
                f'Invalid header length of {len(tmpDf)} in input dataframe')

    # Concat all dataframes in list and rename columns
    df = pd.concat(dfList, ignore_index=True, copy=False)
    df.columns = ['Timestamp', 'Description', 'Value']

    # Round timestamp for given time interval
    df['Timestamp'] = pd.to_datetime(
        df['Timestamp'], format='%d/%m/%Y %H:%M')
    df['Timestamp'] = df['Timestamp'].dt.round(f'{freq}min')

    # Sort data by timestamp and ignore non-numeric data
    df.sort_values('Timestamp', inplace=True)
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

    # Make log data into wide format (pivot table)
    df = pd.pivot_table(df, index='Timestamp',
                        columns='Description', values='Value')
    df.reset_index(inplace=True)

    return df


def merge_wide_dataframes(dfList: list) -> pd.DataFrame:
    """Merge a list of wide dataframes to a big final merged dataframe
    Args:
        dfList (list): A list of wide dataframes needed to be merged.

    Returns:
        pd.DataFrame: A wide format pandas DataFrame.
    """
    # Error out if Timestamp is not in header of any dataframe in the list
    for tmpDf in dfList:
        if 'Timestamp' not in tmpDf.columns:
            raise ValueError(
                f'Could not find Timestamp columns in dataframe, first column named as {tmpDf.columns[0]}')

    # Iterate merge process
    df = reduce(lambda df1, df2: pd.merge(
        df1, df2, on='Timestamp', how='outer'), dfList)

    # Sort columns alphabetically and sort rows by timestamp
    df = df[['Timestamp']+sorted(df.columns[1:])]
    df.sort_values('Timestamp', ignore_index=True, inplace=True)

    return df


def save_file_to_portal(api: exergenics.ExergenicsApi, filePath: str, jobId: Union[int, str],  nodeName: str, removeFile: bool = True) -> str:
    """Upload a local file to s3 and save it to jobData in Exergenics portal.

    Args:
        api (exergenics.ExergenicsApi): Exergenics Api object
        filePath (str): A local path for file needed to be uploaded
        jobId (int): The Id of selected job
        nodeName (str): The name of node in jobData
        removeFile (bool, optional): Remove local file after uploading or not. Defaults to True.

    Returns:
        str: url for file uploaded
    """
    # Error out if no file exist in input file path
    if not os.path.isfile(filePath):
        raise ValueError(f'No file existing in local path: {filePath}.')

    url2s3 = api.sendToBucket(filePath)
    if removeFile is True:
        os.remove(filePath)
    api.setJobData(jobId, nodeName, url2s3)
    return url2s3
