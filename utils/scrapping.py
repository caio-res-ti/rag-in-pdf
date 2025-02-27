import time
from selenium import webdriver
from bs4 import BeautifulSoup
import re


output_folder = r".\\output"
rx_num_decreto = r"\/(D[0-9]+)\."

# Inicializa o WebDriver
chrome = webdriver.Chrome()
link_home = "https://www4.planalto.gov.br/legislacao/portal-legis/legislacao-1/decretos1/2024-decretos"
chrome.get(link_home)

# Força a espera 
time.sleep(5)
print("Aguarde...")
time.sleep(5)

# Pega o html da página
page_html = chrome.page_source
chrome.quit()

# Inicializa um objeto BeautifulSoup
soup = BeautifulSoup(page_html, 'html.parser')

print("Aguarde...")
time.sleep(5)

# Pega a tabela com os links dos decretos
table = soup.find("table", class_="visaoQuadrosTabela")

if table:
    for row in table.find_all("tr"):
        for cell in row.find_all("td"):
            href_decreto = cell.find('a')
            if href_decreto:
                
                # Pegar o link do decreto
                link_decreto = href_decreto.get("href")

                # Acessar o link
                chrome = webdriver.Chrome()
                chrome.get(link_decreto)

                # Força a espera 
                time.sleep(5)
                print("Aguarde...")
                time.sleep(5)

                # Pega o html da página do Decreto
                page_html = chrome.page_source
                chrome.quit()

                print("Aguarde...")
                time.sleep(5)

                # Inicializa um objeto BeautifulSoup
                soup = BeautifulSoup(page_html, 'html.parser')

                # Pega o texto da página
                texto = soup.get_text()

                # Salvar o texto em um txt
                num_decreto = re.findall(rx_num_decreto, link_decreto)
                print("Salvando texto...", num_decreto[0])
                if num_decreto:
                    print(num_decreto[0])
                    nome_arquivo = output_folder + "//" + num_decreto[0] + ".txt"
                    with open(nome_arquivo, "w", encoding="utf-8") as f:
                        f.write(texto)


else:
    print("Nenhuma tabela foi encontrada.")



print("\n Finalizado.")