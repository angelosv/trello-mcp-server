"""
Herramientas para revisar y actualizar tarjetas existentes basándose en commits recientes.
"""

import logging
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from mcp.server.fastmcp import Context

from server.models import TrelloCard
from server.services.card import CardService
from server.trello import client
from server.utils.code_analyzer import (
    analyze_commit_for_kotlin,
    get_recent_commits_analysis,
    run_git_command
)

logger = logging.getLogger(__name__)

service = CardService(client)


def extract_commit_hash_from_card(card: TrelloCard) -> Optional[str]:
    """
    Extrae el hash del commit de la descripción de una tarjeta.
    
    Args:
        card: Tarjeta de Trello
        
    Returns:
        Hash del commit si se encuentra, None en caso contrario
    """
    if not card.desc:
        return None
    
    # Buscar patrón: **Commit:** `hash`
    pattern = r'\*\*Commit:\*\*\s*`([a-f0-9]{8,40})`'
    match = re.search(pattern, card.desc)
    
    if match:
        return match.group(1)
    
    # Buscar patrón alternativo: Commit: hash
    pattern2 = r'Commit[:\s]+([a-f0-9]{8,40})'
    match2 = re.search(pattern2, card.desc, re.IGNORECASE)
    
    if match2:
        return match2.group(1)
    
    return None


def get_card_commit_date(card: TrelloCard) -> Optional[str]:
    """
    Extrae la fecha del commit de la descripción de una tarjeta.
    
    Args:
        card: Tarjeta de Trello
        
    Returns:
        Fecha del commit si se encuentra, None en caso contrario
    """
    if not card.desc:
        return None
    
    # Buscar patrón: **Fecha:** fecha
    pattern = r'\*\*Fecha:\*\*\s*([0-9]{4}-[0-9]{2}-[0-9]{2})'
    match = re.search(pattern, card.desc)
    
    if match:
        return match.group(1)
    
    return None


async def review_cards_for_updates(
    ctx: Context,
    list_id: str,
    since: str = "today",
) -> Dict:
    """
    Revisa las tarjetas existentes y determina cuáles necesitan actualizarse
    basándose en commits recientes.
    
    Args:
        list_id: ID de la lista donde buscar tarjetas
        since: Fecha desde la cual analizar commits (ej: "today", "yesterday")
        
    Returns:
        Diccionario con tarjetas que necesitan actualización y commits nuevos
    """
    try:
        logger.info(f"Revisando tarjetas en lista {list_id} para actualizaciones desde {since}")
        
        # Obtener todas las tarjetas de la lista
        cards = await service.get_cards(list_id)
        logger.info(f"Encontradas {len(cards)} tarjetas en la lista")
        
        # Obtener commits recientes relevantes
        relevant_commits = get_recent_commits_analysis(since)
        logger.info(f"Encontrados {len(relevant_commits)} commits relevantes desde {since}")
        
        # Crear mapa de commits por hash
        commits_by_hash = {}
        for commit_analysis in relevant_commits:
            commit_hash = commit_analysis.get('commit', {}).get('hash', '')
            if commit_hash:
                commits_by_hash[commit_hash[:8]] = commit_analysis
                commits_by_hash[commit_hash] = commit_analysis
        
        # Analizar cada tarjeta
        cards_to_update = []
        cards_up_to_date = []
        new_commits_without_cards = []
        
        # Crear set de commits que ya tienen tarjeta
        commits_with_cards = set()
        
        for card in cards:
            commit_hash = extract_commit_hash_from_card(card)
            
            if commit_hash:
                # Normalizar hash (puede ser corto o largo)
                hash_short = commit_hash[:8] if len(commit_hash) >= 8 else commit_hash
                hash_full = commit_hash if len(commit_hash) == 40 else None
                
                commits_with_cards.add(hash_short)
                if hash_full:
                    commits_with_cards.add(hash_full)
                
                # Verificar si el commit tiene cambios nuevos
                if hash_short in commits_by_hash or (hash_full and hash_full in commits_by_hash):
                    # Verificar si hay cambios nuevos desde que se creó la tarjeta
                    card_date = get_card_commit_date(card)
                    commit_analysis = commits_by_hash.get(hash_short) or commits_by_hash.get(hash_full)
                    
                    if commit_analysis:
                        commit_date = commit_analysis.get('commit', {}).get('date', '')
                        
                        # Si la tarjeta es más antigua que el commit, puede necesitar actualización
                        # Pero por ahora, solo marcamos si hay commits nuevos relacionados
                        cards_to_update.append({
                            'card': card,
                            'commit_hash': commit_hash,
                            'reason': 'Commit tiene cambios recientes relacionados'
                        })
                    else:
                        cards_up_to_date.append({
                            'card': card,
                            'commit_hash': commit_hash,
                            'reason': 'Tarjeta está actualizada'
                        })
                else:
                    cards_up_to_date.append({
                        'card': card,
                        'commit_hash': commit_hash,
                        'reason': 'Commit no tiene cambios recientes'
                    })
            else:
                # Tarjeta sin commit asociado - puede ser manual
                cards_up_to_date.append({
                    'card': card,
                    'commit_hash': None,
                    'reason': 'Tarjeta sin commit asociado'
                })
        
        # Encontrar commits nuevos sin tarjeta
        for commit_analysis in relevant_commits:
            commit_hash = commit_analysis.get('commit', {}).get('hash', '')
            if commit_hash:
                hash_short = commit_hash[:8]
                hash_full = commit_hash
                
                if hash_short not in commits_with_cards and hash_full not in commits_with_cards:
                    new_commits_without_cards.append(commit_analysis)
        
        result = {
            'cards_to_update': cards_to_update,
            'cards_up_to_date': cards_up_to_date,
            'new_commits_without_cards': new_commits_without_cards,
            'summary': {
                'total_cards': len(cards),
                'cards_to_update': len(cards_to_update),
                'cards_up_to_date': len(cards_up_to_date),
                'new_commits': len(new_commits_without_cards)
            }
        }
        
        logger.info(f"Revisión completada: {len(cards_to_update)} tarjetas a actualizar, "
                   f"{len(new_commits_without_cards)} commits nuevos sin tarjeta")
        
        return result
        
    except Exception as e:
        error_msg = f"Error revisando tarjetas: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def get_available_members_for_assignment(
    ctx: Context,
    board_id: str,
) -> List[Dict]:
    """
    Obtiene la lista de miembros disponibles para asignar a tarjetas.
    
    Args:
        board_id: ID del board
        
    Returns:
        Lista de miembros con su información
    """
    try:
        from server.services.board import BoardService
        board_service = BoardService(client)
        
        members = await board_service.get_board_members(board_id)
        
        member_list = []
        for member in members:
            member_list.append({
                'id': member.id,
                'username': getattr(member, 'username', None),
                'fullName': getattr(member, 'fullName', None),
                'initials': getattr(member, 'initials', None)
            })
        
        logger.info(f"Encontrados {len(member_list)} miembros disponibles")
        return member_list
        
    except Exception as e:
        error_msg = f"Error obteniendo miembros: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def suggest_members_for_commit(
    ctx: Context,
    commit_hash: str,
    board_id: str,
) -> List[str]:
    """
    Sugiere miembros para asignar basándose en el autor del commit y miembros comunes.
    
    Args:
        commit_hash: Hash del commit
        board_id: ID del board
        
    Returns:
        Lista de IDs de miembros sugeridos
    """
    try:
        # Analizar commit para obtener autor
        analysis = analyze_commit_for_kotlin(commit_hash)
        commit_data = analysis.get('commit', {})
        author_email = commit_data.get('email', '').lower()
        author_name = commit_data.get('author', '').lower()
        
        # Obtener miembros disponibles
        members = await get_available_members_for_assignment(ctx, board_id)
        
        suggested_member_ids = []
        
        # Buscar miembros por email o nombre
        for member in members:
            member_email = (member.get('username', '') or '').lower()
            member_name = (member.get('fullName', '') or '').lower()
            
            # Si el autor coincide con un miembro, sugerirlo
            if author_email and author_email in member_email:
                suggested_member_ids.append(member['id'])
            elif author_name and any(part in member_name for part in author_name.split()):
                suggested_member_ids.append(member['id'])
        
        # Si no hay coincidencias, sugerir miembros comunes de Kotlin
        if not suggested_member_ids:
            # Buscar miembros con nombres comunes (Miguel, Angelo, etc.)
            common_names = ['miguel', 'angelo', 'angello']
            for member in members:
                member_name = (member.get('fullName', '') or '').lower()
                if any(name in member_name for name in common_names):
                    suggested_member_ids.append(member['id'])
                    if len(suggested_member_ids) >= 3:  # Máximo 3 sugerencias
                        break
        
        logger.info(f"Miembros sugeridos para commit {commit_hash[:8]}: {len(suggested_member_ids)}")
        return suggested_member_ids
        
    except Exception as e:
        error_msg = f"Error sugiriendo miembros: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        return []

