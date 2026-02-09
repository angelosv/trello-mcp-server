# Workflow Tools - Guía de Uso

Este documento describe las nuevas herramientas de workflow agregadas al MCP de Trello para gestionar tarjetas de manera más fluida.

## 🎯 Herramientas Disponibles

### 1. `analyze_developer_work`
Analiza las tarjetas en las listas "Doing" y "Done" para ver qué ha trabajado el desarrollador.

**Parámetros:**
- `board_id` (requerido): ID del board de Trello
- `doing_list_name` (opcional, default: "Doing"): Nombre de la lista "Doing"
- `done_list_name` (opcional, default: "Done"): Nombre de la lista "Done"

**Retorna:**
- Dict con tarjetas en Doing y Done, y un resumen

**Ejemplo de uso:**
```
analyze_developer_work(board_id="6964ea21570279f07def7786")
```

---

### 2. `analyze_and_recommend_cards`
Analiza tarjetas en "To do" y "Backlog" y recomienda cuáles trabajar esta semana basándose en prioridad.

**Parámetros:**
- `board_id` (requerido): ID del board de Trello
- `todo_list_name` (opcional, default: "To do"): Nombre de la lista "To do"
- `backlog_list_name` (opcional, default: "Backlog"): Nombre de la lista "Backlog"

**Retorna:**
- Dict con recomendaciones organizadas por prioridad:
  - `priority_1_critical_engagement`: Tarjetas críticas de Engagement (máx 5)
  - `priority_2_other_critical`: Otras tarjetas críticas (máx 3)
  - `priority_3_high_engagement`: Tarjetas de alta prioridad de Engagement (máx 3)
  - `summary`: Resumen estadístico

**Ejemplo de uso:**
```
analyze_and_recommend_cards(board_id="6964ea21570279f07def7786")
```

---

### 3. `move_cards_by_priority`
Mueve tarjetas de una lista a otra basándose en filtros de prioridad y tipo.

**Parámetros:**
- `board_id` (requerido): ID del board de Trello
- `from_list_name` (requerido): Nombre de la lista origen
- `to_list_name` (requerido): Nombre de la lista destino
- `priority_filter` (opcional): Filtrar por prioridad ("CRÍTICA", "ALTA", "MEDIA", "BAJA"). Si es None, mueve todas.
- `engagement_only` (opcional, default: False): Si es True, solo mueve tarjetas relacionadas con Engagement
- `limit` (opcional): Número máximo de tarjetas a mover

**Retorna:**
- Dict con resultados:
  - `moved`: Lista de tarjetas movidas exitosamente
  - `failed`: Lista de tarjetas que fallaron al mover
  - `summary`: Resumen de la operación

**Ejemplos de uso:**
```
# Mover todas las tarjetas críticas de Engagement de Backlog a To do
move_cards_by_priority(
    board_id="6964ea21570279f07def7786",
    from_list_name="Backlog",
    to_list_name="To do",
    priority_filter="CRÍTICA",
    engagement_only=True
)

# Mover las primeras 5 tarjetas de alta prioridad
move_cards_by_priority(
    board_id="6964ea21570279f07def7786",
    from_list_name="Backlog",
    to_list_name="To do",
    priority_filter="ALTA",
    limit=5
)
```

---

### 4. `update_card_description`
Actualiza la descripción de una tarjeta.

**Parámetros:**
- `card_id` (requerido): ID de la tarjeta a actualizar
- `new_description` (requerido): Nueva descripción

**Retorna:**
- TrelloCard actualizado

**Ejemplo de uso:**
```
update_card_description(
    card_id="6985d72109107f0667740b4f",
    new_description="Nueva descripción actualizada..."
)
```

---

### 5. `move_critical_cards_to_todo`
Mueve automáticamente tarjetas críticas y de alta prioridad de Engagement de Backlog a To do.

**Parámetros:**
- `board_id` (requerido): ID del board de Trello
- `backlog_list_name` (opcional, default: "Backlog"): Nombre de la lista Backlog
- `todo_list_name` (opcional, default: "To do"): Nombre de la lista To do

**Retorna:**
- Dict con resultados:
  - `critical_moved`: Tarjetas críticas movidas
  - `high_engagement_moved`: Tarjetas de alta prioridad de Engagement movidas
  - `summary`: Resumen de la operación

**Ejemplo de uso:**
```
move_critical_cards_to_todo(board_id="6964ea21570279f07def7786")
```

---

## 📋 Casos de Uso Comunes

### Analizar trabajo del desarrollador
```
analyze_developer_work(board_id="6964ea21570279f07def7786")
```

### Obtener recomendaciones para esta semana
```
analyze_and_recommend_cards(board_id="6964ea21570279f07def7786")
```

### Mover tarjetas completadas a Done
```
move_cards_by_priority(
    board_id="6964ea21570279f07def7786",
    from_list_name="Doing",
    to_list_name="Done",
    limit=10
)
```

### Mover tarjetas críticas a To do
```
move_critical_cards_to_todo(board_id="6964ea21570279f07def7786")
```

---

## 🔧 Detalles Técnicos

### Detección de Prioridad
Las herramientas detectan prioridad buscando en la descripción de la tarjeta:
- **CRÍTICA**: "Prioridad: CRÍTICA", "crítica", "critical"
- **ALTA**: "Prioridad: ALTA", "alta", "high"
- **MEDIA**: "Prioridad: MEDIA", "media", "medium" (default)
- **BAJA**: "Prioridad: BAJA", "baja", "low"

### Detección de Engagement
Una tarjeta se considera relacionada con Engagement si contiene en nombre o descripción:
- "engagement"
- "poll"
- "contest"
- "vote"
- "participat"

---

## 🚀 Próximos Pasos

Estas herramientas están disponibles directamente en Cursor a través del MCP de Trello. Puedes usarlas sin necesidad de crear scripts adicionales.

Para usar las herramientas, simplemente menciona qué quieres hacer y el sistema las invocará automáticamente.
