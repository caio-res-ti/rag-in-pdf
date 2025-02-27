import requests
import json
import os
import time
from pprint import pprint

os.system("clear; echo 'Processing...' ")

model_name = "llama3"

prompt = """Instructions: Você é um assistente para definição de uma lista de tipos de documentos baseada na área de negócio de uma empresa. Dada uma área de negócio a ser fornecida através de um contexto,
sua tarefa é criar uma lista de tipos documentos possíveis para esse ramo de negócio. Você deve responder apenas com a lista e não incluir qualquer informação adicional. Seja preciso e objetivo.
Contexto: Minha empresa de contabilidade presta serviços de contabilidade para diversas empresas de ramos diversos e possui as seguintes áreas: registro e escrituração contábil, comercial, Recursos Humanos, 
Consultoria Tributária e Jurídica. 
Output indicator: json"""

prompt = """Contexto: escola de ensino fundamental e médio que presta serviços de ensino para crianças e jovens e possui as áeras de: registro escolar, contabilidade, secretaria acadêmica, Recursos Humanos e Diretoria."""

system = """Você é um assistente para definição de uma lista de tipos de documentos baseada na área de negócio de uma empresa. Dada uma área de negócio a ser fornecida através de um contexto,
sua tarefa é criar uma lista de tipos documentos possíveis para essa área de negócio. Você deve responder em Português do Brasil. Seja preciso e inclua na resposta os campos tipo, descrição e área."""

format = 'json'

stream = False

num_ctx = 4096

url = "http://10.159.11.24:11434/api/generate"
#data = {"model": model_name, "prompt": prompt, "stream": stream, "num_ctx": num_ctx, "format": format, "system": system}
data = {"model": model_name, "prompt": prompt, "stream": stream, "format": format, "system": system}

response = requests.post(url, json=data)
#response.text

dic = json.loads(response.text)
pprint(dic['response'])
