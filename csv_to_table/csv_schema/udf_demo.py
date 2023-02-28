from sqlite3 import Row
import pyspark
import pandas as pd
from pyspark import SQLContext
from pyspark.sql.functions import udf
from pyspark.sql.types import StructType, StructField, FloatType, StringType, IntegerType


def toInt(x):
    if isinstance(x, str) == True:
        st = [str(ord(i)) for i in x]
        return (int(''.join(st)))
    else:
        return None

def toIntEmployee(rdd):
    s = rdd['employee']
    if isinstance(s, str) == True:
        st = [str(ord(i)) for i in s]
        e = int(''.join(st))
    else:
        e = s
    return Row(rdd['sales'], rdd['employee'], rdd['ID'], e)
if __name__ == '__main__':
    '''
        conf = pyspark.SparkConf()

    sc = pyspark.SparkContext.getOrCreate(conf=conf)

    spark = SQLContext(sc)

    schema = StructType([StructField("sales", FloatType(), True),
    StructField("employee", StringType(), True),
    StructField("ID", IntegerType(), True)])

    data = [[10.2, 'Fred', 123]]

    df= spark.createDataFrame(data, schema = schema)

    colsInt = udf(lambda z : toInt(z), IntegerType())

    spark.udf.register("colsInt", colsInt)

    df_applied = df.withColumn('semployee', colsInt('employee'))

    #Usind RDD
    rdd = df.rdd.map(toIntEmployee)
    for x in rdd.collect():
        print(x)
    #print(df_applied.head())
    '''

    '''
    df1 = pd.DataFrame({'a':['a1','a2', 'a3', 'a4'], 'b':['b1','b2','b3','b4']})
    df2 = pd.DataFrame({'a':['a5','a3','a2','a6','a7'], 'B':['b2', 'b3', 'b8', 'b5', 'b1']})

    print('Dataframe 1 :',df1)
    print('Dataframe 2 :',df2)
    print('After concatenating : ')
    print(pd.concat([df1, df2]))
    '''

    df1 = pd.DataFrame({'mag':[101,256,760], 'cat':['A1','A2','A3']})
    df2 = pd.DataFrame({'A1':['E50R', 'T605', 'IR50', 'NaN'], 'A2':['AZ33', 'YYU6', 'POD9', 'YY9I'], 'A3':['REZ3', 'YHGJ', 'BF53', 'NaN']})

    #df.pivot(index='fff', columns='bbb', values=['baa', 'zzz'])

    #df1 = df1.pivot(columns='mag', values = df2)

    df = pd.DataFrame({'name':['Esha', 'Anik', 'Yukta', 'Sabita', 'Yukta','Esha', 'Esha'], 
    'subject':['Physics', 'Chem', 'Chem', 'Maths', 'Physics', 'Maths','Chem'], 
    'marks':[68, 77, 89, 91, 47, 97, 14]})
    df = df.pivot(index=['name'], columns='subject', values='marks')

    print(df.fillna(0))
    '''
    
    output_df = pd.DataFrame(columns = df1['mag'])

    for i, row in df1.iterrows():
        col_name = row['mag']
        ref_column = row['cat']
        output_df[col_name] = df2[ref_column]    

    print('Output datafarme is :')
    print(output_df)
    '''
    


