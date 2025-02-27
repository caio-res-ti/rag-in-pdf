from app_gemini_api import main

def test_app():
    # Defina o caminho do seu arquivo PDF
    pdf_path = "data/CF_enxuta_280_pags.pdf"  # Substitua com o caminho correto do seu arquivo PDF
    # Defina a pergunta que você quer fazer
    question = "Qual é o artigo da Constituição que trata sobre a liberdade de expressão?"

    # Chama a função main que executa o fluxo
    resposta = main(pdf_path, question)

    # Exibe a resposta gerada pelo modelo
    print("Resposta do modelo Gemini:")
    print(resposta)

if __name__ == "__main__":
    test_app()
