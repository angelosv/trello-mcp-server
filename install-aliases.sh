#!/bin/bash
# Script para agregar aliases de Trello MCP Server al shell

SHELL_RC="$HOME/.zshrc"
INSTALL_DIR="$HOME/.trello-mcp-server"

# Verificar si ya existen los aliases
if grep -q "# Trello MCP Server aliases" "$SHELL_RC" 2>/dev/null; then
    echo "⚠️  Los aliases ya están instalados"
    echo "   Para reinstalar, elimina las líneas de 'Trello MCP Server aliases' en $SHELL_RC"
    exit 0
fi

echo "🔧 Agregando aliases de Trello MCP Server..."
echo ""

# Agregar aliases al .zshrc
cat >> "$SHELL_RC" << 'EOF'

# Trello MCP Server aliases
alias trello-status='launchctl list | grep -q trello-mcp-server && echo "Servicio activo" || echo "Servicio inactivo"'
alias trello-start='launchctl start com.reachu.trello-mcp-server && echo "Servicio iniciado"'
alias trello-stop='launchctl stop com.reachu.trello-mcp-server && echo "Servicio detenido"'
alias trello-restart='launchctl unload ~/Library/LaunchAgents/com.reachu.trello-mcp-server.plist 2>/dev/null; launchctl load ~/Library/LaunchAgents/com.reachu.trello-mcp-server.plist && echo "Servicio reiniciado"'
alias trello-logs='tail -f ~/.trello-mcp-server/server.log'
alias trello-errors='tail -f ~/.trello-mcp-server/server.error.log'

# Scripts de automatización
alias trello-detect='python3 ~/.trello-mcp-server/scripts/detect_swift_changes.py'
alias trello-validate='python3 ~/.trello-mcp-server/scripts/validate_tasks.py'
alias trello-generate='python3 ~/.trello-mcp-server/scripts/generate_trello_cards.py'
alias trello-update='python3 ~/.trello-mcp-server/scripts/update_cards_template.py'
alias trello-add='python3 ~/.trello-mcp-server/scripts/add_feature.py'

# Función helper para detectar cambios desde el lunes
trello-monday() {
    python3 ~/.trello-mcp-server/scripts/detect_swift_changes.py --since "last monday" "$@"
}

# Función helper para validar una tarea específica
trello-check() {
    if [ -z "$1" ]; then
        python3 ~/.trello-mcp-server/scripts/validate_tasks.py --verbose
    else
        python3 ~/.trello-mcp-server/scripts/validate_tasks.py --task-number "$1"
    fi
}
EOF

echo "✅ Aliases agregados a $SHELL_RC"
echo ""
echo "📋 Aliases disponibles:"
echo "   trello-status      - Ver estado del servicio"
echo "   trello-start       - Iniciar servicio"
echo "   trello-stop        - Detener servicio"
echo "   trello-restart     - Reiniciar servicio"
echo "   trello-logs        - Ver logs en tiempo real"
echo "   trello-errors      - Ver errores en tiempo real"
echo ""
echo "📚 Scripts de automatización:"
echo "   trello-detect      - Detectar cambios en Swift SDK"
echo "   trello-validate    - Validar todas las tareas"
echo "   trello-generate    - Generar tarjetas desde guía"
echo "   trello-update      - Actualizar formato de tarjetas"
echo "   trello-add         - Agregar nueva funcionalidad (interactivo)"
echo ""
echo "🎯 Funciones helper:"
echo "   trello-monday      - Detectar cambios desde el lunes"
echo "   trello-check [N]   - Validar tarea específica (o todas)"
echo ""
echo "💡 Ejemplos de uso:"
echo "   trello-monday --add-to-guide --auto-create"
echo "   trello-check 13"
echo "   trello-logs"
echo ""
echo "🔄 Recarga tu shell con: source ~/.zshrc"
echo "   O simplemente abre una nueva terminal"

