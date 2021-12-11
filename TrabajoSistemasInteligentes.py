#!/usr/bin/env python
# coding: utf-8

# In[1]:


#solicitud pagina web
get_ipython().system('pip install requests-html')


# In[2]:


#esta es una libreria que me permite manejar fechas, tuve problemas con datetime ya que datetime no reconoce fechas
#acortadas en español, mas no palabras como Diciembre, esas si las reconoce.
get_ipython().system('pip install Arrow')


# In[3]:


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


# In[12]:


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
    #metodo para leer jsons
    def lecturaJson(self):
        #print(self.webPage.getTema())
        with open(self.webPage.getTema()+'.data.json') as file:
            data = json.load(file)
        return data
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
        return self.get(self.titulo,'titulo')
    #metodo para obtener TODAS fecha en el segundo link y guardarlo en el json
    def getFecha(self):
        i=0
        self.enlace=self.getEnlace()
        for link in self.enlace:
            noticia=self.webPage.getRequest(link)
            elements=noticia.find_all('div', class_='a_md_f')
            if elements:
                for item in elements:
                    self.fecha.append(self.setDate(self.webPage.parseo(item.select('time'))))
                    self.addFecha(self.fecha[i],i)
            else: 
               #caso excepcional para TECNOLOGIA ya que contiene articulos que son ads pero tambien forman parte de los articulos
                elements=noticia.find_all('div', class_='a_pt | uppercase color_gray_medium_lighter')
                for item in elements:
                    self.fecha.append(self.setDate(self.webPage.parseo(item.select('a'))))
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
                    self.articulo.append(self.webPage.parseo(item.select('p')))
            else:
             #caso excepcional para TECNOLOGIA ya que contiene articulos que son ads pero tambien forman parte de los articulos
                elements=noticia.find_all('div',class_='a_b article_body | color_gray_dark initial_letter especial a_b__e col desktop_8 tablet_8 mobile_4 margin_center')
                for item in elements:
                    self.articulo.append(self.webPage.parseo(item.select('p')))
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
    #obtenemos la descripcion (borrar no se usa)
    def getDescripcion(self):
        print(self.descripcion)
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
        f = open(nombre, "r")
        texto=str(f.read())
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
        
    def mostrarArticulo(self):
        texto=''
        #consultamos en el json el nombre del txt
        data=self.lecturaJson()
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
        return arr
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
    def similitud(self,e1):
        n_noticia=0
        #contador de similitudes
        contador_match=0
        maximo=self.max
        i=0
        e1_=self.eliminarEspacios(e1)
        e2=self.getEtiqueta()
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
            
            self.similitudes.append(resultado_)
            #print(array2)
            #print('grado de similitud con array1',str(resultado_)+'%')
            #print('_______________________________________')
        return self.similitudes
    


# In[5]:


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


# In[6]:


class WebPages():
    def __init__(self, tema, url):
        self.tema = tema
        self.url = url
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
   
    def getRequest(self,url):
        request = requests.get(url, headers=self.headers)
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


# In[8]:


#by Adilem Dobras


# In[15]:


from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from tkinter import scrolledtext
class Application(ttk.Frame):
    
    def __init__(self, main_window,sanidad,tecnologia,ciencia):
        super().__init__(main_window)
        self.grid()
        #self.usuario= Usuario.__new__(Usuario)
        self.create_widgets()
        self.sanidad=sanidad
        self.tecnologia=tecnologia
        self.ciencia=ciencia
        self.sort=[]
        self.tema=''
        self.usuario_sanidad=Usuario('','sanidad',5,self.sanidad)
        self.usuario_tecnologia=Usuario('','tecnologia',5,self.tecnologia)
        self.usuario_ciencia=Usuario('','ciencia',5,self.ciencia)
        self.page=''
        #self.data = Data(self.webPage)
    def create_widgets(self):
        """this creates all the objects in the window"""

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
        self.categoria.current(0)
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
            init_list=self.sanidad.getTitulo()
        elif self.categoria.get() == 'Tecnología':
            init_list=self.tecnologia.getTitulo()
        elif self.categoria.get() == 'Ciencia':
            init_list=self.ciencia.getTitulo()
        lista = [x for x in init_list]
        self.noticias['values'] = lista

        
    def getArticulo(self,event):
        if self.categoria.get() in 'Sanidad':
            self.usuario_sanidad=Usuario(self.noticias.get(),'sanidad',5,self.sanidad)
            self.usuario_sanidad.cargarSeleccion()
            self.text_area.insert(END,self.sanidad.mostrarArticulo())
        elif self.categoria.get() == 'Tecnología':
            self.usuario_tecnologia=Usuario(self.noticias.get(),'tecnologia',5,self.tecnologia)
            self.usuario_tecnologia.cargarSeleccion()
            self.text_area.insert(END,self.tecnologia.mostrarArticulo())
        elif self.categoria.get() == 'Ciencia':
            self.usuario_ciencia=Usuario(self.noticias.get(),'ciencia',5,self.ciencia)
            self.usuario_ciencia.cargarSeleccion()
            self.text_area.insert(END,self.ciencia.mostrarArticulo())
    def getTop(self):
        if self.categoria.get() in 'Sanidad':
            self.usuario_sanidad.setTop(int(self.top_items.get()))
            self.sanidad.similitud(self.sanidad.etiqueta)
            self.sort=self.sanidad.sorting(self.sanidad.similitudes)
            init_list=self.sanidad.similitudes
        elif self.categoria.get() == 'Tecnología':
            self.usuario_tecnologia.setTop(int(self.top_items.get()))
            self.tecnologia.similitud(self.tecnologia.etiqueta)
            self.sort=self.tecnologia.sorting(self.tecnologia.similitudes)
            init_list=self.tecnologia.similitudes
        elif self.categoria.get() == 'Ciencia':
            self.usuario_ciencia.setTop(int(self.top_items.get()))
            self.ciencia.similitud(self.ciencia.etiqueta)
            self.sort=self.ciencia.sorting(self.ciencia.similitudes)
            init_list=self.ciencia.similitudes
            
        lista = [x for x in init_list]
        self.top_articulos['values'] =lista
    def getOtrosAtriculos(self,event):
        if self.categoria.get() in 'Sanidad':
            print(self.top_articulos.current())
            articulo= self.sanidad.getSimilitud_Paginas(self.sort[self.top_articulos.current()])
            self.otras_noticias.insert(END,articulo)
        elif self.categoria.get() == 'Tecnología':
            articulo= self.tecnologia.getSimilitud_Paginas(self.sort[self.top_articulos.current()])
            self.otras_noticias.insert(END,articulo)
        elif self.categoria.get() == 'Ciencia':
            print(self.sort[self.top_articulos.current()])
            articulo= self.ciencia.getSimilitud_Paginas(self.sort[self.top_articulos.current()])
            self.otras_noticias.insert(END,articulo)
        
    
         
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
data_sanidad.getEtiqueta()
data_ciencia.saveArticle()       
data_ciencia.getEtiqueta()
data_tecnologia.saveArticle()       
data_tecnologia.getEtiqueta()
main_window = tk.Tk()
app = Application(main_window,data_sanidad,data_tecnologia,data_ciencia)
main_window.geometry("700x550")
main_window.mainloop()

