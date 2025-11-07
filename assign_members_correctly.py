#!/usr/bin/env python3
"""
Script para verificar y asignar correctamente los miembros a las tarjetas.
Primero obtiene los miembros del board y luego los asigna.
"""

import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"
BOARD_ID = "5dea6d99c0ea505b4c3a435e"  # Reachu Dev

# IDs de todas las tarjetas creadas
CARD_IDS = [
    "690df9893a3db5cc11835542", "690df98ce9522bba4c64351d", "690df98d7928e825118584a0",
    "690df98ed8907330ae06a7a6", "690df98ff0737ff7aafa67b4", "690df98fe2903bd00a232941",
    "690df990f75c1756a635afec", "690df991b1f430dab2c0edd2", "690df99140a13f6c6c2c5a0c",
    "690df992073c5486b5faf96d", "690df993c8c05c26d9757cd6", "690df996bac4defd7561e1c3",
    "690df996aacaa51018c032b9", "690df9970ada3fc754d483c9", "690df998ee6d9fbe60763e9d",
    "690df9999f31537df86af6fc", "690df99ac182d7c1eecef2de", "690df99a368ac558dd33e20a",
    "690df99be2ae446d6ed3d520", "690df99caad17cd24095a337", "690df99de24358e9c3974d7e",
    "690df9a04323d1f4a8cecffc", "690df9a131eba60b2907ede3", "690df9a1adbb5c2aed5cfd76",
    "690df9a2e6e6076b8b5bd259", "690df9a3cee74ec9b268a1f1", "690df9a40315d439df7120a4",
    "690df9a5fdc97003412dcc4d", "690df9a536ba6108de3cb492", "690df9a665fdbbbd29b9bbd6",
]


def get_board_members():
    """Obtiene todos los miembros del board."""
    url = f"{TRELLO_API_BASE}/boards/{BOARD_ID}/members"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def get_card_members(card_id):
    """Obtiene los miembros asignados a una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}/members"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def add_member_to_card(card_id, member_id):
    """Agrega un miembro a una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}/idMembers"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "value": member_id
    }
    with httpx.Client() as client:
        response = client.post(url, params=params)
        if response.status_code == 200:
            return True
        elif response.status_code == 400:
            # Ya está asignado o error
            return False
        else:
            response.raise_for_status()
            return False


def main():
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados en .env")
        sys.exit(1)
    
    # Obtener miembros del board
    print("🔍 Obteniendo miembros del board...")
    members = get_board_members()
    
    print(f"\n📋 Miembros encontrados en el board:")
    miguel_ids = []
    angelo_id = None
    
    for member in members:
        username = member.get("username", "")
        full_name = member.get("fullName", "")
        member_id = member.get("id", "")
        print(f"   - {full_name} (@{username}) - ID: {member_id}")
        
        # Buscar Miguels y Angelo
        if "miguel" in username.lower() or "miguel" in full_name.lower():
            miguel_ids.append(member_id)
        if "angelo" in username.lower() or "angelo" in full_name.lower():
            angelo_id = member_id
    
    if not miguel_ids:
        print("❌ No se encontraron miembros con 'Miguel' en el nombre")
        sys.exit(1)
    
    if not angelo_id:
        print("❌ No se encontró un miembro con 'Angelo' en el nombre")
        sys.exit(1)
    
    print(f"\n✅ IDs identificados:")
    print(f"   Miguels: {miguel_ids}")
    print(f"   Angelo: {angelo_id}")
    
    # Verificar una tarjeta primero
    print(f"\n🔍 Verificando tarjeta de ejemplo...")
    sample_card = CARD_IDS[0]
    current_members = get_card_members(sample_card)
    print(f"   Miembros actuales en tarjeta {sample_card}:")
    for member in current_members:
        print(f"     - {member.get('fullName', 'N/A')} (@{member.get('username', 'N/A')})")
    
    # Asignar miembros a todas las tarjetas
    print(f"\n📝 Asignando miembros a todas las tarjetas...")
    all_member_ids = miguel_ids + [angelo_id]
    
    success_count = {member_id: 0 for member_id in all_member_ids}
    
    for card_id in CARD_IDS:
        print(f"\n📋 Procesando tarjeta {card_id}...")
        
        for member_id in all_member_ids:
            if add_member_to_card(card_id, member_id):
                success_count[member_id] += 1
                print(f"   ✅ Miembro {member_id} agregado")
            else:
                print(f"   ⚠️  Miembro {member_id} ya estaba asignado o error")
    
    print(f"\n✅ Resumen final:")
    for member_id in all_member_ids:
        member_name = next((m.get("fullName", "Unknown") for m in members if m.get("id") == member_id), "Unknown")
        print(f"   {member_name}: {success_count[member_id]}/{len(CARD_IDS)} tarjetas")


if __name__ == "__main__":
    main()

