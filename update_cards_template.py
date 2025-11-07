#!/usr/bin/env python3
"""
Script para actualizar las tarjetas de Trello con el template mejorado
y estimaciones de tiempo considerando uso de AI.
"""

import os
import sys
import httpx
import re
import time
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"
BOARD_ID = "5dea6d99c0ea505b4c3a435e"

# Mapeo de tareas a estimaciones (en horas, considerando uso de AI)
TASK_ESTIMATIONS = {
    1: "2-3 horas",  # Estructura base de localización
    2: "3-4 horas",  # Enum con 130+ traducciones (más trabajo manual)
    3: "2-3 horas",  # Carga desde JSON
    4: "2-3 horas",  # Integración en ConfigurationLoader
    5: "3-4 horas",  # CampaignManager singleton
    6: "2-3 horas",  # Fetch campaña REST API
    7: "3-4 horas",  # Fetch componentes REST API
    8: "5-6 horas",  # WebSocket (más complejo)
    9: "4-5 horas",  # Handlers WebSocket
    10: "3-4 horas",  # CacheManager
    11: "3-4 horas",  # RProductBanner estructura
    12: "2-3 horas",  # Caching styling
    13: "5-6 horas",  # UI RProductBanner (más complejo)
    14: "2-3 horas",  # RProductCarousel estructura
    15: "4-5 horas",  # 3 layouts carousel
    16: "2-3 horas",  # RProductStore estructura
    17: "3-4 horas",  # Grid y List views
    18: "3-4 horas",  # RProductSpotlight estructura
    19: "4-5 horas",  # UI RProductSpotlight
    20: "2-3 horas",  # Integración localización componentes
    21: "2-3 horas",  # Más integración localización
    22: "2-3 horas",  # Final integración localización
    23: "2-3 horas",  # Modelos configuración
    24: "2-3 horas",  # Más modelos
    25: "2-3 horas",  # Component sealed class
    26: "2-3 horas",  # Skeleton loaders
    27: "1-2 horas",  # Auto-hide verificación
    28: "1-2 horas",  # Soporte componentId verificación
    29: "6-8 horas",  # Tests (más trabajo)
    30: "4-6 horas",  # Documentación
}

# Dependencias entre tareas
TASK_DEPENDENCIES = {
    1: [],
    2: [1],
    3: [1, 2],
    4: [1, 2, 3],
    5: [],
    6: [5],
    7: [5, 6],
    8: [5, 6],
    9: [5, 8],
    10: [5, 6, 7],
    11: [5, 7, 10],
    12: [11],
    13: [11, 12],
    14: [5, 7, 10],
    15: [14],
    16: [5, 7, 10],
    17: [16],
    18: [5, 7, 10],
    19: [18],
    20: [1, 2, 3, 4, 11, 13],
    21: [1, 2, 3, 4, 14, 15],
    22: [1, 2, 3, 4, 16, 17, 18, 19],
    23: [11, 14, 16, 18],
    24: [23],
    25: [23, 24],
    26: [11, 14, 16, 18],
    27: [11, 14, 15, 16, 17, 18, 19],
    28: [11, 14, 16, 18],
    29: [5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19],
    30: [11, 13, 14, 15, 16, 17, 18, 19],
}

# Tags por tarea
TASK_TAGS = {
    1: ["Kotlin", "Backend", "Localización", "Prioridad"],
    2: ["Kotlin", "Backend", "Localización", "Prioridad"],
    3: ["Kotlin", "Backend", "Localización"],
    4: ["Kotlin", "Backend", "Localización"],
    5: ["Kotlin", "Backend", "Prioridad"],
    6: ["Kotlin", "Backend", "API"],
    7: ["Kotlin", "Backend", "API"],
    8: ["Kotlin", "Backend", "WebSocket", "Prioridad"],
    9: ["Kotlin", "Backend", "WebSocket"],
    10: ["Kotlin", "Backend", "Cache"],
    11: ["Kotlin", "UX/UI", "Prioridad"],
    12: ["Kotlin", "UX/UI"],
    13: ["Kotlin", "UX/UI", "Prioridad"],
    14: ["Kotlin", "UX/UI"],
    15: ["Kotlin", "UX/UI"],
    16: ["Kotlin", "UX/UI"],
    17: ["Kotlin", "UX/UI"],
    18: ["Kotlin", "UX/UI"],
    19: ["Kotlin", "UX/UI"],
    20: ["Kotlin", "UX/UI", "Localización"],
    21: ["Kotlin", "UX/UI", "Localización"],
    22: ["Kotlin", "UX/UI", "Localización"],
    23: ["Kotlin", "Backend"],
    24: ["Kotlin", "Backend"],
    25: ["Kotlin", "Backend"],
    26: ["Kotlin", "UX/UI"],
    27: ["Kotlin", "UX/UI"],
    28: ["Kotlin", "UX/UI"],
    29: ["Kotlin", "Testing"],
    30: ["Kotlin", "Documentación"],
}

# IDs de las tarjetas existentes (en orden)
CARD_IDS = [
    "690df9893a3db5cc11835542", "690df98ce9522bba4c64351d", "690df98d7928e825118584a0",
    "690df98ed8907330ae06a7a6", "690df98ff0737ff7aafa67b4", "690df98fe2903bd00a232941",
    "690df990f75c1756a635afec", "690df991b1f430dab2c0edd2", "690df99140a13f6c6c2c5a0c",
    "690df992073c5486b5faf96d", "690df993c8c05c26d9757cd6", "690df996bac4defd7561e1c3",
    "690df996aacaa51018c032b9", "690df9970ada3fc754d483c9", "690df998ee6d9fbe60763e9d",
    "690df9999f31537df86af6fc", "690df99ac182d7c1eecef2de", "690df99a368ac558dd33e20a",
    "690df99be2ae446d6ed3d520", "690df99caad17cd24095a337", "690df99de24358e9c3974d7e",
    "690df9a04323d1f4a8cecffc", "690df9a131eba60b2907ede3", "690df9a1adbb5c2aed5cfd76",
    "690df9a2e6e6076b8b5bd259", "690df9a3cee74ec9b268a1f1", "690df9a40315d439df7120a4",
    "690df9a5fdc97003412dcc4d", "690df9a536ba6108de3cb492", "690df9a665fdbbbd29b9bbd6",
]


def read_guide_section(task_number: int) -> dict:
    """Lee una sección específica de la guía."""
    guide_path = "/Users/angelo/ReachuSwiftSDK/KOTLIN_IMPLEMENTATION_GUIDE.md"
    
    try:
        with open(guide_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo de guía: {guide_path}")
        return None
    
    # Mapeo de tareas agrupadas
    grouped_tasks = {
        18: "18-19",
        19: "18-19",
        20: "20-22",
        21: "20-22",
        22: "20-22",
        23: "23-24",
        24: "23-24",
    }
    
    # Buscar patrón de tarea agrupada o individual
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
    
    # Títulos específicos para tareas agrupadas
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
    
    # Extraer subsecciones
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
    
    return {
        'title': title,
        'sections': sections,
        'full_content': section
    }


def format_dependencies(deps: list) -> str:
    """Formatea las dependencias como string."""
    if not deps:
        return "Ninguna"
    return ", ".join([f"Tarea #{d}" for d in deps])


def format_tags(tags: list) -> str:
    """Formatea los tags como string."""
    return ", ".join(tags)


def generate_new_description(task_number: int, task_data: dict) -> str:
    """Genera la nueva descripción con el template mejorado."""
    estimation = TASK_ESTIMATIONS.get(task_number, "2-4 horas")
    dependencies = format_dependencies(TASK_DEPENDENCIES.get(task_number, []))
    tags = format_tags(TASK_TAGS.get(task_number, ["Kotlin"]))
    
    title = task_data['title']
    sections = task_data['sections']
    
    # Obtener contenido de cada sección
    swift_section = sections.get('Cómo funciona en Swift', 'Ver código Swift de referencia en la guía completa.')
    kotlin_section = sections.get('Qué hacer en Kotlin', 'Implementar según especificaciones en la guía completa.')
    files_section = sections.get('Archivos a revisar', 'Ver referencias en la guía completa.')
    considerations_section = sections.get('Consideraciones importantes', 'Ver consideraciones en la guía completa.')
    
    # Contexto basado en el número de tarea
    context_map = {
        1: "Esta tarea establece la base del sistema de localización del SDK. Sin esto, no se pueden mostrar textos traducidos.",
        2: "Define todas las claves de traducción y sus valores por defecto. Es fundamental para que el sistema de localización funcione.",
        3: "Permite cargar traducciones desde archivos JSON externos, dando flexibilidad para actualizar traducciones sin recompilar.",
        4: "Integra el sistema de localización en el ConfigurationLoader, permitiendo que se configure automáticamente al inicializar el SDK.",
        5: "Gestiona el estado de las campañas en tiempo real. Es el corazón del sistema de campañas y componentes dinámicos.",
        6: "Obtiene información de la campaña desde el backend, permitiendo saber si está activa, pausada o terminada.",
        7: "Obtiene los componentes activos de la campaña, que son los que se mostrarán en la UI.",
        8: "Establece conexión WebSocket para recibir actualizaciones en tiempo real de la campaña y sus componentes.",
        9: "Procesa los eventos recibidos por WebSocket y actualiza el estado de la campaña y componentes.",
        10: "Persiste el estado de campañas y componentes en cache local, permitiendo carga rápida al iniciar la app.",
        11: "Crea el componente base RProductBanner que muestra banners de productos promocionales.",
        12: "Optimiza el rendimiento cacheando valores de styling parseados, evitando recalcular en cada render.",
        13: "Implementa la UI completa del banner con imagen, overlay, texto y botón, siguiendo el diseño del Swift SDK.",
        14: "Crea el componente base RProductCarousel para mostrar carruseles de productos.",
        15: "Implementa los 3 layouts del carrusel (full, compact, horizontal) con auto-scroll opcional.",
        16: "Crea el componente base RProductStore para mostrar tiendas de productos.",
        17: "Implementa las vistas Grid y List del store, permitiendo diferentes formas de visualizar productos.",
        18: "Crea el componente base RProductSpotlight para destacar productos específicos.",
        19: "Implementa la UI completa del spotlight con badge highlight y diseño especial.",
        20: "Integra el sistema de localización en los componentes UI, reemplazando strings hardcodeados.",
        21: "Continúa la integración de localización en más componentes UI.",
        22: "Completa la integración de localización en todos los componentes restantes.",
        23: "Define los modelos de configuración para los componentes, permitiendo parsear JSON del backend.",
        24: "Completa los modelos de configuración restantes.",
        25: "Define la sealed class Component que representa todos los tipos de componentes posibles.",
        26: "Implementa skeleton loaders para mostrar mientras cargan los componentes, mejorando UX.",
        27: "Verifica que todos los componentes implementen correctamente el auto-hide cuando no deben mostrarse.",
        28: "Verifica que todos los componentes soporten el parámetro componentId para mostrar componentes específicos.",
        29: "Crea tests unitarios para asegurar que toda la funcionalidad funciona correctamente.",
        30: "Documenta todos los componentes y su uso, facilitando la integración por parte de otros desarrolladores.",
    }
    
    context = context_map.get(task_number, "Esta tarea es parte de la implementación del SDK Kotlin basado en el SDK Swift.")
    
    # Construir la nueva descripción
    desc = f"""## [Tarea #{task_number}] {title}

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
A: Consulta primero la guía completa (`KOTLIN_IMPLEMENTATION_GUIDE.md`) y el código Swift de referencia. Si persiste, documenta el problema y busca ayuda.

**Q: ¿Debo seguir exactamente el código Swift?**  
A: Adapta el código Swift a las mejores prácticas de Kotlin y Android, manteniendo la funcionalidad equivalente. Usa coroutines en lugar de async/await, StateFlow en lugar de @Published, etc.

**Q: ¿Cómo verifico que funciona correctamente?**  
A: Ejecuta los tests, prueba en la demo app, y verifica que el comportamiento sea equivalente al Swift SDK. Compara visualmente con el demo de Swift si es un componente UI.
"""
    
    return desc


def update_card(card_id: str, description: str):
    """Actualiza la descripción de una tarjeta usando POST con JSON body."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}"
    
    # Usar POST con JSON body para evitar límite de tamaño en query params
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    
    data = {
        "desc": description
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            # Usar PUT con JSON body
            response = client.put(url, params=params, json=data)
            if response.status_code == 200:
                return True
            else:
                print(f"   Error HTTP {response.status_code}: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"   Excepción: {str(e)}")
        return False


def main():
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados en .env")
        sys.exit(1)
    
    print("🔄 Actualizando tarjetas con template mejorado...\n")
    
    success_count = 0
    error_count = 0
    
    for task_num in range(1, 31):
        card_id = CARD_IDS[task_num - 1]
        
        print(f"📝 Procesando Tarea #{task_num}...", end=" ")
        
        # Leer datos de la guía
        task_data = read_guide_section(task_num)
        
        if not task_data:
            print(f"⚠️  No se encontró la tarea #{task_num} en la guía")
            error_count += 1
            continue
        
        # Generar nueva descripción
        new_description = generate_new_description(task_num, task_data)
        
        # Actualizar tarjeta
        if update_card(card_id, new_description):
            print(f"✅")
            success_count += 1
        else:
            print(f"❌ Error")
            error_count += 1
        
        # Rate limiting
        time.sleep(0.5)
    
    print(f"\n✅ Completado!")
    print(f"   Exitosas: {success_count}/30")
    print(f"   Errores: {error_count}/30")


if __name__ == "__main__":
    main()

