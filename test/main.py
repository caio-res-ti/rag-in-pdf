import os
import logging
import tiktoken
import chromadb
import re
import requests
import json
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configuração de log
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configurações para personalização fácil no código
OLLAMA_URL = "http://10.159.11.24:11434/api/generate"  # URL do modelo Ollama
CHUNK_SIZE = 1024  # Tamanho do chunk
CHUNK_OVERLAP = 25  # Sobreposição de chunks
N_RESULTS = 15  # Número de resultados a serem retornados pelo ChromaDB
MODEL_OLLAMA = "gemma2:latest"  # Nome do modelo no Ollama (por exemplo, "mistral", "gemma:7b", etc.)

# Definindo o caminho do PDF e a pergunta
pdf_path = "data/CF_enxuta_280_pags.pdf"  # Caminho para o arquivo PDF
question = "O que a constituição diz sobre liberdade de expressão?"  # Pergunta para o modelo

# Defina se vai usar o Ollama ou o Gemini
use_ollama = False  # Mude para False para usar o modelo Gemini

# Função para calcular o número de tokens em uma string
def num_tokens_from_string(string: str) -> int:
    encoding_name = "cl100k_base"
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    logging.debug(f"Número de tokens calculado: {num_tokens}")
    return num_tokens

# Função para pré-processar o texto
def pre_process_text(text: str) -> str:
    logging.debug("Iniciando o pré-processamento do texto")
    text = text.strip()
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip() != '']
    text = '\n'.join(non_empty_lines)

    lines = text.split('\n')
    filtered_lines = [line for line in lines if not re.search(r'\.{6,}', line)]
    text = '\n'.join(filtered_lines)

    text = re.sub(r'\s{2,}', ' ', text)
    logging.debug("Texto pré-processado com sucesso")
    return text

# Função para carregar o documento PDF
def load_pdf_document(file_path: str):
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    for doc in docs:
        doc.page_content = pre_process_text(doc.page_content)
    logging.debug(f"Documento PDF carregado, número de páginas: {len(docs)}")
    return docs

# Função para dividir o conteúdo do documento em partes menores
def split_text(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    splits = text_splitter.split_documents(docs)
    logging.debug(f"Texto dividido em {len(splits)} partes")
    return splits

# Função para configurar o banco de dados ChromaDB
def configure_chromadb(splits):
    client = chromadb.Client()
    documents = [data.page_content for data in splits]
    metadatas = [{'source': data.metadata.get('source', 'unknown')} for data in splits]
    ids = [str(index + 1) for index in range(len(splits))]

    law_collection = client.get_or_create_collection(name="law_collection")
    law_collection.add(documents=documents, metadatas=metadatas, ids=ids)
    logging.debug(f"{len(documents)} documentos adicionados ao ChromaDB")
    return law_collection

# Função para realizar uma consulta no banco de dados ChromaDB
def query_chromadb(law_collection, question):
    logging.debug(f"Consultando o banco de dados ChromaDB com a pergunta: {question}")
    results = law_collection.query(query_texts=[question], n_results=N_RESULTS)
    context = "\n".join(x for x in results['documents'][0])
    logging.debug(f"Contexto adquirido, tamanho do contexto: {len(context)} caracteres")
    return context

# Função para interagir com o modelo Gemini (Google)
def query_gemini_api(context, question):
    logging.debug("Iniciando a consulta ao modelo Gemini")
    genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))  # Passa a chave
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"role: você é um assistente jurídico prestativo, que justifica com leis, artigos, incisos e traz informações a mais em suas respostas. Com base neste contexto {context}. Responda: {question}."
    response = model.generate_content(prompt)
    logging.debug(f"Resposta recebida do modelo Gemini, comprimento: {len(response.text)} caracteres")
    return response.text

# Função para interagir com o modelo Ollama
def query_ollama_api(context, question):
    logging.debug("Iniciando a consulta ao modelo Ollama")
    prompt = f"Em português, responda a pergunta com base no contexto: {context}. Pergunta: {question}. Justifique-se"
    data = {
        "model": MODEL_OLLAMA,
        "prompt": prompt,
        "stream": False,
        "num_ctx": 4096
    }
    response = requests.post(OLLAMA_URL, json=data)
    dic = json.loads(response.text)
    answer = dic['response']
    logging.debug(f"Resposta recebida do modelo Ollama, comprimento: {len(answer)} caracteres")
    return answer

# Função principal para carregar o PDF e configurar ChromaDB
def load_chromadb(pdf_path):
    # Carregar o documento e dividir em partes
    docs = load_pdf_document(pdf_path)
    splits = split_text(docs)
    
    # Configurar o banco de dados ChromaDB
    law_collection = configure_chromadb(splits)
    logging.debug("ChromaDB carregado com sucesso.")
    return law_collection

# Função principal para controlar o fluxo de consulta
def query_law_collection(law_collection, question, use_ollama=True):
    logging.debug("Iniciando o processo de consulta")

    # Consultar o banco de dados ChromaDB para obter o contexto
    context = query_chromadb(law_collection, question)

    # Consultar o modelo escolhido (Ollama ou Gemini) e retornar a resposta
    if use_ollama:
        response = query_ollama_api(context, question)
    else:
        response = query_gemini_api(context, question)

    logging.debug("Processo finalizado com sucesso")
    return response

# Função para interagir com o terminal e fazer consultas
def interactive_query():
    # Carregar ChromaDB uma vez
    law_collection = load_chromadb(pdf_path)
    
    # Loop interativo para fazer consultas repetidas
    while True:
        question = input("Digite sua pergunta (ou 'sair' para terminar): ")
        if question.lower() == 'sair':
            print("Saindo...")
            break
        
        response = query_law_collection(law_collection, question, use_ollama)
        print("Resposta recebida:")
        print(response)

if __name__ == "__main__":
    # Iniciar o loop interativo
    interactive_query()
