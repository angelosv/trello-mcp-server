# Guía de Tarjetas Inteligentes en Trello MCP

## Descripción

El servidor MCP de Trello ahora incluye herramientas inteligentes que analizan el código antes de crear tarjetas, determinando automáticamente si los cambios son relevantes para implementación en Kotlin.

## Herramientas Disponibles

### 1. `create_smart_card_from_commit`

Analiza un commit específico y crea una tarjeta solo si es relevante para Kotlin.

**Parámetros:**
- `commit_hash` (requerido): Hash del commit a analizar
- `idList` (requerido): ID de la lista donde crear la tarjeta
- `idMembers` (opcional): IDs de miembros separados por comas
- `idLabels` (opcional): IDs de labels separados por comas

**Ejemplo de uso:**
```
Analiza el commit 4e2a84f y crea una tarjeta si es relevante para Kotlin
```

### 2. `create_smart_cards_from_recent_commits`

Analiza commits recientes y crea tarjetas automáticamente para los relevantes.

**Parámetros:**
- `idList` (requerido): ID de la lista donde crear las tarjetas
- `since` (opcional): Fecha desde la cual analizar (default: "today")
  - Ejemplos: "today", "yesterday", "7 days ago", "2024-11-07"
- `idMembers` (opcional): IDs de miembros separados por comas
- `idLabels` (opcional): IDs de labels separados por comas
- `dry_run` (opcional): Si es True, solo analiza sin crear tarjetas

**Ejemplo de uso:**
```
Analiza los commits de hoy y crea tarjetas para los relevantes en Kotlin
```

### 3. `analyze_file_for_kotlin`

Analiza un archivo específico para determinar si es relevante para Kotlin.

**Parámetros:**
- `file_path` (requerido): Ruta del archivo a analizar
- `commit_hash` (opcional): Hash del commit para analizar cambios específicos

**Ejemplo de uso:**
```
Analiza si Sources/ReachuUI/Components/RProductCard.swift es relevante para Kotlin
```

## Criterios de Relevancia

Un cambio se considera relevante para Kotlin si:

1. **Ubicación del archivo:**
   - Está en `Sources/ReachuCore/`
   - Está en `Sources/ReachuUI/`
   - Está en `Sources/ReachuDesignSystem/`
   - Está en `Sources/ReachuNetwork/`

2. **Tipo de cambio:**
   - Cambios en API pública (`public` keywords)
   - Nuevas funcionalidades (`func`, `function`)
   - Nuevos modelos (`struct`, `class`, `enum`)
   - Cambios significativos (>50 líneas modificadas)

3. **Keywords relevantes encontrados:**
   - `public`, `struct`, `class`, `enum`, `func`, `protocol`
   - `Configuration`, `Manager`, `Service`, `Component`, `Model`
   - `API`, `Network`, `Cache`, `Localization`, `Translation`

## Exclusiones Automáticas

Los siguientes cambios NO se consideran relevantes:

- Archivos en `.vscode/`, `Demo/`, `Tests/`
- Cambios en configuración de proyecto (`.xcodeproj`, `.xcworkspace`)
- Archivos de documentación (`README.md`, `CHANGELOG.md`)
- Cambios solo en UI específica de Swift (`import SwiftUI`, `@State`, `View`)

## Flujo de Trabajo Recomendado

1. **Después de hacer commits en Swift SDK:**
   ```
   Usa create_smart_cards_from_recent_commits con since="today"
   ```

2. **Para analizar un commit específico:**
   ```
   Usa create_smart_card_from_commit con el hash del commit
   ```

3. **Para verificar un archivo antes de crear tarjeta:**
   ```
   Usa analyze_file_for_kotlin para ver el análisis
   ```

## Ventajas

- ✅ Solo crea tarjetas cuando es necesario
- ✅ Analiza automáticamente el código
- ✅ Identifica cambios relevantes vs irrelevantes
- ✅ Genera descripciones detalladas con contexto
- ✅ Evita crear tarjetas duplicadas o innecesarias

## Ejemplo de Tarjeta Generada

Cuando se crea una tarjeta inteligente, incluye:

- Hash del commit y autor
- Mensaje del commit
- Lista de archivos relevantes con tipo de cambio
- Keywords encontrados
- Estadísticas de cambios (+líneas, -líneas)
- Tareas sugeridas como checklist

## Troubleshooting

Si una tarjeta no se crea cuando esperabas:

1. Verifica que el archivo esté en `Sources/`
2. Revisa el análisis con `analyze_file_for_kotlin`
3. Verifica que haya keywords relevantes en los cambios
4. Usa `dry_run=True` para ver qué se detectaría sin crear tarjetas

