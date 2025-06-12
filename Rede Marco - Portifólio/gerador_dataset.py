import os
import pandas as pd
import numpy as np
import datetime

print("Iniciando a geração do dataset de consumo de energia...")

# --- 1. Definição das Lojas (Unidades) ---
# Lista com 92 lojas, incluindo bairro, cidade, UF e região.
lojas_info = [
    {'bairro': 'Liberdade', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Copacabana', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Savassi', 'cidade': 'Belo Horizonte', 'uf': 'MG', 'regiao': 'Sudeste'},
    {'bairro': 'Boa Viagem', 'cidade': 'Recife', 'uf': 'PE', 'regiao': 'Nordeste'},
    {'bairro': 'Moinhos de Vento', 'cidade': 'Porto Alegre', 'uf': 'RS', 'regiao': 'Sul'},
    {'bairro': 'Asa Sul', 'cidade': 'Brasília', 'uf': 'DF', 'regiao': 'Centro-Oeste'},
    {'bairro': 'Batel', 'cidade': 'Curitiba', 'uf': 'PR', 'regiao': 'Sul'},
    {'bairro': 'Graça', 'cidade': 'Salvador', 'uf': 'BA', 'regiao': 'Nordeste'},
    {'bairro': 'Aldeota', 'cidade': 'Fortaleza', 'uf': 'CE', 'regiao': 'Nordeste'},
    {'bairro': 'Adrianópolis', 'cidade': 'Manaus', 'uf': 'AM', 'regiao': 'Norte'},
    {'bairro': 'Tijuca', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Pinheiros', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Lourdes', 'cidade': 'Belo Horizonte', 'uf': 'MG', 'regiao': 'Sudeste'},
    {'bairro': 'Setor Marista', 'cidade': 'Goiânia', 'uf': 'GO', 'regiao': 'Centro-Oeste'},
    {'bairro': 'Ponta Verde', 'cidade': 'Maceió', 'uf': 'AL', 'regiao': 'Nordeste'},
    {'bairro': 'Cabral', 'cidade': 'Curitiba', 'uf': 'PR', 'regiao': 'Sul'},
    {'bairro': 'Jardins', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Leblon', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Beira Mar', 'cidade': 'Florianópolis', 'uf': 'SC', 'regiao': 'Sul'},
    {'bairro': 'Nazaré', 'cidade': 'Belém', 'uf': 'PA', 'regiao': 'Norte'},
    {'bairro': 'Moema', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Ipanema', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Funcionários', 'cidade': 'Belo Horizonte', 'uf': 'MG', 'regiao': 'Sudeste'},
    {'bairro': 'Casa Forte', 'cidade': 'Recife', 'uf': 'PE', 'regiao': 'Nordeste'},
    {'bairro': 'Auxiliadora', 'cidade': 'Porto Alegre', 'uf': 'RS', 'regiao': 'Sul'},
    {'bairro': 'Asa Norte', 'cidade': 'Brasília', 'uf': 'DF', 'regiao': 'Centro-Oeste'},
    {'bairro': 'Água Verde', 'cidade': 'Curitiba', 'uf': 'PR', 'regiao': 'Sul'},
    {'bairro': 'Rio Vermelho', 'cidade': 'Salvador', 'uf': 'BA', 'regiao': 'Nordeste'},
    {'bairro': 'Meireles', 'cidade': 'Fortaleza', 'uf': 'CE', 'regiao': 'Nordeste'},
    {'bairro': 'Ponta Negra', 'cidade': 'Manaus', 'uf': 'AM', 'regiao': 'Norte'},
    {'bairro': 'Vila Madalena', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Barra da Tijuca', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Pampulha', 'cidade': 'Belo Horizonte', 'uf': 'MG', 'regiao': 'Sudeste'},
    {'bairro': 'Sete de Setembro', 'cidade': 'Blumenau', 'uf': 'SC', 'regiao': 'Sul'},
    {'bairro': 'Jardim Goiás', 'cidade': 'Goiânia', 'uf': 'GO', 'regiao': 'Centro-Oeste'},
    {'bairro': 'Marco Zero', 'cidade': 'Macapá', 'uf': 'AP', 'regiao': 'Norte'},
    {'bairro': 'Centro', 'cidade': 'Vitória', 'uf': 'ES', 'regiao': 'Sudeste'},
    {'bairro': 'Plano Diretor Sul', 'cidade': 'Palmas', 'uf': 'TO', 'regiao': 'Norte'},
    {'bairro': 'Tirol', 'cidade': 'Natal', 'uf': 'RN', 'regiao': 'Nordeste'},
    {'bairro': 'Jatiúca', 'cidade': 'Maceió', 'uf': 'AL', 'regiao': 'Nordeste'},
    {'bairro': 'Ilha do Leite', 'cidade': 'Recife', 'uf': 'PE', 'regiao': 'Nordeste'},
    {'bairro': 'Teresópolis', 'cidade': 'Porto Alegre', 'uf': 'RS', 'regiao': 'Sul'},
    {'bairro': 'Sudoeste', 'cidade': 'Brasília', 'uf': 'DF', 'regiao': 'Centro-Oeste'},
    {'bairro': 'Mercês', 'cidade': 'Curitiba', 'uf': 'PR', 'regiao': 'Sul'},
    {'bairro': 'Pituba', 'cidade': 'Salvador', 'uf': 'BA', 'regiao': 'Nordeste'},
    {'bairro': 'Cocó', 'cidade': 'Fortaleza', 'uf': 'CE', 'regiao': 'Nordeste'},
    {'bairro': 'Vieiralves', 'cidade': 'Manaus', 'uf': 'AM', 'regiao': 'Norte'},
    {'bairro': 'Itaim Bibi', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Botafogo', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Anchieta', 'cidade': 'Belo Horizonte', 'uf': 'MG', 'regiao': 'Sudeste'},
    {'bairro': 'Caminho das Árvores', 'cidade': 'Salvador', 'uf': 'BA', 'regiao': 'Nordeste'},
    {'bairro': 'Jardim Botânico', 'cidade': 'Curitiba', 'uf': 'PR', 'regiao': 'Sul'},
    {'bairro': 'Trindade', 'cidade': 'Florianópolis', 'uf': 'SC', 'regiao': 'Sul'},
    {'bairro': 'Umarizal', 'cidade': 'Belém', 'uf': 'PA', 'regiao': 'Norte'},
    {'bairro': 'Vila Olímpia', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Flamengo', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Gutierrez', 'cidade': 'Belo Horizonte', 'uf': 'MG', 'regiao': 'Sudeste'},
    {'bairro': 'Espinheiro', 'cidade': 'Recife', 'uf': 'PE', 'regiao': 'Nordeste'},
    {'bairro': 'Petrópolis', 'cidade': 'Porto Alegre', 'uf': 'RS', 'regiao': 'Sul'},
    {'bairro': 'Lago Sul', 'cidade': 'Brasília', 'uf': 'DF', 'regiao': 'Centro-Oeste'},
    {'bairro': 'Champagnat', 'cidade': 'Curitiba', 'uf': 'PR', 'regiao': 'Sul'},
    {'bairro': 'Ondina', 'cidade': 'Salvador', 'uf': 'BA', 'regiao': 'Nordeste'},
    {'bairro': 'Varjota', 'cidade': 'Fortaleza', 'uf': 'CE', 'regiao': 'Nordeste'},
    {'bairro': 'Parque 10', 'cidade': 'Manaus', 'uf': 'AM', 'regiao': 'Norte'},
    {'bairro': 'Perdizes', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Laranjeiras', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Cidade Jardim', 'cidade': 'Belo Horizonte', 'uf': 'MG', 'regiao': 'Sudeste'},
    {'bairro': 'Boa Vista', 'cidade': 'Recife', 'uf': 'PE', 'regiao': 'Nordeste'},
    {'bairro': 'Menino Deus', 'cidade': 'Porto Alegre', 'uf': 'RS', 'regiao': 'Sul'},
    {'bairro': 'Noroeste', 'cidade': 'Brasília', 'uf': 'DF', 'regiao': 'Centro-Oeste'},
    {'bairro': 'Centro Cívico', 'cidade': 'Curitiba', 'uf': 'PR', 'regiao': 'Sul'},
    {'bairro': 'Barra', 'cidade': 'Salvador', 'uf': 'BA', 'regiao': 'Nordeste'},
    {'bairro': 'Praia de Iracema', 'cidade': 'Fortaleza', 'uf': 'CE', 'regiao': 'Nordeste'},
    {'bairro': 'Dom Pedro', 'cidade': 'Manaus', 'uf': 'AM', 'regiao': 'Norte'},
    {'bairro': 'Tatuapé', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Glória', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Santo Agostinho', 'cidade': 'Belo Horizonte', 'uf': 'MG', 'regiao': 'Sudeste'},
    {'bairro': 'Parnamirim', 'cidade': 'Recife', 'uf': 'PE', 'regiao': 'Nordeste'},
    {'bairro': 'Rio Branco', 'cidade': 'Porto Alegre', 'uf': 'RS', 'regiao': 'Sul'},
    {'bairro': 'Guará', 'cidade': 'Brasília', 'uf': 'DF', 'regiao': 'Centro-Oeste'},
    {'bairro': 'Rebouças', 'cidade': 'Curitiba', 'uf': 'PR', 'regiao': 'Sul'},
    {'bairro': 'Imbuí', 'cidade': 'Salvador', 'uf': 'BA', 'regiao': 'Nordeste'},
    {'bairro': 'Mucuripe', 'cidade': 'Fortaleza', 'uf': 'CE', 'regiao': 'Nordeste'},
    {'bairro': 'Flores', 'cidade': 'Manaus', 'uf': 'AM', 'regiao': 'Norte'},
    {'bairro': 'Mooca', 'cidade': 'São Paulo', 'uf': 'SP', 'regiao': 'Sudeste'},
    {'bairro': 'Catete', 'cidade': 'Rio de Janeiro', 'uf': 'RJ', 'regiao': 'Sudeste'},
    {'bairro': 'Prado', 'cidade': 'Belo Horizonte', 'uf': 'MG', 'regiao': 'Sudeste'},
    {'bairro': 'Jaçanã', 'cidade': 'Recife', 'uf': 'PE', 'regiao': 'Nordeste'},
    {'bairro': 'Cristo Redentor', 'cidade': 'Porto Alegre', 'uf': 'RS', 'regiao': 'Sul'},
    {'bairro': 'Taguatinga', 'cidade': 'Brasília', 'uf': 'DF', 'regiao': 'Centro-Oeste'},
    {'bairro': 'Juvevê', 'cidade': 'Curitiba', 'uf': 'PR', 'regiao': 'Sul'},
    {'bairro': 'Stiep', 'cidade': 'Salvador', 'uf': 'BA', 'regiao': 'Nordeste'}
]

# Distribuição de formatos: 14 Hiper, 34 Super, 44 Bairro
formatos = ['Hiper'] * 14 + ['Super'] * 34 + ['Bairro'] * 44
np.random.shuffle(formatos) # Embaralha os formatos para distribuição aleatória

lojas_df = pd.DataFrame(lojas_info)
lojas_df['Formato'] = formatos

# --- 2. Criação das Colunas Adicionais para as Lojas ---

# Área da unidade baseada no formato
area_map = {'Hiper': (3500, 6000), 'Super': (1500, 3000), 'Bairro': (400, 1200)}
lojas_df['Area da unidade em m²'] = lojas_df['Formato'].apply(lambda f: np.random.randint(area_map[f][0], area_map[f][1]))

# Nome da loja e sigla
lojas_df['Nome'] = lojas_df['Formato'] + ' ' + lojas_df['bairro']
lojas_df['Sigla'] = lojas_df['bairro'].apply(lambda n: n[:3].upper())
lojas_df['Unidade'] = lojas_df['Sigla'] + ' - ' + lojas_df['Nome']

# Consumo base por formato e fator de sazonalidade por região
consumo_base_map = {'Hiper': 5000, 'Super': 2200, 'Bairro': 800}
sazonalidade_map = {'Norte': 0.15, 'Nordeste': 0.20, 'Centro-Oeste': 0.30, 'Sudeste': 0.35, 'Sul': 0.40}

lojas_df['consumo_base'] = lojas_df['Formato'].map(consumo_base_map)
lojas_df['fator_sazonalidade'] = lojas_df['regiao'].map(sazonalidade_map)

# --- 3. Geração da Série Temporal ---
# Datas diárias para os últimos 3 anos
hoje = datetime.date.today()
data_final = hoje - datetime.timedelta(days=1)
data_inicial = data_final - datetime.timedelta(days=3*365 -1)
datas = pd.to_datetime(pd.date_range(start=data_inicial, end=data_final, freq='D'))

# --- 4. Combinação de Lojas e Datas e Cálculo do Consumo ---
# Cria um DataFrame com todas as combinações de lojas e datas
df_final = pd.DataFrame(pd.MultiIndex.from_product([lojas_df['Unidade'], datas], names=['Unidade', 'Data']).to_frame(index=False))

# Junta as informações das lojas
df_final = pd.merge(df_final, lojas_df, on='Unidade')

# Cálculo do consumo com sazonalidade e aleatoriedade
# A função -cos(x) modela o padrão: alto no início/fim do ano e baixo no meio
dia_do_ano = df_final['Data'].dt.dayofyear
fator_sazonal = -np.cos(2 * np.pi * dia_do_ano / 365) # Onda cosenoidal invertida

# O consumo é a base * (1 + variação_sazonal + ruído_aleatório)
variacao_sazonal = df_final['fator_sazonalidade'] * fator_sazonal
ruido_aleatorio = np.random.uniform(-0.05, 0.05, size=len(df_final)) # Pequena variação diária

df_final['Consumo kWh'] = df_final['consumo_base'] * (1 + variacao_sazonal + ruido_aleatorio)
df_final['Consumo kWh'] = df_final['Consumo kWh'].round(2)

# --- 5. Finalização e Exportação ---
# Organiza e seleciona as colunas finais
colunas_finais = [
    'Unidade', 'Area da unidade em m²', 'Data', 'Consumo kWh',
    'Formato', 'cidade', 'uf', 'regiao'
]
df_final = df_final[colunas_finais]

# Pega o caminho absoluto do diretório onde o script está
diretorio_do_script = os.path.dirname(os.path.abspath(__file__))

# Exporta para CSV
nome_do_arquivo = 'consumo_energia_marco.csv'

# Junta o caminho do diretório com o nome do arquivo para ter um caminho completo
caminho_completo = os.path.join(diretorio_do_script, nome_do_arquivo)

df_final.to_csv(caminho_completo, index=False, date_format='%Y-%m-%d')

print(f"Dataset gerado com sucesso! Salvo em: {caminho_completo}")
print("\nPré-visualização do dataset:")
print(df_final.head())