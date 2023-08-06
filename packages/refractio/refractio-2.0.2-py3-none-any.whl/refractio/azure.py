#! -*- coding: utf-8 -*-
"""Class to get Azure connection object and related operations"""

import os
from io import StringIO
import pandas as pd
from .manager import (
    get_conn_details_from_conn_name,
    get_conn_details_from_ds_name,
    validate_project_id,
    default_connection_name
)


class Azure:

    def __init__(self):
        self.__connection_details = None
        self.con_obj = None

    def _get_connection(self):
        try:
            # Connect to Azure Blob
            from azure.storage.blob import BlockBlobService
            # create a BlockBlobService object
            self.con_obj = BlockBlobService(
                account_name=self.__connection_details["params"]["READER_STORAGE"]["account_name"] if self.__connection_details["params"]["READER_STORAGE"].get("account_name") else self.__connection_details["params"]["READER_STORAGE"]["accountName"],
                account_key=self.__connection_details["params"]["READER_STORAGE"]["account_key"] if self.__connection_details["params"]["READER_STORAGE"].get("account_key") else self.__connection_details["params"]["READER_STORAGE"]["accountKey"]
            )
        except Exception as ex:
            print(f"Connection details fetched: {self.__connection_details}")
            print(f"Ex: {ex}")
            raise Exception(f"Exception occurred in creating azure blob connection: "
                            f"{self.__connection_details.get('detailMessage')}")

    def get_connection(self, connection_name=None):
        try:
            # Getting connection
            if self.con_obj is None:
                # Getting default connection name
                if connection_name is None:
                    connection_name = default_connection_name("AZURE")
                    if not connection_name:
                        raise Exception("Could not get the default connection name,"
                                        "please create/pass an active azure blob connection name.")
                self.__connection_details = get_conn_details_from_conn_name(
                    connection_name=connection_name, connection_type="azure")
                self._get_connection()
                print(f"Connection object created: {self.con_obj}")
            else:
                print(f"Existing connection object fetched: {self.con_obj}")

            return self.con_obj
        except Exception as ex:
            print(f"Exception occurred in getting azure blob connection: {ex}")

    def get_dataframe(self, dataset_name, project_id=os.getenv("project_id"), row_count=-1):
        try:
            project_id = validate_project_id(project_id)

            self.__connection_details = get_conn_details_from_ds_name(dataset_name=dataset_name, project_id=project_id)

            # Creating new connection attached to dataset_id for reading the dataset.
            self._get_connection()

            # create a container
            container_name = self.__connection_details["params"]["READER_STORAGE"]["container"]
            self.con_obj.create_container(container_name)

            # get the data from the blob
            blob_name = self.__connection_details["params"]["READER_STORAGE"]["blob_name"]
            blob_data = self.con_obj.get_blob_to_bytes(container_name, blob_name)

            s = str(blob_data.content, 'utf-8')
            data = StringIO(s)
            return pd.read_csv(data, nrows=int(row_count)) if int(row_count) > 0 else pd.read_csv(data)
        except Exception as ex:
            print(f"Exception occurred in reading data_frame from azure blob connection: {ex}")
