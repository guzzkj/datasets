"""
Script de Extração de Dados Financeiros para Power BI
======================================================
Autor  : Engenheiro de Dados Python
Gerado : 2026-04-10

Dependências:
    pip install yfinance python-bcb pandas

Saídas:
    cotacoes_b3.csv      – Cotações diárias dos ativos e do Ibovespa
    taxa_selic.csv       – Histórico diário da taxa Selic (BCB)
    guia_acoes_powerbi.md – Guia de modelagem para Power BI
"""

import sys
import io
import textwrap
from pathlib import Path
from datetime import date, timedelta

# Garante UTF-8 no terminal Windows (sem quebrar se já for UTF-8)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import pandas as pd
import yfinance as yf

# ── python-bcb é opcional; avisamos se não estiver instalado ─────────────────
try:
    from bcb import sgs
    BCB_DISPONIVEL = True
except ImportError:
    BCB_DISPONIVEL = False
    print("[AVISO] python-bcb não encontrado. A taxa Selic será extraída via "
          "API pública do BCB sem essa biblioteca.")

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────────────────────────────────────
ATIVOS = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "WEGE3.SA", "ABEV3.SA"]
INDICE = "^BVSP"
DATA_FIM   = date.today()
DATA_INICIO = DATA_FIM - timedelta(days=3 * 365)

DIR_SAIDA = Path(__file__).parent
ARQUIVO_COTACOES = DIR_SAIDA / "cotacoes_b3.csv"
ARQUIVO_SELIC    = DIR_SAIDA / "taxa_selic.csv"
ARQUIVO_GUIA     = DIR_SAIDA / "guia_acoes_powerbi.md"

# ─────────────────────────────────────────────────────────────────────────────
# PARTE 1-A: COTAÇÕES (yfinance)
# ─────────────────────────────────────────────────────────────────────────────

def extrair_cotacoes() -> pd.DataFrame:
    """Extrai preços de fechamento ajustado para os ativos e o Ibovespa."""
    tickers = ATIVOS + [INDICE]
    print(f"\n[1/4] Baixando cotações de {len(tickers)} tickers "
          f"({DATA_INICIO} → {DATA_FIM})…")

    raw: pd.DataFrame = yf.download(
        tickers=tickers,
        start=DATA_INICIO.isoformat(),
        end=DATA_FIM.isoformat(),
        auto_adjust=True,
        progress=True,
    )

    # yfinance retorna MultiIndex quando múltiplos tickers são passados
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"].copy()
    else:
        close = raw[["Close"]].copy()
        close.columns = [tickers[0]]

    # Limpar nulos: remove linhas onde TODOS os tickers são NaN;
    # preenche lacunas internas com forward-fill (feriados locais)
    close = close.dropna(how="all").ffill()

    # Transforma para formato longo (tidy)
    df = (
        close
        .reset_index()
        .rename(columns={"Date": "data", "index": "data"})
        .melt(id_vars="data", var_name="ticker", value_name="preco_fechamento")
    )

    # Garante tipos corretos
    df["data"] = pd.to_datetime(df["data"]).dt.normalize()
    df["preco_fechamento"] = df["preco_fechamento"].astype(float).round(4)

    # Remove linhas ainda nulas depois do ffill (início de série mais curta)
    df = df.dropna(subset=["preco_fechamento"])

    # Ordena e reseta índice
    df = df.sort_values(["ticker", "data"]).reset_index(drop=True)

    # Variação percentual diária por ticker
    df["retorno_diario_pct"] = (
        df
        .groupby("ticker")["preco_fechamento"]
        .pct_change()
        .round(6)
    )

    # Coluna auxiliar: tipo de ativo
    df["tipo"] = df["ticker"].apply(
        lambda t: "Índice" if t == INDICE else "Ação"
    )

    print(f"   >> {len(df):,} linhas geradas.")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# PARTE 1-B: TAXA SELIC (BCB – Série 11 = Selic diária)
# ─────────────────────────────────────────────────────────────────────────────

def extrair_selic_via_bcb_lib() -> pd.DataFrame:
    """Usa python-bcb (SGS série 11 = Selic diária)."""
    print("\n[2/4] Baixando Selic via python-bcb…")
    df = sgs.get({"selic_diaria": 11}, start=DATA_INICIO.isoformat())
    df = df.reset_index().rename(columns={"Date": "data", "index": "data"})
    df["data"] = pd.to_datetime(df["data"]).dt.normalize()
    df["selic_diaria_pct"] = df["selic_diaria"].astype(float).round(6)
    df = df[["data", "selic_diaria_pct"]].dropna()
    return df


def extrair_selic_via_api() -> pd.DataFrame:
    """Fallback: API pública do BCB sem dependência extra."""
    import urllib.request, json

    print("\n[2/4] Baixando Selic via API pública do BCB (fallback)…")
    inicio_str = DATA_INICIO.strftime("%d/%m/%Y")
    fim_str    = DATA_FIM.strftime("%d/%m/%Y")
    url = (
        "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
        f"?formato=json&dataInicial={inicio_str}&dataFinal={fim_str}"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        dados = json.loads(resp.read().decode())

    df = pd.DataFrame(dados)
    df["data"] = pd.to_datetime(df["data"], dayfirst=True).dt.normalize()
    df["selic_diaria_pct"] = pd.to_numeric(df["valor"], errors="coerce").round(6)
    df = df[["data", "selic_diaria_pct"]].dropna()
    print(f"   >> {len(df):,} observacoes da Selic.")
    return df


def extrair_selic() -> pd.DataFrame:
    if BCB_DISPONIVEL:
        return extrair_selic_via_bcb_lib()
    return extrair_selic_via_api()


# ─────────────────────────────────────────────────────────────────────────────
# PARTE 1-C: EXPORTAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def exportar(df_cotacoes: pd.DataFrame, df_selic: pd.DataFrame) -> None:
    print("\n[3/4] Exportando CSVs…")

    df_cotacoes.to_csv(ARQUIVO_COTACOES, index=False, sep=",", encoding="utf-8-sig")
    print(f"   OK {ARQUIVO_COTACOES.name}  ({len(df_cotacoes):,} linhas)")

    df_selic.to_csv(ARQUIVO_SELIC, index=False, sep=",", encoding="utf-8-sig")
    print(f"   OK {ARQUIVO_SELIC.name}  ({len(df_selic):,} linhas)")


# ─────────────────────────────────────────────────────────────────────────────
# PARTE 2: GERAÇÃO DO GUIA MARKDOWN
# ─────────────────────────────────────────────────────────────────────────────

GUIA_MD = textwrap.dedent("""\
# Guia de Modelagem Power BI – Monitor de Carteira B3

> Gerado automaticamente pelo script `extrair_dados.py`.
> Última execução: {data_geracao}

---

## 1. Esquema Estrela

O modelo segue o padrão **Star Schema**, com uma tabela fato central e
dimensões ao redor.

```
                     ┌─────────────────────┐
                     │   dCalendario (Dim)  │
                     │─────────────────────│
                     │ PK  data            │
                     │     ano             │
                     │     mes             │
                     │     trimestre       │
                     │     nome_mes        │
                     │     dia_semana      │
                     │     flag_fim_semana  │
                     └──────────┬──────────┘
                                │ 1
                                │
            ┌───────────────────┼──────────────────────┐
            │                   │                      │
           N│                  N│                     N│
  ┌─────────┴──────────┐  ┌────┴───────────┐  ┌───────┴──────────┐
  │  fCotacoes (Fato)  │  │  fSelic (Fato) │  │  dAtivo (Dim)    │
  │────────────────────│  │────────────────│  │──────────────────│
  │ FK  data           │  │ FK  data       │  │ PK  ticker       │
  │ FK  ticker         │  │     selic_%    │  │     nome_completo│
  │     preco_fecham.  │  └────────────────┘  │     setor        │
  │     retorno_%      │                      │     tipo         │
  │     tipo           │                      └──────────────────┘
  └────────────────────┘
```

### Relacionamentos no Power BI
| De (Muitos)               | Para (Um)           | Cardinalidade | Direção Filtro |
|---------------------------|---------------------|---------------|----------------|
| fCotacoes[data]           | dCalendario[data]   | N:1           | Único →        |
| fSelic[data]              | dCalendario[data]   | N:1           | Único →        |
| fCotacoes[ticker]         | dAtivo[ticker]      | N:1           | Único →        |

> **Dica:** Crie a `dCalendario` com a função DAX `CALENDARAUTO()` ou via
> script Power Query para garantir continuidade de datas.

---

## 2. Tabela Calendário (Power Query M)

Cole o código abaixo em uma nova consulta em branco no Power Query:

```m
let
    DataInicio  = #date(2021, 1, 1),
    DataFim     = Date.From(DateTime.LocalNow()),
    TotalDias   = Duration.Days(DataFim - DataInicio) + 1,
    ListaDatas  = List.Dates(DataInicio, TotalDias, #duration(1,0,0,0)),
    Tabela      = Table.FromList(ListaDatas, Splitter.SplitByNothing(),
                    {"data"}, null, ExtraValues.Error),
    TipoData    = Table.TransformColumnTypes(Tabela, {{"data", type date}}),
    Ano         = Table.AddColumn(TipoData,   "ano",         each Date.Year([data]),  Int64.Type),
    Mes         = Table.AddColumn(Ano,        "mes",         each Date.Month([data]), Int64.Type),
    Trimestre   = Table.AddColumn(Mes,        "trimestre",   each "T" & Text.From(Date.QuarterOfYear([data])), type text),
    NomeMes     = Table.AddColumn(Trimestre,  "nome_mes",    each Date.MonthName([data], "pt-BR"), type text),
    DiaSemana   = Table.AddColumn(NomeMes,    "dia_semana",  each Date.DayOfWeekName([data], "pt-BR"), type text),
    FimSemana   = Table.AddColumn(DiaSemana,  "flag_fim_semana",
                    each if Date.DayOfWeek([data], Day.Monday) >= 5 then 1 else 0, Int64.Type)
in
    FimSemana
```

---

## 3. Fórmulas DAX

### 3.1 Retorno Acumulado no Ano (YTD)

```dax
Retorno YTD =
VAR PrimeiroPrecoAno =
    CALCULATE(
        FIRSTNONBLANK(fCotacoes[preco_fechamento], 1),
        DATESYTD(dCalendario[data])
    )
VAR UltimoPreco =
    LASTNONBLANK(fCotacoes[preco_fechamento], 1)
RETURN
    DIVIDE(UltimoPreco - PrimeiroPrecoAno, PrimeiroPrecoAno)
```

> Formate como **Porcentagem** com 2 casas decimais.
> Use em um cartão ou gráfico de barras por ticker para comparar rentabilidade no ano.

---

### 3.2 Drawdown (Queda Máxima em Relação ao Pico)

```dax
Drawdown =
VAR TabelaAcumulada =
    ADDCOLUMNS(
        CALCULATETABLE(
            VALUES(dCalendario[data]),
            ALLSELECTED(dCalendario[data])
        ),
        "@preco",
        CALCULATE(
            LASTNONBLANK(fCotacoes[preco_fechamento], 1),
            fCotacoes[data] <= MAX(dCalendario[data])
        )
    )
VAR PicoHistorico =
    MAXX(
        FILTER(TabelaAcumulada, [@preco] <> BLANK()),
        [@preco]
    )
VAR PrecoAtual =
    LASTNONBLANK(fCotacoes[preco_fechamento], 1)
RETURN
    DIVIDE(PrecoAtual - PicoHistorico, PicoHistorico)
```

> Valor negativo indica queda em relação ao pico.
> Formate como **Porcentagem**. Use em um gráfico de área com linha de referência em 0.

---

### 3.3 Volatilidade Anualizada (Desvio Padrão dos Retornos Diários × √252)

```dax
Volatilidade Anualizada =
VAR DesvioPadrao =
    CALCULATE(
        STDEV.P(fCotacoes[retorno_diario_pct]),
        ALLSELECTED(dCalendario[data])
    )
RETURN
    DesvioPadrao * SQRT(252)
```

> Representa o risco anualizado do ativo.
> Formate como **Porcentagem** com 2 casas. Use em um gráfico de barras para comparar risco entre ativos.

---

### 3.4 Medidas Auxiliares Úteis

```dax
-- Preço mais recente selecionado
Preço Atual =
    LASTNONBLANK(fCotacoes[preco_fechamento], 1)

-- Selic média do período selecionado (taxa anualizada simplificada)
Selic Média Período =
    AVERAGEX(
        CALCULATETABLE(fSelic, ALLSELECTED(dCalendario[data])),
        fSelic[selic_diaria_pct]
    ) * 252

-- Retorno vs Ibovespa (spread)
Alpha vs Ibovespa =
    VAR RetornoAtivo   = [Retorno YTD]
    VAR RetornoIbovespa =
        CALCULATE([Retorno YTD], fCotacoes[tipo] = "Índice")
    RETURN RetornoAtivo - RetornoIbovespa
```

---

## 4. Análises e Perguntas de Negócio para o Dashboard

### Análise 1 — Impacto da Selic no Drawdown da Carteira
**Pergunta:** *Nos períodos em que a Selic esteve acima de 12% a.a., o
drawdown médio dos ativos foi maior?*

- **Visual sugerido:** Gráfico de dispersão (Scatter Plot)
  - Eixo X: Selic Média Período (%)
  - Eixo Y: Drawdown (%)
  - Legenda/cor: Ticker
- **Por que importa:** Alta da Selic encarece crédito e comprime múltiplos;
  setores sensíveis a juros (bancos, utilities) tendem a sofrer mais.
- **Dado de suporte:** Filtre por períodos de alta (COPOM) usando a
  `dCalendario` com uma coluna `ciclo_selic` calculada.

---

### Análise 2 — Comparativo de Rentabilidade vs. Ibovespa (Alpha)
**Pergunta:** *Quais ativos geraram alpha positivo (superaram o Ibovespa)
no período selecionado?*

- **Visual sugerido:** Gráfico de barras horizontais com formatação
  condicional (verde = alpha positivo, vermelho = negativo)
  - Eixo Y: Ticker
  - Eixo X: `[Alpha vs Ibovespa]`
- **Por que importa:** Identifica ativos que de fato agregam valor à carteira
  acima do benchmark de mercado.
- **Segmentadores recomendados:** Período (Mês/Trimestre/Ano), Setor.

---

### Análise 3 — Fronteira Risco × Retorno
**Pergunta:** *Qual ativo oferece o melhor retorno ajustado ao risco
(maior retorno YTD por unidade de volatilidade)?*

- **Visual sugerido:** Gráfico de dispersão (Bubble Chart)
  - Eixo X: `[Volatilidade Anualizada]`
  - Eixo Y: `[Retorno YTD]`
  - Tamanho da bolha: Volume negociado (se disponível)
  - Legenda: Ticker
  - Linha de referência no eixo Y = Selic Média (custo de oportunidade)
- **Por que importa:** Visualiza o trade-off clássico risco/retorno.
  Ativos acima e à esquerda da linha da Selic são os mais eficientes.
- **Insight adicional:** Calcule o Índice de Sharpe simplificado:
  `([Retorno YTD] - [Selic Média Período]) / [Volatilidade Anualizada]`

---

## 5. Checklist de Importação no Power BI

- [ ] Importar `cotacoes_b3.csv` → renomear para `fCotacoes`
- [ ] Importar `taxa_selic.csv` → renomear para `fSelic`
- [ ] Criar consulta M da `dCalendario` (seção 2 acima)
- [ ] Criar tabela `dAtivo` manualmente (ticker, nome, setor) ou via CSV auxiliar
- [ ] Criar todos os relacionamentos (seção 1)
- [ ] Marcar `dCalendario` como **Tabela de Datas** (clique direito → Marcar como tabela de datas)
- [ ] Criar medidas DAX em uma tabela de medidas dedicada (`_Medidas`)
- [ ] Aplicar formatação condicional nos cartões de Drawdown (vermelho se < -10%)

---

*Fim do guia. Dúvidas? Revise os tipos de coluna no Power Query antes de
criar os relacionamentos — `data` deve ser `Date` e `ticker` deve ser `Text`.*
""")


def gerar_guia(data_geracao: str) -> None:
    print("\n[4/4] Gerando guia Markdown para Power BI...")
    conteudo = GUIA_MD.replace("{data_geracao}", data_geracao)
    ARQUIVO_GUIA.write_text(conteudo, encoding="utf-8")
    print(f"   OK {ARQUIVO_GUIA.name}")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Monitor de Carteira B3 – Extração de Dados")
    print("=" * 60)
    print(f"  Ativos   : {', '.join(ATIVOS)}")
    print(f"  Indice   : {INDICE}")
    print(f"  Periodo  : {DATA_INICIO} a {DATA_FIM}")
    print(f"  Saída    : {DIR_SAIDA.resolve()}")
    print("=" * 60)

    try:
        df_cotacoes = extrair_cotacoes()
        df_selic    = extrair_selic()
        exportar(df_cotacoes, df_selic)
        gerar_guia(data_geracao=date.today().strftime("%d/%m/%Y"))

        print("\n[OK] Processo concluído com sucesso!")
        print(f"     Arquivos gerados em: {DIR_SAIDA.resolve()}\n")

    except Exception as exc:
        print(f"\n[ERRO] {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
