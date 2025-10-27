import pandas as pd

# Carrega o CSV consolidado
df = pd.read_csv('base-de-dados-CSV/ITENS_PROVA_CONSOLIDADO.csv', sep=';', encoding='utf-8', decimal=',')

# Filtra por Matemática
df_mt = df[df['SG_AREA'] == 'MT'].copy()

print("=== ANÁLISE DE HABILIDADES - MATEMÁTICA ===\n")

# Verifica o tipo e valores da coluna CO_HABILIDADE
print(f"Total de questões de Matemática: {len(df_mt)}")
print(f"\nTipo da coluna CO_HABILIDADE: {df_mt['CO_HABILIDADE'].dtype}")
print(f"\nValores únicos de CO_HABILIDADE:")
print(df_mt['CO_HABILIDADE'].value_counts().sort_index())

# Verifica se há valores NaN
print(f"\nValores NaN em CO_HABILIDADE: {df_mt['CO_HABILIDADE'].isna().sum()}")

# Verifica questões com habilidades 6, 7, 8, 9
habilidades_desejadas = [6.0, 7.0, 8.0, 9.0]
df_filtrado = df_mt[df_mt['CO_HABILIDADE'].isin(habilidades_desejadas)]

print(f"\n=== FILTRO POR HABILIDADES 6, 7, 8, 9 ===")
print(f"Questões encontradas: {len(df_filtrado)}")

if len(df_filtrado) > 0:
    print("\nDistribuição por ano:")
    print(df_filtrado['ANO_PROVA'].value_counts().sort_index())
    
    print("\nPrimeiras 5 questões encontradas:")
    print(df_filtrado[['ANO_PROVA', 'CO_POSICAO', 'CO_HABILIDADE', 'TX_GABARITO']].head())
else:
    print("\n⚠️ NENHUMA QUESTÃO ENCONTRADA!")
    print("\nVerificando exemplos de valores na coluna:")
    print(df_mt['CO_HABILIDADE'].head(20))