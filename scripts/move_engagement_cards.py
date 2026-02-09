#!/usr/bin/env python3
"""
Mover tarjetas de Engagement Improvements del Backlog a To do
"""
import os
import subprocess
import json
import sys
import time

# IDs conocidos del board Dev
BOARD_ID = '6964ea21570279f07def7786'
BACKLOG_LIST_ID = '6985d6babb14a3a08db187a8'  # backlog (lowercase)
TODO_LIST_ID = '6964ed62b23b70bbd5c89432'  # To do (de conversación anterior)

# Tarjetas de Engagement que creamos (prioritarias para mover)
ENGAGEMENT_CARDS = [
    "6985f75601b379d47f292a75",  # Testing: Engagement Backend Improvements
    "6985f758865df376c0242f49",  # Backend: Actualizar API para aceptar API key en headers
]

# Intentar obtener credenciales
api_key = os.environ.get('TRELLO_API_KEY')
token = os.environ.get('TRELLO_TOKEN')

# Si no están en env, intentar leer .env
if not api_key or not token:
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if key == 'TRELLO_API_KEY':
                        api_key = value
                    elif key == 'TRELLO_TOKEN':
                        token = value

if not api_key or not token:
    print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
    print("   Configúralos en .env o como variables de entorno")
    sys.exit(1)

def api_call(method, endpoint, data=None):
    """Make Trello API call"""
    url = f"https://api.trello.com/1/{endpoint}"
    params = f"key={api_key}&token={token}"
    
    if data:
        params += "&" + "&".join([f"{k}={v}" for k, v in data.items()])
    
    url = f"{url}?{params}"
    
    cmd = ["curl", "-s", "-X", method, url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return result.stdout
    return None

# Usar ID conocido de "To do" o intentar encontrarla
todo_id = TODO_LIST_ID

# Verificar que la lista existe
todo_list = api_call("GET", f"lists/{todo_id}")
if todo_list and isinstance(todo_list, dict):
    print(f"✅ Lista 'To do' encontrada: {todo_list.get('name', 'To do')}")
else:
    # Intentar encontrar por nombre
    lists = api_call("GET", f"boards/{BOARD_ID}/lists")
    if lists and isinstance(lists, list):
        for lst in lists:
            name_lower = lst.get('name', '').lower()
            if name_lower in ['to do', 'todo', 'to-do']:
                todo_id = lst['id']
                print(f"✅ Encontrada lista 'To do': {todo_id}")
                break
    
    if not todo_id:
        print("❌ Error: No se encontró lista 'To do'")
        print("Listas disponibles:")
        if lists and isinstance(lists, list):
            for lst in lists:
                print(f"  - {lst.get('name', 'Unknown')}: {lst.get('id', 'Unknown')}")
        sys.exit(1)

# Obtener información de las tarjetas antes de moverlas
print(f"\n📋 Revisando tarjetas de Engagement...\n")

cards_to_move = []
for card_id in ENGAGEMENT_CARDS:
    card = api_call("GET", f"cards/{card_id}", {"fields": "id,name,idList"})
    if card and isinstance(card, dict):
        card_name = card.get('name', 'Unknown')
        current_list = card.get('idList', '')
        
        if current_list == BACKLOG_LIST_ID:
            cards_to_move.append((card_id, card_name))
            print(f"  ✓ {card_name}")
            print(f"    Estado: En Backlog (listo para mover)")
        elif current_list == todo_id:
            print(f"  ⏭️  {card_name}")
            print(f"    Estado: Ya está en 'To do'")
        else:
            print(f"  ⚠️  {card_name}")
            print(f"    Estado: En otra lista (ID: {current_list})")
    else:
        print(f"  ❌ Error obteniendo tarjeta {card_id}")

# Mover tarjetas
if cards_to_move:
    print(f"\n🔄 Moviendo {len(cards_to_move)} tarjetas a 'To do'...\n")
    
    moved = []
    failed = []
    
    for card_id, card_name in cards_to_move:
        result = api_call("PUT", f"cards/{card_id}", {"idList": todo_id})
        if result:
            moved.append(card_name)
            print(f"  ✅ Movida: {card_name}")
        else:
            failed.append(card_name)
            print(f"  ❌ Error moviendo: {card_name}")
        time.sleep(0.3)
    
    print(f"\n✅ RESUMEN:")
    print(f"   ✅ Movidas exitosamente: {len(moved)}")
    if moved:
        for name in moved:
            print(f"      - {name}")
    if failed:
        print(f"   ❌ Fallidas: {len(failed)}")
        for name in failed:
            print(f"      - {name}")
else:
    print("\n⚠️  No hay tarjetas para mover (ya están en 'To do' o en otra lista)")
