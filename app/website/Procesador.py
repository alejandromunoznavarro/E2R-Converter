#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador.py: 
This application is an easy to read converter of Spanish text that contains numbers and percentages.
This project was developed as a final project for a Master's Degree in Artificial Intelligence at the Polytechnic University of Madrid.
"""
__author__ = "Alejandro Muñoz Navarro"
__copyright__ = "Copyright 2022, Universidad Politécnica de Madrid"
__credits__ = ["Alejandro Muñoz Navarro", "María del Carmen Suárez de Figueroa"]
__version__ = "1.0.0"
__email__ = "alejandro@munoznavarro.com"

# PROCESAMIENTO DEL TEXTO
import nltk

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

from nltk.tokenize.treebank import TreebankWordDetokenizer

# !pip install spacy
# !python -m spacy download es_core_news_md
import es_core_news_md

# CONVERSIÓN DE LETRA A NÚMERO
# !pip install spa2num
from spa2num import converter

class Procesador:
    def __init__(self):
          self.tokenizer = nltk.data.load('tokenizers/punkt/spanish.pickle')
          self.nlp = es_core_news_md.load()
    
    def limpiarTexto(self,tokens):
          """
          En esta función se limpiará el texto de todos los paréntesis y se redondearán
          los números decimales
          """
          # Cambiamos los números en palabra por cifras
          numero = []
          # Realizamos otros cambios
          new = []
          parentesis = 0

          especiales = ["treinta","cuarenta","cincuenta", "sesenta",
           "setenta", "ochenta", "noventa"]
          unidades = ["uno","un","una","dos","tres","cuatro","cinco","seis","siete","ocho","nueve"]
          for pos,token in enumerate(tokens):
            # Eliminamos los parentesis
            if token.text == '(':
                parentesis += 1
            elif parentesis > 0 and token.text == ')':
              parentesis -= 1
            elif parentesis > 0:
              pass
            else:
              # Si es una palabra
              if token.text.isalpha() and token.pos_ != 'CCONJ' and token.pos_ != 'CONJ' and ((token.text.lower() != 'un' and token.text.lower() != 'una') or (len(numero)>1 and numero[-2].lower() in especiales)):
                try :
                  if token.text.lower() == 'una':
                    numero.append('un')
                  else:
                    converter.to_number(token.text)
                    numero.append(token.text)
                except :
                  if len(numero)>0:
                    aux = self.nlp(str(converter.to_number(" ".join(numero))))
                    new.append(aux[0])
                    numero = []
                  new.append(token)
              elif token.text.lower() == 'y' and len(numero)>0 and numero[-1].lower() in especiales and len(tokens)>pos+1 and tokens[pos+1].text.lower() in unidades:
                numero.append(token.text)
              # Si es una cifra o un símbolo
              else:
                if token.text.isnumeric():
                  numero.append(token.text)
                elif len(numero) > 0:
                  aux = self.nlp(str(converter.to_number(" ".join(numero))))
                  new.append(aux[0])
                  numero = []
                  new.append(token)
                else:
                  new.append(token)
        
          if len(numero) > 0:
            aux = self.nlp(str(converter.to_number(" ".join(numero))))
            new.append(aux[0])
        
          
        
          for i,token in enumerate(new): 
          # Redondeamos en caso de ser necesario
            try:
              num = float(token.text.replace(',','.'))
              token = self.nlp(str(round(num)))
              new[i] = token[0]
            except:
              pass
        
          return new
    
    
    def destokenizar(self,frase):
          """
          En esta función se destokeniza una frase léxicamente, añadiendo mayúsculas y
          reemplazando algunas palabras como 'a el' por 'al'
          """
          new = TreebankWordDetokenizer().detokenize(frase)
          new = new.replace(' a el ',' al ')
          new = new.replace('A el ','Al ')
          new = new.replace(' de el ',' del ')
          new = new.replace('De el ',' Del ')
          new = new.replace(' más de más de ',' más de ')
          new = new.replace('Más de más de ','Más de ')
          new = new.replace(' más de mucho ',' mucho ')
          new = new.replace('Más de mucho ','Mucho ')
          new = new.replace(' más de mucha ',' mucha ')
          new = new.replace('Más de mucha ','Mucha ')
          new = new.replace(' más de muchos ',' muchos ')
          new = new.replace('Más de muchos ','Muchos ')
          new = new.replace(' más de muchas ',' muchas ')
          new = new.replace('Más de muchas ','Muchas ')
          return ''.join([new[0].upper(),new[1:]])
  
    def sustitution(self,tokens):
          """
          En esta función se procesará cada frase obteniendo la nueva frase como
          resultado. Para ello se extraerá la cifra al que hace referencia el porcentaje
          y la estructura de este. Con ello realizaremos la sustitución adecuada.
          La estructuras según su prioridad en la búsqueda son las siguientes:
        
          0%
          Se sustituirá por 'nada'/'ninguno'/'ninguna' en caso de ser anterior a la preposición 'de'
          En caso contrario se sustituirá por 'nada'. A continuación se observa algunos de los casos
          en los que se realizarán más cambios según su estructura:
          
          - CASO 1: 
                con + (un/el) + % + de/a/en --> sin + nada/ninguno/ninguna + de/a/en
          - CASO 2:
                (el/un) + otro + % —> nada/ninguno/ninguna
                ese/este/aquel + % —> nada/ninguno/ninguna
                casi + (un/el) + % —> casi + nada/ninguno/ninguna
                de/en/a + (un/el) % —> de/en/a + nada/ninguno/ninguna
                mi/tu/su/sus... + % --> no verb + nada/ninguno/ninguna
          - CASO 3:
                verb + (un/el) + % + de + (la/el) + ... —> no verb + nada + de (la/el)
                verb + (un/el) + % + de + los/las + … —> no verb + ninguna/o + de + los/las + …
                verb + (un/el) + % + en/a —> no verb + nada + en/a
                verb + mi/tu/su/sus... + % --> no verb + nada/ninguno/ninguna
          - CASO 4:
                Cuando el % es anterior al verbo, no es necesario hacer una doble negación.
                Sin embargo, en este caso realizar la sustitución es más dificil debido a
                la ambigüedad del verbo. Un verbo puede referirse a una persona o a una cosa.
                Dependiendo del caso, la sustitución sería 'nadie' para el primero y 'nada'
                para el segundo. Para contemplar este caso deberíamos tener un corpus con
                los verbos que se podrían usar en cada caso y obtener una sustitución corecta,
                por lo que en este proyecto será eliminado por este momento.
                
                (un/el) + % + verb --> ¿?
                  un 0% aumentó en el ultimo año - nada aumentó en el ultimo año
                  un 0% votó en el ultimo año - nadie votó en el ultimo año
          """
        
          
          minusculas = [i.text.lower() for i in tokens]
          frase = [i.text for i in tokens]
          porcentaje = minusculas.index('%')
          new = list(reversed(frase[porcentaje+1:]))
          rules = [0,0,0,0]  # [base word added, no added to verb/aux, noun/adv, start to add]
          
          # añadimos las palabras de sustitución
        
          
          if int(minusculas[porcentaje-1]) == 0: # RANGO 0%
            if len(minusculas)>porcentaje+1 and minusculas[porcentaje+1] == 'de':
              if minusculas[porcentaje+2] == 'los':
                new.append('ninguno') 
              elif minusculas[porcentaje+2] == 'las':
                new.append('ninguna') 
              else:
                new.append('nada') 
            else:
              new.append('nada')
            
          elif int(minusculas[porcentaje-1])>0 and int(minusculas[porcentaje-1])<25:
            
            """ ESTO SON LOS RANGOS """
            # RANGO 1 - 9%
            if int(minusculas[porcentaje-1]) > 0 and int(minusculas[porcentaje-1]) < 10: # no añade det
              masculino = 'muy pocos'
              femenino = 'muy pocas'
              singularm = 'muy poco'
              singularf = 'muy poca'
        
            # RANGO 10 - 24%
            else:
              
              masculino = 'pocos'
              femenino = 'pocas'
              singularm = 'poco'
              singularf = 'poca'
        

            """ ESTA ES LA SUSTITUCIÓN """
            # Añadimos la palabra base
            if len(minusculas)>porcentaje+1 and minusculas[porcentaje+1] == 'de':
              if minusculas[porcentaje+2] == 'los':
                new.append(masculino)
                rules[1] = 1
              elif minusculas[porcentaje+2] == 'las':
                new.append(femenino) 
                rules[1] = 2
              elif minusculas[porcentaje+2] == 'la':
                new.append(singularf)
              elif minusculas[porcentaje+2] == 'el':
                new.append(singularm)
              else:
                try:
                  genero = tokens[porcentaje+2].morph.get("Gender")
                  numero = tokens[porcentaje+2].morph.get("Number")
                  if genero[0] == 'Masc':
                    if numero[0] == 'Sing':
                      new[-1]='el'
                      new.append('de')
                      new.append(singularm)
                    else:
                      rules[1] = 1
                      new[-1]='los'
                      new.append('de')
                      new.append(masculino)
                  else:
                    if numero[0] == 'Sing':
                      new[-1]='la'
                      new.append('de')
                      new.append(singularf)
                    else:
                      rules[1] = 2
                      new[-1]='las'
                      new.append('de')
                      new.append(femenino)
                except:
                  try:
                    genero = tokens[porcentaje+3].morph.get("Gender")
                    numero = tokens[porcentaje+3].morph.get("Number")
                    if genero[0] == 'Masc':
                      if numero[0] == 'Sing':
                        new.append(singularm)
                      else:
                        rules[1] = 1
                        new.append(masculino)
                    else:
                      if numero[0] == 'Sing':
                        new.append(singularf)
                      else:
                        rules[1] = 2
                        new.append(femenino)
                  except:
                    new.append(singularm)
            else:
              new.append(singularm)

            # En el caso de 'poco', si tiene PREP o ADP antes del porcentaje, añadimos un det acorde a la sustitución
            if int(minusculas[porcentaje-1]) > 9 and ((porcentaje-2 >= 0 and (tokens[porcentaje-2].pos_ == 'PREP' or tokens[porcentaje-2].pos_ == 'ADP')) or (porcentaje-3 >= 0 and (tokens[porcentaje-3].pos_ == 'PREP' or tokens[porcentaje-3].pos_ == 'ADP'))):
              if new[-1]==masculino:
                new.append('unos')
              elif new[-1]==femenino:
                new.append('unas')
              elif new[-1]==singularm:
                new.append('un')
              else:
                new[-1] = singularm # en este caso el femenino no tiene coherencia
                new.append('un')
            

          elif int(minusculas[porcentaje-1])>24 and int(minusculas[porcentaje-1])<76:
          
            # RANGO 25%
            if int(minusculas[porcentaje-1]) == 25: # no añade det/pron
              masculino = '1 de cada 4'
              femenino = '1 de cada 4'
              singular = '1 de cada 4'
        
            # RANGO 26 - 40%
            elif int(minusculas[porcentaje-1]) > 25 and int(minusculas[porcentaje-1]) < 41: # no añade det/pron
              masculino = '1 de cada 3'
              femenino = '1 de cada 3'
              singular = '1 de cada 3'
        
            # RANGO 41 - 49%
            elif int(minusculas[porcentaje-1]) > 40 and int(minusculas[porcentaje-1]) < 50: # no añade det/pron
              rules[2] = 1 # se necesita eliminar la palabra casi si se encuentra en la frase
              masculino = 'casi la mitad'
              femenino = 'casi la mitad'
              singular = 'casi la mitad'
        
            # RANGO 50%
            elif int(minusculas[porcentaje-1]) == 50: # no añade det/pron
              masculino = 'la mitad'
              femenino = 'la mitad'
              singular = 'la mitad'
        
            # RANGO 51 - 74%
            elif int(minusculas[porcentaje-1]) > 50 and int(minusculas[porcentaje-1]) < 75: # no añade det/pron
              # para frases con "más de (det) %" se cambia todo
              masculino = 'más de la mitad'
              femenino = 'más de la mitad'
              singular = 'más de la mitad'
        
            # RANGO 75%
            elif int(minusculas[porcentaje-1]) == 75: # no añade det/pron
              masculino = 'la mayoría'
              femenino = 'la mayoría'
              singular = 'la mayoría'
        
            """ ESTA ES LA SUSTITUCIÓN """
            # Añadimos la palabra base
            if len(minusculas)>porcentaje+1 and minusculas[porcentaje+1] == 'de':
              if minusculas[porcentaje+2] == 'los':
                new.append(masculino)
                rules[1] = 1
              elif minusculas[porcentaje+2] == 'las':
                new.append(femenino) 
                rules[1] = 2
              else:
                new.append(singular) 
            else:
              new.append(singular)
        
          
          elif int(minusculas[porcentaje-1]) > 75 and int(minusculas[porcentaje-1]) < 91: # RANGO 76 - 90% no añade det/pron
            masculino = 'muchos'
            femenino = 'muchas'
            singularm = 'mucho'
            singularf = 'mucha'
            """ ESTA ES LA SUSTITUCIÓN """
            # Añadimos la palabra base
            if len(minusculas)>porcentaje+1 and minusculas[porcentaje+1] == 'de':
              if minusculas[porcentaje+2] == 'los':
                new.append(masculino)
                rules[1] = 1
              elif minusculas[porcentaje+2] == 'las':
                new.append(femenino) 
                rules[1] = 2
              elif minusculas[porcentaje+2] == 'la':
                new.append(singularf)
              elif minusculas[porcentaje+2] == 'el':
                new.append(singularm)
              else:
                try:
                  genero = tokens[porcentaje+2].morph.get("Gender")
                  numero = tokens[porcentaje+2].morph.get("Number")
                  if genero[0] == 'Masc':
                    if numero[0] == 'Sing':
                      new[-1] = singularm
                    else:
                      new[-1] = masculino
                  else:
                    if numero[0] == 'Sing':
                      new[-1] = singularf
                    else:
                      new[-1] = femenino
                except:
                  try:
                    genero = tokens[porcentaje+3].morph.get("Gender")
                    numero = tokens[porcentaje+3].morph.get("Number")
                    if genero[0] == 'Masc':
                      if numero[0] == 'Sing':
                        new[-1] = singularm
                      else:
                        rules[1] = 1
                        new[-1] = masculino
                    else:
                      if numero[0] == 'Sing':
                        new[-1] = singularf
                      else:
                        rules[1] = 2
                        new[-1] = femenino
                  except:
                    new[-1] = singularm
            else:
              new.append(singularm)
        
          elif int(minusculas[porcentaje-1]) > 90 and int(minusculas[porcentaje-1]) <= 100:
            
            if int(minusculas[porcentaje-1]) > 90 and int(minusculas[porcentaje-1]) < 100: # RANGO 91 - 99%
              rules[2] = 1 # se necesita eliminar la palabra casi si se encuentra en la frase
              masculino = 'casi todos'
              femenino = 'casi todas'
              singularm = 'casi todo'
              singularf = 'casi toda'
              singular = 'casi totalmente'
        
            
            else: # RANGO 100%
              masculino = 'todos'
              femenino = 'todas'
              singularm = 'todo'
              singularf = 'toda'
              singular = 'totalmente'
        
            """ ESTA ES LA SUSTITUCIÓN """
            # Añadimos la palabra base
            if len(minusculas)>porcentaje+1 and minusculas[porcentaje+1] == 'de':
              if minusculas[porcentaje+2] == 'los':
                new[-1]=masculino
              elif minusculas[porcentaje+2] == 'las':
                new[-1]=femenino
              elif minusculas[porcentaje+2] == 'la':
                new[-1]=singularf
              elif minusculas[porcentaje+2] == 'el':
                new[-1]=singularm
              else:
                try:
                  genero = tokens[porcentaje+2].morph.get("Gender")
                  numero = tokens[porcentaje+2].morph.get("Number")
                  if genero[0] == 'Masc':
                    if numero[0] == 'Sing':
                      new[-1]='el'
                      new.append(singularm)
                    else:
                      new[-1] = 'los'
                      new.append(masculino)
                  else:
                    if numero[0] == 'Sing':
                      new[-1] = 'la'
                      new.append(singularf)
                    else:
                      new[-1] = 'las'
                      new.append(femenino)
                except:
                  new[-1] = 'el'
                  new.append(singularm)
            elif (len(minusculas)>porcentaje+1 and tokens[porcentaje+1].pos_ == 'PREP'):
              new.append(singularm)
            elif (len(minusculas)>porcentaje+1 and tokens[porcentaje+1].pos_ == 'ADJ'):
              rules[1]=1
              new.append(singular)
            elif (porcentaje-2>=0 and tokens[porcentaje-2].pos_ == 'VERB') or (porcentaje-3>=0 and tokens[porcentaje-3].pos_ == 'VERB') or (porcentaje-4>=0 and tokens[porcentaje-4].pos_ == 'VERB') or (porcentaje-5>=0 and tokens[porcentaje-5].pos_ == 'VERB') or (porcentaje-6>=0 and tokens[porcentaje-6].pos_ == 'VERB') or (porcentaje-7>=0 and tokens[porcentaje-7].pos_ == 'VERB'):
              rules[1]=1
              new.append(singular)
            else:
              new.append(singularm)
          else:
            print('ERROR EN PORCENTAJE:',tokens[porcentaje-1])
            # TO DO: determinar como sustituir porcentajes fuera del límite

          
          # RESTO DEL TEXTO
          for i in range(porcentaje-2, -1, -1):
            # RANGO 0%
            if int(minusculas[porcentaje-1]) == 0: 
              # CASO 2: es el caso más básico
              if (tokens[i].pos_ != 'DET' and tokens[i].pos_ != 'PRON') or rules[3]:
                rules[3] = 1
                if tokens[i].pos_ == 'NOUN' and tokens[i].pos_ == 'ADV':
                  rules[1] = 0

                # CASO 3: es como el caso 2 pero se niega el verbo si aparece antes de un sust/adv
                # Spacy tiene un error: identifica verbo como adjetivo cuando a este le sigue 'de'
                if (tokens[i].pos_ == 'VERB' or tokens[i].pos_ == 'AUX' or (tokens[i].pos_ == 'ADJ' and minusculas[i+1]=='de')) and not rules[1] and not rules[2] and ((i>0 and minusculas[i-1] != 'no') or i==0):
                  new.append(frase[i])
                  rules[1] = 2
                # CASO 1: es como el 2 pero se cambia 'con' por 'sin'
                elif minusculas[i] == 'con' and not rules[2]: 
                  new.append('sin')
                  rules[2] = 1
                else:
                  new.append(frase[i])

                if (((i>0 and minusculas[i-1] not in ['me', 'te', 'se', 'nos', 'os','le','les','lo','los','la','las'] and tokens[i-1].pos_ != 'AUX') or i==0) and rules[1]==2) :
                  new.append('no')
                  rules[1]=1
        
            # RANGO 1 - 75      
            elif int(minusculas[porcentaje-1])>0 and int(minusculas[porcentaje-1])<76:
              # rules[palabra base añadida, singular/masculino/femenino, duplicados, start to add]
              if (tokens[i].pos_ != 'DET' and tokens[i].pos_ != 'PRON') or rules[3]:
                rules[3] = 1
                if rules[2] == 1 and minusculas[i] == 'casi':
                  rules[2] = 0
                else:
                  rules[2] = 0
                  new.append(frase[i])
        
        
            # RANGO 76 - 90%
            elif int(minusculas[porcentaje-1]) > 75 and int(minusculas[porcentaje-1]) < 91: # no añade det/pron
              if (tokens[i].pos_ != 'DET' and tokens[i].pos_ != 'PRON') or rules[3]:
                rules[3] = 1
                if rules[2] == 1 and frase[i] == 'casi':
                  rules[2] = 0
                else:
                  rules[2] = 0
                  new.append(frase[i])
        
            # RANGO 91 - 100%
            else:
              if (tokens[i].pos_ != 'DET' and not rules[1]) or rules[3] or (tokens[i].pos_ != 'DET' and tokens[i].pos_ != 'ADP' and rules[1]):
                rules[3] = 1
                if rules[2] == 1 and frase[i] == 'casi':
                  rules[2] = 0
                else:
                  rules[2] = 0
                  new.append(frase[i])
        
          return list(reversed(new)) # Devuelve lista de strings


    def sustitucion_compuesta(self,tokens):
          frase = [i.text.lower() for i in tokens]
          porcentaje = frase.index('%')
          new = list(reversed(tokens[porcentaje:]))
          rules = [0,0,0,0]  # [base word added, no added to verb/aux, noun/adv, start to add]
          porcentajes = []
          for i in range(porcentaje-1, -1, -1):
            if rules[0] and porcentaje-1 > 0:
              new.append(tokens[i])

            if tokens[i].text.isnumeric() and not rules[0] and float(tokens[i].text)>=0 and float(tokens[i].text)<=1900:
              porcentajes.append(float(tokens[i].text))
        
            if (tokens[i].pos_ != 'ADP' and tokens[i].pos_ != 'DET' and tokens[i].pos_ != 'CONJ' and tokens[i].pos_ != 'CCONJ'and tokens[i].text != ',' and tokens[i].text != '-' and tokens[i].pos_ != 'NUM' and not rules[0]) or (not rules[0] and i==0):
              rules[0] = 1
              #sustitución
              media = sum(porcentajes) / len(porcentajes)
              tmedia = self.nlp(str(round(float(media))))
              new.append(tmedia[0])
              # añadimos la palabra anterior a los porcentajes
              #if porcentaje-2 >=0 and tokens[porcentaje-2].pos_ == 'DET':
              #  new.append(tokens[porcentaje-2])
              
              if i+1 < porcentaje-1 and tokens[i+1].text != 'entre' and tokens[i+1].text != 'alrededor' and tokens[i+1].pos_ != 'NUM':
                new.append(tokens[i+1])
              if tokens[i].pos_ != 'NUM':
                new.append(tokens[i])
      
            
          return self.sustitution(list(reversed(new)))
      
    def preparar(self,texto):
        new_texto = texto
        new_texto = new_texto.replace('0%', '0 %')
        new_texto = new_texto.replace('1%', '1 %')
        new_texto = new_texto.replace('2%', '2 %')
        new_texto = new_texto.replace('3%', '3 %')
        new_texto = new_texto.replace('4%', '4 %')
        new_texto = new_texto.replace('5%', '5 %')
        new_texto = new_texto.replace('6%', '6 %')
        new_texto = new_texto.replace('7%', '7 %')
        new_texto = new_texto.replace('8%', '8 %')
        new_texto = new_texto.replace('9%', '9 %')
        new_texto = new_texto.replace(' al ', ' a el ')
        new_texto = new_texto.replace('Al ', 'A el ')
        new_texto = new_texto.replace(' del ', ' de el ')
        new_texto = new_texto.replace('Del ', 'De el ')
        new_texto = new_texto.replace(' por ciento', ' %')
        new_texto = new_texto.replace('-', ' - ')
        new_texto = new_texto.replace('  ', ' ')
        return new_texto

    def comprobarMayusculas(self,new):
          frase = self.destokenizar(new)
          new_frase = self.preparar(frase)
          tokens = self.nlp(new_frase)
          if tokens[1].pos_ != 'SYM' and tokens[1].pos_ != 'PUNCT' and tokens[1].pos_ != 'PROPN' and tokens[1].pos_ != 'NOUN' and tokens[1].text[0]==tokens[1].text[0].upper() and tokens[1].text[1]==tokens[1].text[1].lower():
            aux = new[1]
            aux = ''.join([aux[0].lower(),aux[1:]])
            new[1] = aux
            frase = self.destokenizar(new)
            new_frase = self.preparar(frase)
            tokens = self.nlp(new_frase)
          return tokens

    def procesado(self,texto):
      
          new_texto = self.preparar(texto)
          texto_procesado = []
          
          for i,frase in enumerate(self.tokenizer.tokenize(new_texto)):

            # Tokenizamos
            tokens = self.nlp(frase)
            # Limpiamos la frase
            frase_limpia = self.limpiarTexto(tokens)
            
            # Destokenizamos
            frase = self.destokenizar([tok.text for tok in frase_limpia])
            
            # Sustituimos si queda algún porcentaje
            while '%' in frase:
              
              new = self.sustitucion_compuesta(frase_limpia)
              tokens = self.comprobarMayusculas(new)
              frase_limpia = self.limpiarTexto(tokens)
              frase = self.destokenizar([tok.text for tok in frase_limpia])
            texto_procesado.append(frase)
          texto_junto = ' '.join(texto_procesado)
          return texto_junto