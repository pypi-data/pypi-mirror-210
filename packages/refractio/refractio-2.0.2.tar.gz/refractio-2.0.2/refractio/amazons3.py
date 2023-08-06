#! -*- coding: utf-8 -*-
"""Class to get AmazonS3 connection object and related operations"""

import os
import pandas as pd
from .manager import (
    get_conn_details_from_conn_name,
    get_conn_details_from_ds_name,
    validate_project_id,
    default_connection_name
)


class AmazonS3:

    def __init__(self):
        self.__connection_details = None
        self.con_obj = None

    def _get_connection(self):
        try:
            # Connect to AmazonS3
            import boto3
            self.con_obj = boto3.client(
                "s3",
                aws_access_key_id=self.__connection_details["params"]["READER_STORAGE"]["access_key"] if self.__connection_details["params"]["READER_STORAGE"].get("access_key") else self.__connection_details["params"]["READER_STORAGE"]["accessKey"],
                aws_secret_access_key=self.__connection_details["params"]["READER_STORAGE"]["secret_key"] if self.__connection_details["params"]["READER_STORAGE"].get("secret_key") else self.__connection_details["params"]["READER_STORAGE"]["secretKey"]
            )
        except Exception as ex:
            print(f"Connection details fetched: {self.__connection_details}")
            print(f"Ex: {ex}")
            raise Exception(f"Exception occurred in creating amazon s3 connection: "
                            f"{self.__connection_details.get('detailMessage')}")

    def get_connection(self, connection_name=None):
        try:
            # Getting connection
            if self.con_obj is None:
                # Getting default connection name
                if connection_name is None:
                    connection_name = default_connection_name("AMAZONS3")
                    if not connection_name:
                        raise Exception("Could not get the default connection name,"
                                        "please create/pass an active amazon s3 connection name.")
                self.__connection_details = get_conn_details_from_conn_name(
                    connection_name=connection_name, connection_type="amazons3")
                self._get_connection()
                print(f"Connection object created: {self.con_obj}")
            else:
                print(f"Existing connection object fetched: {self.con_obj}")

            return self.con_obj
        except Exception as ex:
            print(f"Exception occurred in getting amazon s3 connection: {ex}")

    def get_dataframe(self, dataset_name, project_id=os.getenv("project_id"), row_count=-1):
        try:
            project_id = validate_project_id(project_id)

            self.__connection_details = get_conn_details_from_ds_name(dataset_name=dataset_name, project_id=project_id)

            # Creating new connection attached to dataset_id for reading the dataset.
            self._get_connection()

            file_name = self.__connection_details["params"]["READER_STORAGE"]["s3_folder"] + "/" + \
                        self.__connection_details["params"]["READER_STORAGE"]["file"]
            response = self.con_obj.get_object(Bucket=self.__connection_details["params"]["READER_STORAGE"][
                "bucket_name"], Key=file_name)
            status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

            if status == 200:
                print(f"Successful S3 get_object response. Status - {status}")
                return pd.read_csv(response.get("Body"), nrows=int(row_count)) if int(
                    row_count) > 0 else pd.read_csv(response.get("Body"))
            else:
                print(f"Unsuccessful S3 get_object response. Status - {status}")
        except Exception as ex:
            print(f"Exception occurred in reading data_frame from amazon s3 connection: {ex}")
