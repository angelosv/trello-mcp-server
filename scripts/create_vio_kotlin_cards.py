#!/usr/bin/env python3
"""
Script para crear tarjetas de VioKotlinSDK en la board Dev.
Crea 7 tarjetas en "To do", asignadas a Alan, con tags (Kotlin como tag, no en título).
Incluye checklists Trello nativos.
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

# Dev board
DEV_BOARD_ID = "6964ea21570279f07def7786"
TODO_LIST_NAME = "To do"

# 7 tarjetas VioKotlinSDK - títulos SIN [Kotlin], Kotlin es tag
VIO_KOTLIN_CARDS = [
    (
        "Renombrar proyecto root a VioKotlinSDK",
        """## Renombrar proyecto root a VioKotlinSDK

**Referencia:** VioKotlinSDK ya existe como repo; settings.gradle.kts sigue con rootProject.name = "ReachuKotlinSDK".

### Archivos
- settings.gradle.kts: rootProject.name = "VioKotlinSDK"
- Actualizar referencias en build, CI, README

### Criterios de aceptación
- [ ] rootProject.name cambiado a VioKotlinSDK
- [ ] README y build actualizados
- [ ] Demos verificados tras el cambio
""",
        ["Kotlin", "Config", "Rebrand"],
        ["Cambiar rootProject.name en settings.gradle.kts", "Actualizar README y referencias build", "Verificar que demos compilan"],
    ),
    (
        "Implementar flujo contentId en SDK",
        """## Implementar flujo contentId en SDK

**Referencia:** Backend tiene GET /v1/sdk/broadcast?contentId=xxx&country=yyy. Swift SDK tiene plan; Kotlin debe implementar paridad.

### Flujo
1. App abre stream con contentId + country
2. SDK llama GET /v1/sdk/broadcast
3. Si hasEngagement=false: no mostrar engagement
4. Si hasEngagement=true: usar broadcastId de respuesta para polls/contests

### Criterios de aceptación
- [ ] BroadcastValidationService creado
- [ ] BroadcastValidationResult model
- [ ] Integración en video player / setup
- [ ] Usar campaignApiKey de config
""",
        ["Kotlin", "SDK", "API", "priority-high"],
        ["Crear BroadcastValidationService", "Crear BroadcastValidationResult", "Integrar en video player/setup", "Usar campaignApiKey"],
    ),
    (
        "Crear BroadcastValidationService y BroadcastValidationResult",
        """## Crear BroadcastValidationService y BroadcastValidationResult

**Referencia:** Endpoint GET /v1/sdk/broadcast en api-dev.vio.live.

### Servicio
- Llamar GET /v1/sdk/broadcast?contentId=&country=
- Header X-Api-Key con campaignApiKey (o apiKey si no definido)

### Modelo BroadcastValidationResult
- hasEngagement, broadcastId, broadcastName, status
- campaignId, websocketChannel
- campaignComponents, broadcastComponents (polls, contests, chat)

### Criterios de aceptación
- [ ] BroadcastValidationService con validate(contentId, country)
- [ ] BroadcastValidationResult model
- [ ] Usar campaignApiKey de VioConfiguration
""",
        ["Kotlin", "SDK", "API"],
        ["Crear BroadcastValidationService.kt", "Crear BroadcastValidationResult en CampaignModels", "Usar campaignApiKey de config"],
    ),
    (
        "Añadir campaignApiKey en CampaignConfiguration y vio-config",
        """## Añadir campaignApiKey en CampaignConfiguration y vio-config

**Referencia:** Para contentId flow se usa API key distinta (ej. viaplay_api_key_...). Swift SDK plan incluye campaignApiKey.

### Cambios
- ModuleConfigurations.kt: CampaignConfiguration.campaignApiKey (nullable)
- ConfigurationLoader: cargar campaignApiKey desde campaigns.campaignApiKey
- vio-config.json demos: añadir campaignApiKey cuando aplique

### Criterios de aceptación
- [ ] CampaignConfiguration con campaignApiKey
- [ ] ConfigurationLoader actualizado
- [ ] vio-config demos con campaignApiKey
- [ ] BroadcastValidationService usa campaignApiKey si definido
""",
        ["Kotlin", "Config", "API"],
        ["Añadir campaignApiKey a CampaignConfiguration", "Actualizar ConfigurationLoader", "Añadir en vio-config demos", "Usar en BroadcastValidationService"],
    ),
    (
        "Añadir VioSessionContext (contexto de sesión por broadcast)",
        """## Añadir VioSessionContext (contexto de sesión por broadcast)

**Referencia:** Swift SDK tiene VioSessionContext inyectable con userId y broadcastContext para multi-sesión.

### Modelo
- Clase VioSessionContext (no singleton)
- Propiedades: userId, broadcastContext
- Inyectable en video player, overlay, engagement components

### Integración
- EngagementRepository/EngagementRepositoryBackend debe usar userId de sesión
- Fallback a UUID local si userId es null

### Criterios de aceptación
- [ ] VioSessionContext creado
- [ ] Inyectar en TV2VideoPlayer / overlay
- [ ] EngagementManager/Repository usa userId de sesión
""",
        ["Kotlin", "SDK", "Config"],
        ["Crear VioSessionContext.kt", "Inyectar en video player/overlay", "Conectar EngagementManager/Repository a userId"],
    ),
    (
        "Integrar rama contentId en setupMatchContext / video player",
        """## Integrar rama contentId en setupMatchContext / video player

**Referencia:** Si la app pasa contentId + country, validar antes de discoverCampaigns.

### Lógica
- Si contentId + country provistos: llamar BroadcastValidationService.validate()
- Si hasEngagement=false: no discoverCampaigns, no loadEngagement
- Si hasEngagement=true: crear BroadcastContext con broadcastId de respuesta, setMatchContext, discoverCampaigns, loadEngagement
- Mantener flujo legacy con matchId cuando no hay contentId

### Archivos
- TV2VideoPlayer.kt: setupMatchContext()
- ViaplayDemoApp: ejemplo con contentId para Real Madrid - Barcelona

### Criterios de aceptación
- [ ] Rama contentId en setupMatchContext
- [ ] ViaplayDemoApp con flujo contentId
- [ ] Flujo legacy matchId intacto
""",
        ["Kotlin", "SDK"],
        ["Rama contentId en TV2VideoPlayer/setupMatchContext", "ViaplayDemoApp con contentId", "Mantener flujo legacy matchId"],
    ),
    (
        "Actualizar documentación del SDK",
        """## Actualizar documentación del SDK

**Referencia:** tareas.txt del repo; guía migración Reachu→Vio.

### Incluir
- docs/README.md: URLs vio.live, ejemplos actualizados
- KDoc en clases públicas (VioConfiguration, VioColors, BroadcastValidationService, etc.)
- Guía de migración Reachu → Vio
- Ejemplos de flujo contentId

### Criterios de aceptación
- [ ] docs/README.md actualizado
- [ ] KDoc en clases principales
- [ ] Guía de migración Reachu→Vio
- [ ] Ejemplos contentId
- [ ] Sin referencias reachu.io en docs
""",
        ["Kotlin", "Documentación", "Rebrand"],
        ["Actualizar docs/README.md", "KDoc en clases principales", "Guía migración Reachu→Vio", "Ejemplos contentId", "Eliminar referencias reachu.io"],
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


def create_checklist(card_id: str, name: str, items: list):
    """Create Trello checklist with items."""
    with httpx.Client() as client:
        r = client.post(
            f"{TRELLO_API_BASE}/checklists",
            params={
                "key": TRELLO_API_KEY,
                "token": TRELLO_TOKEN,
                "idCard": card_id,
                "name": name,
            },
        )
        r.raise_for_status()
        checklist = r.json()
        checklist_id = checklist["id"]

        for item in items:
            client.post(
                f"{TRELLO_API_BASE}/checklists/{checklist_id}/checkItems",
                params={
                    "key": TRELLO_API_KEY,
                    "token": TRELLO_TOKEN,
                    "name": item,
                },
            )
            time.sleep(0.2)
        return checklist_id


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
    for _, _, tags, _ in VIO_KOTLIN_CARDS:
        all_tags.update(tags)

    label_cache = {}
    for tag in all_tags:
        color = "red" if tag == "priority-high" else "blue"
        label_cache[tag] = find_or_create_label(board_id, tag, color=color)

    # Crear tarjetas
    success = 0
    for title, desc, tags, checklist_items in VIO_KOTLIN_CARDS:
        print(f"📝 {title[:50]}...", end=" ")
        label_ids = [label_cache[t] for t in tags if t in label_cache]
        try:
            card = create_card(list_id, title, desc, label_ids, member_ids)
            if checklist_items:
                create_checklist(card["id"], "Tareas", checklist_items)
            print(f"✅ {card['shortUrl']}")
            success += 1
        except Exception as e:
            print(f"❌ {e}")
        time.sleep(0.5)

    print(f"\n✅ {success}/{len(VIO_KOTLIN_CARDS)} tarjetas creadas en To do")


if __name__ == "__main__":
    main()
