import json
import io
import numpy as np
import re
import unittest
import pandas as pd
from rest_app.services.Config import REGEX, PAYLOAD_COLUMNS
from dotenv import load_dotenv
from rest_app.services.Delta import get_table, build_schedule_table, json_to_parquet

load_dotenv()

class Testing(unittest.TestCase):
    '''
        Unit tests. Only the code in Delta.py is addressed. The code is written in such
        a way that when a None file_system is provided the methods look for data in the
        local file system, otherwise the data is expected to be in an Azure Storage account.
    '''

    def test_get_table_size(self):
        '''
            Simple test case to fetch data from the local file system
        '''
        table_path = "tests/input_data/T_ROUTE"
        df_test = get_table(file_system=None, container=None, table_path=table_path)
        self.assertEqual(9, len(df_test), "Expected number of rows not obtained.")

    def test_schedule_table_schema(self):
        '''
            This test case should test presence of expected columns in the schema etc.
        '''
        path = "tests/input_data"
        start_date = '2021-07-01'
        end_date = '2021-07-08'
        vessel_filter = '' # all vessels
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)
        self.assertEqual(110, len(df_test), 'Expected number of rows not obtained')

        expected_columns = ['Scheduled_Departure_Date_Time',
                            'Scheduled_Arrival_Date_Time',
                            'Actual_Arrival_Date_Time',
                            'Actual_Departure_Date_Time',
                            'RouteCode',
                            'Route',
                            'Vessel_Code',
                            'Vessel',
                            'Sailing_ID',
                            'Lane',
                            'LastUpdate_ts',
                            'Added_dt',
                            'Deleted_dt',
                            'Destination_Port',
                            'Origin_Port',
                            'Departure_Berth',
                            'Arrival_Berth',
                            'UTC_Scheduled_Departure_Date_Time',
                            'UTC_Scheduled_Arrival_Date_Time',
                            'UTC_Actual_Arrival_Date_Time',
                            'UTC_Actual_Departure_Date_Time',
                            'Dep_var',
                            'Arr_var'
                            ]

        actual_columns = df_test.columns.to_list()

        self.assertEqual(expected_columns, actual_columns,
            f'Expected schema={expected_columns}, but obtained schema={actual_columns}')

    def test_schedule_table_sample_content(self):
        '''
            This test case verifies some content in the constructed table.
        '''
        path = "tests/input_data"
        start_date = '2020-05-24'
        end_date = '2020-05-26'
        vessel_filter = '' # all vessels
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)

        df_test_filtered = df_test.loc[(df_test.Sailing_ID == 44852)]
        expected_vessel_name = 'Seaspan Greg'
        expected_route_code = 'DUK>SUR'

        actual_vessel_name = df_test_filtered['Vessel'].values[0]
        actual_route_code = df_test_filtered['RouteCode'].values[0]

        self.assertEqual(expected_vessel_name, actual_vessel_name)
        self.assertEqual(expected_route_code, actual_route_code)


    def test_schedule_table_schema_for_one_vessel(self):
        '''
            This test case should test presence of expected columns in the schema etc.
        '''
        path = "tests/input_data"
        start_date = '2021-07-01'
        end_date = '2021-07-08'
        vessel_filter = 'SG'
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)
        self.assertEqual(8, len(df_test), 'Expected number of rows not obtained')


    def test_deleted_dt_null(self):
        '''
            This test case should test confirm presence of non Null Deleted_dt.
            In this case:
                Sailing_ID = 52552
                Deleted_dt = Null
        '''
        path = "tests/input_data"
        start_date = '2021-08-07'
        end_date = '2021-08-08'
        vessel_filter = '' # all vessels
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)
        self.assertEqual(9, len(df_test), 'Expected number of rows not obtained')

        raised = False
        try:
            actual_deleted_dt = df_test.loc[df_test['Sailing_ID'] == 52552]['Deleted_dt'].to_list()[0]
        except :
            raised = True

        self.assertFalse(raised, '--* Deleted_Dt not found')
        self.assertTrue(pd.isnull(actual_deleted_dt), 'Null Deleted_dt expected but not found')


    def test_deleted_dt_not_null(self):
        '''
            This test case should also test confirm presence of non Null Deleted_dt.
            Added for ticket 1135
            In this case:
                Sailing_ID = 53185
                Deleted_dt = 2021-09-09 09:41:04.510
                Scheduled_Departure_Date_Time = 2021-09-07T02:30:00.000
        '''
        path = "tests/input_data"
        start_date = '2021-09-07'
        end_date = '2021-09-08'
        vessel_filter = '' # all vessels
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)
        self.assertEqual(22, len(df_test), 'Expected number of rows not obtained')

        expected_deleted_dt = pd.Timestamp('2021-09-09 09:41:04.510')
        raised = False
        try:
            actual_deleted_dt = df_test.loc[df_test['Sailing_ID'] == 53185]['Deleted_dt'].to_list()[0]
        except : 
            raised = True

        self.assertFalse(raised, '--* Deleted_Dt not found')
        self.assertEqual(expected_deleted_dt, actual_deleted_dt, 'Value of Deleted_dt did not match')   


    def test_deleted_dt_re_not_null(self):
        '''
            This test case should also test confirm presence of non Null Deleted_dt.
            Added for ticket 1135
            In this case:
                Sailing_ID = 54869
                Deleted_dt = 2021-12-06 
                Scheduled_Departure_Date_Time = 2021-12-15 09:55:00
        '''
        path = "tests/input_data"
        start_date = '2021-12-15'
        end_date = '2021-12-16'
        vessel_filter = 'SW,RE'
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)
        self.assertEqual(9, len(df_test), 'Expected number of rows not obtained')

        expected_deleted_dt = pd.Timestamp('2021-12-06 15:27:42.833')
        raised = False
        try:
            actual_deleted_dt = df_test.loc[df_test['Sailing_ID'] == 54869]['Deleted_dt'].to_list()[0]
        except : 
            raised = True

        self.assertFalse(raised, '--* Deleted_Dt not found')
        self.assertEqual(expected_deleted_dt, actual_deleted_dt, 'Value of Deleted_dt did not match')        

    def test_timezone(self):
        '''
            All times are PST. Thus, datetimes should not have a trailing Z.
        '''
        path = "tests/input_data"
        start_date = '2020-05-24'
        end_date = '2020-05-26'
        vessel_filter = '' # all vessels
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)

        a_time = df_test.loc[df_test['Sailing_ID'] == 44852]['Actual_Departure_Date_Time'].to_list()[0]
        a_time_ends_with_z = str(a_time).endswith('Z')
        print(f'+++ a_time = {str(a_time)}')
        self.assertFalse(a_time_ends_with_z, f'Timestamp {a_time} should not end in a Z')

        # Now convert the dataframe to JSON the way the wrapper code does
        json_output = df_test.to_json(orient='records', date_format='iso')
        j_z_removed = re.sub(REGEX, '\\1', json_output)  
        d = json.loads(j_z_removed)

        # Lets get the same Actual_Departure_Date_Time
        b_time = None
        for index, item in enumerate(d):
            s_id = item['Sailing_ID']
            if (s_id == 44852):
                b_time = item['Actual_Departure_Date_Time']
                print(f'+++ b_time = {str(b_time)}')

        b_time_ends_with_z = b_time.endswith('Z')
        self.assertFalse(b_time_ends_with_z, f'JSON timestamp {b_time} should not end in a Z')

    def test_utc_times_pdt(self):
        '''
            This test case verifies the new UTC columns added for ticket
            https://dev.azure.com/seaspan-edw/DataOps/_workitems/edit/1639
            This test case is after DST
        '''
        path = "tests/input_data"
        start_date = '2022-03-24'
        end_date = '2022-03-26'
        vessel_filter = '' # all vessels
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)

        df_test_filtered = df_test.loc[(df_test.Sailing_ID == 56672)]
        expected_scheduled_departure_date_time = np.datetime64('2022-03-24 21:45:00')
        expected_utc_scheduled_departure_date_time = np.datetime64('2022-03-25 04:45:00')

        actual_scheduled_departure_date_time = df_test_filtered['Scheduled_Departure_Date_Time'].values[0]
        actual_utc_scheduled_departure_date_time = df_test_filtered['UTC_Scheduled_Departure_Date_Time'].values[0]

        self.assertEqual(expected_scheduled_departure_date_time, actual_scheduled_departure_date_time)
        self.assertEqual(expected_utc_scheduled_departure_date_time, actual_utc_scheduled_departure_date_time)

    def test_utc_times_pst(self):
        '''
            This test case verifies the new UTC columns added for ticket
            https://dev.azure.com/seaspan-edw/DataOps/_workitems/edit/1639
            This test case is before DST
        '''
        path = "tests/input_data"
        start_date = '2022-02-24'
        end_date = '2022-02-26'
        vessel_filter = '' # all vessels
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)

        df_test_filtered = df_test.loc[(df_test.Sailing_ID == 56419)]
        expected_scheduled_departure_date_time = np.datetime64('2022-02-24 19:40:00')
        expected_utc_scheduled_departure_date_time = np.datetime64('2022-02-25 03:40:00')

        actual_scheduled_departure_date_time = df_test_filtered['Scheduled_Departure_Date_Time'].values[0]
        actual_utc_scheduled_departure_date_time = df_test_filtered['UTC_Scheduled_Departure_Date_Time'].values[0]

        self.assertEqual(expected_scheduled_departure_date_time, actual_scheduled_departure_date_time)
        self.assertEqual(expected_utc_scheduled_departure_date_time, actual_utc_scheduled_departure_date_time)

    def test_match_scheduled_arrival_to_utc_scheduled_arrival(self):
        '''
            This test case is to explore a bug where we some cases where the Scheduled_Arrival_Date_Time
            is non-null but the corresponding UTC_Scheduled_Arrival_Date_Time is null.
            We know this problem is observed with sailing Ids, 59424 and 57710 for example.
        '''
        path = "tests/input_data"
        start_date = '2022-10-04'
        end_date = '2022-10-07'
        vessel_filter = '' # all vessels
        df_test = build_schedule_table(None, None, path, start_date, end_date, vessel_filter)

        df_test_filtered = df_test.loc[(df_test.Sailing_ID == 59424)]
        expected_scheduled_departure_date_time = np.datetime64('2022-10-06 06:45:00')
        expected_utc_scheduled_departure_date_time = np.datetime64('2022-10-06 13:45:00')
        expected_scheduled_arrival_date_time = np.datetime64('2022-10-06 10:00:00')
        expected_utc_scheduled_arrival_date_time = np.datetime64('2022-10-06 17:00:00')

        actual_scheduled_departure_date_time = df_test_filtered['Scheduled_Departure_Date_Time'].values[0]
        actual_utc_scheduled_departure_date_time = df_test_filtered['UTC_Scheduled_Departure_Date_Time'].values[0]
        actual_scheduled_arrival_date_time = df_test_filtered['Scheduled_Arrival_Date_Time'].values[0]
        actual_utc_scheduled_arrival_date_time = df_test_filtered['UTC_Scheduled_Arrival_Date_Time'].values[0]

        self.assertEqual(expected_scheduled_departure_date_time, actual_scheduled_departure_date_time)
        self.assertEqual(expected_utc_scheduled_departure_date_time, actual_utc_scheduled_departure_date_time)
        self.assertEqual(expected_scheduled_arrival_date_time, actual_scheduled_arrival_date_time)
        self.assertEqual(expected_utc_scheduled_arrival_date_time, actual_utc_scheduled_arrival_date_time)

    def test_event_json_passage_start_to_parquet(self):
        '''
            This test case throws in real looking payload
        '''
        json_str = '''
{
	"meta": {
		"id": "384371328sdfjldf",
        "version": 1,
		"topic": "passage_started",
		"recorded_at": "2023-02-12T00:00:00.000Z"
	},
	"data": {
		"passage": {
			"id": "ldkfap93487r",
			"started_at": "2023-02-12T00:00:00.000Z",
			"completed_at": null,
			"from_dock": {
				"id": "57d",
				"name": "sd3",
				"port": {
					"id": "456p",
					"country_id": "CA",
					"name": "Tilbury",
					"unlocode": null
				}
			},
			"to_dock": null,
			"vessel": {
                "code": "TRN",
				"id": "fff171b6-59c3-48c4-9596-a89cd5be7eb1",
				"imo_number": 1234,
				"name": "Trader"
			},
			"voyage": {
				"id": "394873",
				"number": "1"
			}
		}
	}
}
        '''
        parquet_data = json_to_parquet(json.loads(json_str))

        byte_stream = io.BytesIO(parquet_data)
        df = pd.read_parquet(byte_stream)

        num_rows_expected = 1
        actual_num_rows = len(df)
        expected_sailing_id = '394873'
        actual_sailing_id = df['data_passage_voyage_id'][0]
        expected_from_port_name = 'Tilbury'
        actual_from_port_name = df['data_passage_from_dock_port_name'][0]

        self.assertEqual(num_rows_expected, actual_num_rows, f'{num_rows_expected} rows expected but {actual_num_rows} obtained')
        self.assertEqual(expected_sailing_id, actual_sailing_id, f'sailing_id={expected_sailing_id}, but {actual_sailing_id} obtained')
        self.assertEqual(expected_from_port_name, actual_from_port_name, f'from_port={expected_from_port_name}, but {actual_from_port_name} obtained')


    def test_event_none_in_json_passage_start_to_parquet(self):
        '''
            This test case throws in real looking payload
        '''
        json_str = '''
{
	"meta": {
		"id": "384371328sdfjldf",
        "version": 1,
		"topic": "passage_started",
		"recorded_at": "2023-02-12T00:00:00.000Z"
	},
	"data": {
		"passage": {
			"id": "ldkfap93487r",
			"started_at": "2023-02-12T00:00:00.000Z",
			"completed_at": null,
			"from_dock": {
				"id": "57d",
				"name": "sd3",
				"port": {
					"id": "456p",
					"country_id": "CA",
					"name": "Tilbury",
					"unlocode": null
				}
			},
			"to_dock": null,
			"vessel": {
                "code": "TRN",
				"id": "fff171b6-59c3-48c4-9596-a89cd5be7eb1",
				"imo_number": 6789,
				"name": "Transported"
			},
			"voyage": {
				"id": "394873",
				"number": "1"
			}
		}
	}
}
        '''
        parquet_data = json_to_parquet(json.loads(json_str))

        byte_stream = io.BytesIO(parquet_data)
        df = pd.read_parquet(byte_stream)

        num_rows_expected = 1
        actual_num_rows = len(df)
        actual_to_port_name = df['data_passage_to_dock_port_name'][0]

        self.assertEqual(num_rows_expected, actual_num_rows, f'{num_rows_expected} rows expected but {actual_num_rows} obtained')
        self.assertIsNone(actual_to_port_name, f'passage_start events should have None to_port_name but was {actual_to_port_name}')


    def test_event_columns_in_parquet(self):
        '''
            This test case simply counts the number of columns returned in the parquet
        '''
        json_str = '''
{
	"meta": {
		"id": "384371328sdfjldf",
        "version": 1,
		"topic": "passage_started",
		"recorded_at": "2023-02-12T00:00:00.000Z"
	},
	"data": {
		"passage": {
			"id": "ldkfap93487r",
			"started_at": "2023-02-12T00:00:00.000Z",
			"completed_at": null,
			"from_dock": {
				"id": "57d",
				"name": "sd3",
				"port": {
					"id": "456p",
					"country_id": "CA",
					"name": "Tilbury",
					"unlocode": null
				}
			},
			"to_dock": null,
			"vessel": {
                "code": "TRN",
				"id": "fff171b6-59c3-48c4-9596-a89cd5be7eb1",
				"imo_number": 6789,
				"name": "Transported"
			},
			"voyage": {
				"id": "394873",
				"number": "1"
			}
		}
	}
}
        '''
        parquet_data = json_to_parquet(json.loads(json_str))

        byte_stream = io.BytesIO(parquet_data)
        df = pd.read_parquet(byte_stream)
        df_cols = df.columns

        expected_num_cols = len(PAYLOAD_COLUMNS.split(','))
        actual_num_cols = len(df_cols)

        self.assertEqual(expected_num_cols, actual_num_cols, f'{expected_num_cols} columns expected but {actual_num_cols} obtained')


    def test_event_column_types_in_2_parquet(self):
        '''
            This test case compares the dtypes of columns across two different parquets.
            The first is for a passage_start event and the second a passage_completed event.
        '''
        start_json_str = '''
{
	"meta": {
		"id": "384371328sdfjldf",
        "version": 1,
		"topic": "passage_started",
		"recorded_at": "2023-02-12T00:00:00.000Z"
	},
	"data": {
		"passage": {
			"id": "ldkfap93487r",
			"started_at": "2023-02-12T00:00:00.000Z",
			"completed_at": null,
			"from_dock": {
				"id": "57d",
				"name": "sd3",
				"port": {
					"id": "456p",
					"country_id": "CA",
					"name": "Tilbury",
					"unlocode": "372"
				}
			},
			"to_dock": null,
			"vessel": {
                "code": "TRN",
				"id": "fff171b6-59c3-48c4-9596-a89cd5be7eb1",
				"imo_number": 6789,
				"name": "Transporter"
			},
			"voyage": {
				"id": "394873",
				"number": "1"
			}
		}
	}
}
        '''

        stop_json_str = '''
{
	"meta": {
		"id": "8374iadf",
        "version": 1,
		"topic": "passage_completed",
		"recorded_at": "2023-02-12T02:45:00.000Z"
	},
	"data": {
		"passage": {
			"id": "ldkfap93487r",
			"started_at": "2023-02-12T00:00:00.000Z",
			"completed_at": "2023-02-12T02:44:31.000Z",
			"from_dock": {
				"id": "57d",
				"name": "sd3",
				"port": {
					"id": "456p",
					"country_id": "CA",
					"name": "Tilbury",
					"unlocode": "372"
				}
			},
			"to_dock": {
				"id": "32e",
				"name": "kd8",
				"port": {
					"id": "98s",
					"country_id": "CA",
					"name": "Duke Point",
					"unlocode": null
				}
			},
			"vessel": {
                "code": "TRN",
				"id": "fff171b6-59c3-48c4-9596-a89cd5be7eb1",
				"imo_number": 6789,
				"name": "Transporter"
			},
			"voyage": {
				"id": "982374",
				"number": "2"
			}
		}
	}
}
        '''
        start_parquet_data = json_to_parquet(json.loads(start_json_str))
        stop_parquet_data = json_to_parquet(json.loads(stop_json_str))

        byte_stream = io.BytesIO(start_parquet_data)
        start_df = pd.read_parquet(byte_stream)
        start_dtypes = start_df.dtypes.to_dict()
        byte_stream = io.BytesIO(stop_parquet_data)
        stop_df = pd.read_parquet(byte_stream)
        stop_dtypes = stop_df.dtypes.to_dict()

        self.assertDictEqual(start_dtypes, stop_dtypes, '--* column types differ!')


    def test_null_version(self):
        '''
            This test checks that a meta.version field is added to the parquet
        '''
        json_str = '''
{
	"meta": {
		"id": "384371328sdfjldf",
		"topic": "passage_started",
		"recorded_at": "2023-02-12T00:00:00.000Z"
	},
	"data": {
		"passage": {
			"id": "ldkfap93487r",
			"started_at": "2023-02-12T00:00:00.000Z",
			"completed_at": null,
			"from_dock": {
				"id": "57d",
				"name": "sd3",
				"port": {
					"id": "456p",
					"country_id": "CA",
					"name": "Tilbury",
					"unlocode": null
				}
			},
			"to_dock": null,
			"vessel": {
                "code": "TRN",
				"id": "fff171b6-59c3-48c4-9596-a89cd5be7eb1",
				"imo_number": 6789,
				"name": "Transported"
			},
			"voyage": {
				"id": "394873",
				"number": "1"
			}
		}
	}
}
        '''
        parquet_data = json_to_parquet(json.loads(json_str))

        byte_stream = io.BytesIO(parquet_data)
        df = pd.read_parquet(byte_stream)

        num_rows_expected = 1
        actual_num_rows = len(df)
        actual_version = df['meta_version'][0]

        self.assertEqual(num_rows_expected, actual_num_rows, f'{num_rows_expected} rows expected but {actual_num_rows} obtained')
        self.assertIsNone(actual_version, f'version should be None but was {actual_version}')


    def test_non_null_version(self):
        '''
            This test checks that a meta.version field is added to the parquet
        '''
        json_str = '''
{
	"meta": {
		"id": "384371328sdfjldf",
		"topic": "passage_started",
		"recorded_at": "2023-02-12T00:00:00.000Z",
        "version": 1
	},
	"data": {
		"passage": {
			"id": "ldkfap93487r",
			"started_at": "2023-02-12T00:00:00.000Z",
			"completed_at": null,
			"from_dock": {
				"id": "57d",
				"name": "sd3",
				"port": {
					"id": "456p",
					"country_id": "CA",
					"name": "Tilbury",
					"unlocode": null
				}
			},
			"to_dock": null,
			"vessel": {
                "code": "TRN",
				"id": "fff171b6-59c3-48c4-9596-a89cd5be7eb1",
				"imo_number": 6789,
				"name": "Transported"
			},
			"voyage": {
				"id": "394873",
				"number": "1"
			}
		}
	}
}
        '''
        parquet_data = json_to_parquet(json.loads(json_str))

        byte_stream = io.BytesIO(parquet_data)
        df = pd.read_parquet(byte_stream)

        num_rows_expected = 1
        actual_num_rows = len(df)
        actual_version = df['meta_version'][0]
        expected_version = 1

        self.assertEqual(num_rows_expected, actual_num_rows, f'{num_rows_expected} rows expected but {actual_num_rows} obtained')
        self.assertEqual(expected_version, actual_version, f'version {expected_version} expected but obtained {actual_version}')
