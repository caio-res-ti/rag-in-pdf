import os
import logging
from dotenv import load_dotenv
import tiktoken
import re
import chromadb
import google.generativeai as genai

# Configuração básica de log: logs serão mostrados com timestamp e nível de severidade
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para carregar a chave da API do Google do arquivo .env
def load_api_key():
    load_dotenv()  # Carrega variáveis de ambiente do arquivo .env
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        logging.error("Chave inexistente ou não definida no .env")
        raise ValueError("Chave inexistente ou não definida no .env")
    logging.debug("Chave da API carregada com sucesso")
    return google_api_key

# Função para calcular o número de tokens a partir de uma string de texto
def num_tokens_from_string(string: str) -> int:
    """Retorna o número de tokens em uma string de texto."""
    encoding_name = "cl100k_base"  # Especifica o tipo de codificação
    encoding = tiktoken.get_encoding(encoding_name)  # Obtém a codificação
    num_tokens = len(encoding.encode(string))  # Calcula o número de tokens
    logging.debug(f"Número de tokens calculado: {num_tokens}")
    return num_tokens

# Função para pré-processar o texto (limpeza)
def pre_process_text(text: str) -> str:
    """Remove espaços extras, linhas vazias e pontos excessivos do texto."""
    logging.debug("Iniciando o pré-processamento do texto")
    text = text.strip()  # Remove espaços no início e fim
    lines = text.split('\n')  # Divide o texto em linhas
    non_empty_lines = [line for line in lines if line.strip() != '']  # Remove linhas vazias
    text = '\n'.join(non_empty_lines)  # Junta as linhas novamente

    lines = text.split('\n')  # Divide novamente
    filtered_lines = [line for line in lines if not re.search(r'\.{6,}', line)]  # Remove linhas com mais de 5 pontos
    text = '\n'.join(filtered_lines)  # Junta as linhas sem os pontos excessivos

    text = re.sub(r'\s{2,}', ' ', text)  # Substitui múltiplos espaços por um único
    logging.debug("Texto pré-processado com sucesso")
    return text

# Função para carregar o documento PDF usando o PyMuPDF
def load_pdf_document(file_path: str):
    from langchain_community.document_loaders import PyMuPDFLoader
    logging.debug(f"Iniciando o carregamento do documento PDF: {file_path}")
    loader = PyMuPDFLoader(file_path)  # Carrega o PDF
    docs = loader.load()  # Extrai o conteúdo do PDF
    for doc in docs:
        doc.page_content = pre_process_text(doc.page_content)  # Pré-processa o conteúdo das páginas
    logging.debug(f"Documento PDF carregado, número de páginas: {len(docs)}")
    return docs

# Função para dividir o conteúdo do documento em partes menores
def split_text(docs):
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    logging.debug("Iniciando a divisão do texto em partes menores")

    # Define a estratégia de divisão do texto
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,  # Tamanho máximo de cada parte
        chunk_overlap=25,  # Sobreposição entre as partes
        length_function=len,
        is_separator_regex=False,
    )
    splits = text_splitter.split_documents(docs)  # Divide o documento em partes
    logging.debug(f"Texto dividido em {len(splits)} partes")
    return splits

# Função para configurar o banco de dados ChromaDB com os textos divididos
def configure_chromadb(splits):
    client = chromadb.Client()  # Inicializa o cliente do ChromaDB
    documents = [data.page_content for data in splits]  # Extrai os textos
    metadatas = [{'source': data.metadata.get('source', 'unknown')} for data in splits]  # Obtém metadados
    ids = [str(index + 1) for index in range(len(splits))]  # Gera IDs únicos para os documentos

    law_collection = client.get_or_create_collection(name="law_collection")  # Cria ou obtém uma coleção
    law_collection.add(documents=documents, metadatas=metadatas, ids=ids)  # Adiciona os documentos ao ChromaDB
    logging.debug(f"{len(documents)} documentos adicionados ao ChromaDB")
    return law_collection

# Função para realizar uma consulta no banco de dados ChromaDB
def query_chromadb(law_collection, question):
    logging.debug(f"Consultando o banco de dados ChromaDB com a pergunta: {question}")
    results = law_collection.query(query_texts=[question], n_results=15)  # Realiza a consulta
    context = "\n".join(x for x in results['documents'][0])  # Obtém o contexto mais relevante
    logging.debug(f"Contexto adquirido, tamanho do contexto: {len(context)} caracteres")
    return context

# Função para interagir com o modelo Gemini da Google para gerar respostas
def query_gemini_api(context, question, google_api_key):
    logging.debug("Iniciando a consulta ao modelo Gemini")
    genai.configure(api_key=google_api_key)  # Configura a API do Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')  # Define o modelo
    prompt = f"role: você é um assistente jurídico prestativo, que justifica com leis, artigos, incisos e traz informações a mais em suas respostas. Com base neste contexto {context}. Responda: {question}."
    
    response = model.generate_content(prompt)  # Gera a resposta do modelo
    logging.debug(f"Resposta recebida do modelo Gemini, comprimento: {len(response.text)} caracteres")
    return response.text

# Função principal para realizar todo o fluxo de processamento
def main(pdf_path, question):
    logging.debug("Iniciando o processo")
    google_api_key = load_api_key()  # Carrega a chave da API

    # Carregar o documento e dividir em partes
    docs = load_pdf_document(pdf_path)
    splits = split_text(docs)
    
    # Configurar o banco de dados ChromaDB e consultar
    law_collection = configure_chromadb(splits)
    context = query_chromadb(law_collection, question)

    # Consultar o modelo Gemini e retornar a resposta
    response = query_gemini_api(context, question, google_api_key)
    logging.debug("Processo finalizado com sucesso")
    return response