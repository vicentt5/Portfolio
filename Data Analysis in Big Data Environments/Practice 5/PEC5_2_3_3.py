"""
Programa que muestra exclusivamente las entradas via stream socket capturadas mediante Structured Streaming 
 Para ponerlo en marcha utilizamos netcat

`$ nc -lk <vuestro puerto>`
 y ejecutamos con 
    `$ python3 PEC5_2_1_0.py localhost <vuestro puerto>`
"""
import json
import time
import sys
import findspark
findspark.init()

from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, LongType, DoubleType
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
    
    schema = StructType([ 
    StructField("longitude",DoubleType(),True),
    StructField("vertical_rate",StringType(),True),
    StructField("country",StringType(),True),
    StructField("callsign",StringType(),True),
    StructField("velocity",DoubleType(),True),
    StructField("latitude",DoubleType(),True)])

    vuelosdf1 = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "Cloudera02:9092").option("subscribe", "PEC5vripollr").load()
    vuelosdf2 = vuelosdf1.selectExpr("CAST(value AS STRING)")
    #vuelosdf2.createOrReplaceTempView("Tabla")
    #vuelosdf3 = spark.sql("select value from Tabla")
    #vuelosdf3.printSchema()
    vuelosdf3 = vuelosdf2.select(from_json(col("value"), schema).alias("data")).select("data.*")


    # Start running the query that prints the windowed word counts to the console
    
    #vuelosdf2.createOrReplaceTempView("Tabla")
    #vuelosdf3 = spark.sql("select value from Tabla")
    
    #vuelosdf4 = vuelosdf3.select(from_json(col("value"), schema).alias("data")).select("data.*")
    
    vuelosdf3.writeStream\
      .format("console")\
      .outputMode("append")\
      .option('truncate', 'false')\
      .start()\
      .awaitTermination()

    # Creamos el dataframe representando el stream de linias del netcat desde host:port
    #vuelosdf = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "Cloudera02:9092").option("subscribe", "PEC5vripollr").load()
    
    #json_edit = vuelosdf.select(from_json("value",schema))
    #vuelosdf.select(from_json("value", schema).alias("json")).collect()
    #vuelosdf = vuelosdf.withColumn("jsonData",from_json(col("value").cast("string"),schema)).collect()

    #vuelosdf = vuelosdf.select(from_json(col("value").cast("string"),schema).alias("parsed"))
    #vuelosdf = vuelosdf.select("parsed.*")
    #query = vuelosdf.writeStream\
     #   .format("console")\
      #  .option("truncate", False)\
       # .start()
