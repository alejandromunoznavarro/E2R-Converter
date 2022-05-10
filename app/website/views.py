__author__ = "Alejandro Muñoz Navarro"
__copyright__ = "Copyright 2022, Universidad Politécnica de Madrid"
__credits__ = ["Alejandro Muñoz Navarro", "María del Carmen Suárez de Figueroa"]
__license__ = "CC"
__version__ = "1.0.0"
__email__ = "alejandro@munoznavarro.com"

from re import template
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from . import Procesador
import unicodedata

def procesar_texto(text):
    run = Procesador.Procesador()
    leido = text.encode("utf-8").decode("utf-8")
    sin_procesar = unicodedata.normalize("NFKD", leido).split(sep='\n')
    procesado = ''
    for i,parrafo in enumerate(sin_procesar):
        try:
            resultado = run.procesado(parrafo)
            procesado += resultado+'\n'
        except:
            procesado += '¡ERROR FRASE:'+parrafo+'!\n'
    return procesado

def procesar_archivo(file):
    run = Procesador.Procesador()
    leido = file.read().decode("utf-8")
    sin_procesar = unicodedata.normalize("NFKD", leido).split(sep='\n')
    procesado = ''
    for i,parrafo in enumerate(sin_procesar):
        try:
            resultado = run.procesado(parrafo)
            procesado += resultado+'\n'
        except:
            procesado += '¡ERROR FRASE:'+parrafo+'!\n'
    archivo = open('./website/static/temp/Procesado.txt',"w")
    archivo.write(procesado)
    return leido,procesado

def index(request):
    return render(request, 'index.html')

def e2r_converter(request):
    if request.method == 'GET':
        text = request.GET.get('text1')
        if text != None and text != '':
            procesado = procesar_texto(text)
        else:
            procesado = ''
            text =''
        return render(request, 'e2r_converter.html', {'text_original':text,'text_procesado':procesado})

    elif request.method == 'POST':
        try:
            myfile = request.FILES['myfile']
            procesado = procesar_archivo(myfile)
            return render(request, 'e2r_converter.html', {'file_procesado': procesado})
        except KeyError:
            return render(request, 'e2r_converter.html', {'file_alert': 'Archivo no seleccionado. Por favor, seleccione un archivo.'})
        
    else:
        return render(request, 'e2r_converter.html')

def e2r_converter_file(request):
    if request.method == 'POST':
        try:
            myfile = request.FILES['myfile']
            sin_procesar,procesado = procesar_archivo(myfile)
            return render(request, 'e2r_converter_file.html', {'file_procesado': procesado, 'file_original':sin_procesar})
        except KeyError:
            return render(request, 'e2r_converter_file.html', {'file_alert': 'Archivo no seleccionado. Por favor, seleccione un archivo.'})
        
    else:
        return render(request, 'e2r_converter_file.html')

def e2r_converter_text(request):
    if request.method == 'GET':
        text = request.GET.get('text1')
        if text != None and text != '':
            procesado = procesar_texto(text)
        else:
            procesado = ''
            text =''
        return render(request, 'e2r_converter_text.html', {'text_original':text,'text_procesado':procesado})

    else:
        return render(request, 'e2r_converter_text.html')
    