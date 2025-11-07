"""
Análisis inteligente de código para determinar si los cambios son relevantes para Kotlin.
"""

import os
import re
import subprocess
import logging
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Rutas del proyecto
SWIFT_SDK_PATH = "/Users/angelo/ReachuSwiftSDK"
KOTLIN_GUIDE_PATH = "/Users/angelo/ReachuSwiftSDK/KOTLIN_IMPLEMENTATION_GUIDE.md"

# Archivos/carpetas que NO son relevantes para Kotlin
EXCLUDE_PATTERNS = [
    r'\.vscode/',
    r'\.git/',
    r'Demo/',
    r'Tests/',
    r'\.xcodeproj/',
    r'\.xcworkspace/',
    r'Package\.resolved',
    r'\.gitignore',
    r'README\.md',
    r'CHANGELOG\.md',
]

# Componentes que SÍ son relevantes para Kotlin
RELEVANT_PATTERNS = [
    r'Sources/ReachuCore/',
    r'Sources/ReachuUI/',
    r'Sources/ReachuDesignSystem/',
    r'Sources/ReachuNetwork/',
]

# Patrones que indican cambios relevantes para Kotlin
KOTLIN_RELEVANT_KEYWORDS = [
    'public', 'struct', 'class', 'enum', 'func', 'protocol',
    'Configuration', 'Manager', 'Service', 'Component', 'Model',
    'API', 'Network', 'Cache', 'Localization', 'Translation',
]

# Patrones que indican cambios NO relevantes para Kotlin
KOTLIN_IRRELEVANT_KEYWORDS = [
    'import SwiftUI', 'import UIKit', '@State', '@Binding', '@ObservedObject',
    'View', 'PreviewProvider', 'XCTest', 'test', 'Test',
]


def run_git_command(cmd: List[str], cwd: str = SWIFT_SDK_PATH) -> str:
    """Ejecuta un comando git y retorna la salida."""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.warning(f"Error ejecutando git: {e.stderr}")
        return ""


def is_relevant_for_kotlin(file_path: str) -> bool:
    """
    Determina si un archivo es relevante para implementación en Kotlin.
    
    Args:
        file_path: Ruta del archivo
        
    Returns:
        True si es relevante para Kotlin, False en caso contrario
    """
    # Excluir archivos que no son relevantes
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, file_path):
            return False
    
    # Incluir archivos en Sources/ que son parte del SDK
    for pattern in RELEVANT_PATTERNS:
        if re.search(pattern, file_path):
            return True
    
    # Si no está en Sources/, probablemente no es relevante
    if 'Sources/' not in file_path:
        return False
    
    return False


def analyze_file_changes(file_path: str, commit_hash: str) -> Dict:
    """
    Analiza los cambios en un archivo para determinar su relevancia para Kotlin.
    
    Args:
        file_path: Ruta del archivo
        commit_hash: Hash del commit
        
    Returns:
        Diccionario con análisis del archivo
    """
    full_path = os.path.join(SWIFT_SDK_PATH, file_path)
    
    if not os.path.exists(full_path) or not file_path.endswith('.swift'):
        return {
            'relevant': False,
            'reason': 'Archivo no existe o no es Swift'
        }
    
    # Obtener diff del archivo
    diff_output = run_git_command(['show', commit_hash, '--', file_path])
    
    if not diff_output:
        return {
            'relevant': False,
            'reason': 'No hay cambios en este commit'
        }
    
    # Analizar el diff
    added_lines = []
    removed_lines = []
    
    for line in diff_output.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            added_lines.append(line[1:].strip())
        elif line.startswith('-') and not line.startswith('---'):
            removed_lines.append(line[1:].strip())
    
    # Buscar keywords relevantes
    relevant_keywords_found = []
    irrelevant_keywords_found = []
    
    all_changes = '\n'.join(added_lines + removed_lines)
    
    for keyword in KOTLIN_RELEVANT_KEYWORDS:
        if re.search(rf'\b{keyword}\b', all_changes, re.IGNORECASE):
            relevant_keywords_found.append(keyword)
    
    for keyword in KOTLIN_IRRELEVANT_KEYWORDS:
        if re.search(rf'\b{keyword}\b', all_changes, re.IGNORECASE):
            irrelevant_keywords_found.append(keyword)
    
    # Determinar relevancia
    is_relevant = len(relevant_keywords_found) > len(irrelevant_keywords_found)
    
    # Analizar tipo de cambio
    change_type = 'unknown'
    if any('public' in line.lower() for line in added_lines):
        change_type = 'api_change'
    elif any('func' in line.lower() or 'function' in line.lower() for line in added_lines):
        change_type = 'functionality_added'
    elif any('struct' in line.lower() or 'class' in line.lower() for line in added_lines):
        change_type = 'model_added'
    elif len(removed_lines) > len(added_lines) * 2:
        change_type = 'refactor'
    elif len(added_lines) > len(removed_lines) * 2:
        change_type = 'feature_added'
    else:
        change_type = 'modification'
    
    return {
        'relevant': is_relevant,
        'reason': f"Keywords relevantes: {relevant_keywords_found}, Irrelevantes: {irrelevant_keywords_found}",
        'change_type': change_type,
        'added_lines': len(added_lines),
        'removed_lines': len(removed_lines),
        'relevant_keywords': relevant_keywords_found,
        'irrelevant_keywords': irrelevant_keywords_found,
        'diff_summary': f"+{len(added_lines)} -{len(removed_lines)}"
    }


def analyze_commit_for_kotlin(commit_hash: str) -> Dict:
    """
    Analiza un commit completo para determinar si es relevante para Kotlin.
    
    Args:
        commit_hash: Hash del commit
        
    Returns:
        Diccionario con análisis del commit
    """
    # Obtener información del commit
    commit_info = run_git_command(['show', '--stat', '--format=%H|%an|%ae|%ad|%s', '--date=short', commit_hash])
    
    if not commit_info:
        return {
            'relevant': False,
            'reason': 'Commit no encontrado'
        }
    
    lines = commit_info.split('\n')
    header = lines[0] if lines else ''
    parts = header.split('|') if '|' in header else []
    
    commit_data = {
        'hash': parts[0] if len(parts) > 0 else commit_hash,
        'author': parts[1] if len(parts) > 1 else 'unknown',
        'email': parts[2] if len(parts) > 2 else '',
        'date': parts[3] if len(parts) > 3 else '',
        'message': parts[4] if len(parts) > 4 else '',
    }
    
    # Obtener archivos modificados
    files_output = run_git_command(['show', '--name-status', '--format=', commit_hash])
    
    relevant_files = []
    irrelevant_files = []
    
    for line in files_output.split('\n'):
        if not line.strip():
            continue
        
        status = line[0] if line else ''
        file_path = line.split('\t', 1)[1] if '\t' in line else line[2:]
        
        if is_relevant_for_kotlin(file_path):
            file_analysis = analyze_file_changes(file_path, commit_hash)
            if file_analysis.get('relevant', False):
                relevant_files.append({
                    'path': file_path,
                    'status': status,
                    'analysis': file_analysis
                })
            else:
                irrelevant_files.append({
                    'path': file_path,
                    'status': status,
                    'reason': file_analysis.get('reason', 'No relevante')
                })
    
    is_relevant = len(relevant_files) > 0
    
    return {
        'relevant': is_relevant,
        'commit': commit_data,
        'relevant_files': relevant_files,
        'irrelevant_files': irrelevant_files,
        'reason': f"{len(relevant_files)} archivos relevantes, {len(irrelevant_files)} irrelevantes"
    }


def get_recent_commits_analysis(since: str = "today") -> List[Dict]:
    """
    Analiza commits recientes y determina cuáles son relevantes para Kotlin.
    
    Args:
        since: Fecha desde la cual analizar (ej: "today", "yesterday", "7 days ago")
        
    Returns:
        Lista de análisis de commits relevantes
    """
    # Obtener commits recientes
    commits_output = run_git_command([
        'log',
        f'--since={since}',
        '--pretty=format:%H',
        '--all'
    ])
    
    if not commits_output:
        return []
    
    commit_hashes = commits_output.split('\n')
    
    relevant_commits = []
    
    for commit_hash in commit_hashes:
        if not commit_hash.strip():
            continue
        
        analysis = analyze_commit_for_kotlin(commit_hash.strip())
        
        if analysis.get('relevant', False):
            relevant_commits.append(analysis)
    
    return relevant_commits


def should_create_kotlin_task(file_analysis: Dict, commit_analysis: Dict) -> Tuple[bool, str]:
    """
    Determina si se debe crear una tarea en Kotlin basándose en el análisis.
    
    Args:
        file_analysis: Análisis del archivo
        commit_analysis: Análisis del commit
        
    Returns:
        Tupla (debe_crear_tarea, razón)
    """
    if not file_analysis.get('relevant', False):
        return False, file_analysis.get('reason', 'No relevante para Kotlin')
    
    change_type = file_analysis.get('change_type', 'unknown')
    
    # Cambios que siempre requieren tarea en Kotlin
    if change_type in ['api_change', 'functionality_added', 'model_added', 'feature_added']:
        return True, f"Cambio de tipo '{change_type}' requiere implementación en Kotlin"
    
    # Refactor puede o no requerir tarea
    if change_type == 'refactor':
        # Si hay keywords relevantes, probablemente sí
        if file_analysis.get('relevant_keywords'):
            return True, "Refactor con cambios en API pública"
        else:
            return False, "Refactor interno, no requiere cambios en Kotlin"
    
    # Modificaciones menores pueden no requerir tarea
    if change_type == 'modification':
        added = file_analysis.get('added_lines', 0)
        removed = file_analysis.get('removed_lines', 0)
        
        # Si hay muchos cambios, probablemente sí
        if added + removed > 50:
            return True, "Cambios significativos (>50 líneas)"
        elif file_analysis.get('relevant_keywords'):
            return True, "Modificación con keywords relevantes"
        else:
            return False, "Modificación menor, revisar manualmente"
    
    return False, "Tipo de cambio desconocido"

