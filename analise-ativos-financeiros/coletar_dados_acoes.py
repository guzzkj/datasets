import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

print("Iniciando a coleta de dados de ativos financeiros...")

# --- Configuração dos Tickers ---
# O sufixo ".SA" indica que a ação é da bolsa de São Paulo (B3).
tickers = ['PETR4.SA', 'MGLU3.SA', 'ITUB4.SA', 'AAPL', 'GOOGL', 'MSFT']

# Período de tempo para a análise (últimos 5 anos)
data_final = datetime.now()
data_inicial = data_final - timedelta(days=5*365)
start_date_str = data_inicial.strftime('%Y-%m-%d')
end_date_str = data_final.strftime('%Y-%m-%d')

print(f"Buscando dados para os tickers: {', '.join(tickers)}")
print(f"Período: {start_date_str} a {end_date_str}")

# --- Coleta de Dados ---
dados_acoes = yf.download(tickers, start=start_date_str, end=end_date_str)

if not dados_acoes.empty:
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


    colunas_preco = [col for col in dados_formatados.columns if 'preco' in col]

    dados_formatados[colunas_preco] = dados_formatados[colunas_preco].round(2)
    print("Casas decimais arredondadas para 2 dígitos.")

    output_filename = 'dados_historicos_acoes.csv'
    

    dados_formatados.to_csv(output_filename, index=False, decimal=',')
    
    print(f"\nProcesso concluído. Os dados foram salvos em '{output_filename}' usando VÍRGULA como separador decimal.")
    print("\nPré-visualização dos dados formatados:")
    print(dados_formatados.tail())
else:
    print("Nenhum dado foi retornado pelo yfinance.")