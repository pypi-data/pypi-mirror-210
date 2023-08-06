import tempfile
import os

import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook


class PostgresLoader:

    def __init__(self, pg_conn_id):
        self.__pg_conn_id = pg_conn_id

    def __clearTable(self, tableName, schema):
        pgHook = PostgresHook(postgres_conn_id=self.__pg_conn_id)
        sql = f'delete from {schema}.{tableName}'
        pgHook.run(sql=sql)

    def copy_data(self, tuples, tableName, schema, columns, clear=False):
        df = pd.DataFrame(data=tuples, columns=columns);

        pgHook = PostgresHook(postgres_conn_id=self.__pg_conn_id)
        if clear == True:
            self.__clearTable(tableName=tableName, schema=schema)

        tmpFile = tempfile.NamedTemporaryFile(suffix='.csv');
        tmpPath = os.path.realpath(tmpFile.name)

        #each column should be incased in "" to avoid naming conflicts name->"name"
        columnsJoined = ','.join('"'+columnName.lower()+'"' for columnName in columns)


        print(columnsJoined)
        print(df)
        df.to_csv(tmpFile, index=False, header=True)


        sql = f"COPY {schema}.{tableName} ({columnsJoined}) FROM STDIN DELIMITER ',' CSV HEADER"
        print(sql)
        conn = pgHook.get_conn();
        cursor = conn.cursor()
        result = cursor.copy_expert(sql, open(tmpPath, "r"))
        print("StatusMessage: ",cursor.statusmessage)
        print("result: ", result)
        conn.commit()
        conn.close()

    def import_data(self, rows, colNames, tableName, schema, clear=False):
        pgHook = PostgresHook(postgres_conn_id=self.__pg_conn_id)
        if clear == True:
            self.__clearTable(tableName=tableName, schema=schema)
        # sql = PostgresHook._generate_insert_sql(table=schema + '.' +tableName, values=rows[0], target_fields=colNames, replace=False)

        #each column should be incased in "" to avoid naming conflicts name->"name"
        columnsJoined = ','.join('"'+columnName.lower()+'"' for columnName in colNames)
        placeHolderJoined = ', '.join(list(map(lambda x: '%s', range(len(colNames)))))
        sql = f'insert into {schema}.{tableName}({columnsJoined}) values({placeHolderJoined})'
        for row in rows:
            pgHook.run(sql=sql, parameters=row)
        return 0

    def run_function(self, functionName, schema, parameters=[]):
        pgHook = PostgresHook(postgres_conn_id=self.__pg_conn_id)
        placeHolderJoined = ', '.join(list(map(lambda x: '%s', range(len(parameters)))))
        sql = f'select {schema}.{functionName}({placeHolderJoined})'
        result = pgHook.get_first(sql=sql, parameters=parameters)
        return result

    def load_to_tuples(self, tableName, colNames, schema, where=None):
        """
        Reads data from a Postgres table and returns it as a list of tuples.

        :param tableName: The name of the table to read from.
        :param colNames: A list of strings representing the column names to read.
        :param schema: The schema of the table.
        :param where: OPTIONAL. A list of objects representing the column, symbol, and value to filter by.
                    Example: [{ 'column': 'bool', 'symbol': '=', 'value': 0 }, { 'column': 'desc', 'symbol': '<>', 'value': 'test' },{
                                                                                                                                             "column": "desc",
                                                                                                                                             "symbol": "<>",
                                                                                                                                             "value": "\"4\""
                                                                                                                                           }]
                    ATTENTION: types need to match!

        :return: A list of tuples representing the rows in the table.
        """

        # Initialize a PostgresHook to connect to the database
        pgDbHook = PostgresHook(self.__pg_conn_id)

        # Create a string with the lowercase column names separated by commas
        columns = ",".join('"' + columnName.lower() + '"' for columnName in colNames)

        # If a where clause is specified, construct the SQL WHERE clause with the filter conditions + check if value is string or number....
        if len(where) > 0:
            whereClause = "WHERE " + " AND ".join('"' + cond['column'].lower() + '"' + ' ' + cond['symbol'] + ' ' +
                                                (f"'{cond['value']}'" if not str(cond['value']).isdigit() else str(cond['value']))
                                                for cond in where)
        else:
            whereClause = ""

        # Construct the SQL query with the specified table, columns, and WHERE clause
        sql = f"SELECT {columns} FROM {schema}.{tableName} {whereClause}"

        # Execute the SQL query and retrieve the data as a Pandas DataFrame
        df = pgDbHook.get_pandas_df(sql)
        print("Used SQL statement: ", sql)

        # Convert the DataFrame to a list of tuples representing the rows in the table
        return list(df.itertuples(index=False))



    def get_column_names(self, tableName, schema):
        pgHook = PostgresHook(postgres_conn_id=self.__pg_conn_id)
        sql = f'''
        SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = '{schema}'
            AND table_name   = '{tableName}'
            order by ordinal_position;
        '''
        df = pgHook.get_pandas_df(sql=sql)
        columnNames = df['column_name'].tolist()
        print(columnNames)
        return columnNames

