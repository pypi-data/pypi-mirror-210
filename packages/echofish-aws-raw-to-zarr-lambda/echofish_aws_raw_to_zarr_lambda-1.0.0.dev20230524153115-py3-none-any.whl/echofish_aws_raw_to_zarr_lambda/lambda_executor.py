import os
import json
import glob
import shutil
import echopype as ep
import boto3
import botocore
import numpy as np
import pandas as pd
import geopandas
from datetime import datetime
from botocore.config import Config
from botocore.exceptions import ClientError
from enum import Enum


class LambdaExecutor:

    def __init__(self, environment, prefix, ship_name, cruise_name, sensor_name, input_bucket, output_bucket, overwrite):
        self.environment = environment
        self.prefix = prefix
        self.ship_name = ship_name
        self.cruise_name = cruise_name
        self.sensor_name = sensor_name
        self.input_bucket = input_bucket
        self.output_bucket = output_bucket
        self.session = boto3.Session()
        max_pool_connections = 64
        self.client_config = botocore.config.Config(max_pool_connections=max_pool_connections)
        self.s3 = self.session.client(service_name='s3', config=self.client_config)
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            max_concurrency=100,
            num_download_attempts=5,
            max_io_queue=100,
            use_threads=True,
            max_bandwidth=None
        )

        self.overwrite = overwrite

    def __find_child_objects(self, bucket_name, sub_prefix):
        # Find all objects for a given prefix string.
        # Returns list of strings.
        paginator = self.s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=sub_prefix)
        objects = []
        for page in page_iterator:
            objects.extend(page['Contents'])
        return objects

    def __get_raw_files(self, bucket_name, sub_prefix, file_suffix):
        # Get all children files. Optionally defined by file_suffix.
        # Returns empty list if none are found or error encountered.
        print('Getting raw files')
        raw_files = []
        try:
            children = self.__find_child_objects(bucket_name=bucket_name, sub_prefix=sub_prefix)
            if file_suffix is None:
                raw_files = children
            else:
                for i in children:
                    # Note any files with predicate 'NOISE' are to be ignored, see: "Bell_M._Shimada/SH1507"
                    if i['Key'].endswith(file_suffix) and not os.path.basename(i['Key']).startswith('NOISE'):
                        raw_files.append(i['Key'])
                return raw_files
        except ClientError as err:
            print(f"Some problem was encountered: {err}")
        finally:
            return raw_files

    def __create_table(self, prefix, ship_name, cruise_name, sensor_name):
        # HASH: FILE_NAME, RANGE: SENSOR_NAME
        # TODO: TEMPORARY — MOVE TO ORCHESTRATOR
        dynamodb = self.__session.client(service_name='dynamodb')
        table_name = f"{prefix}_{ship_name}_{cruise_name}_{sensor_name}"
        existing_tables = dynamodb.list_tables()['TableNames']
        if table_name not in existing_tables:
            params = {
                'TableName': table_name,
                'KeySchema': [
                    {'AttributeName': 'FILE_NAME', 'KeyType': 'HASH'},
                    {'AttributeName': 'CRUISE_NAME', 'KeyType': 'RANGE'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'FILE_NAME', 'AttributeType': 'S'},
                    {'AttributeName': 'CRUISE_NAME', 'AttributeType': 'S'}
                ],
                'BillingMode': 'PAY_PER_REQUEST',
                'Tags': [
                    {
                        'Key': 'project',
                        'Value': 'echofish'
                    },
                    {
                        'Key': 'created',
                        'Value': datetime.now().isoformat(timespec="seconds") + "Z"
                    }
                ],
            }
            # TODO: create_table returns a dict for validation
            print('Creating table...')
            dynamodb.create_table(**params)
            waiter = dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name)
            print(f"table: {table_name} created")
            # TODO: TEMPORARY — MOVE TO ORCHESTRATOR
        else:
            print('Table exists already.')

    def __get_processing_status(self, prefix, ship_name, sensor_name, file_name, cruise_name):
        # HASH: FILE_NAME, RANGE: SENSOR_NAME
        dynamodb = self.session.client(service_name='dynamodb')
        table_name = f"{prefix}_{ship_name}_{cruise_name}_{sensor_name}"
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                'FILE_NAME': {'S': file_name},  # Partition Key
                'CRUISE_NAME': {'S': cruise_name},  # Sort Key
            },
            AttributesToGet=['PIPELINE_STATUS']
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            if 'Item' in response:
                return response['Item']['PIPELINE_STATUS']['S'] # PROCESSING or SUCCESS
            else:
                return 'NONE'

    def __set_processing_status(self, prefix, ship_name, cruise_name, sensor_name, file_name, new_status):
        # Updates PIPELINE_STATUS via new_status value
        # HASH: FILE_NAME, RANGE: SENSOR_NAME
        dynamodb = self.session.client(service_name='dynamodb')
        table_name = f"{prefix}_{ship_name}_{cruise_name}_{sensor_name}"
        response = dynamodb.put_item(  # TODO: verify status_code['ResponseMetadata']['HTTPStatusCode'] == 200
            TableName=table_name,
            Item={
                'FILE_NAME': {'S': file_name},  # HASH
                'SHIP_NAME': {'S': ship_name},
                'CRUISE_NAME': {'S': cruise_name},
                'SENSOR_NAME': {'S': sensor_name},  # RANGE
                'PIPELINE_TIME': {'S': datetime.now().isoformat(timespec="seconds") + "Z"},
                'PIPELINE_STATUS': {'S': new_status},  # TODO: change to enum
            }
        )
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        assert(status_code == 200), "Unable to update dynamodb table"

    def __delete_all_local_raw_and_zarr_files(self):
        # Used to cleanse the system of any ephemeral files
        for i in ['*.raw*', '*.zarr']:
            for j in glob.glob(i):
                f'Deleting {j}'
                if os.path.isdir(j):
                    shutil.rmtree(j, ignore_errors=True)
                elif os.path.isfile(j):
                    os.remove(j)

    def __get_file_count(self, store_name):
        count = 0  # count number of local zarr files
        for subdir, dirs, files in os.walk(store_name):
            count += len(files)
        return count

    def __write_to_table(self, prefix, cruise_name, sensor_name, ship_name, file_name, zarr_bucket, zarr_path, min_echo_range, max_echo_range, num_ping_time_dropna, start_time, end_time, frequencies, channels):
        # HASH: FILE_NAME, RANGE: SENSOR_NAME
        dynamodb = self.session.client(service_name='dynamodb')
        table_name = f"{prefix}_{ship_name}_{cruise_name}_{sensor_name}"
        response = dynamodb.put_item(  # TODO: verify status_code['ResponseMetadata']['HTTPStatusCode'] == 200
            TableName=table_name,
            Item={
                'FILE_NAME': {'S': file_name},
                'SHIP_NAME': {'S': ship_name},
                'CRUISE_NAME': {'S': cruise_name},
                'SENSOR_NAME': {'S': sensor_name},
                'ZARR_BUCKET': {'S': zarr_bucket},
                'ZARR_PATH': {'S': zarr_path},
                'MIN_ECHO_RANGE': {'N': str(np.round(min_echo_range, 4))},
                'MAX_ECHO_RANGE': {'N': str(np.round(max_echo_range, 4))},
                'NUM_PING_TIME_DROPNA': {'N': str(num_ping_time_dropna)},
                'START_TIME': {'S': start_time},
                'END_TIME': {'S': end_time},
                'PIPELINE_TIME': {'S': datetime.now().isoformat(timespec="seconds") + "Z"},
                'PIPELINE_STATUS': {'S': 'SUCCESS'},
                'FREQUENCIES': {'L': [{'N': str(i)} for i in frequencies]},
                'CHANNELS': {'L': [{'S': i} for i in channels]},
            }
        )
        status_code = response['ResponseMetadata']['HTTPStatusCode']
        #print(f"Status code: {status_code}")
        assert (status_code == 200), "Unable to update dynamodb table"

    def __chunks(self, ll, n):
        # Yields successive n-sized chunks from ll.
        # Needed to delete files in groups of N
        for i in range(0, len(ll), n):
            yield ll[i:i + n]

    def __delete_remote(self, raw_zarr_files, output_bucket, s3_zarr_client):
        # Delete in groups of 100
        objects_to_delete = []
        for raw_zarr_file in raw_zarr_files:
            objects_to_delete.append({'Key': raw_zarr_file['Key']})
        # Delete in groups of 100 -- Boto3 constraint.
        for batch in self.__chunks(objects_to_delete, 100):
            # print(f"0: {batch[0]}, -1: {batch[-1]}")
            deleted = s3_zarr_client.delete_objects(
                Bucket=output_bucket,
                Delete={
                    "Objects": batch
                }
            )
            print(f"Deleted {len(deleted['Deleted'])} files")

    def __upload_files(self, local_directory, bucket, object_prefix, s3_client):
        # Note: the files are being uploaded to a third party bucket where
        # the credentials should be saved in the aws secrets manager.
        for subdir, dirs, files in os.walk(local_directory):
            for file in files:
                local_path = os.path.join(subdir, file)
                print(local_path)
                s3_key = os.path.join(object_prefix, local_path)
                try:
                    # s3 = session.client(service_name='s3', config=client_config)
                    s3_client.upload_file(
                        Filename=local_path,
                        Bucket=bucket,
                        Key=s3_key,
                        Config=self.transfer_config
                    )
                except ClientError as e:
                    # logging.error(e)
                    print(e)

    def __main(self):
        sub_prefix = os.path.join("data", "raw", self.ship_name, self.cruise_name, self.sensor_name)
        raw_files = self.__get_raw_files(
            bucket_name=self.input_bucket,
            sub_prefix=sub_prefix,
            file_suffix='.raw',
        )
        # TODO: Coordinate file updates with dyanmoDB
        self.__create_table(
            prefix=self.prefix,
            ship_name=self.ship_name,
            cruise_name=self.cruise_name,
            sensor_name=self.sensor_name
        )
        # TODO: don't need to loop, process single file at time
        for raw_file in raw_files:
            print(f"Processing: {raw_file}")
            row_split = raw_file.split(os.sep)
            ship_name, cruise_name, sensor_name, file_name = row_split[-4:]  # 'Okeanos_Explorer', 'EX1608', 'EK60'
            zarr_prefix = os.path.join("data", "raw", ship_name, cruise_name, sensor_name)
            store_name = f"{os.path.splitext(file_name)[0]}.zarr"
            #
            processing_status = self.__get_processing_status(prefix=self.prefix, ship_name=ship_name, sensor_name=self.sensor_name, file_name=file_name, cruise_name=cruise_name)
            if processing_status == 'SUCCESS':
                print('Already processed, skipping...')
                continue
            self.__set_processing_status(
                prefix=self.prefix,
                ship_name=ship_name,
                cruise_name=cruise_name,
                sensor_name=sensor_name,
                file_name=file_name,
                new_status="PROCESSING",
            )
            #################################################################
            self.__delete_all_local_raw_and_zarr_files()
            #
            self.s3.download_file(
                Bucket=self.input_bucket,
                Key=raw_file,
                Filename=os.path.basename(raw_file),
                Config=self.transfer_config
            )
            print(f'Opening raw: {file_name}')
            echodata = ep.open_raw(file_name, sonar_model=sensor_name)  # 'EK60'
            if os.path.exists(os.path.basename(raw_file)):
                print(f'Removing existing raw file: {os.path.basename(raw_file)}')
                os.remove(os.path.basename(raw_file))
            print('Compute volume backscattering strength (Sv) from raw data.')
            ds_Sv = ep.calibrate.compute_Sv(echodata)
            frequencies = echodata.environment.frequency_nominal.values
            assert(
                    'latitude' in echodata.platform.variables and 'longitude' in echodata.platform.variables
            ), "GPS coordinates not found."
            latitude = echodata.platform.latitude.values
            longitude = echodata.platform.longitude.values  # len(longitude) == 14691
            # RE time coordinates: https://github.com/OSOceanAcoustics/echopype/issues/656#issue-1219104771
            nmea_times = echodata.platform.time1.values  # len(nmea_times) == 14691
            time1 = echodata.environment.time1.values  # len(sv_times) == 9776
            # Because of differences in measurement frequency, figure out where sv_times match up to nmea_times
            assert(
                    np.all(time1[:-1] <= time1[1:]) and np.all(nmea_times[:-1] <= nmea_times[1:])
            ), "NMEA time stamps are not sorted."
            indices = nmea_times.searchsorted(time1, side="right") - 1
            lat = latitude[indices]
            lat[indices < 0] = np.nan  # values recorded before indexing are set to nan
            lon = longitude[indices]
            lon[indices < 0] = np.nan
            # https://osoceanacoustics.github.io/echopype-examples/echopype_tour.html
            gps_df = pd.DataFrame({'latitude': lat, 'longitude': lon, 'time1': time1}).set_index(['time1'])
            gps_gdf = geopandas.GeoDataFrame(
                gps_df,
                geometry=geopandas.points_from_xy(gps_df['longitude'], gps_df['latitude']),
                crs="epsg:4326"
            )
            # Returns a FeatureCollection with IDs as "time1"
            geo_json = gps_gdf.to_json()
            zarr_path = os.path.join(zarr_prefix, store_name)
            min_echo_range = float(np.nanmin(ds_Sv.echo_range.values[np.nonzero(ds_Sv.echo_range.values)]))
            max_echo_range = float(np.nanmax(ds_Sv.echo_range))
            num_ping_time_dropna = gps_df.dropna().shape[0]
            start_time = np.datetime_as_string(ds_Sv.ping_time.values[0], unit='ms') + "Z"
            end_time = np.datetime_as_string(ds_Sv.ping_time.values[-1], unit='ms') + "Z"
            channels = list(ds_Sv.channel.values)
            #
            if os.path.exists(store_name):
                print(f'Removing existing zarr directory: {store_name}')
                shutil.rmtree(store_name)
            print('Creating Zarr')
            #
            # TODO: will this crash if it doesn't write to /tmp directory
            #
            ds_Sv.to_zarr(store=store_name)
            print('Note: Adding GeoJSON inside Zarr store')
            with open(os.path.join(store_name, 'geo.json'), "w") as outfile:
                outfile.write(geo_json)
            file_count = self.__get_file_count(store_name=store_name)
            #################################################################
            # if ENV[environment] is ENV.PROD:
            #     print("If PROD use external credential to write to noaa-wcsd-zarr-pds bucket")
            #     secret = get_secret(secret_name=SECRET_NAME)
            #     s3_zarr_client = boto3.client(
            #         service_name='s3',
            #         aws_access_key_id=secret['NOAA_WCSD_ZARR_PDS_ACCESS_KEY_ID'],
            #         aws_secret_access_key=secret['NOAA_WCSD_ZARR_PDS_SECRET_ACCESS_KEY'],
            #     )
            # else:
            print("If DEV use regular credentials to write to dev bucket")
            s3_zarr_client = self.session.client(service_name='s3', config=self.client_config)
            #################################################################
            raw_zarr_files = self.__get_raw_files(
                bucket_name=self.output_bucket,
                sub_prefix=os.path.join(zarr_prefix, store_name)
            )
            if len(raw_zarr_files) == file_count and not self.overwrite:
                # if PROCESSING but there are already files there and OVERWRITE is false
                print(f'objects: {store_name} already exist in {self.output_bucket} with proper count {file_count}.')
                self.__write_to_table(
                    prefix=self.prefix,
                    cruise_name=cruise_name,
                    sensor_name=sensor_name,
                    ship_name=ship_name,
                    file_name=file_name,
                    zarr_bucket=self.output_bucket,
                    zarr_path=zarr_path,
                    min_echo_range=min_echo_range,
                    max_echo_range=max_echo_range,
                    num_ping_time_dropna=num_ping_time_dropna,
                    start_time=start_time,
                    end_time=end_time,
                    frequencies=frequencies,
                    channels=channels,
                )
                continue
            if len(raw_zarr_files) > 0:
                print(f'{len(raw_zarr_files)} objects already exist at {store_name} in {self.output_bucket}. Deleting.')
                self.__delete_remote(raw_zarr_files=raw_zarr_files, output_bucket=self.output_bucket, s3_zarr_client=s3_zarr_client)
            #
            print('Uploading files')
            self.__upload_files(
                local_directory=store_name,
                bucket=self.output_bucket,
                object_prefix=zarr_prefix,
                s3_client=s3_zarr_client
            )
            # Verify number of remote zarr files.
            num_raw_files = len(self.__get_raw_files(
                bucket_name=self.output_bucket,
                sub_prefix=os.path.join(zarr_prefix, store_name)
            ))
            if not num_raw_files == file_count:
                raise
            if os.path.exists(store_name):
                print(f'Removing zarr directory: {store_name}')
                shutil.rmtree(store_name)
            #
            # Write to DynamoDB
            #
            self.__write_to_table(
                prefix=self.prefix,
                cruise_name=cruise_name,
                sensor_name=sensor_name,
                ship_name=ship_name,
                file_name=file_name,
                zarr_bucket=self.output_bucket,
                zarr_path=zarr_path,
                min_echo_range=min_echo_range,
                max_echo_range=max_echo_range,
                num_ping_time_dropna=num_ping_time_dropna,
                start_time=start_time,
                end_time=end_time,
                frequencies=frequencies,
                channels=channels,
            )
            #
            print(f'Done processing {raw_file}')

    def execute(self):
        print("Processing bucket: {event['bucket']}, key: {event['key']}.")
        message = "Processing bucket: {event['bucket']}, key: {event['key']}."
        self.__main()
        return {'message': message}
