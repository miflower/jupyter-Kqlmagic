# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import re
import os

from Kqlmagic.kql_engine import KqlEngine, KqlEngineError
from Kqlmagic.cache_client import CacheClient
from Kqlmagic.kql_proxy import KqlResponse
from Kqlmagic.constants import ConnStrKeys


class CacheEngine(KqlEngine):
    _URI_SCHEMA_NAME = "cache"
    _ALT_URI_SCHEMA_NAMES = [_URI_SCHEMA_NAME, "file"]
    _MANDATORY_KEY = ConnStrKeys.FOLDER
    _VALID_KEYS_COMBINATIONS = [[ConnStrKeys.FOLDER, ConnStrKeys.ALIAS]]

    @classmethod
    def tell_format(cls):
        return """
               {0}://{1}='<foldername>'
               """.format(cls._URI_SCHEMA_NAME, ConnStrKeys.FOLDER)

    # Object constructor
    def __init__(self, conn_str, current=None, **kwargs):
        super().__init__()
        self._parsed_conn = {}
        self.kql_engine = None
        if isinstance(conn_str, KqlEngine):
            self.kql_engine = conn_str
            folder_name = conn_str.get_database() + "_at_" + conn_str.get_cluster()
            conn_str = "{0}://{1}='{2}'".format(self._URI_SCHEMA_NAME, ConnStrKeys.FOLDER, folder_name)
        self._parsed_conn = self._parse_common_connection_str(
            conn_str, current, self._URI_SCHEMA_NAME, self._MANDATORY_KEY, self._ALT_URI_SCHEMA_NAMES, self._VALID_KEYS_COMBINATIONS
        )
        self.client = CacheClient()

        folder_path = self.client._get_folder_path(self.get_database())
        validation_file_path = folder_path + "/" + "validation_file.json"
        if not os.path.exists(validation_file_path):
            outfile = open(validation_file_path, "w")
            outfile.write(self.validate_json_file_content)
            outfile.flush()
            outfile.close()

    def validate(self, **kwargs):
        client = self.get_client()
        if not client:
            raise KqlEngineError("Client is not defined.")
        # query = "range c from 1 to 10 step 1 | count"
        filename = "validation_file.json"
        database = self.get_database()
        response = client.execute(database, filename, accept_partial_results=False, timeout=None)
        # print(response.json_response)
        table = KqlResponse(response, **kwargs).tables[0]
        if table.rowcount() != 1 or table.colcount() != 1 or [r for r in table.fetchall()][0][0] != 10:
            raise KqlEngineError("Client failed to validate connection.")

    validate_json_file_content = """{"Tables": [{"TableName": "Table_0", "Columns": [{"ColumnName": "Count", "DataType": "Int64", "ColumnType": "long"}], "Rows": [[10]]}, {"TableName": "Table_1", "Columns": [{"ColumnName": "Value", "DataType": "String", "ColumnType": "string"}], "Rows": [["{\\"Visualization\\":null,\\"Title\\":null,\\"XColumn\\":null,\\"Series\\":null,\\"YColumns\\":null,\\"XTitle\\":null,\\"YTitle\\":null,\\"XAxis\\":null,\\"YAxis\\":null,\\"Legend\\":null,\\"YSplit\\":null,\\"Accumulate\\":false,\\"IsQuerySorted\\":false,\\"Kind\\":null}"]]}, {"TableName": "Table_2", "Columns": [{"ColumnName": "Timestamp", "DataType": "DateTime", "ColumnType": "datetime"}, {"ColumnName": "Severity", "DataType": "Int32", "ColumnType": "int"}, {"ColumnName": "SeverityName", "DataType": "String", "ColumnType": "string"}, {"ColumnName": "StatusCode", "DataType": "Int32", "ColumnType": "int"}, {"ColumnName": "StatusDescription", "DataType": "String", "ColumnType": "string"}, {"ColumnName": "Count", "DataType": "Int32", "ColumnType": "int"}, {"ColumnName": "RequestId", "DataType": "Guid", "ColumnType": "guid"}, {"ColumnName": "ActivityId", "DataType": "Guid", "ColumnType": "guid"}, {"ColumnName": "SubActivityId", "DataType": "Guid", "ColumnType": "guid"}, {"ColumnName": "ClientActivityId", "DataType": "String", "ColumnType": "string"}], "Rows": [["2018-09-17T01:45:07.5325114Z", 4, "Info", 0, "Query completed successfully", 1, "21d61568-0a1a-41e2-ab8c-7a85992a1f3b", "21d61568-0a1a-41e2-ab8c-7a85992a1f3b", "8a9c6cc6-f723-431f-9396-4c91ec9a8837", "9dff54f7-dd4c-445f-89e1-02b50661086e"], ["2018-09-17T01:45:07.5325114Z", 6, "Stats", 0, "{\\"ExecutionTime\\":0.0,\\"resource_usage\\":{\\"cache\\":{\\"memory\\":{\\"hits\\":0,\\"misses\\":0,\\"total\\":0},\\"disk\\":{\\"hits\\":0,\\"misses\\":0,\\"total\\":0}},\\"cpu\\":{\\"user\\":\\"00:00:00\\",\\"kernel\\":\\"00:00:00\\",\\"total cpu\\":\\"00:00:00\\"},\\"memory\\":{\\"peak_per_node\\":0}},\\"input_dataset_statistics\\":{\\"extents\\":{\\"total\\":0,\\"scanned\\":0},\\"rows\\":{\\"total\\":0,\\"scanned\\":0}},\\"dataset_statistics\\":[{\\"table_row_count\\":1,\\"table_size\\":8}]}", 1, "21d61568-0a1a-41e2-ab8c-7a85992a1f3b", "21d61568-0a1a-41e2-ab8c-7a85992a1f3b", "8a9c6cc6-f723-431f-9396-4c91ec9a8837", "9dff54f7-dd4c-445f-89e1-02b50661086e"]]}, {"TableName": "Table_3", "Columns": [{"ColumnName": "Ordinal", "DataType": "Int64", "ColumnType": "long"}, {"ColumnName": "Kind", "DataType": "String", "ColumnType": "string"}, {"ColumnName": "Name", "DataType": "String", "ColumnType": "string"}, {"ColumnName": "Id", "DataType": "String", "ColumnType": "string"}, {"ColumnName": "PrettyName", "DataType": "String", "ColumnType": "string"}], "Rows": [[0, "QueryResult", "PrimaryResult", "1bd5362f-e1f6-4258-abb3-9c2fedca8bdb", ""], [1, "QueryProperties", "@ExtendedProperties", "b1f9ef32-f6f7-4304-9e94-616a3472fb7e", ""], [2, "QueryStatus", "QueryStatus", "00000000-0000-0000-0000-000000000000", ""]]}]}"""