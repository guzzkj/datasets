"""
Gerador de Dataset Sintético de SaaS - Análise de Cohort
=========================================================
Engenharia de Dados | Power BI Analytics
Gera: dim_clientes.csv, fato_pagamentos_saas.csv, guia_cohort_powerbi.md
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, timedelta
import random
import os

# ---------------------------------------------------------------------------
# Configurações globais
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

fake = Faker("pt_BR")
Faker.seed(SEED)

N_CLIENTES      = 5_000
MESES_HISTORICO = 24          # janela de dados
DATA_FIM        = date(2026, 3, 31)
DATA_INICIO     = DATA_FIM - timedelta(days=MESES_HISTORICO * 30)

PLANOS = {
    "Starter":      49.90,
    "Professional": 149.90,
    "Business":     399.90,
    "Enterprise":   999.90,
}

SEGMENTOS = ["B2B", "B2C", "SMB", "Mid-Market", "Enterprise"]

# ---------------------------------------------------------------------------
# Curva de sobrevivência realista por mês de vida
# Baseada em benchmarks SaaS: alta evasão nos meses 1-2, estabilização depois
# ---------------------------------------------------------------------------
def prob_churn_no_mes(mes_vida: int) -> float:
    """Retorna a probabilidade de churn ocorrer EXATAMENTE no mês `mes_vida`."""
    # Modelo: distribuição de Weibull invertida + cauda longa
    # Mês 1: ~22%, Mês 2: ~14%, Mês 3: ~9%, decrescendo até ~2% no mês 12+
    if mes_vida == 1:
        return 0.22
    elif mes_vida == 2:
        return 0.14
    elif mes_vida == 3:
        return 0.09
    elif mes_vida == 4:
        return 0.07
    elif mes_vida == 5:
        return 0.055
    elif mes_vida <= 8:
        return 0.04
    elif mes_vida <= 12:
        return 0.03
    elif mes_vida <= 18:
        return 0.025
    else:
        return 0.02


def sortear_mes_churn(meses_disponiveis: int) -> int | None:
    """
    Simula o mês de vida em que o cliente deu churn.
    Retorna None se o cliente sobreviveu a todos os meses.
    """
    for mes in range(1, meses_disponiveis + 1):
        if random.random() < prob_churn_no_mes(mes):
            return mes
    return None  # cliente ativo


# ---------------------------------------------------------------------------
# 1. Geração de dim_clientes
# ---------------------------------------------------------------------------
print("Gerando dim_clientes...")

registros_clientes = []

for i in range(1, N_CLIENTES + 1):
    # Data de aquisição: distribuição uniforme nos últimos 24 meses
    dias_offset = random.randint(0, MESES_HISTORICO * 30)
    data_aquisicao = DATA_INICIO + timedelta(days=dias_offset)

    plano = random.choices(
        list(PLANOS.keys()),
        weights=[0.35, 0.30, 0.25, 0.10],  # Starter mais comum
        k=1,
    )[0]

    segmento = random.choices(
        SEGMENTOS,
        weights=[0.25, 0.30, 0.25, 0.15, 0.05],
        k=1,
    )[0]

    # Quantos meses o cliente poderia ter vivido até DATA_FIM?
    meses_desde_aquisicao = max(
        1,
        (DATA_FIM.year - data_aquisicao.year) * 12
        + (DATA_FIM.month - data_aquisicao.month),
    )

    mes_churn = sortear_mes_churn(meses_desde_aquisicao)
    status = "Churn" if mes_churn is not None else "Ativo"

    if mes_churn:
        # Mês de vida >> data real do churn
        data_churn = date(
            data_aquisicao.year + (data_aquisicao.month - 1 + mes_churn - 1) // 12,
            (data_aquisicao.month - 1 + mes_churn - 1) % 12 + 1,
            min(data_aquisicao.day, 28),
        )
    else:
        data_churn = None

    registros_clientes.append(
        {
            "id_cliente":        f"CLI-{i:05d}",
            "nome_cliente":      fake.company(),
            "segmento":          segmento,
            "plano":             plano,
            "valor_mensalidade": PLANOS[plano],
            "data_aquisicao":    data_aquisicao,
            "data_churn":        data_churn,
            "status_cliente":    status,
            "cidade":            fake.city(),
            "estado":            fake.state_abbr(),
            "canal_aquisicao":   random.choice(
                ["Orgânico", "Pago", "Referência", "Parceiro", "Evento"]
            ),
        }
    )

dim_clientes = pd.DataFrame(registros_clientes)
print(f"  >> {len(dim_clientes)} clientes | Churn: {(dim_clientes.status_cliente=='Churn').sum()} | Ativos: {(dim_clientes.status_cliente=='Ativo').sum()}")


# ---------------------------------------------------------------------------
# 2. Geração de fato_pagamentos_saas
# ---------------------------------------------------------------------------
print("Gerando fato_pagamentos_saas...")

registros_pagamentos = []

for _, cliente in dim_clientes.iterrows():
    data_aquisicao = cliente["data_aquisicao"]
    data_churn     = cliente["data_churn"]
    valor_base     = cliente["valor_mensalidade"]

    # Define até quando o cliente pagou
    if data_churn:
        data_ultima = data_churn
    else:
        data_ultima = DATA_FIM

    # Gera um pagamento por mês de vida
    mes_corrente = date(data_aquisicao.year, data_aquisicao.month, 1)
    mes_vida = 0

    while mes_corrente <= date(data_ultima.year, data_ultima.month, 1):
        mes_vida += 1

        # Pequena variação no valor (desconto eventual, promoção)
        fator = random.gauss(1.0, 0.02)  # ±2% de ruído
        fator = max(0.90, min(1.10, fator))
        valor_pago = round(valor_base * fator, 2)

        # Dia de pagamento: próximo ao dia de aquisição (com leve variação)
        dia_pgto = min(
            data_aquisicao.day + random.randint(-2, 2),
            28,  # evita problemas com fevereiro
        )
        dia_pgto = max(1, dia_pgto)

        data_pagamento = date(mes_corrente.year, mes_corrente.month, dia_pgto)

        registros_pagamentos.append(
            {
                "id_pagamento":   f"PAG-{len(registros_pagamentos)+1:08d}",
                "id_cliente":     cliente["id_cliente"],
                "data_pagamento": data_pagamento,
                "mes_vida":       mes_vida,
                "valor_pago":     valor_pago,
                "plano":          cliente["plano"],
                "status_pgto":    "Pago",
                "mes_referencia": mes_corrente.strftime("%Y-%m"),
            }
        )

        # Avança um mês
        if mes_corrente.month == 12:
            mes_corrente = date(mes_corrente.year + 1, 1, 1)
        else:
            mes_corrente = date(mes_corrente.year, mes_corrente.month + 1, 1)

fato_pagamentos = pd.DataFrame(registros_pagamentos)
print(f"  >> {len(fato_pagamentos):,} registros de pagamento")


# ---------------------------------------------------------------------------
# 3. Exportação dos CSVs
# ---------------------------------------------------------------------------
output_dir = os.path.dirname(os.path.abspath(__file__))

dim_clientes.to_csv(os.path.join(output_dir, "dim_clientes.csv"), index=False, encoding="utf-8-sig")
fato_pagamentos.to_csv(os.path.join(output_dir, "fato_pagamentos_saas.csv"), index=False, encoding="utf-8-sig")

print(f"\nArquivos exportados em: {output_dir}")
print("  [OK] dim_clientes.csv")
print("  [OK] fato_pagamentos_saas.csv")


# ---------------------------------------------------------------------------
# 4. Geração do guia_cohort_powerbi.md
# ---------------------------------------------------------------------------
print("\nGerando guia_cohort_powerbi.md...")

guia = r"""# Guia Analítico de Cohort SaaS — Power BI
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
"""

guia_path = os.path.join(output_dir, "guia_cohort_powerbi.md")
with open(guia_path, "w", encoding="utf-8") as f:
    f.write(guia)

print("  [OK] guia_cohort_powerbi.md")

# ---------------------------------------------------------------------------
# 5. Sumário Final
# ---------------------------------------------------------------------------
print("\n" + "="*60)
print("RESUMO DO DATASET GERADO")
print("="*60)
print(f"Clientes totais          : {len(dim_clientes):,}")
print(f"  >> Ativos               : {(dim_clientes.status_cliente=='Ativo').sum():,}")
print(f"  >> Churn                : {(dim_clientes.status_cliente=='Churn').sum():,}")
print(f"Taxa de Churn geral      : {(dim_clientes.status_cliente=='Churn').mean()*100:.1f}%")
print(f"Registros de pagamento   : {len(fato_pagamentos):,}")
print(f"Receita total simulada   : R$ {fato_pagamentos.valor_pago.sum():,.2f}")
print(f"Período                  : {DATA_INICIO} >> {DATA_FIM}")
print("="*60)

# Distribuição por plano
print("\nDistribuição por Plano:")
dist_plano = dim_clientes.groupby("plano").agg(
    clientes=("id_cliente","count"),
    churn_pct=("status_cliente", lambda x: (x=="Churn").mean()*100)
).reset_index()
print(dist_plano.to_string(index=False))
