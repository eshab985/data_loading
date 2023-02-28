import json
from flask import Flask, render_template, request, jsonify, flash
import os

import psycopg2
import requests
from sqlalchemy import create_engine
import generate_table_schema, generate_csv_schema
import pandas as pd
import datetime
import json

dbname = 'cust_transaction'
user = 'postgres'
password = 'user'
port = 5432

connection = psycopg2.connect(dbname=dbname, user=user,password=password)
engine = create_engine('postgresql+psycopg2://{0}:{1}@127.0.0.1:{2}/{3}'.format(user, password, port, dbname))
dirname = 'D:\\dev\\sample_files'
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = dirname
app.config['MAX_CONTENT_PATH'] = 50 * 1024 * 1024
app.config['SECRET_KEY'] = 'ALT49KEY'

@app.route('/')
def csv_table_view():
    csv_files = []
    mapping_jsons = []
    for files in os.listdir(dirname):
        if files.endswith('.csv'):
            csv_files.append(files)
    #get the mappings
    for file in os.listdir('D:\\dev\\csv_to_table\\csv_schema\\mappings'):
        mapping_jsons.append(file)
    tables = generate_table_schema.get_tables(connection)
    return render_template('firstpage.html', files=csv_files, tables = tables, mappings=mapping_jsons)

@app.route('/getcsvs')
def csv_view():
    files_to_render = []
    for files in os.listdir(dirname):
        if files.endswith('.csv'):
            files_to_render.append(files)
    
    return render_template('index.html', files=files_to_render)

@app.route('/gettables')
def get_tablenames():
    tables = generate_table_schema.get_tables(connection)
    return {'data': tables}

@app.route('/get_table_unique_cols/<name>')
def get_table_columns(name):
    print('Table name got on server = ',name)
    schemaDtls = generate_table_schema.get_unique_valued_columns(name, connection)
    return {'columns' : schemaDtls[0], 'datatypes' : schemaDtls[1]}
@app.route('/render/<string:name>')
def render_csv(name):
    print('Name of file got = ',name)
    with open(os.path.join(dirname, name), 'r') as f:
        return render_template('csv_content.html', content=f.read())

@app.route('/csvschema/<string:csv>')
def get_csv_schema(csv):
    csv_path = os.path.join(dirname, csv)
    schema = generate_csv_schema.get_schema(csv_path)

    return render_template('csv_schema.html', schema=schema)

@app.route('/dbtables')
def get_dbschema():   
    
    tables = generate_table_schema.get_tables(connection)
    
    return render_template('table_view.html', tables= tables)

@app.route('/tableschema/<string:table>')
def table_schema(table):
    table_dtls = generate_table_schema.get_schema(table, connection)
    table_cols_dtls = zip(table_dtls[0],table_dtls[1])
    print('Type of data = ',type(table_dtls[2]))

    data= []
    for row in table_dtls[2]:
        row_dict = dict()
        for i,colname in enumerate(table_dtls[0]):
            row_dict[colname] = row[i]
        print(row_dict)
        data.append(row_dict)
        print(type(row_dict))
        print('----')
    return render_template('tableschema.html', table=table, table_columns_datatypes=table_cols_dtls, data=data, pk = table_dtls[3])

import win32api
@app.route('/delschema/<table>')
def deleteSchema(table):
    generate_table_schema.delete_table(connection, table)
    msg = 'Successfully deleted schema for table {0}'.format(table)
    #win32api.MessageBox(0, msg, 0x00001000)

    return {'message':msg}
@app.route('/mapping/<string:mapping>')
def view_mapping(mapping):
    mapping_path = os.path.join('D:\\dev\\csv_to_table\\csv_schema\\mappings',mapping)
    with open(mapping_path, 'r') as f:
        data = json.load(f)

    source = data['csv']
    target = data['table']
    col_mapping = data['mappings']

    return render_template('mappingview.html', file=mapping, source=source, target=target, mapping=col_mapping)

@app.route('/process',methods=['POST'])
def process_selection():

    data = request.data
    print('Data = ',data)
    csv_table_dict = json.loads(data)
    csv_selected = csv_table_dict['csv']
    table_selected = csv_table_dict['table']
    print('CSV selected = ',csv_selected)
    print('Table selected = ',table_selected)

   

    response = jsonify({'table':table_selected,'csv':csv_selected})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/render_page2/<string:csv>/<string:table>')
def render_second_page(csv, table):
    #get the csv and table schema
    table_schema = generate_table_schema.get_schema(table, connection)
    csv_schema = generate_csv_schema.get_schema(os.path.join(dirname, csv))

    '''
    print('Schema for table ', table)
    for col, dtype in table_schema[0]:
        print(col,'----',dtype)
    '''
    print('Primary key = ',table_schema[3])
    return render_template('secondpage.html', csv=csv, csv_schema=csv_schema, table=table, table_cols=table_schema[0], cols_types = table_schema[1], primary_key=table_schema[3])

@app.route('/merge_csv_to_table', methods=['POST'])
def apply_mapping():
    if request.method == 'POST':
        print('In apply mapping')
        received = request.get_json()
        file = received['mapping_file']
        
        with open(os.path.join('D:\\dev\\csv_to_table\\csv_schema\\mappings',file)) as f:
            data = f.read()
        jsonData = json.loads(data)
        csv = jsonData['csv']
        table = jsonData['table']
        mappings = jsonData['mappings']
        primary_key = jsonData['primary-key']
        #table_df = pd.read_sql("select * from {0} ".format(table), connection)
        csv_df = pd.read_csv(os.path.join(dirname,csv))
        table_df = pd.read_sql_query('SELECT * FROM "{0}"'.format(table), engine)
        print('Table as dataframe :')
        print(table_df)
        csv_primary = mappings[primary_key]

        '''
        Iterate through csv_df  and check if primary key
        '''

        for index,row in csv_df.iterrows():
            ans = hasKey(table_df[primary_key], row[csv_primary])
            if ans[0] == True:
                update(table_df, ans[1], mappings.keys(), row, mappings)
            else:
                insert(table_df, row, mappings)

        table_df.to_sql(name=table, con=engine, if_exists='replace', index=False)
        '''selected_cols = []
        for table_col in mappings.keys():
            selected_cols.append(mappings[table_col])
        csv_df = csv_df[selected_cols]
        for table_col in mappings.keys():
            csv_df.rename(columns={mappings[table_col]:table_col},inplace=True)
        csv_df.to_sql(name=table, con=engine, if_exists='append', index=False)
        '''
        return {'response': 'Mapping applied'}
    return "Made GET request to merge_csv_to_table"


@app.route('/save_mapping', methods=['POST'])
def save_to_json():
    if request.method == 'POST':
        print('Inside save tojson')
        received = json.loads(request.data, strict=False)
        print('Received data = ',received)
        #received = request.get_json()
        table = received['table']
        csv = received['csv']
        
        print('Received CSV : ',csv)
        print('Received table : ',table)
        print('Received mapping : ',received['mappings'])

        
        
        #mappings = received['mappings']
        cur_dt = datetime.datetime.now()
        file_name = "".join([table,'-',csv[0:csv.rfind('.')],'-',(str(cur_dt).replace(' ', '-')).replace(':','-'),'.json'])
        path = os.path.join('D:\\dev\\csv_to_table\\csv_schema\\mappings', file_name)

        with open(path, 'w') as file:
            json.dump(received, file)

    
    return {'response':'Mapping saved in JSON file'}

@app.route('/view_merged_table/<string:table>')
def merged_table_display(table):
    print('Redirected to merge table display')
    query = "select * from {0}".format(table)
    cursor = connection.cursor()
    cursor.execute(query)

    rows = cursor.fetchall()
    print('Printing rows of table {0} after merging csv data'.format(table))
    for row in rows:
        print(row)
    return "Merged"

@app.route('/render_add_schema')
def render_new_schema():
    return render_template('add_table_schema.html')

@app.route('/redirect_upload_csv')
def redirect_add_csv():
    return render_template('add_csv.html')

from werkzeug.utils import secure_filename
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        
        return render_template('acknowledge_csv_upload.html')

@app.route('/add_schema', methods= ['POST'])
def add_schema():
    if request.method == 'POST':
        received = json.loads(request.data, strict=False)

        createCmd = received['create_command']
        print('Received command = ',createCmd)
        generate_table_schema.add_schema(connection, createCmd, received['table'])
    return {'response':'Table created'}


def get_mapped_row(row, mappings):
    ret_row = []
    for key in mappings.key():
        col_name=mappings[key]
        ret_row.append(row[col_name])
    return ret_row

def hasKey(pk_col, csv_pk_val):
    row_num = 0
    for val in pk_col:
        if val == csv_pk_val:
            return [True, row_num]
        row_num = row_num + 1

    return [False]

def update(table_df, table_row_idx, table_cols, csv_row, mapping):
    for col in table_cols:
        table_df.at[table_row_idx,col] = csv_row[mapping[col]]

def insert(table_df,row,mappings):
    inserted_row = []
    for key in mappings:
        print('Table column  : ',key)
        print('CSV column :',mappings[key])
        print('CSV column value :',row[mappings[key]])
        inserted_row.append(row[mappings[key]])
    table_df.loc[len(table_df.index)] = inserted_row
if __name__ == '__main__':
    #get_csv_schema('bank.csv')
    app.run(debug=True)

