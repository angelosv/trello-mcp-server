# Scripts de Utilidad para Trello

Scripts reutilizables para gestionar tarjetas de Trello desde la línea de comandos.

## Configuración

Los scripts requieren variables de entorno:

```bash
export TRELLO_API_KEY="tu_api_key"
export TRELLO_TOKEN="tu_api_token"
```

O puedes crear un archivo `.env` en la raíz del proyecto (ver `.env.example`):

```bash
TRELLO_API_KEY=tu_api_key
TRELLO_TOKEN=tu_api_token
```

## Scripts Disponibles

### `complete_engagement_cards.py`

Completa tarjetas de Trello con descripciones, etiquetas, miembros y checklists.

**Uso:**
```bash
python scripts/complete_engagement_cards.py \
    --board-id <BOARD_ID> \
    --list-id <LIST_ID> \
    [--cards-file <CARDS_JSON_FILE>]
```

**Ejemplo:**
```bash
python scripts/complete_engagement_cards.py \
    --board-id 6964ea21570279f07def7786 \
    --list-id 6985d6babb14a3a08db187a8 \
    --cards-file cards_data.json
```

**Archivo JSON de ejemplo (`cards_data.json`):**
```json
{
    "card_id_1": {
        "desc": "Descripción completa de la tarjeta...",
        "labels": ["kotlin", "sdk", "compose"],
        "checklist": [
            "Tarea 1",
            "Tarea 2",
            "Tarea 3"
        ]
    },
    "card_id_2": {
        "desc": "Otra descripción...",
        "labels": ["kotlin", "sdk"],
        "checklist": ["Tarea única"]
    }
}
```

### `verify_cards.py`

Verifica el estado completo de tarjetas en una lista.

**Uso:**
```bash
python scripts/verify_cards.py \
    --board-id <BOARD_ID> \
    --list-id <LIST_ID>
```

**Ejemplo:**
```bash
python scripts/verify_cards.py \
    --board-id 6964ea21570279f07def7786 \
    --list-id 6985d6babb14a3a08db187a8
```

**Verifica:**
- ✅ Descripciones completas (>200 caracteres)
- ✅ Etiquetas asignadas (kotlin, sdk, etc.)
- ✅ Miembros asignados (mínimo 2)
- ✅ Checklists creados con items

### `move_cards.py`

Mueve tarjetas entre listas.

**Uso:**
```bash
python scripts/move_cards.py \
    --board-id <BOARD_ID> \
    --from-list-name <FROM_LIST_NAME> \
    --to-list-name <TO_LIST_NAME> \
    [--card-names <CARD_NAMES_FILE>] \
    [--first-n <NUMBER>]
```

**Ejemplos:**

Mover todas las tarjetas de una lista a otra:
```bash
python scripts/move_cards.py \
    --board-id 6964ea21570279f07def7786 \
    --from-list-name "backlog" \
    --to-list-name "Backlog"
```

Mover solo las primeras 6 tarjetas:
```bash
python scripts/move_cards.py \
    --board-id 6964ea21570279f07def7786 \
    --from-list-name "backlog" \
    --to-list-name "To do" \
    --first-n 6
```

Mover tarjetas específicas desde archivo JSON:
```bash
python scripts/move_cards.py \
    --board-id 6964ea21570279f07def7786 \
    --from-list-name "backlog" \
    --to-list-name "To do" \
    --card-names critical_cards.json
```

**Archivo JSON de ejemplo (`critical_cards.json`):**
```json
[
    "Crear módulo ReachuEngagementSystem - Estructura base",
    "Implementar EngagementManager - Gestor principal de engagement",
    "Implementar VideoSyncManager - Sincronización con video"
]
```

## Casos de Uso Comunes

### 1. Completar tarjetas nuevas con información detallada

```bash
# Crear archivo con datos de tarjetas
cat > cards_data.json << EOF
{
    "card_id_1": {
        "desc": "Descripción completa...",
        "labels": ["kotlin", "sdk"],
        "checklist": ["Tarea 1", "Tarea 2"]
    }
}
EOF

# Completar tarjetas
python scripts/complete_engagement_cards.py \
    --board-id <BOARD_ID> \
    --list-id <LIST_ID> \
    --cards-file cards_data.json
```

### 2. Verificar que todas las tarjetas estén completas

```bash
python scripts/verify_cards.py \
    --board-id <BOARD_ID> \
    --list-id <LIST_ID>
```

### 3. Organizar tarjetas: mover primeras críticas a "To do"

```bash
python scripts/move_cards.py \
    --board-id <BOARD_ID> \
    --from-list-name "Backlog" \
    --to-list-name "To do" \
    --first-n 6
```

## Notas

- Los scripts incluyen pausas entre llamadas API para evitar rate limiting
- Los scripts son idempotentes: puedes ejecutarlos múltiples veces sin problemas
- Los scripts verifican que las credenciales estén configuradas antes de ejecutar
