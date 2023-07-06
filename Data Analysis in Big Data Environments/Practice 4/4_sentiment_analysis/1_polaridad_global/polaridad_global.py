import json
import re
from textblob import TextBlob
import findspark
findspark.init()

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.flume import FlumeUtils


sc = SparkContext(appName="FlumeStreaming", master="local[2]")
sc.setLogLevel("ERROR")

ssc = StreamingContext(sc, 5)
ssc.checkpoint("checkpoint")
flumeStream = FlumeUtils.createStream(ssc, 'localhost', 20216)

#NOS QUEDAMOS CON LOS TWEETS EN INGLES Y EXTRAEMOS EL TEXTO
tweets_json = flumeStream.map(lambda x: json.loads(x[1]))
text_0 = tweets_json.filter(lambda x: x['lang'] == 'en').map(lambda x: x['text'])

#-----------------------PREPROCESADO-----------------------
#QUITAMOS EMOJIS
def remove_emojis(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)

text_1 = text_0.map(lambda x: remove_emojis(x))
#QUITAMOS URLs
text_2 = text_1.map(lambda x: re.sub(r'http\S+', '', x))
#QUITAMOS MENCIONES
text_3 = text_2.map(lambda x: re.sub(r'@\S+', '', x))
#QUITAMOS SALTOS DE LINEA Y SIGNOS DE PUNTUACION
text_4 = text_3.map(lambda x: re.sub(r'[\n,,,.,¿,?,¡,!,:,;,^,(,),…,#,*,-,_,&,%,$]',' ',x))
#REDUCIMOS LOS ESPACIOS MULTIPLES A UN UNICO ESPACIO 
text_5 = text_4.map(lambda x: re.sub(' +', ' ', x))
#AÑADIMOS UN ESPACIO AL PRINCIPIO Y AL FINAL PARA PODER FILTRAR MEJOR LAS STOP WORDS
text_6 = text_5.map(lambda x: ' '+x+' ')
#CONVERTIMOS TODO A MINUSCULAS
text_7 = text_6.map(lambda x: x.lower())
#BORRAMOS STOP WORDS
stop_words = [" a ", " about ", " above ", " after ", " again ", " against ", " all ", " am ", " an ", " and ", " any ", " are ", " aren't ", " as ", " at ", " be ", " because ", " been ", " before ", " being ", " below ", " between ", " both ", " but ", " by ", " can't ", " cannot ", " could ", " couldn't ", " did ", " didn't ", " do ", " does ", " doesn't ", " doing ", " don't ", " down ", " during ", " each ", " few ", " for ", " from ", " further ", " had ", " hadn't ", " has ", " hasn't ", " have ", " haven't ", " having ", " he ", " he'd ", " he'll ", " he's ", " her ", " here ", " here's ", " hers ", " herself ", " him ", " himself ", " his ", " how ", " how's ", " i ", " i'd ", " i'll ", " i'm ", " i've ", " if ", " in ", " into ", " is ", " isn't ", " it ", " it's ", " its ", " itself ", " let's ", " me ", " more ", " most ", " mustn't ", " my ", " myself ", " no ", " nor ", " not ", " of ", " off ", " on ", " once ", " only ", " or ", " other ", " ought ", " our ", " ours ourselves ", " out ", " over ", " own ", " same ", " shan't ", " she ", " she'd ", " she'll ", " she's ", " should ", " shouldn't ", " so ", " some ", " such ", " than ", " that ", " that's ", " the ", " their ", " theirs ", " them ", " themselves ", " then ", " there ", " there's ", " these ", " they ", " they'd ", " they'll ", " they're ", " they've ", " this ", " those ", " through ", " to ", " too ", " under ", " until ", " up ", " very ", " was ", " wasn't ", " we ", " we'd ", " we'll ", " we're ", " we've ", " were ", " weren't ", " what ", " what's ", " when ", " when's ", " where ", " where's ", " which ", " while ", " who ", " who's ", " whom ", " why ", " why's ", " with ", " won't ", " would ", " wouldn't ", " you ", " you'd ", " you'll ", " you're ", " you've ", " your ", " yours ", " yourself ", " yo "]

def remove_sw(input_string):
    for item in stop_words:
        input_string = input_string.replace(item,' ')
    return input_string

text_8 = text_7.map(lambda x: remove_sw(x))
#BORRAMOS EL ESPACIO INICIAL Y EL FINAL
text_9 = text_8.map(lambda x: re.sub(r'^\s+','', x))
text_10 = text_9.map(lambda x: re.sub('\s+\Z','', x))

#-------------------TextBlob-------------------
#CALCULAMOS LA POLARIDAD DEL TWEET Y LE ASIGNAMOS 'positive', 'negative' O 'neutral' EN FUNCION DE SU VALOR
text_polarity = text_10.map(lambda x: 'positive' if TextBlob(x).sentiment.polarity>0 else('negative' if TextBlob(x).sentiment.polarity<0 else('neutral')))
text_polarity_count = text_polarity.map(lambda x: (x, 1))\
                                    .reduceByKeyAndWindow(lambda x, y: x+y, lambda x, y: x-y, 90, 5)\
                                    .transform(lambda rdd: rdd.sortBy(lambda x: -x[1]))
text_polarity_count.pprint()


ssc.start()
ssc.awaitTermination()