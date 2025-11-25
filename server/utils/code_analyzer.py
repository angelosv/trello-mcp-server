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
KOTLIN_SDK_PATH = "/Users/angelo/Documents/GitHub/ReachuKotlinSDK"
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
    
    # Analizar cambios específicos en el código
    code_changes = analyze_code_changes(added_lines, removed_lines)
    
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
        'diff_summary': f"+{len(added_lines)} -{len(removed_lines)}",
        'code_changes': code_changes  # Nuevo: análisis detallado de cambios
    }


def analyze_code_changes(added_lines: List[str], removed_lines: List[str]) -> Dict:
    """
    Analiza los cambios en el código para extraer información detallada.
    
    Args:
        added_lines: Líneas agregadas
        removed_lines: Líneas eliminadas
        
    Returns:
        Diccionario con análisis detallado de cambios
    """
    changes = {
        'functions_added': [],
        'functions_modified': [],
        'properties_added': [],
        'properties_modified': [],
        'classes_added': [],
        'structs_added': [],
        'enums_added': [],
        'extensions_added': [],
        'initializers_modified': [],
        'api_changes': [],
        'property_details': {},  # Detalles de propiedades (tipo, valor por defecto, etc.)
        'function_details': {},   # Detalles de funciones (parámetros, tipo de retorno)
        'description': []
    }
    
    # Combinar líneas para análisis contextual
    all_lines = '\n'.join(added_lines)
    
    # Analizar funciones agregadas/modificadas (más completo)
    for i, line in enumerate(added_lines):
        # Funciones públicas (con o sin modificadores)
        func_patterns = [
            r'(?:public\s+)?(?:static\s+)?(?:@\w+\s+)?func\s+(\w+)\s*\(',
            r'private\s+func\s+(\w+)\s*\(',
            r'fileprivate\s+func\s+(\w+)\s*\(',
        ]
        
        for pattern in func_patterns:
            func_match = re.search(pattern, line)
            if func_match:
                func_name = func_match.group(1)
                # Verificar si es nueva o modificada
                if any(func_name in rl and '(' in rl for rl in removed_lines):
                    changes['functions_modified'].append(func_name)
                else:
                    changes['functions_added'].append(func_name)
                
                # Extraer detalles de la función
                func_details = extract_function_details(line, added_lines[i:i+5])
                if func_details:
                    changes['function_details'][func_name] = func_details
                break
        
        # Propiedades (más completo - incluye private, let, var, computed properties)
        prop_patterns = [
            r'(?:public\s+)?(?:private\s+)?(?:static\s+)?(?:@\w+\s+)?(let|var)\s+(\w+)',
            r'private\s+(let|var)\s+(\w+)',
            r'fileprivate\s+(let|var)\s+(\w+)',
        ]
        
        for pattern in prop_patterns:
            prop_match = re.search(pattern, line)
            if prop_match:
                prop_name = prop_match.group(2) if len(prop_match.group(0).split()) > 2 else prop_match.group(1)
                prop_type = prop_match.group(1) if prop_match.group(1) in ['let', 'var'] else 'var'
                
                # Verificar si es nueva o modificada
                if any(prop_name in rl and (prop_type in rl or '=' in rl) for rl in removed_lines):
                    changes['properties_modified'].append(prop_name)
                else:
                    changes['properties_added'].append(prop_name)
                
                # Extraer detalles de la propiedad
                prop_details = extract_property_details(line, prop_name)
                if prop_details:
                    changes['property_details'][prop_name] = prop_details
                break
        
        # Clases/Structs/Enums (más completo)
        type_patterns = [
            r'(?:public\s+)?(class|struct|enum)\s+(\w+)',
            r'private\s+(class|struct|enum)\s+(\w+)',
        ]
        
        for pattern in type_patterns:
            type_match = re.search(pattern, line)
            if type_match:
                type_kind = type_match.group(1)
                type_name = type_match.group(2)
                
                if type_kind == 'class':
                    changes['classes_added'].append(type_name)
                elif type_kind == 'struct':
                    changes['structs_added'].append(type_name)
                elif type_kind == 'enum':
                    changes['enums_added'].append(type_name)
                break
        
        # Extensiones
        ext_match = re.search(r'extension\s+(\w+)', line)
        if ext_match:
            ext_name = ext_match.group(1)
            if ext_name not in changes['extensions_added']:
                changes['extensions_added'].append(ext_name)
        
        # Inicializadores modificados
        init_match = re.search(r'init\s*\(', line)
        if init_match:
            # Buscar si hay cambios en parámetros
            if any('init' in rl and '(' in rl for rl in removed_lines):
                changes['initializers_modified'].append('init')
    
    # Analizar cambios en asignaciones de propiedades (self.prop = ...)
    for line in added_lines:
        assign_match = re.search(r'self\.(\w+)\s*=', line)
        if assign_match:
            prop_name = assign_match.group(1)
            if prop_name not in changes['properties_modified']:
                changes['properties_modified'].append(prop_name)
    
    # Generar descripción detallada
    desc_parts = []
    
    if changes['classes_added']:
        desc_parts.append(f"✅ Clases agregadas: {', '.join(changes['classes_added'])}")
    if changes['structs_added']:
        desc_parts.append(f"✅ Structs agregados: {', '.join(changes['structs_added'])}")
    if changes['enums_added']:
        desc_parts.append(f"✅ Enums agregados: {', '.join(changes['enums_added'])}")
    if changes['extensions_added']:
        desc_parts.append(f"✅ Extensiones agregadas: {', '.join(changes['extensions_added'])}")
    
    if changes['properties_added']:
        props_info = []
        for prop in changes['properties_added'][:5]:
            prop_detail = changes['property_details'].get(prop, {})
            if prop_detail.get('type'):
                props_info.append(f"{prop} ({prop_detail['type']})")
            else:
                props_info.append(prop)
        desc_parts.append(f"✅ Propiedades agregadas: {', '.join(props_info)}")
    
    if changes['properties_modified']:
        props_info = []
        for prop in changes['properties_modified'][:5]:
            prop_detail = changes['property_details'].get(prop, {})
            if prop_detail.get('type'):
                props_info.append(f"{prop} ({prop_detail['type']})")
            else:
                props_info.append(prop)
        desc_parts.append(f"🔄 Propiedades modificadas: {', '.join(props_info)}")
    
    if changes['functions_added']:
        funcs_info = []
        for func in changes['functions_added'][:5]:
            func_detail = changes['function_details'].get(func, {})
            if func_detail.get('params'):
                params_str = ', '.join(func_detail['params'][:3])
                funcs_info.append(f"{func}({params_str}...)")
            else:
                funcs_info.append(func)
        desc_parts.append(f"✅ Funciones agregadas: {', '.join(funcs_info)}")
    
    if changes['functions_modified']:
        desc_parts.append(f"🔄 Funciones modificadas: {', '.join(changes['functions_modified'][:5])}")
    
    if changes['initializers_modified']:
        desc_parts.append(f"🔄 Inicializadores modificados")
    
    # Analizar cambios específicos en configuración, componentes, etc.
    config_changes = []
    component_changes = []
    manager_changes = []
    service_changes = []
    
    for line in added_lines:
        if 'Configuration' in line or 'Config' in line or 'Theme' in line:
            config_match = re.search(r'(\w+Config|\w+Configuration|\w+Theme)', line)
            if config_match:
                config_changes.append(config_match.group(1))
        
        if 'Component' in line or 'View' in line:
            comp_match = re.search(r'(R\w+|Component\w+)', line)
            if comp_match:
                component_changes.append(comp_match.group(1))
        
        if 'Manager' in line:
            mgr_match = re.search(r'(\w+Manager)', line)
            if mgr_match:
                manager_changes.append(mgr_match.group(1))
        
        if 'Service' in line:
            svc_match = re.search(r'(\w+Service)', line)
            if svc_match:
                service_changes.append(svc_match.group(1))
    
    if config_changes:
        desc_parts.append(f"⚙️ Cambios en configuración: {', '.join(list(set(config_changes))[:3])}")
    if component_changes:
        desc_parts.append(f"🎨 Cambios en componentes: {', '.join(list(set(component_changes))[:3])}")
    if manager_changes:
        desc_parts.append(f"📦 Cambios en managers: {', '.join(list(set(manager_changes))[:3])}")
    if service_changes:
        desc_parts.append(f"🔧 Cambios en services: {', '.join(list(set(service_changes))[:3])}")
    
    changes['description'] = desc_parts
    
    return changes


def extract_property_details(line: str, prop_name: str) -> Dict:
    """Extrae detalles de una propiedad (tipo, valor por defecto, etc.)"""
    details = {}
    
    # Buscar tipo de la propiedad
    type_match = re.search(r':\s*(\w+(?:<[^>]+>)?(?:\?)?)', line)
    if type_match:
        details['type'] = type_match.group(1)
    
    # Buscar valor por defecto
    default_match = re.search(r'=\s*([^,\n]+)', line)
    if default_match:
        default_val = default_match.group(1).strip()
        if len(default_val) < 50:  # Limitar longitud
            details['default'] = default_val
    
    return details


def extract_function_details(line: str, context_lines: List[str]) -> Dict:
    """Extrae detalles de una función (parámetros, tipo de retorno, etc.)"""
    details = {}
    
    # Buscar parámetros
    params_match = re.search(r'\(([^)]+)\)', line)
    if params_match:
        params_str = params_match.group(1)
        # Extraer nombres de parámetros
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if ':' in param:
                param_name = param.split(':')[0].strip()
                if param_name and not param_name.startswith('_'):
                    params.append(param_name)
        if params:
            details['params'] = params
    
    # Buscar tipo de retorno
    return_match = re.search(r'->\s*(\w+(?:<[^>]+>)?(?:\?)?)', line)
    if return_match:
        details['return_type'] = return_match.group(1)
    
    return details


def check_kotlin_implementation(swift_file_path: str, code_changes: Dict) -> Dict:
    """
    Revisa si los cambios en Swift ya están implementados en Kotlin.
    
    Args:
        swift_file_path: Ruta del archivo Swift
        code_changes: Diccionario con los cambios detectados en Swift
        
    Returns:
        Diccionario con información sobre la implementación en Kotlin
    """
    kotlin_info = {
        'needs_implementation': True,
        'kotlin_file_path': None,
        'already_implemented': [],
        'missing_implementation': [],
        'notes': []
    }
    
    if not os.path.exists(KOTLIN_SDK_PATH):
        kotlin_info['notes'].append('Proyecto Kotlin no encontrado en la ruta esperada')
        return kotlin_info
    
    # Mapear ruta Swift a ruta Kotlin equivalente
    kotlin_path = map_swift_to_kotlin_path(swift_file_path)
    
    if kotlin_path and os.path.exists(kotlin_path):
        kotlin_info['kotlin_file_path'] = kotlin_path
        
        # Leer archivo Kotlin
        try:
            with open(kotlin_path, 'r', encoding='utf-8') as f:
                kotlin_content = f.read()
        except Exception as e:
            kotlin_info['notes'].append(f'Error leyendo archivo Kotlin: {str(e)}')
            return kotlin_info
        
        # Verificar si las propiedades/funciones/clases ya existen
        properties_added = code_changes.get('properties_added', [])
        functions_added = code_changes.get('functions_added', [])
        classes_added = code_changes.get('classes_added', [])
        
        already_implemented = []
        missing = []
        
        # Buscar propiedades en Kotlin
        for prop in properties_added:
            # Buscar patrones comunes en Kotlin (val/var propName)
            kotlin_patterns = [
                rf'\bval\s+{prop}\b',
                rf'\bvar\s+{prop}\b',
                rf'property\s+{prop}\b',
            ]
            found = any(re.search(pattern, kotlin_content, re.IGNORECASE) for pattern in kotlin_patterns)
            if found:
                already_implemented.append(f'propiedad: {prop}')
            else:
                missing.append(f'propiedad: {prop}')
        
        # Buscar funciones en Kotlin
        for func in functions_added:
            # Buscar funciones en Kotlin (fun funcName)
            kotlin_patterns = [
                rf'\bfun\s+{func}\s*\(',
                rf'\bprivate\s+fun\s+{func}\s*\(',
                rf'\bpublic\s+fun\s+{func}\s*\(',
            ]
            found = any(re.search(pattern, kotlin_content, re.IGNORECASE) for pattern in kotlin_patterns)
            if found:
                already_implemented.append(f'función: {func}')
            else:
                missing.append(f'función: {func}')
        
        # Buscar clases/structs en Kotlin
        for cls in classes_added:
            # Buscar clases/data classes en Kotlin
            kotlin_patterns = [
                rf'\bclass\s+{cls}\b',
                rf'\bdata\s+class\s+{cls}\b',
                rf'\bobject\s+{cls}\b',
                rf'\bsealed\s+class\s+{cls}\b',
            ]
            found = any(re.search(pattern, kotlin_content, re.IGNORECASE) for pattern in kotlin_patterns)
            if found:
                already_implemented.append(f'clase: {cls}')
            else:
                missing.append(f'clase: {cls}')
        
        kotlin_info['already_implemented'] = already_implemented
        kotlin_info['missing_implementation'] = missing
        kotlin_info['needs_implementation'] = len(missing) > 0
        
        if already_implemented:
            kotlin_info['notes'].append(f'Ya implementado en Kotlin: {", ".join(already_implemented[:3])}')
        if missing:
            kotlin_info['notes'].append(f'Falta implementar en Kotlin: {", ".join(missing[:3])}')
    else:
        # Archivo no existe en Kotlin - necesita implementación
        kotlin_info['notes'].append('Archivo equivalente no encontrado en Kotlin - necesita implementación completa')
        kotlin_info['missing_implementation'] = [
            f'archivo: {os.path.basename(swift_file_path)}'
        ] + [f'propiedad: {p}' for p in properties_added[:3]] + \
          [f'función: {f}' for f in functions_added[:3]] + \
          [f'clase: {c}' for c in classes_added[:3]]
    
    return kotlin_info


def map_swift_to_kotlin_path(swift_path: str) -> Optional[str]:
    """
    Mapea una ruta de archivo Swift a su equivalente en Kotlin.
    
    Args:
        swift_path: Ruta del archivo Swift
        
    Returns:
        Ruta equivalente en Kotlin o None si no se puede mapear
    """
    # Mapeos comunes
    path_mappings = {
        'Sources/ReachuCore/': 'src/main/kotlin/io/reachu/core/',
        'Sources/ReachuUI/': 'src/main/kotlin/io/reachu/ui/',
        'Sources/ReachuDesignSystem/': 'src/main/kotlin/io/reachu/design/',
        'Sources/ReachuNetwork/': 'src/main/kotlin/io/reachu/network/',
    }
    
    # Buscar mapeo
    for swift_prefix, kotlin_prefix in path_mappings.items():
        if swift_prefix in swift_path:
            # Reemplazar prefijo y extensión
            relative_path = swift_path.replace(swift_prefix, '')
            # Convertir nombre de archivo Swift a Kotlin
            filename = os.path.basename(relative_path)
            kotlin_filename = filename.replace('.swift', '.kt')
            
            # Construir ruta Kotlin
            kotlin_path = os.path.join(KOTLIN_SDK_PATH, kotlin_prefix, kotlin_filename)
            
            # Verificar si existe
            if os.path.exists(kotlin_path):
                return kotlin_path
            
            # Intentar buscar en subdirectorios
            kotlin_dir = os.path.join(KOTLIN_SDK_PATH, kotlin_prefix)
            if os.path.exists(kotlin_dir):
                # Buscar archivo recursivamente
                for root, dirs, files in os.walk(kotlin_dir):
                    if kotlin_filename in files:
                        return os.path.join(root, kotlin_filename)
    
    return None


def analyze_commit_for_kotlin(commit_hash: str) -> Dict:
    """
    Analiza un commit completo para determinar si es relevante para Kotlin.
    Ahora también revisa el código Kotlin para ver si ya está implementado.
    
    Args:
        commit_hash: Hash del commit
        
    Returns:
        Diccionario con análisis del commit
    """
    # Obtener información básica del commit
    commit_info = run_git_command(['show', '--stat', '--format=%H|%an|%ae|%ad|%s', '--date=short', commit_hash])
    
    if not commit_info:
        return {
            'relevant': False,
            'reason': 'Commit no encontrado'
        }
    
    lines = commit_info.split('\n')
    header = lines[0] if lines else ''
    parts = header.split('|') if '|' in header else []
    
    # Obtener mensaje completo del commit (incluyendo cuerpo si existe)
    full_message_output = run_git_command(['log', '-1', '--format=%B', commit_hash])
    full_message = full_message_output.strip() if full_message_output else ''
    
    # Separar primera línea (subject) del resto (body)
    message_lines = full_message.split('\n')
    subject = message_lines[0] if message_lines else ''
    body = '\n'.join(message_lines[1:]).strip() if len(message_lines) > 1 else ''
    
    commit_data = {
        'hash': parts[0] if len(parts) > 0 else commit_hash,
        'author': parts[1] if len(parts) > 1 else 'unknown',
        'email': parts[2] if len(parts) > 2 else '',
        'date': parts[3] if len(parts) > 3 else '',
        'message': subject,  # Primera línea del mensaje
        'message_full': full_message,  # Mensaje completo
        'message_body': body,  # Cuerpo del mensaje (sin la primera línea)
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
                # Revisar si ya está implementado en Kotlin
                code_changes = file_analysis.get('code_changes', {})
                kotlin_check = check_kotlin_implementation(file_path, code_changes)
                
                # Agregar información de Kotlin al análisis
                file_analysis['kotlin_check'] = kotlin_check
                
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
    
    # Determinar relevancia: es relevante si hay archivos que necesitan implementación en Kotlin
    needs_implementation = any(
        f.get('analysis', {}).get('kotlin_check', {}).get('needs_implementation', True)
        for f in relevant_files
    )
    
    is_relevant = len(relevant_files) > 0 and needs_implementation
    
    return {
        'relevant': is_relevant,
        'commit': commit_data,
        'relevant_files': relevant_files,
        'irrelevant_files': irrelevant_files,
        'reason': f"{len(relevant_files)} archivos relevantes, {len(irrelevant_files)} irrelevantes" + 
                 (f" ({sum(1 for f in relevant_files if f.get('analysis', {}).get('kotlin_check', {}).get('needs_implementation', True))} necesitan implementación)" if relevant_files else "")
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

