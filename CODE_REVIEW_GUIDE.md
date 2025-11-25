# Guía de Revisión de Código Kotlin

Este documento explica cómo usar las herramientas de revisión de código para analizar implementaciones Kotlin y proporcionar feedback automático en las tarjetas de Trello.

## 📋 Descripción General

Cuando un desarrollador de Kotlin completa una tarea, el sistema puede:
1. **Analizar el código implementado** - Busca archivos Kotlin relacionados con la tarjeta
2. **Comparar con requisitos** - Verifica que la implementación cumpla con los requisitos de la tarjeta
3. **Generar feedback** - Crea comentarios detallados con sugerencias y problemas encontrados
4. **Mover tarjeta a Doing** - Si hay problemas, devuelve la tarjeta a "Doing" para corrección

## 🛠️ Herramientas Disponibles

### `review_kotlin_implementation`

Revisa la implementación Kotlin de una tarjeta y agrega feedback como comentario.

**Parámetros:**
- `card_id` (requerido): ID de la tarjeta de Trello a revisar
- `kotlin_project_path` (opcional): Ruta al proyecto Kotlin (default: `/Users/angelo`)
- `board_id` (opcional): ID del board (necesario para mover la tarjeta)
- `move_to_doing_if_issues` (opcional): Si mover la tarjeta a "Doing" si hay problemas (default: `true`)

**Ejemplo de uso:**

```python
# Revisar una tarjeta específica
result = await review_kotlin_implementation(
    ctx=context,
    card_id="abc123def456",
    kotlin_project_path="/ruta/al/proyecto/kotlin",
    board_id="board123",
    move_to_doing_if_issues=True
)
```

## 🔍 Cómo Funciona

### 1. Extracción de Requisitos

El sistema analiza la descripción de la tarjeta para extraer:
- **Commit hash** relacionado (si existe)
- **Archivos mencionados** (archivos Swift que deben portarse a Kotlin)
- **Keywords relevantes** (palabras clave de la implementación)
- **Requisitos específicos** (checkboxes y subtítulos)

### 2. Búsqueda de Archivos Kotlin

El sistema busca archivos Kotlin relacionados:
- Convierte nombres de archivos Swift a Kotlin (`.swift` → `.kt`)
- Busca archivos que contengan keywords relevantes
- Busca en el proyecto Kotlin especificado

### 3. Análisis de Código

Para cada archivo Kotlin encontrado, el sistema verifica:
- ✅ **Existencia del archivo** - Si el archivo existe
- ✅ **Implementación básica** - Si el archivo tiene contenido significativo
- ✅ **Estructura de código** - Clases, objetos, interfaces definidos
- ✅ **Documentación** - Comentarios y documentación presente
- ✅ **Manejo de errores** - Try-catch para funciones asíncronas
- ✅ **Comparación con Swift** - Si hay archivo Swift de referencia, compara funcionalidades

### 4. Generación de Feedback

El sistema genera un comentario estructurado con:
- 📄 **Archivos encontrados** - Lista de archivos Kotlin relacionados
- ✅ **Implementación correcta** - Si el código cumple con los requisitos
- ❌ **Problemas encontrados** - Características faltantes o problemas de calidad
- 💡 **Sugerencias** - Mejoras recomendadas

### 5. Acciones Automáticas

Si se encuentran problemas:
- Se agrega un comentario detallado a la tarjeta
- La tarjeta se mueve automáticamente a la lista "Doing" (si está configurado)
- Se proporciona un resumen de los problemas encontrados

## 📝 Formato del Feedback

El comentario generado sigue este formato:

```markdown
## 📝 Revisión de Código Kotlin

**Tarjeta:** [Nombre de la tarjeta]

### ✅ Archivos encontrados: X
- `ruta/al/archivo1.kt`
- `ruta/al/archivo2.kt`

### 📄 Análisis: `archivo1.kt`
✅ **Implementación encontrada**

**Características faltantes:**
- ❌ Funciones faltantes comparadas con Swift: func1, func2

**Problemas de calidad:**
- ⚠️ Falta documentación en el código

**Sugerencias:**
- 💡 Considerar agregar manejo de errores para funciones asíncronas

### 📊 Resumen
❌ **Se encontraron problemas que requieren atención.**
Por favor, revisa los puntos mencionados arriba y corrige los problemas antes de marcar como completado.
```

## 🎯 Casos de Uso

### Caso 1: Revisión Automática al Completar Tarea

Cuando un desarrollador marca una tarjeta como "Done", puedes ejecutar:

```python
# Revisar todas las tarjetas en "Done"
cards = await get_cards(list_id="done_list_id")
for card in cards:
    await review_kotlin_implementation(
        ctx=context,
        card_id=card.id,
        board_id="board123",
        move_to_doing_if_issues=True
    )
```

### Caso 2: Revisión Manual de una Tarjeta Específica

```python
# Revisar una tarjeta específica sin moverla
result = await review_kotlin_implementation(
    ctx=context,
    card_id="card_id_here",
    kotlin_project_path="/custom/path/to/kotlin",
    move_to_doing_if_issues=False
)
```

### Caso 3: Revisión Batch de Múltiples Tarjetas

```python
# Revisar múltiples tarjetas
card_ids = ["card1", "card2", "card3"]
for card_id in card_ids:
    try:
        result = await review_kotlin_implementation(
            ctx=context,
            card_id=card_id,
            board_id="board123"
        )
        print(f"✅ {result['card_name']}: {result['files_found']} archivos")
    except Exception as e:
        print(f"❌ Error revisando {card_id}: {e}")
```

## ⚙️ Configuración

### Rutas del Proyecto

Por defecto, el sistema busca en:
- **Swift SDK:** `/Users/angelo/ReachuSwiftSDK`
- **Kotlin SDK:** `/Users/angelo/Documents/GitHub/ReachuKotlinSDK`

El sistema busca en **todo el proyecto Kotlin** de forma general (no solo en `src/main/kotlin/`), incluyendo todos los subdirectorios y archivos `.kt` en cualquier ubicación del proyecto.

Puedes especificar rutas personalizadas usando el parámetro `kotlin_project_path`.

### Lista "Doing"

El sistema busca automáticamente una lista llamada:
- "Doing"
- "En progreso"
- "In progress"

Si tu board usa un nombre diferente, puedes modificar la función `find_doing_list()` en `code_review.py`.

## 🔧 Personalización

### Agregar Nuevos Checks

Puedes extender el análisis agregando nuevos checks en `analyze_kotlin_code()`:

```python
def analyze_kotlin_code(file_path: str, swift_reference_path: Optional[str] = None):
    # ... código existente ...
    
    # Nuevo check personalizado
    if 'suspend' in kotlin_code and 'CoroutineScope' not in kotlin_code:
        analysis['suggestions'].append("Considerar usar CoroutineScope para manejo de coroutines")
    
    return analysis
```

### Mejorar Comparación con Swift

Puedes mejorar la comparación agregando más análisis en `analyze_kotlin_code()`:

```python
# Comparar propiedades
swift_properties = re.findall(r'var\s+(\w+)', swift_code)
kotlin_properties = re.findall(r'var\s+(\w+)', kotlin_code)

missing_properties = set(swift_properties) - set(kotlin_properties)
if missing_properties:
    analysis['missing_features'].append(
        f"Propiedades faltantes: {', '.join(list(missing_properties)[:5])}"
    )
```

## 📊 Resultado de la Revisión

La función retorna un diccionario con:

```python
{
    'card_id': 'abc123',
    'card_name': 'Nombre de la tarjeta',
    'files_found': 2,
    'has_issues': True,
    'feedback_added': True,
    'moved_to_doing': True,
    'files_analyzed': ['/ruta/archivo1.kt', '/ruta/archivo2.kt']
}
```

## 🚨 Manejo de Errores

El sistema maneja errores comunes:
- **Archivo no encontrado** - Se reporta como problema
- **Error de lectura** - Se agrega a problemas de calidad
- **Lista "Doing" no encontrada** - Se registra un warning pero no falla
- **Error al agregar comentario** - Se reporta pero no bloquea la revisión

## 💡 Mejores Prácticas

1. **Revisar regularmente** - Ejecuta revisiones después de cada sprint o cuando se completen tareas
2. **Configurar rutas correctas** - Asegúrate de que las rutas del proyecto Kotlin sean correctas
3. **Revisar feedback manualmente** - Aunque el sistema es automático, siempre revisa el feedback generado
4. **Personalizar checks** - Ajusta los checks según las necesidades de tu proyecto
5. **Mantener actualizado** - Actualiza la guía de implementación cuando haya cambios en los requisitos

## 🔗 Referencias

- [Trello API - Comments](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/#actions)
- [Kotlin Implementation Guide](../ReachuSwiftSDK/KOTLIN_IMPLEMENTATION_GUIDE.md)
- [Smart Cards Guide](./SMART_CARDS_GUIDE.md)
- [Card Review Guide](./CARD_REVIEW_GUIDE.md)

