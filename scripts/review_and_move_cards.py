#!/usr/bin/env python3
"""
Script para revisar tarjetas en Backlog y mover las prioritarias a To do
"""
import os
import subprocess
import json
import sys
import time

# Cargar variables de entorno desde .env si existe
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

api_key = os.environ.get('TRELLO_API_KEY')
token = os.environ.get('TRELLO_TOKEN')
board_id = '6964ea21570279f07def7786'

if not api_key or not token:
    print("Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
    sys.exit(1)

def api_call(method, endpoint, data=None):
    """Make Trello API call"""
    url = f"https://api.trello.com/1/{endpoint}?key={api_key}&token={token}"
    if data:
        if method == "PUT":
            url += "&" + "&".join([f"{k}={v}" for k, v in data.items()])
        else:
            url += "&" + "&".join([f"{k}={v}" for k, v in data.items()])
    
    cmd = ["curl", "-s", "-X", method, url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return result.stdout
    return None

# Obtener listas
lists_result = api_call("GET", f"boards/{board_id}/lists")
if not lists_result or not isinstance(lists_result, list):
    print(f"Error obteniendo listas: {lists_result}")
    sys.exit(1)

lists = lists_result
backlog_id = None
todo_id = None

for lst in lists:
    name_lower = lst['name'].lower()
    if name_lower == 'backlog':
        backlog_id = lst['id']
    elif name_lower in ['to do', 'todo', 'to-do']:
        todo_id = lst['id']

if not backlog_id:
    print("Error: No se encontró lista 'backlog'")
    sys.exit(1)

if not todo_id:
    print("Error: No se encontró lista 'To do'")
    sys.exit(1)

print(f"📋 Backlog ID: {backlog_id}")
print(f"✅ To Do ID: {todo_id}\n")

# Obtener tarjetas del backlog
cards_result = api_call("GET", f"lists/{backlog_id}/cards", {"fields": "id,name,labels,desc"})
if not cards_result or not isinstance(cards_result, list):
    print(f"Error obteniendo tarjetas: {cards_result}")
    cards_result = []

cards = cards_result

print(f"📊 Tarjetas en Backlog ({len(cards)}):\n")
for i, card in enumerate(cards, 1):
    labels = [l.get('name', l.get('color', '')) for l in card.get('labels', [])]
    desc_preview = card.get('desc', '')[:100].replace('\n', ' ')
    print(f"{i}. {card['name']}")
    print(f"   Labels: {', '.join(labels) if labels else 'ninguno'}")
    print(f"   Desc: {desc_preview}...")
    print()

# Identificar tarjetas prioritarias basadas en contenido
priority_keywords = ['testing', 'test', 'alta', 'high priority', 'crítico', 'critical']
high_priority_cards = []

for card in cards:
    name_lower = card['name'].lower()
    desc_lower = card.get('desc', '').lower()
    
    # Buscar keywords de prioridad
    is_priority = any(keyword in name_lower or keyword in desc_lower for keyword in priority_keywords)
    
    # También considerar las tarjetas que creamos sobre engagement improvements
    if 'engagement' in name_lower and ('testing' in name_lower or 'backend' in name_lower):
        is_priority = True
    
    if is_priority:
        high_priority_cards.append(card)

print(f"\n🎯 Tarjetas prioritarias identificadas ({len(high_priority_cards)}):\n")
for card in high_priority_cards:
    print(f"  - {card['name']}")

# Mover tarjetas prioritarias
if high_priority_cards:
    print(f"\n🔄 Moviendo {len(high_priority_cards)} tarjetas a 'To do'...\n")
    
    moved = []
    for card in high_priority_cards:
        result = api_call("PUT", f"cards/{card['id']}", {"idList": todo_id})
        if result:
            moved.append(card['name'])
            print(f"  ✅ Movida: {card['name']}")
        else:
            print(f"  ❌ Error moviendo: {card['name']}")
        time.sleep(0.3)
    
    print(f"\n✅ RESUMEN: {len(moved)}/{len(high_priority_cards)} tarjetas movidas exitosamente")
else:
    print("\n⚠️  No se identificaron tarjetas prioritarias para mover")
