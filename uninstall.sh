#!/bin/bash
# Desinstalador del Trello MCP Server

SERVICE_NAME="com.reachu.trello-mcp-server"
SERVICE_FILE="$HOME/Library/LaunchAgents/${SERVICE_NAME}.plist"
INSTALL_DIR="$HOME/.trello-mcp-server"

echo "🗑️  Desinstalando Trello MCP Server..."
echo ""

# Detener y descargar servicio
if [ -f "$SERVICE_FILE" ]; then
    echo "🛑 Deteniendo servicio..."
    launchctl unload "$SERVICE_FILE" 2>/dev/null || true
    rm -f "$SERVICE_FILE"
    echo "✅ Servicio eliminado"
fi

# Eliminar directorio de instalación
if [ -d "$INSTALL_DIR" ]; then
    read -p "¿Eliminar directorio de instalación ($INSTALL_DIR)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        echo "✅ Directorio eliminado"
    else
        echo "ℹ️  Directorio mantenido en $INSTALL_DIR"
    fi
fi

echo ""
echo "✅ Desinstalación completada"

