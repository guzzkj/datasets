import kagglehub
import pandas as pd

print("Iniciando o download do dataset Superstore do Kaggle...")

# CORREÇÃO: O caminho completo do dataset, incluindo o nome do arquivo, 
# é passado em uma única string.
dataset_path = "vivek468/superstore-dataset-final/Super-Store-Dataset.csv"

try:
    # CORREÇÃO: A chamada da função agora usa apenas o caminho completo, 
    # sem o parâmetro 'file_path'.
    df = kagglehub.load_dataset(dataset_path)

    print("Dataset carregado com sucesso na memória!")
    print("Amostra dos dados:")
    print(df.head())

    # Agora, salvamos o DataFrame em um arquivo CSV local
    output_filename = 'superstore_dataset_local.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8')
    
    print(f"\nSucesso! O dataset foi salvo como '{output_filename}' na sua pasta.")
    print("Você já pode usar este arquivo no Tableau.")

except Exception as e:
    print(f"\nOcorreu um erro: {e}")
    print("Verifique se o arquivo 'kaggle.json' está na pasta correta (C:/Users/SEU_USUARIO/.kaggle/) ou se há algum problema de conexão.")