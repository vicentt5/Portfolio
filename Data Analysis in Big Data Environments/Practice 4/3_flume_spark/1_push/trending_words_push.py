import json
import findspark
import re
findspark.init()

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.flume import FlumeUtils


sc = SparkContext(appName="FlumeStreaming", master="local[2]")
sc.setLogLevel("ERROR")
ssc = StreamingContext(sc, 5)
ssc.checkpoint("checkpoint")

#recibimos el stream de flume (json)
flumeStream = FlumeUtils.createStream(ssc, 'localhost', 20216)
#lo convertimos a diccionario python con json.loads
tweets_json = flumeStream.map(lambda x: json.loads(x[1]))
#nos quedamos con el texto del tweet
text = tweets_json.map(lambda x:x['text'])
#separamos el texto por palabras
words = text.flatMap(lambda x:x.split(' '))\
            .flatMap(lambda x:x.split('\n'))\
            .flatMap(lambda x:x.split(','))\
            .flatMap(lambda x:x.split('.'))\
            .filter(lambda x:x!='https://t')\
            .filter(lambda x:x!='')\
            .map(lambda x:x.upper())
#transformamos las palabras en una tupla clave-valor para poder realizar el conteo
kv = words.map(lambda x:(x,1))
#usamos reduceByKey para contar las apariciones de una palabra dentro de un mismo tweet
#acumulamos los conteos con los tweets anteriores con updateStateByKey
word_count = kv.reduceByKey(lambda x, y: x + y)\
              .updateStateByKey(lambda x, y: sum(x) + (y or 0))
#ordenamos los conteos en orden descendiente
sorted_word_count = word_count.transform(lambda x: x.sortBy(lambda x:-x[1]))
sorted_word_count.pprint(10)

ssc.start()
ssc.awaitTermination()