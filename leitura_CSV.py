import pandas as pd


df = pd.read_csv("ITENS_PROVA_2015.csv", sep = ";")
print("\033[1;32m*-*-\033[m"*23)

print(df.head()) #mostra os dados em forma de tabela


print("\033[1;32m*-*-\033[m"*23)
# for cabeçalho in df.columns:
#     print(cabeçalho) #printa o nome de todos os cabeçalhos


# transformar provas do enem no formato questão, enunciado, imagem
# etapas, passos, unir para criar sistema

materia = df.loc[df["SG_AREA"] == "MT"]
número = df.loc[df["CO_POSICAO"] == "173"]

if not número.empty:
    
    gabarito = número["TX_GABARITO"].values[0]
    questao = número["CO_POSICAO"].values[0]
    print("O gabarito da questão {} é letra {}".format(questao, gabarito))
    print(materia)

else:
    print("Nenhuma linha encontrada")

