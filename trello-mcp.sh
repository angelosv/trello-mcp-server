#!/bin/bash
# Script de gestión del servicio Trello MCP Server

SERVICE_NAME="com.reachu.trello-mcp-server"
SERVICE_FILE="$HOME/Library/LaunchAgents/${SERVICE_NAME}.plist"
INSTALL_DIR="$HOME/.trello-mcp-server"

case "$1" in
    start)
        echo "▶️  Iniciando servicio..."
        launchctl load "$SERVICE_FILE" 2>/dev/null || launchctl start "$SERVICE_NAME"
        echo "✅ Servicio iniciado"
        ;;
    stop)
        echo "⏹️  Deteniendo servicio..."
        launchctl stop "$SERVICE_NAME" 2>/dev/null || launchctl unload "$SERVICE_FILE"
        echo "✅ Servicio detenido"
        ;;
    restart)
        echo "🔄 Reiniciando servicio..."
        launchctl unload "$SERVICE_FILE" 2>/dev/null || true
        sleep 1
        launchctl load "$SERVICE_FILE"
        echo "✅ Servicio reiniciado"
        ;;
    status)
        echo "📊 Estado del servicio:"
        if launchctl list | grep -q "$SERVICE_NAME"; then
            echo "✅ Servicio activo"
            echo ""
            echo "📝 Logs recientes:"
            tail -n 20 "$INSTALL_DIR/server.log" 2>/dev/null || echo "   No hay logs disponibles"
        else
            echo "❌ Servicio inactivo"
        fi
        ;;
    logs)
        echo "📝 Mostrando logs (Ctrl+C para salir):"
        tail -f "$INSTALL_DIR/server.log" 2>/dev/null || echo "❌ No se encontraron logs"
        ;;
    install)
        "$(dirname "$0")/install.sh"
        ;;
    uninstall)
        "$(dirname "$0")/uninstall.sh"
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|install|uninstall}"
        echo ""
        echo "Comandos:"
        echo "  start      - Iniciar el servicio"
        echo "  stop       - Detener el servicio"
        echo "  restart    - Reiniciar el servicio"
        echo "  status     - Ver estado y logs recientes"
        echo "  logs       - Ver logs en tiempo real"
        echo "  install    - Instalar el servicio"
        echo "  uninstall  - Desinstalar el servicio"
        exit 1
        ;;
esac

