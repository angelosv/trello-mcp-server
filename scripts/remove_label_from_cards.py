#!/usr/bin/env python3
"""
Remove a label from one or more Trello cards.

Útil para corregir asignaciones incorrectas de etiquetas (ej: quitar etiqueta vacía
y usar la correcta como Kotlin).

Uso:
    # Quitar etiqueta específica de tarjetas específicas
    python scripts/remove_label_from_cards.py \\
        --label-id 6964ea21570279f07def77f3 \\
        --card-ids 698c9fd83f99805c8c9f9aa3 698c9fdae330005d5a70b42f

    # Quitar etiqueta de todas las tarjetas de una lista
    python scripts/remove_label_from_cards.py \\
        --label-id 6964ea21570279f07def77f3 \\
        --list-id 6964ed62b23b70bbd5c89432
"""
import argparse
import os
import sys

import httpx

# Load .env
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    try:
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k, v = line.strip().split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    if k == 'TRELLO_API_KEY':
                        os.environ['TRELLO_API_KEY'] = v
                    elif k in ('TRELLO_API_TOKEN', 'TRELLO_TOKEN'):
                        os.environ['TRELLO_TOKEN'] = v
    except FileNotFoundError:
        pass


def get_cards_from_list(list_id: str, key: str, token: str) -> list[str]:
    """Obtiene los IDs de las tarjetas en una lista."""
    r = httpx.get(
        f"https://api.trello.com/1/lists/{list_id}/cards",
        params={"key": key, "token": token, "fields": "id"}
    )
    r.raise_for_status()
    return [c["id"] for c in r.json()]


def remove_label_from_card(card_id: str, label_id: str, key: str, token: str) -> bool:
    """Quita una etiqueta de una tarjeta."""
    r = httpx.delete(
        f"https://api.trello.com/1/cards/{card_id}/idLabels/{label_id}",
        params={"key": key, "token": token}
    )
    return r.status_code == 200


def main():
    load_env()
    KEY = os.getenv("TRELLO_API_KEY", "e582f14026a35a1b1a886d0ba2ad2316")
    TOKEN = os.getenv("TRELLO_API_TOKEN") or os.getenv("TRELLO_TOKEN")

    parser = argparse.ArgumentParser(description="Quitar etiqueta de tarjetas de Trello")
    parser.add_argument("--label-id", required=True, help="ID de la etiqueta a quitar")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--card-ids", nargs="+", help="IDs de las tarjetas")
    group.add_argument("--list-id", help="ID de la lista (quita la etiqueta de todas las tarjetas)")
    args = parser.parse_args()

    if not TOKEN:
        print("❌ TRELLO_API_TOKEN o TRELLO_TOKEN requerido en .env")
        sys.exit(1)

    if args.card_ids:
        card_ids = args.card_ids
    else:
        card_ids = get_cards_from_list(args.list_id, KEY, TOKEN)
        print(f"Encontradas {len(card_ids)} tarjetas en la lista")

    success = 0
    for card_id in card_ids:
        if remove_label_from_card(card_id, args.label_id, KEY, TOKEN):
            print(f"✓ Quitada etiqueta de tarjeta {card_id}")
            success += 1
        else:
            print(f"✗ Error en tarjeta {card_id}")

    print(f"\n{success}/{len(card_ids)} tarjetas actualizadas")


if __name__ == "__main__":
    main()
