# Contexto para Cursor: Proceso de Gestión de Tareas Kotlin SDK

## 🎯 Propósito

Este documento proporciona contexto completo a Cursor sobre cómo gestionar tareas de implementación del SDK Kotlin usando Trello y scripts de automatización.

## 📁 Estructura de Archivos

```
~/trello-mcp-server/
├── PROCESS_DOCUMENTATION.md      # Documentación completa del proceso
├── generate_trello_cards.py      # Script para crear nuevas tarjetas
├── update_cards_template.py     # Script para actualizar tarjetas existentes
├── assign_members_correctly.py  # Script para asignar miembros
└── .env                         # Configuración (TRELLO_API_KEY, TRELLO_TOKEN)

/Users/angelo/ReachuSwiftSDK/
└── KOTLIN_IMPLEMENTATION_GUIDE.md  # Guía principal con todas las tareas
```

## 🔄 Flujo de Trabajo Típico

### Cuando hay nuevos cambios en Swift SDK (ej: lunes)

1. **Analizar cambios:**
   ```bash
   cd /Users/angelo/ReachuSwiftSDK
   git log --since="last monday" --oneline
   ```

2. **Actualizar guía:**
   - Abrir `KOTLIN_IMPLEMENTATION_GUIDE.md`
   - Agregar nuevas secciones con formato estándar
   - Documentar cómo funciona en Swift y qué hacer en Kotlin

3. **Generar tarjetas:**
   ```bash
   cd ~/trello-mcp-server
   python3 generate_trello_cards.py --start-task X --end-task Y
   ```

4. **Verificar en Trello:**
   - Revisar que las tarjetas se crearon correctamente
   - Verificar asignaciones y tags
   - Ajustar estimaciones si es necesario

### Cuando necesitas actualizar tarjetas existentes

```bash
cd ~/trello-mcp-server
python3 update_cards_template.py
```

## 📝 Formato de Tareas en la Guía

Cada tarea en `KOTLIN_IMPLEMENTATION_GUIDE.md` debe seguir este formato:

```markdown
## X. Nombre de la tarea

### Cómo funciona en Swift
[Código Swift y explicación]

### Qué hacer en Kotlin
[Pasos específicos con ejemplos]

### Archivos a revisar
- `path/to/file.swift` (líneas X-Y)

### Consideraciones importantes
[Notas clave]
```

## 🏷️ Sistema de Tags

Los tags se asignan automáticamente según el tipo de tarea:

- **Kotlin**: Todas las tareas
- **Backend**: Localización, Campaign Management, Modelos
- **UX/UI**: Componentes UI
- **API**: Fetch de datos, WebSocket
- **Cache**: Persistencia
- **Localización**: Sistema de traducciones
- **WebSocket**: Conexiones en tiempo real
- **Testing**: Tests unitarios
- **Documentación**: Docs
- **Prioridad**: Tareas críticas

## ⏱️ Estimaciones con AI

Las estimaciones consideran que el desarrollador usa AI (Cursor):

- **Simple** (1-3h): Estructuras básicas, data classes
- **Mediana** (2-4h): Lógica de negocio, integraciones
- **Compleja** (4-6h): WebSocket, UI compleja
- **Muy compleja** (5-8h): Integración múltiple
- **Tests/Docs** (4-8h): Testing y documentación

## 🔗 Dependencias

Las dependencias se establecen automáticamente:

- **Localización (1-4)**: Secuencial
- **Campaign (5-10)**: 5 es base, resto depende de 5
- **Componentes (11-19)**: Dependen de 5,7,10
- **Integración (20-22)**: Dependen de localización + componentes
- **Modelos (23-25)**: Dependen de componentes
- **Polish (26-30)**: Dependen de componentes implementados

## 👥 Miembros del Equipo

Por defecto, todas las tarjetas se asignan a:
- Miguel Angel López Monzón (miguel1)
- Miguel Angel López Monzón (miguel2)
- Angelo (angelo)

## 🛠️ Comandos Útiles

### Crear tarjetas nuevas
```bash
python3 generate_trello_cards.py --start-task 31 --end-task 35
```

### Actualizar tarjetas existentes
```bash
python3 update_cards_template.py
```

### Detectar cambios en Swift SDK
```bash
python3 detect_swift_changes.py --since "last monday" --add-to-guide
```

### Validar tareas
```bash
python3 validate_tasks.py --verbose
```

## 📚 Referencias Clave

- **Swift SDK**: `/Users/angelo/ReachuSwiftSDK/Sources/`
- **Documentación**: `/Users/angelo/Documents/GitHub/Reachu-documentation-v2/docs/swift-sdk/`
- **Demo**: `/Users/angelo/PregancyDemo/PregancyDemo/`
- **Guía**: `/Users/angelo/ReachuSwiftSDK/KOTLIN_IMPLEMENTATION_GUIDE.md`

## 💡 Tips para Cursor

1. **Siempre lee** `KOTLIN_IMPLEMENTATION_GUIDE.md` antes de crear tareas
2. **Revisa** el código Swift de referencia para entender el contexto
3. **Usa** los scripts para automatizar, no hagas cambios manuales
4. **Mantén** el formato consistente en la guía
5. **Actualiza** la guía cuando encuentres información nueva

## 🔄 Actualización Continua

Este proceso debe evolucionar:
- Agregar nuevas automatizaciones según necesidad
- Mejorar estimaciones basándose en datos reales
- Refinar templates según feedback
- Documentar lecciones aprendidas

---

**Para más detalles:** Ver `PROCESS_DOCUMENTATION.md`

