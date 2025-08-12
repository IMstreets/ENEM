import os
import json
import leitura_CSV as microdados

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def fetch_question_details(ano, numero_questao):
    caminho_arquivo = os.path.join(
        BASE_DIR, "enem-api", "public",
        str(ano), "questions", str(numero_questao), "details.json"
    )
    
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return dados
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        exit()
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON em {caminho_arquivo}: {e}")
        exit()

# Teste

detalhes = fetch_question_details(2015, int(microdados.número))
print(detalhes["context"])
print("\n")
print(detalhes["files"])
print("\n")
print(detalhes["alternativesIntroduction"])
print("\n{}) {}\n".format(detalhes["alternatives"][0]["letter"],detalhes["alternatives"][0]["text"]))
print("{}) {}\n".format(detalhes["alternatives"][1]["letter"],detalhes["alternatives"][1]["text"]))
print("{}) {}\n".format(detalhes["alternatives"][2]["letter"],detalhes["alternatives"][2]["text"]))
print("{}) {}\n".format(detalhes["alternatives"][3]["letter"],detalhes["alternatives"][3]["text"]))
print("{}) {}\n".format(detalhes["alternatives"][4]["letter"],detalhes["alternatives"][4]["text"]))

# print("\n")
# print(detalhes["alternatives"][0]["letter"])



### isso pega cada questão pela API e retorna um dicionário no formato: {"title": "{Nº questão} - ENEM {ano}", index: {nº questão}, "year": {ano},} 


    