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
        .outputMode('append')\
        .format('text')\
        .option("path", "hdfs://Cloudera01/user/vripollr/prueba2")\
        .option("checkpointLocation", "checkpoint2")\
        .start()
    #evitamos que el programa finalice mientras la consulta se ejecuta
    
    query.awaitTermination()
    
    
    
    # Creamos el dataframe representando el stream de linias del netcat desde host:port
    #serie = (spark.readStream.format("rate").option("rowsPerSecond", 1).load())

    
    #simula=serie.select(to_timestamp(unix_timestamp("timestamp")+100*col("value")%3).alias("timestamp"),when(col("value")%3==0,"Vigo").otherwise("Barcelona").alias("Ciudades"),(15+col("value")%5).alias("Temperatura"))

    #valores = simula.writeStream.outputMode("append").format("console").start()
    
    #procesa=simula.groupBy("Ciudades").mean("Temperatura")
    
    #consulta = procesa.writeStream.outputMode("complete").format("console").start()

    #simula=lineas.select(to_timestamp(unix_timestamp("timestamp")).alias ("timestamp"))

    # Separamos las linias en palabras
   # words = lines.select(explode(split(lines.value, ' ')).alias('palabra'),lines.timestamp.alias('tiempo'))
    
    #windowedCounts = words.filter(length(words.palabra)>=3).groupBy(words.palabra,window(words.tiempo, "10 minutes", "5 minutes")).count().orderBy('window')
    #windowedCounts = windowedCounts.withColumnRenamed('window', 'tiempo').drop('count')

    # Start running the query that prints the windowed word counts to the console


    #evitamos que el programa finalice mientras la consulta se ejecuta
    
    #consulta.awaitTermination()