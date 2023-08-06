#! -*- coding: utf-8 -*-
"""Class to get HIVE connection object and related operations"""

import os
import pandas as pd
from .manager import (
    get_conn_details_from_conn_name,
    get_conn_details_from_ds_name,
    validate_project_id,
    default_connection_name,
    get_dataframe_query
)


class Hive:

    def __init__(self):
        self.__connection_details = None
        self.con_obj = None

    def _get_connection(self, user_id):
        try:
            os.environ['USER'] = user_id
            # Connect to Hive
            from impala.dbapi import connect
            self.con_obj = connect(
                # todo: To update the keys here, once we have the connection manager API created for refractio.
                user=self.__connection_details["params"]["READER"].get("user") if self.__connection_details["params"]["READER"].get("user") else self.__connection_details["params"]["READER"].get("dbUserName"),
                password=self.__connection_details["params"]["READER"].get("password") if self.__connection_details["params"]["READER"].get("password") else self.__connection_details["params"]["READER"].get("dbPassword"),
                host=self.__connection_details["params"]["READER"]["host"] if self.__connection_details["params"]["READER"].get("host") else self.__connection_details["params"]["READER"].get("ipAddress"),
                auth_mechanism='PLAIN',
                port=int(self.__connection_details["params"]["READER"]["port"]),
                database=self.__connection_details["params"]["READER"].get("database")
            )
        except Exception as ex:
            print(f"Connection details fetched: {self.__connection_details}")
            print(f"Ex: {ex}")
            raise Exception(f"Exception occurred in creating hive connection: "
                            f"{self.__connection_details.get('detailMessage')}")

    def get_connection(self, connection_name=None, user_id="1001"):
        try:
            # Getting connection
            if self.con_obj is None or not self.con_obj.open:   # todo: need to check, how to validate live connection.
                # Getting default connection name
                if connection_name is None:
                    connection_name = default_connection_name("HIVE")
                    if not connection_name:
                        raise Exception("Could not get the default connection name,"
                                        "please create/pass an active hive connection name.")
                self.__connection_details = get_conn_details_from_conn_name(
                    connection_name=connection_name, connection_type="hive")
                self._get_connection(user_id=user_id)
                print(f"Connection object created: {self.con_obj}\nPlease close the connection after use!")
            else:
                print(f"Existing connection object fetched: {self.con_obj}\nPlease close the connection after use!")

            return self.con_obj
        except Exception as ex:
            print(f"Exception occurred in getting hive connection: {ex}")

    def get_dataframe(self, dataset_name, project_id=os.getenv("project_id"), user_id="1001", row_count=-1):
        try:
            project_id = validate_project_id(project_id)

            self.__connection_details = get_conn_details_from_ds_name(dataset_name=dataset_name, project_id=project_id)
            # Creating new connection attached to dataset_id for reading the dataset.
            self._get_connection(user_id=user_id)

            query = get_dataframe_query(self.__connection_details['params']['READER']['tables'], row_count)     # Get query to fetch details

            data_frame = pd.read_sql(query, self.con_obj)   # Read data from hive

            self.con_obj.close()    # Closing the connection used for reading dataset.
            return data_frame
        except Exception as ex:
            print(f"Exception occurred in reading data_frame from hive connection: {ex}")

    def execute_query(self, query, connection_name=None, user_id="1001"):
        try:
            # Getting connection object
            if self.con_obj is None or not self.con_obj.open:   # todo: need to check, how to validate live connection.
                self.get_connection(connection_name, user_id=user_id)

            data_frame = pd.read_sql(query, self.con_obj)   # Fetch all records in pandas dataframe

            self.con_obj.close()    # Closing the connection
            return data_frame
        except Exception as ex:
            print(f"Exception occurred in execute_query: {ex}")

    def close_connection(self):
        self.con_obj.close()
        print("hive connection closed!")
