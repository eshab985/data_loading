This Django application performs loading of data from a chosen csv file to Postgres database table.
First a mapping from the datatypes inferred from the csv files to Postgres datatypes is generated. Primary key and other table constraints like FOREIGN KEY , CHECK constraints can be mentioned.
Data uploading is governed by the mapping json 
