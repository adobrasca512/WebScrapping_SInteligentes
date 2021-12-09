#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#solicitud pagina web
pip install requests-html


# In[ ]:


#esta es una libreria que me permite manejar fechas, tuve problemas con datetime ya que datetime no reconoce fechas
#acortadas en español, mas no palabras como Diciembre, esas si las reconoce.
pip install Arrow


# In[32]:


#web scrapping
from bs4 import BeautifulSoup
import requests
#maneja mi archivo json
import json
#lo uso para remover archivos y no duplicar
import os
from datetime import datetime


# In[628]:


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
    #metodo para añadir keys a jsons
    #|key=llave del json
    #|name=valor de la key
    #|posicion=posicion a guardar dentro del json
    def add(self,key,name,posicion):
        with open(self.webPage.getTema()+'.data.json') as json_file:
            json_decoded = json.load(json_file)
            json_decoded[self.webPage.getTema()][posicion][key] = name
        with open(self.webPage.getTema()+'.data.json', 'w') as json_file:
            json.dump(json_decoded, json_file)
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
        import locale
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        import arrow
        
        fecha = arrow.get(fdate, 'DD MMM YYYY',locale='ES')
        d=str(fecha)
        fecha_ = d.split('T', 1)[0]
        return fecha_
    #metodo para extraer valores del json con sus keys
    #|value=array para añadir los items a un array
    #|nombre=la key del json
    def get(self,value,nombre):
        #aqui saco todos los titulos
        with open(self.webPage.getTema()+'.data.json') as file:
            data = json.load(file)
        for item in data[self.webPage.getTema()]:
            value.append(item[nombre])
        return value
    #metodo para obtener el titulo dentro del json
    def getTitulo(self):
        return self.get(self.titulo,'titulo')
    #metodo para obtener la fecha en el segundo link y guardarlo en el json
    def getFecha(self):
        i=0
        self.enlace=self.getEnlace()
        for link in self.enlace:
            noticia=self.webPage.getRequest(link)
            elements=noticia.find_all('div', class_='a_md_f')
            for item in elements:
                self.fecha.append(self.setDate(self.webPage.parseo(item.select('time'))))
                self.addFecha(self.setDate(self.webPage.parseo(item.select('time'))),i)
            i=i+1
        return self.fecha
    #metodo para obtener el enlace dentro del json
    def getEnlace(self):
        #aqui saco todos los titulos
        self.enlace=[]
        return self.get(self.enlace,'enlace')
    #metodo para obtener el articulo dentro del json
    def getArticulo(self):
        self.enlace=self.getEnlace()
        for link in self.enlace:
            noticia=self.webPage.getRequest(link)
            elements=noticia.find_all('div', class_='a_c')
            for item in elements:
                self.articulo.append(parseo(item.select('p')))
        return self.articulo
    #metodo obtengo la etiqueda de TODAS las paginas.
    def getEtiqueta(self):
        i=0
        j=0
        arr_etiquetas=[]
        self.etiqueta=[]
        self.enlace=self.getEnlace()
        for link in self.enlace:
            noticia=self.webPage.getRequest(link)
            elements=noticia.find_all('ul', class_='_df _ls')
            for item in elements:
                e=parseo(item.select('li'))
                arr_etiquetas=e.split(',')
                self.etiqueta.append(arr_etiquetas)
            self.addEtiqueta(arr_etiquetas,i)
            i=i+1
        return self.etiqueta
    #metodo para guardar el articulo en un TXT
    def saveArticle(self):
        i=0
        #emparejamos titulo y articulo
        self.titulo=self.getTitulo()
        self.articulo=self.getArticulo()
        self.fecha=self.getFecha()
        for articulo, titulo,fecha in zip(self.articulo, self.titulo,self.fecha): #obtenemos los valores en cada iteración
            parrafo=titulo+'\n'+articulo
            parrafo_=parrafo.strip("[]")
            tema=self.webPage.getTema()
            nombre=tema+'.'+fecha+'.'+str(i)+'.txt'
            self.addTxt(nombre,i)
            self.webPage.escritura(parrafo_,nombre)
            
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
    #
    def getDescripcion(self):
        print(self.descripcion)
    #cuando el usuario defina el articulo a ver el dato se basara en el articulo seleccionado
    #|etiqueta=etiqueta del articulo
    def setEtiqueta(self,etiqueta):
        self.etiqueta=etiqueta
    #cuando el usuario defina el articulo a ver el dato se basara en el articulo seleccionado
    #|top=top de articulos
    def setMax(self,maxi):
        self.max=maxi
    def getSimilitud_Paginas():
        #recorro las noticias:
        print()
    #metodo que abre el archivo txt y lo muestra 
    def mostrarArticulo(self):
        texto=''
        #consultamos en el json el nombre del txt
        with open(self.webPage.getTema()+'.data.json') as file:
            data = json.load(file)
        for item in data[self.webPage.getTema()]:
            if item['titulo'] == self.titulo:
                texto=item['articulo']
        #abrimos el txt y lo leemos
        f = open(texto, "r")
        self.articulo=str(f.read())
        return self.articulo
    #estos son los calculos de la similitud
    #|match=match del array1 con array2
    #ejemplo: [a,b,c]U[d,c,r]=c 1 match
    #|e1=es el array que escogio el usuario
    #|array2= son los otros arrays top
    def calculos(self,e1,array2,match):
        #print('match encontrados',match)
        #print('formula',str(2),'*',str(match),'/',str((len(e1))),'+',str(len(array2)))
        formula=(2*match)/((len(e1))+(len(array2)))
        return formula
    #aqui obtengo las similitudes entr etiquetas
    #|e1= es el array que escogio el usuario
    def similitud(self,e1):
        similitudes=[]
        #contador de similitudes
        contador_match=0
        maximo=self.max
        i=0
        e2=self.getEtiqueta()
        #aqui sera en el array simple ['comida','perro','gato']
        for array2 in e2:
            contador_match=0
            #solo obtendre las similitudes de los top
            if(i<self.max):
                #[['comida','perro','avispa'],['azul','perro','can']]  
                for item in array2:
                    for array1 in e1:
                        #print('_______________________________________')
                        #print(item,'es igual a',array1)
                        if array1 in item:
                            contador_match=contador_match+1
                            #print(item,'SI igual a',array1)
                            #print()
                            #print('array encontrado similitud:',array2)          
                        resultado=self.calculos(e1,array2,contador_match)

                        resultado_=resultado*100
                    #añadimos el resultado en un array de similitudes
                i=i+1
                similitudes.append(resultado)
            else:
                break
                #print(array2)
                #print('grado de similitud con array1',str(resultado_)+'%')
                #print('_______________________________________')
        return similitudes
    


# In[627]:


class Usuario():
    def __init__(self, titulo, categoria,top,data):
        self.titulo = titulo
        self.categoria = categoria
        self.data = data
        self.top=top
    #seteamos los campos de datos para que nos muestre los necesarios nada mas
    def cargarSeleccion(self):
        with open(self.categoria+'.data.json') as file:
            data = json.load(file)
       
        for item in data[self.categoria]:
            #validamos que la seccion seleccionada este en el json
            if self.titulo  in item['titulo']:
                self.data.setEnlace(item["enlace"]) 
                self.data.setTitulo(item["titulo"])
                self.data.setDescripcion(item["descripcion"]) 
                self.data.setFecha(item["fecha"])
                self.data.setEtiqueta(item["etiquetas"])
                self.data.setMax(self.top)


# In[626]:


class WebPages():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    def __init__(self, tema, url):
        self.tema = tema
        self.url = url
    def getRequest(self,url):
        request = requests.get(url, headers=headers)
        html = request.content
        soup = BeautifulSoup(html, from_encoding='utf-8')
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
        soup=getRequest(self.url)
    
    # Encontramos todos los articulos necesarios
        elements=soup.find_all('article', class_='c')
    #de todos los articulos iremos revisando item x item.
        for item in elements:
            #aqui es donde tomo los enlaces,titulos,entradillas, fechas y las introduzco en un json
            enlace='https://elpais.com'+item.a['href']
            d=item.select('div span time')
            fecha=parseo(d)
            fecha_=self.setDate(fecha)
            article_list[self.tema].append({'titulo':parseo(item.select('header h2 a')),'enlace':enlace,'descripcion':parseo(item.select('p'),),
                                            'fecha':fecha_,'articulo':'','etiquetas':[]} )
            
        return article_list   
    #obtengo el tema;sanidad,tecnologia,ciencia.
    def getTema(self):
        return self.tema


# In[624]:


#falta solamente limitarlo
#ordenar noticias por orden de similitud, linquear similitud con noticia
if __name__ == '__main__':
    #colocamos las tres webpages:
    sanidad=WebPages('sanidad','https://elpais.com/noticias/sanidad/' )
    tecnologia=WebPages('tecnologia','https://elpais.com/tecnologia/' )
    ciencia=WebPages('ciencia','https://elpais.com/ciencia/' )
    #preguntamos usuario
    print('¿que categoria desea ver?')
    print('1.Sanidad\n2.Tecnologia\n3.Ciencia')
    desicion=input()
    #print(desicion)
    #desicion=1
    
    if int(desicion) == 1:
        #cargamos los datos de las paginas en un json
        sanidad.escritura(sanidad.miPais_news_scraper(),'sanidad.data.json')
        #cargamos nuestros datos,aqui en data en este momento estan TODOS LOS DATOS
        data=Data(sanidad)
        #guardamos TODOS los articulos
        data.saveArticle()
        #guardamos TODAS las etiquetas
        #print(data.getEtiqueta())
        data.getEtiqueta()
        #print(data.getTitulo())
        #le metemos los datos al usuario para que pueda verlos, al igual se le pide su eleccion
        #usuario al seleccionar le cambia los valores a datos, para especificar que quiere solo algunos
        usuario=Usuario('China tira de diplomacia sanitaria para posicionarse en el Mekong y más allá','sanidad',5,data)
        usuario.cargarSeleccion()
        #mostrar titulo
        print('--------------------TITULO-------------------')
        print(data.titulo)
        #mostrar descripcion
        print('--------------------DESCRIPCION-------------------')
        print(data.descripcion)
        #mostrar el articulo
        print('--------------------ARTICULO-------------------')
        print(data.mostrarArticulo())
        #mostrar el fecha
        print('--------------------FECHA-------------------')
        print(data.fecha)
        #mostrar los porcentajes
        #print(data.etiqueta)
        print('--------------------SIMILITUDES-------------------')
        print(data.similitud(data.etiqueta))
    elif int(desicion) == 2:
         #cargamos los datos de las paginas en un json
        tecnologia.escritura(tecnologia.miPais_news_scraper(),'tecnologia.data.json')
        #cargamos nuestros datos,aqui en data en este momento estan TODOS LOS DATOS
        data=Data(tecnologia)
        #guardamos TODOS los articulos
        data.saveArticle()
        #guardamos TODAS las etiquetas
        #print(data.getEtiqueta())
        data.getEtiqueta()
        #print(data.getTitulo()) Los videojuegos oficializan su salto al mundo de los NFT
        #le metemos los datos al usuario para que pueda verlos, al igual se le pide su eleccion
        #usuario al seleccionar le cambia los valores a datos, para especificar que quiere solo algunos
        usuario=Usuario('Los videojuegos oficializan su salto al mundo de los NFT','tecnologia',data)
        usuario.cargarSeleccion()
        #mostrar titulo
        print('--------------------TITULO-------------------')
        print(data.titulo)
        #mostrar descripcion
        print('--------------------DESCRIPCION-------------------')
        print(data.descripcion)
        #mostrar el articulo
        print('--------------------ARTICULO-------------------')
        print(data.mostrarArticulo())
        #mostrar el fecha
        print('--------------------FECHA-------------------')
        print(data.fecha)
        #mostrar los porcentajes
        #print(data.etiqueta)
        print('--------------------SIMILITUDES-------------------')
        print(data.similitud(data.etiqueta))
    elif int(desicion) == 3:
         #cargamos los datos de las paginas en un json
        ciencia.escritura(ciencia.miPais_news_scraper(),'ciencia.data.json')
        #cargamos nuestros datos,aqui en data en este momento estan TODOS LOS DATOS
        data=Data(ciencia)
        #guardamos TODOS los articulos
        data.saveArticle()
        #guardamos TODAS las etiquetas
        #print(data.getEtiqueta())
        data.getEtiqueta()
        #print(data.getTitulo()) Los videojuegos oficializan su salto al mundo de los NFT
        #le metemos los datos al usuario para que pueda verlos, al igual se le pide su eleccion
        #usuario al seleccionar le cambia los valores a datos, para especificar que quiere solo algunos
        usuario=Usuario('Científicos europeos simulan el inicio de un embarazo usando un embrión artificial','ciencia',5,data)
        usuario.cargarSeleccion()
        #mostrar titulo
        print('--------------------TITULO-------------------')
        print(data.titulo)
        #mostrar descripcion
        print('--------------------DESCRIPCION-------------------')
        print(data.descripcion)
        #mostrar el articulo
        print('--------------------ARTICULO-------------------')
        print(data.mostrarArticulo())
        #mostrar el fecha
        print('--------------------FECHA-------------------')
        print(data.fecha)
        #mostrar los porcentajes
        print('--------------------SIMILITUDES-------------------')
        print(data.similitud(data.etiqueta))
    else:
        print('error')


# In[629]:


#by Adilem Dobras

