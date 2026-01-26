#!/usr/bin/env python3
"""Script simple para listar los boards de Trello"""

import asyncio
import os
from dotenv import load_dotenv
from server.services.board import BoardService
from server.utils.trello_api import TrelloClient

load_dotenv()

async def list_boards():
    """Lista todos los boards de Trello"""
    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")
    
    if not api_key or not token:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados en .env")
        return
    
    client = TrelloClient(api_key=api_key, token=token)
    service = BoardService(client)
    
    try:
        print("📋 Obteniendo boards de Trello...\n")
        boards = await service.get_boards()
        
        if not boards:
            print("No se encontraron boards.")
            return
        
        print(f"✅ Encontrados {len(boards)} boards:\n")
        print("-" * 80)
        
        for i, board in enumerate(boards, 1):
            print(f"\n{i}. {board.name}")
            print(f"   ID: {board.id}")
            if board.desc:
                desc = board.desc[:60] + "..." if len(board.desc) > 60 else board.desc
                print(f"   Descripción: {desc}")
            print(f"   URL: {board.url}")
            if board.closed:
                print(f"   Estado: ❌ Archivado")
            else:
                print(f"   Estado: ✅ Activo")
        
        print("\n" + "-" * 80)
        print(f"\nTotal: {len(boards)} boards")
        
    except Exception as e:
        print(f"❌ Error al obtener boards: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(list_boards())
