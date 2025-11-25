"""
Herramienta para revisar código Kotlin implementado y compararlo con los requisitos de la tarjeta.
"""

import logging
import os
import re
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from mcp.server.fastmcp import Context

from server.models import TrelloCard
from server.services.card import CardService
from server.services.list import ListService
from server.trello import client

logger = logging.getLogger(__name__)

card_service = CardService(client)
list_service = ListService(client)

# Rutas del proyecto
KOTLIN_SDK_PATH = "/Users/angelo/Documents/GitHub/ReachuKotlinSDK"
SWIFT_SDK_PATH = "/Users/angelo/ReachuSwiftSDK"
KOTLIN_GUIDE_PATH = "/Users/angelo/ReachuSwiftSDK/KOTLIN_IMPLEMENTATION_GUIDE.md"


def extract_card_requirements(card: TrelloCard) -> Dict[str, any]:
    """
    Extrae los requisitos de la tarjeta analizando su descripción.
    
    Returns:
        Dict con información sobre los requisitos:
        - commit_hash: Hash del commit relacionado
        - files_mentioned: Archivos mencionados en la descripción
        - keywords: Palabras clave relevantes
        - requirements: Lista de requisitos extraídos
    """
    desc = card.desc or ""
    
    # Extraer commit hash si existe
    commit_match = re.search(r'`([a-f0-9]{8,})`', desc)
    commit_hash = commit_match.group(1) if commit_match else None
    
    # Extraer archivos mencionados
    file_pattern = r'`([^`]+\.swift)`|`([^`]+\.kt)`'
    files_mentioned = re.findall(file_pattern, desc)
    files_mentioned = [f[0] or f[1] for f in files_mentioned]
    
    # Extraer keywords relevantes
    keywords = []
    keyword_patterns = [
        r'\*\*([^*]+)\*\*:',  # Secciones en negrita
        r'Keywords?: ([^\n]+)',  # Keywords explícitos
    ]
    for pattern in keyword_patterns:
        matches = re.findall(pattern, desc)
        keywords.extend(matches)
    
    # Extraer requisitos específicos
    requirements = []
    requirement_patterns = [
        r'- \[ \] ([^\n]+)',  # Checkboxes sin marcar
        r'### ([^\n]+)',  # Subtítulos
    ]
    for pattern in requirement_patterns:
        matches = re.findall(pattern, desc)
        requirements.extend(matches)
    
    return {
        'commit_hash': commit_hash,
        'files_mentioned': files_mentioned,
        'keywords': keywords,
        'requirements': requirements,
        'description': desc
    }


def find_kotlin_implementation_files(card: TrelloCard, kotlin_project_path: str) -> List[str]:
    """
    Busca archivos Kotlin relacionados con la tarjeta.
    Busca en todo el proyecto Kotlin de forma general.
    
    Args:
        card: La tarjeta de Trello
        kotlin_project_path: Ruta al proyecto Kotlin
        
    Returns:
        Lista de rutas de archivos Kotlin encontrados
    """
    requirements = extract_card_requirements(card)
    files_found = []
    found_paths = set()  # Para evitar duplicados
    
    # Buscar en todo el proyecto Kotlin (búsqueda general)
    kotlin_path = Path(kotlin_project_path)
    
    if not kotlin_path.exists():
        logger.warning(f"Ruta Kotlin no encontrada: {kotlin_path}")
        return []
    
    # Buscar archivos mencionados en la descripción
    for file_mentioned in requirements['files_mentioned']:
        # Extraer nombre base del archivo Swift
        swift_filename = os.path.basename(file_mentioned)
        kotlin_filename = swift_filename.replace('.swift', '.kt')
        
        # Buscar por nombre exacto en todo el proyecto
        for kotlin_file in kotlin_path.rglob(kotlin_filename):
            file_path = str(kotlin_file)
            if file_path not in found_paths:
                files_found.append(file_path)
                found_paths.add(file_path)
        
        # También buscar por nombre sin extensión (puede haber múltiples archivos relacionados)
        base_name = os.path.splitext(kotlin_filename)[0]
        for kotlin_file in kotlin_path.rglob(f"*{base_name}*.kt"):
            file_path = str(kotlin_file)
            if file_path not in found_paths:
                files_found.append(file_path)
                found_paths.add(file_path)
    
    # Buscar por keywords si no se encontraron archivos
    if not files_found and requirements['keywords']:
        for keyword in requirements['keywords']:
            # Limpiar keyword (remover markdown, espacios, etc.)
            clean_keyword = re.sub(r'[^\w]', '', keyword).strip()
            if len(clean_keyword) < 3:  # Ignorar keywords muy cortos
                continue
            
            # Buscar archivos que contengan el keyword en el nombre en todo el proyecto
            for kotlin_file in kotlin_path.rglob(f"*{clean_keyword}*.kt"):
                file_path = str(kotlin_file)
                if file_path not in found_paths:
                    files_found.append(file_path)
                    found_paths.add(file_path)
    
    # Buscar por nombre de la tarjeta si aún no se encontraron archivos
    if not files_found and card.name:
        # Extraer palabras clave del nombre de la tarjeta
        card_keywords = re.findall(r'\b[A-Z][a-z]+\w+\b', card.name)
        for keyword in card_keywords:
            if len(keyword) < 4:  # Ignorar palabras muy cortas
                continue
            # Buscar en todo el proyecto
            for kotlin_file in kotlin_path.rglob(f"*{keyword}*.kt"):
                file_path = str(kotlin_file)
                if file_path not in found_paths:
                    files_found.append(file_path)
                    found_paths.add(file_path)
    
    return files_found


def analyze_kotlin_code(file_path: str, swift_reference_path: Optional[str] = None) -> Dict[str, any]:
    """
    Analiza un archivo Kotlin y compara con la referencia Swift si está disponible.
    
    Args:
        file_path: Ruta al archivo Kotlin
        swift_reference_path: Ruta al archivo Swift de referencia (opcional)
        
    Returns:
        Dict con análisis del código:
        - has_implementation: Si tiene implementación básica
        - missing_features: Lista de características faltantes
        - code_quality_issues: Problemas de calidad de código
        - suggestions: Sugerencias de mejora
    """
    analysis = {
        'has_implementation': False,
        'missing_features': [],
        'code_quality_issues': [],
        'suggestions': [],
        'file_exists': False
    }
    
    if not os.path.exists(file_path):
        analysis['missing_features'].append(f"Archivo no encontrado: {file_path}")
        return analysis
    
    analysis['file_exists'] = True
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            kotlin_code = f.read()
        
        # Verificar implementación básica
        if len(kotlin_code.strip()) > 100:  # Archivo no vacío
            analysis['has_implementation'] = True
        
        # Buscar características comunes que deberían estar
        if 'class' not in kotlin_code and 'object' not in kotlin_code and 'interface' not in kotlin_code:
            analysis['missing_features'].append("No se encontraron clases, objetos o interfaces definidos")
        
        # Verificar documentación
        if '/**' not in kotlin_code and '//' not in kotlin_code:
            analysis['code_quality_issues'].append("Falta documentación en el código")
        
        # Verificar manejo de errores
        if 'try' not in kotlin_code and 'catch' not in kotlin_code:
            # No es necesariamente un problema, pero puede ser una sugerencia
            if 'suspend' in kotlin_code or 'async' in kotlin_code:
                analysis['suggestions'].append("Considerar agregar manejo de errores para funciones asíncronas")
        
        # Comparar con Swift si está disponible
        if swift_reference_path and os.path.exists(swift_reference_path):
            try:
                with open(swift_reference_path, 'r', encoding='utf-8') as f:
                    swift_code = f.read()
                
                # Comparar funcionalidades básicas
                swift_functions = re.findall(r'func\s+(\w+)', swift_code)
                kotlin_functions = re.findall(r'fun\s+(\w+)', kotlin_code)
                
                missing_functions = set(swift_functions) - set(kotlin_functions)
                if missing_functions:
                    analysis['missing_features'].append(
                        f"Funciones faltantes comparadas con Swift: {', '.join(list(missing_functions)[:5])}"
                    )
            except Exception as e:
                logger.warning(f"Error comparando con Swift: {e}")
    
    except Exception as e:
        logger.error(f"Error analizando archivo Kotlin {file_path}: {e}")
        analysis['code_quality_issues'].append(f"Error al leer el archivo: {str(e)}")
    
    return analysis


def generate_review_feedback(
    card: TrelloCard,
    kotlin_files: List[str],
    analyses: List[Dict[str, any]]
) -> Tuple[str, bool]:
    """
    Genera feedback basado en el análisis del código.
    
    Args:
        card: La tarjeta de Trello
        kotlin_files: Lista de archivos Kotlin encontrados
        analyses: Lista de análisis de cada archivo
        
    Returns:
        Tuple con (feedback_text, has_issues)
    """
    requirements = extract_card_requirements(card)
    
    feedback_parts = []
    has_issues = False
    
    # Encabezado
    feedback_parts.append("## 📝 Revisión de Código Kotlin\n")
    feedback_parts.append(f"**Tarjeta:** {card.name}\n")
    
    # Verificar si se encontraron archivos
    if not kotlin_files:
        feedback_parts.append("### ⚠️ Archivos no encontrados\n")
        feedback_parts.append("No se encontraron archivos Kotlin relacionados con esta tarjeta.\n")
        feedback_parts.append(f"**Archivos esperados (basados en la descripción):**")
        for file_mentioned in requirements['files_mentioned']:
            kotlin_name = file_mentioned.replace('.swift', '.kt')
            feedback_parts.append(f"- `{kotlin_name}`")
        has_issues = True
    else:
        feedback_parts.append(f"### ✅ Archivos encontrados: {len(kotlin_files)}\n")
        for file_path in kotlin_files:
            feedback_parts.append(f"- `{file_path}`")
        feedback_parts.append("")
    
    # Analizar cada archivo
    for i, (file_path, analysis) in enumerate(zip(kotlin_files, analyses)):
        feedback_parts.append(f"### 📄 Análisis: `{os.path.basename(file_path)}`\n")
        
        if not analysis['file_exists']:
            feedback_parts.append("❌ **Archivo no existe**\n")
            has_issues = True
        elif not analysis['has_implementation']:
            feedback_parts.append("⚠️ **Implementación incompleta**\n")
            feedback_parts.append("El archivo existe pero parece estar vacío o incompleto.\n")
            has_issues = True
        else:
            feedback_parts.append("✅ **Implementación encontrada**\n")
        
        # Problemas encontrados
        if analysis['missing_features']:
            feedback_parts.append("**Características faltantes:**")
            for feature in analysis['missing_features']:
                feedback_parts.append(f"- ❌ {feature}")
            has_issues = True
        
        if analysis['code_quality_issues']:
            feedback_parts.append("**Problemas de calidad:**")
            for issue in analysis['code_quality_issues']:
                feedback_parts.append(f"- ⚠️ {issue}")
            has_issues = True
        
        if analysis['suggestions']:
            feedback_parts.append("**Sugerencias:**")
            for suggestion in analysis['suggestions']:
                feedback_parts.append(f"- 💡 {suggestion}")
        
        feedback_parts.append("")
    
    # Resumen
    feedback_parts.append("### 📊 Resumen\n")
    if has_issues:
        feedback_parts.append("❌ **Se encontraron problemas que requieren atención.**\n")
        feedback_parts.append("Por favor, revisa los puntos mencionados arriba y corrige los problemas antes de marcar como completado.\n")
    else:
        feedback_parts.append("✅ **Implementación parece correcta.**\n")
        feedback_parts.append("El código implementado cumple con los requisitos básicos de la tarjeta.\n")
    
    feedback_text = "\n".join(feedback_parts)
    return feedback_text, has_issues


async def find_doing_list(board_id: str) -> Optional[str]:
    """
    Busca la lista "Doing" en el board.
    
    Args:
        board_id: ID del board
        
    Returns:
        ID de la lista "Doing" o None si no se encuentra
    """
    try:
        lists = await list_service.get_lists(board_id)
        for list_item in lists:
            if list_item.name.lower() in ['doing', 'en progreso', 'in progress']:
                return list_item.id
        return None
    except Exception as e:
        logger.error(f"Error buscando lista Doing: {e}")
        return None


async def review_kotlin_implementation(
    ctx: Context,
    card_id: str,
    kotlin_project_path: Optional[str] = None,
    board_id: Optional[str] = None,
    move_to_doing_if_issues: bool = True,
) -> Dict[str, any]:
    """
    Revisa la implementación Kotlin de una tarjeta y agrega feedback como comentario.
    
    Args:
        card_id: ID de la tarjeta de Trello
        kotlin_project_path: Ruta al proyecto Kotlin
        board_id: ID del board (necesario para mover la tarjeta)
        move_to_doing_if_issues: Si mover la tarjeta a "Doing" si hay problemas
        
    Returns:
        Dict con el resultado de la revisión
    """
    try:
        logger.info(f"Revisando implementación Kotlin para tarjeta {card_id}...")
        
        # Usar ruta por defecto si no se especificó
        if kotlin_project_path is None:
            kotlin_project_path = KOTLIN_SDK_PATH
        
        # Obtener la tarjeta
        card = await card_service.get_card(card_id)
        
        # Extraer requisitos
        requirements = extract_card_requirements(card)
        
        # Buscar archivos Kotlin relacionados
        kotlin_files = find_kotlin_implementation_files(card, kotlin_project_path)
        
        # Analizar cada archivo
        analyses = []
        for file_path in kotlin_files:
            # Buscar archivo Swift de referencia si existe commit hash
            swift_reference = None
            if requirements['commit_hash']:
                # Intentar encontrar archivo Swift relacionado
                for file_mentioned in requirements['files_mentioned']:
                    swift_path = os.path.join(SWIFT_SDK_PATH, file_mentioned)
                    if os.path.exists(swift_path):
                        swift_reference = swift_path
                        break
            
            analysis = analyze_kotlin_code(file_path, swift_reference)
            analyses.append(analysis)
        
        # Si no se encontraron archivos, crear análisis vacío
        if not kotlin_files:
            analyses.append({
                'has_implementation': False,
                'missing_features': [],
                'code_quality_issues': [],
                'suggestions': [],
                'file_exists': False
            })
        
        # Generar feedback
        feedback_text, has_issues = generate_review_feedback(card, kotlin_files, analyses)
        
        # Agregar comentario a la tarjeta
        try:
            await card_service.add_comment_to_card(card_id, feedback_text)
            logger.info(f"Comentario agregado a la tarjeta {card_id}")
        except Exception as e:
            logger.error(f"Error agregando comentario: {e}")
            await ctx.error(f"Error agregando comentario: {str(e)}")
        
        # Mover a "Doing" si hay problemas
        if has_issues and move_to_doing_if_issues and board_id:
            try:
                doing_list_id = await find_doing_list(board_id)
                if doing_list_id:
                    await card_service.update_card(card_id, idList=doing_list_id)
                    logger.info(f"Tarjeta {card_id} movida a Doing debido a problemas encontrados")
                else:
                    logger.warning("No se encontró lista 'Doing' para mover la tarjeta")
            except Exception as e:
                logger.error(f"Error moviendo tarjeta a Doing: {e}")
        
        return {
            'card_id': card_id,
            'card_name': card.name,
            'files_found': len(kotlin_files),
            'has_issues': has_issues,
            'feedback_added': True,
            'moved_to_doing': has_issues and move_to_doing_if_issues and board_id is not None,
            'files_analyzed': kotlin_files
        }
    
    except Exception as e:
        error_msg = f"Error revisando implementación: {str(e)}"
        logger.error(error_msg)
        await ctx.error(error_msg)
        raise

