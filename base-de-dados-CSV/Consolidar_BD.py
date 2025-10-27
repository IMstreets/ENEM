import pandas as pd
import glob
import re
import os

# Caminho para a pasta com os arquivos
# IMPORTANTE: Modifique este caminho para onde estão seus arquivos
pasta = os.path.dirname(os.path.abspath(__file__))  # Pega o diretório do script

print(f"Procurando arquivos em: {pasta}\n")

# Debug: lista todos os arquivos CSV na pasta
print("=== DEBUG: Listando todos os arquivos CSV na pasta ===")
todos_csv = glob.glob(os.path.join(pasta, '*.csv'))
if not todos_csv:
    # Tenta também listar arquivos sem usar glob
    print("Tentando listar arquivos diretamente...")
    try:
        todos_arquivos = os.listdir(pasta)
        todos_csv = [os.path.join(pasta, f) for f in todos_arquivos if f.endswith('.csv')]
    except Exception as e:
        print(f"Erro ao listar arquivos: {e}")
for f in todos_csv:
    print(f"  - {os.path.basename(f)}")
print(f"Total de CSVs encontrados: {len(todos_csv)}\n")

# Busca todos os arquivos CSV que seguem o padrão do nome
arquivos = [f for f in todos_csv if 'ITENS_PROVA_' in os.path.basename(f) and f != 'ITENS_PROVA_CONSOLIDADO.csv']

# Ordena os arquivos por nome
arquivos.sort()

# Lista para armazenar os dataframes
dfs = []

print(f"Arquivos ITENS_PROVA encontrados: {len(arquivos)}\n")

for arquivo in arquivos:
    # Extrai o ano do nome do arquivo usando regex
    match = re.search(r'ITENS_PROVA_(\d{4})\.csv', os.path.basename(arquivo))
    
    if match:
        ano = match.group(1)
        print(f"Processando arquivo: {os.path.basename(arquivo)} - Ano: {ano}")
        
        # Lê o arquivo CSV com separador ponto e vírgula
        df = pd.read_csv(arquivo, sep=';', encoding='latin1')
        
        # Adiciona a coluna ANO_PROVA
        df['ANO_PROVA'] = int(ano)
        
        # Adiciona à lista
        dfs.append(df)
    else:
        print(f"AVISO: Não foi possível extrair o ano do arquivo: {os.path.basename(arquivo)}")

# Concatena todos os dataframes
if dfs:
    df_consolidado = pd.concat(dfs, ignore_index=True)
    
    print(f"\n{'='*60}")
    print(f"Total de registros consolidados: {len(df_consolidado)}")
    print(f"Anos presentes: {sorted(df_consolidado['ANO_PROVA'].unique())}")
    print(f"{'='*60}\n")
    
    # Salva o arquivo consolidado
    arquivo_saida = 'ITENS_PROVA_CONSOLIDADO.csv'
    df_consolidado.to_csv(arquivo_saida, sep=';', index=False, encoding='utf-8')
    
    print(f"Arquivo consolidado salvo como: {arquivo_saida}")
    print(f"\nPrimeiras linhas do arquivo consolidado:")
    print(df_consolidado.head())
    print(f"\nÚltimas linhas do arquivo consolidado:")
    print(df_consolidado.tail())
else:
    print("Nenhum arquivo foi processado. Verifique o caminho e o padrão dos nomes dos arquivos.")