'''
    This test code addresses only non MockBlob related functionality.
    As it is not able to create MockBlobs locally and we don't want to use
    Azurite?
'''
import unittest
import pandas as pd
import time

from sql2parquet.bol import unix2utc, diff_in_seconds, expired_files


class MockBlob:
    '''
        This class is used to create a Mock Blob.
        A real Blob has a name attribute. We need to create a list
        of these for unit test puporses.
    '''
    def __init__(self, name):
        self.name = name

class Test_Utils(unittest.TestCase):
    '''
        TODO: Documentation
    '''
    # Used to display all columns without truncation
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)


    def test_unix2utc(self):
        '''
            Test time conversion method
        '''
        unit_time = 1702326046
        utc_time = unix2utc(unit_time)
        expected_utc_time = '20231211T20:20:46'
        self.assertEqual(utc_time, expected_utc_time, f'--* Expected UTC time to be 2021-02-08 14:07:26 but obtained {utc_time}')


    def test_diff_in_seconds(self):
        '''
            Test time difference method
        '''
        t1 = '20210208T14:07:26'
        t2 = '20210208T14:07:56'
        diff = diff_in_seconds(t1, t2)
        expected_diff = 30
        self.assertEqual(diff, expected_diff, f'--* Expected diff to be {expected_diff} but obtained {diff}')


    def test_expired_files(self):
        '''
            Test expired files method
        '''
        list_of_files = [MockBlob('silver/TOPSv2/T_BOL/BOL_20231208T14:07:26.parquet'),
                         MockBlob('silver/TOPSv2/T_BOL/BOL_20210208T14:07:56.parquet')
                         ]
        expected_list_of_expired_files = list_of_files.copy()
        now = unix2utc(time.time())
        new_filename = MockBlob(f'silver/TOPSv2/T_BOL/BOL_{now}.parquet')
        list_of_files.append(new_filename)
        actual_expired_files = expired_files(list_of_files, now, 7500)

        self.assertListEqual(actual_expired_files, expected_list_of_expired_files, f'--* Expected expired_files to be {expected_list_of_expired_files} but obtained {actual_expired_files}')


    def test_expired_files_none_too_old(self):
        '''
            Test expired files method. In this case, none of the files are too old.
        '''
        now = unix2utc(time.time())
        new_filename = f'silver/TOPSv2/T_BOL/BOL_{now}.parquet'
        list_of_files = [MockBlob('silver/TOPSv2/T_BOL/BOL_20231208T14:07:26.parquet'),
                         MockBlob('silver/TOPSv2/T_BOL/BOL_20210208T14:07:56.parquet'),
                         MockBlob(f'{new_filename}')
                         ]
        expected_list_of_expired_files = []
        actual_expired_files = expired_files(list_of_files, now, 750000000)

        self.assertListEqual(actual_expired_files, expected_list_of_expired_files, f'--* Expected expired_files to be {expected_list_of_expired_files} but obtained {actual_expired_files}')

