#!/usr/bin/env python3
"""
Script para crear tarjetas de Trello para las mejoras de Engagement implementadas
"""

import os
import json
import subprocess
import time
import sys

# Configuración
API_KEY = os.environ.get('TRELLO_API_KEY')
TOKEN = os.environ.get('TRELLO_TOKEN')
BOARD_ID = '6964ea21570279f07def7786'
LIST_ID = '6985d6babb14a3a08db187a8'  # backlog

if not API_KEY or not TOKEN:
    print("Error: TRELLO_API_KEY and TRELLO_TOKEN must be set")
    sys.exit(1)

def api_call(method, endpoint, data=None):
    """Make API call to Trello"""
    url = f"https://api.trello.com/1/{endpoint}?key={API_KEY}&token={TOKEN}"
    
    if method == "GET":
        result = subprocess.run(['curl', '-s', url], capture_output=True, text=True)
    elif method == "POST":
        if data:
            result = subprocess.run(
                ['curl', '-s', '-X', 'POST', url, '-H', 'Content-Type: application/json', '-d', json.dumps(data)],
                capture_output=True, text=True
            )
        else:
            result = subprocess.run(['curl', '-s', '-X', 'POST', url], capture_output=True, text=True)
    elif method == "PUT":
        result = subprocess.run(['curl', '-s', '-X', 'PUT', url, '-H', 'Content-Type: application/json', '-d', json.dumps(data)], capture_output=True, text=True)
    
    try:
        return json.loads(result.stdout)
    except:
        return None

# Tarjetas a crear
cards = [
    {
        "name": "Testing: Engagement Backend Improvements",
        "desc": """## Testing de las mejoras implementadas en Engagement System

### Objetivo
Crear tests unitarios y de integración para las nuevas funcionalidades implementadas en el sistema de Engagement.

### Tareas

#### Tests Unitarios
- [ ] Test de `RequestRetryHandler` con exponential backoff
- [ ] Test de `EngagementCache` con TTL y expiración
- [ ] Test de `EngagementDataValidator` con datos válidos e inválidos
- [ ] Test de `NetworkClient` protocol con mock
- [ ] Test de manejo de errores mejorados

#### Tests de Integración
- [ ] Test de `BackendEngagementRepository` con retry en errores transitorios
- [ ] Test de cache hit/miss scenarios
- [ ] Test de invalidación de cache después de votos
- [ ] Test de validación de datos del backend

#### Archivos a crear
- `Tests/ReachuEngagementSystemTests/RequestRetryHandlerTests.swift`
- `Tests/ReachuEngagementSystemTests/EngagementCacheTests.swift`
- `Tests/ReachuEngagementSystemTests/EngagementDataValidatorTests.swift`
- `Tests/ReachuEngagementSystemTests/BackendEngagementRepositoryTests.swift`

### Referencias
- Branch: `feature/engagement-backend-improvements` (merged)
- Changelog: `CHANGELOG_ENGAGEMENT_IMPROVEMENTS.md`
- Archivos nuevos: `NetworkClient.swift`, `EngagementCache.swift`, `RequestRetryHandler.swift`, `EngagementMetrics.swift`, `EngagementDataValidator.swift`

### Prioridad
ALTA - Necesario para validar que las mejoras funcionan correctamente""",
        "labels": ["testing", "swift", "sdk"],
        "checklist": [
            "Crear estructura de tests para RequestRetryHandler",
            "Implementar tests de exponential backoff",
            "Crear tests para EngagementCache con TTL",
            "Implementar tests de validación de datos",
            "Crear mocks de NetworkClient para testing",
            "Implementar tests de integración para BackendEngagementRepository",
            "Validar que cache funciona correctamente",
            "Validar que retry funciona en errores transitorios"
        ]
    },
    {
        "name": "Backend: Actualizar API para aceptar API key en headers",
        "desc": """## Actualización del Backend para API Key en Headers

### Objetivo
Actualizar el backend para aceptar la API key en el header HTTP `X-API-Key` además de en query parameters (backward compatibility).

### Cambios Requeridos

#### Endpoints afectados
- `GET /v1/engagement/polls`
- `GET /v1/engagement/contests`
- `POST /v1/engagement/polls/{pollId}/vote`
- `POST /v1/engagement/contests/{contestId}/participate`

#### Implementación
1. **Middleware de autenticación**
   - Verificar header `X-API-Key` primero
   - Fallback a query parameter `apiKey` (backward compatibility)
   - Validar API key contra base de datos

2. **Logging**
   - Remover API key de logs cuando viene en query params
   - No loguear API key cuando viene en header (ya no aparece)

3. **Documentación**
   - Actualizar documentación de API
   - Marcar query param como deprecated
   - Recomendar uso de header

### Prioridad
MEDIA - Mejora de seguridad pero no bloqueante (backward compatible)

### Referencias
- SDK Swift ya implementado con header `X-API-Key`
- Backward compatible: sigue funcionando con query params""",
        "labels": ["backend", "api", "security"],
        "checklist": [
            "Implementar middleware para leer X-API-Key header",
            "Mantener soporte para query param apiKey (backward compat)",
            "Actualizar validación de autenticación",
            "Remover API key de logs cuando viene en query params",
            "Actualizar documentación de API",
            "Testing de ambos métodos (header y query param)"
        ]
    },
    {
        "name": "Monitoring: Revisar métricas de EngagementRequestMetrics",
        "desc": """## Monitoreo de Métricas de Engagement

### Objetivo
Revisar y analizar las métricas capturadas por `EngagementRequestMetrics` en el sistema de analytics.

### Métricas a Monitorear

#### Métricas Capturadas
- Endpoint llamado (`/v1/engagement/polls`, `/v1/engagement/contests`, etc.)
- Broadcast ID
- Duración de request (ms)
- Status code HTTP
- Tamaño de respuesta (bytes)
- Número de retries
- Errores (si los hay)

#### Dashboards a Crear
1. **Performance Dashboard**
   - Tiempo promedio de respuesta por endpoint
   - P95/P99 latencia
   - Throughput (requests/segundo)

2. **Error Dashboard**
   - Tasa de error por endpoint
   - Tipos de errores más comunes
   - Retry rate

3. **Cache Effectiveness Dashboard**
   - Cache hit rate
   - Tiempo ahorrado por cache hits
   - TTL effectiveness

### Acciones
- [ ] Configurar dashboard en Mixpanel/Analytics
- [ ] Crear alertas para errores altos
- [ ] Crear alertas para latencia alta
- [ ] Revisar métricas semanalmente
- [ ] Ajustar TTL de cache basado en métricas

### Prioridad
MEDIA - Importante para optimización pero no bloqueante

### Referencias
- `EngagementMetrics.swift` - Implementación de métricas
- Integración con `AnalyticsManager`""",
        "labels": ["monitoring", "analytics", "performance"],
        "checklist": [
            "Configurar dashboard en Mixpanel para engagement metrics",
            "Crear alertas para tasa de error > 5%",
            "Crear alertas para latencia P95 > 2s",
            "Revisar métricas de cache hit rate",
            "Documentar métricas importantes",
            "Establecer baseline de performance"
        ]
    },
    {
        "name": "Documentación: Engagement Backend Improvements",
        "desc": """## Documentación de las Mejoras de Engagement

### Objetivo
Documentar las mejoras implementadas en el sistema de Engagement para desarrolladores y usuarios del SDK.

### Documentación Requerida

#### Para Desarrolladores del SDK
1. **Guía de Arquitectura**
   - Explicar nuevos componentes (`NetworkClient`, `EngagementCache`, `RequestRetryHandler`)
   - Diagramas de flujo de datos
   - Patrones de diseño utilizados

2. **Guía de Testing**
   - Cómo crear mocks de `NetworkClient`
   - Cómo testear retry logic
   - Cómo testear cache

3. **Guía de Migración**
   - Cambios en `EngagementError` enum
   - Nuevos métodos y propiedades
   - Backward compatibility notes

#### Para Usuarios del SDK
1. **Release Notes**
   - Nuevas funcionalidades
   - Mejoras de performance
   - Mejoras de seguridad

2. **Best Practices**
   - Cómo manejar errores mejorados
   - Cómo monitorear métricas
   - Configuración recomendada

### Archivos a Crear/Actualizar
- `Documentation/ENGAGEMENT_ARCHITECTURE.md`
- `Documentation/ENGAGEMENT_TESTING.md`
- `Documentation/ENGAGEMENT_MIGRATION.md`
- `README.md` (actualizar sección de Engagement)
- Release notes en GitHub

### Prioridad
BAJA - Documentación importante pero no bloqueante

### Referencias
- `CHANGELOG_ENGAGEMENT_IMPROVEMENTS.md`
- Código fuente de las mejoras""",
        "labels": ["documentation", "sdk"],
        "checklist": [
            "Crear guía de arquitectura de Engagement",
            "Documentar nuevos componentes y su uso",
            "Crear guía de testing con ejemplos",
            "Actualizar README con mejoras",
            "Crear release notes para nueva versión",
            "Documentar métricas disponibles"
        ]
    }
]

# Crear tarjetas
created_cards = []
for card_data in cards:
    print(f"Creating card: {card_data['name']}")
    
    # Crear tarjeta
    card = api_call("POST", f"lists/{LIST_ID}/cards", {
        "name": card_data["name"],
        "desc": card_data["desc"],
        "pos": "top"
    })
    
    if not card or "id" not in card:
        print(f"  ❌ Failed to create card")
        continue
    
    card_id = card["id"]
    created_cards.append(card_id)
    print(f"  ✅ Created card: {card_id}")
    
    # Agregar labels
    if card_data.get("labels"):
        # Primero obtener labels del board
        labels_result = api_call("GET", f"boards/{BOARD_ID}/labels")
        if labels_result:
            for label_name in card_data["labels"]:
                # Buscar label existente o crear nuevo
                label_id = None
                for label in labels_result:
                    if label.get("name") == label_name:
                        label_id = label["id"]
                        break
                
                if not label_id:
                    # Crear nuevo label
                    new_label = api_call("POST", f"boards/{BOARD_ID}/labels", {
                        "name": label_name,
                        "color": "blue"
                    })
                    if new_label and "id" in new_label:
                        label_id = new_label["id"]
                
                if label_id:
                    api_call("POST", f"cards/{card_id}/idLabels", {"value": label_id})
                    time.sleep(0.2)
    
    # Crear checklist
    if card_data.get("checklist"):
        checklist = api_call("POST", f"cards/{card_id}/checklists", {
            "name": "Tareas"
        })
        
        if checklist and "id" in checklist:
            checklist_id = checklist["id"]
            for item in card_data["checklist"]:
                api_call("POST", f"checklists/{checklist_id}/checkItems", {
                    "name": item
                })
                time.sleep(0.2)
    
    time.sleep(0.5)

print(f"\n✅ Created {len(created_cards)} cards successfully!")
