import pandas as pd
import os

base_de_dados_CSV = r"base-de-dados-CSV"
lista_ano = [2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024]

for ano in lista_ano:
    arquivo_csv = os.path.join(base_de_dados_CSV, f"ITENS_PROVA_{str(ano)}.csv")

    df = pd.read_csv(arquivo_csv, sep=";", encoding="latin1")

    # Função para aplicar a fórmula com tratamento de exceção
    def ajustar_nota(valor):
        try:
            # Substitui vírgula por ponto, converte para float e aplica fórmula
            numero = float(str(valor).replace(",", "."))
            if -10 < numero < 10:
                nota = numero * 100 + 500
            else:
                nota = (numero/1000) + 500
            # Retorna como string com 2 casas decimais, usando vírgula
            return "{:.2f}".format(nota)
        except (ValueError, TypeError):
            print(f"[ERRO] Ano {ano} | Linha {i} | Valor inválido: {valor}")
            # mantém o valor original
            df.at[i, "NU_PARAM_B"] = valor
    # Aplica a função a toda a coluna
    df["NU_PARAM_B"] = df["NU_PARAM_B"].apply(ajustar_nota)

    # Salva o CSV sobrescrevendo o original
    df.to_csv(arquivo_csv, sep=";", index=False, encoding="latin1")

    print(f"Arquivo {ano} atualizado com sucesso!")

# Exibe última base processada
print(df[["CO_POSICAO", "NU_PARAM_B"]])