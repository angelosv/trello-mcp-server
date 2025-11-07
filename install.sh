#!/bin/bash
# Instalador del Trello MCP Server
# Instala el servidor como servicio del sistema y configura todo automáticamente

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.trello-mcp-server"
SERVICE_NAME="com.reachu.trello-mcp-server"
SERVICE_FILE="$HOME/Library/LaunchAgents/${SERVICE_NAME}.plist"

echo "🚀 Instalando Trello MCP Server..."
echo ""

# Crear directorio de instalación
echo "📁 Creando directorio de instalación..."
mkdir -p "$HOME/.local/share" 2>/dev/null || true
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$HOME/Library/LaunchAgents"

# Copiar archivos del servidor
echo "📋 Copiando archivos del servidor..."
cp -r "$SCRIPT_DIR"/server "$INSTALL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR"/main.py "$INSTALL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR"/pyproject.toml "$INSTALL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR"/requirements.txt "$INSTALL_DIR/" 2>/dev/null || true

# Copiar scripts de automatización
echo "📋 Copiando scripts de automatización..."
cp "$SCRIPT_DIR"/*.py "$INSTALL_DIR/scripts/" 2>/dev/null || true
cp "$SCRIPT_DIR"/scripts/*.py "$INSTALL_DIR/scripts/" 2>/dev/null || true

# Copiar documentación
echo "📋 Copiando documentación..."
cp "$SCRIPT_DIR"/*.md "$INSTALL_DIR/" 2>/dev/null || true

# Verificar que .env existe
if [ ! -f "$INSTALL_DIR/.env" ]; then
    if [ -f "$SCRIPT_DIR/.env" ]; then
        cp "$SCRIPT_DIR/.env" "$INSTALL_DIR/.env"
    else
        echo "⚠️  No se encontró .env. Creando template..."
        cat > "$INSTALL_DIR/.env" << EOF
TRELLO_API_KEY=your_trello_api_key
TRELLO_TOKEN=your_trello_token
USE_CLAUDE_APP=false
MCP_SERVER_PORT=8000
MCP_SERVER_HOST=0.0.0.0
EOF
        echo "📝 Por favor edita $INSTALL_DIR/.env con tus credenciales"
    fi
fi

# Crear servicio launchd
echo "🔧 Creando servicio del sistema..."
cat > "$SERVICE_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${SERVICE_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>${INSTALL_DIR}/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${INSTALL_DIR}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${INSTALL_DIR}/server.log</string>
    <key>StandardErrorPath</key>
    <string>${INSTALL_DIR}/server.error.log</string>
</dict>
</plist>
EOF

# Instalar dependencias Python
echo "📦 Instalando dependencias Python..."
cd "$INSTALL_DIR"
if command -v pip3 &> /dev/null; then
    pip3 install -q -r requirements.txt 2>/dev/null || pip3 install -q httpx "mcp[cli]" python-dotenv uvicorn starlette fastmcp
else
    echo "⚠️  pip3 no encontrado. Por favor instala las dependencias manualmente:"
    echo "   pip3 install httpx mcp python-dotenv uvicorn starlette fastmcp"
fi

# Hacer scripts ejecutables
chmod +x "$INSTALL_DIR/scripts"/*.py 2>/dev/null || true

# Cargar servicio
echo "🔄 Cargando servicio..."
launchctl unload "$SERVICE_FILE" 2>/dev/null || true
launchctl load "$SERVICE_FILE"

echo ""
echo "✅ Instalación completada!"
echo ""
echo "📍 Ubicación: $INSTALL_DIR"
echo "📝 Logs: $INSTALL_DIR/server.log"
echo "🔧 Scripts: $INSTALL_DIR/scripts/"
echo ""
echo "🔧 Comandos útiles:"
echo "   Iniciar:   launchctl start ${SERVICE_NAME}"
echo "   Detener:   launchctl stop ${SERVICE_NAME}"
echo "   Reiniciar: launchctl unload $SERVICE_FILE && launchctl load $SERVICE_FILE"
echo "   Ver logs:  tail -f $INSTALL_DIR/server.log"
echo ""
echo "📚 Scripts disponibles:"
echo "   $INSTALL_DIR/scripts/generate_trello_cards.py"
echo "   $INSTALL_DIR/scripts/detect_swift_changes.py"
echo "   $INSTALL_DIR/scripts/validate_tasks.py"
echo ""
echo "⚠️  No olvides editar $INSTALL_DIR/.env con tus credenciales de Trello"
echo ""
echo "💡 Tip: Instala aliases para comandos más cortos:"
echo "   ./install-aliases.sh"
