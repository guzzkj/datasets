"""
Pokemon TCG Dataset Extractor
Extrai cartas das 10 expansões mais recentes da API pokemontcg.io
e gera um guia de modelagem para Power BI.
"""

import requests
import pandas as pd
import time
import re
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
BASE_URL = "https://api.pokemontcg.io/v2"
HEADERS = {
    "User-Agent": "PokemonTCG-DataExtractor/1.0",
    # Se você tiver uma API key, descomente e preencha:
    # "X-Api-Key": "SUA_API_KEY_AQUI"
}
PAGE_SIZE = 250   # máximo permitido pela API
DELAY_BETWEEN_REQUESTS = 0.3   # segundos — respeita o rate limit sem key


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_json(url: str, params: dict) -> dict:
    """Faz GET com retry simples em caso de erro temporário."""
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:
                wait = 10 * attempt
                print(f"  Rate limit atingido. Aguardando {wait}s...")
                time.sleep(wait)
            else:
                raise e
        except requests.exceptions.RequestException as e:
            if attempt == 3:
                raise e
            time.sleep(5)
    return {}


def paginate(url: str, params: dict) -> list[dict]:
    """Percorre todas as páginas de um endpoint e retorna lista de itens."""
    items, page = [], 1
    while True:
        params["page"] = page
        data = get_json(url, params)
        batch = data.get("data", [])
        items.extend(batch)
        total_count = data.get("totalCount", 0)
        print(f"    Página {page} — {len(items)}/{total_count} itens")
        if len(items) >= total_count or not batch:
            break
        page += 1
        time.sleep(DELAY_BETWEEN_REQUESTS)
    return items


# ---------------------------------------------------------------------------
# Etapa 1 — Buscar as 10 expansões mais recentes
# ---------------------------------------------------------------------------
def fetch_latest_sets(n: int = 10) -> list[dict]:
    print(f"\n[1/3] Buscando as {n} expansões mais recentes...")
    raw = paginate(f"{BASE_URL}/sets", {"pageSize": PAGE_SIZE, "orderBy": "-releaseDate"})
    # Filtra apenas sets com data de lançamento válida e ordena decrescente
    sets_with_date = [s for s in raw if s.get("releaseDate")]
    sets_with_date.sort(key=lambda s: s["releaseDate"], reverse=True)
    selected = sets_with_date[:n]
    for s in selected:
        print(f"  • {s['name']} ({s['releaseDate']}) — id: {s['id']}")
    return selected


# ---------------------------------------------------------------------------
# Etapa 2 — Extrair cartas de cada expansão
# ---------------------------------------------------------------------------
def fetch_cards_for_sets(sets: list[dict]) -> list[dict]:
    print(f"\n[2/3] Extraindo cartas das {len(sets)} expansões...")
    all_cards = []
    for i, s in enumerate(sets, 1):
        set_id = s["id"]
        print(f"  [{i}/{len(sets)}] {s['name']} ({set_id})")
        cards = paginate(
            f"{BASE_URL}/cards",
            {"q": f"set.id:{set_id}", "pageSize": PAGE_SIZE},
        )
        # Enriquece cada carta com meta de set para facilitar o parse
        for c in cards:
            c["_set_name"] = s["name"]
            c["_set_release_date"] = s["releaseDate"]
        all_cards.extend(cards)
    print(f"  Total bruto: {len(all_cards)} cartas")
    return all_cards


# ---------------------------------------------------------------------------
# Etapa 3 — Parsear e limpar os campos
# ---------------------------------------------------------------------------
def parse_hp(value) -> pd.NA | int:
    if not value:
        return pd.NA
    digits = re.sub(r"\D", "", str(value))
    return int(digits) if digits else pd.NA


def flatten_types(types_list) -> str:
    if not types_list:
        return "Sem Tipo"
    return ", ".join(str(t) for t in types_list)


def total_energy_cost(attacks: list) -> int:
    """Soma o custo de energia de todos os ataques da carta."""
    if not attacks:
        return 0
    total = 0
    for attack in attacks:
        costs = attack.get("convertedEnergyCost", 0)
        total += costs if isinstance(costs, int) else 0
    return total


def max_attack_damage(attacks: list) -> pd.NA | int:
    """Retorna o maior dano numérico encontrado nos ataques."""
    if not attacks:
        return pd.NA
    damages = []
    for attack in attacks:
        raw = str(attack.get("damage", "") or "")
        digits = re.sub(r"\D", "", raw)
        if digits:
            damages.append(int(digits))
    return max(damages) if damages else pd.NA


def transform_cards(raw_cards: list[dict]) -> pd.DataFrame:
    print("\n[3/3] Transformando e limpando dados...")
    rows = []
    for c in raw_cards:
        attacks = c.get("attacks") or []
        row = {
            "id":               c.get("id", ""),
            "nome":             c.get("name", ""),
            "supertipo":        c.get("supertype", ""),
            "hp":               parse_hp(c.get("hp")),
            "tipos":            flatten_types(c.get("types")),
            "custo_energia_total":  total_energy_cost(attacks),
            "dano_maximo_ataque":   max_attack_damage(attacks),
            "nome_expansao":    c.get("_set_name", c.get("set", {}).get("name", "")),
            "data_lancamento":  c.get("_set_release_date", c.get("set", {}).get("releaseDate", "")),
            "imagem_small":     c.get("images", {}).get("small", ""),
            "imagem_large":     c.get("images", {}).get("large", ""),
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # --- Tipos de dados ---
    df["hp"] = pd.to_numeric(df["hp"], errors="coerce").astype("Int64")
    df["custo_energia_total"] = df["custo_energia_total"].fillna(0).astype("int64")
    df["dano_maximo_ataque"] = pd.to_numeric(df["dano_maximo_ataque"], errors="coerce").astype("Int64")
    df["data_lancamento"] = pd.to_datetime(df["data_lancamento"], errors="coerce")

    # --- Nulos em texto ---
    text_cols = ["id", "nome", "supertipo", "tipos", "nome_expansao", "imagem_small", "imagem_large"]
    for col in text_cols:
        df[col] = df[col].fillna("").str.strip()

    # --- Remover duplicatas por ID ---
    before = len(df)
    df.drop_duplicates(subset=["id"], inplace=True)
    print(f"  Duplicatas removidas: {before - len(df)}")
    print(f"  Registros finais: {len(df)}")
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Exportar CSV
# ---------------------------------------------------------------------------
def export_csv(df: pd.DataFrame, path: str = "pokemon_tcg_dataset.csv") -> None:
    df_export = df.copy()
    # Formata data como string ISO para compatibilidade com PBI
    df_export["data_lancamento"] = df_export["data_lancamento"].dt.strftime("%Y-%m-%d")
    df_export.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"\n  Dataset exportado → {path}")


# ---------------------------------------------------------------------------
# Gerar Guia Power BI
# ---------------------------------------------------------------------------
GUIDE_TEMPLATE = Path(__file__).with_name("guia_powerbi_template.md")


def generate_powerbi_guide(path: str = "guia_powerbi.md") -> None:
    template = GUIDE_TEMPLATE.read_text(encoding="utf-8")
    content = template.format(generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Guia Power BI gerado → {path}")


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  POKÉMON TCG — EXTRATOR DE DATASET")
    print("=" * 60)

    sets = fetch_latest_sets(n=10)
    raw_cards = fetch_cards_for_sets(sets)
    df = transform_cards(raw_cards)
    export_csv(df, "pokemon_tcg_dataset.csv")
    generate_powerbi_guide("guia_powerbi.md")

    print("\n" + "=" * 60)
    print("  Concluído com sucesso!")
    print(f"  Cartas no dataset : {len(df)}")
    print(f"  Expansões cobertas: {df['nome_expansao'].nunique()}")
    print(f"  Período           : {df['data_lancamento'].min()} → {df['data_lancamento'].max()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
