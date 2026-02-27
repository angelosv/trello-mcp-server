# Análisis: Cómo LiveLike identifica eventos deportivos

## 🎯 Enfoque de LiveLike

### Concepto: **Program ID**

LiveLike usa un concepto muy simple y directo:

```swift
// 1. Crear sesión con Program ID
let config = SessionConfiguration(programID: "<program-id>")
session = engagementSDK.contentSession(config: config)

// 2. Asignar sesión a los view controllers
widgetViewController.session = session
chatViewController.session = session
```

**Características clave:**
- **Program ID** es el identificador único del evento deportivo
- Se crea **antes** del evento en el Producer Suite o vía API
- El Program ID se almacena en los **metadatos del contenido** (video)
- Cuando el usuario reproduce el video, se extrae el Program ID de los metadatos
- Una sesión se inicia con ese Program ID específico
- Todos los widgets y chat están asociados a ese Program ID

**Flujo completo:**
1. **Pre-evento**: Productor crea Program en Producer Suite → Obtiene Program ID
2. **Configuración**: Program ID se almacena en metadatos del contenido (ej: en el sistema de video)
3. **Reproducción**: Usuario abre video → App extrae Program ID de metadatos
4. **Inicialización**: App crea `ContentSession` con Program ID
5. **Asignación**: Session se asigna a `WidgetViewController` y `ChatViewController`
6. **Recepción**: SDK recibe widgets/chat asociados a ese Program ID automáticamente

---

## 🎯 Enfoque de Reachu

### Concepto: **BroadcastContext** + **Auto-discovery**

Reachu usa un enfoque más flexible:

```swift
// 1. Crear BroadcastContext con broadcastId
let broadcastContext = BroadcastContext(
    broadcastId: "barcelona-psg-2025-01-23",
    channelId: 123,
    startTime: "2025-01-23T20:00:00Z"
)

// 2. Establecer contexto en CampaignManager
await CampaignManager.shared.setBroadcastContext(broadcastContext)

// 3. Si auto-discovery está habilitado, descubre Campaign ID automáticamente
// 4. Carga engagement asociado al broadcastId
EngagementManager.shared.loadEngagement(context: broadcastContext)
```

**Características clave:**
- **BroadcastContext** contiene: `broadcastId`, `channelId`, `startTime`, `endTime`, `metadata`
- **Auto-discovery**: Puede descubrir Campaign ID automáticamente usando `broadcastId`
- **Múltiples campañas**: Soporta múltiples campañas activas simultáneamente
- **Filtrado**: Los engagement (polls/contests) se filtran por `broadcastId`
- **Sincronización**: VideoSyncManager sincroniza con tiempo de video

**Flujo completo:**
1. **Reproducción**: Usuario abre video → App crea BroadcastContext con broadcastId
2. **Establecer contexto**: `CampaignManager.setBroadcastContext(broadcastContext)`
3. **Auto-discovery** (si está habilitado):
   - Llama a `/v1/sdk/campaigns?broadcastId=...`
   - Descubre Campaign IDs asociados a ese broadcastId
   - Carga campañas activas
4. **Filtrado**: Filtra componentes por broadcastId
5. **Engagement**: `EngagementManager.loadEngagement()` carga polls/contests para ese broadcastId
6. **Sincronización**: VideoSyncManager sincroniza engagement con tiempo de video

---

## 📊 Comparación Detallada

| Aspecto | LiveLike | Reachu |
|---------|----------|--------|
| **Identificador Principal** | Program ID (string único) | BroadcastContext (estructura con broadcastId + más info) |
| **Cuándo se crea** | Antes del evento (Producer Suite) | Dinámicamente cuando se reproduce el video |
| **Dónde se almacena** | Metadatos del contenido | Se pasa directamente al SDK |
| **Auto-discovery** | ❌ No (requiere Program ID explícito) | ✅ Sí (descubre Campaign ID desde broadcastId) |
| **Múltiples Eventos** | Un Program ID = Un evento | Múltiples campañas pueden estar activas simultáneamente |
| **Sincronización Video** | No mencionado explícitamente | ✅ Sí (VideoSyncManager) |
| **Filtrado Contextual** | Por Program ID | Por broadcastId + matchContext (opcional) |
| **Información Adicional** | Solo Program ID | broadcastId, channelId, startTime, endTime, metadata |
| **Simplicidad** | ⭐⭐⭐⭐⭐ Muy simple | ⭐⭐⭐⭐ Flexible pero más complejo |

---

## 💡 Ventajas de cada enfoque

### LiveLike (Program ID)
✅ **Simplicidad máxima**: Un solo identificador, muy fácil de entender
✅ **Claridad**: Es explícito qué evento se está reproduciendo
✅ **Control total**: El productor controla completamente qué Program ID usar
✅ **API limpia**: `contentSession(programID)` es muy directo

### Reachu (BroadcastContext + Auto-discovery)
✅ **Flexibilidad**: Auto-discovery permite encontrar campañas automáticamente
✅ **Contexto rico**: BroadcastContext incluye más información útil
✅ **Múltiples campañas**: Soporta múltiples campañas activas simultáneamente
✅ **Sincronización video**: Integración explícita con tiempo de video
✅ **Menos configuración**: No necesita crear Program antes del evento

---

## 🔍 Observaciones Clave

### Lo que LiveLike hace bien:
1. **Simplicidad**: El concepto de "Program ID" es muy claro
2. **API limpia**: `SessionConfiguration(programID:)` es intuitivo
3. **Documentación clara**: Explica exactamente qué necesitas (Program ID)

### Lo que Reachu hace mejor:
1. **Auto-discovery**: No necesitas crear nada antes del evento
2. **Contexto rico**: Más información disponible para filtrado y lógica
3. **Sincronización video**: Integración explícita con tiempo de video
4. **Múltiples campañas**: Soporta escenarios más complejos

---

## 🎯 Recomendaciones para Reachu

Basándome en el análisis de LiveLike, aquí hay algunas mejoras que podríamos considerar:

### 1. Simplificar la API (inspirado en LiveLike)

**Opción A: Agregar método simplificado**
```swift
// Propuesta: Método simplificado similar a LiveLike
let session = ReachuSDK.shared.startSession(
    broadcastId: "match-123",
    channelId: "channel-456"
)

// Internamente hace:
// - Crea BroadcastContext
// - Llama setBroadcastContext()
// - Descubre Campaign ID (si auto-discovery está habilitado)
// - Carga campañas activas
// - Carga engagement
// - Inicializa VideoSyncManager

widgetViewController.session = session
chatViewController.session = session
```

**Opción B: Mantener enfoque actual pero mejorar documentación**
- Documentar claramente que `broadcastId` es equivalente al "Program ID" de LiveLike
- Explicar el flujo completo de inicialización
- Mostrar ejemplos claros comparados con LiveLike

### 2. Mejorar la documentación

Crear una guía que explique:
- **Para desarrolladores**: "broadcastId es como el Program ID de LiveLike"
- **Flujo completo**: Desde que el usuario abre el video hasta que recibe widgets
- **Ejemplos prácticos**: Cómo obtener broadcastId de metadatos del video

### 3. Concepto de "Session" explícito

Podríamos agregar un concepto de "Session" similar a LiveLike que encapsule:
- BroadcastContext
- CampaignManager state
- EngagementManager state
- VideoSyncManager state

Esto haría la API más similar a LiveLike y más fácil de entender.

---

## 📝 Conclusión

**LiveLike** usa un enfoque más simple y directo con **Program ID**, mientras que **Reachu** usa un enfoque más flexible con **BroadcastContext** y **auto-discovery**.

**Reachu tiene ventajas**:
- Auto-discovery elimina la necesidad de crear Programs antes del evento
- Contexto más rico permite filtrado más sofisticado
- Sincronización explícita con video

**Pero LiveLike tiene ventajas**:
- API más simple y clara
- Concepto más fácil de entender
- Documentación más directa

**Recomendación**: Mantener el enfoque flexible de Reachu pero agregar una capa de simplificación opcional similar a LiveLike para desarrolladores que prefieren simplicidad.
