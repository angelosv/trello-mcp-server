#!/usr/bin/env python3
"""
Actualiza las descripciones de tarjetas para reflejar el estado real.
"""
import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")

# Tarjeta: Crear modelos EngagementModels
MODELS_CARD_ID = "6985d72109107f0667740b4f"
MODELS_DESC = """**Prioridad: CRÍTICA** - Modelos de datos fundamentales para el sistema de engagement.

## Estado Actual
✅ Los modelos YA ESTÁN IMPLEMENTADOS en los commits (4050dda, 13c3681, b7704f1)
- Commit: 4050dda - Implementar DemoEngagementRepository
- Archivo: library/io/reachu/ReachuEngagementSystem/models/EngagementModels.kt
- Los modelos incluyen: Poll, Contest, PollOption, PollResults, PollOptionResults, ContestType, EngagementError

## Tarea Real
1. Verificar que los modelos estén en origin/main
2. Traer los cambios a la rama local (full-migration o la que corresponda)
3. Verificar que compilen correctamente
4. Comparar con Swift SDK para asegurar compatibilidad
5. Verificar backward compatibility con matchId/matchStartTime si es necesario

## Modelos Implementados (verificar)
- Poll: id, broadcastId, question, options, startTime, endTime, videoStartTime, videoEndTime, broadcastStartTime, isActive, totalVotes, broadcastContext
- PollOption: id, text, voteCount, percentage
- Contest: id, broadcastId, title, description, prize, contestType, startTime, endTime, videoStartTime, videoEndTime, broadcastStartTime, isActive, broadcastContext
- ContestType: quiz, giveaway
- PollResults: pollId, totalVotes, options
- PollOptionResults: optionId, voteCount, percentage
- EngagementError: sealed class con todos los casos de error

## Referencias
- Commits: git show 4050dda:library/io/reachu/ReachuEngagementSystem/models/EngagementModels.kt
- Swift SDK: /Users/angelo/ReachuSwiftSDK/Sources/ReachuEngagementSystem/Models/EngagementModels.swift

## Notas
- Los modelos usan String para fechas (no Date) - verificar si esto es correcto
- EngagementError está incluido en el mismo archivo (no necesita archivo separado)
- Verificar serialización con kotlinx.serialization"""

# Tarjeta: Crear EngagementError
ERROR_CARD_ID = "6985d72295507d7dda6be262"
ERROR_DESC = """**Prioridad: CRÍTICA** - Errores específicos del sistema de engagement.

## Estado Actual
✅ EngagementError YA ESTÁ IMPLEMENTADO en los commits
- Commit: 4050dda - Implementar DemoEngagementRepository
- Archivo: library/io/reachu/ReachuEngagementSystem/models/EngagementModels.kt (líneas 67-85)
- Está incluido en el mismo archivo que los modelos (no necesita archivo separado)

## Implementación Actual
EngagementError está implementado como sealed class con todos los casos requeridos:
- PollNotFound
- ContestNotFound
- PollClosed
- AlreadyVoted
- VoteFailed
- ParticipationFailed
- InvalidURL

## Tarea Real
1. Verificar que EngagementError esté en origin/main
2. Traer los cambios a la rama local
3. Verificar que compile correctamente
4. Comparar con Swift SDK para asegurar que todos los casos de error están cubiertos
5. Verificar que los mensajes de error sean apropiados

## Referencias
- Commit: git show 4050dda:library/io/reachu/ReachuEngagementSystem/models/EngagementModels.kt
- Swift SDK: /Users/angelo/ReachuSwiftSDK/Sources/ReachuEngagementSystem/Managers/EngagementManager.swift (líneas 279-308)

## Notas
- EngagementError está en EngagementModels.kt junto con los modelos
- Usa sealed class para mejor manejo de errores con pattern matching
- Todos los casos de error requeridos están implementados"""

async def update_card_desc(card_id, desc):
    """Actualiza la descripción de una tarjeta."""
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"https://api.trello.com/1/cards/{card_id}",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "desc": desc
            }
        )
        return response.status_code == 200

async def main():
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
        sys.exit(1)
    
    print("📝 Actualizando descripciones de tarjetas...\n")
    
    # Actualizar tarjeta de modelos
    print("1. Actualizando: Crear modelos EngagementModels")
    success1 = await update_card_desc(MODELS_CARD_ID, MODELS_DESC)
    print(f"   {'✓ Actualizada' if success1 else '✗ Error'}\n")
    
    # Actualizar tarjeta de errores
    print("2. Actualizando: Crear EngagementError")
    success2 = await update_card_desc(ERROR_CARD_ID, ERROR_DESC)
    print(f"   {'✓ Actualizada' if success2 else '✗ Error'}\n")
    
    print("="*80)
    print("RESUMEN")
    print("="*80)
    print(f"\n✅ Tarjetas actualizadas: {sum([success1, success2])}/2")
    
    if success1 and success2:
        print("\n✓ Ambas tarjetas actualizadas correctamente")
        print("  Las descripciones ahora reflejan que los modelos y errores ya están implementados")
        print("  La tarea real es traerlos a la rama local y verificar que funcionen")

if __name__ == "__main__":
    asyncio.run(main())
