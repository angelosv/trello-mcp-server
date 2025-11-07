# ✅ Aliases Instalados Correctamente

## 🎯 Comandos Disponibles

### Gestión del Servicio
- `trello-status` - Ver estado del servicio
- `trello-start` - Iniciar servicio
- `trello-stop` - Detener servicio  
- `trello-restart` - Reiniciar servicio
- `trello-logs` - Ver logs en tiempo real
- `trello-errors` - Ver errores en tiempo real

### Scripts de Automatización
- `trello-detect` - Detectar cambios en Swift SDK
- `trello-validate` - Validar todas las tareas
- `trello-generate` - Generar tarjetas desde guía
- `trello-update` - Actualizar formato de tarjetas

### Funciones Helper
- `trello-monday [opciones]` - Detectar cambios desde el lunes
- `trello-check [número]` - Validar tarea específica (o todas)

## 💡 Ejemplos de Uso

```bash
# Ver estado
trello-status

# Detectar cambios del lunes y crear tarjetas
trello-monday --add-to-guide --auto-create

# Validar tarea específica
trello-check 13

# Ver logs
trello-logs

# Generar nuevas tarjetas
trello-generate --start-task 31 --end-task 35
```

## 🔄 Para Activar los Aliases

**Opción 1:** Recargar tu shell actual
```bash
source ~/.zshrc
```

**Opción 2:** Abrir una nueva terminal (los aliases estarán disponibles automáticamente)

## ✅ Verificación

Después de recargar, prueba:
```bash
trello-status
```

Deberías ver: "Servicio activo" o "Servicio inactivo"


