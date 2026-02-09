#!/usr/bin/env python3
"""
Analiza las tarjetas que el desarrollador movió en Trello
"""
import os
import subprocess
import json
import sys
from datetime import datetime

# Leer .env
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                parts = line.strip().split('=', 1)
                if len(parts) == 2:
                    key, value = parts
                    os.environ[key] = value

api_key = os.environ.get('TRELLO_API_KEY')
token = os.environ.get('TRELLO_TOKEN')
board_id = '6964ea21570279f07def7786'

if not api_key or not token:
    print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
    sys.exit(1)

def api_call(method, endpoint, params=None):
    """Make Trello API call"""
    url = f"https://api.trello.com/1/{endpoint}"
    query_params = f"key={api_key}&token={token}"
    
    if params:
        query_params += "&" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    url = f"{url}?{query_params}"
    
    cmd = ["curl", "-s", "-X", method, url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return result.stdout
    return None

print("🔍 Analizando tarjetas en Trello...\n")

# Obtener todas las listas
lists = api_call("GET", f"boards/{board_id}/lists")
if not lists or not isinstance(lists, list):
    print(f"❌ Error obteniendo listas: {lists}")
    sys.exit(1)

print("📋 Listas encontradas:")
list_map = {}
for lst in lists:
    list_name = lst.get('name', 'Unknown')
    list_id = lst.get('id', '')
    list_map[list_id] = list_name
    print(f"  - {list_name}: {list_id}")

# IDs conocidos de nuestras tarjetas de Engagement
engagement_card_ids = [
    "6985f75601b379d47f292a75",  # Testing
    "6985f758865df376c0242f49",  # Backend
    "6985f764ed6ed5c45d95c077",  # Monitoring
    "6985f76407e65cc885c91b89",  # Documentación
]

print(f"\n📊 Analizando tarjetas de Engagement ({len(engagement_card_ids)} tarjetas)...\n")

# Analizar cada tarjeta
cards_analysis = []
for card_id in engagement_card_ids:
    card = api_call("GET", f"cards/{card_id}", {
        "fields": "id,name,idList,dateLastActivity,labels,idMembers,checklists"
    })
    
    if card and isinstance(card, dict):
        card_name = card.get('name', 'Unknown')
        current_list_id = card.get('idList', '')
        current_list_name = list_map.get(current_list_id, 'Unknown')
        last_activity = card.get('dateLastActivity', '')
        labels = card.get('labels', [])
        members = card.get('idMembers', [])
        checklists = card.get('checklists', [])
        
        # Determinar estado
        is_in_backlog = 'backlog' in current_list_name.lower()
        is_in_todo = 'to do' in current_list_name.lower() or 'todo' in current_list_name.lower()
        
        cards_analysis.append({
            'id': card_id,
            'name': card_name,
            'current_list': current_list_name,
            'current_list_id': current_list_id,
            'is_in_backlog': is_in_backlog,
            'is_in_todo': is_in_todo,
            'last_activity': last_activity,
            'labels': [l.get('name', l.get('color', '')) for l in labels],
            'members_count': len(members),
            'checklists_count': len(checklists),
            'checklist_items': sum(len(c.get('checkItems', [])) for c in checklists)
        })

# Mostrar análisis
print("=" * 80)
print("ANÁLISIS DE TARJETAS DE ENGAGEMENT")
print("=" * 80)

backlog_cards = [c for c in cards_analysis if c['is_in_backlog']]
todo_cards = [c for c in cards_analysis if c['is_in_todo']]
other_cards = [c for c in cards_analysis if not c['is_in_backlog'] and not c['is_in_todo']]

print(f"\n✅ En 'To do' ({len(todo_cards)} tarjetas):")
for card in todo_cards:
    print(f"\n  📌 {card['name']}")
    print(f"     Lista: {card['current_list']}")
    print(f"     Labels: {', '.join(card['labels']) if card['labels'] else 'ninguno'}")
    print(f"     Miembros: {card['members_count']}")
    print(f"     Checklists: {card['checklists_count']} ({card['checklist_items']} items)")
    print(f"     Última actividad: {card['last_activity']}")

print(f"\n📦 En 'Backlog' ({len(backlog_cards)} tarjetas):")
for card in backlog_cards:
    print(f"\n  📌 {card['name']}")
    print(f"     Lista: {card['current_list']}")
    print(f"     Labels: {', '.join(card['labels']) if card['labels'] else 'ninguno'}")

if other_cards:
    print(f"\n📍 En otras listas ({len(other_cards)} tarjetas):")
    for card in other_cards:
        print(f"\n  📌 {card['name']}")
        print(f"     Lista: {card['current_list']}")

# Resumen de lo que el desarrollador movió
print("\n" + "=" * 80)
print("RESUMEN: Lo que el desarrollador movió")
print("=" * 80)

if todo_cards:
    print(f"\n✅ El desarrollador movió {len(todo_cards)} tarjeta(s) a 'To do':")
    for card in todo_cards:
        print(f"   - {card['name']}")
        if card['checklists_count'] > 0:
            print(f"     ✓ Tiene {card['checklists_count']} checklist(s) con {card['checklist_items']} items")
        if card['members_count'] > 0:
            print(f"     ✓ Tiene {card['members_count']} miembro(s) asignado(s)")
else:
    print("\n⚠️  No hay tarjetas en 'To do' aún")

if backlog_cards:
    print(f"\n📦 Quedan {len(backlog_cards)} tarjeta(s) en 'Backlog':")
    for card in backlog_cards:
        print(f"   - {card['name']}")

print("\n" + "=" * 80)
