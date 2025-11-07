# 🎯 Aliases de Trello MCP Server

## 📋 Comandos Disponibles

### Gestión del Servicio

```bash
trello-status      # Ver estado del servicio
trello-start       # Iniciar servicio
trello-stop        # Detener servicio
trello-restart     # Reiniciar servicio
trello-logs        # Ver logs en tiempo real (Ctrl+C para salir)
trello-errors      # Ver errores en tiempo real
```

### Scripts de Automatización

```bash
trello-detect      # Detectar cambios en Swift SDK
trello-validate    # Validar todas las tareas
trello-generate    # Generar tarjetas desde guía
trello-update      # Actualizar formato de tarjetas
```

### Funciones Helper (con parámetros)

```bash
# Detectar cambios desde el lunes con opciones
trello-monday --add-to-guide --auto-create
trello-monday --since "7 days ago" --dry-run

# Validar tarea específica o todas
trello-check 13              # Validar tarea #13
trello-check                 # Validar todas las tareas
trello-check --verbose       # Validar todas con detalles
```

## 💡 Ejemplos de Uso

### Lunes: Detectar cambios del fin de semana
```bash
trello-monday --add-to-guide --auto-create
```

### Antes de empezar trabajo
```bash
trello-check 13
```

### Ver qué está pasando con el servidor
```bash
trello-status
trello-logs
```

### Generar nuevas tarjetas
```bash
trello-generate --start-task 31 --end-task 35
```

### Validar todas las tareas
```bash
trello-validate --verbose
```

## 🔧 Instalación

```bash
cd ~/trello-mcp-server
./install-aliases.sh
source ~/.zshrc  # O abre una nueva terminal
```

## 🗑️ Desinstalación

```bash
cd ~/trello-mcp-server
./uninstall-aliases.sh
source ~/.zshrc
```


