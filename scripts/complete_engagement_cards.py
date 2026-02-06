#!/usr/bin/env python3
"""
Script para completar tarjetas de Trello con descripciones, etiquetas, miembros y checklists.

Uso:
    python scripts/complete_engagement_cards.py --board-id <BOARD_ID> --list-id <LIST_ID>

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

# Configuración desde variables de entorno
KEY = os.getenv("TRELLO_API_KEY", "")
TOKEN = os.getenv("TRELLO_TOKEN", "")
BASE_URL = "https://api.trello.com/1"

def api_call(method, endpoint, data=None, retries=3):
    """Make Trello API call with retries"""
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
    
    for attempt in range(retries):
        cmd = ["curl", "-s", "-X", method, url, "--max-time", "10"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except:
                return result.stdout
        
        if attempt < retries - 1:
            time.sleep(1)
    
    return None

def update_card_desc(card_id, desc):
    """Update card description"""
    return api_call("PUT", f"cards/{card_id}", {"desc": desc})

def add_label_to_card(card_id, label_id):
    """Add label to card"""
    return api_call("POST", f"cards/{card_id}/idLabels", {"value": label_id})

def add_member_to_card(card_id, member_id):
    """Add member to card"""
    return api_call("POST", f"cards/{card_id}/idMembers", {"value": member_id})

def create_checklist(card_id, name, items):
    """Create checklist with items"""
    checklist_data = api_call("POST", f"checklists", {
        "idCard": card_id,
        "name": name
    })
    
    if not checklist_data or "id" not in checklist_data:
        return None
    
    checklist_id = checklist_data["id"]
    
    for item in items:
        api_call("POST", f"checklists/{checklist_id}/checkItems", {"name": item})
        time.sleep(0.2)  # Pequeña pausa entre items
    
    return checklist_id

def get_board_labels(board_id):
    """Get all labels from board"""
    labels_data = api_call("GET", f"boards/{board_id}/labels")
    labels_map = {}
    for label in labels_data:
        name = label.get('name', '').lower()
        if name:
            labels_map[name] = label['id']
        # También mapear por color si no tiene nombre
        labels_map[label.get('color', '')] = label['id']
    return labels_map

def get_board_members(board_id):
    """Get all members from board"""
    members_data = api_call("GET", f"boards/{board_id}/members")
    return [m['id'] for m in members_data]

def process_card(card_id, card_data, board_id, labels_map, members):
    """Process a single card with description, labels, members and checklist"""
    print(f"\n📝 Procesando: {card_id}")
    
    # Actualizar descripción
    if "desc" in card_data:
        if update_card_desc(card_id, card_data["desc"]):
            print("  ✓ Descripción actualizada")
    
    # Agregar etiquetas
    if "labels" in card_data:
        for label_name in card_data["labels"]:
            label_id = labels_map.get(label_name.lower())
            if label_id:
                add_label_to_card(card_id, label_id)
                print(f"  ✓ Etiqueta '{label_name}' agregada")
    
    # Agregar usuarios
    if members:
        for member_id in members:
            add_member_to_card(card_id, member_id)
        print(f"  ✓ Usuarios asignados ({len(members)})")
    
    # Crear checklist
    if "checklist" in card_data:
        create_checklist(card_id, "Tareas", card_data["checklist"])
        print(f"  ✓ Checklist creado con {len(card_data['checklist'])} items")

def main():
    parser = argparse.ArgumentParser(description="Completar tarjetas de Trello con descripciones, etiquetas, miembros y checklists")
    parser.add_argument("--board-id", required=True, help="ID del board de Trello")
    parser.add_argument("--list-id", required=True, help="ID de la lista de Trello")
    parser.add_argument("--cards-file", help="Archivo JSON con datos de las tarjetas (opcional)")
    
    args = parser.parse_args()
    
    # Obtener etiquetas y miembros del board
    print("🔍 Obteniendo configuración del board...")
    labels_map = get_board_labels(args.board_id)
    members = get_board_members(args.board_id)
    
    print(f"   Etiquetas encontradas: {len(labels_map)}")
    print(f"   Miembros encontrados: {len(members)}\n")
    
    # Si se proporciona archivo de tarjetas, usarlo
    if args.cards_file and os.path.exists(args.cards_file):
        with open(args.cards_file, 'r') as f:
            cards_data = json.load(f)
    else:
        # Obtener tarjetas de la lista
        cards = api_call("GET", f"lists/{args.list_id}/cards", {"fields": "id,name"})
        if not cards:
            print("No se encontraron tarjetas en la lista")
            return
        
        print(f"📋 Se encontraron {len(cards)} tarjetas")
        print("⚠️  Usa --cards-file para proporcionar descripciones y checklists")
        print("\nTarjetas encontradas:")
        for card in cards:
            print(f"  - {card['name']} (ID: {card['id']})")
        return
    
    # Procesar tarjetas
    print(f"\n📋 Procesando {len(cards_data)} tarjetas...\n")
    
    for card_id, data in cards_data.items():
        try:
            process_card(card_id, data, args.board_id, labels_map, members)
            time.sleep(0.5)  # Pausa entre tarjetas
        except Exception as e:
            print(f"  ✗ Error procesando tarjeta {card_id}: {e}")
            continue
    
    print(f"\n✅ Completado! Procesadas {len(cards_data)} tarjetas")

if __name__ == "__main__":
    main()
