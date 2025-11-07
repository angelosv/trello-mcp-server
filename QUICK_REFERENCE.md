# Scripts de Automatización - Resumen Rápido

## 🎯 Tableros de Trabajo

- **Reachu Dev**: Tablero principal para desarrollo Reachu
- **Tipio Dev**: Tablero principal para desarrollo Tipio

## 🚀 Scripts Disponibles

### 1. `trello-add` ⭐ NUEVO - Agregar Funcionalidades
**Agrega nuevas funcionalidades a Reachu Dev o Tipio Dev**

```bash
# Modo interactivo (recomendado)
trello-add --interactive

# Desde archivo Swift
trello-add --board "Reachu Dev" --name "Portar X" --swift-file "Sources/Path/File.swift"

# Descripción manual
trello-add --board "Tipio Dev" --name "Nueva funcionalidad" --description "Descripción..."
```

### 2. `trello-generate`
**Genera nuevas tarjetas desde la guía de implementación**

```bash
trello-generate --start-task 31 --end-task 35
```

### 3. `trello-update`
**Actualiza tarjetas existentes con template mejorado**

```bash
trello-update
```

### 4. `trello-detect` / `trello-monday`
**Detecta cambios en Swift SDK y sugiere nuevas tareas**

```bash
# Analizar cambios desde el lunes
trello-monday

# Analizar y agregar a la guía
trello-monday --add-to-guide

# Analizar y crear tarjetas automáticamente
trello-monday --add-to-guide --auto-create
```

### 5. `trello-validate` / `trello-check`
**Valida que las tareas estén completas**

```bash
# Validar todas las tareas
trello-check

# Validar con detalles
trello-validate --verbose

# Validar tarea específica
trello-check 13
```

## 📅 Flujo Semanal Recomendado

### Lunes: Detectar Cambios
```bash
# 1. Detectar cambios desde el lunes pasado
trello-monday --add-to-guide

# 2. Revisar sugerencias y ajustar si es necesario
# 3. Crear tarjetas automáticamente
trello-monday --add-to-guide --auto-create
```

### Durante la Semana: Agregar Funcionalidades
```bash
# Agregar nueva funcionalidad (interactivo)
trello-add --interactive

# O desde archivo Swift
trello-add --board "Reachu Dev" --name "Portar X" --swift-file "Sources/Path/File.swift"
```

### Antes de Empezar: Validar
```bash
# Validar que las tareas estén completas antes de empezar
trello-check 13
```

### Viernes: Revisión
```bash
# Validar todas las tareas
trello-check --verbose
```

## 🎯 Casos de Uso Comunes

### Agregar nueva funcionalidad detectada en Swift
```bash
# Opción 1: Automático desde cambios
trello-monday --add-to-guide --auto-create

# Opción 2: Manual desde archivo Swift
trello-add --board "Reachu Dev" --name "Portar CampaignManager" \
  --swift-file "Sources/ReachuSDK/Managers/CampaignManager.swift" \
  --tags "Kotlin,Backend"
```

### Agregar funcionalidad nueva manualmente
```bash
trello-add --interactive
```

### Generar tarjetas desde guía actualizada
```bash
trello-generate --start-task X --end-task Y
```

### Actualizar formato de tarjetas existentes
```bash
trello-update
```

### Verificar calidad antes de empezar trabajo
```bash
trello-check 13 --verbose
```

## 📚 Documentación Completa

- **Proceso completo**: `PROCESS_DOCUMENTATION.md`
- **Contexto para Cursor**: `CURSOR_CONTEXT.md`

