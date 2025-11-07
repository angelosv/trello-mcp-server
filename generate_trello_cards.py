#!/usr/bin/env python3
"""
Script reutilizable para generar tarjetas de Trello desde KOTLIN_IMPLEMENTATION_GUIDE.md

Uso:
    python3 generate_trello_cards.py [--board-id BOARD_ID] [--list-id LIST_ID] [--start-task START] [--end-task END]

Ejemplos:
    # Generar todas las tareas nuevas
    python3 generate_trello_cards.py

    # Generar solo tareas 20-25
    python3 generate_trello_cards.py --start-task 20 --end-task 25

    # Generar en un board/list específico
    python3 generate_trello_cards.py --board-id XXX --list-id YYY
"""

import os
import sys
import httpx
import re
import time
import argparse
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"

# Configuración por defecto
DEFAULT_BOARD_ID = "5dea6d99c0ea505b4c3a435e"  # Reachu Dev
DEFAULT_LIST_NAME = "To Do"  # Se buscará esta lista

# Mapeo de tareas a estimaciones (en horas, considerando uso de AI)
TASK_ESTIMATIONS = {
    1: "2-3 horas", 2: "3-4 horas", 3: "2-3 horas", 4: "2-3 horas",
    5: "3-4 horas", 6: "2-3 horas", 7: "3-4 horas", 8: "5-6 horas",
    9: "4-5 horas", 10: "3-4 horas", 11: "3-4 horas", 12: "2-3 horas",
    13: "5-6 horas", 14: "2-3 horas", 15: "4-5 horas", 16: "2-3 horas",
    17: "3-4 horas", 18: "3-4 horas", 19: "4-5 horas", 20: "2-3 horas",
    21: "2-3 horas", 22: "2-3 horas", 23: "2-3 horas", 24: "2-3 horas",
    25: "2-3 horas", 26: "2-3 horas", 27: "1-2 horas", 28: "1-2 horas",
    29: "6-8 horas", 30: "4-6 horas",
}

# Dependencias entre tareas
TASK_DEPENDENCIES = {
    1: [], 2: [1], 3: [1, 2], 4: [1, 2, 3], 5: [],
    6: [5], 7: [5, 6], 8: [5, 6], 9: [5, 8], 10: [5, 6, 7],
    11: [5, 7, 10], 12: [11], 13: [11, 12], 14: [5, 7, 10], 15: [14],
    16: [5, 7, 10], 17: [16], 18: [5, 7, 10], 19: [18],
    20: [1, 2, 3, 4, 11, 13], 21: [1, 2, 3, 4, 14, 15],
    22: [1, 2, 3, 4, 16, 17, 18, 19], 23: [11, 14, 16, 18], 24: [23],
    25: [23, 24], 26: [11, 14, 16, 18], 27: [11, 14, 15, 16, 17, 18, 19],
    28: [11, 14, 16, 18], 29: [5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19],
    30: [11, 13, 14, 15, 16, 17, 18, 19],
}

# Tags por tarea
TASK_TAGS = {
    1: ["Kotlin", "Backend", "Localización", "Prioridad"],
    2: ["Kotlin", "Backend", "Localización", "Prioridad"],
    3: ["Kotlin", "Backend", "Localización"], 4: ["Kotlin", "Backend", "Localización"],
    5: ["Kotlin", "Backend", "Prioridad"], 6: ["Kotlin", "Backend", "API"],
    7: ["Kotlin", "Backend", "API"], 8: ["Kotlin", "Backend", "WebSocket", "Prioridad"],
    9: ["Kotlin", "Backend", "WebSocket"], 10: ["Kotlin", "Backend", "Cache"],
    11: ["Kotlin", "UX/UI", "Prioridad"], 12: ["Kotlin", "UX/UI"],
    13: ["Kotlin", "UX/UI", "Prioridad"], 14: ["Kotlin", "UX/UI"], 15: ["Kotlin", "UX/UI"],
    16: ["Kotlin", "UX/UI"], 17: ["Kotlin", "UX/UI"], 18: ["Kotlin", "UX/UI"],
    19: ["Kotlin", "UX/UI"], 20: ["Kotlin", "UX/UI", "Localización"],
    21: ["Kotlin", "UX/UI", "Localización"], 22: ["Kotlin", "UX/UI", "Localización"],
    23: ["Kotlin", "Backend"], 24: ["Kotlin", "Backend"], 25: ["Kotlin", "Backend"],
    26: ["Kotlin", "UX/UI"], 27: ["Kotlin", "UX/UI"], 28: ["Kotlin", "UX/UI"],
    29: ["Kotlin", "Testing"], 30: ["Kotlin", "Documentación"],
}

# IDs de miembros del equipo
TEAM_MEMBERS = {
    "miguel1": "619f90698c4fc547cc133149",
    "miguel2": "680a7cb22a55497d4f4223d4",
    "angelo": "5c8ba472ce95df5cb68edf00",
}


def get_board_lists(board_id: str):
    """Obtiene las listas de un board."""
    url = f"{TRELLO_API_BASE}/boards/{board_id}/lists"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def get_board_labels(board_id: str):
    """Obtiene los labels de un board."""
    url = f"{TRELLO_API_BASE}/boards/{board_id}/labels"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def find_or_create_label(board_id: str, label_name: str, color: str = "blue"):
    """Encuentra o crea un label."""
    labels = get_board_labels(board_id)
    
    for label in labels:
        if label.get("name", "").lower() == label_name.lower():
            return label["id"]
    
    # Crear nuevo label
    url = f"{TRELLO_API_BASE}/boards/{board_id}/labels"
    params = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN, "name": label_name, "color": color}
    
    with httpx.Client() as client:
        response = client.post(url, params=params)
        response.raise_for_status()
        return response.json()["id"]


def read_guide_section(task_number: int) -> dict:
    """Lee una sección específica de la guía."""
    guide_path = "/Users/angelo/ReachuSwiftSDK/KOTLIN_IMPLEMENTATION_GUIDE.md"
    
    try:
        with open(guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return None
    
    # Mapeo de tareas agrupadas
    grouped_tasks = {18: "18-19", 19: "18-19", 20: "20-22", 21: "20-22", 22: "20-22", 23: "23-24", 24: "23-24"}
    
    search_pattern = grouped_tasks.get(task_number, str(task_number))
    
    if search_pattern in ["18-19", "20-22", "23-24"]:
        pattern = rf"## {search_pattern}\. (.+?)(?=## \d+\.|$)"
    else:
        pattern = rf"## {task_number}\. (.+?)(?=## \d+\.|$)"
    
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return None
    
    section = match.group(1)
    title_line = section.split('\n')[0].strip()
    
    title_map = {
        18: "Crear componente RProductSpotlight con estructura base",
        19: "Implementar UI del RProductSpotlight con badge highlight",
        20: "Integrar localización en componentes UI (Parte 1)",
        21: "Integrar localización en componentes UI (Parte 2)",
        22: "Integrar localización en componentes UI (Parte 3)",
        23: "Crear modelos de configuración (Parte 1)",
        24: "Crear modelos de configuración (Parte 2)",
    }
    
    title = title_map.get(task_number, title_line if title_line else f"Tarea {task_number}")
    
    sections = {}
    current_section = None
    current_content = []
    
    for line in section.split('\n'):
        if line.startswith('### '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line.replace('### ', '').strip()
            current_content = []
        else:
            current_content.append(line)
    
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return {'title': title, 'sections': sections, 'full_content': section}


def generate_description(task_number: int, task_data: dict) -> str:
    """Genera la descripción de la tarjeta."""
    estimation = TASK_ESTIMATIONS.get(task_number, "2-4 horas")
    dependencies = ", ".join([f"Tarea #{d}" for d in TASK_DEPENDENCIES.get(task_number, [])]) or "Ninguna"
    tags = ", ".join(TASK_TAGS.get(task_number, ["Kotlin"]))
    
    title = task_data['title']
    sections = task_data['sections']
    
    swift_section = sections.get('Cómo funciona en Swift', 'Ver código Swift de referencia.')
    kotlin_section = sections.get('Qué hacer en Kotlin', 'Implementar según especificaciones.')
    files_section = sections.get('Archivos a revisar', 'Ver referencias en la guía.')
    considerations_section = sections.get('Consideraciones importantes', 'Ver consideraciones en la guía.')
    
    context_map = {
        1: "Esta tarea establece la base del sistema de localización del SDK.",
        2: "Define todas las claves de traducción y sus valores por defecto.",
        3: "Permite cargar traducciones desde archivos JSON externos.",
        4: "Integra el sistema de localización en el ConfigurationLoader.",
        5: "Gestiona el estado de las campañas en tiempo real.",
        6: "Obtiene información de la campaña desde el backend.",
        7: "Obtiene los componentes activos de la campaña.",
        8: "Establece conexión WebSocket para actualizaciones en tiempo real.",
        9: "Procesa eventos recibidos por WebSocket.",
        10: "Persiste el estado en cache local.",
        11: "Crea el componente base RProductBanner.",
        12: "Optimiza rendimiento cacheando valores de styling.",
        13: "Implementa la UI completa del banner.",
        14: "Crea el componente base RProductCarousel.",
        15: "Implementa los 3 layouts del carrusel.",
        16: "Crea el componente base RProductStore.",
        17: "Implementa las vistas Grid y List.",
        18: "Crea el componente base RProductSpotlight.",
        19: "Implementa la UI completa del spotlight.",
        20: "Integra localización en componentes UI (Parte 1).",
        21: "Integra localización en componentes UI (Parte 2).",
        22: "Integra localización en componentes UI (Parte 3).",
        23: "Define modelos de configuración (Parte 1).",
        24: "Define modelos de configuración (Parte 2).",
        25: "Define la sealed class Component.",
        26: "Implementa skeleton loaders.",
        27: "Verifica auto-hide de componentes.",
        28: "Verifica soporte para componentId.",
        29: "Crea tests unitarios.",
        30: "Documenta componentes y su uso.",
    }
    
    context = context_map.get(task_number, "Esta tarea es parte de la implementación del SDK Kotlin.")
    
    return f"""## [Tarea #{task_number}] {title}

**⏱️ Estimación:** {estimation} (con AI)
**📋 Dependencias:** {dependencies}
**🏷️ Tags:** {tags}

### Contexto

{context}

### Cómo funciona en Swift

{swift_section}

### Qué hacer en Kotlin

{kotlin_section}

### Archivos a revisar

{files_section}

### Consideraciones importantes

{considerations_section}

### Criterios de aceptación

- [ ] Código implementado y compilando sin errores
- [ ] Tests unitarios pasando (si aplica)
- [ ] Documentación actualizada
- [ ] Revisado por peer
- [ ] Demo funcionando correctamente
- [ ] Cumple con los estándares de código del proyecto

### Preguntas frecuentes

**Q: ¿Qué pasa si encuentro un problema durante la implementación?**  
A: Consulta primero la guía completa (`KOTLIN_IMPLEMENTATION_GUIDE.md`) y el código Swift de referencia.

**Q: ¿Debo seguir exactamente el código Swift?**  
A: Adapta el código Swift a las mejores prácticas de Kotlin y Android, manteniendo la funcionalidad equivalente.

**Q: ¿Cómo verifico que funciona correctamente?**  
A: Ejecuta los tests, prueba en la demo app, y verifica que el comportamiento sea equivalente al Swift SDK.
"""


def create_card(list_id: str, name: str, description: str, label_ids: list = None, member_ids: list = None):
    """Crea una tarjeta en Trello."""
    url = f"{TRELLO_API_BASE}/cards"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "idList": list_id,
        "name": name,
        "desc": description,
    }
    
    if label_ids:
        params["idLabels"] = ",".join(label_ids)
    
    with httpx.Client() as client:
        response = client.post(url, params=params)
        response.raise_for_status()
        card = response.json()
        
        # Agregar miembros después de crear la tarjeta
        if member_ids:
            for member_id in member_ids:
                add_member_url = f"{TRELLO_API_BASE}/cards/{card['id']}/idMembers"
                add_member_params = {
                    "key": TRELLO_API_KEY,
                    "token": TRELLO_TOKEN,
                    "value": member_id
                }
                client.post(add_member_url, params=add_member_params)
        
        return card


def main():
    parser = argparse.ArgumentParser(description="Genera tarjetas de Trello desde la guía de implementación")
    parser.add_argument("--board-id", default=DEFAULT_BOARD_ID, help="ID del board de Trello")
    parser.add_argument("--list-id", help="ID de la lista (si no se proporciona, se busca 'To Do')")
    parser.add_argument("--list-name", default=DEFAULT_LIST_NAME, help="Nombre de la lista a buscar")
    parser.add_argument("--start-task", type=int, default=1, help="Número de tarea inicial")
    parser.add_argument("--end-task", type=int, default=30, help="Número de tarea final")
    
    args = parser.parse_args()
    
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
        sys.exit(1)
    
    # Obtener lista
    if args.list_id:
        list_id = args.list_id
    else:
        lists = get_board_lists(args.board_id)
        list_obj = next((l for l in lists if l["name"] == args.list_name), None)
        if not list_obj:
            print(f"❌ No se encontró la lista '{args.list_name}'")
            sys.exit(1)
        list_id = list_obj["id"]
    
    print(f"📋 Generando tarjetas en lista '{args.list_name}' (ID: {list_id})...\n")
    
    # Obtener o crear labels
    label_cache = {}
    for tag in set(sum(TASK_TAGS.values(), [])):
        label_id = find_or_create_label(args.board_id, tag)
        label_cache[tag] = label_id
    
    success_count = 0
    error_count = 0
    
    for task_num in range(args.start_task, args.end_task + 1):
        print(f"📝 Procesando Tarea #{task_num}...", end=" ")
        
        task_data = read_guide_section(task_num)
        if not task_data:
            print("⚠️  No encontrada en guía")
            error_count += 1
            continue
        
        # Generar descripción
        description = generate_description(task_num, task_data)
        
        # Obtener label IDs
        tags = TASK_TAGS.get(task_num, [])
        label_ids = [label_cache[tag] for tag in tags if tag in label_cache]
        
        # Miembros (todos por defecto)
        member_ids = list(TEAM_MEMBERS.values())
        
        # Crear tarjeta
        try:
            card = create_card(list_id, f"[Tarea #{task_num}] {task_data['title']}", description, label_ids, member_ids)
            print(f"✅ Creada: {card['shortUrl']}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            error_count += 1
        
        time.sleep(0.5)
    
    print(f"\n✅ Completado!")
    print(f"   Exitosas: {success_count}/{args.end_task - args.start_task + 1}")
    print(f"   Errores: {error_count}/{args.end_task - args.start_task + 1}")


if __name__ == "__main__":
    main()

