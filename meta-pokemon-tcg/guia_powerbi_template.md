# Guia de Modelagem e DAX — Pokémon TCG Dataset

Gerado automaticamente em: {generated_at}

---

## 1. Estrutura Recomendada: Esquema Estrela

O Esquema Estrela organiza os dados em uma **Tabela Fato** central e
**Tabelas Dimensão** ao redor, eliminando redundâncias e acelerando
consultas no Power BI.

### Tabela Fato: `Fato_Carta`

Contém as métricas numéricas e as chaves estrangeiras para as dimensões.

| Coluna               | Tipo       | Descrição                                  |
|----------------------|------------|--------------------------------------------|
| id_carta (PK/FK)     | Texto      | Chave natural da carta                     |
| id_expansao (FK)     | Texto      | Chave para Dim_Expansao                    |
| id_tipo (FK)         | Texto      | Chave para Dim_Tipo                        |
| id_supertipo (FK)    | Texto      | Chave para Dim_Supertipo                   |
| hp                   | Inteiro    | Pontos de vida da carta                    |
| custo_energia_total  | Inteiro    | Soma do custo de energia de todos ataques  |
| dano_maximo_ataque   | Inteiro    | Maior dano numérico entre os ataques       |

### Tabela Dimensão: `Dim_Carta`

| Coluna        | Tipo   | Descrição                         |
|---------------|--------|-----------------------------------|
| id_carta (PK) | Texto  | Chave primária                    |
| nome          | Texto  | Nome da carta                     |
| imagem_small  | Texto  | URL da imagem pequena             |
| imagem_large  | Texto  | URL da imagem grande              |

### Tabela Dimensão: `Dim_Expansao`

| Coluna           | Tipo  | Descrição                   |
|------------------|-------|-----------------------------|
| id_expansao (PK) | Texto | Chave primária              |
| nome_expansao    | Texto | Nome da expansão            |
| data_lancamento  | Data  | Data de lançamento          |

### Tabela Dimensão: `Dim_Tipo`

| Coluna     | Tipo  | Descrição          |
|------------|-------|--------------------|
| id_tipo    | Texto | Ex: "Fire", "Water"|
| nome_tipo  | Texto | Tipo de energia    |

### Tabela Dimensão: `Dim_Supertipo`

| Coluna         | Tipo  | Descrição                         |
|----------------|-------|-----------------------------------|
| id_supertipo   | Texto | Ex: "Pokémon", "Trainer", "Energy"|
| nome_supertipo | Texto | Categoria da carta                |

### Tabela de Datas: `Dim_Calendario`

Crie uma tabela de calendário contínua ligada a `Dim_Expansao[data_lancamento]`
para habilitar a inteligência de tempo do DAX.

```dax
Dim_Calendario =
CALENDAR(
    DATE(2000, 1, 1),
    TODAY()
)
```

---

## 2. Fórmulas DAX Prontas para Uso

### DAX 1 — Ranking de Custo-Benefício (Dano por Energia)

Identifica as cartas com maior relação dano/energia.
Cartas com custo 0 recebem um índice fixo para evitar divisão por zero.

```dax
Indice_Custo_Beneficio =
DIVIDE(
    Fato_Carta[dano_maximo_ataque],
    IF(
        Fato_Carta[custo_energia_total] = 0,
        1,
        Fato_Carta[custo_energia_total]
    ),
    0
)
```

**Como usar:** Adicione como coluna calculada em `Fato_Carta`.
Use em visuais de ranking (Top N por Índice_Custo_Beneficio).

---

### DAX 2 — Contagem do Meta (Cartas Mais Fortes)

Conta quantas cartas estão acima do limiar de HP e dano considerado "meta"
(ex: HP ≥ 200 e dano ≥ 200). Ajuste os thresholds conforme o contexto.

```dax
Qtd_Cartas_Meta =
CALCULATE(
    COUNTROWS(Fato_Carta),
    Fato_Carta[hp] >= 200,
    Fato_Carta[dano_maximo_ataque] >= 200
)
```

**Como usar:** Adicione como medida em `Fato_Carta`.
Exiba em um cartão (Card visual) no dashboard principal.
Combine com filtros de expansão para ver a evolução do meta.

---

### DAX 3 — Inteligência de Tempo: Cartas Lançadas nos Últimos 12 Meses

Compara a contagem de cartas do período selecionado
com os 12 meses anteriores, usando a data de lançamento da expansão.

```dax
Cartas_Ultimos_12_Meses =
CALCULATE(
    COUNTROWS(Fato_Carta),
    DATESINPERIOD(
        Dim_Calendario[Date],
        LASTDATE(Dim_Calendario[Date]),
        -12,
        MONTH
    )
)
```

**Como usar:** Adicione como medida em `Fato_Carta`.
Requer que `Dim_Calendario[Date]` esteja relacionado a
`Dim_Expansao[data_lancamento]`. Use em gráficos de linha para
visualizar o volume de cartas ao longo do tempo.

---

## 3. Dicas de Importação no Power BI

1. **Importe o CSV** via *Obter Dados → Texto/CSV*.
2. No *Editor do Power Query*, converta `data_lancamento` para o tipo **Data**.
3. Converta `hp`, `custo_energia_total` e `dano_maximo_ataque` para **Número Inteiro**.
4. Crie as dimensões usando *Referência* da tabela principal e removendo colunas desnecessárias.
5. Crie a `Dim_Calendario` com a fórmula DAX acima e marque-a como **Tabela de Datas**.
6. Estabeleça os relacionamentos no modelo antes de criar as medidas DAX.
