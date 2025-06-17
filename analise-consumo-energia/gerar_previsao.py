import pandas as pd
from prophet import Prophet
import warnings
import os

warnings.simplefilter('ignore', FutureWarning)

print("Iniciando processo AVANÇADO de previsão por unidade...")

# --- 1. Carregar o Dataset Detalhado Original ---
print("Carregando o dataset detalhado...")
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_filename = 'consumo_energia_supermercados_v2.csv'
csv_path = os.path.join(script_dir, csv_filename)

try:
    df_detalhado = pd.read_csv(csv_path, parse_dates=['Data'])
except FileNotFoundError:
    print(f"Erro: O arquivo '{csv_filename}' não foi encontrado.")
    exit()

# --- 2. Iterar e Gerar Previsão para Cada Unidade ---
unidades = df_detalhado['Unidade'].unique()
all_forecasts = []

print(f"Encontradas {len(unidades)} unidades. Iniciando loop de previsão...")

for i, unidade in enumerate(unidades):
    print(f"Processando unidade {i+1}/{len(unidades)}: {unidade}")

    # Filtra o dataframe para a unidade atual
    df_unidade = df_detalhado[df_detalhado['Unidade'] == unidade].copy()
    
    # Prepara os dados para o Prophet ('ds' e 'y')
    df_prophet = df_unidade[['Data', 'Consumo kWh']].rename(columns={'Data': 'ds', 'Consumo kWh': 'y'})

    # Cria e treina um modelo específico para esta unidade
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
    model.fit(df_prophet)

    # Cria datas futuras para a previsão
    future_dates = model.make_future_dataframe(periods=200, freq='D')
    forecast = model.predict(future_dates)
    
    # Adiciona o nome da unidade ao resultado da previsão
    forecast['Unidade'] = unidade
    
    # Adiciona o resultado à lista de todas as previsões
    all_forecasts.append(forecast)

print("Loop de previsão finalizado.")

# --- 3. Consolidar e Unir os Dados ---
print("Consolidando todos os resultados...")
# Concatena os resultados de todas as 92 previsões em um único dataframe
forecast_completo = pd.concat(all_forecasts)

# Seleciona e renomeia as colunas importantes
forecast_final = forecast_completo[['ds', 'Unidade', 'yhat']].rename(columns={
    'ds': 'Data',
    'yhat': 'Consumo_Previsto_kWh'
})
forecast_final['Consumo_Previsto_kWh'] = forecast_final['Consumo_Previsto_kWh'].round(2)

# Unimos a previsão detalhada com os dados detalhados históricos
# Usamos um merge 'outer' para garantir que TODAS as datas (passadas e futuras) sejam mantidas
df_final = pd.merge(df_detalhado, forecast_final, on=['Data', 'Unidade'], how='outer')

# Organiza o dataframe por unidade e data
df_final = df_final.sort_values(by=['Unidade', 'Data'])

# Exporta o resultado para um novo e único CSV
output_filename = 'dataset_final_com_previsao_por_loja.csv'
df_final.to_csv(output_filename, index=False, date_format='%Y-%m-%d')

print(f"Processo finalizado! Dataset unificado salvo em '{output_filename}'.")