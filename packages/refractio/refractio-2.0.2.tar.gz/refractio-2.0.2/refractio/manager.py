#! -*- coding: utf-8 -*-
"""Module to get helping methods for refractio"""

import os
import requests


def get_conn_details_from_conn_name(connection_name, connection_type):
    """
    To get connection details by using connection_name from connection manager API.
    :param connection_name:
    :param connection_type:
    :return: connection_details
    """
    url = f"http://connection-manager:80/connections/api/ConnectionManager/v1/connections?" \
          f"connectionType={connection_type}&name={connection_name}"
    connection_details = requests.get(url, verify=False).json()
    return format_connection_details(connection_details)


def get_conn_details_from_ds_name(dataset_name, project_id):
    """
    To get connection details by using dataset_name and project_id from connection manager API.
    :param dataset_name:
    :param project_id:
    :return: connection_details
    """
    url = f"http://connection-manager:80/connections/api/External/v1/external/getConnConfig/" \
          f"{dataset_name}/refract_user/{project_id}"  # user id hard coded, as it's not being used in API code.
    return requests.get(url, verify=False).json()


def format_connection_details(con_details):
    """
    To format the connection_details in the required format.
    :param con_details:
    :return: formatted connection_details
    """
    connection_details = {}
    if con_details["connectionSources"]["sourceName"] == "RDBMS":
        connection_details = {
            "params": {
                "READER": con_details
            }
        }
    elif con_details["connectionSources"]["sourceName"] in ["CLOUD", "FILE_SYSTEMS", "FILE"]:
        connection_details = {
            "params": {
                "READER_STORAGE": con_details
            }
        }
    return connection_details


def validate_project_id(project_id):
    """
    Validates and returns project_id.
    :param project_id:
    :return: project_id
    """
    if not project_id:
        project_id = os.getenv("PROJECT_ID")
        if not project_id:
            raise Exception(f"Could not read project_id from env, please pass project_id as a keyword argument"
                            f" to get_dataframe method,\nproject_id:{project_id}")
    return project_id


def default_connection_name(datasource):
    """
    To get pick a default connection name created by the user.
    :return: connection_name
    """
    con_name = None
    url = f"http://connection-manager:80/connections/api/ConnectionManager/v1/connection/sourceName?profile=default"
    connection_details = requests.post(url, data=datasource, verify=False).json()

    # Reading username from OS env, will need to make a common variable in env to get current logged-in user id.
    default_user_name = os.getenv("userId") if os.getenv("userId") else (
        os.getenv("MOSAIC_ID") if os.getenv("MOSAIC_ID") else os.getenv("user_id"))

    if default_user_name:
        print(f"User name picked from OS env: {default_user_name}")
        print(f"Fetching connections created by {default_user_name} user")
        con_name = [con['name'] for con in connection_details if
                    (con["createdBy"].lower() if con["createdBy"] else None) == default_user_name.lower()]
        print(f"Connection names fetched {con_name}, created by {default_user_name}")
    else:
        print("Could not get user id from the OS env.")
    return con_name[0] if con_name else None  # first connection name from all the connections created by user_id


def get_dataframe_query(table_name, row_count):
    """
    To get the query to fetch dataframe
    :param table_name:
    :param row_count:
    :return: query
    """
    if int(row_count) > 0:
        print(f"fetching {row_count} records!")
        return f"SELECT * FROM {table_name} LIMIT {row_count}"
    else:
        return f"SELECT * FROM {table_name}"
