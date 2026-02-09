#!/usr/bin/env python3
"""
Mueve tarjetas críticas y de alta prioridad de Backlog a To do.
"""
import os
import sys
import asyncio
import httpx
import re
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BACKLOG_LIST_ID = "6964ed5eeb630c1ed6fcccb0"
TODO_LIST_ID = "6964ed62b23b70bbd5c89432"

async def get_card_details(card_id):
    """Obtiene detalles de una tarjeta."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trello.com/1/cards/{card_id}",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "fields": "id,name,desc"
            }
        )
        if response.status_code == 200:
            return response.json()
        return None

def is_critical_or_high_priority(desc):
    """Verifica si la tarjeta es crítica o de alta prioridad."""
    if not desc:
        return False
    desc_lower = desc.lower()
    return any(keyword in desc_lower for keyword in [
        "prioridad: crítica", "prioridad: critica", "crítica", "critica", "critical",
        "prioridad: alta", "alta", "high priority", "high"
    ])

def is_engagement_related(name, desc):
    """Verifica si está relacionada con Engagement."""
    text = (name + " " + (desc or "")).lower()
    return any(keyword in text for keyword in [
        "engagement", "poll", "contest", "vote", "participat"
    ])

async def move_card_to_todo(card_id, card_name):
    """Mueve una tarjeta a To do."""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://api.trello.com/1/cards/{card_id}",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "idList": TODO_LIST_ID
            }
        )
        return response.status_code == 200

async def main():
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
        sys.exit(1)
    
    print("🔍 Buscando tarjetas críticas y de alta prioridad en Backlog...\n")
    
    # Obtener tarjetas del backlog
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trello.com/1/lists/{BACKLOG_LIST_ID}/cards",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "fields": "id,name,desc"
            }
        )
        if response.status_code != 200:
            print(f"❌ Error obteniendo tarjetas: {response.status_code}")
            sys.exit(1)
        
        backlog_cards = response.json()
    
    print(f"📋 Tarjetas en Backlog: {len(backlog_cards)}\n")
    
    # Filtrar tarjetas que deben moverse
    cards_to_move = []
    
    for card in backlog_cards:
        card_id = card['id']
        card_name = card.get('name', '')
        card_desc = card.get('desc', '')
        
        # Obtener detalles completos
        details = await get_card_details(card_id)
        if details:
            card_desc = details.get('desc', card_desc)
        
        is_critical = is_critical_or_high_priority(card_desc)
        is_engagement = is_engagement_related(card_name, card_desc)
        
        # Mover si es crítica o alta prioridad, especialmente si es de Engagement
        if is_critical or (is_engagement and is_critical_or_high_priority(card_desc)):
            cards_to_move.append({
                'id': card_id,
                'name': card_name,
                'is_critical': 'CRÍTICA' in card_desc.upper() or 'CRITICAL' in card_desc.upper(),
                'is_high': 'ALTA' in card_desc.upper() or 'HIGH' in card_desc.upper(),
                'is_engagement': is_engagement
            })
    
    if not cards_to_move:
        print("✅ No hay tarjetas críticas o de alta prioridad en Backlog que mover")
        return
    
    print(f"📌 Tarjetas a mover a To do: {len(cards_to_move)}\n")
    
    moved = []
    failed = []
    
    for card in cards_to_move:
        priority_label = "CRÍTICA" if card['is_critical'] else "ALTA"
        engagement_label = " (Engagement)" if card['is_engagement'] else ""
        
        print(f"  📌 {card['name']} [{priority_label}{engagement_label}]")
        
        success = await move_card_to_todo(card['id'], card['name'])
        if success:
            moved.append(card)
            print(f"     ✓ Movida a To do")
        else:
            failed.append(card)
            print(f"     ✗ Error al mover")
        
        await asyncio.sleep(0.3)
    
    print("\n" + "="*80)
    print("RESUMEN")
    print("="*80)
    print(f"\n✅ Movidas exitosamente: {len(moved)}/{len(cards_to_move)}")
    
    if moved:
        print("\n  Tarjetas movidas:")
        for card in moved:
            priority = "CRÍTICA" if card['is_critical'] else "ALTA"
            print(f"    ✓ [{priority}] {card['name']}")
    
    if failed:
        print(f"\n❌ Fallidas: {len(failed)}")
        for card in failed:
            print(f"    ✗ {card['name']}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(main())
