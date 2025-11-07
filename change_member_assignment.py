#!/usr/bin/env python3
"""
Script para cambiar las asignaciones de las tarjetas al otro Miguel.
"""

import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"

# IDs de los dos Miguels
MIGUEL_1_ID = "619f90698c4fc547cc133149"  # miguelangellopezmonzon
MIGUEL_2_ID = "680a7cb22a55497d4f4223d4"  # miguelangellopezmonzon2

# IDs de todas las tarjetas creadas
CARD_IDS = [
    "690df9893a3db5cc11835542",  # Tarea 1
    "690df98ce9522bba4c64351d",  # Tarea 2
    "690df98d7928e825118584a0",  # Tarea 3
    "690df98ed8907330ae06a7a6",  # Tarea 4
    "690df98ff0737ff7aafa67b4",  # Tarea 5
    "690df98fe2903bd00a232941",  # Tarea 6
    "690df990f75c1756a635afec",  # Tarea 7
    "690df991b1f430dab2c0edd2",  # Tarea 8
    "690df99140a13f6c6c2c5a0c",  # Tarea 9
    "690df992073c5486b5faf96d",  # Tarea 10
    "690df993c8c05c26d9757cd6",  # Tarea 11
    "690df996bac4defd7561e1c3",  # Tarea 12
    "690df996aacaa51018c032b9",  # Tarea 13
    "690df9970ada3fc754d483c9",  # Tarea 14
    "690df998ee6d9fbe60763e9d",  # Tarea 15
    "690df9999f31537df86af6fc",  # Tarea 16
    "690df99ac182d7c1eecef2de",  # Tarea 17
    "690df99a368ac558dd33e20a",  # Tarea 18
    "690df99be2ae446d6ed3d520",  # Tarea 19
    "690df99caad17cd24095a337",  # Tarea 20
    "690df99de24358e9c3974d7e",  # Tarea 21
    "690df9a04323d1f4a8cecffc",  # Tarea 22
    "690df9a131eba60b2907ede3",  # Tarea 23
    "690df9a1adbb5c2aed5cfd76",  # Tarea 24
    "690df9a2e6e6076b8b5bd259",  # Tarea 25
    "690df9a3cee74ec9b268a1f1",  # Tarea 26
    "690df9a40315d439df7120a4",  # Tarea 27
    "690df9a5fdc97003412dcc4d",  # Tarea 28
    "690df9a536ba6108de3cb492",  # Tarea 29
    "690df9a665fdbbbd29b9bbd6",  # Tarea 30
]


async def remove_member_from_card(client: httpx.AsyncClient, card_id: str, member_id: str):
    """Remueve un miembro de una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}/idMembers/{member_id}"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    try:
        response = await client.delete(url, params=params)
        response.raise_for_status()
        print(f"✅ Member {member_id} removido de tarjeta {card_id}")
        return True
    except Exception as e:
        print(f"⚠️  Error removiendo member {member_id} de tarjeta {card_id}: {e}")
        return False


async def add_member_to_card(client: httpx.AsyncClient, card_id: str, member_id: str):
    """Agrega un miembro a una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}/idMembers"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "value": member_id
    }
    try:
        response = await client.put(url, params=params)
        response.raise_for_status()
        print(f"✅ Member {member_id} agregado a tarjeta {card_id}")
        return True
    except Exception as e:
        print(f"❌ Error agregando member {member_id} a tarjeta {card_id}: {e}")
        return False


async def process_cards():
    """Procesa todas las tarjetas cambiando la asignación al otro Miguel."""
    async with httpx.AsyncClient() as client:
        total = len(CARD_IDS)
        success_remove = 0
        success_add = 0
        
        for card_id in CARD_IDS:
            print(f"\n📋 Procesando tarjeta {card_id}...")
            
            # Remover Miguel 1 (si está asignado)
            if await remove_member_from_card(client, card_id, MIGUEL_1_ID):
                success_remove += 1
            await asyncio.sleep(0.2)
            
            # Agregar Miguel 2
            if await add_member_to_card(client, card_id, MIGUEL_2_ID):
                success_add += 1
            await asyncio.sleep(0.2)
        
        print(f"\n✅ Completado!")
        print(f"   Miembros removidos: {success_remove}/{total}")
        print(f"   Miembros agregados: {success_add}/{total}")


if __name__ == "__main__":
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados en .env")
        sys.exit(1)
    
    asyncio.run(process_cards())

