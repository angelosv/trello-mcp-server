#!/usr/bin/env python3
"""
Detector de cambios en Swift SDK que analiza commits recientes y sugiere nuevas tareas.

Uso:
    python3 detect_swift_changes.py [--since DATE] [--auto-create] [--dry-run]

Ejemplos:
    # Analizar cambios desde el lunes pasado
    python3 detect_swift_changes.py --since "last monday"

    # Analizar cambios de la última semana y crear tarjetas automáticamente
    python3 detect_swift_changes.py --since "7 days ago" --auto-create

    # Solo mostrar sugerencias sin crear tarjetas
    python3 detect_swift_changes.py --since "last monday" --dry-run
"""

import os
import sys
import subprocess
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Set

SWIFT_SDK_PATH = "/Users/angelo/ReachuSwiftSDK"
GUIDE_PATH = "/Users/angelo/ReachuSwiftSDK/KOTLIN_IMPLEMENTATION_GUIDE.md"


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
        print(f"⚠️  Error ejecutando git: {e.stderr}")
        return ""


def parse_date_since(date_str: str) -> str:
    """Convierte expresiones de fecha a formato git."""
    date_str_lower = date_str.lower()
    
    if "last monday" in date_str_lower or "monday" in date_str_lower:
        today = datetime.now()
        days_since_monday = (today.weekday()) % 7
        if days_since_monday == 0:  # Es lunes
            days_since_monday = 7
        monday = today - timedelta(days=days_since_monday)
        return monday.strftime("%Y-%m-%d")
    elif "days ago" in date_str_lower:
        days = int(re.search(r'(\d+)', date_str_lower).group(1))
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%d")
    elif "weeks ago" in date_str_lower:
        weeks = int(re.search(r'(\d+)', date_str_lower).group(1))
        date = datetime.now() - timedelta(weeks=weeks)
        return date.strftime("%Y-%m-%d")
    else:
        # Intentar parsear como fecha
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            return date_str  # Dejar como está, git puede manejarlo


def get_recent_commits(since: str) -> List[Dict]:
    """Obtiene commits recientes con información detallada."""
    since_date = parse_date_since(since)
    
    # Obtener commits con formato personalizado
    cmd = [
        "log",
        f"--since={since_date}",
        "--pretty=format:%H|%an|%ae|%ad|%s",
        "--date=short",
        "--name-status"
    ]
    
    output = run_git_command(cmd)
    if not output:
        return []
    
    commits = []
    current_commit = None
    current_files = []
    
    for line in output.split('\n'):
        if '|' in line and len(line.split('|')) == 5:
            # Nuevo commit
            if current_commit:
                current_commit['files'] = current_files
                commits.append(current_commit)
            
            parts = line.split('|')
            current_commit = {
                'hash': parts[0],
                'author': parts[1],
                'email': parts[2],
                'date': parts[3],
                'message': parts[4],
                'files': []
            }
            current_files = []
        elif line.startswith(('A\t', 'M\t', 'D\t', 'R')):
            # Archivo modificado
            file_status = line[0]
            file_path = line.split('\t', 1)[1] if '\t' in line else line[2:]
            current_files.append({
                'status': file_status,
                'path': file_path
            })
    
    if current_commit:
        current_commit['files'] = current_files
        commits.append(current_commit)
    
    return commits


def get_existing_tasks() -> Set[str]:
    """Obtiene las tareas ya documentadas en la guía."""
    try:
        with open(GUIDE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return set()
    
    # Buscar todos los números de tarea
    pattern = r'## (\d+)\.'
    tasks = re.findall(pattern, content)
    return set(tasks)


def analyze_swift_file(file_path: str) -> Dict:
    """Analiza un archivo Swift para detectar funcionalidades."""
    full_path = os.path.join(SWIFT_SDK_PATH, file_path)
    
    if not os.path.exists(full_path) or not file_path.endswith('.swift'):
        return {}
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return {}
    
    analysis = {
        'path': file_path,
        'classes': [],
        'functions': [],
        'public_apis': [],
        'complexity': 'low'
    }
    
    # Detectar clases públicas
    class_pattern = r'public\s+(?:class|struct|enum)\s+(\w+)'
    classes = re.findall(class_pattern, content)
    analysis['classes'] = classes
    
    # Detectar funciones públicas
    func_pattern = r'public\s+func\s+(\w+)'
    functions = re.findall(func_pattern, content)
    analysis['functions'] = functions
    
    # Detectar APIs públicas (más importante)
    api_pattern = r'public\s+(?:class|struct|enum|func|var|let)\s+(\w+)'
    apis = re.findall(api_pattern, content)
    analysis['public_apis'] = apis
    
    # Estimar complejidad basándose en líneas y estructuras
    lines = len(content.split('\n'))
    if lines > 500:
        analysis['complexity'] = 'high'
    elif lines > 200:
        analysis['complexity'] = 'medium'
    
    return analysis


def categorize_change(file_path: str, status: str) -> str:
    """Categoriza el tipo de cambio."""
    if 'Manager' in file_path:
        return 'Backend'
    elif 'Component' in file_path or 'View' in file_path or 'UI' in file_path:
        return 'UX/UI'
    elif 'Configuration' in file_path or 'Config' in file_path:
        return 'Configuration'
    elif 'Model' in file_path or 'DTO' in file_path:
        return 'Models'
    elif 'Localization' in file_path or 'Translation' in file_path:
        return 'Localization'
    elif 'Network' in file_path or 'API' in file_path:
        return 'API'
    elif 'Cache' in file_path or 'Storage' in file_path:
        return 'Cache'
    else:
        return 'Other'


def suggest_task(change: Dict, commits: List[Dict]) -> Dict:
    """Sugiere una nueva tarea basándose en los cambios."""
    file_path = change['path']
    status = change['status']
    
    # Analizar archivo si es nuevo o modificado significativamente
    if status in ['A', 'M']:
        analysis = analyze_swift_file(file_path)
    else:
        analysis = {}
    
    category = categorize_change(file_path, status)
    
    # Generar nombre de tarea
    file_name = os.path.basename(file_path).replace('.swift', '')
    if status == 'A':
        task_name = f"Portar {file_name} a Kotlin"
    elif status == 'M':
        task_name = f"Actualizar implementación de {file_name} en Kotlin"
    else:
        task_name = f"Revisar cambios en {file_name}"
    
    # Encontrar commits relacionados
    related_commits = [
        c for c in commits
        if any(f['path'] == file_path for f in c.get('files', []))
    ]
    
    # Estimar complejidad
    complexity = analysis.get('complexity', 'low')
    if complexity == 'high':
        estimation = "5-8 horas"
    elif complexity == 'medium':
        estimation = "3-5 horas"
    else:
        estimation = "2-3 horas"
    
    # Determinar tags
    tags = ["Kotlin"]
    if category == 'Backend':
        tags.append("Backend")
    elif category == 'UX/UI':
        tags.append("UX/UI")
    elif category == 'Localization':
        tags.append("Localización")
    elif category == 'API':
        tags.append("API")
    elif category == 'Cache':
        tags.append("Cache")
    
    if complexity == 'high':
        tags.append("Prioridad")
    
    suggestion = {
        'task_name': task_name,
        'file_path': file_path,
        'category': category,
        'estimation': estimation,
        'tags': tags,
        'complexity': complexity,
        'related_commits': related_commits,
        'analysis': analysis,
        'status': status
    }
    
    return suggestion


def generate_guide_section(suggestion: Dict, next_task_number: int) -> str:
    """Genera una sección para la guía de implementación."""
    file_path = suggestion['file_path']
    task_name = suggestion['task_name']
    analysis = suggestion.get('analysis', {})
    
    section = f"""## {next_task_number}. {task_name}

### Cómo funciona en Swift

El archivo `{file_path}` contiene:
"""
    
    if analysis.get('classes'):
        section += f"- Clases: {', '.join(analysis['classes'])}\n"
    if analysis.get('functions'):
        section += f"- Funciones públicas: {len(analysis['functions'])} funciones\n"
    
    section += f"""
**Archivo:** `{file_path}`

### Qué hacer en Kotlin

1. Revisar el código Swift en `{file_path}`
2. Portar la funcionalidad equivalente a Kotlin
3. Adaptar a las mejores prácticas de Kotlin/Android
4. Mantener la misma API pública si es posible

### Archivos a revisar
- `{file_path}`

### Consideraciones importantes

- Complejidad estimada: {suggestion['complexity']}
- Categoría: {suggestion['category']}
- Commits relacionados:
"""
    
    for commit in suggestion['related_commits'][:3]:  # Máximo 3 commits
        section += f"  - {commit['hash'][:8]}: {commit['message']}\n"
    
    return section


def main():
    parser = argparse.ArgumentParser(
        description="Detecta cambios en Swift SDK y sugiere nuevas tareas"
    )
    parser.add_argument(
        "--since",
        default="last monday",
        help="Fecha desde la cual analizar cambios (ej: 'last monday', '7 days ago', '2024-01-01')"
    )
    parser.add_argument(
        "--auto-create",
        action="store_true",
        help="Crear tarjetas automáticamente en Trello"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar sugerencias sin crear nada"
    )
    parser.add_argument(
        "--add-to-guide",
        action="store_true",
        help="Agregar sugerencias a la guía de implementación"
    )
    
    args = parser.parse_args()
    
    print(f"🔍 Analizando cambios desde: {args.since}\n")
    
    # Obtener commits recientes
    commits = get_recent_commits(args.since)
    
    if not commits:
        print("✅ No se encontraron commits recientes")
        return
    
    print(f"📝 Encontrados {len(commits)} commits\n")
    
    # Obtener archivos modificados
    all_files = {}
    for commit in commits:
        for file_info in commit.get('files', []):
            file_path = file_info['path']
            if file_path.endswith('.swift') and 'Sources/' in file_path:
                if file_path not in all_files:
                    all_files[file_path] = file_info
                # Mantener el estado más reciente
                all_files[file_path] = file_info
    
    if not all_files:
        print("✅ No se encontraron archivos Swift modificados")
        return
    
    print(f"📁 Archivos Swift modificados: {len(all_files)}\n")
    
    # Obtener tareas existentes
    existing_tasks = get_existing_tasks()
    next_task_number = max([int(t) for t in existing_tasks] + [0]) + 1
    
    # Generar sugerencias
    suggestions = []
    for file_path, file_info in all_files.items():
        suggestion = suggest_task(file_info, commits)
        suggestions.append(suggestion)
    
    # Mostrar sugerencias
    print("=" * 80)
    print("💡 SUGERENCIAS DE NUEVAS TAREAS")
    print("=" * 80)
    print()
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"📋 Sugerencia #{i}: {suggestion['task_name']}")
        print(f"   📁 Archivo: {suggestion['file_path']}")
        print(f"   🏷️  Tags: {', '.join(suggestion['tags'])}")
        print(f"   ⏱️  Estimación: {suggestion['estimation']}")
        print(f"   📊 Complejidad: {suggestion['complexity']}")
        print(f"   📝 Commits: {len(suggestion['related_commits'])} commits relacionados")
        print()
    
    # Agregar a guía si se solicita
    if args.add_to_guide and not args.dry_run:
        print("📝 Agregando sugerencias a la guía...")
        try:
            with open(GUIDE_PATH, 'r', encoding='utf-8') as f:
                guide_content = f.read()
            
            # Agregar nuevas secciones al final (antes del resumen)
            new_sections = []
            current_task_num = next_task_number
            
            for suggestion in suggestions:
                section = generate_guide_section(suggestion, current_task_num)
                new_sections.append(section)
                current_task_num += 1
            
            # Insertar antes del "## Resumen General"
            if "## Resumen General" in guide_content:
                insert_pos = guide_content.find("## Resumen General")
                guide_content = (
                    guide_content[:insert_pos] +
                    "\n".join(new_sections) + "\n\n---\n\n" +
                    guide_content[insert_pos:]
                )
            else:
                guide_content += "\n\n" + "\n".join(new_sections)
            
            with open(GUIDE_PATH, 'w', encoding='utf-8') as f:
                f.write(guide_content)
            
            print(f"✅ Agregadas {len(suggestions)} nuevas secciones a la guía")
        except Exception as e:
            print(f"❌ Error agregando a la guía: {e}")
    
    # Crear tarjetas automáticamente si se solicita
    if args.auto_create and not args.dry_run:
        print("\n🎫 Creando tarjetas en Trello...")
        # Importar y usar generate_trello_cards
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            from generate_trello_cards import create_card, get_board_lists, find_or_create_label, TEAM_MEMBERS
            
            # Obtener lista "To Do"
            lists = get_board_lists("5dea6d99c0ea505b4c3a435e")
            todo_list = next((l for l in lists if l["name"] == "To Do"), None)
            
            if not todo_list:
                print("❌ No se encontró la lista 'To Do'")
                return
            
            # Crear tarjetas
            for suggestion in suggestions:
                # Generar descripción básica
                description = generate_guide_section(suggestion, next_task_number)
                
                # Obtener labels
                label_ids = []
                for tag in suggestion['tags']:
                    label_id = find_or_create_label("5dea6d99c0ea505b4c3a435e", tag)
                    label_ids.append(label_id)
                
                # Crear tarjeta
                card = create_card(
                    todo_list["id"],
                    f"[Tarea #{next_task_number}] {suggestion['task_name']}",
                    description,
                    label_ids,
                    list(TEAM_MEMBERS.values())
                )
                
                print(f"✅ Creada tarjeta: {card['shortUrl']}")
                next_task_number += 1
                time.sleep(0.5)
            
            print(f"\n✅ Creadas {len(suggestions)} tarjetas en Trello")
        except ImportError:
            print("⚠️  No se pudo importar generate_trello_cards.py")
            print("   Ejecuta manualmente: python3 generate_trello_cards.py")
        except Exception as e:
            print(f"❌ Error creando tarjetas: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Análisis completado")
    print("=" * 80)


if __name__ == "__main__":
    import time
    main()

