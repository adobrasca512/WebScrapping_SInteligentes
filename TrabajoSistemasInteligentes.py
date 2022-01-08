#!/usr/bin/env python
# coding: utf-8

# In[36]:


from IPython import get_ipython


# In[37]:



#esta es una libreria que me permite manejar fechas, tuve problemas con datetime ya que datetime no reconoce fechas
#acortadas en español, mas no palabras como Diciembre, esas si las reconoce.
get_ipython().system('pip install Arrow')


# In[38]:


get_ipython().system('pip install request-html')


# In[ ]:


pip install --user --install-option="--prefix=" -U scikit-learn


# In[ ]:


pip install --upgrade pip


# In[ ]:


pip install numpy


# In[ ]:


pip install nltk


# In[ ]:


get_ipython().system('python -m nltk.downloader stopwords')


# In[ ]:


pip install textblob


# In[ ]:


pip install tfidf


# In[ ]:


pip install -U scikit-learn scipy matplotlib


# In[ ]:


pip install PorterStemmer


# In[15]:


#web scrapping
from bs4 import BeautifulSoup
import requests
#maneja mi archivo json
import json
#lo uso para remover archivos y no duplicar
import os
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
import arrow
import sys
import unicodedata
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import numpy as np
import numpy.linalg as LA
from nltk.stem.porter import PorterStemmer
import re


# In[64]:


class DataQuery:
    
    def __init__(self,sanidad,ciencia):
        self.sanidad=sanidad
        self.ciencia=ciencia
        self.cosine=[]
    def getSanidad(self):
        return self.sanidad
    def getCiencia(self):
        return self.ciencia
    def lecturaJsonV(self,tema):  
        tema_=tema+'.data.json'
        with open(tema_) as file:
            data = json.load(file)
            file.close()
        return data[tema]
      #TF-IDF
    def getNameArticulos(self,json):
        articulos=[]
        for item in json:
            #titulos= item['titulo'] == self.titulo:
            articulos.append(item['articulo'])
        #print(articulos)
        return articulos
    #con esto unire los nombres de los articulos
    #y unire la query a los articulos
    def unirArrays(self,a,b):
        c=np.append(a,b)
        return c
    #devuelve un array de articulos
    def getAllArticulos(self,json):
        arr_articulos=[]
        for item in json:
            f = open(item, "r", encoding="utf8")
            leer=str(f.read())
            arr_articulos.append(leer.strip('""'))
            f.close()
        return arr_articulos
    #se le pone una lista de documentos mas la query y la query
    #devuelve un vector de documentos con la query insertada en tf
    #lo utilizo para poder calcular la posicion de la query y ver las frecuencias
    #Ejemplo: [[0 1 0 2 3],[0 0 0 1 2]]->frecuencias
    def calcularTF(self,documentos,query):
        #stopwords elimina las palabras frecuentes como: a, el, ella,etc.
        stopWords = stopwords.words('spanish')
        vectorizer = CountVectorizer(stop_words = stopWords)
        vector_documentos = vectorizer.fit_transform(documentos).toarray()
        vector_query = vectorizer.transform(query).toarray()
        #funcion del coseno se le introducen dos valores 
        
        cx = lambda a, b : round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 3)
        i=0
        x=0
        posicionQuery=0
        for vector in vector_documentos:
            #print (vector)
            for testV in vector_query:
                if np.array_equal(vector,testV):
                    #print(vector,'y',testV)
                    posicionQuery=i
                #print (testV)
                cosine = cx(vector, testV)
                #print (cosine)
            i=i+1
        return posicionQuery
    #Funcion que convierte documentos en vectores y calcula la similitud
    #esto facilitara obtener la similitud para poder discriminar mejor 
    #documentos
    def vectorTF_IDF(self,documentos):
        stop=list(stopwords.words('spanish'))
        tfidf_vectorizer = TfidfVectorizer(stop_words=set(stop),tokenizer=stemming_tokenizer,use_idf=True,norm='l2')
        #tfidf_vectorizer2 = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(documentos)
        #tfidf_query = tfidf_vectorizer2.fit_transform(query)
       # cosine = cosine_similarity(tfidf_matrix[x], tfidf_matrix)  #here the first element of tfidf_matrix_train is matched with other three elements
        #print (cosine)
        return tfidf_matrix
    def similitudTF_IDF(self,vector_documento,posicion_query):
        cosine = cosine_similarity(vector_documento[posicion_query], vector_documento)  #here the first element of tfidf_matrix_train is matched with other three elements
        return cosine
    #ordenamos las similitudes coseno en un array y betamos a los que no pertenescan al top
    def sorting(self,cosine,top):
        arr=self.integers(cosine)
        for i in range(len(cosine)):
            for j in range(i + 1,len(cosine)):
                if cosine[i] < cosine[j]:
                    cosine[j],cosine[i] = cosine[i],cosine[j]
                    arr[j],arr[i] = arr[i],arr[j]
        self.cosine=self.solo_Top(cosine,top)
        #print('COSINE:',cosine)
        arr_=[]
        arr_=self.solo_Top(arr,top)
        return arr_
    #aqui sacare los articulos top
    def getArticulosSeleccionados(self,array_posiciones,articulos):
        arr_articulos=[]
        
        
        for posicion in array_posiciones:
           # print('ARTICULO EN POSICION',str(posicion))
           # print('-----------------------------')
            #print(articulos[posicion])
           # print('-----------------------------')
            arr_articulos.append(articulos[posicion])
        #print('LONGITUD ARTICULOS: ',str(len(arr_articulos))) 
        
        return arr_articulos
            
    def integers(self,li):
        arr=[]
        #print('lista')
        #print(li)
        for i in range(len(li)):
            arr.append(i)
        return arr
      #aqui rompo el array y saco solo el top
    #|arr=array recortado
    def solo_Top(self,cosine,top):
        new_arr=[]
        #lo adelanto para no tomar la query
        i=0
        
        cosine.pop(0)
        for i in range(top):
            print(cosine[i])
            new_arr.append(cosine[i])
            i=i+1
        #new_arr.pop(0)
        return new_arr
    
def stemming_tokenizer(str_input):
    porter_stemmer = PorterStemmer()
    words = re.sub(r"[^A-Za-z0-9\-]", " ", str_input).lower().split()
    words = [porter_stemmer.stem(word) for word in words]
    return words


# In[65]:


class Data():
    #la data la obtengo de las paginas, es dependiente
    def __init__(self,webPage):
        self.titulo = []
        self.descripcion = ''
        self.fecha=[]
        self.enlace=[]
        self.articulo=[]
        self.webPage=webPage
        self.etiqueta=[]
        self.max=0
        self.similitudes=[]
        self.other_etiquetas=[]
        self.posicionQuery=0
    #metodo para leer jsons
    def lecturaJson(self):
        with open(self.webPage.getTema()+'.data.json') as file:
            data = json.load(file)
            file.close()
        return data
     #metodo para leer jsons
        
    def lecturaJsonV(tema,self):
        with open(tema+'.data.json') as file:
            data = json.load(file)
            file.close()
        return data[tema]
    #metodo para añadir keys a jsons
    #|key=llave del json
    #|name=valor de la key
    #|posicion=posicion a guardar dentro del json
    def add(self,key,name,posicion):
        data=self.lecturaJson()
        data[self.webPage.getTema()][posicion][key] = name
        with open(self.webPage.getTema()+'.data.json', 'w') as json_file:
            json.dump(data, json_file)
            json_file.close()
    #añado la ubicacion del articulo en el json
    #|name=nombre del valor de la key
    #|posicion=posicion a guardar
    def addTxt(self,name,posicion):
        self.add('articulo',name,posicion)
    #añado las etiquetas al json
    #|name=nombre del valor de la key
    #|posicion=posicion a guardar
    def addEtiqueta(self,etiqueta,posicion):
        self.add('etiquetas',etiqueta,posicion)
    #añado la fecha al json
    #|name=nombre del valor de la key
    #|posicion=posicion a guardar
    def addFecha(self,fecha,posicion):
        self.add('fecha',fecha,posicion)
    #aqui limpio la fecha del articulo para que se vea 05-12-2021 asi
    #|date=fecha string
    def setDate(self,date):
        date1=date.strip('UTC')
        fdate = date1.split('-', 1)[0]
        fecha = arrow.get(fdate, 'DD MMM YYYY',locale='ES')
        d=str(fecha)
        fecha_ = d.split('T', 1)[0]
        return fecha_
    #metodo para extraer valores del json con sus keys
    #|value=array para añadir los items a un array
    #|nombre=la key del json
    def get(self,value,nombre):
        #aqui saco todos los titulos
        data=self.lecturaJson()
        for item in data[self.webPage.getTema()]:
            value.append(item[nombre])
        return value
    #metodo para obtener TODOS los titulos dentro del json
    def getTitulo(self):
        arr=[]
        return self.get(arr,'titulo')
    #metodo para obtener TODAS fecha en el segundo link y guardarlo en el json
    def getFecha(self):
        i=0
        self.enlace=self.getEnlace()
        for link in self.enlace:
            noticia=self.webPage.getRequest(link)
            elements=noticia.find_all('div', class_='a_md_f')
            if elements:
                for item in elements:
                    if item.select('time'):
                        self.fecha.append(self.setDate(self.webPage.parseo(item.select('time'))))
                        self.addFecha(self.fecha[i],i)
                    else:
                        print('no tiene time')
            else: 
                #despues de tanta vaina voy a eliminar los que no siguen el patron que yo tengo
               #caso excepcional para TECNOLOGIA ya que contiene articulos que son ads pero tambien forman parte de los articulos
                #elements=noticia.find_all('div', class_='a_pt | uppercase color_gray_medium_lighter')
                #for item in elements:
                self.fecha.append(datetime.today().strftime('%Y-%m-%d'))
                self.addFecha(self.fecha[i],i)
            i=i+1
        return self.fecha
    #metodo para obtener el enlace dentro del json
    def getEnlace(self):
        #aqui saco todos los titulos
        self.enlace=[]
        return self.get(self.enlace,'enlace')
    #metodo para obtener el articulo dentro del json
    def getArticulo(self):
        i=0
        self.enlace=self.getEnlace()
        for link in self.enlace:
            noticia=self.webPage.getRequest(link)
            elements=noticia.find_all('div', class_='a_c clearfix')
            if elements:    
                for item in elements:
                    self.articulo.append(str(self.webPage.parseo(item.select('p'))))
            else:
                print('no encontrado, FALTA ARTICULO->Reemplazando...')
             #caso excepcional para TECNOLOGIA ya que contiene articulos que son ads pero tambien forman parte de los articulos
                #elements=noticia.find_all('div',class_='a_b article_body | color_gray_dark initial_letter especial a_b__e col desktop_8 tablet_8 mobile_4 margin_center')
                #for item in elements:
                self.articulo.append('Debido a que no es compatible con el Scrapper no se puede mostrar este articulo')
            i=i+1
        return self.articulo
    #metodo obtengo la etiqueda de TODAS las paginas.
    def getEtiqueta(self):
        i=0
        arr_etiquetas=[]
        self.etiqueta=[]
        self.enlace=self.getEnlace()
        for link in self.enlace:
            noticia=self.webPage.getRequest(link)
            elements=noticia.find_all('ul', class_='_df _ls')
            for item in elements:
                e=self.webPage.parseo(item.select('li'))
                arr_etiquetas=e.split(',')
                self.etiqueta.append(arr_etiquetas)
            self.addEtiqueta(arr_etiquetas,i)
            i=i+1
            self.other_etiquetas=self.etiqueta
        return self.etiqueta
    #metodo para guardar el articulo en un TXT
    def saveArticle(self):
        i=0
        #emparejamos titulo y articulo
        self.titulo=self.getTitulo()
        self.articulo=self.getArticulo()
        self.fecha=self.getFecha() 
        #print('TITULO')
        #print(len(self.titulo))
       # print('ARTICULO')
       # print(len(self.articulo))
       # print('FECHAS')
      #  print(len(self.fecha))
        for articulo, titulo,fecha in zip(self.articulo, self.titulo,self.fecha): #obtenemos los valores en cada iteración
            parrafo=titulo+'\n'+articulo
            parrafo_=parrafo.strip("[]")
            tema=self.webPage.getTema()
            nombre=tema+'.'+fecha+'.'+str(i)+'.txt'
            self.addTxt(nombre,i)
            self.webPage.escrituraTexto(parrafo_,nombre)
            i=i+1   
    #cuando el usuario defina el articulo a ver el dato se basara en el articulo seleccionado
    #|titulo=titulo del articulo
    def setTitulo(self,titulo):
        self.titulo=titulo
    #cuando el usuario defina el articulo a ver el dato se basara en el articulo seleccionado
    #|descripcion=descripcion del articulo
    def setDescripcion(self,descripcion):
        self.descripcion=descripcion
    #cuando el usuario defina el articulo a ver el dato se basara en el articulo seleccionado
    #|fecha=fecha del articulo
    def setFecha(self,fecha):
        self.fecha=fecha
    #cuando el usuario defina el articulo a ver el dato se basara en el articulo seleccionado
    #|enlace=enlace del articulo
    def setEnlace(self,enlace):
        self.enlace=enlace
 
    #cuando el usuario defina el articulo a ver el dato se basara en el articulo seleccionado
    #|etiqueta=etiqueta del articulo
    def setEtiqueta(self,etiqueta):
        self.etiqueta=etiqueta
    #setea el valor del top
    #|maxi=top de articulos
    def setMax(self,maxi):
        self.max=maxi
    #aqui leemos exclusivamente un txt
    #|nombre=nombre del articulo
    def lecturaTxt(self,nombre):
        f = open(nombre, "r", encoding="utf8")
        texto=f.read()
        f.close()
        return texto
    #este metodo es para obtener un elemento por su key 
    #|key=llave del json
    def getX(self,key):
        #leo el json
        value=[]
        data=self.lecturaJson()
        #recorro el json y busco su txt
        for item in data[self.webPage.getTema()]:
            #verificamos si la posicion esta en el top
            value.append(item[key])
            #self.similitudes=value
            # me devuelve un array de txt
        return value
    #metodo para mostrar las noticias en el top
    #|posicion_noticia= es la posicion de la noticia a obtener
    def getSimilitud_Paginas(self,posicion_noticia):
        pag_similitud=[]
        articulo=''
        #cargamos el array de textos [texto1.txt,texto2.txt,texto3.txt] hasta la posicion top
        articulos=self.getX('articulo')
        #cuando se seleccione el boton me dira que noticia es: la 1, la 2,etc 
        #leo el texto en la posicion estipulada
        #verifico que el valor sea menor que el maximo
        articulo=self.lecturaTxt(articulos[posicion_noticia])
        #hacemos match con las similitudes
        return articulo
    #TF-IDF
    def getNameArticulos(json,self):
        articulos=[]
        for item in json:
            #titulos= item['titulo'] == self.titulo:
            articulos.append(item['articulo'])
        return articulos
    #con esto unire los nombres de los articulos
    #y unire la query a los articulos
    def unirArrays(a,b,self):
        c=np.append(a,b)
        return c
    #devuelve un array de articulos
    def getAllArticulos(json,self):
        arr_articulos=[]
        for item in json:
            f = open(item, "r", encoding="utf8")
            leer=str(f.read())
            arr_articulos.append(leer.strip('""'))
            f.close()
        return arr_articulos
    #se le pone una lista de documentos mas la query y la query
    #devuelve un vector de documentos con la query insertada en tf
    #lo utilizo para poder calcular la posicion de la query y ver las frecuencias
    #Ejemplo: [[0 1 0 2 3],[0 0 0 1 2]]->frecuencias
    def calcularTF(documentos,query,self):
        #stopwords elimina las palabras frecuentes como: a, el, ella,etc.
        stopWords = stopwords.words('spanish')
        vectorizer = CountVectorizer(stop_words = stopWords)
        vector_documentos = vectorizer.fit_transform(documentos).toarray()
        vector_query = vectorizer.transform(query).toarray()
        #funcion del coseno se le introducen dos valores 
        
        cx = lambda a, b : round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 3)
        i=0
        x=0
        posicionQuery=0
        for vector in vector_documentos:
            print (vector)
            for testV in vector_query:
                if np.array_equal(vector,testV):
                    print(vector,'y',testV)
                    posicionQuery=i
                print (testV)
                cosine = cx(vector, testV)
                print (cosine)
            i=i+1
        return posicionQuery
    #Funcion que convierte documentos en vectores y calcula la similitud
    #esto facilitara obtener la similitud para poder discriminar mejor 
    #documentos
    def vectorTF_IDF(documentos,self):
        tfidf_vectorizer = TfidfVectorizer()
        #tfidf_vectorizer2 = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(documentos)
        #tfidf_query = tfidf_vectorizer2.fit_transform(query)
       # cosine = cosine_similarity(tfidf_matrix[x], tfidf_matrix)  #here the first element of tfidf_matrix_train is matched with other three elements
        #print (cosine)
        return tfidf_matrix
    def similitudTF_IDF(vector_documento,posicion_query,self):
        cosine = cosine_similarity(vector_documento[posicion_query], vector_documento)  #here the first element of tfidf_matrix_train is matched with other three elements
        return cosine
    def mostrarArticulo(self):
        texto=''
        
        #consultamos en el json el nombre del txt
        data=self.lecturaJson()
        for item in data[self.webPage.getTema()]:
            if item['titulo'] == self.titulo:
                texto=item['articulo']
        #abrimos el txt y lo leemos
        f = open(texto, "r", encoding="utf8")
        self.articulo=str(f.read())
        a=self.articulo.strip('""')
        self.articulo=a
        f.close()
        return self.articulo
    #estos son los calculos de la similitud
    #|match=match del array1 con array2
    #ejemplo: [a,b,c]U[d,c,r]=c 1 match
    #|e1=es el array que escogio el usuario
    #|array2= son los otros arrays top
    def calculos(self,e1,array2,match):
       # print('match encontrados',match)
        #print('formula',str(2),'*',str(match),'/',str((len(e1))),'+',str(len(array2)))
        formula=(2*match)/((len(e1))+(len(array2)))
        return formula
    #metodo para rankear la lista, devuelve una lista de las nuevas posiciones de los elementos
    #|li=es el array de similitudes
    def integers(self,li):
        arr=[]
        for i in range(len(li)):
            arr.append(i)
        return arr
    def sorting(self,li):
        arr=self.integers(li)
        for i in range(len(li)):
            for j in range(len(li)):
                if li[i] > li[j]:
                    li[j],li[i] = li[i],li[j]
                    arr[j],arr[i] = arr[i],arr[j]
        self.similitudes=self.solo_Top(li)
        arr_=[]
        arr_=self.solo_Top(arr)
        return arr_
    #esto lo hago solo por si acaso en las similitudes tengo algo ejemplo:
    #[covid-19 enfermedad, covid]U[covid-19, covid] para que no diga que son totalmente iguales o algo asi.
    def eliminarEspacios(self,arr):
        new_arr=[]
        for item in arr:
            a_string=str(item)
            a=a_string.replace(" ", "")
            new_arr.append(a)
        return new_arr
     #aqui rompo el array y saco solo el top
    #|arr=array recortado
    def solo_Top(self,arr):
        new_arr=[]
        i=0
        maxi=self.max
        for item in arr:
            if i<maxi:
                new_arr.append(item)
            else:
                break
            i=i+1
        return new_arr
    #aqui obtengo las similitudes entr etiquetas
    #|e1= es el array que escogio el usuario
    def similitud(self,e2):
        n_noticia=0
        #contador de similitudes
        contador_match=0
        maximo=self.max
        i=0
        e1=self.etiqueta
        e1_=self.eliminarEspacios(e1)
        #print(self.etiqueta)
        resultados=[]
        #aqui sera en el array simple ['comida','perro','gato']
        for array2 in e2:
            contador_match=0
        #solo obtendre las similitudes de los top
            array2_=self.eliminarEspacios(array2)
            #[['comida','perro','avispa'],['azul','perro','can']]  
            for item in array2_:
                #print('entrando en el bucle')
                ##print(item)
                for array1 in e1_:
                    #print('_______________________________________')
                    #print(item,'es igual a',array1)
                    if str(array1) == str(item):
                        contador_match=contador_match+1
                        #print(item,'SI igual a',array1)
                        #print()
                        #print('array encontrado similitud:',array2_)          
                    resultado=self.calculos(e1_,array2_,contador_match)
                    #print('la similitud total es de:',resultado)
                    resultado_=resultado*100
                #añadimos el resultado en un array de similitudes
            i=i+1
            
            resultados.append(resultado_)
            #print(array2)
            #print('grado de similitud con array1',str(resultado_)+'%')
            #print('_______________________________________')
        arr_final=[]
        arr_final=self.sorting(resultados)
        return arr_final
    


# In[66]:


class Usuario():
    def __init__(self, titulo, categoria,top,data):
        self.titulo = titulo
        self.categoria = categoria
        self.data = data
        self.top=top
    #seteamos los campos de datos para que nos muestre los necesarios nada mas
    def cargarSeleccion(self):
        data=self.data.lecturaJson()
        #print('categoria es',self.categoria)
        for item in data[self.categoria]:
            #validamos que la seccion seleccionada este en el json
            if self.titulo  in item['titulo']:
                self.data.setEnlace(item["enlace"]) 
                self.data.setTitulo(item["titulo"])
                self.data.setDescripcion(item["descripcion"]) 
                self.data.setFecha(item["fecha"])
                self.data.setEtiqueta(item["etiquetas"])
                self.data.setMax(self.top)
    def setTop(self,top):
        self.top=top
        self.data.setMax(self.top)


# In[67]:



class WebPages():
    def __init__(self, tema, url):
        self.tema = tema
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
   
    def getRequest(self,url):
        request = requests.get(url, headers=self.headers)
        html = request.content.decode("utf-8")
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    #metodo que escribe un archivo
    #|texto=lo que quieras introducir en el archivo
    #|nombre=nombre del archivo 
    def escritura(self,texto,nombre):
        #si existe un path con este nombre lo quitaremos, evita duplicados
        if os.path.exists(nombre):
            os.remove(nombre)
            #print('este path existe, lo eliminaremos')
        with open(nombre, 'w') as f:
            json.dump(texto, f)
            f.close()
    def escrituraTexto(self,texto,nombre):
        #si existe un path con este nombre lo quitaremos, evita duplicados
        if os.path.exists(nombre):
            os.remove(nombre)
            #print('este path existe, lo eliminaremos')
        file= open(nombre, 'w', encoding='utf-8')
        file.write(texto)
        file.close()
    #parseo: se encarga de pasar el fragmento html a texto
    #|fragmento=pedazo de html ejemplo=<a>...</a> 
    def parseo(self,fragmento):
    #vuelvo string el fragmento html
        word=str(fragmento)
    #remueve los brackets
        parsedword=word.strip("[]")
    #obtengo el texto dentro del html, en caso de que halla texto contenido
        soup1=BeautifulSoup(parsedword, from_encoding='utf-8').get_text()
        return soup1
    #inicia el scrappeo a los primeros links
    def miPais_news_scraper(self):
        article_list={}
        article_list[self.tema]=[]
        soup=self.getRequest(self.url)
    
    # Encontramos todos los articulos necesarios
        elements=soup.find_all('article', class_='c')
    #de todos los articulos iremos revisando item x item.
        for item in elements:
            #aqui es donde tomo los enlaces,titulos,entradillas, fechas y las introduzco en un json
            enlace='https://elpais.com'+item.a['href']
            article_list[self.tema].append({'titulo':self.parseo(item.select('header h2 a')),'enlace':enlace,'descripcion':self.parseo(item.select('p'),),
                                            'fecha':"",'articulo':'','etiquetas':[]} )
            
        return article_list   
        
    #obtengo el tema;sanidad,tecnologia,ciencia.
    def getTema(self):
        return self.tema


# In[68]:


#by Adilem Dobras


# In[69]:


# primero se compila esto: se utiliza para descargar todos los articulos y guardarlos
if __name__ == '__main__':
    #sanidad
    sanidad=WebPages('sanidad','https://elpais.com/noticias/sanidad/' )
    sanidad.escritura(sanidad.miPais_news_scraper(),'sanidad.data.json')
    #tecnologia
    tecnologia=WebPages('tecnologia','https://elpais.com/tecnologia/')
    tecnologia.escritura(tecnologia.miPais_news_scraper(),'tecnologia.data.json')
    #ciencia
    ciencia=WebPages('ciencia','https://elpais.com/ciencia/' )
    ciencia.escritura(ciencia.miPais_news_scraper(),'ciencia.data.json')
    data_sanidad=Data(sanidad)
    data_ciencia=Data(ciencia)
    data_tecnologia=Data(tecnologia)
    data_sanidad.saveArticle() 
    print('Sanidad Descargado 1/3 archivos completados...')
    data_sanidad.getEtiqueta()
    data_ciencia.saveArticle()
    print('Ciencia Descargado 2/3 archivos completados...')
    data_ciencia.getEtiqueta()
    data_tecnologia.saveArticle() 
    print('Tecnología Descargado 3/3 archivos completados...')
    data_tecnologia.getEtiqueta()
    print('Descarga completada...')


# In[59]:


#se compila este para poder mostrar recomendaciones por noticias
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from tkinter import scrolledtext
class R_Noticias(ttk.Frame):
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.grid()
        self.create_widgets()
        self.sort=[]
        self.tema=''
        self.usuario_sanidad=Usuario('','sanidad',5,sanidad)
        self.usuario_tecnologia=Usuario('','tecnologia',5,tecnologia)
        self.usuario_ciencia=Usuario('','ciencia',5,ciencia)
        self.page=''
    def create_widgets(self):
        self.title_lbl = ttk.Label(self,text = "Seleccionar Noticia de Referencia").grid(column = 0, row = 0)
        self.label = ttk.Label(self, text = "Medio").grid(column = 0,
                                                      row = 1)
        self.label1 = ttk.Label(self, text = "Categoria").grid(column = 1,
                                                      row =1)
        
        self.label2 = ttk.Label(self, text = "Noticias").grid(column = 2,row = 1)
        self.combovar = StringVar()
        self.combovar1 = StringVar()
        self.combovar2 = StringVar()
        self.top_text = StringVar()
        self.articulos_similitud = StringVar()
        self.medio = ttk.Combobox(self,textvariable = self.combovar,state = 'readonly')
        self.medio['values'] = ('Medio 1','Mi País','Medio 2')
        self.medio.current(0)
        self.medio.grid(column = 0, row = 2)
        self.categoria = ttk.Combobox(self,textvariable = self.combovar1,state = 'readonly')
        self.categoria['values'] = ('Sanidad','Tecnología','Ciencia')
        self.categoria.grid(column = 1, row = 2)
        self.noticias = ttk.Combobox(self,textvariable = self.combovar2,state = 'readonly')
        self.noticias.grid(column = 2, row = 2)
        self.categoria.bind("<<ComboboxSelected>>", self.selection_changed)
        self.entry_var = tk.StringVar()
        self.noticias.bind("<<ComboboxSelected>>", self.getArticulo)
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=5,
                                      font=("Times New Roman", 15))
        self.text_area.grid(column=0,columnspan=8, row=3,rowspan=2, pady=10, padx=10)
        self.label4 = ttk.Label(self, text = "Top:").grid(column = 0,
                                                      row = 7)
        self.top_items = ttk.Combobox(self,textvariable =  self.top_text,state = 'readonly')
        self.top_items['values'] = (1,2,3,4,5)
        self.top_items.current(4)
        self.top_items.grid(column = 0, row = 8)
        self.top_articulos = ttk.Combobox(self,state = 'readonly')
        self.label4 = ttk.Label(self, text = "Ranking:").grid(column = 2,
                                                      row = 7)
        self.top_articulos.grid(column = 2, row = 8)
        self.top=ttk.Button(self, text="Buscar",command=self.getTop)
        self.top.grid(row=8,column=1)
        self.top_articulos.bind("<<ComboboxSelected>>", self.getOtrosAtriculos)
        self.otras_noticias = scrolledtext.ScrolledText(self, wrap=tk.WORD,height=5,
                                      font=("Times New Roman", 15))
        self.otras_noticias.grid(column=0,columnspan=8, row=10,rowspan=2, pady=10, padx=10)
   
    def selection_changed(self, event):
        if self.categoria.get() in 'Sanidad':
            init_list=data_sanidad.getTitulo()
        elif self.categoria.get() == 'Tecnología':
            init_list=data_tecnologia.getTitulo()
        elif self.categoria.get() == 'Ciencia':
            init_list=data_ciencia.getTitulo()
        lista = [x for x in init_list]
        self.noticias['values'] = lista
        self.noticias.current(0)

        
    def getArticulo(self,event):
        self.text_area.delete(1.0, END)
        if self.categoria.get() in 'Sanidad':
            self.usuario_sanidad=Usuario(self.noticias.get(),'sanidad',5,data_sanidad)
            self.usuario_sanidad.cargarSeleccion()
            self.text_area.insert(END,str(data_sanidad.mostrarArticulo()))
        elif self.categoria.get() == 'Tecnología':
            self.usuario_tecnologia=Usuario(self.noticias.get(),'tecnologia',5,data_tecnologia)
            self.usuario_tecnologia.cargarSeleccion()
            self.text_area.insert(END,data_tecnologia.mostrarArticulo())
        elif self.categoria.get() == 'Ciencia':
            self.usuario_ciencia=Usuario(self.noticias.get(),'ciencia',5,data_ciencia)
            self.usuario_ciencia.cargarSeleccion()
            self.text_area.insert(END,data_ciencia.mostrarArticulo())
    def getTop(self):
        self.top_articulos.set('')
        if self.categoria.get() in 'Sanidad':
            self.usuario_sanidad.setTop(int(self.top_items.get()))
            self.sort=data_sanidad.similitud(data_sanidad.other_etiquetas)
            init_list=data_sanidad.similitudes
        elif self.categoria.get() == 'Tecnología':
            self.usuario_tecnologia.setTop(int(self.top_items.get()))
            self.sort=data_tecnologia.similitud(data_tecnologia.other_etiquetas)
            init_list=data_tecnologia.similitudes
        elif self.categoria.get() == 'Ciencia':
            self.usuario_ciencia.setTop(int(self.top_items.get()))
            self.sort=data_ciencia.similitud(data_ciencia.other_etiquetas)
            init_list=data_ciencia.similitudes
        
        lista = [x for x in init_list]
        self.top_articulos['values'] =lista
        self.top_articulos.current(0)
    def getOtrosAtriculos(self,event):
        self.otras_noticias.delete(1.0, END)
        if self.categoria.get() in 'Sanidad':
            articulo= data_sanidad.getSimilitud_Paginas(self.sort[self.top_articulos.current()])
            self.otras_noticias.insert(END,articulo)
        elif self.categoria.get() == 'Tecnología':
            articulo= data_tecnologia.getSimilitud_Paginas(self.sort[self.top_articulos.current()])
            self.otras_noticias.insert(END,articulo)
        elif self.categoria.get() == 'Ciencia':
            articulo=data_ciencia.getSimilitud_Paginas(self.sort[self.top_articulos.current()])
            self.otras_noticias.insert(END,articulo)
        


# In[60]:


# se compila este para realizar busquedas por noticias
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from tkinter import scrolledtext
class B_Noticias(ttk.Frame):
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.grid()
        self.create_widgets()
        self.tf_idf=DataQuery('sanidad','ciencia')
        self.articulos=[]
    def create_widgets(self):
        """this creates all the objects in the window"""

        self.title_lbl = ttk.Label(self,text = "Busqueda de Noticia").grid(column = 0, row = 0)
        self.label = ttk.Label(self, text = "Consulta:").grid(column = 0,
                                                      row = 1,padx=10, pady=10)
        self.entry = ttk.Entry(self,width=30)
        self.entry.grid(column=1,row=1,padx=10, pady=10)
        self.label1 = ttk.Label(self, text = "Top:").grid(column = 0,
                                                      row = 3, pady=10, padx=10)
        self.combovar = StringVar()
        self.top_items = ttk.Combobox(self,textvariable = self.combovar,state = 'readonly')
        self.top_items['values'] = (1,2,3,4,5)
        self.top_items.current(4)
        self.top_items.grid(column = 1, row = 3)
        self.label2 = ttk.Label(self, text = "Filtrar:").grid(column = 2,
                                                      row = 3)
        self.combovar_medio = StringVar()
        self.medio = ttk.Combobox(self,textvariable = self.combovar_medio,state = 'readonly')
        self.medio['values'] = ('Todos','Medio 1','Mi pais','Medio 3')
        self.medio.current(0)
        self.medio.grid(column = 3, row = 3)
        self.buscar=ttk.Button(self, text="Buscar",command=self.setRanking)
        self.buscar.grid(row=3,column=4)
        self.label3 = ttk.Label(self, text = "Ranking:").grid(column = 0,
                                                      row = 4)
        self.combovar_ranking = StringVar()
        self.ranking = ttk.Combobox(self,textvariable = self.combovar_ranking,state = 'readonly')
        self.ranking.bind("<<ComboboxSelected>>", self.getArticulo)
        self.ranking.grid(column = 0, row = 5)
        self.label3 = ttk.Label(self, text = "Texto de la noticia:").grid(column = 1,
                                                      row = 4)
        self.noticia = scrolledtext.ScrolledText(self, wrap=tk.WORD,height=5,
                                      font=("Times New Roman", 15))
        self.noticia.grid(column=1,columnspan=8, row=5,rowspan=2, pady=10, padx=10)
    def setRanking(self):
        if self.medio.get()=='Mi pais':
            
            #print(tf_idf.getCiencia())
            #abro el json
            json_sanidad=self.tf_idf.lecturaJsonV('sanidad')
            #saco las direcciones de los articulos
            #print(json_sanidad)
            articulos_sanidad=self.tf_idf.getNameArticulos(json_sanidad)
            #abro el json
            json_ciencia=self.tf_idf.lecturaJsonV('ciencia')
            #saco las direcciones de los articulos 
            articulos_ciencia=self.tf_idf.getNameArticulos(json_ciencia)
            json_tecnologia=self.tf_idf.lecturaJsonV('tecnologia')
            #saco las direcciones de los articulos 
            articulos_tecnologia=self.tf_idf.getNameArticulos(json_tecnologia)
            #inserto todas las direcciones en un array
            articulos_=self.tf_idf.unirArrays(articulos_sanidad,articulos_ciencia)
            articulos=self.tf_idf.unirArrays(articulos_,articulos_tecnologia)
            #print(articulos)
            #consigo el array de documentos
            array_documentos=self.tf_idf.getAllArticulos(articulos)
            #consulto la query al usuario y la inserto en el array de documentos
            array_query=[self.entry.get()]
            array_documentos_query=self.tf_idf.unirArrays(array_query,array_documentos)
            #print(array_documentos_query)
            #busco la posicion de mi query
            posicion_query=self.tf_idf.calcularTF(array_documentos_query,array_query)
            #obtengo el vector de documentos
            vector_documentos=self.tf_idf.vectorTF_IDF(array_documentos_query)
            #obtengo la similitud
            similitud=self.tf_idf.similitudTF_IDF(vector_documentos,posicion_query)
            s=str(similitud).strip('[]')
            arrays_similitudes=s.split(' ')
            array=[]
            for item in arrays_similitudes:
                if item!='':

                    array.append(float(item.strip("\n'")))
            print('top: ',self.top_items.get())
            array_posiciones=self.tf_idf.sorting(array,int(self.top_items.get()))
            print(array_posiciones)
            init_list=self.tf_idf.cosine
            self.articulos=self.tf_idf.getArticulosSeleccionados(array_posiciones,array_documentos_query)
        lista = [x for x in init_list]
        self.ranking['values'] =lista
    def getArticulo(self,event):
        self.noticia.delete(1.0, END)
        array=self.articulos
        self.noticia.insert(END,array[self.ranking.current()])
   
        


# In[61]:


#este se compila para poder mostrar el menu NOTA: ACTUALMENTE SOLO FUNCIONAN LOS ARCHIVOS DE MI PAIS
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from tkinter import scrolledtext
class Menu(ttk.Frame):
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.grid()
        self.create_widgets()
        
    def create_widgets(self):
        """this creates all the objects in the window"""

        self.title_lbl = ttk.Label(self,text = "Busqueda de Noticia").grid(column = 0, row = 0)
        self.buscar=ttk.Button(self, text="Busqueda por consulta",command=self.setB_Noticias)
        self.buscar.grid(row=3,column=2)
        self.buscar=ttk.Button(self, text="Recomendacion de noticias",command=self.setR_Noticias)
        self.buscar.grid(row=5,column=2)
        
    def setB_Noticias(self):
        print('entro')
        main_window = tk.Tk()
        recomendacion_n = B_Noticias(main_window)
        main_window.geometry("1000x700")
        main_window.mainloop()
    def setR_Noticias(self):
        main_window = tk.Tk()
        recomendacion_n = R_Noticias(main_window)
        main_window.geometry("750x550")
        main_window.mainloop()
   
        
            
        

main_window = tk.Tk()
menu = Menu(main_window)
main_window.geometry("500x100")
main_window.mainloop() 


# from tkinter import ttk
# import tkinter as tk
# from tkinter.messagebox import showinfo
# sanidad=WebPages('sanidad','https://elpais.com/noticias/sanidad/' )
# sanidad.escritura(sanidad.miPais_news_scraper(),'sanidad.data.json')
# data_sanidad=Data(sanidad)
# tecnologia=WebPages('tecnologia','https://elpais.com/tecnologia/')
# tecnologia.escritura(tecnologia.miPais_news_scraper(),'tecnologia.data.json')
# data_tecnologia=Data(tecnologia)
# ciencia=WebPages('ciencia','https://elpais.com/ciencia/' )
# ciencia.escritura(ciencia.miPais_news_scraper(),'ciencia.data.json')
# data_ciencia=Data(ciencia)
# # root window
# root = tk.Tk()
# root.geometry('300x120')
# root.title('Progressbar Demo')
# 
# 
# def update_progress_label(file):
#     return f"Current Progress: {pb['value']}%"," files downloaded",file
# 
# 
# def progress():
#     if pb['value'] < 100:
#         pb['value'] += 20
#         value_label['text'] = update_progress_label('')
#     else:
#         showinfo(message='The progress completed!')
# 
# 
# def stop():
#     pb.stop()
#     value_label['text'] = update_progress_label('stop')
# 
# def cargando_sanidad():
#     data_sanidad.saveArticle()       
#     data_sanidad.getEtiqueta()
#     pb['value'] += 33.4
#     value_label['text'] = update_progress_label('/Sanidad')
# def cargando_ciencia():
#     data_ciencia.saveArticle()       
#     data_ciencia.getEtiqueta()
#     value_label['text'] = update_progress_label('/Ciencia')
#     pb['value'] += 33.33
# def cargando_tecnologia():
#     data_tecnologia.saveArticle()       
#     data_tecnologia.getEtiqueta()
#     value_label['text'] = update_progress_label('/Tecnologia')
#     pb['value'] += 33.33
#     if pb['value'] == 100:
#         showinfo(message='The progress completed!')
#     
# # progressbar
# pb = ttk.Progressbar(
#     root,
#     orient='horizontal',
#     mode='determinate',
#     length=280
# )
# # place the progressbar
# pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
# 
# # label
# value_label = ttk.Label(root, text=update_progress_label(''))
# value_label.grid(column=0, row=1, columnspan=2)
# 
# # start button
# ciencia = ttk.Button(root,text='Download Ciencia',command=cargando_ciencia)
# ciencia.grid(column=0, row=2, padx=10, pady=10, sticky=tk.E)
# 
# sanidad = ttk.Button(root,text='Download Sanidad',command=cargando_sanidad)
# sanidad.grid(column=1, row=2, padx=10, pady=10, sticky=tk.W)
# tecnologia = ttk.Button(root,text='Download Tecnologia',command=cargando_tecnologia)
# tecnologia.grid(column=2, row=2, padx=10, pady=10, sticky=tk.W)
# 
# root.mainloop()

# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.feature_extraction.text import TfidfTransformer
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from nltk.corpus import stopwords
# import numpy as np
# import numpy.linalg as LA
# from textblob import TextBlob
# from nltk.stem.porter import PorterStemmer
# import re
# porter_stemmer = PorterStemmer()
# def stemming_tokenizer(str_input):
#     words = re.sub(r"[^A-Za-z0-9\-]", " ", str_input).lower().split()
#     words = [porter_stemmer.stem(word) for word in words]
#     return words
# documentos = ["The best Italian restaurant enjoy the best pasta.","The best the best American restaurant.", "American restaurant enjoy the best hamburger.",
#               "Korean restaurant enjoy the best bibimbap"] #Documents
# query = ["The best the best American restaurant."] #Query
# #stopwords elimina las palabras frecuentes como: a, el, ella,etc.
# stopWords = stopwords.words('spanish')
# 
# vectorizer = CountVectorizer(stop_words = stopWords)
# #print transformer
# 
# vector_documentos = vectorizer.fit_transform(documentos).toarray()
# vector_query = vectorizer.transform(query).toarray()
# 
# print ('Vector de documentos', vectorizer.vocabulary_)
# print('Vector de documentos en array:',vector_documentos)
# print ('Vector de query en array', vector_query)
# print('--------------------------------------------')
# #funcion del coseno se le introducen dos valores 
# cx = lambda a, b : round(np.inner(a, b)/(LA.norm(a)*LA.norm(b)), 3)
# i=0
# x=0
# for vector in vector_documentos:
#     print (vector)
#     for testV in vector_query:
#         if np.array_equal(vector,testV):
#             print(vector,'y',testV)
#             x=i
#         print (testV)
#         cosine = cx(vector, testV)
#         print (cosine)
#     i=i+1
# print('X ESTA EN LA POSICION',x)
# for testV in vector_query:
#     print ('a',testV)
#     cosine = similarity_scores = vector_documentos.dot(testV)/(np.linalg.norm(vector_documentos, axis=1) * np.linalg.norm(testV))
# print ('similitud en el documento N: ',cosine)
# 
# print('--------------------------------------------')
# stop = list(stopwords.words('english'))
# tfidf_vectorizer = TfidfVectorizer(stop_words='english',tokenizer=stemming_tokenizer,use_idf=True,norm='l2')
# tfidf_vectorizer2 = TfidfVectorizer()
# tfidf_matrix = tfidf_vectorizer.fit_transform(documentos)
# tfidf_query = tfidf_vectorizer2.fit_transform(query)
# #print ('QUERY',tfidf_query.toarray())
# print (tfidf_matrix.toarray())
# 
# #print ('similitud en el documento N: ',cosine)
# #importante 
# cosine = cosine_similarity(tfidf_matrix[x], tfidf_matrix)  #here the first element of tfidf_matrix_train is matched with other three elements
# print (cosine)
# 
# """
# transformer.fit(vector_documentos)
# print()
# print (transformer.transform(vector_documentos).toarray())
# 
# transformer.fit(vector_query)
# print ()
# tfidf = transformer.transform(vector_query)
# print (tfidf.todense())
# for v in transformer.transform(vector_documentos).toarray():
#     for q in transformer.transform(vector_query).toarray():
#         cosine = cx(v, q)
#         print ('similitud en el documento N: ',cosine)"""
#         
