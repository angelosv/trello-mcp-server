#!/usr/bin/env python3
"""
Script para agregar etiquetas y asignaciones a las tarjetas de Trello creadas.
"""

import os
import sys
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"

# IDs de etiquetas
LABELS = {
    "kotlin": "68d44d0bba63fd0d88249ce0",
    "prioridad": "5dea6d998bdee58e0ddd1688",
    "reachu": "665854fedd97ae78fc195cc3",
    "backend": "5dea6d998bdee58e0ddd1691",
    "new_functionality": "652692a9becaf9e71091cb65",
    "ux_ui": "66b48ca61d8c470eb07fd108",
    "refactoring": "5f96eb51155fd25ee7ffd63a",
    "testing": "60112d196dc58e8c298ad573",
    "documentation": "634e7874434fcc009b8f56ec",
}

# ID de Miguel
MIGUEL_ID = "619f90698c4fc547cc133149"

# Mapeo de tarjetas con sus etiquetas y asignaciones
CARDS_CONFIG = {
    # Tarea 1: Estructura base de localización
    "690df9893a3db5cc11835542": {
        "labels": ["kotlin", "prioridad", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 2: Enum ReachuTranslationKey
    "690df98ce9522bba4c64351d": {
        "labels": ["kotlin", "prioridad", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 3: Carga desde archivo JSON
    "690df98d7928e825118584a0": {
        "labels": ["kotlin", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 4: Integración en ConfigurationLoader
    "690df98ed8907330ae06a7a6": {
        "labels": ["kotlin", "prioridad", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 5: CampaignManager singleton
    "690df98ff0737ff7aafa67b4": {
        "labels": ["kotlin", "prioridad", "reachu", "backend"],
        "member": MIGUEL_ID
    },
    # Tarea 6: Fetch campaña
    "690df98fe2903bd00a232941": {
        "labels": ["kotlin", "prioridad", "reachu", "backend"],
        "member": MIGUEL_ID
    },
    # Tarea 7: Fetch componentes
    "690df990f75c1756a635afec": {
        "labels": ["kotlin", "prioridad", "reachu", "backend"],
        "member": MIGUEL_ID
    },
    # Tarea 8: WebSocket
    "690df991b1f430dab2c0edd2": {
        "labels": ["kotlin", "prioridad", "reachu", "backend"],
        "member": MIGUEL_ID
    },
    # Tarea 9: Handlers WebSocket
    "690df99140a13f6c6c2c5a0c": {
        "labels": ["kotlin", "prioridad", "reachu", "backend"],
        "member": MIGUEL_ID
    },
    # Tarea 10: CacheManager
    "690df992073c5486b5faf96d": {
        "labels": ["kotlin", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 11: RProductBanner estructura
    "690df993c8c05c26d9757cd6": {
        "labels": ["kotlin", "prioridad", "reachu", "new_functionality"],
        "member": MIGUEL_ID
    },
    # Tarea 12: RProductBanner caching
    "690df996bac4defd7561e1c3": {
        "labels": ["kotlin", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 13: RProductBanner UI
    "690df996aacaa51018c032b9": {
        "labels": ["kotlin", "prioridad", "reachu", "ux_ui"],
        "member": MIGUEL_ID
    },
    # Tarea 14: RProductCarousel estructura
    "690df9970ada3fc754d483c9": {
        "labels": ["kotlin", "prioridad", "reachu", "new_functionality"],
        "member": MIGUEL_ID
    },
    # Tarea 15: RProductCarousel layouts
    "690df998ee6d9fbe60763e9d": {
        "labels": ["kotlin", "prioridad", "reachu", "ux_ui"],
        "member": MIGUEL_ID
    },
    # Tarea 16: RProductStore estructura
    "690df9999f31537df86af6fc": {
        "labels": ["kotlin", "prioridad", "reachu", "new_functionality"],
        "member": MIGUEL_ID
    },
    # Tarea 17: RProductStore grid/list
    "690df99ac182d7c1eecef2de": {
        "labels": ["kotlin", "prioridad", "reachu", "ux_ui"],
        "member": MIGUEL_ID
    },
    # Tarea 18: RProductSpotlight estructura
    "690df99a368ac558dd33e20a": {
        "labels": ["kotlin", "prioridad", "reachu", "new_functionality"],
        "member": MIGUEL_ID
    },
    # Tarea 19: RProductSpotlight UI
    "690df99be2ae446d6ed3d520": {
        "labels": ["kotlin", "prioridad", "reachu", "ux_ui"],
        "member": MIGUEL_ID
    },
    # Tarea 20: Localización RCheckoutOverlay
    "690df99caad17cd24095a337": {
        "labels": ["kotlin", "prioridad", "reachu", "refactoring"],
        "member": MIGUEL_ID
    },
    # Tarea 21: Localización RProductDetailOverlay
    "690df99de24358e9c3974d7e": {
        "labels": ["kotlin", "reachu", "refactoring"],
        "member": MIGUEL_ID
    },
    # Tarea 22: Localización otros componentes
    "690df9a04323d1f4a8cecffc": {
        "labels": ["kotlin", "reachu", "refactoring"],
        "member": MIGUEL_ID
    },
    # Tarea 23: ProductBannerConfig
    "690df9a131eba60b2907ede3": {
        "labels": ["kotlin", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 24: Otros configs
    "690df9a1adbb5c2aed5cfd76": {
        "labels": ["kotlin", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 25: Component sealed class
    "690df9a2e6e6076b8b5bd259": {
        "labels": ["kotlin", "prioridad", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 26: Skeleton loaders
    "690df9a3cee74ec9b268a1f1": {
        "labels": ["kotlin", "reachu", "ux_ui"],
        "member": MIGUEL_ID
    },
    # Tarea 27: Auto-hide
    "690df9a40315d439df7120a4": {
        "labels": ["kotlin", "prioridad", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 28: componentId support
    "690df9a5fdc97003412dcc4d": {
        "labels": ["kotlin", "reachu"],
        "member": MIGUEL_ID
    },
    # Tarea 29: Tests
    "690df9a536ba6108de3cb492": {
        "labels": ["kotlin", "reachu", "testing"],
        "member": MIGUEL_ID
    },
    # Tarea 30: Documentación
    "690df9a665fdbbbd29b9bbd6": {
        "labels": ["kotlin", "reachu", "documentation"],
        "member": MIGUEL_ID
    },
}


async def add_label_to_card(client: httpx.AsyncClient, card_id: str, label_id: str):
    """Agrega una etiqueta a una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}/idLabels"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "value": label_id
    }
    try:
        response = await client.post(url, params=params)
        response.raise_for_status()
        print(f"✅ Label {label_id} agregada a tarjeta {card_id}")
        return True
    except Exception as e:
        print(f"❌ Error agregando label {label_id} a tarjeta {card_id}: {e}")
        return False


async def add_member_to_card(client: httpx.AsyncClient, card_id: str, member_id: str):
    """Agrega un miembro a una tarjeta."""
    url = f"{TRELLO_API_BASE}/cards/{card_id}/idMembers"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "value": member_id
    }
    try:
        response = await client.put(url, params=params)
        response.raise_for_status()
        print(f"✅ Member {member_id} agregado a tarjeta {card_id}")
        return True
    except Exception as e:
        print(f"❌ Error agregando member {member_id} a tarjeta {card_id}: {e}")
        return False


async def process_cards():
    """Procesa todas las tarjetas agregando etiquetas y miembros."""
    async with httpx.AsyncClient() as client:
        total = len(CARDS_CONFIG)
        success_labels = 0
        success_members = 0
        
        for card_id, config in CARDS_CONFIG.items():
            print(f"\n📋 Procesando tarjeta {card_id}...")
            
            # Agregar etiquetas
            for label_key in config["labels"]:
                label_id = LABELS[label_key]
                if await add_label_to_card(client, card_id, label_id):
                    success_labels += 1
                await asyncio.sleep(0.2)  # Rate limiting
            
            # Agregar miembro
            if config.get("member"):
                if await add_member_to_card(client, card_id, config["member"]):
                    success_members += 1
                await asyncio.sleep(0.2)  # Rate limiting
        
        print(f"\n✅ Completado!")
        print(f"   Etiquetas agregadas: {success_labels}/{total * 3} (aprox)")
        print(f"   Miembros agregados: {success_members}/{total}")


if __name__ == "__main__":
    if not TRELLO_API_KEY or not TRELLO_TOKEN:
        print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados en .env")
        sys.exit(1)
    
    asyncio.run(process_cards())

