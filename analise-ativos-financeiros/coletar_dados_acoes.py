import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

print("Iniciando a coleta de dados de ativos financeiros (MODO DE TESTE)...")

# --- CONFIGURAÇÃO DOS TICKERS ---
# Definimos os tickers (símbolos) das ações que queremos analisar.
tickers = ['PETR4.SA', 'MGLU3.SA', 'ITUB4.SA', 'AAPL', 'GOOGL', 'MSFT']

# Configuração de Período Desejado
data_final = datetime.now()
data_inicial = data_final - timedelta(days=5*365)
start_date_str = data_inicial.strftime('%Y-%m-%d')
end_date_str = data_final.strftime('%Y-%m-%d')

print(f"Buscando dados para o ticker de teste: {tickers[0]}")

# ---  Inspecionar o resultado do download ---
try:
    dados_acoes = yf.download(tickers, start=start_date_str, end=end_date_str)
    
    # Log de verificação de download
    print("\n--- Diagnóstico do Download ---")
    print(f"O DataFrame baixado tem {len(dados_acoes)} linhas.")
    if not dados_acoes.empty:
        print("Amostra dos dados baixados:")
        print(dados_acoes.head())
    else:
        print("O DataFrame retornado está vazio.")
    print("---------------------------\n")

    if not dados_acoes.empty:
        # Apenas executa se o download foi bem-sucedido.
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
        print("Processo finalizado sem sucesso, pois nenhum dado foi retornado.")

except Exception as e:
    print(f"Ocorreu um erro durante o download: {e}")