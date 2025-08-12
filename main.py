#PAREI NA PARTE DE FAZER UM FOR COM O NUMERO DE QUESTÕES QUE O USUÁRIO QUER IMPLEMENTAR


import os
import json
import leitura_CSV as microdados


ano = int(input("Qual o ano de execução da prova? "))

print("""Qual a area que deseja imprimir?
      MT para Matemática
      CN para Ciências da Natureza
      LC para linguagens e suas comunicações
      CH para Ciências Humanas
      """)


area = input("Diga qual a area que deseja: ").upper().strip()

if area == "MT" or "CN" or "LC" or "CH":



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

detalhes = fetch_question_details(ano, int(microdados.questao))

# Aqui começa o print da questão
if detalhes["context"]:
    print(detalhes["context"])
    print("\n")

if detalhes["files"]:
    print(detalhes["files"])
    print("\n")

if detalhes["alternativesIntroduction"]:
    print(detalhes["alternativesIntroduction"])

print("\n{}) {}\n".format(detalhes["alternatives"][0]["letter"],detalhes["alternatives"][0]["text"]))
print("{}) {}\n".format(detalhes["alternatives"][1]["letter"],detalhes["alternatives"][1]["text"]))
print("{}) {}\n".format(detalhes["alternatives"][2]["letter"],detalhes["alternatives"][2]["text"]))
print("{}) {}\n".format(detalhes["alternatives"][3]["letter"],detalhes["alternatives"][3]["text"]))
print("{}) {}\n".format(detalhes["alternatives"][4]["letter"],detalhes["alternatives"][4]["text"]))

