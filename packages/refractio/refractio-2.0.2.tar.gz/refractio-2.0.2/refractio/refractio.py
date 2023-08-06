#! -*- coding: utf-8 -*-
"""Library to read and write dataframes"""

import os
import requests
import pandas as pd

from .manager import validate_project_id


def get_dataframe(ds_name, project_id=os.getenv("project_id"), row_count=-1, strategy="top", user_id="1001"):
    """
    Param:
        ds_name,
        project_id=os.getenv("project_id"),
        row_count=-1,
        strategy="top"
        user_id="1001"
    To get pandas dataframe.
    Need to install mosaic-connector-python for reading dataframe using connector backend,
    git+https://gitlab+deploy-token-14:myUpFE_XRxShG53Hs6tV@git.lti-aiq.in/mosaic-decisions-2-0/mosaic-connector-python.git@1.0.29.3
    """
    try:
        project_id = validate_project_id(project_id)
        url = f"http://connection-manager:80/connections/api/External/v1/external/getConnConfig/" \
              f"{ds_name}/refract_user/{project_id}"    # user id hard coded, as it's not being used in API code.
        connection_details = requests.get(url, verify=False).json()

        if connection_details["params"]["READER"]["type"] == "RDBMS":
            if connection_details["params"]["READER"]["sub_type"] == "SNOWFLAKE":
                data_frame = get_snowflake_df(connection_details, row_count, strategy)
            elif connection_details["params"]["READER"]["sub_type"] == "MYSQL":
                data_frame = get_mysql_df(connection_details, row_count, strategy)
            elif connection_details["params"]["READER"]["sub_type"] == "HIVE":
                data_frame = get_hive_df(connection_details, row_count, strategy, user_id)
            else:
                print("Reading dataframe using connector backend")
                # Need to install, git+https://gitlab+deploy-token-14:myUpFE_XRxShG53Hs6tV@git.lti-aiq.in/mosaic-decisions-2-0/mosaic-connector-python.git
                from connector.mosaicio import MosaicioConnector
                connector = MosaicioConnector()
                data_frame = connector.getPandasDataFrame(
                    param=connection_details["params"],
                    row_count=row_count,
                    strategy=strategy
                )
        elif connection_details["params"]["READER"]["type"] == "FILE":
            if connection_details["params"]["READER_STORAGE"]["type"] == "AMAZONS3":
                data_frame = get_s3_df(connection_details, row_count, strategy)
            elif connection_details["params"]["READER_STORAGE"]["type"] == "AZURE":
                data_frame = get_azureblob_df(connection_details, row_count, strategy)
            elif connection_details["params"]["READER_STORAGE"]["type"] == "SFTP":
                data_frame = get_sftp_df(connection_details, row_count, strategy)
        return data_frame
    except Exception as ex:
        print(f'project_id: {project_id}')
        print(f"Connection details fetched: {connection_details}")
        print(f"Exception occurred in get_dataframe: {ex}")


def get_local_dataframe(local_file_path, row_count=-1):
    """
    Param:
        local_file_path,
        row_count
    To read data frame from NAS local file system
    """
    try:
        sub_type = local_file_path.split(".")[-1]
        nrows = row_count if int(row_count) > 0 else None
        if sub_type == "csv":
            return pd.read_csv(filepath_or_buffer=local_file_path,
                               sep=",",
                               nrows=nrows)
        elif sub_type == "tsv":
            return pd.read_csv(filepath_or_buffer=local_file_path,
                               sep="\t",
                               nrows=nrows)
        elif sub_type == "xlsx":
            return pd.read_excel(io=local_file_path,
                                 nrows=nrows,
                                 parse_dates=False,
                                 engine="openpyxl")
        elif sub_type == "xls":
            return pd.read_excel(io=local_file_path,
                                 nrows=nrows,
                                 parse_dates=False)
    except Exception as ex:
        print(f"Exception occurred in get_local_dataframe: {ex}")


def get_snowflake_df(connection_details, row_count, strategy):
    """
    Param:
        connection_details: connection details dict
        row_count: number of rows to be fetched
        strategy: top/bottom
    To read data frame form snowflake connection
    """
    print("Reading dataframe from snowflake native connector")

    import snowflake.connector

    # Connect to Snowflake
    con = snowflake.connector.connect(
        user=connection_details["params"]["READER"]["user"],
        password=connection_details["params"]["READER"]["password"],
        account=connection_details["params"]["READER"]["accountId"],
        database=connection_details["params"]["READER"]["database"],
        role=connection_details["params"]["READER"]["role"],
        cloudPlatform=connection_details["params"]["READER"]["cloudPlatform"],
        schema=connection_details["params"]["READER"]["schema"],
        wareHouse=connection_details["params"]["READER"]["wareHouse"],
        region=connection_details["params"]["READER"]["region"]
    )
    # Create cursor
    cur = con.cursor()
    if int(row_count) > 0:
        # Execute query
        cur.execute(f"SELECT * FROM {connection_details['params']['READER']['tables']} LIMIT {int(row_count)}")
    else:
        cur.execute(f"SELECT * FROM {connection_details['params']['READER']['tables']}")

    # Read results into a pandas DataFrame
    data_frame = cur.fetch_pandas_all()

    # Close cursor and connection
    cur.close()
    con.close()
    return data_frame


def get_hive_df(connection_details, row_count, strategy, user_id):
    """
    Param:
        connection_details: connection details dict
        row_count: number of rows to be fetched
        strategy: top/bottom
        user_id: template image user id
    To read data frame form hive connection
    """
    print("Reading dataframe from hive native connector")

    # Non Kerberos Connection
    from impala.dbapi import connect
    os.environ['USER'] = user_id
    conn = connect(host=connection_details["params"]["READER"]["host"],
                   port=int(connection_details["params"]["READER"]["port"]),
                   auth_mechanism='PLAIN',
                   user=connection_details["params"]["READER"]["user"],
                   password=connection_details["params"]["READER"]["password"],
                   database=connection_details["params"]["READER"]["database"])

    if int(row_count) > 0:
        # Generate query
        query = f"SELECT * FROM {connection_details['params']['READER']['tables']} LIMIT {int(row_count)}"
    else:
        query = f"SELECT * FROM {connection_details['params']['READER']['tables']}"

    # Read data from Hive
    data_frame = pd.read_sql(query, conn)

    # Close the connection
    conn.close()
    return data_frame


def get_mysql_df(connection_details, row_count, strategy):
    """
    Param:
        connection_details: connection details dict
        row_count: number of rows to be fetched
        strategy: top/bottom
    To read data frame form mysql connection
    """
    print("Reading dataframe from mysql native connector")
    import pymysql

    conn = pymysql.connect(host=connection_details["params"]["READER"]["host"],
                           port=int(connection_details["params"]["READER"]["port"]),
                           user=connection_details["params"]["READER"]["user"],
                           passwd=connection_details["params"]["READER"]["password"],
                           db=connection_details["params"]["READER"]["database"])

    if int(row_count) > 0:
        # Generate query
        query = f"SELECT * FROM {connection_details['params']['READER']['tables']} LIMIT {int(row_count)}"
    else:
        query = f"SELECT * FROM {connection_details['params']['READER']['tables']}"
    # Read data fromm mysql
    data_frame = pd.read_sql(query, con=conn)
    # Close connection
    conn.close()
    return data_frame


def get_s3_df(connection_details, row_count, strategy):
    """
    Param:
        connection_details: connection details dict
        row_count: number of rows to be fetched
        strategy: top/bottom
    To read data frame form amazon S3 connection
    """
    print("Reading dataframe from s3 native connector")

    import boto3

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=connection_details["params"]["READER_STORAGE"]["access_key"],
        aws_secret_access_key=connection_details["params"]["READER_STORAGE"]["secret_key"],
    )
    file_name = connection_details["params"]["READER_STORAGE"]["s3_folder"] + "/" + \
                connection_details["params"]["READER_STORAGE"]["file"]
    response = s3_client.get_object(Bucket=connection_details["params"]["READER_STORAGE"]["bucket_name"],
                                    Key=file_name)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        print(f"Successful S3 get_object response. Status - {status}")
        data_frame = pd.read_csv(response.get("Body"), nrows=int(row_count)) if int(row_count) > 0 else pd.read_csv(
            response.get("Body"))
        return data_frame
    else:
        print(f"Unsuccessful S3 get_object response. Status - {status}")


def get_azureblob_df(connection_details, row_count, strategy):
    """
    Param:
        connection_details: connection details dict
        row_count: number of rows to be fetched
        strategy: top/bottom
    To read data frame form azureblob connection
    """
    print("Reading dataframe from azureblob native connector")

    from azure.storage.blob import BlockBlobService
    from io import StringIO

    # create a BlockBlobService object
    blob_service = BlockBlobService(
        account_name=connection_details["params"]["READER_STORAGE"]["account_name"],
        account_key=connection_details["params"]["READER_STORAGE"]["account_key"]
    )

    # create a container
    container_name = connection_details["params"]["READER_STORAGE"]["container"]
    blob_service.create_container(container_name)

    # get the data from the blob
    blob_name = connection_details["params"]["READER_STORAGE"]["blob_name"]
    blob_data = blob_service.get_blob_to_bytes(container_name, blob_name)

    s = str(blob_data.content, 'utf-8')
    data = StringIO(s)
    # read the data
    data_frame = pd.read_csv(data, nrows=int(row_count)) if int(row_count) > 0 else pd.read_csv(data)
    return data_frame


def get_sftp_df(connection_details, row_count, strategy):
    """
    Param:
        connection_details: connection details dict
        row_count: number of rows to be fetched
        strategy: top/bottom
    To read data frame form sftp connection
    """
    print("Reading dataframe from sftp native connector")

    import pysftp
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(host=connection_details["params"]["READER_STORAGE"]["host"],
                           username=connection_details["params"]["READER_STORAGE"]["user"],
                           password=connection_details["params"]["READER_STORAGE"]["password"],
                           cnopts=cnopts) as sftp:
        sftp.get(connection_details["params"]["READER_STORAGE"]["sftp_file_path"])
        file_name = connection_details["params"]["READER_STORAGE"]["sftp_file_path"].split("/")[-1]
        data_frame = pd.read_csv(file_name, nrows=int(row_count)) if int(row_count) > 0 else pd.read_csv(file_name)
        return data_frame


def write_rdbms_dataframe(data_frame, connection_id, data_source, database_name, schema, table_name):
    """
    Param:
        data_frame: data_frame to write to RDBMS
        connection_id: user selected connection_id
        data_source: HIVE, MYSQL, ORACLE, SNOWFLAKE, SQLSERVER, POSTGRES
        database_name: user selected DB name
        schema: user selected schema
        table_name: output table name
    To write data frame using connectors backend code.
    """
    try:
        url = f"http://connection-manager:80/connections/api/ConnectionManager/v1/connection/{connection_id}"
        connection_details = requests.get(url, data=data_source, verify=False).json()
        writer = {
            "WRITER": {
                "sub_type": connection_details["connectionSources"]["connectionType"],
                "type": connection_details["connectionSources"]["sourceName"],
                "user": connection_details["dbUserName"],
                "password": connection_details["dbPassword"],
                "port": connection_details["port"],
                "host": connection_details["ipAddress"],
                "database": database_name,
                "schema": schema,
                "tables": table_name,
                "DATASET_WRITE_MODE": "overwrite",
                "accountId": connection_details.get("accountName"),
                "region": connection_details.get("region"),
                "cloudPlatform": connection_details.get("cloudPlatform"),
                "wareHouse": connection_details.get("wareHouse")
            }
        }
        from connector.mosaicio import MosaicioConnector
        MosaicioConnector().writePandasDataFrame(data_frame, writer)
    except Exception as ex:
        print(f"Exception occurred in write_rdbms_dataframe: {ex}")
