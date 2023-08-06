#! -*- coding: utf-8 -*-
"""Class to get SNOWFLAKE connection object and related operations"""

import os
from .manager import (
    get_conn_details_from_conn_name,
    get_conn_details_from_ds_name,
    validate_project_id,
    default_connection_name,
    get_dataframe_query
)


class Snowflake:

    def __init__(self):
        self.__connection_details = None
        self.con_obj = None

    def _get_connection(self):
        try:
            # Connect to Snowflake
            import snowflake.connector
            self.con_obj = snowflake.connector.connect(
                # todo: To update the keys here, once we have the connection manager API created for refractio.
                user=self.__connection_details["params"]["READER"].get("user") if self.__connection_details["params"]["READER"].get("user") else self.__connection_details["params"]["READER"].get("dbUserName"),
                password=self.__connection_details["params"]["READER"].get("password") if self.__connection_details["params"]["READER"].get("password") else self.__connection_details["params"]["READER"].get("dbPassword"),
                account=self.__connection_details["params"]["READER"].get("accountId") if self.__connection_details["params"]["READER"].get("accountId") else self.__connection_details["params"]["READER"].get("accountName"),
                database=self.__connection_details["params"]["READER"].get("database"),
                role=self.__connection_details["params"]["READER"]["role"],
                cloudPlatform=self.__connection_details["params"]["READER"]["cloudPlatform"],
                schema=self.__connection_details["params"]["READER"].get("schema"),
                wareHouse=self.__connection_details["params"]["READER"]["wareHouse"],
                region=self.__connection_details["params"]["READER"]["region"]
            )
        except Exception as ex:
            print(f"Connection details fetched: {self.__connection_details}")
            print(f"Ex: {ex}")
            raise Exception(f"Exception occurred in creating snowflake connection: "
                            f"{self.__connection_details.get('detailMessage')}")

    def get_connection(self, connection_name=None):
        try:
            # Getting connection
            if self.con_obj is None or self.con_obj.is_closed():
                # Getting default connection name
                if connection_name is None:
                    connection_name = default_connection_name("SNOWFLAKE")
                    if not connection_name:
                        raise Exception("Could not get the default connection name,"
                                        "please create/pass an active snowflake connection name.")
                self.__connection_details = get_conn_details_from_conn_name(
                    connection_name=connection_name, connection_type="snowflake")
                self._get_connection()
                print(f"Connection object created: {self.con_obj}\nPlease close the connection after use!")
            else:
                print(f"Existing connection object fetched: {self.con_obj}\nPlease close the connection after use!")

            return self.con_obj
        except Exception as ex:
            print(f"Exception occurred in getting snowflake connection: {ex}")

    def get_dataframe(self, dataset_name, project_id=os.getenv("project_id"), row_count=-1):
        try:
            project_id = validate_project_id(project_id)

            self.__connection_details = get_conn_details_from_ds_name(dataset_name=dataset_name, project_id=project_id)
            # Creating new connection attached to dataset_id for reading the dataset.
            self._get_connection()

            cur = self.con_obj.cursor()     # Creating cursor for executing query

            query = get_dataframe_query(self.__connection_details['params']['READER']['tables'], row_count)     # Get query to fetch details

            cur.execute(query)      # Execute query

            data_frame = cur.fetch_pandas_all()     # Fetch all records in pandas dataframe

            cur.close()
            # Closing the connection used for reading dataset.
            self.con_obj.close()
            return data_frame
        except Exception as ex:
            print(f"Exception occurred in reading data_frame from snowflake connection: {ex}")

    def execute_query(self, query, database=None, schema=None, connection_name=None):
        try:
            # Getting connection object
            if self.con_obj is None or self.con_obj.is_closed():
                self.get_connection(connection_name)

            # Creating cursor for executing query
            cur = self.con_obj.cursor()
            if database and schema:
                cur.execute(f"USE {database}.{schema}")     # To select database and schema

            cur.execute(query)  # Execute user query

            data_frame = cur.fetch_pandas_all()     # Fetch all records in pandas dataframe

            cur.close()     # Closing the cursor
            self.con_obj.close()    # Closing the connection
            return data_frame
        except Exception as ex:
            print(f"Exception occurred in execute_query: {ex}")

    def close_connection(self):
        self.con_obj.close()
        print("Snowflake connection closed!")
