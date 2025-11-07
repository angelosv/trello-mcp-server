# Guía de Revisión y Asignación de Tarjetas

## Nuevas Funcionalidades

### 1. Sugerencia Automática de Miembros

El sistema ahora sugiere automáticamente miembros para asignar a las tarjetas basándose en:

- **Autor del commit**: Si el autor del commit coincide con un miembro del board, se sugiere automáticamente
- **Miembros comunes**: Si no hay coincidencia, se sugieren miembros comunes (Miguel, Angelo, etc.)

**Ejemplo de uso:**
```
Crear tarjeta para commit 8658a4a con sugerencia automática de miembros
```

El sistema mostrará:
```
💡 Miembros sugeridos automáticamente: Miguel Angel López Monzón, angelo.sv
```

### 2. Revisión de Tarjetas Existentes

Nueva herramienta para revisar qué tarjetas necesitan actualizarse y cuáles commits nuevos no tienen tarjeta.

**Herramienta:** `review_cards_for_updates`

**Parámetros:**
- `list_id`: ID de la lista donde buscar tarjetas
- `since`: Fecha desde la cual analizar commits (default: "today")

**Retorna:**
- `cards_to_update`: Tarjetas que pueden necesitar actualización
- `cards_up_to_date`: Tarjetas que están actualizadas
- `new_commits_without_cards`: Commits nuevos sin tarjeta asociada
- `summary`: Resumen estadístico

**Ejemplo de uso:**
```
Revisar tarjetas en la lista para ver cuáles necesitan actualización
```

### 3. Obtener Miembros Disponibles

**Herramienta:** `get_available_members_for_assignment`

Obtiene la lista completa de miembros disponibles en un board para asignación.

**Parámetros:**
- `board_id`: ID del board

**Retorna:**
- Lista de miembros con: id, username, fullName, initials

### 4. Sugerir Miembros para Commit

**Herramienta:** `suggest_members_for_commit`

Sugiere miembros para asignar basándose en el autor del commit.

**Parámetros:**
- `commit_hash`: Hash del commit
- `board_id`: ID del board

**Retorna:**
- Lista de IDs de miembros sugeridos

## Flujo de Trabajo Mejorado

### Crear Tarjetas con Sugerencia Automática

1. **Análisis automático del commit**
2. **Sugerencia de miembros** basada en autor del commit
3. **Información al usuario** sobre miembros sugeridos
4. **Creación de tarjeta** con miembros asignados automáticamente

### Revisar Estado de Tarjetas

1. **Ejecutar revisión**: `review_cards_for_updates`
2. **Ver resumen**: Cuántas tarjetas necesitan actualización
3. **Ver commits nuevos**: Commits sin tarjeta asociada
4. **Tomar acción**: Crear tarjetas para commits nuevos o actualizar existentes

## Ejemplos de Uso

### Ejemplo 1: Crear tarjeta con sugerencia automática

```python
# El sistema automáticamente:
# 1. Analiza el commit
# 2. Sugiere miembros basándose en el autor
# 3. Muestra sugerencias al usuario
# 4. Crea la tarjeta con miembros asignados

create_smart_card_from_commit(
    commit_hash="8658a4a",
    idList="645e0787a4ef6845516d172b",
    idBoard="5dea6d99c0ea505b4c3a435e",
    auto_suggest_members=True  # Por defecto True
)
```

### Ejemplo 2: Revisar tarjetas existentes

```python
# Revisa todas las tarjetas y compara con commits recientes
result = review_cards_for_updates(
    list_id="645e0787a4ef6845516d172b",
    since="today"
)

# Resultado incluye:
# - cards_to_update: Tarjetas que pueden necesitar actualización
# - new_commits_without_cards: Commits nuevos sin tarjeta
# - summary: Estadísticas
```

### Ejemplo 3: Obtener miembros disponibles

```python
# Obtiene lista completa de miembros
members = get_available_members_for_assignment(
    board_id="5dea6d99c0ea505b4c3a435e"
)

# Cada miembro tiene:
# - id: ID del miembro
# - username: Nombre de usuario
# - fullName: Nombre completo
# - initials: Iniciales
```

## Configuración

### Desactivar Sugerencia Automática

Si prefieres asignar miembros manualmente:

```python
create_smart_card_from_commit(
    commit_hash="...",
    idList="...",
    idBoard="...",
    auto_suggest_members=False  # Desactivar sugerencia automática
)
```

### Personalizar Asignación

Puedes proporcionar miembros específicos:

```python
create_smart_card_from_commit(
    commit_hash="...",
    idList="...",
    idBoard="...",
    idMembers="619f90698c4fc547cc133149,680a7cb22a55497d4f4223d4"  # IDs separados por coma
)
```

## Ventajas

✅ **Asignación inteligente**: Sugiere miembros basándose en el autor del commit  
✅ **Revisión automática**: Identifica tarjetas que necesitan actualización  
✅ **Detección de gaps**: Encuentra commits nuevos sin tarjeta  
✅ **Información clara**: Muestra sugerencias antes de crear tarjetas  
✅ **Flexibilidad**: Permite desactivar sugerencias o asignar manualmente

