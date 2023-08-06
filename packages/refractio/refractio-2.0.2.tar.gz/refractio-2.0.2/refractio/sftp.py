#! -*- coding: utf-8 -*-
"""Class to get SFTP connection object and related operations"""

import os
import pandas as pd
from .manager import (
    get_conn_details_from_conn_name,
    get_conn_details_from_ds_name,
    validate_project_id,
    default_connection_name
)


class Sftp:

    def __init__(self):
        self.__connection_details = None
        self.con_obj = None

    def _get_connection(self):
        try:
            # Connect to SFTP
            import pysftp
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            self.con_obj = pysftp.Connection(
                # todo: To update the keys here, once we have the connection manager API created for refractio.
                username=self.__connection_details["params"]["READER_STORAGE"].get("user") if self.__connection_details["params"]["READER_STORAGE"].get("user") else self.__connection_details["params"]["READER_STORAGE"].get("dbUserName"),
                password=self.__connection_details["params"]["READER_STORAGE"].get("password") if self.__connection_details["params"]["READER_STORAGE"].get("password") else self.__connection_details["params"]["READER_STORAGE"].get("dbPassword"),
                host=self.__connection_details["params"]["READER_STORAGE"]["host"] if self.__connection_details["params"]["READER_STORAGE"].get("host") else self.__connection_details["params"]["READER_STORAGE"].get("ipAddress"),
                cnopts=cnopts
            )
        except Exception as ex:
            print(f"Connection details fetched: {self.__connection_details}")
            print(f"Ex: {ex}")
            raise Exception(f"Exception occurred in creating sftp connection: "
                            f"{self.__connection_details.get('detailMessage')}")

    def _active_connection(self):
        try:
            if self.con_obj.listdir():
                return True
        except Exception:
            return False

    def get_connection(self, connection_name=None):
        try:
            # Getting connection
            if self.con_obj is None or not self._active_connection():
                # Getting default connection name
                if connection_name is None:
                    connection_name = default_connection_name("SFTP")
                    if not connection_name:
                        raise Exception("Could not get the default connection name,"
                                        "please create/pass an active sftp connection name.")
                self.__connection_details = get_conn_details_from_conn_name(
                    connection_name=connection_name, connection_type="sftp")
                self._get_connection()
                print(f"Connection object created: {self.con_obj}\nPlease close the connection after use!")
            else:
                print(f"Existing connection object fetched: {self.con_obj}\nPlease close the connection after use!")

            return self.con_obj
        except Exception as ex:
            print(f"Exception occurred in getting sftp connection: {ex}")

    def get_dataframe(self, dataset_name, project_id=os.getenv("project_id"), row_count=-1):
        try:
            project_id = validate_project_id(project_id)

            self.__connection_details = get_conn_details_from_ds_name(dataset_name=dataset_name, project_id=project_id)

            # Creating new connection attached to dataset_id for reading the dataset.
            self._get_connection()

            # Getting the file to current working directory
            self.con_obj.get(self.__connection_details["params"]["READER_STORAGE"]["sftp_file_path"])

            # Extracting the file name
            file_name = self.__connection_details["params"]["READER_STORAGE"]["sftp_file_path"].split("/")[-1]

            # Reading pandas dataframe
            data_frame = pd.read_csv(file_name, nrows=int(row_count)) if int(row_count) > 0 else pd.read_csv(file_name)

            self.con_obj.close()    # Closing the connection used for reading dataset.
            return data_frame
        except Exception as ex:
            print(f"Exception occurred in reading data_frame from sftp connection: {ex}")

    def close_connection(self):
        self.con_obj.close()
        print("sftp connection closed!")
