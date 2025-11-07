# Trello MCP Server - Instalación y Configuración

## 🚀 Instalación Rápida

### Opción 1: Instalación como Servicio del Sistema (Recomendado)

```bash
cd ~/trello-mcp-server
chmod +x install.sh trello-mcp.sh
./install.sh
```

Esto instalará el servidor en `~/.local/share/trello-mcp-server` y lo ejecutará como servicio del sistema.

### Opción 2: Docker (Para desarrollo o producción)

```bash
cd ~/trello-mcp-server
docker-compose up -d
```

### Opción 3: Ejecución Manual

```bash
cd ~/trello-mcp-server
python3 main.py
```

## 📋 Configuración

### 1. Credenciales de Trello

Edita el archivo `.env`:

```bash
# Ubicación después de instalar:
~/.local/share/trello-mcp-server/.env

# O si ejecutas manualmente:
~/trello-mcp-server/.env
```

```env
TRELLO_API_KEY=tu_api_key
TRELLO_TOKEN=tu_token
USE_CLAUDE_APP=false
MCP_SERVER_PORT=8000
MCP_SERVER_HOST=0.0.0.0
```

### 2. Configurar Cursor

Edita `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "trello": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## 🔧 Gestión del Servicio

Usa el script `trello-mcp.sh`:

```bash
# Iniciar
./trello-mcp.sh start

# Detener
./trello-mcp.sh stop

# Reiniciar
./trello-mcp.sh restart

# Ver estado
./trello-mcp.sh status

# Ver logs en tiempo real
./trello-mcp.sh logs
```

## 📁 Estructura después de Instalación

```
~/.local/share/trello-mcp-server/
├── main.py                    # Servidor principal
├── server/                    # Código del servidor
├── scripts/                   # Scripts de automatización
│   ├── generate_trello_cards.py
│   ├── detect_swift_changes.py
│   ├── validate_tasks.py
│   └── ...
├── .env                       # Configuración
├── server.log                 # Logs del servidor
└── server.error.log           # Logs de errores
```

## 🐳 Docker

### Desarrollo

```bash
docker-compose up
```

### Producción

```bash
docker-compose up -d
docker-compose logs -f
```

## 🔍 Verificación

### Verificar que el servidor está corriendo

```bash
curl http://localhost:8000/sse
```

### Verificar desde Cursor

En Cursor, intenta usar comandos como:
- "Muestra mis tableros de Trello"
- "Crea una tarjeta en..."

## 🛠️ Troubleshooting

### El servidor no inicia

1. Verificar logs:
   ```bash
   tail -f ~/.local/share/trello-mcp-server/server.log
   ```

2. Verificar que el puerto 8000 esté libre:
   ```bash
   lsof -i :8000
   ```

3. Verificar credenciales en `.env`

### Cursor no se conecta

1. Verificar que el servidor esté corriendo
2. Verificar la URL en `~/.cursor/mcp.json`
3. Reiniciar Cursor

### Reinstalar

```bash
./trello-mcp.sh uninstall
./install.sh
```

## 📚 Scripts de Automatización

Los scripts están disponibles en:
- `~/.local/share/trello-mcp-server/scripts/` (después de instalar)
- `~/trello-mcp-server/` (desarrollo)

Ver `QUICK_REFERENCE.md` para más detalles.

## 🔄 Actualización

```bash
cd ~/trello-mcp-server
git pull  # Si usas git
./trello-mcp.sh restart
```

## 🗑️ Desinstalación

```bash
./trello-mcp.sh uninstall
```

Esto detendrá el servicio y eliminará los archivos (opcional).


