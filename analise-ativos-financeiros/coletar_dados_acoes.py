import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

print("Iniciando a coleta de dados de ativos financeiros (MODO DE TESTE)...")

# --- TESTE 1: Simplificar a lista de tickers ---
# Vamos testar com apenas uma ação internacional para minimizar as variáveis.
tickers = ['MSFT'] 

# Mantemos o período de 5 anos
data_final = datetime.now()
data_inicial = data_final - timedelta(days=5*365)
start_date_str = data_inicial.strftime('%Y-%m-%d')
end_date_str = data_final.strftime('%Y-%m-%d')

print(f"Buscando dados para o ticker de teste: {tickers[0]}")

# --- TESTE 2: Inspecionar o resultado do download ---
try:
    dados_acoes = yf.download(tickers, start=start_date_str, end=end_date_str)
    
    # Adicionamos um print para verificar o que foi baixado
    print("\n--- Diagnóstico do Download ---")
    print(f"O DataFrame baixado tem {len(dados_acoes)} linhas.")
    if not dados_acoes.empty:
        print("Amostra dos dados baixados:")
        print(dados_acoes.head())
    else:
        print("O DataFrame retornado está VAZIO. Isso confirma que a busca de dados falhou silenciosamente.")
    print("---------------------------\n")

    if not dados_acoes.empty:
        # O resto do script só executa se os dados forem baixados com sucesso
        dados_formatados = dados_acoes.stack().reset_index()
        dados_formatados = dados_formatados.rename(columns={
            'Date': 'data',
            'level_1': 'ticker',
            'Open': 'preco_abertura',
            'High': 'preco_maximo',
            'Low': 'preco_minimo',
            'Close': 'preco_fechamento',
            'Adj Close': 'preco_fechamento_ajustado',
            'Volume': 'volume'
        })
        
        output_filename = 'dados_historicos_acoes.csv'
        dados_formatados.to_csv(output_filename, index=False)
        print(f"Processo concluído. Os dados foram salvos em '{output_filename}'.")
    else:
        print("Processo finalizado sem salvar dados, pois nenhum foi retornado.")

except Exception as e:
    print(f"Ocorreu um erro durante o download: {e}")