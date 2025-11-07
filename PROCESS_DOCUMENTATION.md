# Proceso de Gestión de Tareas Kotlin SDK con Trello

Este documento explica el proceso completo para crear y gestionar tareas de implementación del SDK Kotlin usando Trello y automatización.

## 📋 Flujo Completo

### 1. Crear Guía de Implementación

Cuando hay nuevas funcionalidades en Swift SDK que necesitan portarse a Kotlin:

1. **Analizar cambios en Swift SDK**
   - Revisar commits recientes en `ReachuSwiftSDK`
   - Identificar nuevas funcionalidades o cambios significativos
   - Documentar cómo funciona en Swift

2. **Crear/Actualizar `KOTLIN_IMPLEMENTATION_GUIDE.md`**
   - Agregar nueva sección con formato:
     ```markdown
     ## X. Nombre de la tarea
     
     ### Cómo funciona en Swift
     [Código y explicación]
     
     ### Qué hacer en Kotlin
     [Pasos específicos]
     
     ### Archivos a revisar
     - `path/to/file.swift` (líneas X-Y)
     
     ### Consideraciones importantes
     [Notas clave]
     ```

### 2. Generar Tarjetas de Trello

Usar el script `generate_trello_cards.py` para crear tarjetas automáticamente:

```bash
cd ~/trello-mcp-server
python3 generate_trello_cards.py
```

El script:
- Lee `KOTLIN_IMPLEMENTATION_GUIDE.md`
- Crea tarjetas en Trello con template mejorado
- Asigna miembros y tags automáticamente
- Establece dependencias entre tareas

### 3. Actualizar Tarjetas Existentes

Si necesitas actualizar tarjetas con nuevo formato o información:

```bash
cd ~/trello-mcp-server
python3 update_cards_template.py
```

## 🔧 Scripts Disponibles

### `generate_trello_cards.py`
Genera nuevas tarjetas desde la guía de implementación.

**Uso:**
```bash
python3 generate_trello_cards.py [--board-id BOARD_ID] [--list-id LIST_ID]
```

**Características:**
- Lee secciones de `KOTLIN_IMPLEMENTATION_GUIDE.md`
- Crea tarjetas con template estructurado
- Asigna estimaciones de tiempo (considerando uso de AI)
- Establece dependencias automáticamente
- Asigna tags apropiados
- Asigna miembros del equipo

### `update_cards_template.py`
Actualiza tarjetas existentes con nuevo formato o información.

**Uso:**
```bash
python3 update_cards_template.py [--card-ids CARD_ID1,CARD_ID2,...]
```

**Características:**
- Actualiza descripciones con template mejorado
- Mantiene información existente
- Agrega criterios de aceptación
- Agrega preguntas frecuentes

### `detect_swift_changes.py`
Detecta cambios recientes en el Swift SDK y sugiere nuevas tareas.

**Uso:**
```bash
# Analizar cambios desde el lunes pasado
python3 detect_swift_changes.py --since "last monday"

# Analizar y agregar a la guía automáticamente
python3 detect_swift_changes.py --since "7 days ago" --add-to-guide

# Analizar y crear tarjetas automáticamente
python3 detect_swift_changes.py --since "last monday" --auto-create

# Solo mostrar sugerencias sin hacer cambios
python3 detect_swift_changes.py --since "last monday" --dry-run
```

**Características:**
- Analiza commits recientes en el repositorio Swift SDK
- Detecta archivos nuevos y modificados
- Analiza complejidad del código
- Sugiere estimaciones de tiempo
- Puede agregar tareas a la guía automáticamente
- Puede crear tarjetas en Trello automáticamente

### `validate_tasks.py`
Valida que las tareas de Trello estén completas y correctas.

**Uso:**
```bash
# Validar todas las tareas
python3 validate_tasks.py

# Validar con salida detallada
python3 validate_tasks.py --verbose

# Validar una tarea específica
python3 validate_tasks.py --task-number 13

# Validar e intentar corregir automáticamente
python3 validate_tasks.py --fix
```

**Características:**
- Valida estructura del template
- Verifica criterios de aceptación
- Valida estimaciones de tiempo
- Verifica tags y miembros asignados
- Valida que archivos referenciados existan
- Verifica que dependencias estén completadas
- Valida que tareas estén en la guía
- Genera reporte de estadísticas

## 📝 Template de Tarjeta

Cada tarjeta sigue este formato:

```markdown
## [Tarea #X] Nombre de la tarea

**⏱️ Estimación:** X-Y horas (con AI)
**📋 Dependencias:** Tareas #Y, #Z
**🏷️ Tags:** Kotlin, Backend, Prioridad

### Contexto
[Por qué es importante]

### Cómo funciona en Swift
[Código Swift relevante]

### Qué hacer en Kotlin
[Pasos específicos]

### Archivos a revisar
- `path/to/file.swift` (líneas X-Y)

### Consideraciones importantes
[Notas clave]

### Criterios de aceptación
- [ ] Código implementado y compilando
- [ ] Tests unitarios pasando
- [ ] Documentación actualizada
- [ ] Revisado por peer
- [ ] Demo funcionando

### Preguntas frecuentes
**Q: ...**
A: ...
```

## 🎯 Estimaciones de Tiempo (con AI)

- **Tareas simples** (estructuras básicas): 1-3 horas
- **Tareas medianas** (lógica de negocio): 2-4 horas
- **Tareas complejas** (WebSocket, UI compleja): 4-6 horas
- **Tareas muy complejas** (integración múltiple): 5-8 horas
- **Tests y documentación**: 4-8 horas

## 🔗 Dependencias Comunes

- **Localización (1-4):** Secuencial, cada una depende de la anterior
- **Campaign Management (5-10):** 
  - 5 es independiente
  - 6-10 dependen de 5
  - 8-9 son WebSocket (dependen de 5,6)
  - 10 depende de 5,6,7
- **Componentes UI (11-19):**
  - Cada componente depende de 5,7,10
  - Estructura → Caching → UI
- **Integración (20-22):** Dependen de localización y componentes
- **Modelos (23-25):** Dependen de componentes
- **Polish (26-30):** Dependen de componentes implementados

## 🏷️ Tags por Tipo

- **Kotlin**: Todas las tareas
- **Backend**: Localización, Campaign Management, Modelos
- **UX/UI**: Componentes UI, Skeletons
- **API**: Fetch de datos, WebSocket
- **Cache**: Persistencia de datos
- **Localización**: Sistema de traducciones
- **WebSocket**: Conexiones en tiempo real
- **Testing**: Tests unitarios
- **Documentación**: Docs
- **Prioridad**: Tareas críticas para el MVP

## 👥 Miembros del Equipo

- **Miguel Angel López Monzón** (@miguelangellopezmonzon)
- **Miguel Angel López Monzón** (@miguelangellopezmonzon2)
- **Angelo** (@angelosv1)

## 📅 Proceso Semanal

### Lunes: Revisar Cambios en Swift SDK

1. Revisar commits del fin de semana
2. Identificar nuevas funcionalidades
3. Actualizar `KOTLIN_IMPLEMENTATION_GUIDE.md`
4. Generar nuevas tarjetas si es necesario

### Durante la Semana: Desarrollo

1. Trabajar en tareas según dependencias
2. Actualizar estado en Trello
3. Marcar criterios de aceptación cuando se completen

### Viernes: Revisión

1. Revisar progreso de la semana
2. Identificar bloqueadores
3. Planificar siguiente semana

## 🚀 Automatización Futura

### Integración con GitHub

- Webhook que crea tarjetas cuando se mergea código Swift
- Sincronización de labels entre GitHub y Trello
- Actualización automática cuando se cierra un PR

### Dashboard de Progreso

- Script que genera reporte de progreso
- Tiempo estimado vs real
- Tareas bloqueadas
- Próximas tareas prioritarias

### Validación Automática

- Script que verifica completitud de tareas
- Valida que dependencias estén completadas
- Verifica que archivos referenciados existan

## 📚 Archivos Clave

- **Guía de Implementación**: `/Users/angelo/ReachuSwiftSDK/KOTLIN_IMPLEMENTATION_GUIDE.md`
- **Scripts**: `~/trello-mcp-server/`
- **Configuración Trello**: `~/trello-mcp-server/.env`
- **Swift SDK**: `/Users/angelo/ReachuSwiftSDK/Sources/`
- **Documentación**: `/Users/angelo/Documents/GitHub/Reachu-documentation-v2/docs/swift-sdk/`

## 💡 Tips para Cursor

Cuando trabajes con este proceso en Cursor:

1. **Lee primero** `KOTLIN_IMPLEMENTATION_GUIDE.md` para entender el contexto
2. **Revisa** el código Swift de referencia antes de implementar
3. **Sigue** el template de tarjeta para mantener consistencia
4. **Actualiza** la guía cuando encuentres información nueva
5. **Usa** los scripts para automatizar tareas repetitivas

## 🔄 Actualización Continua

Este proceso debe evolucionar:

- Agregar nuevas automatizaciones según necesidad
- Mejorar estimaciones basándose en datos reales
- Refinar templates según feedback del equipo
- Documentar lecciones aprendidas

---

**Última actualización:** $(date)
**Mantenido por:** Equipo de Desarrollo Reachu

