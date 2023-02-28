

def get_schema(table, connection):
    
    cursor = connection.cursor()
    query = "SELECT column_name, data_type FROM information_schema.columns "\
        "WHERE table_name = '{0}'".format(table)

    cursor.execute(query)    
    column_names = []
    data_types = []
    for (column_name, data_type) in cursor:
        column_names.append(column_name)
        data_types.append(data_type)

    #table_column_dtls = zip(column_names, data_types)
    cursor.close()

    cursor = connection.cursor()
    query = "SELECT * FROM {0}".format(table)
    cursor.execute(query)
    data = []
    for row in cursor:
        data.append(row)
    cursor.close()
    cursor = connection.cursor()
    query = "SELECT c.column_name "\
        "FROM information_schema.key_column_usage AS c "\
        "LEFT JOIN information_schema.table_constraints AS t "\
        "ON t.constraint_name = c.constraint_name "\
        "WHERE t.table_name = '{0}' AND t.constraint_type = 'PRIMARY KEY';".format(table)

    cursor.execute(query)
    row = cursor.fetchone()
    primary_key = row[0]
    cursor.close()
    return [column_names, data_types, data, primary_key]

def get_tables(connection):
    cursor = connection.cursor()
    query = "SELECT table_name "\
  "FROM information_schema.tables "\
  "WHERE table_type = 'BASE TABLE' "\
  "AND table_schema NOT IN ('pg_catalog', 'information_schema');"

    cursor.execute(query)
    rows = cursor.fetchall()

    tables = []
    for row in rows:
        tables.append(row[0])
    cursor.close()
    return tables

def add_schema(connection, query, table):
    cursor = connection.cursor()
    cursor.execute(query)
    print('Table {0} created successfully'.format(table))
    connection.commit()
    cursor.close()

def get_unique_valued_columns(table, connection):
    query = "SELECT c.column_name "\
        "FROM information_schema.key_column_usage AS c "\
        "LEFT JOIN information_schema.table_constraints AS t "\
        "ON t.constraint_name = c.constraint_name "\
        "WHERE t.table_name = '{0}' AND (t.constraint_type = 'PRIMARY KEY' OR t.constraint_type = 'UNIQUE');".format(table)

    cursor = connection.cursor()
    cursor.execute(query)

    col_names = []
    col_dtypes = []

    rows = cursor.fetchall()
    for row in rows[0]:
        col_names.append(row) 
        datatype_query = "SELECT c.data_type FROM information_schema.columns as c WHERE c.column_name = '{0}'".format(row)
        cursor.execute(datatype_query)
        dtype = cursor.fetchone()[0]
        col_dtypes.append(dtype)
    cursor.close()

    return [col_names, col_dtypes]

def delete_table(connection, table):
    cursor = connection.cursor()
    cursor.execute('DROP TABLE {0}'.format(table))
    cursor.close()