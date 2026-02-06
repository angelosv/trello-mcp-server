#!/usr/bin/env python3
"""
Script para verificar el estado completo de tarjetas en Trello.

Uso:
    python scripts/verify_cards.py --board-id <BOARD_ID> --list-id <LIST_ID>

Variables de entorno requeridas:
    TRELLO_API_KEY
    TRELLO_TOKEN
"""
import json
import os
import subprocess
import sys
import argparse

KEY = os.getenv("TRELLO_API_KEY", "")
TOKEN = os.getenv("TRELLO_TOKEN", "")
BASE_URL = "https://api.trello.com/1"

def api_call(endpoint):
    """Make Trello API call"""
    if not KEY or not TOKEN:
        print("Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
        print("       Configúralos en .env o como variables de entorno")
        sys.exit(1)
    
    url = f"{BASE_URL}/{endpoint}?key={KEY}&token={TOKEN}"
    cmd = ["curl", "-s", url]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except:
            return None
    return None

def verify_cards(board_id, list_id):
    """Verify cards in a list"""
    # Obtener tarjetas
    cards = api_call(f"lists/{list_id}/cards")
    if not cards:
        print("Error obteniendo tarjetas")
        return
    
    # Obtener etiquetas
    labels_data = api_call(f"boards/{board_id}/labels")
    labels_map = {}
    for label in labels_data:
        labels_map[label['id']] = label.get('name', '') or label.get('color', '')
    
    # Obtener miembros
    members_data = api_call(f"boards/{board_id}/members")
    members_map = {}
    for member in members_data:
        members_map[member['id']] = member.get('fullName', member.get('username', ''))
    
    print(f'📊 VERIFICACIÓN - {len(cards)} tarjetas\n')
    print('='*80)
    
    issues = []
    perfect = []
    
    for card in cards:
        card_id = card['id']
        card_name = card['name']
        desc_len = len(card.get('desc', ''))
        card_labels = [labels_map.get(lid, '?') for lid in card.get('idLabels', [])]
        card_members = [members_map.get(mid, '?') for mid in card.get('idMembers', [])]
        
        # Verificar checklist
        checklists = api_call(f"cards/{card_id}/checklists")
        checklist_count = len(checklists) if checklists else 0
        items_count = sum(len(c.get('checkItems', [])) for c in checklists) if checklists else 0
        
        # Verificaciones
        has_kotlin = any('kotlin' in str(l).lower() for l in card_labels)
        has_sdk = any('sdk' in str(l).lower() for l in card_labels)
        has_2_members = len(card_members) >= 2
        has_desc = desc_len > 200
        has_checklist = checklist_count > 0 and items_count > 0
        
        all_ok = has_kotlin and has_sdk and has_2_members and has_desc and has_checklist
        
        if all_ok:
            perfect.append(card_name)
            status = '✅'
        else:
            issues.append({
                'name': card_name,
                'kotlin': has_kotlin,
                'sdk': has_sdk,
                'members': len(card_members),
                'desc': desc_len,
                'checklist': items_count
            })
            status = '⚠️'
        
        print(f'{status} {card_name[:55]}')
        print(f'   Labels: {", ".join(card_labels[:3]) if card_labels else "NINGUNA"}')
        print(f'   Members: {len(card_members)} | Desc: {desc_len} chars | Checklist: {items_count} items')
        print()
    
    print('='*80)
    print(f'\n📈 RESUMEN:')
    print(f'   ✅ Perfectas: {len(perfect)}/{len(cards)}')
    print(f'   ⚠️  Con problemas: {len(issues)}/{len(cards)}')
    
    if issues:
        print(f'\n⚠️  TARJETAS CON PROBLEMAS:')
        for issue in issues:
            problems = []
            if not issue['kotlin']: problems.append('falta kotlin')
            if not issue['sdk']: problems.append('falta sdk')
            if issue['members'] < 2: problems.append(f'solo {issue["members"]} miembros')
            if issue['desc'] < 200: problems.append(f'desc corta ({issue["desc"]} chars)')
            if issue['checklist'] == 0: problems.append('sin checklist')
            print(f'   - {issue["name"]}: {", ".join(problems)}')
    else:
        print('\n🎉 ¡Todas las tarjetas están completas y correctas!')

def main():
    parser = argparse.ArgumentParser(description="Verificar estado de tarjetas en Trello")
    parser.add_argument("--board-id", required=True, help="ID del board de Trello")
    parser.add_argument("--list-id", required=True, help="ID de la lista de Trello")
    
    args = parser.parse_args()
    verify_cards(args.board_id, args.list_id)

if __name__ == "__main__":
    main()
