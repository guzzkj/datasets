# Análise Comparativa de Ativos Financeiros

![Status](./img/preview_dashboard.png)

## 📄 Resumo do Projeto

Este projeto apresenta uma solução completa de Business Intelligence para a análise de performance de ativos financeiros. O objetivo é comparar o desempenho histórico, o retorno e o risco (volatilidade) de um portfólio de ações selecionadas de diferentes mercados (B3 no Brasil e Nasdaq nos EUA).

A solução vai desde a coleta de dados históricos via API com Python até o desenvolvimento de um dashboard interativo e analiticamente robusto no Power BI, utilizando medidas DAX avançadas para permitir uma comparação justa e profunda entre os ativos.

## 📊 Dashboard Interativo

O resultado final do projeto é um dashboard interativo que permite a exploração da performance das ações sob diferentes períodos e seleções, fornecendo insights sobre retorno, risco e atividade de mercado.

**[Acesse o dashboard completo e interativo aqui](https:)**

## 🎯 O Problema de Negócio

Comparar a performance de ações de diferentes mercados apresenta desafios significativos, como moedas distintas (BRL vs. USD) e escalas de preço muito diferentes. Uma análise superficial baseada apenas nos preços absolutos pode levar a conclusões equivocadas sobre o crescimento real e o risco de cada ativo.

Este projeto buscou responder às seguintes questões:
* Como comparar de forma justa o crescimento percentual de ações com preços e moedas diferentes?
* Qual ativo ofereceu o melhor retorno no período selecionado?
* Qual ativo apresentou o maior risco (volatilidade) para o investidor?
* Existe uma correlação entre o volume de negociações e os movimentos de preço?

## ✨ Principais Funcionalidades

* **KPIs Dinâmicos:** Cartões de indicadores que exibem o retorno total, os preços máximo e mínimo, e identificam automaticamente os ativos de melhor e pior performance no período selecionado.

* **Análise de Performance Normalizada:** Um gráfico de linha que compara o crescimento de todos os ativos a partir de uma base comum (Base 100), permitindo uma visualização clara da performance relativa.

* **Análise de Risco (Volatilidade):** Um gráfico de barras que ranqueia os ativos pelo seu nível de risco, calculado através do desvio padrão dos retornos diários.

* **Análise de Volume:** Um gráfico de colunas que exibe o volume diário de negociação, fornecendo contexto sobre a força dos movimentos de mercado.

* **Filtros Interativos:** Segmentações de dados que permitem ao usuário final filtrar a análise por um intervalo de datas específico e selecionar as ações de interesse.

## 🛠️ Ferramentas e Tecnologias

* **Linguagem:** Python 3
* **Bibliotecas de Análise:** Pandas, yfinance
* **Ferramenta de BI:** Power BI
* **Linguagem de Fórmulas:** DAX (Data Analysis Expressions)
* **Controle de Versão:** Git & GitHub

## ⚙️ Metodologia
O projeto foi estruturado em três etapas principais:

1.  **Coleta e Preparação de Dados (coletar_dados_acoes.py):** Desenvolvimento de um script Python para se conectar à API do Yahoo Finance (via yfinance) e extrair 5 anos de dados históricos para 6 ações selecionadas. O script também realiza a formatação inicial dos dados, salvando-os em um arquivo CSV com o separador decimal correto (vírgula) para o Power BI.

2.  **Tratamento e Modelagem (Power Query):** No Power BI, os dados foram carregados no Power Query Editor para verificação dos tipos de dados e seleção das colunas relevantes para a análise, garantindo um modelo de dados limpo e performático.

3.  **Desenvolvimento do Dashboard (Power BI & DAX):** O dashboard foi construído utilizando visuais interativos. A lógica analítica foi implementada através de medidas DAX avançadas para calcular o Preço Indexado (Base 100), o Retorno no Período %, a Volatilidade (Desvio Padrão) e os KPIs de melhor/pior performance.

## 🚀 Como Executar o Projeto Localmente
Para executar o script de coleta de dados, siga os passos abaixo.

**Pré-requisitos:**
* Python 3.x
* pip (gerenciador de pacotes do Python)

```bash
# 1. Clone o repositório
git clone https://github.com/guzzkj/datasets.git

# 2. Navegue até o diretório do projeto
cd datasets/analise-ativos-financeiros

# 3. Instale as dependências necessárias
# (Recomendado: criar um ambiente virtual primeiro)
pip install pandas yfinance

# 4. Execute o script de coleta de dados
# Este script cria o arquivo 'dados_historicos_acoes.csv'
python coletar_dados_acoes.py
```

## 👨‍💻 Autor

Projeto desenvolvido por **Gustavo Henrique Barros da Silva**.

* **LinkedIn:** [https://www.linkedin.com/in/gustavohbarros/](https://www.linkedin.com/in/gustavohbarros/)
* **Email:** [gustavobarros.ctt@gmail.com](mailto:gustavobarros.ctt@gmail.com)