# Instrucciones para Mover Tarjetas de Engagement

## Tarjetas Prioritarias a Mover

Las siguientes tarjetas deben moverse del **Backlog** a **To do**:

1. **Testing: Engagement Backend Improvements** (ID: `6985f75601b379d47f292a75`)
   - Prioridad: ALTA
   - Razón: Crítica para validar las mejoras implementadas

2. **Backend: Actualizar API para aceptar API key en headers** (ID: `6985f758865df376c0242f49`)
   - Prioridad: MEDIA (pero importante para seguridad)
   - Razón: Mejora de seguridad, el SDK ya está listo

## Cómo Moverlas

### Opción 1: Manualmente en Trello
1. Ir a: https://trello.com/b/BiGFGFvQ/dev
2. Encontrar las tarjetas en la lista "backlog"
3. Arrastrarlas a la lista "To do"

### Opción 2: Usando el script (requiere credenciales válidas)
```bash
cd /Users/angelo/Documents/GitHub/trello-mcp-server
python3 scripts/move_cards.py \
    --board-id 6964ea21570279f07def7786 \
    --from-list-name "backlog" \
    --to-list-name "To do" \
    --first-n 2
```

### Opción 3: Usando curl directamente
```bash
# Mover tarjeta 1
curl -X PUT "https://api.trello.com/1/cards/6985f75601b379d47f292a75?idList=6964ed62b23b70bbd5c89432&key=YOUR_API_KEY&token=YOUR_TOKEN"

# Mover tarjeta 2
curl -X PUT "https://api.trello.com/1/cards/6985f758865df376c0242f49?idList=6964ed62b23b70bbd5c89432&key=YOUR_API_KEY&token=YOUR_TOKEN"
```

## IDs de Referencia
- Board ID: `6964ea21570279f07def7786`
- Backlog List ID: `6985d6babb14a3a08db187a8`
- To Do List ID: `6964ed62b23b70bbd5c89432`
