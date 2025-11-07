#!/usr/bin/env python3
"""
Script para agregar nuevas funcionalidades a los tableros Reachu Dev y Tipio Dev.

Uso:
    python3 add_feature.py --board "Reachu Dev" --name "Nueva funcionalidad" --description "Descripción"
    python3 add_feature.py --board "Tipio Dev" --name "Nueva funcionalidad" --swift-file "Sources/Path/File.swift"
    python3 add_feature.py --interactive  # Modo interactivo
"""

import os
import sys
import argparse
import httpx
from typing import Optional, Dict, List

# IDs de los tableros
BOARDS = {
    "Reachu Dev": "5dea6d99c0ea505b4c3a435e",
    "Tipio Dev": "662a4b0e2b9175b39e04f54b"
}

# Configuración de Trello API
TRELLO_API_KEY = os.getenv("TRELLO_API_KEY")
TRELLO_TOKEN = os.getenv("TRELLO_TOKEN")
TRELLO_API_BASE = "https://api.trello.com/1"

if not TRELLO_API_KEY or not TRELLO_TOKEN:
    print("❌ Error: TRELLO_API_KEY y TRELLO_TOKEN deben estar configurados")
    sys.exit(1)


def get_board_id(board_name: str) -> Optional[str]:
    """Obtiene el ID del tablero por nombre."""
    return BOARDS.get(board_name)


def get_lists(board_id: str) -> List[Dict]:
    """Obtiene las listas de un tablero."""
    url = f"{TRELLO_API_BASE}/boards/{board_id}/lists"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def get_or_create_label(board_id: str, label_name: str, color: str = "blue") -> str:
    """Obtiene o crea una etiqueta en el tablero."""
    # Primero buscar etiquetas existentes
    url = f"{TRELLO_API_BASE}/boards/{board_id}/labels"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        labels = response.json()
        
        # Buscar etiqueta existente
        for label in labels:
            if label.get("name", "").lower() == label_name.lower():
                return label["id"]
        
        # Crear nueva etiqueta
        create_url = f"{TRELLO_API_BASE}/boards/{board_id}/labels"
        create_params = {
            "key": TRELLO_API_KEY,
            "token": TRELLO_TOKEN,
            "name": label_name,
            "color": color
        }
        
        response = client.post(create_url, params=create_params)
        response.raise_for_status()
        return response.json()["id"]


def get_members(board_id: str) -> List[Dict]:
    """Obtiene los miembros del tablero."""
    url = f"{TRELLO_API_BASE}/boards/{board_id}/members"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN
    }
    
    with httpx.Client() as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def create_card(
    list_id: str,
    name: str,
    description: str = "",
    label_ids: List[str] = None,
    member_ids: List[str] = None
) -> Dict:
    """Crea una tarjeta en Trello."""
    url = f"{TRELLO_API_BASE}/cards"
    params = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_TOKEN,
        "idList": list_id,
        "name": name,
        "desc": description
    }
    
    if label_ids:
        params["idLabels"] = ",".join(label_ids)
    
    if member_ids:
        params["idMembers"] = ",".join(member_ids)
    
    with httpx.Client() as client:
        response = client.post(url, params=params)
        response.raise_for_status()
        card = response.json()
        
        # Agregar labels y miembros después si no se pudieron agregar en la creación
        if label_ids:
            for label_id in label_ids:
                try:
                    add_url = f"{TRELLO_API_BASE}/cards/{card['id']}/idLabels"
                    add_params = {
                        "key": TRELLO_API_KEY,
                        "token": TRELLO_TOKEN,
                        "value": label_id
                    }
                    client.post(add_url, params=add_params)
                except:
                    pass
        
        if member_ids:
            for member_id in member_ids:
                try:
                    add_url = f"{TRELLO_API_BASE}/cards/{card['id']}/idMembers"
                    add_params = {
                        "key": TRELLO_API_KEY,
                        "token": TRELLO_TOKEN,
                        "value": member_id
                    }
                    client.put(add_url, params=add_params)
                except:
                    pass
        
        return card


def generate_description_from_swift(swift_file: str) -> str:
    """Genera una descripción básica basada en un archivo Swift."""
    swift_path = f"/Users/angelo/ReachuSwiftSDK/{swift_file}"
    
    if not os.path.exists(swift_path):
        return f"**Archivo Swift:** `{swift_file}`\n\nRevisar implementación en Swift y portar a Kotlin."
    
    try:
        with open(swift_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Detectar clases públicas
        import re
        classes = re.findall(r'public\s+(?:class|struct|enum)\s+(\w+)', content)
        functions = re.findall(r'public\s+func\s+(\w+)', content)
        
        description = f"""**Archivo Swift:** `{swift_file}`

### Cómo funciona en Swift

"""
        
        if classes:
            description += f"- Clases/Structs/Enums: {', '.join(classes[:5])}\n"
        if functions:
            description += f"- Funciones públicas: {len(functions)} funciones\n"
        
        description += f"""
### Qué hacer en Kotlin

1. Revisar el código Swift en `{swift_file}`
2. Portar la funcionalidad equivalente a Kotlin
3. Adaptar a las mejores prácticas de Kotlin/Android
4. Mantener la misma API pública si es posible

### Archivos a revisar
- `{swift_file}`
"""
        
        return description
    except Exception as e:
        return f"**Archivo Swift:** `{swift_file}`\n\nError leyendo archivo: {e}"


def interactive_mode():
    """Modo interactivo para agregar funcionalidades."""
    print("🎯 Agregar Nueva Funcionalidad\n")
    
    # Seleccionar tablero
    print("Selecciona el tablero:")
    boards_list = list(BOARDS.keys())
    for i, board in enumerate(boards_list, 1):
        print(f"  {i}. {board}")
    
    board_choice = input("\nTablero (1-2): ").strip()
    try:
        board_name = boards_list[int(board_choice) - 1]
        board_id = BOARDS[board_name]
    except (ValueError, IndexError):
        print("❌ Selección inválida")
        return
    
    # Obtener listas
    print(f"\n📋 Obteniendo listas de '{board_name}'...")
    lists = get_lists(board_id)
    
    print("\nSelecciona la lista:")
    for i, list_item in enumerate(lists, 1):
        print(f"  {i}. {list_item['name']}")
    
    list_choice = input("\nLista: ").strip()
    try:
        selected_list = lists[int(list_choice) - 1]
        list_id = selected_list["id"]
    except (ValueError, IndexError):
        print("❌ Selección inválida")
        return
    
    # Nombre de la funcionalidad
    name = input("\n📝 Nombre de la funcionalidad: ").strip()
    if not name:
        print("❌ El nombre es requerido")
        return
    
    # Descripción o archivo Swift
    print("\nOpciones:")
    print("  1. Escribir descripción manualmente")
    print("  2. Usar archivo Swift (genera descripción automáticamente)")
    
    desc_choice = input("\nOpción (1-2): ").strip()
    
    if desc_choice == "2":
        swift_file = input("Ruta del archivo Swift (ej: Sources/Path/File.swift): ").strip()
        description = generate_description_from_swift(swift_file)
    else:
        print("\nEscribe la descripción (Ctrl+D para terminar):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        description = "\n".join(lines)
    
    # Etiquetas
    print("\n🏷️  Etiquetas (separadas por comas, Enter para omitir):")
    tags_input = input().strip()
    label_ids = []
    if tags_input:
        tags = [t.strip() for t in tags_input.split(",")]
        print(f"\nCreando/obteniendo etiquetas...")
        for tag in tags:
            label_id = get_or_create_label(board_id, tag)
            label_ids.append(label_id)
    
    # Miembros
    print("\n👥 Miembros del tablero:")
    members = get_members(board_id)
    for i, member in enumerate(members, 1):
        print(f"  {i}. {member.get('fullName', member.get('username', 'Unknown'))}")
    
    members_input = input("\nIDs de miembros (separados por comas, Enter para omitir): ").strip()
    member_ids = []
    if members_input:
        member_ids = [m.strip() for m in members_input.split(",")]
    
    # Crear tarjeta
    print(f"\n🎫 Creando tarjeta en '{board_name}' > '{selected_list['name']}'...")
    
    try:
        card = create_card(
            list_id=list_id,
            name=name,
            description=description,
            label_ids=label_ids,
            member_ids=member_ids
        )
        
        print(f"\n✅ Tarjeta creada exitosamente!")
        print(f"   📎 URL: {card.get('shortUrl', card.get('url', 'N/A'))}")
        print(f"   🆔 ID: {card['id']}")
    except Exception as e:
        print(f"\n❌ Error creando tarjeta: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        description="Agrega nuevas funcionalidades a Reachu Dev o Tipio Dev"
    )
    parser.add_argument(
        "--board",
        choices=list(BOARDS.keys()),
        help="Tablero donde crear la tarjeta"
    )
    parser.add_argument(
        "--name",
        help="Nombre de la funcionalidad"
    )
    parser.add_argument(
        "--description",
        help="Descripción de la funcionalidad"
    )
    parser.add_argument(
        "--swift-file",
        help="Archivo Swift (genera descripción automáticamente)"
    )
    parser.add_argument(
        "--list",
        default="To Do",
        help="Nombre de la lista (default: 'To Do')"
    )
    parser.add_argument(
        "--tags",
        help="Etiquetas separadas por comas"
    )
    parser.add_argument(
        "--members",
        help="IDs de miembros separados por comas"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Modo interactivo"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return
    
    if not args.board or not args.name:
        print("❌ --board y --name son requeridos (o usa --interactive)")
        parser.print_help()
        return
    
    board_id = get_board_id(args.board)
    if not board_id:
        print(f"❌ Tablero '{args.board}' no encontrado")
        return
    
    # Obtener lista
    lists = get_lists(board_id)
    selected_list = next((l for l in lists if l["name"] == args.list), None)
    
    if not selected_list:
        print(f"❌ Lista '{args.list}' no encontrada")
        print(f"   Listas disponibles: {', '.join([l['name'] for l in lists])}")
        return
    
    # Generar descripción
    if args.swift_file:
        description = generate_description_from_swift(args.swift_file)
    elif args.description:
        description = args.description
    else:
        description = ""
    
    # Procesar etiquetas
    label_ids = []
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",")]
        for tag in tags:
            label_id = get_or_create_label(board_id, tag)
            label_ids.append(label_id)
    
    # Procesar miembros
    member_ids = []
    if args.members:
        member_ids = [m.strip() for m in args.members.split(",")]
    
    # Crear tarjeta
    print(f"🎫 Creando tarjeta en '{args.board}' > '{args.list}'...")
    
    try:
        card = create_card(
            list_id=selected_list["id"],
            name=args.name,
            description=description,
            label_ids=label_ids,
            member_ids=member_ids
        )
        
        print(f"\n✅ Tarjeta creada exitosamente!")
        print(f"   📎 URL: {card.get('shortUrl', card.get('url', 'N/A'))}")
        print(f"   🆔 ID: {card['id']}")
    except Exception as e:
        print(f"\n❌ Error creando tarjeta: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

