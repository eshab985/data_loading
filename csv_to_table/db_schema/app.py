from flask import Flask, render_template
import psycopg2
dbname = 'cust_transaction'
user = 'postgres'
password = 'user'
port = 5432

connection = psycopg2.connect(dbname=dbname, user=user,password=password)

app = Flask(__name__)


@app.route('/dbtables')
def get_dbschema():   
    cursor = connection.cursor()
    query = "SELECT table_name "\
  "FROM information_schema.tables "\
  "WHERE table_type = 'BASE TABLE' "\
  "AND table_schema NOT IN ('pg_catalog', 'information_schema');"

    cursor.execute(query)
    tables = []
    rows = cursor.fetchall()

    for row in rows:
        tables.append(row[0])
  
    cursor.close()

    return render_template('table_view.html', tables= tables)

@app.route('/schema/<string:table>')
def table_schema(table):
    cursor = connection.cursor()
    query = "SELECT column_name, data_type FROM information_schema.columns "\
        "WHERE table_name = '{0}'".format(table)

    cursor.execute(query)    
    column_names = []
    data_types = []
    for (column_name, data_type) in cursor:
        column_names.append(column_name)
        data_types.append(data_type)

    table_column_dtls = zip(column_names, data_types)
    cursor.close()
    return render_template('tableschema.html', table=table, table_columns_types=table_column_dtls)

if __name__ == '__main__':
    app.run(debug=True)
