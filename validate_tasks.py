#!/usr/bin/env python3
"""
Validador de completitud que verifica que las tareas de Trello estén completas.

Uso:
    python3 validate_tasks.py [--board-id BOARD_ID] [--fix] [--verbose]

Ejemplos:
    # Validar todas las tareas
    python3 validate_tasks.py

    # Validar y corregir automáticamente
    python3 validate_tasks.py --fix

    # Validar con salida detallada
    python3 validate_tasks.py --verbose
"""

import os
import sys
import httpx
import re
import argparse
from typing import List, Dict, Set
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"
DEFAULT_BOARD_ID = "5dea6d99c0ea505b4c3a435e"  # Reachu Dev
GUIDE_PATH = "/Users/angelo/ReachuSwiftSDK/KOTLIN_IMPLEMENTATION_GUIDE.md"


def get_board_cards(board_id: str) -> List[Dict]:
    """Obtiene todas las tarjetas del board."""
    url = f"{TRELLO_API_BASE}/boards/{board_id}/cards"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def get_card_details(card_id: str) -> Dict:
    """Obtiene detalles completos de una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "fields": "name,desc,idList,idLabels,idMembers,url"
    }
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def get_card_checklists(card_id: str) -> List[Dict]:
    """Obtiene los checklists de una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}/checklists"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def get_list_name(list_id: str) -> str:
    """Obtiene el nombre de una lista."""
    url = f"{TRELLO_API_BASE}/lists/{list_id}"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN, "fields": "name"}
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("name", "Unknown")


def parse_task_number(card_name: str) -> int:
    """Extrae el número de tarea del nombre de la tarjeta."""
    match = re.search(r'Tarea #(\d+)', card_name)
    return int(match.group(1)) if match else None


def validate_criteria_acceptance(card: Dict) -> tuple[bool, str]:
    """Valida que la tarjeta tenga criterios de aceptación."""
    desc = card.get("desc", "")
    
    if "### Criterios de aceptación" not in desc:
        return False, "Falta sección 'Criterios de aceptación'"
    
    # Verificar que tenga al menos un checkbox
    if "- [ ]" not in desc and "- [x]" not in desc:
        return False, "Criterios de aceptación sin checkboxes"
    
    return True, "OK"


def validate_dependencies(card: Dict, all_cards: List[Dict]) -> tuple[bool, str]:
    """Valida que las dependencias estén completadas."""
    desc = card.get("desc", "")
    
    # Extraer dependencias
    deps_match = re.search(r'\*\*📋 Dependencias:\*\* (.+)', desc)
    if not deps_match:
        return True, "OK"  # Sin dependencias es válido
    
    deps_str = deps_match.group(1)
    if deps_str == "Ninguna":
        return True, "OK"
    
    # Extraer números de tarea de las dependencias
    dep_numbers = re.findall(r'Tarea #(\d+)', deps_str)
    if not dep_numbers:
        return True, "OK"
    
    task_num = parse_task_number(card.get("name", ""))
    if not task_num:
        return True, "OK"  # No se puede validar sin número de tarea
    
    # Verificar que las dependencias estén completadas
    list_name = get_list_name(card.get("idList", ""))
    
    missing_deps = []
    for dep_num in dep_numbers:
        dep_card = next(
            (c for c in all_cards if parse_task_number(c.get("name", "")) == int(dep_num)),
            None
        )
        
        if not dep_card:
            missing_deps.append(f"Tarea #{dep_num} (no encontrada)")
        else:
            dep_list_name = get_list_name(dep_card.get("idList", ""))
            if dep_list_name not in ["Done", "Completada", "Terminada"]:
                missing_deps.append(f"Tarea #{dep_num} (en '{dep_list_name}')")
    
    if missing_deps:
        return False, f"Dependencias no completadas: {', '.join(missing_deps)}"
    
    return True, "OK"


def validate_files_exist(card: Dict) -> tuple[bool, str]:
    """Valida que los archivos referenciados existan."""
    desc = card.get("desc", "")
    
    # Buscar sección "Archivos a revisar"
    files_match = re.search(r'### Archivos a revisar\s+(.+?)(?=###|$)', desc, re.DOTALL)
    if not files_match:
        return True, "OK"  # Sin archivos es válido
    
    files_section = files_match.group(1)
    
    # Extraer rutas de archivos
    file_pattern = r'`([^`]+\.swift)`'
    files = re.findall(file_pattern, files_section)
    
    if not files:
        return True, "OK"
    
    missing_files = []
    for file_path in files:
        full_path = os.path.join("/Users/angelo/ReachuSwiftSDK", file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"Archivos no encontrados: {', '.join(missing_files)}"
    
    return True, "OK"


def validate_estimation(card: Dict) -> tuple[bool, str]:
    """Valida que tenga estimación de tiempo."""
    desc = card.get("desc", "")
    
    if "⏱️ Estimación:" not in desc:
        return False, "Falta estimación de tiempo"
    
    # Verificar formato
    est_match = re.search(r'\*\*⏱️ Estimación:\*\* (.+)', desc)
    if not est_match:
        return False, "Estimación en formato incorrecto"
    
    estimation = est_match.group(1)
    if not re.search(r'\d+.*hora', estimation, re.IGNORECASE):
        return False, f"Estimación en formato incorrecto: {estimation}"
    
    return True, "OK"


def validate_tags(card: Dict) -> tuple[bool, str]:
    """Valida que tenga tags asignados."""
    labels = card.get("idLabels", [])
    
    if not labels:
        return False, "No tiene tags asignados"
    
    return True, "OK"


def validate_members(card: Dict) -> tuple[bool, str]:
    """Valida que tenga miembros asignados."""
    members = card.get("idMembers", [])
    
    if not members:
        return False, "No tiene miembros asignados"
    
    return True, "OK"


def validate_template_structure(card: Dict) -> tuple[bool, str]:
    """Valida que siga el template correcto."""
    desc = card.get("desc", "")
    
    required_sections = [
        "### Contexto",
        "### Cómo funciona en Swift",
        "### Qué hacer en Kotlin",
        "### Archivos a revisar",
        "### Consideraciones importantes",
        "### Criterios de aceptación",
        "### Preguntas frecuentes"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in desc:
            missing_sections.append(section.replace("### ", ""))
    
    if missing_sections:
        return False, f"Faltan secciones: {', '.join(missing_sections)}"
    
    return True, "OK"


def validate_task_in_guide(card: Dict) -> tuple[bool, str]:
    """Valida que la tarea esté documentada en la guía."""
    task_num = parse_task_number(card.get("name", ""))
    if not task_num:
        return True, "OK"  # No se puede validar sin número
    
    try:
        with open(GUIDE_PATH, 'r', encoding='utf-8') as f:
            guide_content = f.read()
    except FileNotFoundError:
        return False, "No se encontró la guía de implementación"
    
    # Buscar la tarea en la guía
    pattern = rf"## {task_num}\."
    if not re.search(pattern, guide_content):
        return False, f"Tarea #{task_num} no encontrada en la guía"
    
    return True, "OK"


def validate_card(card: Dict, all_cards: List[Dict], verbose: bool = False) -> Dict:
    """Valida una tarjeta completa."""
    card_details = get_card_details(card["id"])
    
    validations = {
        "template_structure": validate_template_structure(card_details),
        "criteria_acceptance": validate_criteria_acceptance(card_details),
        "estimation": validate_estimation(card_details),
        "tags": validate_tags(card_details),
        "members": validate_members(card_details),
        "files_exist": validate_files_exist(card_details),
        "dependencies": validate_dependencies(card_details, all_cards),
        "in_guide": validate_task_in_guide(card_details),
    }
    
    all_passed = all(result[0] for result in validations.values())
    
    result = {
        "card_id": card["id"],
        "card_name": card.get("name", "Unknown"),
        "card_url": card_details.get("url", ""),
        "all_passed": all_passed,
        "validations": validations
    }
    
    if verbose or not all_passed:
        print(f"\n📋 {result['card_name']}")
        print(f"   🔗 {result['card_url']}")
        for check_name, (passed, message) in validations.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}: {message}")
    
    return result


def fix_card(card: Dict, validation_result: Dict):
    """Intenta corregir automáticamente los problemas de una tarjeta."""
    print(f"\n🔧 Corrigiendo: {validation_result['card_name']}")
    
    fixes_applied = []
    
    # Agregar tags si faltan
    if not validation_result['validations']['tags'][0]:
        print("   ⚠️  No se pueden agregar tags automáticamente (requiere selección manual)")
    
    # Agregar miembros si faltan
    if not validation_result['validations']['members'][0]:
        print("   ⚠️  No se pueden agregar miembros automáticamente (requiere selección manual)")
    
    # Actualizar template si falta estructura
    if not validation_result['validations']['template_structure'][0]:
        print("   💡 Ejecuta: python3 update_cards_template.py para actualizar el template")
    
    return fixes_applied


def main():
    parser = argparse.ArgumentParser(
        description="Valida que las tareas de Trello estén completas"
    )
    parser.add_argument(
        "--board-id",
        default=DEFAULT_BOARD_ID,
        help="ID del board de Trello"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Intentar corregir automáticamente los problemas"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar detalles de todas las validaciones"
    )
    parser.add_argument(
        "--task-number",
        type=int,
        help="Validar solo una tarea específica"
    )
    
    args = parser.parse_args()
    
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
        sys.exit(1)
    
    print("🔍 Validando tareas de Trello...\n")
    
    # Obtener todas las tarjetas
    all_cards_raw = get_board_cards(args.board_id)
    
    # Filtrar solo tarjetas del proyecto Kotlin (que empiezan con "Kotlin ->" o contienen "Tarea #")
    all_cards = [
        c for c in all_cards_raw
        if c.get("name", "").startswith("Kotlin ->") or "Tarea #" in c.get("name", "")
    ]
    
    if args.task_number:
        # Filtrar por número de tarea
        all_cards = [
            c for c in all_cards
            if parse_task_number(c.get("name", "")) == args.task_number
        ]
        if not all_cards:
            print(f"❌ No se encontró la tarea #{args.task_number}")
            return
    
    print(f"📋 Encontradas {len(all_cards)} tarjetas\n")
    
    # Validar cada tarjeta
    results = []
    for card in all_cards:
        result = validate_card(card, all_cards, args.verbose)
        results.append(result)
        
        if args.fix and not result['all_passed']:
            fix_card(card, result)
    
    # Resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 80)
    
    passed = sum(1 for r in results if r['all_passed'])
    failed = len(results) - passed
    
    print(f"\n✅ Tareas válidas: {passed}/{len(results)}")
    print(f"❌ Tareas con problemas: {failed}/{len(results)}")
    
    if failed > 0:
        print("\n📋 Tareas con problemas:")
        for result in results:
            if not result['all_passed']:
                print(f"   - {result['card_name']}")
                print(f"     {result['card_url']}")
                for check_name, (passed, message) in result['validations'].items():
                    if not passed:
                        print(f"       ❌ {check_name}: {message}")
    
    # Estadísticas por tipo de validación
    print("\n📊 Estadísticas por tipo de validación:")
    validation_stats = {}
    for result in results:
        for check_name, (passed, _) in result['validations'].items():
            if check_name not in validation_stats:
                validation_stats[check_name] = {'passed': 0, 'failed': 0}
            if passed:
                validation_stats[check_name]['passed'] += 1
            else:
                validation_stats[check_name]['failed'] += 1
    
    for check_name, stats in validation_stats.items():
        total = stats['passed'] + stats['failed']
        percentage = (stats['passed'] / total * 100) if total > 0 else 0
        print(f"   {check_name}: {stats['passed']}/{total} ({percentage:.1f}%)")
    
    print("\n" + "=" * 80)
    
    # Exit code basado en resultados
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

