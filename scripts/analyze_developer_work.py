#!/usr/bin/env python3
"""
Analiza las tarjetas que el desarrollador movió usando el mismo enfoque que validate_tasks.py
"""
import os
import sys
import httpx
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"
BOARD_ID = "6964ea21570279f07def7786"

# IDs de nuestras tarjetas de Engagement
ENGAGEMENT_CARDS = [
    "6985f75601b379d47f292a75",  # Testing
    "6985f758865df376c0242f49",  # Backend
    "6985f764ed6ed5c45d95c077",  # Monitoring
    "6985f76407e65cc885c91b89",  # Documentación
]

def get_board_lists(board_id: str):
    """Obtiene todas las listas del board."""
    url = f"{TRELLO_API_BASE}/boards/{board_id}/lists"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()

def get_card_details(card_id: str):
    """Obtiene detalles completos de una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "fields": "id,name,desc,idList,idLabels,idMembers,url,dateLastActivity,checklists"
    }
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()

def get_list_name(list_id: str):
    """Obtiene el nombre de una lista."""
    url = f"{TRELLO_API_BASE}/lists/{list_id}"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN, "fields": "name"}
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("name", "Unknown")

def get_card_checklists(card_id: str):
    """Obtiene los checklists de una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}/checklists"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()

def get_label_names(label_ids: list, board_id: str):
    """Obtiene los nombres de los labels."""
    url = f"{TRELLO_API_BASE}/boards/{board_id}/labels"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        labels = response.json()
        
        label_map = {l['id']: l.get('name', l.get('color', '')) for l in labels}
        return [label_map.get(lid, 'Unknown') for lid in label_ids]

def get_member_names(member_ids: list):
    """Obtiene los nombres de los miembros."""
    member_names = []
    for member_id in member_ids:
        url = f"{TRELLO_API_BASE}/members/{member_id}"
        params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN, "fields": "fullName,username"}
        
        with httpx.Client() as client:
            try:
                response = client.get(url, params=params)
                response.raise_for_status()
                member = response.json()
                member_names.append(member.get('fullName', member.get('username', 'Unknown')))
            except:
                member_names.append('Unknown')
    
    return member_names

if __name__ == "__main__":
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
        sys.exit(1)
    
    print("🔍 Analizando trabajo del desarrollador en Trello...\n")
    
    # Obtener listas
    lists = get_board_lists(BOARD_ID)
    list_map = {lst['id']: lst['name'] for lst in lists}
    
    print("📋 Listas disponibles:")
    for lst in lists:
        print(f"  - {lst['name']}: {lst['id']}")
    
    # Analizar tarjetas de Engagement
    print(f"\n📊 Analizando {len(ENGAGEMENT_CARDS)} tarjetas de Engagement...\n")
    
    cards_analysis = []
    for card_id in ENGAGEMENT_CARDS:
        try:
            card = get_card_details(card_id)
            list_id = card.get('idList', '')
            list_name = list_map.get(list_id, 'Unknown')
            
            # Obtener labels y miembros
            label_ids = card.get('idLabels', [])
            member_ids = card.get('idMembers', [])
            
            labels = get_label_names(label_ids, BOARD_ID)
            members = get_member_names(member_ids)
            
            # Obtener checklists
            checklists = get_card_checklists(card_id)
            checklist_items_count = sum(len(cl.get('checkItems', [])) for cl in checklists)
            
            cards_analysis.append({
                'id': card_id,
                'name': card.get('name', 'Unknown'),
                'list_name': list_name,
                'list_id': list_id,
                'url': card.get('url', ''),
                'labels': labels,
                'members': members,
                'checklists_count': len(checklists),
                'checklist_items': checklist_items_count,
                'last_activity': card.get('dateLastActivity', '')
            })
        except Exception as e:
            print(f"  ❌ Error obteniendo tarjeta {card_id}: {e}")
            continue
    
    # Organizar por lista
    backlog_cards = [c for c in cards_analysis if 'backlog' in c['list_name'].lower()]
    todo_cards = [c for c in cards_analysis if 'to do' in c['list_name'].lower() or 'todo' in c['list_name'].lower()]
    other_cards = [c for c in cards_analysis if c not in backlog_cards and c not in todo_cards]
    
    print("=" * 80)
    print("ANÁLISIS DE TARJETAS DE ENGAGEMENT")
    print("=" * 80)
    
    if todo_cards:
        print(f"\n✅ TARJETAS EN 'To do' ({len(todo_cards)} tarjetas):")
        print("   (Estas son las que el desarrollador movió o está trabajando)\n")
        for card in todo_cards:
            print(f"  📌 {card['name']}")
            print(f"     Lista: {card['list_name']}")
            print(f"     URL: {card['url']}")
            print(f"     Labels: {', '.join(card['labels']) if card['labels'] else 'ninguno'}")
            print(f"     Miembros: {', '.join(card['members']) if card['members'] else 'ninguno asignado'}")
            print(f"     Checklists: {card['checklists_count']} ({card['checklist_items']} items)")
            print(f"     Última actividad: {card['last_activity']}")
            print()
    
    if backlog_cards:
        print(f"\n📦 TARJETAS EN 'Backlog' ({len(backlog_cards)} tarjetas):")
        print("   (Estas aún no han sido movidas)\n")
        for card in backlog_cards:
            print(f"  📌 {card['name']}")
            print(f"     Lista: {card['list_name']}")
            print(f"     URL: {card['url']}")
            print(f"     Labels: {', '.join(card['labels']) if card['labels'] else 'ninguno'}")
            print()
    
    if other_cards:
        print(f"\n📍 TARJETAS EN OTRAS LISTAS ({len(other_cards)} tarjetas):")
        for card in other_cards:
            print(f"  📌 {card['name']} - {card['list_name']}")
            print(f"     URL: {card['url']}")
            print()
    
    # Resumen de lo que el desarrollador movió
    print("=" * 80)
    print("RESUMEN: Lo que el desarrollador movió")
    print("=" * 80)
    
    if todo_cards:
        print(f"\n✅ El desarrollador movió {len(todo_cards)} tarjeta(s) a 'To do':")
        for card in todo_cards:
            print(f"\n   📋 {card['name']}")
            print(f"      🔗 {card['url']}")
            if card['checklists_count'] > 0:
                print(f"      ✓ Tiene {card['checklists_count']} checklist(s) con {card['checklist_items']} items")
            if card['members']:
                print(f"      👥 Asignado a: {', '.join(card['members'])}")
            if card['labels']:
                print(f"      🏷️  Labels: {', '.join(card['labels'])}")
    else:
        print("\n⚠️  No hay tarjetas en 'To do' aún")
        print("   El desarrollador aún no ha movido tarjetas del Backlog")
    
    if backlog_cards:
        print(f"\n📦 Quedan {len(backlog_cards)} tarjeta(s) en 'Backlog':")
        for card in backlog_cards:
            print(f"   - {card['name']}")
    
    print("\n" + "=" * 80)
