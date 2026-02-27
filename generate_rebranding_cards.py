#!/usr/bin/env python3
"""
Script para crear tarjetas de Trello del rebranding vio.live (solo SDK Kotlin)

Uso:
  python3 generate_rebranding_cards.py              # Crea las 5 tarjetas nuevas
  python3 generate_rebranding_cards.py --replace    # Archiva las antiguas y crea las nuevas

Mapeo de URLs:
- Campaign: dev = api-dev.vio.live, prod = api.vio.live
- Reachu/Ecom: dev = api-ecom.vio.live, prod = api-ecom.vio.live
"""

import os
import sys
import httpx
import time
import argparse
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"

DEFAULT_BOARD_ID = "5dea6d99c0ea505b4c3a435e"  # Reachu Dev
DEFAULT_LIST_NAME = "To do"

# Tarjetas agrupadas (sin [Kotlin] en título - se usan tags)
REBRANDING_CARDS = [
    (
        "Actualizar URLs de configuración (ReachuEnvironment, Campaign, configs)",
        """## Actualizar URLs de configuración para vio.live

**⏱️ Estimación:** 3-4 horas
**🏷️ Tags:** Kotlin, API, Config, WebSocket

### Por qué está agrupado
Todas estas URLs forman la configuración base del SDK. Cambiarlas juntas evita inconsistencias entre entornos.

### Mapeo de URLs
- **Campaign:** dev = api-dev.vio.live, prod = api.vio.live
- **Ecom/GraphQL:** dev y prod = api-ecom.vio.live

### Archivos y cambios

**1. ReachuConfiguration.kt** (líneas 168-174)
- DEVELOPMENT: `graph-ql-dev.reachu.io` → `api-ecom.vio.live`
- SANDBOX: `api-sandbox.reachu.io` → `api-ecom.vio.live`
- PRODUCTION: `api.reachu.io` → `api-ecom.vio.live`

**2. ModuleConfigurations.kt** (líneas 286-288)
- webSocketBaseURL, restAPIBaseURL: `dev-campaing.reachu.io` → `api-dev.vio.live` (dev), `api.vio.live` (prod)

**3. reachu-config.json** (3 demos: TV2DemoApp, ReachuDemoApp, LiveShoppingDemo)
- webSocketBaseURL, restAPIBaseURL → `api-dev.vio.live`

**4. reachu-config-example.json + DemoConfigurationLoader.kt**
- graph-ql-qa/prod.reachu.io → api-ecom.vio.live

### Criterios de aceptación
- [ ] Todas las configs apuntan a vio.live
- [ ] Demos funcionan contra api-dev.vio.live
""",
        ["Kotlin", "API", "Config", "WebSocket"],
    ),
    (
        "Actualizar URLs de red y componentes dinámicos",
        """## Actualizar URLs de red y componentes dinámicos

**⏱️ Estimación:** 1-2 horas
**🏷️ Tags:** Kotlin, API, Config

### Por qué está agrupado
Ambos cambios permiten que la app conecte a los nuevos dominios vio.live (network_security) y que los componentes dinámicos consuman el API correcto.

### Archivos y cambios

**1. network_security_config.xml** (ReachuAndroidUI)
- Añadir dominios: api-dev.vio.live, api.vio.live, api-ecom.vio.live

**2. DynamicComponentsService.kt** (línea 17)
- `api-qa.reachu.io/api/components/stream/$streamId` → URL equivalente vio.live

### Criterios de aceptación
- [ ] Dominios vio.live permitidos en Android
- [ ] Componentes dinámicos funcionan
""",
        ["Kotlin", "API", "Config"],
    ),
    (
        "Actualizar documentación con URLs vio.live",
        """## Actualizar documentación con URLs vio.live

**⏱️ Estimación:** 1-2 horas
**🏷️ Tags:** Kotlin, Documentación

### Archivo
- `docs/README.md`

### Cambios
- successUrl, cancelUrl: `dev.reachu.io/...` → vio.live
- baseUrl GraphQL: graph-ql-dev/qa/prod.reachu.io → api-ecom.vio.live
- href checkout: `dev.reachu.io/checkout` → vio.live

### Criterios de aceptación
- [ ] Documentación sin referencias reachu.io
- [ ] Ejemplos con URLs correctas
""",
        ["Kotlin", "Documentación"],
    ),
    (
        "Actualizar emails y metadata de rebrand",
        """## Actualizar emails y metadata de rebrand

**⏱️ Estimación:** 30 min
**🏷️ Tags:** Kotlin, Config, UX/UI

### Por qué está agrupado
Son cambios menores de texto (emails, placeholders) que completan el rebrand.

### Archivos y cambios

**1. build.gradle.kts** (library y ReachuAndroidUI)
- email.set("dev@reachu.io") → dev@vio.live

**2. RCheckoutOverlayCompose.kt** (línea 2073)
- draft.email.ifBlank { "demo@reachu.io" } → "demo@vio.live"

### Criterios de aceptación
- [ ] Metadatos y placeholders actualizados
""",
        ["Kotlin", "Config", "UX/UI"],
    ),
    (
        "Estrategia de repos: Reachu en repo actual, nuevo código en repo nueva",
        """## Estrategia de repositorios

**⏱️ Estimación:** Lectura / contexto
**🏷️ Tags:** Kotlin, Documentación

### Resumen

- **Repo actual (ReachuKotlinSDK):** Mantener el release de Reachu tal cual. Los cambios de rebrand (vio.live) se hacen aquí para la migración.

- **Repo nueva:** Todo el código nuevo de vio.live irá en una nueva repositorio. El SDK de Reachu queda congelado/estable en su repo; el desarrollo futuro de vio.live se hace en el nuevo repo.

### Implicaciones
- Los cambios de rebrand en este board se aplican al repo actual para poder lanzar la versión que apunta a vio.live.
- Después de ese release, el desarrollo de vio.live continúa en la nueva repo.
""",
        ["Kotlin", "Documentación"],
    ),
]


def get_boards():
    """Obtiene todos los boards del usuario."""
    with httpx.Client() as client:
        r = client.get(
            f"{TRELLO_API_BASE}/members/me/boards",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN, "filter": "open"},
        )
        r.raise_for_status()
        return r.json()


def get_board_members(board_id: str):
    """Obtiene los miembros de un board."""
    with httpx.Client() as client:
        r = client.get(
            f"{TRELLO_API_BASE}/boards/{board_id}/members",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        )
        r.raise_for_status()
        return r.json()


def find_member_by_name_or_id(board_id: str, assignee: str) -> str | None:
    """
    Busca un miembro por nombre (fullName o username) o por ID.
    Retorna el member ID o None si no se encuentra.
    """
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


def find_board_by_name(name: str):
    """Busca un board por nombre (case-insensitive, contiene)."""
    boards = get_boards()
    name_lower = name.lower()
    for b in boards:
        if name_lower in b.get("name", "").lower():
            return b["id"]
    return None


def get_board_lists(board_id: str):
    with httpx.Client() as client:
        r = client.get(
            f"{TRELLO_API_BASE}/boards/{board_id}/lists",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        )
        r.raise_for_status()
        return r.json()


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


def get_list_cards(list_id: str):
    """Obtiene las tarjetas de una lista."""
    with httpx.Client() as client:
        r = client.get(
            f"{TRELLO_API_BASE}/lists/{list_id}/cards",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN},
        )
        r.raise_for_status()
        return r.json()


def update_card(card_id: str, name: str, description: str, label_ids=None):
    """Actualiza una tarjeta existente."""
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "name": name,
        "desc": description,
    }
    if label_ids:
        params["idLabels"] = ",".join(label_ids)
    with httpx.Client() as client:
        r = client.put(f"{TRELLO_API_BASE}/cards/{card_id}", params=params)
        r.raise_for_status()
        return r.json()


def archive_card(card_id: str):
    """Archiva una tarjeta."""
    with httpx.Client() as client:
        r = client.put(
            f"{TRELLO_API_BASE}/cards/{card_id}",
            params={"key": TRELLO_API_KEY, "token": TRELLO_TOKEN, "closed": "true"},
        )
        r.raise_for_status()
        return r.json()


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


# Patrones para identificar tarjetas de rebranding (antiguas o nuevas)
REBRAND_CARD_PATTERNS = [
    "[Kotlin]",
    "Actualizar ReachuEnvironment",
    "Actualizar CampaignConfiguration",
    "Actualizar reachu-config",
    "Actualizar docs/README",
    "Actualizar network_security",
    "Actualizar DynamicComponentsService",
    "Actualizar reachu-config-example",
    "Actualizar build.gradle",
    "Actualizar RCheckoutOverlayCompose",
    "Actualizar URLs de configuración",
    "Actualizar URLs de red",
    "Actualizar documentación",
    "Actualizar emails y metadata",
    "Estrategia de repos",
]


def is_rebrand_card(card_name: str) -> bool:
    """Indica si una tarjeta es de rebranding (antigua o nueva)."""
    name = card_name or ""
    return any(p in name for p in REBRAND_CARD_PATTERNS)


def main():
    parser = argparse.ArgumentParser(description="Crea o actualiza tarjetas de rebranding vio.live (Kotlin) en Trello")
    parser.add_argument("--board-id", help="ID del board (alternativa a --board-name)")
    parser.add_argument("--board-name", default="dev", help="Nombre del board a buscar (default: dev)")
    parser.add_argument("--list-name", default=DEFAULT_LIST_NAME, help="Nombre de la lista (default: To do)")
    parser.add_argument(
        "--assignee",
        default="alanluisvalenzuelasimpson1",
        help="Username, nombre o ID del miembro a asignar (default: alanluisvalenzuelasimpson1). Pasar vacío para no asignar.",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Archiva las tarjetas de rebrand existentes y crea las nuevas (agrupadas). Usar para aplicar los cambios.",
    )
    args = parser.parse_args()

    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Configura TRELLO_API_KEY y TRELLO_TOKEN en .env")
        sys.exit(1)

    # Resolver board ID
    if args.board_id:
        board_id = args.board_id
        print(f"📋 Usando board ID: {board_id}")
    else:
        board_id = find_board_by_name(args.board_name)
        if not board_id:
            print(f"❌ No se encontró board con nombre que contenga '{args.board_name}'")
            print("   Usa --board-id para especificar el ID directamente")
            sys.exit(1)
        print(f"📋 Board encontrado: {args.board_name} (ID: {board_id})")

    # Resolver assignee
    member_ids = []
    if args.assignee and args.assignee.strip():
        assignee_id = find_member_by_name_or_id(board_id, args.assignee.strip())
        if assignee_id:
            member_ids = [assignee_id]
            print(f"👤 Asignando a: {args.assignee}")
        else:
            print(f"⚠️  No se encontró miembro '{args.assignee}' en el board. Tarjetas sin asignar.")

    # Obtener lista
    lists = get_board_lists(board_id)
    list_obj = next((l for l in lists if l["name"] == args.list_name), None)
    if not list_obj:
        print(f"❌ Lista '{args.list_name}' no encontrada. Listas disponibles: {[l['name'] for l in lists]}")
        sys.exit(1)

    list_id = list_obj["id"]

    # Modo --replace: archivar tarjetas antiguas y crear las nuevas
    if args.replace:
        print(f"\n🔄 Modo --replace: archivando tarjetas de rebrand existentes...\n")
        cards = get_list_cards(list_id)
        rebrand_cards = [c for c in cards if is_rebrand_card(c.get("name", ""))]
        archived = 0
        for card in rebrand_cards:
            try:
                archive_card(card["id"])
                print(f"   📦 Archivada: {card['name'][:50]}...")
                archived += 1
                time.sleep(0.3)
            except Exception as e:
                print(f"   ❌ Error archivando '{card.get('name', '')}': {e}")
        print(f"\n   {archived} tarjetas archivadas.\n")

    print(f"📝 Creando tarjetas en lista '{args.list_name}'...\n")

    # Labels
    label_cache = {}
    for tag in set(sum([c[2] for c in REBRANDING_CARDS], [])):
        label_cache[tag] = find_or_create_label(board_id, tag)

    success = 0

    for title, desc, tags in REBRANDING_CARDS:
        print(f"📝 {title[:55]}...", end=" ")
        label_ids = [label_cache[t] for t in tags if t in label_cache]
        try:
            card = create_card(list_id, title, desc, label_ids, member_ids)
            print(f"✅ {card['shortUrl']}")
            success += 1
        except Exception as e:
            print(f"❌ {e}")
        time.sleep(0.5)

    print(f"\n✅ {success}/{len(REBRANDING_CARDS)} tarjetas creadas")


if __name__ == "__main__":
    main()
