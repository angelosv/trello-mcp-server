# Comparación: LiveLike vs Reachu - Identificación de Eventos Deportivos

## 📊 Análisis de LiveLike

### Concepto: **Program ID**

LiveLike usa el concepto de **"Program"** para identificar eventos deportivos:

```swift
// LiveLike Approach
let config = SessionConfiguration(programID: "<program-id>")
session = engagementSDK.contentSession(config: config)
widgetViewController.session = session
chatViewController.session = session
```

**Características:**
- **Program ID** es un identificador único para cada evento/programa
- Se crea en el Producer Suite o vía API antes del evento
- El Program ID se almacena en los metadatos del contenido
- Una sesión se inicia con un Program ID específico
- Todos los widgets y chat están asociados a ese Program ID

**Flujo:**
1. Crear Program en Producer Suite → Obtener Program ID
2. Almacenar Program ID en metadatos del contenido
3. Al iniciar reproducción → Crear ContentSession con Program ID
4. Asignar session a WidgetViewController y ChatViewController
5. SDK recibe widgets/chat asociados a ese Program ID

---

## 📊 Análisis de Reachu

### Concepto: **BroadcastContext** + **Campaign ID**

Reachu usa una combinación de **BroadcastContext** y **Campaign ID**:

```swift
// Reachu Approach
let broadcastContext = BroadcastContext(
    broadcastId: "match-123",
    channelId: "channel-456",
    startTime: "2026-02-09T10:00:00Z"
)

CampaignManager.shared.setBroadcastContext(broadcastContext)
EngagementManager.shared.loadEngagement(context: broadcastContext)
```

**Características:**
- **BroadcastContext** contiene: `broadcastId`, `channelId`, `startTime`, `endTime`
- **Campaign ID** se puede obtener vía auto-discovery usando `broadcastId`
- Soporta múltiples campañas activas simultáneamente
- Los engagement (polls/contests) se filtran por `broadcastId`

**Flujo:**
1. Usuario abre video → Se crea BroadcastContext con broadcastId
2. Si auto-discovery está habilitado → Se busca Campaign ID usando broadcastId
3. CampaignManager carga campañas activas para ese broadcastId
4. EngagementManager carga polls/contests filtrados por broadcastId
5. Todo se sincroniza con el tiempo de video

---

## 🔍 Diferencias Clave

| Aspecto | LiveLike | Reachu |
|---------|----------|--------|
| **Identificador Principal** | Program ID (único por evento) | BroadcastContext (broadcastId + channelId) |
| **Creación** | Se crea antes del evento en Producer Suite | Se crea dinámicamente cuando se inicia el video |
| **Auto-discovery** | No (requiere Program ID explícito) | Sí (puede descubrir Campaign ID desde broadcastId) |
| **Múltiples Eventos** | Un Program ID = Un evento | Múltiples campañas pueden estar activas simultáneamente |
| **Sincronización Video** | No mencionado explícitamente | Sí (VideoSyncManager para sincronizar con tiempo de video) |
| **Filtrado** | Por Program ID | Por broadcastId + matchContext (opcional) |

---

## 💡 Ventajas de cada enfoque

### LiveLike (Program ID)
✅ **Simplicidad**: Un solo identificador
✅ **Claridad**: Es explícito qué evento se está reproduciendo
✅ **Control**: El productor controla completamente qué Program ID usar

### Reachu (BroadcastContext + Auto-discovery)
✅ **Flexibilidad**: Auto-discovery permite encontrar campañas automáticamente
✅ **Contexto Rico**: BroadcastContext incluye más información (channelId, tiempos)
✅ **Múltiples Campañas**: Soporta múltiples campañas activas simultáneamente
✅ **Sincronización Video**: Integración explícita con tiempo de video

---

## 🎯 Recomendaciones para Reachu

Basándome en el análisis de LiveLike, aquí hay algunas observaciones:

### Lo que Reachu hace bien:
1. **Auto-discovery**: Permite descubrir campañas automáticamente desde broadcastId
2. **BroadcastContext rico**: Incluye más contexto que solo un ID
3. **Sincronización con video**: VideoSyncManager es una ventaja clara

### Lo que podríamos mejorar (inspirado en LiveLike):
1. **Simplificar la inicialización**: 
   - LiveLike tiene un flujo muy simple: `contentSession(programID)` → asignar a view controllers
   - Reachu podría tener algo similar: `startSession(broadcastContext)` → automáticamente carga todo

2. **Claridad en la API**:
   - LiveLike es muy claro: "necesitas un Program ID"
   - Reachu podría documentar mejor: "necesitas un BroadcastContext con broadcastId"

3. **Session Management**:
   - LiveLike mantiene una referencia explícita a `ContentSession`
   - Reachu podría tener un concepto similar de "Session" que encapsule todo

---

## 📝 Propuesta: Mejorar Reachu inspirado en LiveLike

### Opción 1: Agregar un método simplificado de inicialización

```swift
// Propuesta: Método simplificado similar a LiveLike
let session = ReachuSDK.shared.startSession(
    broadcastId: "match-123",
    channelId: "channel-456"
)

// Automáticamente:
// - Crea BroadcastContext
// - Descubre Campaign ID (si auto-discovery está habilitado)
// - Carga campañas activas
// - Carga engagement (polls/contests)
// - Inicializa VideoSyncManager

widgetViewController.session = session
chatViewController.session = session
```

### Opción 2: Mantener el enfoque actual pero mejorar documentación

El enfoque actual es más flexible, solo necesita mejor documentación:
- Documentar claramente que `broadcastId` es equivalente al "Program ID" de LiveLike
- Explicar el flujo completo de inicialización
- Mostrar ejemplos claros

---

## 🔗 Referencias

- [LiveLike iOS SDK Documentation](https://docs.livelike.com/docs/ios)
- LiveLike usa: `SessionConfiguration(programID: "<program-id>")`
- Reachu usa: `BroadcastContext(broadcastId: "...")` + `CampaignManager.setBroadcastContext()`
