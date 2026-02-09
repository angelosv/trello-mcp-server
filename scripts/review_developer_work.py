#!/usr/bin/env python3
"""
Revisa las tarjetas en Done y Doing, obtiene comentarios y analiza el trabajo del desarrollador.
"""
import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
BOARD_ID = "6964ea21570279f07def7786"
DOING_LIST_ID = "6964ed646e48737f0130e775"
DONE_LIST_ID = "6964ed66c5545f6ef2fe9131"

async def get_card_comments(card_id):
    """Obtiene los comentarios de una tarjeta."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trello.com/1/cards/{card_id}/actions",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "filter": "commentCard",
                "fields": "data,date,memberCreator"
            }
        )
        response.raise_for_status()
        return response.json()

async def get_card_details(card_id):
    """Obtiene detalles completos de una tarjeta."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trello.com/1/cards/{card_id}",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "fields": "id,name,desc,url,dateLastActivity,idMembers,idLabels"
            }
        )
        response.raise_for_status()
        return response.json()

async def get_list_cards(list_id, list_name):
    """Obtiene todas las tarjetas de una lista."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.trello.com/1/lists/{list_id}/cards",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "fields": "id,name,url,dateLastActivity"
            }
        )
        response.raise_for_status()
        cards = response.json()
        
        print(f"\n{'='*80}")
        print(f"📋 TARJETAS EN '{list_name}' ({len(cards)} tarjetas)")
        print(f"{'='*80}\n")
        
        if not cards:
            print(f"   No hay tarjetas en '{list_name}'")
            return []
        
        cards_with_comments = []
        for card in cards:
            card_id = card['id']
            card_name = card['name']
            card_url = card['url']
            last_activity = card.get('dateLastActivity', '')
            
            print(f"  📌 {card_name}")
            print(f"     URL: {card_url}")
            print(f"     Última actividad: {last_activity}")
            
            # Obtener detalles completos
            details = await get_card_details(card_id)
            desc = details.get('desc', '')
            if desc:
                print(f"     Descripción: {desc[:100]}..." if len(desc) > 100 else f"     Descripción: {desc}")
            
            # Obtener comentarios
            comments = await get_card_comments(card_id)
            if comments:
                print(f"     💬 Comentarios ({len(comments)}):")
                for comment in comments:
                    comment_data = comment.get('data', {}).get('text', '')
                    comment_date = comment.get('date', '')
                    member = comment.get('memberCreator', {}).get('fullName', 'Unknown')
                    print(f"        - [{member}] {comment_date}: {comment_data[:150]}..." if len(comment_data) > 150 else f"        - [{member}] {comment_date}: {comment_data}")
                    cards_with_comments.append({
                        'card': card,
                        'comments': comments,
                        'details': details
                    })
            else:
                print(f"     💬 Sin comentarios")
            
            print()
            
            # Pequeña pausa para no sobrecargar la API
            await asyncio.sleep(0.2)
        
        return cards_with_comments

async def main():
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
        sys.exit(1)
    
    print("🔍 Revisando trabajo del desarrollador en Trello...")
    print("   Analizando tarjetas en 'Doing' y 'Done'\n")
    
    # Obtener tarjetas de Doing
    doing_cards = await get_list_cards(DOING_LIST_ID, "Doing")
    
    # Obtener tarjetas de Done
    done_cards = await get_list_cards(DONE_LIST_ID, "Done")
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DEL TRABAJO DEL DESARROLLADOR")
    print("="*80)
    print(f"\n📊 Estadísticas:")
    print(f"   - Tarjetas en 'Doing': {len(doing_cards)}")
    print(f"   - Tarjetas en 'Done': {len(done_cards)}")
    print(f"   - Total: {len(doing_cards) + len(done_cards)}")
    
    if done_cards:
        print(f"\n✅ Tarjetas completadas:")
        for item in done_cards:
            card = item['card']
            comments_count = len(item['comments'])
            print(f"   - {card['name']}")
            if comments_count > 0:
                print(f"     ({comments_count} comentario(s))")
    
    if doing_cards:
        print(f"\n🔄 Tarjetas en progreso:")
        for item in doing_cards:
            card = item['card']
            comments_count = len(item['comments'])
            print(f"   - {card['name']}")
            if comments_count > 0:
                print(f"     ({comments_count} comentario(s))")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(main())
