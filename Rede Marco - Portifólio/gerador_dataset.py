import pandas as pd
import numpy as np
import datetime

print("Iniciando a geração do dataset de consumo de energia...")

# --- 1. Definição das Lojas (Unidades) ---
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

# Distribuição de formatos
formatos = ['Hiper'] * 14 + ['Super'] * 34 + ['Bairro'] * 44
np.random.shuffle(formatos)

lojas_df = pd.DataFrame(lojas_info)
lojas_df['Formato'] = formatos

# --- 2. Criação das Colunas Adicionais para as Lojas ---
area_map = {'Hiper': (3500, 6000), 'Super': (1500, 3000), 'Bairro': (400, 1200)}
lojas_df['Area da unidade em m²'] = lojas_df['Formato'].apply(lambda f: np.random.randint(area_map[f][0], area_map[f][1]))

lojas_df['Nome'] = lojas_df['Formato'] + ' ' + lojas_df['bairro']
lojas_df['Sigla'] = lojas_df['bairro'].apply(lambda n: n[:3].upper())
lojas_df['Unidade'] = lojas_df['Sigla'] + ' - ' + lojas_df['Nome']

# Formatação Geográfica para o Looker Studio
lojas_df['uf'] = 'BR-' + lojas_df['uf']
lojas_df['País'] = 'Brasil'


# Define uma eficiência base (consumo por m²) para cada formato
eficiencia_map = {'Hiper': 1.3, 'Super': 1.5, 'Bairro': 2.0} # Bairro é menos eficiente por m²
lojas_df['eficiencia_base'] = lojas_df['Formato'].map(eficiencia_map)

# Adiciona um fator aleatório para cada loja (de 85% a 115% da eficiência base)
fator_aleatorio_loja = np.random.uniform(0.85, 1.15, size=len(lojas_df))
lojas_df['consumo_base_individual'] = (lojas_df['eficiencia_base'] * lojas_df['Area da unidade em m²']) * fator_aleatorio_loja

sazonalidade_map = {'Norte': 0.15, 'Nordeste': 0.20, 'Centro-Oeste': 0.30, 'Sudeste': 0.35, 'Sul': 0.40}
lojas_df['fator_sazonalidade'] = lojas_df['regiao'].map(sazonalidade_map)

# --- 3. Geração da Série Temporal ---
# Usando datas fixas para garantir que os 3 anos completos sejam gerados
data_final = datetime.date(2025, 6, 30)
data_inicial = datetime.date(2022, 1, 1)
datas = pd.to_datetime(pd.date_range(start=data_inicial, end=data_final, freq='D'))

# --- 4. Combinação de Lojas e Datas e Cálculo do Consumo ---
df_final = pd.DataFrame(pd.MultiIndex.from_product([lojas_df['Unidade'], datas], names=['Unidade', 'Data']).to_frame(index=False))
df_final = pd.merge(df_final, lojas_df, on='Unidade')

dia_do_ano = df_final['Data'].dt.dayofyear
fator_sazonal = np.cos(2 * np.pi * dia_do_ano / 365)
variacao_sazonal = df_final['fator_sazonalidade'] * fator_sazonal

# NOVO: Fator de variação anual para simular crescimento/redução
ano_map = {
    2022: 1.0,         # Ano base
    2023: 1.15,        # Aumento de 15% no consumo
    2024: 1.08,        # Aumento de 8% em relação a 2022
    2025: 1.12         # Aumento de 25% em relação a 2022
}
df_final['fator_anual'] = df_final['Data'].dt.year.map(ano_map)

# Ruído aleatório diário (pequenas flutuações)
ruido_aleatorio = np.random.uniform(-0.05, 0.05, size=len(df_final))

df_final['Consumo kWh'] = df_final['consumo_base_individual'] * df_final['fator_anual'] * (1 + variacao_sazonal + ruido_aleatorio)
df_final['Consumo kWh'] = df_final['Consumo kWh'].round(2).clip(0) # .clip(0) garante que não haja consumo negativo

# --- 5. Finalização e Exportação ---
colunas_finais = [
    'Unidade', 'Nome', 'Area da unidade em m²', 'Data', 'Consumo kWh',
    'Formato', 'cidade', 'uf', 'regiao', 'País'
]
df_final = df_final[colunas_finais]

# Renomeando as colunas para o formato final desejado
df_final.rename(columns={
    'cidade': 'Cidade',
    'uf': 'UF',
    'regiao': 'Região'
}, inplace=True)

# Exporta para CSV
output_filename = 'consumo_energia_supermercados_v2.csv'
df_final.to_csv(output_filename, index=False, date_format='%Y-%m-%d')

print(f"Dataset gerado com sucesso! {len(df_final)} linhas foram salvas em '{output_filename}'.")
print("\nPré-visualização do dataset:")
print(df_final.head())