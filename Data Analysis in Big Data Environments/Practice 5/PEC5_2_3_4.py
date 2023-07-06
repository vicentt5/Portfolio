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
    
    #ajustamos en número de particiones a 4
    spark.conf.set("spark.sql.shuffle.partitions",4)
    
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
    vuelosdf4 = vuelosdf3.groupBy(col('country')).count().orderBy('country').filter(col('country')!='null')
    
    vuelosdf4.writeStream\
      .format("console")\
      .outputMode("complete")\
      .option('truncate', 'false')\
      .start()\
      .awaitTermination()