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
        .load()

    # Separamos las linias en palabras
    words = lines.select(
        explode(
            split(lines.value, ' ')
        ).alias('palabra')
    )

    wordCounts = words.filter(words.palabra.startswith('a')).filter(length(words.palabra)>=3).groupBy('palabra').count()

    # Ejecutamos la consulta que muestra por consola el word count
    query = wordCounts\
        .writeStream\
        .outputMode('complete')\
        .format('console')\
        .start()
    #evitamos que el programa finalice mientras la consulta se ejecuta

    query.awaitTermination()