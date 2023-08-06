import os
import json
import boto3
import shutil
import botocore
from botocore.config import Config
from botocore.exceptions import ClientError
import numpy as np
from numcodecs import Blosc
import zarr
import pandas as pd
from enum import Enum

ENV = Enum("ENV", ["DEV", "PROD"])
WCSD_BUCKET_NAME = 'noaa-wcsd-pds'
TILE_SIZE = 1024
SECRET_NAME = "NOAA_WCSD_ZARR_PDS_BUCKET"

class LambdaExecutor:

    def __init__(self, environment, prefix, ship_name, cruise_name, sensor_name):
        self.environment=environment,  # DEV or TEST
        self.prefix=prefix,    # unique to each cloudformation deployment
        self.ship_name=ship_name,
        self.cruise_name=cruise_name,
        self.sensor_name=sensor_name
        self.session = boto3.Session()
        max_pool_connections = 128
        self.client_config = botocore.config.Config(max_pool_connections=max_pool_connections)
        # TODO fix me
        # self.transfer_config = boto3.s3.transfer.TransferConfig(
        #     max_concurrency=100,
        #     num_download_attempts=5,
        #     max_io_queue=100,
        #     use_threads=True,
        #     max_bandwidth=None
        # )
        self.transfer_config = None
        self.s3 = self.session.client(service_name='s3', config=self.client_config)  # good



    def __upload_files(self, local_directory, bucket, object_prefix, s3_client):
        # Note: the files are being uploaded to a third party bucket where
        # the credentials should be saved in the aws secrets manager.
        for subdir, dirs, files in os.walk(local_directory):
            for file in files:
                local_path = os.path.join(subdir, file)
                print(local_path)
                s3_key = os.path.join(object_prefix, local_path)
                try:
                    s3_client.upload_file(
                        Filename=local_path,
                        Bucket=bucket,
                        Key=s3_key,
                        Config=self.transfer_config
                    )
                except ClientError as e:
                    # logging.error(e)
                    print(e)


    def __get_secret(self, secret_name):
        # secret_name = "NOAA_WCSD_ZARR_PDS_BUCKET"  # TODO: parameterize
        secretsmanager_client = self.session.client(service_name='secretsmanager')
        try:
            get_secret_value_response = secretsmanager_client.get_secret_value(SecretId=secret_name)
            return json.loads(get_secret_value_response['SecretString'])
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("The requested secret " + secret_name + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                print("The request was invalid due to:", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                print("The request had invalid params:", e)
            elif e.response['Error']['Code'] == 'DecryptionFailure':
                print("The requested secret can't be decrypted using the provided KMS key:", e)
            elif e.response['Error']['Code'] == 'InternalServiceError':
                print("An error occurred on service side:", e)


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
        except:
            print("Some problem was encountered.")
        finally:
            return raw_files


    def __create_zarr_store(self, store_name, width, height, min_echo_range, channel, frequency):
        # Creates an empty Zarr store for cruise level visualization
        compressor = Blosc(cname="zstd", clevel=5, shuffle=Blosc.BITSHUFFLE)
        store = zarr.DirectoryStore(path=store_name)  # TODO: write directly to s3?
        root = zarr.group(store=store, path="/", overwrite=True)
        args = {'compressor': compressor, 'fill_value': np.nan}
        # Coordinate: Time
        root.create_dataset(name="/time", shape=width, chunks=TILE_SIZE, dtype='float32', **args)
        root.time.attrs['_ARRAY_DIMENSIONS'] = ['time']
        # Coordinate: Depth
        root.create_dataset(name="/depth", shape=height, chunks=TILE_SIZE, dtype='float32', **args)
        root.depth.attrs['_ARRAY_DIMENSIONS'] = ['depth']
        root.depth[:] = np.round(
            np.linspace(start=0, stop=min_echo_range * height, num=height),
            decimals=2
        )  # Note: "depth" starts at zero inclusive
        # Coordinates: Channel
        root.create_dataset(name="/channel", shape=len(channel), chunks=1, dtype='str', **args)
        root.channel.attrs['_ARRAY_DIMENSIONS'] = ['channel']
        root.channel[:] = channel
        # Latitude
        root.create_dataset(name="/latitude", shape=width, chunks=TILE_SIZE, dtype='float32', **args)
        root.latitude.attrs['_ARRAY_DIMENSIONS'] = ['time']
        # Longitude
        root.create_dataset(name="/longitude", shape=width, chunks=TILE_SIZE, dtype='float32', **args)
        root.longitude.attrs['_ARRAY_DIMENSIONS'] = ['time']
        # Frequency
        root.create_dataset(name="/frequency", shape=len(frequency), chunks=1, dtype='float32', **args)
        root.frequency.attrs['_ARRAY_DIMENSIONS'] = ['channel']
        root.frequency[:] = frequency
        # Data
        root.create_dataset(
            name="/data",
            shape=(height, width, len(channel)),
            chunks=(TILE_SIZE, TILE_SIZE, 1),
            **args
        )
        root.data.attrs['_ARRAY_DIMENSIONS'] = ['depth', 'time', 'channel']
        # TODO: add metadata from echopype conversion
        zarr.consolidate_metadata(store)
        # foo = xr.open_zarr(f'{cruise_name}.zarr')

    def __get_table_as_dataframe(self, prefix, ship_name, cruise_name, sensor_name):
        # Only successfully processed files will be aggregated into the larger store
        dynamodb = self.session.resource(service_name='dynamodb')
        try:
            # if ENV[environment] is ENV.PROD:
            #     table_name = f"{ship_name}_{cruise_name}_{sensor_name}"
            # else:
            #     table_name = f"{prefix}_{ship_name}_{cruise_name}_{sensor_name}"
            table_name = f"{prefix}_{ship_name}_{cruise_name}_{sensor_name}"
            table = dynamodb.Table(table_name)
            response = table.scan()  # Scan has 1 MB limit on results --> paginate
            data = response['Items']
            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                data.extend(response['Items'])
        except ClientError as err:
            print('Problem finding the dynamodb table')
            raise err
        df = pd.DataFrame(data)
        df_success = df[df['PIPELINE_STATUS'] == 'SUCCESS']
        if df_success.shape[0] == 0:
            raise
        return df_success


    def execute(self):
        #################################################################
        # TODO: Fix this, should write to one bucket variable
        if ENV[self.environment] is ENV.PROD:
            OUTPUT_BUCKET = 'noaa-wcsd-zarr-pds'  # PROD
        else:
            OUTPUT_BUCKET = "noaa-wcsd-pds-index"  # DEV
        #
        df = self.__get_table_as_dataframe(prefix=self.prefix, ship_name=self.ship_name, cruise_name=self.cruise_name, sensor_name=self.sensor_name)
        #################################################################
        # [2] manifest of files determines width of new zarr store
        cruise_channels = list(set([item for sublist in df['CHANNELS'].tolist() for item in sublist]))
        cruise_channels.sort()
        # Note: This values excludes nan coordinates
        consolidated_zarr_width = np.sum(df['NUM_PING_TIME_DROPNA'].astype(int))
        # [3] calculate the max/min measurement resolutions for the whole cruise
        cruise_min_echo_range = float(np.min(df['MIN_ECHO_RANGE'].astype(float)))
        # [4] calculate the largest depth value
        cruise_max_echo_range = float(np.max(df['MAX_ECHO_RANGE'].astype(float)))
        # [5] get number of channels
        cruise_frequencies = [float(i) for i in df['FREQUENCIES'][0]]
        # new_height = int(np.ceil(cruise_max_echo_range / cruise_min_echo_range / tile_size) * tile_size)
        new_height = int(np.ceil(cruise_max_echo_range) / cruise_min_echo_range)
        # new_width = int(np.ceil(total_width / tile_size) * tile_size)
        new_width = int(consolidated_zarr_width)
        #################################################################
        store_name = f"{self.cruise_name}.zarr"
        #################################################################
        if os.path.exists(store_name):
            print(f'Removing local zarr directory: {store_name}')
            shutil.rmtree(store_name)
        #################################################################
        self.__create_zarr_store(
            store_name=store_name,
            width=new_width,
            height=new_height,
            min_echo_range=cruise_min_echo_range,
            channel=cruise_channels,
            frequency=cruise_frequencies
        )
        #################################################################
        if ENV[self.environment] is ENV.PROD:
            # If PROD write to noaa-wcsd-zarr-pds bucket
            secret = self.__get_secret(secret_name=SECRET_NAME)
            s3_zarr_client = boto3.client(
                service_name='s3',
                aws_access_key_id=secret['NOAA_WCSD_ZARR_PDS_ACCESS_KEY_ID'],
                aws_secret_access_key=secret['NOAA_WCSD_ZARR_PDS_SECRET_ACCESS_KEY'],
            )
        else:
            # If DEV write to dev bucket
            s3_zarr_client = boto3.client(service_name='s3')
        #################################################################
        zarr_prefix = os.path.join("data", "processed", self.ship_name, self.cruise_name, self.sensor_name)
        self.__upload_files(
            local_directory=store_name,
            bucket=OUTPUT_BUCKET,
            object_prefix=zarr_prefix,
            s3_client=s3_zarr_client
        )
        # Verify count of the files uploaded
        count = 0
        for subdir, dirs, files in os.walk(store_name):
            count += len(files)
        raw_zarr_files = self.__get_raw_files(
            bucket_name=OUTPUT_BUCKET,
            sub_prefix=os.path.join(zarr_prefix, store_name)
        )
        if len(raw_zarr_files) != count:
            print(f'Problem writing {store_name} with proper count {count}.')
            raise
        if os.path.exists(store_name):
            print(f'Removing local zarr directory: {store_name}')
            shutil.rmtree(store_name)
        #
        print('done')
        #################################################################

