#!/usr/bin/env python3
"""
Script para mover tarjetas entre listas en Trello.

Uso:
    python scripts/move_cards.py --board-id <BOARD_ID> --from-list <FROM_LIST_ID> --to-list <TO_LIST_ID> [--card-names <CARD_NAMES_FILE>]

Variables de entorno requeridas:
    TRELLO_API_KEY
    TRELLO_TOKEN
"""
import json
import os
import subprocess
import sys
import urllib.parse
import time
import argparse

KEY = os.getenv("TRELLO_API_KEY", "")
TOKEN = os.getenv("TRELLO_TOKEN", "")
BASE_URL = "https://api.trello.com/1"

def api_call(method, endpoint, data=None):
    """Make Trello API call"""
    if not KEY or not TOKEN:
        print("Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
        print("       Configúralos en .env o como variables de entorno")
        sys.exit(1)
    
    url = f"{BASE_URL}/{endpoint}"
    if data:
        params = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in data.items()])
        url = f"{url}?{params}&key={KEY}&token={TOKEN}"
    else:
        url = f"{url}?key={KEY}&token={TOKEN}"
    
    cmd = ["curl", "-s", "-X", method, url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return result.stdout
    return None

def move_card_to_list(card_id, list_id):
    """Move card to different list"""
    return api_call("PUT", f"cards/{card_id}", {"idList": list_id})

def find_list_by_name(board_id, list_name):
    """Find list ID by name"""
    lists_data = api_call("GET", f"boards/{board_id}/lists")
    for lst in lists_data:
        if lst['name'] == list_name:
            return lst['id']
    return None

def main():
    parser = argparse.ArgumentParser(description="Mover tarjetas entre listas en Trello")
    parser.add_argument("--board-id", required=True, help="ID del board de Trello")
    parser.add_argument("--from-list", help="ID de la lista origen (o nombre)")
    parser.add_argument("--from-list-name", help="Nombre de la lista origen")
    parser.add_argument("--to-list", help="ID de la lista destino (o nombre)")
    parser.add_argument("--to-list-name", help="Nombre de la lista destino")
    parser.add_argument("--card-names", help="Archivo JSON con nombres de tarjetas a mover (opcional)")
    parser.add_argument("--first-n", type=int, help="Mover solo las primeras N tarjetas")
    
    args = parser.parse_args()
    
    # Resolver IDs de listas
    from_list_id = args.from_list
    if args.from_list_name:
        from_list_id = find_list_by_name(args.board_id, args.from_list_name)
        if not from_list_id:
            print(f"Error: No se encontró lista '{args.from_list_name}'")
            sys.exit(1)
    
    to_list_id = args.to_list
    if args.to_list_name:
        to_list_id = find_list_by_name(args.board_id, args.to_list_name)
        if not to_list_id:
            print(f"Error: No se encontró lista '{args.to_list_name}'")
            sys.exit(1)
    
    if not from_list_id or not to_list_id:
        print("Error: Debes especificar --from-list/--from-list-name y --to-list/--to-list-name")
        sys.exit(1)
    
    # Obtener tarjetas de la lista origen
    cards = api_call("GET", f"lists/{from_list_id}/cards", {"fields": "id,name"})
    if not cards:
        print("No se encontraron tarjetas en la lista origen")
        return
    
    # Filtrar tarjetas si se proporciona archivo
    cards_to_move = cards
    if args.card_names:
        with open(args.card_names, 'r') as f:
            card_names = json.load(f)
        cards_to_move = [c for c in cards if c['name'] in card_names]
    
    # Limitar cantidad si se especifica
    if args.first_n:
        cards_to_move = cards_to_move[:args.first_n]
    
    print(f"🔄 Moviendo {len(cards_to_move)} tarjetas...\n")
    
    moved = []
    failed = []
    
    for card in cards_to_move:
        card_id = card['id']
        card_name = card['name']
        
        if move_card_to_list(card_id, to_list_id):
            moved.append(card_name)
            print(f"✓ Movida: {card_name[:60]}...")
        else:
            failed.append(card_name)
            print(f"✗ Error moviendo: {card_name[:60]}...")
        
        time.sleep(0.2)
    
    print(f"\n✅ RESUMEN:")
    print(f"   ✓ Movidas exitosamente: {len(moved)}")
    if failed:
        print(f"   ✗ Fallidas: {len(failed)}")
        for name in failed:
            print(f"     - {name}")

if __name__ == "__main__":
    main()
