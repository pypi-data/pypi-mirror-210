import pytest
import os
import sys
import pandas as pd
from pandas import Timestamp
import numpy as np
import shutil
import zipfile
from ..src.logger import ETLLogger as Logger
from dotenv import load_dotenv

from ..src.exergenics_etl import (
    create_api,
    create_sql_engine,
    get_time_now,
    create_tmp_folder,
    generate_CSV_name,
    strftime_for_NaT,
    generate_one_manifest_row,
    generate_output_file_path,
    get_file_name_list,
    SkipRowsMachine,
    convertable_to_float,
    InputValidation,
    calculate_time_interval,
    DatetimeParser,
    DEFAULT_POSITION_DAY,
    transform_columns_to_long_dataframes,
    get_point_summary,
    get_statistical_summary,
    merge_long_dataframes,
    merge_wide_dataframes,
    save_file_to_portal
)


load_dotenv()

logger = Logger(loggerName='UnitTest',
                component='data_modules', subComponent='pre_merged')


class TestCreateApiClass:

    @pytest.fixture(scope='class', params=['staging', 'production'])
    def my_valid_environment(self, request):
        return request.param

    @pytest.fixture(scope='class')
    def my_invalid_environment(self):
        return 'environment'

    def test_create_api_for_valid_environment(self, my_valid_environment):
        api = create_api(my_valid_environment)
        assert api.authenticate()

    def test_create_api_for_invalid_environment(self, my_invalid_environment):
        with pytest.raises(ValueError):
            api = create_api(my_invalid_environment)


class TestCreateSQLEngineClass:

    @pytest.fixture(scope='class', params=['datastore', 'header-repo'])
    def my_test_database_name(self, request):
        return request.param

    def test_create_sql_engine(self, my_test_database_name):
        """Test if the engine created is connectable."""
        engine = create_sql_engine(databaseName=my_test_database_name,
                                   host="ex-database.mysql.database.azure.com", user="exergenics", password=os.getenv('MYSQL_PASSWORD'))
        engine.connect()

    def test_none_password(self, my_test_database_name):
        """Test raising TypeError when the password is not found in environment variables
        and is None."""
        myMissingMysqlPassword = os.getenv('MISSING_PASSWORD')
        with pytest.raises(TypeError):
            engine = create_sql_engine(databaseName=my_test_database_name,
                                       host="ex-database.mysql.database.azure.com", user="exergenics", password=myMissingMysqlPassword)


class TestGetTimeNow:

    @pytest.fixture(scope='class')
    def my_expected_output_datetime_length(self):
        return 15

    @pytest.fixture(scope='class')
    def my_expected_output_datetime_type(self):
        return str

    def test_output_datetime_length(self, my_expected_output_datetime_length):
        """Test the length of the output datetime in string."""
        assert len(get_time_now()) == my_expected_output_datetime_length

    def test_output_datetime_type(self, my_expected_output_datetime_type):
        """Test the type of the output datetime in string."""
        assert type(get_time_now()) == my_expected_output_datetime_type


class TestCreateTmpFolderClass:

    @pytest.fixture(scope='class')
    def my_test_folder(self):
        return "test_tmp_folder"

    def test_create_tmp_folder_when_not_exist(self, my_test_folder):
        """Test if the function creates a temporary folder when the folder does not exist."""
        assert not os.path.exists(my_test_folder)

        create_tmp_folder(my_test_folder)
        assert os.path.exists(my_test_folder)

        shutil.rmtree(my_test_folder)

    def test_create_tmp_folder_when_exists(self, my_test_folder):
        """Test if the function will not overwrite when the temporary folder
        we want to create already exists."""
        os.makedirs(my_test_folder+"/sub_folder")
        assert os.path.exists(my_test_folder)
        assert os.path.exists(my_test_folder+"/sub_folder")

        create_tmp_folder(my_test_folder)
        assert os.path.exists(my_test_folder+"/sub_folder")

        shutil.rmtree(my_test_folder)


class TestGenerateCSVNameClass:

    @pytest.fixture(scope='class')
    def my_test_point_name(self):
        return "CM-01 VSD INPUT POWER Trend - Present Value () (kW)"

    def test_generate_CSV_name_without_certain_characters(self, my_test_point_name):
        """Test if the following special characterare not in the output CSV name:
        spaces, '/', '~', '&', '%'.
        """
        csvName = generate_CSV_name(my_test_point_name)
        for c in [' ', '/', '~', '&', '%']:
            assert c not in csvName


class TestStrftimeForNaTClass:

    @pytest.fixture(scope='class')
    def my_NaT(self):
        return pd.to_datetime([np.nan]).min()

    @pytest.fixture(scope='class')
    def my_datetime_object_and_string(self):
        return pd.to_datetime(['2023-03-17', '2023-03-18']).min(), "17/03/2023 00:00"

    def test_strftime_for_NaT(self, my_NaT):
        assert strftime_for_NaT(my_NaT) == ""

    def test_strftime_for_datetime_object(self, my_datetime_object_and_string):
        myDatetimeObject = my_datetime_object_and_string[0]
        myDatetimeString = my_datetime_object_and_string[1]
        assert strftime_for_NaT(
            myDatetimeObject) == myDatetimeString


class TestGenerateOneManifestRowClass:

    @pytest.fixture(scope='class')
    def my_test_point_name(self):
        return "CM-01 CH-LOAD TRD1 _ (TRD1) (%)"

    @pytest.fixture(scope='class')
    def my_test_trend_log_dataframe(self, my_test_point_name):
        return pd.DataFrame({"timepretty": pd.Series(pd.to_datetime(['2023-03-18', ''])),
                             'observation': [my_test_point_name, my_test_point_name],
                             'datapoint': [1, 2]})

    def test_generate_one_manifest_row(self, my_test_point_name, my_test_trend_log_dataframe):
        """Test the type of the output manifest data for a test point."""
        manifestRow = generate_one_manifest_row(
            my_test_point_name, my_test_trend_log_dataframe)
        assert type(manifestRow) == dict


class TestGenerateOutputFilePathClass:

    @pytest.fixture(scope='class', params=['', '/temp/', 'temp'])
    def my_test_path(self, request):
        return request.param

    @pytest.fixture(scope='class')
    def my_test_inputs(self):
        return {'module': 'preheader', 'extension': 'zip', 'bCode': 'CROWN-METROPOL',
                'pCode': 'PLANT-117', 'category': 'zipfile', 'jobId': 101}

    def test_generate_output_file_path(self, my_test_path, my_test_inputs):
        """Test generating output file path with different path prefixes."""
        outputFilePath = generate_output_file_path(
            module=my_test_inputs['module'], extension=my_test_inputs['extension'],
            bCode=my_test_inputs['bCode'], pCode=my_test_inputs['pCode'],
            category=my_test_inputs['category'], jobId=my_test_inputs['jobId'],
            path=my_test_path)
        assert '//' not in outputFilePath


class TestGetFileNameListClass:

    @pytest.fixture(scope="class")
    def my_manual_zipfile(self):
        return zipfile.ZipFile("app/exergenics_etl/test/testData/manual_zipfile.zip")

    def test_get_file_name_list(self, my_manual_zipfile):
        fileNames = get_file_name_list(my_manual_zipfile)
        assert len(fileNames) == 4


class TestSkipRowsMachineClass:

    @pytest.fixture(scope='class')
    def my_expected_first_row(self):
        """The first row of the expected output form skipRowsMachine.read."""
        return pd.Series(['Timestamp', 'Test data point'])
    
    @pytest.fixture(scope='function')
    def my_skipRowsMachine(self):
        skipRowsMachine = SkipRowsMachine()
        return skipRowsMachine

    def test_skiprows1(self, my_expected_first_row, my_skipRowsMachine):
        """Test for finding skiprows value with _auto_skiprows_csv and applying the value on a XLSX sheet."""
        myTestFileNames = ["skiprows_test/skiprows.csv", "skiprows_test/skiprows.xlsx"]
        myTestZipfilePath = "app/exergenics_etl/test/testData/skiprows_test.zip"
        myTestZippedFile = zipfile.ZipFile(myTestZipfilePath)

        for fileName in myTestFileNames:
            df = my_skipRowsMachine.read(fileName, myTestZippedFile)
            assert all(df.columns.values == my_expected_first_row)

    def test_skiprows2(self, my_expected_first_row, my_skipRowsMachine):
        """Test for finding skiprows value with _auto_skiprows_excel and applying the value on a CSV."""
        myTestFileNames = ["skiprows_test/skiprows.xlsx", "skiprows_test/skiprows.csv"]
        myTestZipfilePath = "app/exergenics_etl/test/testData/skiprows_test.zip"
        myTestZippedFile = zipfile.ZipFile(myTestZipfilePath)

        for fileName in myTestFileNames:
            df = my_skipRowsMachine.read(fileName, myTestZippedFile)
            assert all(df.columns.values == my_expected_first_row)
    
    def test_skiprows3(self, my_expected_first_row, my_skipRowsMachine):
        """Test for finding skiprows value with _auto_skiprows_csv and applying the value on a XLSX sheet."""
        myTestFileNames = ["skiprows_test2/skiprows.xlsx", "skiprows_test2/skiprows.csv"]
        myTestZipfilePath = "app/exergenics_etl/test/testData/skiprows_test2.zip"
        myTestZippedFile = zipfile.ZipFile(myTestZipfilePath)

        for fileName in myTestFileNames:
            df = my_skipRowsMachine.read(fileName, myTestZippedFile)
            assert all(df.columns.values == my_expected_first_row)

    def test_skiprows4(self, my_expected_first_row, my_skipRowsMachine):
        myTestFileNames = ["skiprows_test2/skiprows.csv", "skiprows_test2/skiprows.xlsx"]
        myTestZipfilePath = "app/exergenics_etl/test/testData/skiprows_test2.zip"
        myTestZippedFile = zipfile.ZipFile(myTestZipfilePath)

        for fileName in myTestFileNames:
            df = my_skipRowsMachine.read(fileName, myTestZippedFile)
            assert all(df.columns.values == my_expected_first_row)


class TestConvertableToFloatClass:

    @pytest.mark.parametrize("string, expected", [
    ("3.14", True),  # Valid float string
    ("0", True),     # Valid float string
    ("-5.2", True),  # Valid float string
    ("1e-5", True),  # Valid float string
    (np.nan, True),  # Convertable nan
    ("abc", False),  # Invalid float string
    ("1.23.45", False),  # Invalid float string
    ("12a", False),  # Invalid float string
    ("", False),     # Empty string
    ])
    def test_convertable_to_float(self, string, expected):
        assert convertable_to_float(string) == expected


class TestInputValidationClass:

    @pytest.fixture(scope='class')
    def my_wide_format_dataframe(self):
        filePath = 'app/exergenics_etl/test/testData/wide_data.csv'
        df = pd.read_csv(filePath)
        return df

    @pytest.fixture(scope='class')
    def my_long_format_dataframe(self):
        filePath = 'app/exergenics_etl/test/testData/long_data.csv'
        df = pd.read_csv(filePath)
        return df

    @pytest.fixture(scope='class')
    def my_valid_timestamp_headers(self):
        return ['datetime', 'timestamp', 'event', 'timepretty', 'ts']

    @pytest.fixture(scope='class')
    def my_generic_column_headers(self):
        return ['value']

    @pytest.fixture(scope='class')
    def my_inputValidation_object(self, my_valid_timestamp_headers, my_generic_column_headers):
        """Instantiate an InputValidation object for testing."""
        inputValidation = InputValidation(
            my_valid_timestamp_headers, my_generic_column_headers)
        return inputValidation

    def test_check_for_wide_format1(self, my_inputValidation_object, my_wide_format_dataframe):
        """Check for wide format when a wide format dataframe is passed."""
        assert my_inputValidation_object._check_for_wide_format(
            my_wide_format_dataframe)

    def test_check_for_wide_format2(self, my_inputValidation_object, my_long_format_dataframe):
        """Check for wide format when a long format dataframe is passed."""
        assert not my_inputValidation_object._check_for_wide_format(
            my_long_format_dataframe)

    def test_check_for_generic_header1(self, my_inputValidation_object):
        myDfSameName = pd.read_csv(
            'app/exergenics_etl/test/testData/dfSameName.csv', parse_dates=['timepretty'])
        myDfNew = pd.read_csv(
            'app/exergenics_etl/test/testData/dfNew.csv', parse_dates=['timepretty'])
        myPointName = 'Ch1-kwr'

        assert not my_inputValidation_object.check_for_generic_header(
            myPointName, myDfSameName, myDfNew)

    def test_check_for_generic_header2(self, my_inputValidation_object):
        myDfSameName = pd.read_csv(
            'app/exergenics_etl/test/testData/dfSameName_genericHeader.csv', parse_dates=['timepretty'])
        myDfNew = pd.read_csv(
            'app/exergenics_etl/test/testData/dfNew_genericHeader.csv', parse_dates=['timepretty'])
        myPointName = 'Value'

        with pytest.raises(AssertionError):
            my_inputValidation_object.check_for_generic_header(
                myPointName, myDfSameName, myDfNew)

    def test_check_for_generic_header_new(self, my_inputValidation_object):
        """Check if the two dataframes share a generic name that is not in our known, generic header name list."""
        myDfSameName = pd.read_csv(
            'app/exergenics_etl/test/testData/dfSameName_newGenericHeader.csv', parse_dates=['timepretty'])
        myDfNew = pd.read_csv(
            'app/exergenics_etl/test/testData/dfNew_newGenericHeader.csv', parse_dates=['timepretty'])
        myPointName = 'Value'

        with pytest.raises(AssertionError):
            my_inputValidation_object.check_for_generic_header(
                myPointName, myDfSameName, myDfNew)

    @pytest.mark.parametrize("myTestTimestampHeader", ['timestamp', 'time stamp', 'ui::timestamp', 'ts', 'date', 'time', 'datetime', 'date/time'])
    def test_validate_timestamp_column_header(self, my_inputValidation_object, myTestTimestampHeader):
        myDf = pd.DataFrame(
            {myTestTimestampHeader: [],
             'Some random data point': []})

        assert my_inputValidation_object._validate_timestamp_column_header(
            myDf)


class TestCalculateTimeInterval:

    @pytest.fixture(scope='class')
    def my_test_case1(self):
        myTestDtSeries = pd.Series(pd.to_datetime(
            ['2023-05-19 15:08', '2023-05-19 15:09', '2023-05-19 15:10', '2023-05-19 15:10']))
        expectedTimeInterval = '1'
        return myTestDtSeries, expectedTimeInterval

    @pytest.fixture(scope='class')
    def my_test_case2(self):
        myTestDtSeries = pd.Series(pd.to_datetime(
            ['2023-05-19 15:05', '2023-05-19 15:10', '2023-05-19 15:15', '2023-05-19 15:20']))
        expectedTimeInterval = '5'
        return myTestDtSeries, expectedTimeInterval

    @pytest.fixture(scope='class')
    def my_test_case3(self):
        myTestDtSeries = pd.Series(pd.to_datetime(
            ['2023-05-19 15:05', '']))
        expectedTimeInterval = ''  # No time interval when there are < 2 datetimes
        return myTestDtSeries, expectedTimeInterval

    @pytest.fixture(scope='class')
    def my_test_case4(self):
        myTestDtSeries = pd.Series(pd.to_datetime([]))
        expectedTimeInterval = ''  # No time interval when there are < 2 datetimes
        return myTestDtSeries, expectedTimeInterval

    @pytest.mark.parametrize("my_calculate_time_interval_test_case", ['my_test_case1', 'my_test_case2', 'my_test_case3', 'my_test_case4'])
    def test_calculate_time_interval(self, my_calculate_time_interval_test_case, request):
        myTestDtSeries, expectedTimeInterval = request.getfixturevalue(
            my_calculate_time_interval_test_case)

        assert calculate_time_interval(myTestDtSeries) == expectedTimeInterval


class TestDatetimeParserClass:

    @pytest.fixture(scope='function')
    def my_datetimeParser(self):
        datetimeParser = DatetimeParser()
        return datetimeParser

    @pytest.fixture
    def my_test_case_short_year_parsing(self):
        dtSeries = pd.read_csv(
            "app/exergenics_etl/test/testData/timestamps_dayMonthShortYear.csv", header=None)[0]
        my_dtFinalFormat = '%d/%m/%y %H:%M'
        my_dtObjects = pd.to_datetime(dtSeries, format=my_dtFinalFormat)
        return dtSeries, my_dtObjects

    @pytest.fixture(scope='class')
    def my_test_case_ampm_parsing(self):
        dtSeries = pd.read_csv(
            "app/exergenics_etl/test/testData/timestamps_ampm.csv", header=None)[0]
        my_dtFinalFormat = '%d/%m/%Y %I:%M %p'
        my_dtObjects = pd.to_datetime(dtSeries, format=my_dtFinalFormat)
        return dtSeries, my_dtObjects

    @pytest.fixture(scope='class')
    def my_test_case_time_zone_parsing(self):
        dtSeries = pd.read_csv(
            "app/exergenics_etl/test/testData/timestamps_timeZones_1.csv", header=None)[0]  # TODO
        expected_output = pd.read_csv(
            "app/exergenics_etl/test/testData/timestamps_timeZones_expectedOutput_1.csv", header=None)[0]
        return dtSeries, expected_output

    @pytest.fixture
    def my_test_dtSeries_with_unrecognisable_time_parts(self):
        dtSeries = pd.read_csv(
            "app/exergenics_etl/test/testData/timestamps_unrecognisableParts.csv", header=None)[0]
        return dtSeries

    @pytest.fixture
    def my_test_case_for_correcting_format_code_with_AMPM_and_seconds(self):
        my_format_code_list = ['%d', '-', '%b', '-',
                               '%y', ' ', '%H:%M:%S', ' ', '%p', ' ', '%Z']
        correct_format_code_list = ['%d', '-', '%b', '-',
                                    '%y', ' ', '%I:%M:%S', ' ', '%p', ' ', '%Z']
        return my_format_code_list, correct_format_code_list

    @pytest.fixture
    def my_test_case_for_correcting_format_code_with_AMPM(self):
        my_format_code_list = ['%d', '-', '%b', '-',
                               '%y', ' ', '%H:%M', ' ', '%p', ' ', '%Z']
        correct_format_code_list = ['%d', '-', '%b', '-',
                                    '%y', ' ', '%I:%M', ' ', '%p', ' ', '%Z']
        return my_format_code_list, correct_format_code_list

    @pytest.fixture
    def my_format_code_with_AMPM_but_no_time(self):
        my_format_code_list = ['%d', '-', '%b', '-',
                               '%y', ' ', '%H%M', ' ', '%p', ' ', '%Z']
        return my_format_code_list

    @pytest.fixture
    def my_test_case_for_removing_time_zone_from_timestamps_with_time_zones(self):
        myDatetimeParts = ['04', '-', 'Nov', '-',
                           '22', ' ', '4:15:09', ' ', 'AM', ' ', 'AEDT']
        myFormatCodeList = ['%d', '-', '%b', '-', '%y',
                            ' ', '%H:%M:%S', ' ', '%p', ' ', '%Z']
        expectedFormatCodeList = ['%d', '-', '%b', '-', '%y',
                                  ' ', '%H:%M:%S', ' ', '%p', ' ']
        return myDatetimeParts, myFormatCodeList, expectedFormatCodeList

    @pytest.fixture
    def my_test_case_for_removing_time_zone_from_timestamps_without_time_zones(self):
        myDatetimeParts = ['04', '-', 'Nov', '-',
                           '22', ' ', '4:15:09', ' ', 'AM']
        myFormatCodeList = ['%d', '-', '%b', '-', '%y',
                            ' ', '%H:%M:%S', ' ', '%p']
        expectedFormatCodeList = ['%d', '-', '%b', '-', '%y',
                                  ' ', '%H:%M:%S', ' ', '%p']
        return myDatetimeParts, myFormatCodeList, expectedFormatCodeList

    @pytest.fixture
    def my_test_case_for_finding_unrecognisable_time_zone(self):
        myDatetimeParts = ['04', '-', 'Nov', '-',
                           '22', ' ', '4:15:09', ' ', 'AM', ' ', 'ABC']
        myFormatCodeList = ['%d', '-', '%b', '-', '%y',
                            ' ', '%H:%M:%S', ' ', '%p', ' ', 'ABC']
        return myDatetimeParts, myFormatCodeList

    def test_parse_for_short_year(self, my_datetimeParser, my_test_case_short_year_parsing):
        dtSeries, my_dtObjects = my_test_case_short_year_parsing
        assert my_datetimeParser.dtFinalFormat is None
        dtObjects = my_datetimeParser.parse(dtSeries)
        assert my_datetimeParser.dtFinalFormat is not None
        assert dtObjects.equals(my_dtObjects)

    def test_parse_for_ampm(self, my_datetimeParser, my_test_case_ampm_parsing):
        dtSeries, my_dtObjects = my_test_case_ampm_parsing
        assert my_datetimeParser.dtFinalFormat is None
        dtObjects = my_datetimeParser.parse(dtSeries)
        assert my_datetimeParser.dtFinalFormat is not None
        assert dtObjects.equals(my_dtObjects)

    def test_checkTimeZone_for_timestamps_with_time_zones(self, my_datetimeParser, my_test_case_time_zone_parsing):
        dtSeries, expected_output = my_test_case_time_zone_parsing
        dtObjects = my_datetimeParser.parse(dtSeries)
        assert my_datetimeParser.containsTimeZone

    def test_find_day_position_when_timestamps_inadequate(self, my_datetimeParser):
        myTestDtSeries = pd.read_csv(
            "app/exergenics_etl/test/testData/timestamps_findDayPosition.csv", header=None)[0]
        positionDay = my_datetimeParser._find_day_position(
            myTestDtSeries)
        assert positionDay == DEFAULT_POSITION_DAY

    def test_find_day_position_for_finding_day_large_than_12(self, my_datetimeParser):
        myTestDtSeries = pd.read_csv(
            "app/exergenics_etl/test/testData/timestamps_findDayPosition_2.csv", header=None)[0]
        positionDay = my_datetimeParser._find_day_position(
            myTestDtSeries)  # TODO
        my_expected_day_position_2 = 2
        assert positionDay == my_expected_day_position_2

    def test_removeTimeZone_for_timestamps_with_time_zones(self, my_datetimeParser, my_test_case_for_removing_time_zone_from_timestamps_with_time_zones):
        myDatetimeParts, myFormatCodeList, expectedFormatCodeList = my_test_case_for_removing_time_zone_from_timestamps_with_time_zones
        newFormatCodeList = my_datetimeParser._check_and_remove_time_zone(
            myDatetimeParts, myFormatCodeList)
        assert newFormatCodeList == expectedFormatCodeList

    def test_removeTimeZone_for_timestamps_without_time_zones(self, my_datetimeParser, my_test_case_for_removing_time_zone_from_timestamps_without_time_zones):
        myDatetimeParts, myFormatCodeList, expectedFormatCodeList = my_test_case_for_removing_time_zone_from_timestamps_without_time_zones
        newFormatCodeList = my_datetimeParser._check_and_remove_time_zone(
            myDatetimeParts, myFormatCodeList)
        assert newFormatCodeList == expectedFormatCodeList

    def test_checkTimeZone_for_timestamps_with_unrecognisable_time_zones(self, my_datetimeParser, my_test_case_for_finding_unrecognisable_time_zone):
        """
        Test for the method, _check_and_remove_time_zone, in DatetimeParser. 
        If a datetime part that doesn't follow the pattern of timezone or timezone_name defined in DatetimeParser.bricks, 
        but looks like a time zone name
        _check_and_remove_time_zone should be able to detect that and flag that time zone exists.
        """
        myDatetimeParts, myFormatCodeList = my_test_case_for_finding_unrecognisable_time_zone
        my_datetimeParser._check_and_remove_time_zone(
            myDatetimeParts, myFormatCodeList)
        assert my_datetimeParser.containsTimeZone == True

    def test_checkTimeZone_for_timestamps_without_time_zones(self, my_datetimeParser, my_test_case_ampm_parsing):
        dtSeries, my_dtObjects = my_test_case_ampm_parsing
        dtObjects = my_datetimeParser.parse(dtSeries)
        assert not my_datetimeParser.containsTimeZone

    def test_parse_for_time_zone_handling(self, my_datetimeParser, my_test_case_time_zone_parsing):
        dtSeries, expected_output = my_test_case_time_zone_parsing
        dtObjects = my_datetimeParser.parse(dtSeries)
        assert expected_output.equals(dtObjects.astype(str))

    def test_parse_for_timestamps_with_unrecognisable_time_parts(self, my_datetimeParser, my_test_dtSeries_with_unrecognisable_time_parts):
        with pytest.raises(AttributeError):
            my_datetimeParser.parse(
                my_test_dtSeries_with_unrecognisable_time_parts)

    def test_correct_format_code_for_AMPM_with_seconds(self, my_datetimeParser, my_test_case_for_correcting_format_code_with_AMPM_and_seconds):
        """
        Test for the method, _correct_format_code_for_AMPM, in DatetimeParser.
        The method should be able replace %H:%M:%S with %I:%M:%S if %H:%M:%S and %p are parts of the datetime format.
        """
        my_format_code_list, correct_format_code_list = my_test_case_for_correcting_format_code_with_AMPM_and_seconds
        newFormatCodeList = my_datetimeParser._correct_format_code_for_AMPM(
            my_format_code_list)
        assert newFormatCodeList == my_format_code_list

    def test_correct_format_code_for_AMPM(self, my_datetimeParser, my_test_case_for_correcting_format_code_with_AMPM):
        """
        Test for the method, _correct_format_code_for_AMPM, in DatetimeParser.
        The method should be able replace %H:%M with %I:%M if %H:%M and %p are parts of the datetime format.
        """
        my_format_code_list, correct_format_code_list = my_test_case_for_correcting_format_code_with_AMPM
        newFormatCodeList = my_datetimeParser._correct_format_code_for_AMPM(
            my_format_code_list)
        assert newFormatCodeList == my_format_code_list

    def test_correct_format_code_for_AMPM_but_no_time(self, my_datetimeParser, my_format_code_with_AMPM_but_no_time):
        """
        Test for the method, _correct_format_code_for_AMPM, in DatetimeParser.
        The method should raise error if %p is part of the datetime format
        but neither %H:%M:%S nor %H:%M can't be found.
        """
        my_format_code_list = my_format_code_with_AMPM_but_no_time
        with pytest.raises(ValueError):
            my_datetimeParser._correct_format_code_for_AMPM(
                my_format_code_list)

    @pytest.mark.parametrize("myTestMilliseconds", [".1", ".11", ".111", ".1111", ".11111", ".111111"])
    def test_parse_timestamp_with_milliseconds(self, my_datetimeParser, myTestMilliseconds):
        myTestTimestamp = "2022-05-15 05:05:01" + myTestMilliseconds
        myTestDtSeries = pd.Series([myTestTimestamp for i in range(10)])
        my_datetimeParser.parse(myTestDtSeries)

        assert my_datetimeParser.dtFinalFormat == '%Y-%m-%d %H:%M:%S.%f'

    @pytest.mark.parametrize("myTestMilliseconds", [".1 PM", ".11 PM", ".111 PM", ".1111 PM", ".11111 PM", ".111111 PM"])
    def test_parse_timestamp_with_milliseconds_AMPM(self, my_datetimeParser, myTestMilliseconds):
        myTestTimestamp = "2022-05-15 05:05:01" + myTestMilliseconds
        myTestDtSeries = pd.Series([myTestTimestamp for i in range(10)])
        my_datetimeParser.parse(myTestDtSeries)

        assert my_datetimeParser.dtFinalFormat == '%Y-%m-%d %I:%M:%S.%f %p'


class TestTransformColumnsToLongDataframes:

    def test_transform_columns_to_long_dataframes(self):
        myTestWideDataframe = pd.DataFrame({
            'timepretty': pd.to_datetime(['2023-05-19 15:08', '2023-05-19 15:09', '2023-05-19 15:10']),
            'Cooling Tower Fan Frequency': [0, 0, 1],
            'Cooling Tower Fan Power': [0, None, 3]
        })
        myTestFilesWithNanColumn, myTestFileName = (set(), '')
        expectedDfDictOutput = {'Cooling Tower Fan Frequency':
                                pd.DataFrame({'timepretty': [Timestamp('2023-05-19 15:08:00'), Timestamp('2023-05-19 15:09:00'), Timestamp('2023-05-19 15:10:00')],
                                              'observation': ['Cooling Tower Fan Frequency', 'Cooling Tower Fan Frequency', 'Cooling Tower Fan Frequency'],
                                              'datapoint': [0, 0, 1]}),
                                'Cooling Tower Fan Power':
                                    pd.DataFrame({'timepretty': [Timestamp('2023-05-19 15:08:00'), Timestamp('2023-05-19 15:10:00')],
                                                  'observation': ['Cooling Tower Fan Power', 'Cooling Tower Fan Power'],
                                                  'datapoint': [0.0, 3.0]})}

        dfDict, newFilesWithNanColumn = transform_columns_to_long_dataframes(
            myTestWideDataframe, myTestFilesWithNanColumn, myTestFileName)

        assert dfDict.keys() == expectedDfDictOutput.keys()

        # Compare DataFrames for each key
        for key in dfDict.keys():
            df1 = dfDict[key]
            df2 = expectedDfDictOutput[key]
            assert df1.equals(df2)


class TestGetPointSummary:

    @pytest.mark.parametrize("my_get_point_summary_test_case", ['my_summary_statistics_table_test_case1', 'my_summary_statistics_table_test_case2', 'my_summary_statistics_table_test_case3'])
    def test_get_point_summary(self, my_get_point_summary_test_case, request):
        myTestPoint, myTestDf, expectedPointSummary = request.getfixturevalue(
            my_get_point_summary_test_case)
        assert get_point_summary(
            myTestPoint, myTestDf).equals(expectedPointSummary)


class TestGetStatisticalSummary:
    def test_get_statistical_summary(self, my_summary_statistics_table_test_case1, my_summary_statistics_table_test_case2, my_summary_statistics_table_test_case3):
        myTestPoint1, myTestDf1, expectedPointSummary = my_summary_statistics_table_test_case1
        myTestPoint2, myTestDf2, expectedPointSummary = my_summary_statistics_table_test_case2
        myTestPoint3, myTestDf3, expectedPointSummary = my_summary_statistics_table_test_case3
        expectedStatisticalSummaryTable = pd.DataFrame({'count': {'Test data point1': 2.0,
                                                                  'Test data point2': 3.0,
                                                                  'Test data point3': 0.0},
                                                        'mean': {'Test data point1': 1.0,
                                                                 'Test data point2': '',
                                                                 'Test data point3': ''},
                                                        'std': {'Test data point1': 1.414,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        'min': {'Test data point1': 0.0,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        '25%': {'Test data point1': 0.5,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        '50%': {'Test data point1': 1.0,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        '75%': {'Test data point1': 1.5,
                                                                'Test data point2': '',
                                                                'Test data point3': ''},
                                                        'max': {'Test data point1': 2.0,
                                                                'Test data point2': '',
                                                                'Test data point3': ''}})

        assert get_statistical_summary(
            {myTestPoint1: myTestDf1, myTestPoint2: myTestDf2, myTestPoint3: myTestDf3}).equals(expectedStatisticalSummaryTable)


class TestMergeLongDataframesClass:

    @pytest.fixture(scope='class')
    def my_df_list(self):
        df = pd.DataFrame(np.array([['01/01/2023 00:00', 'a', 7], ['01/01/2023 00:08', 'a', 8], ['01/01/2023 00:16', 'a', 9]]),
                          columns=['t', 'd', 'v'])
        df1 = pd.DataFrame(np.array([['01/01/2023 00:00', 'b', 9], ['01/01/2023 00:08', 'b', 8], ['01/01/2023 00:16', 'b', 9]]),
                           columns=['t', 'd', 'v'])
        return [df, df1, df]

    @pytest.fixture(scope='class')
    def my_invalid_df_list(self):
        df = pd.DataFrame(np.array([['a', 7], ['a', 8], ['a', 9]]),
                          columns=['t', 'd'])
        df1 = pd.DataFrame(np.array([['b', 9], ['b', 8], ['b', 9]]),
                           columns=['t', 'd'])
        return [df, df1, df]

    @pytest.fixture(scope='class')
    def my_freq(self):
        return 5

    def test_merge_long_dataframes(self, my_df_list, my_freq):
        """Test the type of the wide dataframe merged from a list of long dataframes."""
        tmpMergedDf = merge_long_dataframes(my_df_list, my_freq)
        assert type(tmpMergedDf) == pd.DataFrame

    def test_merge_invalid_long_dataframes(self, my_invalid_df_list, my_freq):
        """Test the invalid long dataframe in input dfList"""
        with pytest.raises(ValueError):
            tmpMergedDf = merge_long_dataframes(my_invalid_df_list, my_freq)


class TestMergeWideDataframesClass:

    @pytest.fixture(scope='class')
    def my_df_list(self):
        df = pd.DataFrame(np.array([['01/01/2023 00:00', 1.5, 7], ['01/01/2023 00:05', 2.4, 8], ['01/01/2023 00:10', 23.2, 9]]),
                          columns=['Timestamp', 'col1', 'col2'])
        df1 = pd.DataFrame(np.array([['01/01/2023 00:00', 0.6, 9], ['01/01/2023 00:05', 5.5, 8], ['01/01/2023 00:10', 56.2, 9]]),
                           columns=['Timestamp', 'col3', 'col4'])
        return [df, df1]

    @pytest.fixture(scope='class')
    def my_missing_timestamp_df_list(self):
        df = pd.DataFrame(np.array([['01/01/2023 00:00', 1.5, 7], ['01/01/2023 00:05', 2.4, 8], ['01/01/2023 00:10', 23.2, 9]]),
                          columns=['time', 'col1', 'col2'])
        df1 = pd.DataFrame(np.array([['01/01/2023 00:00', 0.6, 9], ['01/01/2023 00:05', 5.5, 8], ['01/01/2023 00:10', 56.2, 9]]),
                           columns=['time', 'col3', 'col4'])
        return [df, df1]

    def test_merge_wide_dataframes(self, my_df_list):
        """Test the type of the wide dataframe merged from a list of wide dataframes."""
        tmpMergedDf = merge_wide_dataframes(my_df_list)
        assert type(tmpMergedDf) == pd.DataFrame

    def test_merge_missing_timestamp_wide_dataframes(self, my_missing_timestamp_df_list):
        """Test the missing timestamp column in input dfList"""
        with pytest.raises(ValueError):
            tmpMergedDf = merge_wide_dataframes(my_missing_timestamp_df_list)


class TestSaveFileToPortalClass:
    # TODO: call jobId and api from conftest.py we created it
    @pytest.fixture(scope="class")
    def my_api(self):
        return None

    @pytest.fixture(scope="class")
    def my_filePath(self):
        return ''

    @pytest.fixture(scope="class")
    def my_jobId(self):
        return ''

    @pytest.fixture(scope="class")
    def my_nodeName(self):
        return ''

    @pytest.fixture(scope='class')
    def my_removeFile(self):
        return False

    def test_save_missing_file_to_portal(self, my_api, my_filePath, my_jobId, my_nodeName, my_removeFile):
        """Test saving missing file to portal"""
        with pytest.raises(ValueError):
            url2s3 = save_file_to_portal(
                my_api, my_filePath, my_jobId, my_nodeName, my_removeFile)
