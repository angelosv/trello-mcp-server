#!/usr/bin/env python3
"""Test de conexión a Trello API"""

import asyncio
import httpx

async def test():
    api_key = "e582f14026a35a1b1a886d0ba2ad2316"
    token = "5d5b42651955614137c1979774560b56139cf7bc9b530b5435f6bb5fb33cee05"
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                'https://api.trello.com/1/members/me/boards',
                params={'key': api_key, 'token': token}
            )
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                boards = r.json()
                print(f"\n✅ Conexión exitosa! Encontrados {len(boards)} boards:\n")
                for i, board in enumerate(boards[:10], 1):
                    print(f"{i}. {board.get('name', 'Sin nombre')} (ID: {board.get('id', 'N/A')})")
            else:
                print(f"Error: {r.text}")
        except Exception as e:
            print(f"Error de conexión: {e}")

asyncio.run(test())
