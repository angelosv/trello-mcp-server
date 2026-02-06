#!/bin/bash
# Ejemplo de uso de los scripts de Trello

# Configurar variables de entorno (o usar .env)
export TRELLO_API_KEY="tu_api_key"
export TRELLO_TOKEN="tu_api_token"

# Board ID y List IDs (ejemplo del board "Dev")
BOARD_ID="6964ea21570279f07def7786"
BACKLOG_LIST="6964ed5eeb630c1ed6fcccb0"
TO_DO_LIST="6964ed62b23b70bbd5c89432"

echo "📋 Ejemplos de uso de scripts de Trello"
echo "========================================"
echo ""

# 1. Verificar tarjetas en una lista
echo "1. Verificar tarjetas en Backlog:"
python scripts/verify_cards.py \
    --board-id "$BOARD_ID" \
    --list-id "$BACKLOG_LIST"
echo ""

# 2. Mover primeras 6 tarjetas críticas a "To do"
echo "2. Mover primeras 6 tarjetas críticas a 'To do':"
python scripts/move_cards.py \
    --board-id "$BOARD_ID" \
    --from-list-name "Backlog" \
    --to-list-name "To do" \
    --first-n 6
echo ""

# 3. Completar tarjetas con descripciones y checklists
echo "3. Completar tarjetas (requiere archivo JSON con datos):"
echo "   python scripts/complete_engagement_cards.py \\"
echo "       --board-id \"$BOARD_ID\" \\"
echo "       --list-id \"$TO_DO_LIST\" \\"
echo "       --cards-file cards_data.json"
echo ""

echo "✅ Ejemplos completados"
