"""
Herramienta inteligente para crear tarjetas en Trello después de analizar código.
"""

import logging
from typing import List, Optional

from mcp.server.fastmcp import Context

from server.models import TrelloCard
from server.services.card import CardService
from server.trello import client
from server.utils.code_analyzer import (
    analyze_commit_for_kotlin,
    get_recent_commits_analysis,
    should_create_kotlin_task,
    is_relevant_for_kotlin,
    analyze_file_changes
)
from server.tools.card_review import (
    suggest_members_for_commit,
    get_available_members_for_assignment
)

logger = logging.getLogger(__name__)

service = CardService(client)


async def create_smart_card_from_commit(
    ctx: Context,
    commit_hash: str,
    idList: str,
    idBoard: str,
    idMembers: Optional[str] = None,
    idLabels: Optional[str] = None,
    auto_suggest_members: bool = True,
) -> TrelloCard:
    """
    Analiza un commit y crea una tarjeta en Trello solo si es relevante para Kotlin.
    
    Args:
        commit_hash: Hash del commit a analizar
        idList: ID de la lista donde crear la tarjeta
        idMembers: IDs de miembros (comma-separated)
        idLabels: IDs de labels (comma-separated)
        
    Returns:
        TrelloCard: La tarjeta creada, o None si no era relevante
    """
    try:
        logger.info(f"Analizando commit {commit_hash} para determinar relevancia para Kotlin...")
        
        # Analizar el commit
        analysis = analyze_commit_for_kotlin(commit_hash)
        
        if not analysis.get('relevant', False):
            await ctx.error(f"Commit {commit_hash} no es relevante para Kotlin: {analysis.get('reason', 'Razón desconocida')}")
            raise ValueError(f"Commit no relevante para Kotlin: {analysis.get('reason')}")
        
        commit_data = analysis.get('commit', {})
        relevant_files = analysis.get('relevant_files', [])
        
        # Generar nombre de tarjeta
        commit_message = commit_data.get('message', 'Sin mensaje')
        if len(commit_message) > 60:
            commit_message = commit_message[:57] + "..."
        
        card_name = f"Kotlin -> {commit_message}"
        
        # Generar descripción detallada
        description_parts = [
            f"**Commit:** `{commit_hash[:8]}`",
            f"**Autor:** {commit_data.get('author', 'unknown')}",
            f"**Fecha:** {commit_data.get('date', 'unknown')}",
            "",
            f"**Mensaje:** {commit_data.get('message', 'Sin mensaje')}",
            "",
            "**Archivos relevantes para Kotlin:**",
        ]
        
        for file_info in relevant_files:
            file_path = file_info['path']
            file_analysis = file_info.get('analysis', {})
            change_type = file_analysis.get('change_type', 'unknown')
            diff_summary = file_analysis.get('diff_summary', '')
            
            description_parts.append(f"- `{file_path}` ({change_type}, {diff_summary})")
            
            # Agregar keywords relevantes si existen
            relevant_keywords = file_analysis.get('relevant_keywords', [])
            if relevant_keywords:
                description_parts.append(f"  - Keywords: {', '.join(relevant_keywords)}")
        
        description_parts.extend([
            "",
            "**Análisis:**",
            f"- Archivos relevantes: {len(relevant_files)}",
            f"- Archivos irrelevantes: {len(analysis.get('irrelevant_files', []))}",
            "",
            "**Tareas sugeridas:**",
            "- [ ] Revisar cambios en código Swift",
            "- [ ] Determinar impacto en SDK Kotlin",
            "- [ ] Implementar cambios equivalentes en Kotlin",
            "- [ ] Actualizar documentación si es necesario",
            "- [ ] Probar cambios en demo app",
        ])
        
        description = "\n".join(description_parts)
        
        # Sugerir miembros si no se proporcionaron y auto_suggest está activado
        final_members = idMembers
        if not final_members and auto_suggest_members:
            suggested_members = await suggest_members_for_commit(ctx, commit_hash, idBoard)
            if suggested_members:
                final_members = ",".join(suggested_members)
                logger.info(f"Miembros sugeridos automáticamente: {final_members}")
                # Informar al usuario sobre los miembros sugeridos
                member_names = []
                for member_id in suggested_members:
                    members = await get_available_members_for_assignment(ctx, idBoard)
                    member = next((m for m in members if m['id'] == member_id), None)
                    if member:
                        member_names.append(member.get('fullName', member.get('username', member_id)))
                if member_names:
                    await ctx.info(f"💡 Miembros sugeridos automáticamente: {', '.join(member_names)}")
        
        # Crear payload
        payload_dict = {
            "idList": idList,
            "name": card_name,
            "desc": description,
        }
        
        if final_members:
            payload_dict["idMembers"] = final_members
        if idLabels:
            payload_dict["idLabels"] = idLabels
        
        logger.info(f"Creando tarjeta inteligente: {card_name}")
        result = await service.create_card(**payload_dict)
        logger.info(f"Tarjeta creada exitosamente: {result.id}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error creando tarjeta inteligente: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def create_smart_cards_from_recent_commits(
    ctx: Context,
    idList: str,
    idBoard: str,
    since: str = "today",
    idMembers: Optional[str] = None,
    idLabels: Optional[str] = None,
    dry_run: bool = False,
    auto_suggest_members: bool = True,
) -> List[TrelloCard]:
    """
    Analiza commits recientes y crea tarjetas solo para los relevantes para Kotlin.
    
    Args:
        idList: ID de la lista donde crear las tarjetas
        since: Fecha desde la cual analizar (ej: "today", "yesterday", "7 days ago")
        idMembers: IDs de miembros (comma-separated)
        idLabels: IDs de labels (comma-separated)
        dry_run: Si es True, solo analiza sin crear tarjetas
        
    Returns:
        Lista de tarjetas creadas
    """
    try:
        logger.info(f"Analizando commits desde: {since}")
        
        # Analizar commits recientes
        relevant_commits = get_recent_commits_analysis(since)
        
        if not relevant_commits:
            await ctx.error(f"No se encontraron commits relevantes para Kotlin desde {since}")
            return []
        
        logger.info(f"Encontrados {len(relevant_commits)} commits relevantes para Kotlin")
        
        if dry_run:
            logger.info("Modo dry-run: no se crearán tarjetas")
            return []
        
        created_cards = []
        
        for commit_analysis in relevant_commits:
            commit_hash = commit_analysis.get('commit', {}).get('hash', '')
            
            if not commit_hash:
                continue
            
            try:
                card = await create_smart_card_from_commit(
                    ctx,
                    commit_hash,
                    idList,
                    idBoard,
                    idMembers,
                    idLabels,
                    auto_suggest_members
                )
                created_cards.append(card)
            except ValueError as e:
                # Commit no relevante, continuar con el siguiente
                logger.info(f"Omitiendo commit {commit_hash}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error creando tarjeta para commit {commit_hash}: {str(e)}")
                continue
        
        logger.info(f"Creadas {len(created_cards)} tarjetas exitosamente")
        return created_cards
        
    except Exception as e:
        error_msg = f"Error analizando commits recientes: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise


async def analyze_file_for_kotlin(
    ctx: Context,
    file_path: str,
    commit_hash: Optional[str] = None,
) -> dict:
    """
    Analiza un archivo específico para determinar si es relevante para Kotlin.
    
    Args:
        file_path: Ruta del archivo a analizar
        commit_hash: Hash del commit (opcional, para analizar cambios)
        
    Returns:
        Diccionario con análisis del archivo
    """
    try:
        logger.info(f"Analizando archivo: {file_path}")
        
        # Verificar si es relevante
        if not is_relevant_for_kotlin(file_path):
            return {
                'relevant': False,
                'reason': 'Archivo no está en Sources/ o está excluido'
            }
        
        # Si hay commit_hash, analizar cambios
        if commit_hash:
            analysis = analyze_file_changes(file_path, commit_hash)
            return analysis
        
        # Si no hay commit_hash, solo verificar relevancia básica
        return {
            'relevant': True,
            'reason': 'Archivo en Sources/ y relevante para SDK'
        }
        
    except Exception as e:
        error_msg = f"Error analizando archivo: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

