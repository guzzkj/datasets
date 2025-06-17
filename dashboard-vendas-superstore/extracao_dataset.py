import kagglehub
import pandas as pd

print("Iniciando o download do dataset Superstore do Kaggle...")

dataset_path = "vivek468/superstore-dataset-final/Super-Store-Dataset.csv"

try:

    df = kagglehub.load_dataset(dataset_path)

    print("Dataset carregado com sucesso na memória!")
    print("Amostra dos dados:")
    print(df.head())

    # Agora, salvamos o DataFrame em um arquivo CSV local
    output_filename = 'Superstore.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8')
    
    print(f"\nSucesso! O dataset foi salvo como '{output_filename}' na sua pasta.")
    print("Você já pode usar este arquivo no Tableau.")

except Exception as e:
    print(f"\nOcorreu um erro: {e}")
    print("Verifique se o arquivo 'kaggle.json' está na pasta correta (C:/Users/SEU_USUARIO/.kaggle/) ou se há algum problema de conexão.")