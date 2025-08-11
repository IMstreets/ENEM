
import pandas as pd


df = pd.read_csv("ITENS_PROVA_2015.csv", sep = ";")
# print("\033[1;32m*-*-\033[m"*23)

# print(df.head()) #mostra os dados em forma de tabela


# print("\033[1;32m*-*-\033[m"*23)
# for cabeçalho in df.columns:
#     print(cabeçalho) #printa o nome de todos os cabeçalhos


# transformar provas do enem no formato questão, enunciado, imagem
# etapas, passos, unir para criar sistema

class prova():
    def __init__(self,co_prova,materia,):
        self.co_prova = co_prova
codigo_prova = df.loc[df["CO_PROVA"] == "CN"]
materia = df.loc[df["SG_AREA"] == "CN"]
linha = df.loc[df["CO_POSICAO"] == 46]

if not linha.empty:
    
    gabarito = linha["TX_GABARITO"].values[0]
    número = linha["CO_POSICAO"].values[0]
    print("O gabarito da questão {} é letra {}".format(número, gabarito))
    print(materia)

else:
    print("Nenhuma linha encontrada")