# Análisis: Qué falta en el Backend de Reachu vs LiveLike

## 📊 Comparación: LiveLike vs Reachu

### LiveLike: Program Management

**Enfoque:**
- Los **Programs** se crean **antes** del evento en el Producer Suite (dashboard)
- Cada Program tiene un **Program ID** único
- El Program ID se almacena en los metadatos del contenido (video)
- El SDK solo necesita el Program ID para iniciar una sesión

**Backend de LiveLike:**
1. **Producer Suite (Dashboard)**: UI para crear Programs
2. **API para crear Programs**: Endpoint para crear Programs programáticamente
3. **Program ID**: Se genera automáticamente al crear un Program
4. **Asociación**: Programs se asocian con widgets/chat antes del evento

### Reachu: BroadcastContext + Auto-discovery

**Enfoque actual:**
- Los **BroadcastContext** se crean dinámicamente cuando el usuario reproduce el video
- El `broadcastId` viene del cliente (app)
- El backend descubre campañas usando `broadcastId` (auto-discovery)
- No hay un concepto de "crear broadcast" en el backend

---

## 🔍 Análisis Paso a Paso: Qué Falta

### 1. ❌ **Falta: Sistema de Gestión de Broadcasts (Equivalente a Programs)**

**LiveLike tiene:**
- Dashboard para crear Programs
- API para crear Programs
- Program ID generado automáticamente
- Asociación Programs ↔ Widgets/Chat antes del evento

**Reachu NO tiene:**
- ❌ Dashboard para crear/managear broadcasts
- ❌ API para crear broadcasts
- ❌ Sistema de generación automática de broadcastId
- ❌ Asociación explícita Broadcast ↔ Campaigns antes del evento

**Lo que Reachu tiene:**
- ✅ Auto-discovery de campañas por `broadcastId`
- ✅ `broadcastId` viene del cliente (app)
- ✅ Campañas se asocian con `broadcastId` en el dashboard

**Problema:**
- El `broadcastId` es generado por el cliente (app), no por el backend
- No hay un registro centralizado de broadcasts
- No hay forma de "pre-crear" un broadcast antes del evento
- No hay validación de que un `broadcastId` sea válido

---

### 2. ❌ **Falta: Endpoint para Crear/Registrar Broadcasts**

**LiveLike tiene:**
```
POST /api/programs
{
  "name": "Barcelona vs PSG",
  "startTime": "2025-01-23T20:00:00Z",
  ...
}
Response: {
  "programId": "prog_abc123xyz"
}
```

**Reachu NO tiene:**
- ❌ Endpoint `POST /v1/broadcasts` para crear broadcasts
- ❌ Endpoint `GET /v1/broadcasts` para listar broadcasts
- ❌ Endpoint `GET /v1/broadcasts/{broadcastId}` para obtener detalles
- ❌ Endpoint `PUT /v1/broadcasts/{broadcastId}` para actualizar

**Lo que Reachu tiene:**
- ✅ Auto-discovery de campañas por `broadcastId` (pero no valida que el broadcast exista)
- ✅ El `broadcastId` viene del cliente sin validación

**Problema:**
- No hay forma de registrar un broadcast antes del evento
- No hay validación de que un `broadcastId` sea válido
- No hay metadata centralizada sobre broadcasts

---

### 3. ❌ **Falta: Tabla de Broadcasts en Base de Datos**

**LiveLike tiene:**
- Tabla `programs` con:
  - `program_id` (PK)
  - `name`
  - `start_time`
  - `end_time`
  - `status`
  - `metadata`

**Reachu NO tiene:**
- ❌ Tabla `broadcasts` o similar
- ❌ Registro centralizado de broadcasts
- ❌ Metadata de broadcasts

**Lo que Reachu tiene:**
- ✅ `broadcastId` se almacena en `campaigns.match_id` (pero solo cuando hay campaña)
- ✅ `BroadcastContext` se pasa desde el cliente

**Problema:**
- No hay un registro independiente de broadcasts
- Un broadcast solo "existe" si tiene una campaña asociada
- No hay forma de tener metadata de un broadcast sin campaña

---

### 4. ⚠️ **Parcialmente Implementado: Asociación Broadcast ↔ Campaigns**

**LiveLike tiene:**
- Programs se crean primero
- Widgets/Chat se asocian a Programs
- Relación explícita: Program → Widgets

**Reachu tiene:**
- ✅ Campañas pueden tener `match_id` (broadcastId)
- ✅ Auto-discovery encuentra campañas por `broadcastId`
- ⚠️ Pero no hay validación de que el `broadcastId` exista

**Problema:**
- La asociación es implícita (campaña tiene `match_id`)
- No hay validación de que un `broadcastId` sea válido antes de asociar campañas
- No hay forma de "pre-asociar" campañas a un broadcast antes del evento

---

### 5. ❌ **Falta: Validación de BroadcastId**

**LiveLike tiene:**
- Program ID se valida al crear sesión
- Si Program ID no existe → Error claro

**Reachu NO tiene:**
- ❌ Validación de que `broadcastId` existe
- ❌ Error claro si `broadcastId` no existe
- ❌ Solo retorna campañas vacías si no hay campañas para ese `broadcastId`

**Problema:**
- El SDK puede usar cualquier `broadcastId` sin validación
- No hay forma de saber si un `broadcastId` es válido
- No hay error claro si el broadcast no existe

---

### 6. ⚠️ **Parcialmente Implementado: Metadata de Broadcasts**

**LiveLike tiene:**
- Metadata completa de Programs:
  - Nombre
  - Fechas
  - Estado
  - Información adicional

**Reachu tiene:**
- ✅ `BroadcastContext` incluye: `broadcastId`, `broadcastName`, `startTime`, `channelId`, `metadata`
- ⚠️ Pero esta metadata viene del cliente, no del backend
- ⚠️ No hay forma de almacenar/recuperar metadata del backend

**Problema:**
- La metadata viene del cliente (no confiable)
- No hay fuente de verdad en el backend
- No hay forma de validar/actualizar metadata

---

### 7. ❌ **Falta: Dashboard UI para Broadcasts**

**LiveLike tiene:**
- Producer Suite con UI completa para:
  - Crear Programs
  - Editar Programs
  - Ver lista de Programs
  - Asociar Widgets a Programs

**Reachu NO tiene:**
- ❌ UI para crear/managear broadcasts
- ❌ UI para ver lista de broadcasts
- ❌ UI para asociar campañas a broadcasts

**Lo que Reachu tiene:**
- ✅ UI para crear campañas con `match_id` (pero no valida que el broadcast exista)
- ✅ UI para editar campañas

**Problema:**
- No hay gestión centralizada de broadcasts
- Los broadcasts se crean implícitamente cuando se crea una campaña con `match_id`
- No hay visibilidad de qué broadcasts existen

---

## 📋 Checklist: Qué Implementar

### Fase 1: Backend API (Crítico)

#### 1.1 Endpoints de Broadcasts
- [ ] `POST /v1/broadcasts` - Crear broadcast
- [ ] `GET /v1/broadcasts` - Listar broadcasts
- [ ] `GET /v1/broadcasts/{broadcastId}` - Obtener detalles
- [ ] `PUT /v1/broadcasts/{broadcastId}` - Actualizar broadcast
- [ ] `DELETE /v1/broadcasts/{broadcastId}` - Eliminar broadcast (soft delete)

#### 1.2 Validación en Auto-Discovery
- [ ] Modificar `GET /v1/sdk/campaigns` para validar que `broadcastId` existe
  - Si `broadcastId` no existe → Retornar error 404 con mensaje claro
  - Si `broadcastId` existe pero no tiene campañas → Retornar array vacío (no error)

#### 1.3 Base de Datos
- [ ] Crear tabla `broadcasts` con campos: broadcast_id, broadcast_name, start_time, end_time, channel_id, status, metadata

---

### Fase 2: Dashboard UI (Importante)

#### 2.1 UI para Broadcasts
- [ ] Página "Broadcasts" en dashboard
- [ ] Lista de broadcasts con filtros
- [ ] Formulario para crear broadcast
- [ ] Formulario para editar broadcast
- [ ] Vista de detalles de broadcast

---

## 🎯 Priorización

### 🔴 Crítico (MVP)
1. **Tabla `broadcasts` en base de datos**
2. **Endpoint `POST /v1/broadcasts`** para crear broadcasts
3. **Endpoint `GET /v1/broadcasts/{broadcastId}`** para validar broadcasts
4. **Validación en auto-discovery** para verificar que `broadcastId` existe

### 🟡 Importante (Post-MVP)
5. **Dashboard UI** para gestionar broadcasts
6. **Endpoint `GET /v1/broadcasts`** para listar broadcasts
7. **Endpoint `PUT /v1/broadcasts/{broadcastId}`** para actualizar

---

## 📊 Resumen

### Lo que falta (Crítico):
1. ❌ **Tabla `broadcasts`** en base de datos
2. ❌ **API para crear/gestionar broadcasts**
3. ❌ **Validación de `broadcastId`** en auto-discovery
4. ❌ **Dashboard UI** para broadcasts

### Lo que ya funciona:
1. ✅ Auto-discovery de campañas por `broadcastId`
2. ✅ Asociación campañas ↔ `broadcastId` (via `match_id`)
3. ✅ `BroadcastContext` con metadata completa

### Beneficios de implementar:
1. ✅ Validación de broadcasts antes del evento
2. ✅ Registro centralizado de broadcasts
3. ✅ Mejor gestión y visibilidad
4. ✅ Equivalente funcional a LiveLike's Programs
