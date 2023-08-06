import os
import re
import boto3
# import logging
import numpy as np
import botocore
from botocore.config import Config
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

class LambdaExecutor:

    def __init__(self, index_ek60_table_name, bucket_name, calibration_bucket, calibration_key):
        self.session = boto3.Session()
        self.dynamodb = self.session.client(service_name='dynamodb')
        self.max_pool_connections = 64
        self.client_config = botocore.config.Config(max_pool_connections=self.max_pool_connections)
        self.s3 = self.session.client(service_name='s3', config=self.client_config)
        self.index_ek60_table_name = index_ek60_table_name
        self.bucket_name = bucket_name
        self.calibration_bucket = calibration_bucket
        self.calibration_key = calibration_key

    def __find_child_objects(
            self,
            sub_prefix: str
        ) -> list:
        # Given a cruise sub_prefix, return all the children objects
        paginator = self.s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=sub_prefix)
        objects = []
        for page in page_iterator:
            objects.extend(page['Contents'])
        return objects

    def __get_all_objects(self) -> pd.DataFrame:
        # Get all objects in data/raw/ s3 folder.
        # Returns pandas dataframe with ['Key', 'LastModified', 'ETag', 'Size', 'StorageClass']
        # Threaded by cruise to decrease time.
        print("getting all objects")
        cruises = []
        for ship in self.s3.list_objects(Bucket=self.bucket_name, Prefix='data/raw/', Delimiter='/').get('CommonPrefixes'):
            for cruise in self.s3.list_objects(Bucket=self.bucket_name, Prefix=ship.get('Prefix'), Delimiter='/').get(
                    'CommonPrefixes'):
                cruises.append(cruise.get('Prefix'))
        all_objects = []
        with ThreadPoolExecutor(max_workers=self.max_pool_connections) as executor:
            futures = [executor.submit(self.__find_child_objects, cruise) for cruise in cruises]
            for future in as_completed(futures):
                all_objects.extend(future.result())
        return pd.DataFrame(all_objects)

    def __get_subset_ek60_prefix(
            self,
            df: pd.DataFrame
    ) -> pd.DataFrame:
        # Returns all objects with 'EK60' in prefix of file path
        # Note that this can include 'EK80' data that are false-positives
        # in dataframe with ['key', 'filename', 'ship', 'cruise', 'sensor', 'size', 'date', 'datagram']
        print("getting subset of ek60 data by prefix")
        objects = []
        for row in df.itertuples():
            row_split = row[1].split(os.sep)
            if len(row_split) == 6:
                filename = os.path.basename(row[1])  # 'EX1608_EK60-D20161205-T040300.raw'
                if filename.endswith(".raw"):
                    ship_name, cruise_name, sensor_name = row_split[2:5]  # 'Okeanos_Explorer', 'EX1608', 'EK60'
                    if re.search("[D](\d{8})", filename) is not None and re.search("[T](\d{6})", filename) is not None:
                        # Parse date if possible e.g.: 'data/raw/Henry_B._Bigelow/HB1006/EK60/HBB-D20100723-T025105.raw'
                        # and 'data/raw/Henry_B._Bigelow/HB1802/EK60/D20180513-T150250.raw'
                        date_substring = re.search("[D](\d{8})", filename).group(1)
                        time_substring = re.search("[T](\d{6})", filename).group(1)
                        date_string = datetime.strptime(f'{date_substring}{time_substring}', '%Y%m%d%H%M%S')
                    else:  # otherwise use current date
                        date_string = f"{datetime.utcnow().isoformat()[:19]}Z"
                    objects.append(
                        {
                            'KEY': row[1],
                            'FILENAME': filename,
                            'SHIP': ship_name,
                            'CRUISE': cruise_name,
                            'SENSOR': sensor_name,
                            'SIZE': row[2],
                            'DATE': date_string,
                            'DATAGRAM': None
                        }
                    )
        return pd.DataFrame(objects)

    def __scan_datagram(self, select_key: str) -> list:
        # Reads the first 8 bytes of S3 file. Used to determine if ek60 or ek80
        # Note: uses boto3 session instead of boto3 client: https://github.com/boto/boto3/issues/801
        # select_key = 'data/raw/Albatross_Iv/AL0403/EK60/L0005-D20040302-T200108-EK60.raw'
        session_thread_pool = boto3.Session()  # remove for lambda
        s3_thread_pool = session_thread_pool.resource(service_name='s3', config=self.client_config)
        obj = s3_thread_pool.Object(bucket_name=self.bucket_name, key=select_key)  # XML0
        first_datagram = obj.get(Range='bytes=3-7')['Body'].read().decode().strip('\x00')
        return [{'KEY': select_key, 'DATAGRAM': first_datagram}]

    def __get_subset_datagrams(self, df: pd.DataFrame) -> list:
        print("getting subset of datagrams")
        select_keys = list(df[['KEY', 'CRUISE']].drop_duplicates(subset='CRUISE')['KEY'].values)
        all_datagrams = []
        with ThreadPoolExecutor(max_workers=self.max_pool_connections) as executor:
            futures = [executor.submit(self.__scan_datagram, select_key) for select_key in select_keys]
            for future in as_completed(futures):
                all_datagrams.extend(future.result())
        return all_datagrams

    def __get_ek60_objects(
            self,
            df: pd.DataFrame,
            subset_datagrams: list
    ) -> pd.DataFrame:
        # for each key write datagram value to all other files in same cruise
        for subset_datagram in subset_datagrams:
            if subset_datagram['DATAGRAM'] == 'CON0':
                select_cruise = df.loc[df['KEY'] == subset_datagram['KEY']]['CRUISE'].iloc[0]
                df.loc[df['CRUISE'] == select_cruise, ['DATAGRAM']] = subset_datagram['DATAGRAM']
        return df.loc[df['DATAGRAM'] == 'CON0']

    def __create_table(
            self
    ) -> None:
        params = {
            'TableName': self.index_ek60_table_name,
            'KeySchema': [
                {'AttributeName': 'CRUISE', 'KeyType': 'HASH'},
                {'AttributeName': 'SHIP', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'CRUISE', 'AttributeType': 'S'},
                {'AttributeName': 'SHIP', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST',
            'Tags': [
                {
                    'Key': 'project',
                    'Value': 'echofish'
                },
            ],
        }
        # TODO: create_table returns a dict for validation
        table = self.dynamodb.create_table(**params)
        waiter = self.dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=self.index_ek60_table_name)
        print(f"table: {self.index_ek60_table_name} created")

    def __delete_table(
            self
    ) -> None:
        # Attempts to delete an existing table.
        try:
            self.dynamodb.delete_table(TableName=self.index_ek60_table_name)
            waiter = self.dynamodb.get_waiter('table_not_exists')
            waiter.wait(TableName=self.index_ek60_table_name)
            print(f"table: {self.index_ek60_table_name} deleted")
        except self.dynamodb.exceptions.ClientError as err:
            # logger.error(
            #     "Could not delete table. Reason: %s: %s",
            #     err.response['Error']['Code'], err.response['Error']['Message']
            # )
            raise err
        except self.dynamodb.exceptions.ParamValidationError as error:
            raise ValueError('The parameters provided are incorrect: {}'.format(error))

    def __get_calibration_information(
            self
    ) -> pd.DataFrame:
        # Calibration data generated by Chuck currently located here:
        #      https://noaa-wcsd-pds-index.s3.amazonaws.com/calibrated_crusies.csv
        response = self.s3.get_object(Bucket=self.calibration_bucket, Key=self.calibration_key)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        calibration_status = pd.DataFrame(columns=["DATASET_NAME", "INSTRUMENT_NAME", "CAL_STATE"])
        if status == 200:
            calibration_status = pd.read_csv(response.get("Body"))
            calibration_status['DATASET_NAME'] = calibration_status['DATASET_NAME'].apply(lambda x: x.split('_EK60')[0])
            # Note: Data are either:
            #      [1] Calibrated w/ calibration data
            #      [2] Calibrated w/o calibration data
            #      [3] uncalibrated
            calibration_status['CAL_STATE'] = calibration_status['CAL_STATE'].apply(lambda x: x.find('Calibrated') >= 0)
        else:
            print(f"Unsuccessful S3 get_object response. Status - {status}")
        return calibration_status

    def execute(self):
        start = datetime.now()  # used for benchmarking
        # Get all object in public dataset bucket
        all_objects = self.__get_all_objects()
        #
        subset_ek60_by_prefix = self.__get_subset_ek60_prefix(
            df=all_objects[all_objects['Key'].str.contains('EK60')][['Key', 'Size']]
        )
        subset_datagrams = self.__get_subset_datagrams(df=subset_ek60_by_prefix)
        ek60_objects = self.__get_ek60_objects(subset_ek60_by_prefix, subset_datagrams)
        print(start)  # 1:26:57 to 1:39:??
        #
        current_tables = self.dynamodb.list_tables()
        if self.index_ek60_table_name in current_tables['TableNames']:
            print('deleting existing table')
            self.__delete_table()

        # create new index table
        self.__create_table()
        calibration_status = self.__get_calibration_information()
        #
        # TODO: melt calibration_status with
        # ek60_objects['CALIBRATED'] = np.repeat(False, ek60_objects.shape[0])
        # cruises = list(set(ek60_objects['CRUISE']))
        # for i in cruises:
        #     print(i)
        #     if i in list(calibration_status['DATASET_NAME']):
        #         ek60_objects.loc[ek60_objects['CRUISE'] == i, 'CALIBRATED'] = True
        # ek60_objects['CALIBRATED'].value_counts()
        #
        cruise_names = list(set(ek60_objects['CRUISE']));
        cruise_names.sort()
        for cruise_name in cruise_names:  # ~322 cruises
            cruise_data = ek60_objects.groupby('CRUISE').get_group(cruise_name)
            ship = cruise_data['SHIP'].iloc[0]
            sensor = cruise_data['SENSOR'].iloc[0]
            datagram = cruise_data['DATAGRAM'].iloc[0]
            file_count = cruise_data.shape[0]
            total_size = np.sum(cruise_data['SIZE'])
            calibrated = cruise_name in calibration_status['DATASET_NAME'].unique()  # ~276 entries
            start_date = np.min(cruise_data['DATE']).isoformat(timespec="seconds") + "Z"
            end_date = np.max(cruise_data['DATE']).isoformat(timespec="seconds") + "Z"
            #
            self.dynamodb.put_item(  # TODO: verify status_code['ResponseMetadata']['HTTPStatusCode'] == 200
                TableName=self.index_ek60_table_name,
                Item={
                    'CRUISE': {'S': cruise_name},
                    'SHIP': {'S': ship},
                    'SENSOR': {'S': sensor},
                    'DATAGRAM': {'S': datagram},
                    'FILE_COUNT': {'N': str(file_count)},
                    'TOTAL_SIZE': {'N': str(total_size)},  # 'SIZE_BYTES'
                    'CALIBRATED': {'S': str(calibrated)},
                    'START_DATE': {'S': start_date},
                    'END_DATE': {'S': end_date},
                    # 'STATUS': {'S': _}
                }
            )
        end = datetime.now()  # used for benchmarking
        print(start)
        print(end)

