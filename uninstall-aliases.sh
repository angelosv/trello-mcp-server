#!/bin/bash
# Script para remover aliases de Trello MCP Server

SHELL_RC="$HOME/.zshrc"

if [ ! -f "$SHELL_RC" ]; then
    echo "❌ No se encontró $SHELL_RC"
    exit 1
fi

# Crear backup
cp "$SHELL_RC" "${SHELL_RC}.backup.$(date +%Y%m%d_%H%M%S)"

# Remover líneas entre los comentarios de inicio y fin
sed -i.bak '/# Trello MCP Server aliases/,/^EOF$/d' "$SHELL_RC" 2>/dev/null || \
sed -i '' '/# Trello MCP Server aliases/,/^EOF$/d' "$SHELL_RC" 2>/dev/null || \
python3 << EOF
import re
with open("$SHELL_RC", "r") as f:
    content = f.read()
# Remover desde "# Trello MCP Server aliases" hasta el siguiente bloque vacío o EOF
pattern = r'# Trello MCP Server aliases.*?(?=\n\n|\Z)'
content = re.sub(pattern, '', content, flags=re.DOTALL)
with open("$SHELL_RC", "w") as f:
    f.write(content)
EOF

echo "✅ Aliases removidos de $SHELL_RC"
echo "📝 Backup guardado en ${SHELL_RC}.backup.*"
echo "🔄 Recarga tu shell con: source ~/.zshrc"


