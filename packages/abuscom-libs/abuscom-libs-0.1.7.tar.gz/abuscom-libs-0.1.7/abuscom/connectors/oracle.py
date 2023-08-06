from airflow.providers.oracle.hooks.oracle import OracleHook

class OracleLoader:
    def __init__(self, ora_conn_id):
        """
        Constructor that initializes an instance of OracleLoader with a connection ID to an Oracle database.

        :param ora_conn_id: The ID of the Airflow connection to the Oracle database.
        """
        self.ora_conn_id = ora_conn_id
        # Create an OracleHook instance to connect to the database.
        self.ora_hook = OracleHook(oracle_conn_id=self.ora_conn_id)

    def read_interface_from_oracle(self, interface_def):
        """
        Reads data from an Oracle database using a SQL statement specified in the interface definition and returns it as a JSON object.

        :param interface_def: A dictionary containing the interface definition, with the following keys:
            - connectionId: The ID of the Airflow connection to the Oracle database.
            - stmt: The SQL statement to execute.
            - columns: A dictionary mapping the column names in the result set to new column names.

        :return: A JSON object containing the result set.
        """
        # Execute the SQL statement and get a pandas DataFrame with the result set.
        df = self.ora_hook.get_pandas_df(sql=interface_def['stmt'])
        # Rename the columns based on the mapping specified in the interface definition.
        df = df.rename(columns=interface_def['columns'])
        # Convert the DataFrame to a JSON object and return it.
        return df.to_json(orient='records')

    def clear_table(self, tableName):
        """
        Clears all data from a table in the Oracle database.

        :param table_name: The name of the table to clear.
        """
        # Construct the SQL statement to delete all rows from the table.
        sql = f'DELETE FROM {tableName}'
        # Execute the SQL statement.
        self.ora_hook.run(sql=sql)

    def copy_data(self, tuples, tableName, columns, clear=False):
        """
        Inserts a bulk of rows into an Oracle table.

        :param tuples: A list of tuples representing the rows to insert.
        :param table_name: The name of the table to insert the rows into.
        :param columns: A list of strings representing the column names in the table.
        :param clear: A boolean indicating whether to clear the table before inserting the rows.

        :return: 0 if successful.
        """
        # If clear is True, then clear the table before inserting the rows.
        if clear:
            self.clear_table(tableName=tableName)
        # If there are rows to insert, then bulk-insert them using the OracleHook.
        if tuples:
            self.ora_hook.bulk_insert_rows(table=tableName, rows=tuples, target_fields=columns)
        # Return 0 to indicate success.
        return 0

    def load_to_tuples(self, tableName, colNames,where=[]):
        """
        Reads data from an Oracle table and returns it as a list of tuples.

        :param tableName: The name of the table to read from.
        :param colNames: A list of strings representing the column names to read.
        :param where: OPTIONAL. A list of objects representing the column, symbol, and value to filter by.
                    Example: [{ 'column': 'bool', 'symbol': '=', 'value': 0 }, { 'column': 'desc', 'symbol': '<>', 'value': 'test' },{
                                                                                                                                             "column": "desc",
                                                                                                                                             "symbol": "<>",
                                                                                                                                             "value": "\"4\""
                                                                                                                                           }]
                    ATTENTION: types need to match!

        :return: A list of tuples representing the rows in the table.
        """
        if(len(colNames)==0):
            print('No Columns given, return 0')
            return 0
        # Create a string with the uppercase column names separated by commas
        columns = ",".join('"' + columnName.upper() + '"' for columnName in colNames)

        # If a where clause is specified, construct the SQL WHERE clause with the filter conditions + check if value is string or number....
        if len(where) > 0:
            whereClause = "WHERE " + " AND ".join('"' + cond['column'].upper() + '"' + ' ' + cond['symbol'] + ' ' +
                                                (f"'{cond['value']}'" if not str(cond['value']).isdigit() else str(cond['value']))
                                                for cond in where)
        else:
            whereClause = ""

        # Construct the SQL query with the specified table, columns, and WHERE clause
        sql = f"SELECT {columns} FROM {tableName} {whereClause}"

        # Execute the SQL query and retrieve the data as a Pandas DataFrame
        df = self.ora_hook.get_pandas_df(sql)
        print("Used SQL statement: ", sql)

        # Convert the DataFrame to a list of tuples representing the rows in the table
        return list(df.itertuples(index=False))


    def get_column_names(self, tableName):
        """
        Gets all column names of the given table using COLUMN_NAME

        :param table_name: The name of the table to read from.

        :return: A list of ColumnNames representing the columns in the table.
        """
        print(f"Finding Oracle columns with: {tableName}")
        columns_query = f"SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE TABLE_NAME = '{tableName.upper()}'"
        with self.ora_hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(columns_query)
                column_names = [row[0] for row in cur.fetchall()]
        return column_names


