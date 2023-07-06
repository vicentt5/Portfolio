"""
Programa que muestra exclusivamente las entradas via stream socket capturadas mediante Structured Streaming 
 Para ponerlo en marcha utilizamos netcat
    `$ nc -lk <vuestro puerto>`
 y ejecutamos con 
    `$ python3 PEC5_2_1_0.py localhost <vuestro puerto>`
"""
import sys
import findspark
findspark.init()

from pyspark import SparkConf, SparkContext, SQLContext, HiveContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

conf = SparkConf()
conf.setMaster("local[2]") #en local con dos threads
sc = SparkContext(conf=conf)

# Introducid el nombre de la app PEC5_ seguido de vuestro nombre de usuario


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: PEC5_2_1_1 localhost 20216", file=sys.stderr)
        exit(-1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    spark = SparkSession\
        .builder\
        .appName('PEC5_vripollr')\
        .getOrCreate()

    # Creamos el dataframe representando el stream de linias del netcat desde host:port
    lines = spark\
        .readStream\
        .format('socket')\
        .option('host', host)\
        .option('port', port)\
        .option('includeTimestamp', 'true')\
        .load()

    # Separamos las linias en palabras
    words_1 = lines.select(explode(split(lines.value, ' ')).alias('palabra'),lines.timestamp.alias('tiempo'))
    words_2 = words_1.filter(length(words_1.palabra)>=3)
    #words.printSchema()
    
    words_2.createOrReplaceTempView("Tabla")
    words_2_sql = spark.sql("select palabra from Tabla")

    # Start running the query that prints the windowed word counts to the console
    query = words_2_sql\
        .writeStream\
        .outputMode('update')\
        .trigger(processingTime="5 second")\
        .format('console')\
        .start()
        #.option("path", "hdfs://Cloudera01/user/vripollr/prueba2")\
        #.option("checkpointLocation", "checkpoint2")\
    #evitamos que el programa finalice mientras la consulta se ejecuta
    
    query.awaitTermination()