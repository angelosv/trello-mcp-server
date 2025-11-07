# 🎯 Guía Rápida: Agregar Funcionalidades a Reachu Dev y Tipio Dev

## 📋 Tableros de Trabajo

- **Reachu Dev**: `5dea6d99c0ea505b4c3a435e`
- **Tipio Dev**: `662a4b0e2b9175b39e04f54b`

## 🚀 Formas de Agregar Funcionalidades

### 1. Modo Interactivo (Recomendado)

```bash
trello-add --interactive
```

Te guiará paso a paso:
1. Seleccionar tablero (Reachu Dev o Tipio Dev)
2. Seleccionar lista
3. Nombre de la funcionalidad
4. Descripción (manual o desde archivo Swift)
5. Etiquetas
6. Miembros

### 2. Desde Archivo Swift

```bash
trello-add --board "Reachu Dev" \
  --name "Portar RNewFeature a Kotlin" \
  --swift-file "Sources/ReachuSDK/Features/RNewFeature.swift" \
  --tags "Kotlin,Backend,Prioridad"
```

### 3. Descripción Manual

```bash
trello-add --board "Tipio Dev" \
  --name "Implementar nueva funcionalidad X" \
  --description "Descripción detallada aquí..." \
  --list "To Do" \
  --tags "Kotlin,UX/UI"
```

## 💡 Ejemplos Comunes

### Agregar funcionalidad detectada en Swift SDK

```bash
# 1. Detectar cambios
trello-monday --add-to-guide

# 2. Revisar la guía actualizada
# 3. Agregar manualmente con trello-add o generar desde guía
trello-generate --start-task X --end-task Y
```

### Agregar funcionalidad nueva desde archivo Swift

```bash
trello-add --board "Reachu Dev" \
  --name "Portar CampaignManager a Kotlin" \
  --swift-file "Sources/ReachuSDK/Managers/CampaignManager.swift" \
  --tags "Kotlin,Backend,Manager" \
  --list "To Do"
```

### Agregar tarea rápida

```bash
trello-add --interactive
# Selecciona Reachu Dev > To Do
# Nombre: "Revisar implementación de X"
# Descripción: breve
```

## 🎯 Flujo Recomendado

### Lunes (Detección Automática)
```bash
trello-monday --add-to-guide --auto-create
```

### Durante la Semana (Agregar Manualmente)
```bash
# Opción 1: Interactivo
trello-add --interactive

# Opción 2: Desde archivo Swift
trello-add --board "Reachu Dev" --name "..." --swift-file "..."

# Opción 3: Desde Cursor
"Muestra las listas de Reachu Dev"
"Crea una tarjeta en Reachu Dev > To Do llamada 'X'"
```

### Viernes (Validación)
```bash
trello-check
```

## 📝 Desde Cursor

También puedes usar comandos naturales en Cursor:

```
Muestra las listas de Reachu Dev
Crea una tarjeta en Reachu Dev > To Do llamada "Nueva funcionalidad"
Muéstrame las tarjetas de Tipio Dev
```

## 🔧 Configuración

Asegúrate de tener configurado:
- `TRELLO_API_KEY` en tu entorno
- `TRELLO_TOKEN` en tu entorno

Verificar:
```bash
echo $TRELLO_API_KEY
echo $TRELLO_TOKEN
```

## 📚 Más Información

- `QUICK_REFERENCE.md` - Todos los comandos disponibles
- `PROCESS_DOCUMENTATION.md` - Proceso completo
- `CURSOR_USAGE.md` - Uso desde Cursor

