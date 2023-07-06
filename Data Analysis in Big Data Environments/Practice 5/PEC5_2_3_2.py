"""
Programa que muestra exclusivamente las entradas via stream socket capturadas mediante Structured Streaming 
 Para ponerlo en marcha utilizamos netcat

`$ nc -lk <vuestro puerto>`
 y ejecutamos con 
    `$ python3 PEC5_2_1_0.py localhost <vuestro puerto>`
"""
import time
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
    vuelosdf = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "Cloudera02:9092").option("subscribe", "PEC5vripollr").load()
    

    # Separamos las linias en palabras
    #words = lines.select(lines.value,lines.timestamp)
    
    #windowedCounts = lines.groupBy(window(lines.timestamp, "10 seconds", "5 seconds"),lines.value).count().drop('count').orderBy('value')
    vuelosdf.printSchema()

    # Start running the query that prints the windowed word counts to the console
    vuelosdf.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .writeStream \
    .option("truncate", "false")\
    .format("console") \
    .outputMode("append") \
    .start() \
    .awaitTermination()

