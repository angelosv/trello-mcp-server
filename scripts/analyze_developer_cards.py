#!/usr/bin/env python3
"""
Analiza las tarjetas que el desarrollador movió usando las herramientas MCP de Trello.
Este script está diseñado para usar las herramientas MCP directamente cuando estén disponibles.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Intentar importar las herramientas MCP
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
    from server.trello import client
    from server.services.list import ListService
    from server.services.card import CardService
    from server.services.checklist import ChecklistService
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  No se pudieron importar las herramientas MCP: {e}")
    MCP_AVAILABLE = False

BOARD_ID = "6964ea21570279f07def7786"

# IDs de tarjetas de Engagement que creamos
ENGAGEMENT_CARDS = {
    "6985f75601b379d47f292a75": "Testing: Engagement Backend Improvements",
    "6985f758865df376c0242f49": "Backend: Actualizar API para aceptar API key en headers",
    "6985f764ed6ed5c45d95c077": "Monitoring: Revisar métricas de EngagementRequestMetrics",
    "6985f76407e65cc885c91b89": "Documentación: Engagement Backend Improvements",
}

async def analyze_cards():
    """Analiza las tarjetas usando las herramientas MCP."""
    if not MCP_AVAILABLE:
        print("❌ Las herramientas MCP no están disponibles.")
        print("   Verifica que el servidor MCP esté corriendo y configurado correctamente.")
        return
    
    card_service = CardService(client)
    checklist_service = ChecklistService(client)
    
    try:
        # Obtener todas las listas del board (incluyendo archivadas)
        print("🔍 Obteniendo listas del board...")
        # Usar la API directamente para obtener todas las listas incluyendo archivadas
        import httpx
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(
                f"https://api.trello.com/1/boards/{BOARD_ID}/lists/all",
                params={
                    "key": os.getenv("TRELLO_API_KEY"),
                    "token": os.getenv("TRELLO_TOKEN"),
                    "fields": "id,name,closed"
                }
            )
            response.raise_for_status()
            lists_data = response.json()
        
        # Convertir a objetos similares a TrelloList para compatibilidad
        class SimpleList:
            def __init__(self, id, name, closed=False):
                self.id = id
                self.name = name
                self.closed = closed
        
        lists = [SimpleList(lst['id'], lst['name'], lst.get('closed', False)) for lst in lists_data]
        
        # Crear mapa de listas
        list_map = {lst.id: lst.name for lst in lists}
        
        print(f"\n📋 Listas encontradas ({len(lists)}):")
        for lst in lists:
            print(f"  - {lst.name}: {lst.id}")
        
        # Analizar cada tarjeta de Engagement
        print(f"\n📊 Analizando {len(ENGAGEMENT_CARDS)} tarjetas de Engagement...\n")
        
        cards_analysis = []
        
        for card_id, card_name in ENGAGEMENT_CARDS.items():
            try:
                print(f"  📌 Analizando: {card_name}")
                card = await card_service.get_card(card_id)
                
                # Obtener nombre de lista
                list_name = list_map.get(card.idList, "Unknown")
                
                # Obtener checklists
                checklists = await checklist_service.get_card_checklists(card_id)
                checklist_items_count = sum(len(cl.get('checkItems', [])) for cl in checklists)
                
                cards_analysis.append({
                    'id': card_id,
                    'name': card.name,
                    'list_name': list_name,
                    'list_id': card.idList,
                    'url': card.url,
                    'checklists_count': len(checklists),
                    'checklist_items': checklist_items_count,
                    'members': card.idMembers if hasattr(card, 'idMembers') else [],
                    'labels': card.idLabels if hasattr(card, 'idLabels') else [],
                })
                
                print(f"     ✓ Lista: {list_name}")
                print(f"     ✓ Checklists: {len(checklists)} ({checklist_items_count} items)")
                print()
                
            except Exception as e:
                print(f"     ❌ Error: {e}\n")
                continue
        
        # Organizar por lista
        backlog_cards = [c for c in cards_analysis if 'backlog' in c['list_name'].lower()]
        todo_cards = [c for c in cards_analysis if 'to do' in c['list_name'].lower() or 'todo' in c['list_name'].lower()]
        other_cards = [c for c in cards_analysis if c not in backlog_cards and c not in todo_cards]
        
        # Mostrar análisis
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
                print(f"     Checklists: {card['checklists_count']} ({card['checklist_items']} items)")
                print()
        
        if backlog_cards:
            print(f"\n📦 TARJETAS EN 'Backlog' ({len(backlog_cards)} tarjetas):")
            print("   (Estas aún no han sido movidas)\n")
            for card in backlog_cards:
                print(f"  📌 {card['name']}")
                print(f"     Lista: {card['list_name']}")
                print(f"     URL: {card['url']}")
                print()
        
        if other_cards:
            print(f"\n📍 TARJETAS EN OTRAS LISTAS ({len(other_cards)} tarjetas):")
            for card in other_cards:
                print(f"  📌 {card['name']} - {card['list_name']}")
                print(f"     URL: {card['url']}")
                print()
        
        # Resumen
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
        else:
            print("\n⚠️  No hay tarjetas en 'To do' aún")
            print("   El desarrollador aún no ha movido tarjetas del Backlog")
        
        if backlog_cards:
            print(f"\n📦 Quedan {len(backlog_cards)} tarjeta(s) en 'Backlog':")
            for card in backlog_cards:
                print(f"   - {card['name']}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("⚠️  Las herramientas MCP no están disponibles.")
        print("   Este script requiere que el servidor MCP esté configurado y corriendo.")
        print("   Verifica:")
        print("   1. Que las credenciales en .env sean válidas")
        print("   2. Que el servidor MCP esté corriendo")
        print("   3. Que las herramientas MCP estén disponibles en Cursor")
        sys.exit(1)
    
    asyncio.run(analyze_cards())
