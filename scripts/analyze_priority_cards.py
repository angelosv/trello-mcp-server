#!/usr/bin/env python3
"""
Analiza las tarjetas en To do y Backlog para recomendar cuáles tomar esta semana.
"""
import os
import sys
import asyncio
import httpx
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TODO_LIST_ID = "6964ed62b23b70bbd5c89432"
BACKLOG_LIST_ID = "6964ed5eeb630c1ed6fcccb0"

async def get_card_details(card_id):
    """Obtiene detalles completos de una tarjeta."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trello.com/1/cards/{card_id}",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "fields": "id,name,desc,idLabels,dateLastActivity,url"
            }
        )
        if response.status_code == 200:
            return response.json()
        return None

async def get_label_names(label_ids, board_id):
    """Obtiene los nombres de los labels."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trello.com/1/boards/{board_id}/labels",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN
            }
        )
        if response.status_code == 200:
            labels = response.json()
            label_map = {l['id']: l.get('name', l.get('color', '')) for l in labels}
            return [label_map.get(lid, 'Unknown') for lid in label_ids]
        return []

async def get_list_cards(list_id, list_name):
    """Obtiene todas las tarjetas de una lista."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trello.com/1/lists/{list_id}/cards",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "fields": "id,name,desc,idLabels,dateLastActivity,url"
            }
        )
        if response.status_code == 200:
            return response.json()
        return []

def extract_priority(desc):
    """Extrae la prioridad de la descripción."""
    if not desc:
        return "MEDIA"
    
    desc_lower = desc.lower()
    if "prioridad: crítica" in desc_lower or "crítica" in desc_lower or "critical" in desc_lower:
        return "CRÍTICA"
    elif "prioridad: alta" in desc_lower or "alta" in desc_lower or "high" in desc_lower:
        return "ALTA"
    elif "prioridad: media" in desc_lower or "media" in desc_lower or "medium" in desc_lower:
        return "MEDIA"
    elif "prioridad: baja" in desc_lower or "baja" in desc_lower or "low" in desc_lower:
        return "BAJA"
    return "MEDIA"

def extract_estimation(desc):
    """Extrae la estimación de tiempo."""
    if not desc:
        return None
    
    match = re.search(r'estimaci[oó]n[:\*]*\s*(\d+.*?hora)', desc, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def is_engagement_related(name, desc):
    """Verifica si la tarjeta está relacionada con Engagement."""
    text = (name + " " + (desc or "")).lower()
    return any(keyword in text for keyword in [
        "engagement", "poll", "contest", "vote", "participat"
    ])

async def analyze_cards():
    """Analiza las tarjetas y hace recomendaciones."""
    board_id = "6964ea21570279f07def7786"
    
    print("🔍 Analizando tarjetas en 'To do' y 'Backlog'...\n")
    
    # Obtener tarjetas
    todo_cards = await get_list_cards(TODO_LIST_ID, "To do")
    backlog_cards = await get_list_cards(BACKLOG_LIST_ID, "Backlog")
    
    print(f"📋 Tarjetas encontradas:")
    print(f"   - To do: {len(todo_cards)}")
    print(f"   - Backlog: {len(backlog_cards)}")
    print(f"   - Total: {len(todo_cards) + len(backlog_cards)}\n")
    
    # Analizar todas las tarjetas
    all_cards = []
    
    for card in todo_cards:
        labels = await get_label_names(card.get('idLabels', []), board_id)
        priority = extract_priority(card.get('desc', ''))
        estimation = extract_estimation(card.get('desc', ''))
        is_engagement = is_engagement_related(card.get('name', ''), card.get('desc', ''))
        
        all_cards.append({
            'id': card['id'],
            'name': card.get('name', 'Unknown'),
            'desc': card.get('desc', ''),
            'url': card.get('url', ''),
            'list': 'To do',
            'priority': priority,
            'estimation': estimation,
            'labels': labels,
            'is_engagement': is_engagement,
            'last_activity': card.get('dateLastActivity', '')
        })
    
    for card in backlog_cards:
        labels = await get_label_names(card.get('idLabels', []), board_id)
        priority = extract_priority(card.get('desc', ''))
        estimation = extract_estimation(card.get('desc', ''))
        is_engagement = is_engagement_related(card.get('name', ''), card.get('desc', ''))
        
        all_cards.append({
            'id': card['id'],
            'name': card.get('name', 'Unknown'),
            'desc': card.get('desc', ''),
            'url': card.get('url', ''),
            'list': 'Backlog',
            'priority': priority,
            'estimation': estimation,
            'labels': labels,
            'is_engagement': is_engagement,
            'last_activity': card.get('dateLastActivity', '')
        })
    
    # Clasificar por prioridad
    critical_cards = [c for c in all_cards if c['priority'] == 'CRÍTICA']
    high_cards = [c for c in all_cards if c['priority'] == 'ALTA']
    engagement_cards = [c for c in all_cards if c['is_engagement']]
    
    # Recomendaciones
    print("="*80)
    print("RECOMENDACIONES PARA ESTA SEMANA")
    print("="*80)
    
    print("\n🎯 PRIORIDAD 1: Tarjetas CRÍTICAS de Engagement")
    print("   (Estas son fundamentales para completar el módulo Engagement)\n")
    
    critical_engagement = [c for c in critical_cards if c['is_engagement']]
    if critical_engagement:
        for i, card in enumerate(critical_engagement[:5], 1):
            print(f"   {i}. {card['name']}")
            print(f"      Lista: {card['list']}")
            print(f"      Estimación: {card['estimation'] or 'No especificada'}")
            print(f"      Labels: {', '.join(card['labels']) if card['labels'] else 'ninguno'}")
            print(f"      URL: {card['url']}")
            print()
    else:
        print("   No hay tarjetas críticas de Engagement pendientes")
    
    print("\n🎯 PRIORIDAD 2: Otras tarjetas CRÍTICAS")
    print("   (Importantes para el SDK en general)\n")
    
    other_critical = [c for c in critical_cards if not c['is_engagement']]
    if other_critical:
        for i, card in enumerate(other_critical[:3], 1):
            print(f"   {i}. {card['name']}")
            print(f"      Lista: {card['list']}")
            print(f"      Estimación: {card['estimation'] or 'No especificada'}")
            print(f"      URL: {card['url']}")
            print()
    else:
        print("   No hay otras tarjetas críticas pendientes")
    
    print("\n🎯 PRIORIDAD 3: Tarjetas de Engagement (ALTA/MEDIA)")
    print("   (Para completar funcionalidades de Engagement)\n")
    
    other_engagement = [c for c in engagement_cards if c['priority'] in ['ALTA', 'MEDIA']]
    if other_engagement:
        for i, card in enumerate(other_engagement[:3], 1):
            print(f"   {i}. {card['name']}")
            print(f"      Prioridad: {card['priority']}")
            print(f"      Lista: {card['list']}")
            print(f"      Estimación: {card['estimation'] or 'No especificada'}")
            print(f"      URL: {card['url']}")
            print()
    else:
        print("   No hay otras tarjetas de Engagement pendientes")
    
    # Resumen
    print("="*80)
    print("RESUMEN DE RECOMENDACIONES")
    print("="*80)
    
    recommended = critical_engagement[:5] + other_critical[:3] + other_engagement[:3]
    
    print(f"\n📊 Total de tarjetas recomendadas: {len(recommended)}")
    print(f"   - Críticas de Engagement: {len(critical_engagement[:5])}")
    print(f"   - Otras críticas: {len(other_critical[:3])}")
    print(f"   - Engagement (alta/media): {len(other_engagement[:3])}")
    
    print(f"\n💡 Estrategia sugerida:")
    print(f"   1. Comenzar con las tarjetas críticas de Engagement (son el bloqueo principal)")
    print(f"   2. Luego las otras críticas si hay tiempo")
    print(f"   3. Finalmente completar Engagement con las de prioridad alta/media")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(analyze_cards())
