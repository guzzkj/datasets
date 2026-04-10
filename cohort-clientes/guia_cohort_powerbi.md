# Guia Analítico de Cohort SaaS — Power BI
> Arquitetura, DAX e Insights de Negócio

---

## 1. Esquema Estrela — Modelagem de Dados

```
                    ┌──────────────────────┐
                    │     dim_calendario   │
                    │─────────────────────│
                    │ PK data             │
                    │    ano              │
                    │    mes             │
                    │    trimestre        │
                    │    mes_ano (texto)  │
                    └──────────┬──────────┘
                               │ (1:N) data_pagamento
                               │
┌──────────────────┐    ┌──────▼───────────────────┐
│   dim_clientes   │    │  fato_pagamentos_saas     │
│─────────────────│    │──────────────────────────│
│ PK id_cliente   │◄───│ FK id_cliente             │
│    nome_cliente  │    │ FK data_pagamento         │
│    segmento      │    │    id_pagamento (PK)      │
│    plano         │    │    mes_vida               │
│    valor_mens.   │    │    valor_pago             │
│    data_aquisicao│    │    plano                  │
│    data_churn    │    │    status_pgto            │
│    status_cliente│    │    mes_referencia         │
│    canal_aquis.  │    └──────────────────────────┘
│    cidade/estado │
└──────────────────┘
```

**Relacionamentos:**
| De | Para | Cardinalidade | Direção do Filtro |
|---|---|---|---|
| `dim_clientes[id_cliente]` | `fato_pagamentos_saas[id_cliente]` | 1 : N | Única (dim >> fato) |
| `dim_calendario[data]` | `fato_pagamentos_saas[data_pagamento]` | 1 : N | Única (dim >> fato) |

> **Passo:** Criar `dim_calendario` via DAX com `CALENDARAUTO()` ou Power Query.

---

## 2. Fórmulas DAX — Análise de Cohort Avançada

### 2.1 Clientes Retidos por Mês de Vida (Cohort Retention)

```dax
Retidos por Mes de Vida =
VAR MesVidaSelecionado = SELECTEDVALUE(fato_pagamentos_saas[mes_vida])

-- Tabela virtual: clientes que chegaram ao mês de vida selecionado
VAR ClientesNoMes =
    CALCULATETABLE(
        VALUES(fato_pagamentos_saas[id_cliente]),
        fato_pagamentos_saas[mes_vida] = MesVidaSelecionado
    )

-- Clientes que também pagaram no mês 1 (cohorte de origem)
VAR ClientesNoMes1 =
    CALCULATETABLE(
        VALUES(fato_pagamentos_saas[id_cliente]),
        fato_pagamentos_saas[mes_vida] = 1
    )

-- Interseção: retidos desde o mês 1
VAR ClientesRetidos = INTERSECT(ClientesNoMes, ClientesNoMes1)

RETURN COUNTROWS(ClientesRetidos)
```

---

### 2.2 Taxa de Retenção por Cohort (Matriz de Cohort %)

```dax
Taxa de Retencao % =
VAR MesVida = SELECTEDVALUE(fato_pagamentos_saas[mes_vida])

VAR CoorteAquisicao =
    CALCULATETABLE(
        VALUES(fato_pagamentos_saas[id_cliente]),
        fato_pagamentos_saas[mes_vida] = 1,
        ALLEXCEPT(fato_pagamentos_saas, dim_clientes[data_aquisicao])
    )

VAR ClientesNoMesAtual =
    CALCULATETABLE(
        VALUES(fato_pagamentos_saas[id_cliente]),
        fato_pagamentos_saas[mes_vida] = MesVida,
        ALLEXCEPT(fato_pagamentos_saas, dim_clientes[data_aquisicao])
    )

VAR Retidos = INTERSECT(ClientesNoMesAtual, CoorteAquisicao)

VAR TotalCohorte = COUNTROWS(CoorteAquisicao)

RETURN
    IF(
        TotalCohorte = 0,
        BLANK(),
        DIVIDE(COUNTROWS(Retidos), TotalCohorte)
    )
```

> Exiba esta medida em uma **Matriz** com `data_aquisicao` (Mês-Ano) nas linhas e `mes_vida` nas colunas, formatando como porcentagem. Use formatação condicional por cor (verde >> vermelho).

---

### 2.3 Taxa de Churn Mensal

```dax
Taxa de Churn Mensal % =
VAR MesAtual = SELECTEDVALUE(dim_calendario[mes_referencia])

VAR ClientesAtivosInicio =
    CALCULATE(
        DISTINCTCOUNT(fato_pagamentos_saas[id_cliente]),
        DATESINPERIOD(
            dim_calendario[data],
            LASTDATE(dim_calendario[data]) - 30,
            -1,
            MONTH
        )
    )

VAR ClientesChurnNoMes =
    CALCULATE(
        COUNTROWS(dim_clientes),
        dim_clientes[status_cliente] = "Churn",
        MONTH(dim_clientes[data_churn]) = MONTH(LASTDATE(dim_calendario[data])),
        YEAR(dim_clientes[data_churn])  = YEAR(LASTDATE(dim_calendario[data]))
    )

RETURN
    DIVIDE(ClientesChurnNoMes, ClientesAtivosInicio, 0)
```

---

### 2.4 MRR — Receita Recorrente Mensal

```dax
MRR =
CALCULATE(
    SUMX(
        fato_pagamentos_saas,
        fato_pagamentos_saas[valor_pago]
    ),
    ALLEXCEPT(dim_calendario, dim_calendario[mes_referencia])
)
```

**Variações de MRR:**

```dax
-- MRR Novo: receita de clientes que pagaram pela 1ª vez no período
MRR Novo =
CALCULATE(
    [MRR],
    fato_pagamentos_saas[mes_vida] = 1
)

-- MRR Churn: receita perdida por evasão no período
MRR Churn (Perdido) =
VAR ClientesChurnMes =
    FILTER(
        dim_clientes,
        dim_clientes[status_cliente] = "Churn"
            && FORMAT(dim_clientes[data_churn], "YYYY-MM")
               = SELECTEDVALUE(dim_calendario[mes_referencia])
    )
RETURN
    SUMX(ClientesChurnMes, ClientesChurnMes[valor_mensalidade]) * -1
```

---

### 2.5 LTV — Lifetime Value por Cohort

```dax
LTV Medio por Cohort =
VAR ReceitaTotalCohorte =
    SUMX(
        fato_pagamentos_saas,
        fato_pagamentos_saas[valor_pago]
    )

VAR ClientesNaCohorte =
    CALCULATE(
        DISTINCTCOUNT(fato_pagamentos_saas[id_cliente]),
        fato_pagamentos_saas[mes_vida] = 1
    )

RETURN DIVIDE(ReceitaTotalCohorte, ClientesNaCohorte, 0)
```

---

## 3. Estrutura do Dashboard — Páginas Recomendadas

### Página 1 — Visão Executiva (MRR & Saúde da Base)
- **KPI Cards:** MRR Total | Clientes Ativos | Taxa de Churn Mensal | MRR Novo vs Churn
- **Gráfico de Área:** Evolução do MRR mês a mês com linha de MRR Churn
- **Segmentador:** Plano | Segmento | Canal de Aquisição

### Página 2 — Matriz de Cohort (Retenção)
- **Matriz Visual:** Linhas = Mês de Aquisição | Colunas = Mês de Vida (1–24)
- Medida: `Taxa de Retencao %`
- Formatação condicional: escala de cor verde (100%) >> vermelho (0%)
- **Gráfico de Linhas:** Curvas de retenção sobrepostas por cohort (ano ou trimestre)

### Página 3 — LTV & Análise de Safra
- **Gráfico de Barras:** LTV Médio por Cohort (safra de aquisição trimestral)
- **Scatter Plot:** LTV × Meses até Churn por Segmento
- **Tabela:** Top 20 clientes por receita acumulada

---

## 4. Insights Críticos de Negócio — O que este modelo revela

### Insight 1 — O "Mês do Penhasco" (Cliff Month)
> **Pergunta:** Em qual mês de vida a evasão é mais brutal?

Na maioria dos SaaS B2C/SMB, o maior volume de churn ocorre nos **meses 1 e 2**
(clientes que não ativaram o produto ou não perceberam valor). Identifique esse
ponto na matriz de cohort: é onde a retenção cai mais abruptamente entre colunas
consecutivas.

**Ação:** Investir em onboarding estruturado e ativação nos primeiros 30 dias reduz
o churn do mês 1 em até 40% (benchmark SaaS).

---

### Insight 2 — Comparação de LTV entre Safras (Vintage Analysis)
> **Pergunta:** Clientes adquiridos em qual período têm maior valor ao longo da vida?

Compare o `LTV Medio por Cohort` entre trimestres. Safras com LTV mais alto indicam
que campanhas de aquisição, canais ou melhorias de produto naquele período geraram
clientes de maior qualidade — ou que o produto evoluiu para resolver melhor a dor do cliente.

**Ação:** Realoque orçamento de marketing para os canais que geraram as safras
com melhor LTV, não apenas as com maior volume de leads.

---

### Insight 3 — Churn de Receita vs. Churn de Clientes (Revenue Churn)
> **Pergunta:** A empresa está perdendo clientes ou receita proporcionalmente maior?

Um SaaS saudável tem **Revenue Churn < Customer Churn**. Se clientes de planos
menores cancelam mais (Starter), mas os de Enterprise retêm bem, o MRR pode crescer
mesmo com alto churn em número de clientes. Analise `MRR Churn (Perdido)` segmentado
por Plano para identificar onde está a "sangria" real de receita.

**Ação:** Estratégias de expansão de receita (upsell/cross-sell) em clientes Starter
retidos por 3+ meses podem transformar o cohort de menor LTV em contribuidores relevantes.

---

## 5. Checklist de Implementação no Power BI

- [ ] Importar `dim_clientes.csv` e `fato_pagamentos_saas.csv`
- [ ] Criar `dim_calendario` via DAX: `dim_calendario = CALENDARAUTO()`
- [ ] Adicionar colunas calculadas em `dim_calendario`: Ano, Mês, Trimestre, MêsAno
- [ ] Configurar os 2 relacionamentos (ver Seção 1)
- [ ] Verificar que as datas estão no tipo correto (Date, não Text)
- [ ] Criar as medidas DAX em uma tabela de medidas dedicada (`_Medidas`)
- [ ] Configurar a Matriz de Cohort com formatação condicional
- [ ] Publicar no Power BI Service e agendar atualização

---

*Gerado automaticamente por `gerar_dataset_saas.py` — Dataset SaaS Sintético*
