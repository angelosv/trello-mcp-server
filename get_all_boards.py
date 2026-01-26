#!/usr/bin/env python3
"""Obtener todas las boards usando el servicio directamente"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.services.board import BoardService
from server.utils.trello_api import TrelloClient

load_dotenv()

async def get_all_boards():
    """Obtiene todas las boards"""
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    
    if not api_key or not token:
        print("❌ Error: Credenciales no configuradas")
        return
    
    client = TrelloClient(api_key=api_key, token=token)
    service = BoardService(client)
    
    try:
        print("📋 Obteniendo todas las boards de Trello...\n")
        boards = await service.get_boards()
        
        if not boards:
            print("No se encontraron boards.")
            return
        
        print(f"✅ Encontradas {len(boards)} boards:\n")
        print("=" * 100)
        
        for i, board in enumerate(boards, 1):
            print(f"\n{i}. {board.name}")
            print(f"   ID: {board.id}")
            if board.desc:
                desc = board.desc[:80] + "..." if len(board.desc) > 80 else board.desc
                print(f"   Descripción: {desc}")
            print(f"   URL: {board.url}")
            if board.closed:
                print(f"   Estado: ❌ Archivado")
            else:
                print(f"   Estado: ✅ Activo")
            if board.idOrganization:
                print(f"   Organización ID: {board.idOrganization}")
        
        print("\n" + "=" * 100)
        print(f"\n📊 Total: {len(boards)} boards")
        
        # También mostrar IDs para uso fácil
        print("\n📝 IDs de boards (para usar en herramientas):")
        for board in boards:
            print(f"   - {board.name}: {board.id}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(get_all_boards())
