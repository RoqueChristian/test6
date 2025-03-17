import pandas as pd

# Carregar o arquivo CSV
df = pd.read_csv("df_vendas.csv")

# Verificar o tipo de dados da coluna 'Data_Emissao'
print(f"Tipo de dados original de 'Data_Emissao': {df['Data_Emissao'].dtype}")

# Verificar se a coluna 'Data_Emissao' já está em datetime, caso contrário, converter
if df['Data_Emissao'].dtype == 'object':  # Se a coluna for do tipo 'object' (string)
    try:
        # Tentar converter as datas no formato brasileiro 'dd/mm/yyyy'
        df['Data_Emissao'] = pd.to_datetime(df['Data_Emissao'], format='%d/%m/%Y', errors='coerce')
        print("Conversão bem-sucedida para datetime no formato brasileiro (dd/mm/yyyy).")
    except Exception as e:
        print(f"Erro ao tentar converter datas: {e}")
else:
    print("A coluna 'Data_Emissao' já está em formato datetime.")

# Verificar se a conversão foi realizada corretamente
print(f"Tipo de dados após a conversão: {df['Data_Emissao'].dtype}")

# Verificar se há valores inválidos (NaT) após a conversão
valores_invalidos = df[df['Data_Emissao'].isna()]
print(f"Entradas inválidas após conversão:\n{valores_invalidos}")
