# 🎯 Guía de Uso en Cursor

## ✅ Estado Actual

- ✅ Servidor MCP instalado y corriendo (`~/.trello-mcp-server`)
- ✅ Servicio del sistema activo (auto-restart habilitado)
- ✅ Cursor configurado (`~/.cursor/mcp.json`)
- ✅ Aliases instalados en tu terminal
- ✅ Scripts de automatización disponibles

## 🔄 Pasos en Cursor

### 1. Reiniciar Cursor (IMPORTANTE)

**Debes reiniciar Cursor completamente** para que detecte el servidor MCP:

1. Cierra Cursor completamente (Cmd+Q)
2. Abre Cursor de nuevo
3. Espera unos segundos para que se conecte al servidor

### 2. Verificar Conexión

Una vez reiniciado Cursor, prueba estos comandos en el chat:

```
Muestra mis tableros de Trello
```

O:

```
¿Qué tableros de Trello tengo?
```

Si funciona, verás la lista de tus tableros.

### 3. Usar Comandos de Trello en Cursor

Ahora puedes usar comandos naturales en Cursor:

**Ver información:**
- "Muestra mis tableros de Trello"
- "¿Qué listas hay en el tablero 'Reachu Dev'?"
- "Muéstrame las tarjetas de la lista 'To Do'"

**Crear tarjetas:**
- "Crea una tarjeta llamada 'Test' en la lista 'To Do' del tablero 'Reachu Dev'"
- "Crea una tarea para Miguel en Kotlin con prioridad"

**Gestionar tarjetas:**
- "Asigna la tarjeta X a Miguel"
- "Agrega la etiqueta 'Prioridad' a la tarjeta Y"
- "Muéstrame los detalles de la tarjeta Z"

### 4. Usar Scripts desde Terminal

Los scripts están disponibles desde cualquier terminal:

```bash
# Ver estado del servidor
trello-status

# Detectar cambios desde el lunes
trello-monday --add-to-guide --auto-create

# Validar tareas
trello-check 13

# Ver logs
trello-logs
```

## 📋 Flujo de Trabajo Recomendado

### Lunes (Detección Automática)
```bash
# En terminal
trello-monday --add-to-guide --auto-create
```

Esto:
1. Detecta cambios en Swift SDK desde el lunes pasado
2. Agrega nuevas tareas a la guía
3. Crea tarjetas en Trello automáticamente

### Durante Desarrollo

**En Cursor:**
- Usa comandos naturales para ver/crear tarjetas
- Pide contexto sobre tareas específicas

**En Terminal:**
- Valida tareas antes de empezar: `trello-check 13`
- Genera nuevas tarjetas: `trello-generate --start-task X --end-task Y`

### Viernes (Revisión)
```bash
# En terminal
trello-validate --verbose
```

## 🔍 Troubleshooting

### Cursor no se conecta al servidor

1. **Verificar que el servidor está corriendo:**
   ```bash
   trello-status
   ```

2. **Ver logs del servidor:**
   ```bash
   trello-logs
   ```

3. **Reiniciar el servidor:**
   ```bash
   trello-restart
   ```

4. **Verificar configuración de Cursor:**
   ```bash
   cat ~/.cursor/mcp.json
   ```
   Debe mostrar: `"url": "http://localhost:8000/sse"`

5. **Reiniciar Cursor completamente** (Cmd+Q y abrir de nuevo)

### El servidor no responde

```bash
# Ver errores
trello-errors

# Reiniciar
trello-restart

# Verificar puerto
lsof -i :8000
```

## 💡 Tips

1. **Siempre reinicia Cursor** después de cambios en el servidor
2. **Usa comandos naturales** en Cursor, no necesitas recordar sintaxis exacta
3. **Los scripts en terminal** son para automatización avanzada
4. **Los logs** te ayudan a debuggear problemas

## 📚 Documentación Completa

- `PROCESS_DOCUMENTATION.md` - Proceso completo
- `CURSOR_CONTEXT.md` - Contexto para Cursor
- `QUICK_REFERENCE.md` - Referencia rápida
- `ALIASES.md` - Todos los aliases disponibles

## ✅ Checklist Inicial

- [ ] Servidor instalado (`trello-status` muestra "activo")
- [ ] Cursor reiniciado completamente
- [ ] Probado comando en Cursor: "Muestra mis tableros"
- [ ] Aliases funcionando (`trello-status` en terminal)
- [ ] Scripts disponibles (`trello-check` funciona)

¡Todo listo para usar! 🚀


