#!/usr/bin/env python3
"""
Script para crear tarjetas de rebrand Kotlin SDK en la board Dev.
Basado en el plan Trello Dev Board Update.
Crea 9 tarjetas en "To do", asignadas a Alan, con tags.
"""

import os
import sys
import time

# Add parent for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"

# Dev board (To do, Doing lists)
DEV_BOARD_ID = "6964ea21570279f07def7786"
TODO_LIST_NAME = "To do"

# 9 tarjetas Kotlin con descripciones completas
KOTLIN_CARDS = [
    (
        "[Kotlin] Renombrar ReachuConfiguration a VioConfiguration",
        """## Renombrar ReachuConfiguration a VioConfiguration

**Referencia:** Swift SDK ya tiene estos cambios aplicados.

### Archivos
- ReachuConfiguration.kt → VioConfiguration.kt
- Actualizar referencias en ConfigurationLoader, ModuleConfigurations, etc.

### Criterios de aceptación
- [ ] Clase renombrada a VioConfiguration
- [ ] Todas las referencias actualizadas
- [ ] Actualizar KDoc/docs si aplica
""",
        ["Kotlin", "Config", "Rebrand"],
    ),
    (
        "[Kotlin] Renombrar ReachuColors, ReachuShadow, ReachuBorderRadius, ReachuTypography, ReachuSpacing",
        """## Renombrar design tokens

**Referencia:** Swift SDK ya tiene estos cambios aplicados (VioColors, VioShadow, etc.).

### Archivos
- library/io/reachu/ReachuDesignSystem/
- ReachuDesignSystem → VioDesignSystem
- ReachuColors, ReachuShadow, ReachuBorderRadius, ReachuTypography, ReachuSpacing → Vio*

### Criterios de aceptación
- [ ] Design tokens renombrados
- [ ] Referencias actualizadas en todo el SDK
- [ ] Actualizar KDoc/docs si aplica
""",
        ["Kotlin", "Config", "Rebrand"],
    ),
    (
        "[Kotlin] Renombrar ReachuCore y tipos internos",
        """## Renombrar ReachuCore

**Referencia:** Swift SDK ya tiene estos cambios aplicados (VioCore).

### Cambios
- ReachuCore → VioCore
- ReachuLogger → VioLogger
- ColorScheme, Variant si aplican

### Criterios de aceptación
- [ ] ReachuCore → VioCore
- [ ] ReachuLogger → VioLogger
- [ ] Actualizar KDoc/docs si aplica
""",
        ["Kotlin", "Config", "Rebrand"],
    ),
    (
        "[Kotlin] Renombrar ReachuUI y componentes",
        """## Renombrar ReachuUI

**Referencia:** Swift SDK ya tiene estos cambios aplicados.

### Archivos
- ReachuUI.kt, ReachuTheme.kt, ReachuButton.kt, AdaptiveReachuColors.kt → Vio*

### Criterios de aceptación
- [ ] Componentes UI renombrados
- [ ] Referencias actualizadas
- [ ] Actualizar KDoc/docs si aplica
""",
        ["Kotlin", "Rebrand", "SDK"],
    ),
    (
        "[Kotlin] Renombrar ReachuEngagementUI y ReachuEngagementSystem",
        """## Renombrar Engagement modules

**Referencia:** Swift SDK ya tiene estos cambios aplicados.

### Cambios
- ReachuEngagementUI → VioEngagementUI
- ReachuEngagementSystem → VioEngagementSystem

### Criterios de aceptación
- [ ] Módulos renombrados
- [ ] Referencias actualizadas
- [ ] Actualizar KDoc/docs si aplica
""",
        ["Kotlin", "Rebrand", "SDK"],
    ),
    (
        "[Kotlin] Actualizar URLs de configuración a vio.live",
        """## Actualizar URLs a vio.live

**Referencia:** Swift SDK ya tiene estos cambios aplicados.

### Mapeo
- graph-ql-dev.reachu.io → api-ecom.vio.live
- dev-campaing.reachu.io → api-dev.vio.live

### Archivos
- ReachuConfiguration, ModuleConfigurations
- reachu-config.json (demos)

### Criterios de aceptación
- [ ] URLs actualizadas
- [ ] Demos funcionan contra api-dev.vio.live
- [ ] Actualizar KDoc/docs si aplica
""",
        ["Kotlin", "Config", "API", "Rebrand"],
    ),
    (
        "[Kotlin] Actualizar network_security_config y DynamicComponentsService",
        """## Actualizar network y DynamicComponents

### Archivos
1. network_security_config.xml (ReachuAndroidUI)
   - Añadir dominios: api-dev.vio.live, api.vio.live, api-ecom.vio.live

2. DynamicComponentsService.kt
   - URLs api-qa.reachu.io → vio.live

### Criterios de aceptación
- [ ] Dominios vio.live permitidos en Android
- [ ] Componentes dinámicos funcionan
- [ ] Actualizar KDoc/docs si aplica
""",
        ["Kotlin", "Config", "API"],
    ),
    (
        "[Kotlin] Actualizar build.gradle y placeholders (email, etc.)",
        """## Actualizar emails y metadata

### Cambios
- dev@reachu.io → dev@vio.live
- demo@reachu.io → demo@vio.live

### Archivos
- build.gradle.kts (library y ReachuAndroidUI)
- RCheckoutOverlayCompose.kt

### Criterios de aceptación
- [ ] Metadatos y placeholders actualizados
- [ ] Actualizar KDoc/docs si aplica
""",
        ["Kotlin", "Config", "Rebrand"],
    ),
    (
        "[Kotlin] Agregar y actualizar documentación del SDK",
        """## Agregar y actualizar documentación del Kotlin SDK

**Importante:** Alan debe agregar y actualizar la documentación a medida que avance en las demás tareas.

### Incluir
- docs/README.md: URLs vio.live, ejemplos actualizados
- KDoc en clases públicas (VioConfiguration, VioColors, etc.)
- Guía de migración Reachu → Vio
- Nuevos nombres de clases y módulos

### Criterios de aceptación
- [ ] docs/README.md actualizado
- [ ] KDoc en clases principales
- [ ] Guía de migración Reachu→Vio
- [ ] Sin referencias reachu.io en docs
""",
        ["Kotlin", "Documentación", "Rebrand"],
    ),
]


def get_board_lists(board_id: str):
    with httpx.Client() as client:
        r = client.get(
            f"{TRELLO_API_BASE}/boards/{board_id}/lists",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        )
        r.raise_for_status()
        return r.json()


def get_board_members(board_id: str):
    with httpx.Client() as client:
        r = client.get(
            f"{TRELLO_API_BASE}/boards/{board_id}/members",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        )
        r.raise_for_status()
        return r.json()


def find_member_by_name_or_id(board_id: str, assignee: str) -> str | None:
    members = get_board_members(board_id)
    assignee_lower = assignee.lower().strip()
    for m in members:
        mid = m.get("id", "")
        if mid == assignee:
            return mid
        full_name = (m.get("fullName") or "").lower()
        username = (m.get("username") or "").lower()
        if assignee_lower in full_name or assignee_lower in username:
            return mid
    return None


def get_board_labels(board_id: str):
    with httpx.Client() as client:
        r = client.get(
            f"{TRELLO_API_BASE}/boards/{board_id}/labels",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        )
        r.raise_for_status()
        return r.json()


def find_or_create_label(board_id: str, label_name: str, color: str = "blue"):
    labels = get_board_labels(board_id)
    for label in labels:
        if label.get("name", "").lower() == label_name.lower():
            return label["id"]
    with httpx.Client() as client:
        r = client.post(
            f"{TRELLO_API_BASE}/boards/{board_id}/labels",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "name": label_name,
                "color": color,
            },
        )
        r.raise_for_status()
        return r.json()["id"]


def create_card(list_id: str, name: str, description: str, label_ids: list, member_ids: list):
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
        r = client.post(f"{TRELLO_API_BASE}/cards", params=params)
        r.raise_for_status()
        card = r.json()
        if member_ids:
            for mid in member_ids:
                client.post(
                    f"{TRELLO_API_BASE}/cards/{card['id']}/idMembers",
                    params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN, "value": mid},
                )
        return card


def main():
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Configura TRELLO_API_KEY y TRELLO_TOKEN en .env")
        sys.exit(1)

    board_id = DEV_BOARD_ID
    print(f"📋 Board Dev (ID: {board_id})")

    # Resolver Alan
    member_ids = []
    alan_id = find_member_by_name_or_id(board_id, "alanluisvalenzuelasimpson1")
    if not alan_id:
        alan_id = find_member_by_name_or_id(board_id, "Alan")
    if alan_id:
        member_ids = [alan_id]
        print(f"👤 Asignando a Alan")
    else:
        print("⚠️  Alan no encontrado en el board. Tarjetas sin asignar.")

    # Obtener lista To do
    lists = get_board_lists(board_id)
    list_obj = next((l for l in lists if l["name"] == TODO_LIST_NAME), None)
    if not list_obj:
        print(f"❌ Lista '{TODO_LIST_NAME}' no encontrada. Listas: {[l['name'] for l in lists]}")
        sys.exit(1)

    list_id = list_obj["id"]
    print(f"📂 Lista: {TODO_LIST_NAME} (ID: {list_id})\n")

    # Labels
    all_tags = set()
    for _, _, tags in KOTLIN_CARDS:
        all_tags.update(tags)

    label_cache = {}
    for tag in all_tags:
        label_cache[tag] = find_or_create_label(board_id, tag)

    # Crear tarjetas
    success = 0
    for title, desc, tags in KOTLIN_CARDS:
        print(f"📝 {title[:60]}...", end=" ")
        label_ids = [label_cache[t] for t in tags if t in label_cache]
        try:
            card = create_card(list_id, title, desc, label_ids, member_ids)
            print(f"✅ {card['shortUrl']}")
            success += 1
        except Exception as e:
            print(f"❌ {e}")
        time.sleep(0.5)

    print(f"\n✅ {success}/{len(KOTLIN_CARDS)} tarjetas creadas en To do")


if __name__ == "__main__":
    main()
