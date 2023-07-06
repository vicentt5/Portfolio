import findspark
findspark.init()

from pyspark import SparkContext
from pyspark.streaming import StreamingContext

#Cambiad el username por vuestro nombre de usuario
sc = SparkContext("local[2]", "top_words_vripollr")
sc.setLogLevel("ERROR")

ssc = StreamingContext(sc, 5)
ssc.checkpoint("checkpoint")

lines = ssc.socketTextStream("localhost", 20216)

words = lines.flatMap(lambda x: x.split(" "))
#Transforma el DStream palabras en un DStream tuplas, con un valor de 1 para cada palabra
kv = words.map(lambda x: (x, 1))

#Aqui se contaran el numero de palabras en modo StateLess
#https://stackoverflow.com/questions/41171319/spark-steaming-updatestatebykey-values-from-previous-microbatch-when-no-new-such
word_count = kv.reduceByKey(lambda x, y: x + y)\
                        .updateStateByKey(lambda x, y: sum(x) + (y or 0))
#Aqui se ordenan en orden descendiente
sorted_word_count = word_count.transform(lambda x: x.sortBy(lambda x:-x[1]))
#Muestra por pantalla el número de veces que aparece cada palabra en el RDD
sorted_word_count.pprint(5)

ssc.start()
ssc.awaitTermination()