import pandas as pd
import os

base_de_dados_CSV = r"base-de-dados-CSV"
lista_ano = [2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024]

for ano in lista_ano:
    arquivo_csv = os.path.join(base_de_dados_CSV, f"ITENS_PROVA_{str(ano)}.csv")

    df = pd.read_csv(arquivo_csv, sep=";", encoding="latin1", decimal=".")
    
    # Substitui vírgula por ponto, converte para float
    df["NU_PARAM_B"] = (
        df["NU_PARAM_B"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    # Função para aplicar a fórmula com tratamento de exceção
    def ajustar_nota(valor):
        try:
            if (100000 < valor > 1000) or (-1000 > valor < -100000):
                nota = valor + 500
            elif 10 > valor > -10:
                nota = (valor*100) + 500
            else:
                nota = 0
                
            return "{:.2f}".format(nota)
        except (ValueError, TypeError):
            print(f"[ERRO] Ano {ano} | | Valor inválido: {valor}")
            # mantém o valor original
            df.at["CO_POSICAO", "NU_PARAM_B"] = valor
    

    #Pega apenas as colunas onde a prova é do caderno azul
    df = df[df["TX_COR"].str.upper() == "AZUL"]

    # Aplica a função AJUSTAR NOTA a toda a coluna (descomente a linha abaixo caso precise)
    df["NU_PARAM_B"] = df["NU_PARAM_B"].apply(ajustar_nota)

    df["NU_PARAM_B"] = (
        df["NU_PARAM_B"]
        .astype(str)
        .str.replace(".", ",", regex=False)
    )


    # Salva o CSV sobrescrevendo o original
    df.to_csv(arquivo_csv, sep=";", index=False, encoding="latin1")

    print(f"Arquivo {ano} atualizado com sucesso!")

# Exibe última base processada
# print(df[["CO_POSICAO", "NU_PARAM_B","TX_COR"]])

