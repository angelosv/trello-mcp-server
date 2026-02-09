#!/usr/bin/env python3
"""
Mueve las tarjetas de Engagement que están completadas de "Doing" a "Done".
"""
import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
DOING_LIST_ID = "6964ed646e48737f0130e775"
DONE_LIST_ID = "6964ed66c5545f6ef2fe9131"

# IDs de las tarjetas de Engagement que están en Doing
ENGAGEMENT_CARDS_IN_DOING = [
    "6985d70f6d8ec90b6ac92f08",  # Crear módulo ReachuEngagementSystem - Estructura base
    "6985d71dcaab734da72ac465",  # Implementar EngagementManager - Gestor principal de engagement
    "6985d71e92015daae2f86231",  # Implementar VideoSyncManager - Sincronización con video
    "6985d71f215c8e760e6d84db",  # Crear EngagementRepositoryProtocol - Interfaz de repositorio
    "6985d71fba3038569c27e807",  # Implementar BackendEngagementRepository - Repositorio backend
    "6985d7203b7586398525a2ac",  # Implementar DemoEngagementRepository - Repositorio demo
]

async def move_card_to_done(card_id, card_name):
    """Mueve una tarjeta a Done."""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://api.trello.com/1/cards/{card_id}",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "idList": DONE_LIST_ID
            }
        )
        if response.status_code == 200:
            print(f"  ✓ Movida: {card_name}")
            return True
        else:
            print(f"  ✗ Error moviendo {card_name}: {response.status_code} - {response.text}")
            return False

async def get_card_name(card_id):
    """Obtiene el nombre de una tarjeta."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trello.com/1/cards/{card_id}",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "fields": "name"
            }
        )
        if response.status_code == 200:
            return response.json().get("name", "Unknown")
        return "Unknown"

async def main():
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
        sys.exit(1)
    
    print("🔄 Moviendo tarjetas de Engagement de 'Doing' a 'Done'...\n")
    print(f"📋 Tarjetas a mover: {len(ENGAGEMENT_CARDS_IN_DOING)}\n")
    
    moved = []
    failed = []
    
    for card_id in ENGAGEMENT_CARDS_IN_DOING:
        card_name = await get_card_name(card_id)
        print(f"  📌 {card_name}")
        
        success = await move_card_to_done(card_id, card_name)
        if success:
            moved.append(card_name)
        else:
            failed.append(card_name)
        
        # Pequeña pausa para no sobrecargar la API
        await asyncio.sleep(0.3)
    
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    print(f"\n✅ Movidas exitosamente: {len(moved)}/{len(ENGAGEMENT_CARDS_IN_DOING)}")
    
    if moved:
        print("\n  Tarjetas movidas:")
        for name in moved:
            print(f"    ✓ {name}")
    
    if failed:
        print(f"\n❌ Fallidas: {len(failed)}")
        for name in failed:
            print(f"    ✗ {name}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(main())
