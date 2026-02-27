# Prompt de Implementación: Sistema de Gestión de Broadcasts

## 🎯 Objetivo

Implementar un sistema completo de gestión de Broadcasts (equivalente a Programs de LiveLike) que permita:
1. Crear y gestionar broadcasts antes de los eventos
2. Asociar campañas a broadcasts
3. Validar broadcasts cuando el SDK los usa
4. Dashboard UI completo para gestión de broadcasts

---

## 📋 Contexto y Arquitectura Actual

### Estado Actual
- ✅ Existe tabla `campaigns` con campo `match_id` (que almacena `broadcastId`)
- ✅ Existe endpoint `GET /v1/sdk/campaigns?broadcastId=...` para auto-discovery
- ✅ El SDK envía `broadcastId` desde el cliente sin validación
- ❌ No existe tabla `broadcasts` independiente
- ❌ No existe API para crear/gestionar broadcasts
- ❌ No existe validación de que `broadcastId` existe

### Arquitectura Propuesta
```
┌─────────────────┐
│   Dashboard UI  │ ← Crear/Editar Broadcasts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backend API    │ ← POST/GET/PUT/DELETE /v1/broadcasts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  broadcasts DB  │ ← Tabla broadcasts (nueva)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  campaigns DB   │ ← campaigns.match_id → broadcasts.broadcast_id (FK)
└─────────────────┘
```

---

## 🗄️ FASE 1: Base de Datos

### 1.1 Crear Tabla `broadcasts`

```sql
CREATE TABLE broadcasts (
    broadcast_id VARCHAR(255) PRIMARY KEY COMMENT 'Identificador único del broadcast (ej: barcelona-psg-2025-01-23)',
    broadcast_name VARCHAR(255) NOT NULL COMMENT 'Nombre legible del broadcast (ej: Barcelona vs PSG)',
    start_time TIMESTAMP NULL COMMENT 'Fecha y hora de inicio del broadcast (ISO 8601)',
    end_time TIMESTAMP NULL COMMENT 'Fecha y hora de fin del broadcast (ISO 8601)',
    channel_id INT NULL COMMENT 'ID del canal asociado (mismo que campaigns.channel_id)',
    status ENUM('upcoming', 'live', 'ended') DEFAULT 'upcoming' COMMENT 'Estado del broadcast',
    metadata JSON NULL COMMENT 'Metadata adicional (equipos, competencia, estadio, etc.)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de última actualización',
    created_by INT NULL COMMENT 'ID del usuario que creó el broadcast',
    
    INDEX idx_status (status),
    INDEX idx_channel_id (channel_id),
    INDEX idx_start_time (start_time),
    INDEX idx_status_start_time (status, start_time),
    
    FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 1.2 Agregar Foreign Key a `campaigns`

```sql
-- Agregar constraint para validar que match_id existe en broadcasts
ALTER TABLE campaigns
ADD CONSTRAINT fk_campaigns_broadcast_id
FOREIGN KEY (match_id) REFERENCES broadcasts(broadcast_id)
ON DELETE SET NULL
ON UPDATE CASCADE;

-- Crear índice para mejorar performance de queries
CREATE INDEX idx_campaigns_match_id ON campaigns(match_id);
```

### 1.3 Migración de Datos Existentes (Opcional)

```sql
-- Si ya existen campañas con match_id, crear broadcasts automáticamente
INSERT INTO broadcasts (broadcast_id, broadcast_name, start_time, channel_id, status, created_at)
SELECT DISTINCT
    c.match_id,
    COALESCE(c.match_name, c.match_id) as broadcast_name,
    c.match_start_time as start_time,
    c.channel_id,
    CASE
        WHEN c.match_start_time > NOW() THEN 'upcoming'
        WHEN c.match_start_time <= NOW() AND (c.end_date IS NULL OR c.end_date >= NOW()) THEN 'live'
        ELSE 'ended'
    END as status,
    MIN(c.created_at) as created_at
FROM campaigns c
WHERE c.match_id IS NOT NULL
  AND c.match_id NOT IN (SELECT broadcast_id FROM broadcasts)
GROUP BY c.match_id, c.match_name, c.match_start_time, c.channel_id;
```

---

## 🔌 FASE 2: Backend API

### 2.1 Endpoint: POST /v1/broadcasts

**Propósito:** Crear un nuevo broadcast

**Request:**
```json
POST /v1/broadcasts
Content-Type: application/json
Authorization: Bearer {admin_token}

{
  "broadcastId": "barcelona-psg-2025-01-23",  // Opcional: si no se proporciona, auto-generar
  "broadcastName": "Barcelona vs PSG",
  "startTime": "2025-01-23T20:00:00Z",  // ISO 8601
  "endTime": "2025-01-23T22:00:00Z",    // Opcional
  "channelId": 1,                        // Opcional
  "metadata": {                          // Opcional
    "homeTeam": "Barcelona",
    "awayTeam": "PSG",
    "competition": "Champions League",
    "round": "Round of 16",
    "stadium": "Camp Nou"
  }
}
```

**Validaciones:**
1. `broadcastName` es requerido
2. `broadcastId` debe ser único (si se proporciona)
3. Si `broadcastId` no se proporciona, generar automáticamente:
   - Formato: `{channelId}-{timestamp}` o `{name-slug}-{date}`
   - Ejemplo: `1-1706035200` o `barcelona-vs-psg-2025-01-23`
4. `startTime` debe ser válido ISO 8601
5. `endTime` debe ser después de `startTime` (si se proporciona)
6. `channelId` debe existir en tabla `channels` (si se proporciona)
7. `status` se calcula automáticamente:
   - Si `startTime` > ahora → `upcoming`
   - Si `startTime` <= ahora <= `endTime` → `live`
   - Si `endTime` < ahora → `ended`

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "broadcastId": "barcelona-psg-2025-01-23",
    "broadcastName": "Barcelona vs PSG",
    "startTime": "2025-01-23T20:00:00Z",
    "endTime": "2025-01-23T22:00:00Z",
    "channelId": 1,
    "status": "upcoming",
    "metadata": {
      "homeTeam": "Barcelona",
      "awayTeam": "PSG",
      "competition": "Champions League"
    },
    "createdAt": "2025-01-20T10:00:00Z",
    "updatedAt": "2025-01-20T10:00:00Z"
  }
}
```

**Errores:**
- `400 Bad Request`: Validación fallida (campos requeridos, formato inválido)
- `409 Conflict`: `broadcastId` ya existe
- `404 Not Found`: `channelId` no existe (si se proporciona)
- `401 Unauthorized`: Token inválido o sin permisos

---

### 2.2 Endpoint: GET /v1/broadcasts/{broadcastId}

**Propósito:** Obtener detalles de un broadcast específico

**Request:**
```
GET /v1/broadcasts/barcelona-psg-2025-01-23
Authorization: Bearer {admin_token}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "broadcastId": "barcelona-psg-2025-01-23",
    "broadcastName": "Barcelona vs PSG",
    "startTime": "2025-01-23T20:00:00Z",
    "endTime": "2025-01-23T22:00:00Z",
    "channelId": 1,
    "channelName": "XXL iOS Channel",
    "status": "upcoming",
    "metadata": {
      "homeTeam": "Barcelona",
      "awayTeam": "PSG",
      "competition": "Champions League"
    },
    "campaigns": [
      {
        "campaignId": 28,
        "campaignName": "Elkjop Campaign",
        "status": "active"
      }
    ],
    "createdAt": "2025-01-20T10:00:00Z",
    "updatedAt": "2025-01-20T10:00:00Z"
  }
}
```

**Errores:**
- `404 Not Found`: Broadcast no existe
- `401 Unauthorized`: Token inválido

---

### 2.3 Endpoint: GET /v1/broadcasts

**Propósito:** Listar broadcasts con filtros y paginación

**Request:**
```
GET /v1/broadcasts?status=upcoming&channelId=1&page=1&limit=20&sortBy=startTime&sortOrder=asc
Authorization: Bearer {admin_token}
```

**Query Parameters:**
- `status` (opcional): Filtrar por estado (`upcoming`, `live`, `ended`)
- `channelId` (opcional): Filtrar por canal
- `startDate` (opcional): Filtrar broadcasts que empiezan después de esta fecha (ISO 8601)
- `endDate` (opcional): Filtrar broadcasts que terminan antes de esta fecha (ISO 8601)
- `search` (opcional): Buscar por nombre o `broadcastId`
- `page` (opcional, default: 1): Número de página
- `limit` (opcional, default: 20): Resultados por página
- `sortBy` (opcional, default: `startTime`): Campo para ordenar (`startTime`, `createdAt`, `broadcastName`)
- `sortOrder` (opcional, default: `desc`): Orden (`asc`, `desc`)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "broadcasts": [
      {
        "broadcastId": "barcelona-psg-2025-01-23",
        "broadcastName": "Barcelona vs PSG",
        "startTime": "2025-01-23T20:00:00Z",
        "endTime": "2025-01-23T22:00:00Z",
        "channelId": 1,
        "channelName": "XXL iOS Channel",
        "status": "upcoming",
        "campaignsCount": 2,
        "createdAt": "2025-01-20T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "totalPages": 3
    }
  }
}
```

---

### 2.4 Endpoint: PUT /v1/broadcasts/{broadcastId}

**Propósito:** Actualizar un broadcast existente

**Request:**
```json
PUT /v1/broadcasts/barcelona-psg-2025-01-23
Content-Type: application/json
Authorization: Bearer {admin_token}

{
  "broadcastName": "Barcelona vs PSG - Updated",
  "startTime": "2025-01-23T21:00:00Z",  // Cambiar hora de inicio
  "endTime": "2025-01-23T23:00:00Z",
  "metadata": {
    "homeTeam": "FC Barcelona",
    "awayTeam": "Paris Saint-Germain",
    "competition": "UEFA Champions League"
  }
}
```

**Validaciones:**
- Solo campos proporcionados se actualizan (PATCH-like behavior)
- `broadcastId` NO se puede cambiar
- `status` se recalcula automáticamente basado en `startTime` y `endTime`
- Validaciones similares a POST

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "broadcastId": "barcelona-psg-2025-01-23",
    "broadcastName": "Barcelona vs PSG - Updated",
    "startTime": "2025-01-23T21:00:00Z",
    "endTime": "2025-01-23T23:00:00Z",
    "status": "upcoming",
    "updatedAt": "2025-01-21T15:30:00Z"
  }
}
```

---

### 2.5 Endpoint: DELETE /v1/broadcasts/{broadcastId}

**Propósito:** Eliminar un broadcast (soft delete)

**Request:**
```
DELETE /v1/broadcasts/barcelona-psg-2025-01-23
Authorization: Bearer {admin_token}
```

**Validaciones:**
- No se puede eliminar si tiene campañas activas asociadas
- Si tiene campañas, retornar error con lista de campañas

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Broadcast deleted successfully"
}
```

**Errores:**
- `400 Bad Request`: Broadcast tiene campañas activas asociadas
- `404 Not Found`: Broadcast no existe

---

### 2.6 Modificar: GET /v1/sdk/campaigns (Validación de BroadcastId)

**Cambio requerido:** Validar que `broadcastId` existe antes de buscar campañas

**Código actual (modificar):**
```python
# Pseudocódigo - ANTES
@router.get("/v1/sdk/campaigns")
async def discover_campaigns(broadcastId: Optional[str] = None):
    campaigns = await db.get_active_campaigns(broadcastId=broadcastId)
    return {"campaigns": campaigns}
```

**Código nuevo:**
```python
# Pseudocódigo - DESPUÉS
@router.get("/v1/sdk/campaigns")
async def discover_campaigns(broadcastId: Optional[str] = None):
    # Si se proporciona broadcastId, validar que existe
    if broadcastId:
        broadcast = await db.get_broadcast(broadcastId)
        if not broadcast:
            raise HTTPException(
                status_code=404,
                detail=f"Broadcast '{broadcastId}' not found"
            )
        
        # Verificar que broadcast está activo o upcoming
        if broadcast.status == "ended":
            # Retornar array vacío, no error (broadcast existe pero terminó)
            return {"campaigns": []}
    
    # Continuar con lógica existente
    campaigns = await db.get_active_campaigns(broadcastId=broadcastId)
    return {"campaigns": campaigns}
```

**Comportamiento:**
- Si `broadcastId` no existe → Error 404 con mensaje claro
- Si `broadcastId` existe pero está `ended` → Retornar array vacío (no error)
- Si `broadcastId` existe y está `upcoming` o `live` → Retornar campañas normalmente
- Si no se proporciona `broadcastId` → Comportamiento actual (retornar todas las campañas activas)

---

## 🎨 FASE 3: Frontend/Dashboard UI

### 3.1 Estructura de Navegación

**Agregar nueva sección "Broadcasts" en el menú principal:**
```
Dashboard
├── Campaigns (existente)
├── Broadcasts (NUEVO) ← Agregar aquí
├── Components (existente)
└── Settings (existente)
```

### 3.2 Página: Lista de Broadcasts

**Ruta:** `/broadcasts`

**Componentes:**
1. **Header con acciones:**
   - Título: "Broadcasts"
   - Botón "Create Broadcast" (lleva a formulario de creación)
   - Botón "Refresh" (recargar lista)

2. **Filtros:**
   - Dropdown "Status" (All, Upcoming, Live, Ended)
   - Dropdown "Channel" (todos los canales)
   - Date picker "Start Date" (filtrar por fecha inicio)
   - Date picker "End Date" (filtrar por fecha fin)
   - Input "Search" (buscar por nombre o ID)

3. **Tabla de Broadcasts:**
   ```
   | Broadcast ID | Name | Channel | Start Time | Status | Campaigns | Actions |
   |--------------|------|---------|------------|--------|-----------|---------|
   | barcelona... | Bar.. | XXL iOS | 2025-01-23 | Upcoming | 2 | [Edit] [Delete] |
   ```

   **Columnas:**
   - **Broadcast ID**: Mostrar primeros 20 caracteres + "..."
   - **Name**: Nombre completo
   - **Channel**: Nombre del canal (o "N/A" si no tiene)
   - **Start Time**: Formato legible (ej: "Jan 23, 2025 8:00 PM")
   - **Status**: Badge con color:
     - `upcoming`: Badge azul
     - `live`: Badge verde
     - `ended`: Badge gris
   - **Campaigns**: Número de campañas asociadas (clickeable → ver campañas)
   - **Actions**: Botones Edit y Delete

4. **Paginación:**
   - Mostrar página actual, total de páginas
   - Botones "Previous" y "Next"
   - Selector de resultados por página (10, 20, 50)

**Estados:**
- **Loading**: Mostrar skeleton/spinner
- **Empty**: Mostrar mensaje "No broadcasts found" con botón "Create Broadcast"
- **Error**: Mostrar mensaje de error con botón "Retry"

---

### 3.3 Página: Crear Broadcast

**Ruta:** `/broadcasts/create`

**Formulario:**
```
┌─────────────────────────────────────┐
│ Create Broadcast                     │
├─────────────────────────────────────┤
│ Broadcast ID*                        │
│ [________________] [Auto-generate]   │
│ (Leave empty to auto-generate)       │
│                                      │
│ Broadcast Name*                      │
│ [Barcelona vs PSG____________]        │
│                                      │
│ Channel                              │
│ [Select Channel ▼]                  │
│                                      │
│ Start Time*                          │
│ [📅] [2025-01-23] [🕐] [20:00]      │
│                                      │
│ End Time                             │
│ [📅] [2025-01-23] [🕐] [22:00]      │
│                                      │
│ Metadata (Optional)                  │
│ ┌─────────────────────────────────┐ │
│ │ Home Team: [Barcelona______]   │ │
│ │ Away Team: [PSG_____________]   │ │
│ │ Competition: [Champions League] │ │
│ │ Round: [Round of 16_________]  │ │
│ │ Stadium: [Camp Nou__________]   │ │
│ └─────────────────────────────────┘ │
│                                      │
│ [Cancel] [Create Broadcast]         │
└─────────────────────────────────────┘
```

**Validaciones en Frontend:**
- `broadcastName` es requerido
- `startTime` es requerido y debe ser fecha futura
- `endTime` debe ser después de `startTime`
- `broadcastId` debe ser único (validar con API antes de crear)

**Flujo:**
1. Usuario llena formulario
2. Click "Create Broadcast"
3. Validar campos en frontend
4. Mostrar loading spinner
5. Llamar `POST /v1/broadcasts`
6. Si éxito → Redirigir a `/broadcasts/{broadcastId}` (página de detalles)
7. Si error → Mostrar mensaje de error específico

---

### 3.4 Página: Detalles de Broadcast

**Ruta:** `/broadcasts/{broadcastId}`

**Layout:**
```
┌─────────────────────────────────────┐
│ ← Back to Broadcasts                │
│                                      │
│ Barcelona vs PSG                    │
│ barcelona-psg-2025-01-23            │
│ [Upcoming] [Edit] [Delete]          │
├─────────────────────────────────────┤
│ Details                             │
│ ┌─────────────────────────────────┐ │
│ │ Start Time: Jan 23, 2025 8:00 PM│ │
│ │ End Time: Jan 23, 2025 10:00 PM │ │
│ │ Channel: XXL iOS Channel       │ │
│ │ Status: Upcoming                │ │
│ └─────────────────────────────────┘ │
│                                      │
│ Metadata                            │
│ ┌─────────────────────────────────┐ │
│ │ Home Team: Barcelona            │ │
│ │ Away Team: PSG                  │ │
│ │ Competition: Champions League   │ │
│ └─────────────────────────────────┘ │
│                                      │
│ Associated Campaigns (2)            │
│ ┌─────────────────────────────────┐ │
│ │ [Elkjop Campaign] [View →]    │ │
│ │ [Power Campaign] [View →]     │ │
│ └─────────────────────────────────┘ │
│                                      │
│ [Edit Broadcast] [Delete Broadcast]│
└─────────────────────────────────────┘
```

**Funcionalidades:**
- Ver todos los detalles del broadcast
- Ver campañas asociadas (con link a página de campaña)
- Botón "Edit" → Lleva a página de edición
- Botón "Delete" → Muestra confirmación antes de eliminar

---

### 3.5 Página: Editar Broadcast

**Ruta:** `/broadcasts/{broadcastId}/edit`

**Formulario:** Similar a crear, pero:
- Pre-llenado con datos actuales
- `broadcastId` es readonly (no se puede cambiar)
- Botón "Save Changes" en lugar de "Create Broadcast"

**Flujo:**
1. Cargar datos del broadcast con `GET /v1/broadcasts/{broadcastId}`
2. Pre-llenar formulario
3. Usuario modifica campos
4. Click "Save Changes"
5. Llamar `PUT /v1/broadcasts/{broadcastId}`
6. Si éxito → Redirigir a página de detalles
7. Si error → Mostrar mensaje de error

---

### 3.6 Integración: Crear Campaña con Broadcast

**Modificar página de creación de campaña:**

**Agregar sección "Broadcast Context":**
```
┌─────────────────────────────────────┐
│ Campaign Settings                   │
│ ...                                 │
│                                      │
│ Broadcast Context                   │
│ ┌─────────────────────────────────┐ │
│ │ [ ] Associate with Broadcast    │ │
│ │                                  │ │
│ │ Broadcast: [Select Broadcast ▼]│ │
│ │                                  │ │
│ │ Or create new:                  │ │
│ │ [Create New Broadcast →]        │ │
│ └─────────────────────────────────┘ │
│                                      │
│ [Save Campaign]                     │
└─────────────────────────────────────┘
```

**Comportamiento:**
- Checkbox "Associate with Broadcast"
- Si está marcado → Mostrar dropdown con broadcasts disponibles
- Dropdown filtra por:
  - Status: `upcoming` o `live`
  - Channel: Mismo que el canal de la campaña
- Opción "Create New Broadcast" → Abre modal o nueva página
- Al seleccionar broadcast → Auto-llenar `match_id`, `match_name`, `match_start_time`

---

### 3.7 Componentes Reutilizables

**1. BroadcastStatusBadge:**
```jsx
<BroadcastStatusBadge status="upcoming" />
// Renderiza: <span className="badge badge-blue">Upcoming</span>
```

**2. BroadcastSelector:**
```jsx
<BroadcastSelector
  value={selectedBroadcastId}
  onChange={setSelectedBroadcastId}
  channelId={campaignChannelId}
  status={['upcoming', 'live']}
/>
```

**3. BroadcastForm:**
```jsx
<BroadcastForm
  initialData={broadcast}
  onSubmit={handleSubmit}
  onCancel={handleCancel}
/>
```

---

## 🔄 FASE 4: Flujos de Usuario

### Flujo 1: Crear Broadcast y Asociar Campaña

```
1. Admin va a /broadcasts
2. Click "Create Broadcast"
3. Llena formulario:
   - Name: "Barcelona vs PSG"
   - Start Time: 2025-01-23 20:00
   - Channel: XXL iOS Channel
4. Click "Create Broadcast"
5. Backend crea broadcast → Retorna broadcastId
6. Frontend redirige a /broadcasts/{broadcastId}
7. Admin ve detalles del broadcast
8. Admin va a crear campaña (/campaigns/create)
9. En sección "Broadcast Context":
   - Marca checkbox "Associate with Broadcast"
   - Selecciona "Barcelona vs PSG" del dropdown
10. Backend asocia campaña con broadcast (guarda match_id)
11. Campaña creada con broadcast asociado
```

### Flujo 2: SDK Usa Broadcast (Validación)

```
1. Usuario abre app → Reproduce video
2. App crea BroadcastContext con broadcastId: "barcelona-psg-2025-01-23"
3. SDK llama: GET /v1/sdk/campaigns?broadcastId=barcelona-psg-2025-01-23
4. Backend valida:
   - ¿Existe broadcast "barcelona-psg-2025-01-23"?
   - ✅ Sí existe → Continuar
   - ❌ No existe → Error 404 "Broadcast not found"
5. Backend busca campañas con match_id = "barcelona-psg-2025-01-23"
6. Retorna campañas asociadas
7. SDK muestra widgets/campañas del broadcast
```

### Flujo 3: Broadcast Termina (Auto-update Status)

```
1. Broadcast tiene startTime: 2025-01-23 20:00, endTime: 2025-01-23 22:00
2. Job/cron job corre cada minuto:
   - Busca broadcasts con status="live" y endTime < NOW()
   - Actualiza status a "ended"
3. SDK intenta usar broadcast terminado:
   - GET /v1/sdk/campaigns?broadcastId=...
   - Backend retorna: {"campaigns": []} (no error, pero sin campañas)
```

---

## ✅ Checklist de Implementación

### Backend
- [ ] Crear tabla `broadcasts` con migración
- [ ] Agregar foreign key `campaigns.match_id → broadcasts.broadcast_id`
- [ ] Implementar `POST /v1/broadcasts`
- [ ] Implementar `GET /v1/broadcasts/{broadcastId}`
- [ ] Implementar `GET /v1/broadcasts` (lista con filtros)
- [ ] Implementar `PUT /v1/broadcasts/{broadcastId}`
- [ ] Implementar `DELETE /v1/broadcasts/{broadcastId}`
- [ ] Modificar `GET /v1/sdk/campaigns` para validar broadcastId
- [ ] Agregar tests unitarios para cada endpoint
- [ ] Agregar tests de integración

### Frontend
- [ ] Agregar ruta `/broadcasts` en router
- [ ] Crear componente `BroadcastsList`
- [ ] Crear componente `BroadcastForm` (crear/editar)
- [ ] Crear componente `BroadcastDetails`
- [ ] Crear componente `BroadcastSelector` (para usar en campañas)
- [ ] Agregar sección "Broadcasts" en menú
- [ ] Integrar selector de broadcast en formulario de campaña
- [ ] Agregar validaciones en frontend
- [ ] Agregar manejo de errores
- [ ] Agregar loading states

### Testing
- [ ] Test: Crear broadcast exitosamente
- [ ] Test: Crear broadcast con broadcastId duplicado → Error 409
- [ ] Test: Crear broadcast sin broadcastId → Auto-generar
- [ ] Test: Listar broadcasts con filtros
- [ ] Test: Actualizar broadcast
- [ ] Test: Eliminar broadcast sin campañas → Éxito
- [ ] Test: Eliminar broadcast con campañas → Error 400
- [ ] Test: SDK usa broadcastId válido → Retorna campañas
- [ ] Test: SDK usa broadcastId inválido → Error 404
- [ ] Test: SDK usa broadcastId terminado → Retorna array vacío

---

## 📝 Notas de Implementación

### Auto-generación de BroadcastId

**Estrategia recomendada:**
```python
def generate_broadcast_id(broadcast_name: str, start_time: datetime, channel_id: int = None) -> str:
    # Opción 1: Usar nombre + fecha
    name_slug = slugify(broadcast_name)  # "Barcelona vs PSG" → "barcelona-vs-psg"
    date_str = start_time.strftime("%Y-%m-%d")  # "2025-01-23"
    base_id = f"{name_slug}-{date_str}"
    
    # Verificar unicidad, agregar sufijo si es necesario
    if broadcast_exists(base_id):
        timestamp = int(start_time.timestamp())
        base_id = f"{name_slug}-{date_str}-{timestamp}"
    
    return base_id
```

### Actualización Automática de Status

**Cron Job recomendado:**
```python
# Ejecutar cada minuto
async def update_broadcast_statuses():
    # Actualizar broadcasts que deberían estar "live"
    await db.execute("""
        UPDATE broadcasts
        SET status = 'live'
        WHERE status = 'upcoming'
          AND start_time <= NOW()
          AND (end_time IS NULL OR end_time >= NOW())
    """)
    
    # Actualizar broadcasts que deberían estar "ended"
    await db.execute("""
        UPDATE broadcasts
        SET status = 'ended'
        WHERE status IN ('upcoming', 'live')
          AND end_time IS NOT NULL
          AND end_time < NOW()
    """)
```

### Validación de BroadcastId en Auto-Discovery

**Código Python ejemplo:**
```python
@router.get("/v1/sdk/campaigns")
async def discover_campaigns(
    apiKey: str = Query(...),
    broadcastId: Optional[str] = None,
    matchId: Optional[str] = None  # Backward compatibility
):
    # Validar API key
    client_app = await validate_api_key(apiKey)
    if not client_app:
        raise HTTPException(401, "Invalid API key")
    
    # Usar broadcastId o matchId (backward compatibility)
    effective_broadcast_id = broadcastId or matchId
    
    # Si se proporciona broadcastId, validar que existe
    if effective_broadcast_id:
        broadcast = await db.get_broadcast(effective_broadcast_id)
        if not broadcast:
            raise HTTPException(
                status_code=404,
                detail=f"Broadcast '{effective_broadcast_id}' not found"
            )
        
        # Si broadcast terminó, retornar array vacío (no error)
        if broadcast.status == "ended":
            return {"campaigns": []}
    
    # Buscar campañas activas
    campaigns = await db.get_active_campaigns(
        broadcast_id=effective_broadcast_id,
        channel_id=client_app.channel_id
    )
    
    return {"campaigns": campaigns}
```

---

## 🎯 Priorización

### Sprint 1 (MVP - Crítico)
1. ✅ Tabla `broadcasts` en base de datos
2. ✅ `POST /v1/broadcasts` - Crear broadcast
3. ✅ `GET /v1/broadcasts/{broadcastId}` - Validar broadcast
4. ✅ Modificar `GET /v1/sdk/campaigns` para validar broadcastId
5. ✅ Página lista de broadcasts (básica)

### Sprint 2 (Importante)
6. ✅ `GET /v1/broadcasts` - Listar con filtros
7. ✅ `PUT /v1/broadcasts/{broadcastId}` - Actualizar
8. ✅ `DELETE /v1/broadcasts/{broadcastId}` - Eliminar
9. ✅ Página crear/editar broadcast
10. ✅ Integración con formulario de campaña

### Sprint 3 (Mejoras)
11. ✅ Auto-generación de broadcastId
12. ✅ Cron job para actualizar status automáticamente
13. ✅ Dashboard UI completo con todas las funcionalidades
14. ✅ Tests completos

---

## 📚 Referencias

- Documentación existente: `BACKEND_CAMPAIGNS_IMPLEMENTATION.md`
- Endpoint actual: `GET /v1/sdk/campaigns` (modificar)
- Tabla existente: `campaigns` (agregar FK)

---

**¡Implementar siguiendo este prompt paso a paso!**
