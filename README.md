# Trello MCP Server

Servidor MCP (Model Context Protocol) para integración de Trello con Cursor, incluyendo scripts de automatización para gestión de tareas del SDK Kotlin.

## 🚀 Inicio Rápido

```bash
# Instalar como servicio del sistema
./install.sh

# O usar Docker
docker-compose up -d

# O ejecutar manualmente
python3 main.py
```

## 📚 Documentación

- **[INSTALLATION.md](INSTALLATION.md)** - Guía completa de instalación y configuración
- **[PROCESS_DOCUMENTATION.md](PROCESS_DOCUMENTATION.md)** - Proceso completo de gestión de tareas
- **[CURSOR_CONTEXT.md](CURSOR_CONTEXT.md)** - Contexto para Cursor
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Referencia rápida de scripts

## 🔧 Scripts de Automatización

- `generate_trello_cards.py` - Genera tarjetas desde la guía
- `detect_swift_changes.py` - Detecta cambios en Swift SDK
- `validate_tasks.py` - Valida completitud de tareas
- `update_cards_template.py` - Actualiza formato de tarjetas

Ver `QUICK_REFERENCE.md` para más detalles.

## 🐳 Docker

```bash
docker-compose up -d
docker-compose logs -f
```

## 📝 Configuración

1. Copia `.env.example` a `.env`
2. Agrega tus credenciales de Trello
3. Configura Cursor en `~/.cursor/mcp.json`

Ver `INSTALLATION.md` para detalles completos.
