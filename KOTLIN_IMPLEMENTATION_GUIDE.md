# Guía de Implementación Kotlin SDK - Tareas Detalladas

Este documento explica en detalle cada tarea para implementar las funcionalidades del SDK Swift en Kotlin. Para cada tarea se incluye:
- Cómo funciona actualmente en Swift
- Qué debe implementarse en Kotlin
- Referencias a código específico
- Ejemplos y consideraciones importantes

---

## 1. Crear estructura base de localización (ReachuLocalization singleton, LocalizationConfiguration)

### Cómo funciona en Swift

En Swift, `ReachuLocalization` es una clase singleton que gestiona todas las traducciones del SDK:

```swift
// Sources/ReachuCore/Configuration/ReachuLocalization.swift
public class ReachuLocalization {
    public static let shared = ReachuLocalization()
    
    private var configuration: LocalizationConfiguration = .default
    private var currentLanguage: String = "en"
    
    public func configure(_ config: LocalizationConfiguration) {
        self.configuration = config
        self.currentLanguage = config.defaultLanguage
    }
    
    public func setLanguage(_ language: String) {
        self.currentLanguage = language
    }
    
    public func string(for key: String, language: String? = nil, defaultValue: String? = nil) -> String {
        // Intenta obtener traducción del idioma solicitado
        // Si no existe, usa defaultLanguage
        // Si tampoco existe, usa fallbackLanguage
        // Si tampoco existe, usa defaultValue o la key misma
    }
}
```

La configuración se almacena en `LocalizationConfiguration`:

```swift
public struct LocalizationConfiguration {
    public let defaultLanguage: String
    public let translations: [String: [String: String]]  // language -> key -> translation
    public let fallbackLanguage: String
}
```

### Qué hacer en Kotlin

1. **Crear `ReachuLocalization` como object singleton:**
   ```kotlin
   object ReachuLocalization {
       private var configuration: LocalizationConfiguration = LocalizationConfiguration.default
       private var currentLanguage: String = "en"
       
       fun configure(config: LocalizationConfiguration) {
           this.configuration = config
           this.currentLanguage = config.defaultLanguage
       }
       
       fun setLanguage(language: String) {
           this.currentLanguage = language
       }
       
       fun string(key: String, language: String? = null, defaultValue: String? = null): String {
           // Misma lógica de fallback que en Swift
       }
   }
   ```

2. **Crear data class `LocalizationConfiguration`:**
   ```kotlin
   data class LocalizationConfiguration(
       val defaultLanguage: String = "en",
       val translations: Map<String, Map<String, String>> = emptyMap(),
       val fallbackLanguage: String = "en"
   ) {
       companion object {
           val default = LocalizationConfiguration()
       }
   }
   ```

3. **Crear función helper top-level:**
   ```kotlin
   fun rLocalizedString(key: String, defaultValue: String? = null): String {
       return ReachuLocalization.string(key, defaultValue = defaultValue)
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuCore/Configuration/ReachuLocalization.swift` (líneas 1-87)
- `Sources/ReachuCore/Configuration/LocalizationConfiguration.swift` (líneas 1-62)

**Consideraciones importantes:**
- El singleton debe ser thread-safe en Kotlin (object ya lo es)
- La función `string()` debe manejar el mismo orden de fallback que Swift
- El formato de traducciones es: `Map<LanguageCode, Map<TranslationKey, TranslationValue>>`

---

## 2. Crear enum ReachuTranslationKey con todas las claves y traducciones por defecto en inglés

### Cómo funciona en Swift

Swift usa un enum con todas las claves de traducción y un diccionario estático con las traducciones por defecto:

```swift
// Sources/ReachuCore/Configuration/ReachuTranslationKey.swift
public enum ReachuTranslationKey: String, CaseIterable {
    // Common
    case addToCart = "common.addToCart"
    case remove = "common.remove"
    case close = "common.close"
    // ... más casos
    
    // Cart
    case cart = "cart.title"
    case cartEmpty = "cart.empty"
    // ... más casos
    
    // Default English Values
    public static let defaultEnglish: [String: String] = [
        "common.addToCart": "Add to Cart",
        "common.remove": "Remove",
        "cart.title": "Cart",
        // ... ~130+ traducciones más
    ]
}
```

### Qué hacer en Kotlin

1. **Crear sealed class o enum class con todas las claves:**
   ```kotlin
   enum class ReachuTranslationKey(val key: String) {
       // Common
       ADD_TO_CART("common.addToCart"),
       REMOVE("common.remove"),
       CLOSE("common.close"),
       // ... más casos
       
       // Cart
       CART("cart.title"),
       CART_EMPTY("cart.empty"),
       // ... más casos
   }
   ```

2. **Crear objeto companion con traducciones por defecto:**
   ```kotlin
   companion object {
       val defaultEnglish: Map<String, String> = mapOf(
           "common.addToCart" to "Add to Cart",
           "common.remove" to "Remove",
           "cart.title" to "Cart",
           // ... todas las ~130+ traducciones
       )
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuCore/Configuration/ReachuTranslationKey.swift` (líneas 1-261)
- Todas las claves están documentadas en: `docs/swift-sdk/localization.mdx` (líneas 133-295)

**Consideraciones importantes:**
- Debe incluir TODAS las categorías: Common, Cart, Checkout, Address, Payment, Product, Order, Shipping, Discount, Validation, Errors
- Total aproximado: ~130+ claves de traducción
- Las traducciones por defecto están hardcodeadas en líneas 134-259 del archivo Swift
- El formato de clave es siempre `"category.key"` (ej: `"cart.title"`, `"checkout.proceed"`)

---

## 3. Implementar carga de traducciones desde archivo JSON externo (reachu-translations.json)

### Cómo funciona en Swift

Swift carga traducciones desde un archivo JSON en el bundle de la app:

```swift
// Sources/ReachuCore/Configuration/ConfigurationLoader.swift (líneas 640-674)
private static func loadTranslationsFromFile(_ fileName: String, bundle: Bundle = .main) -> [String: [String: String]]? {
    guard let path = bundle.path(forResource: fileName, ofType: "json"),
          let data = FileManager.default.contents(atPath: path) else {
        return nil
    }
    
    let decoder = JSONDecoder()
    
    // Formato 1: { "translations": { "en": {...}, "es": {...} } }
    if let wrapper = try? decoder.decode(TranslationsFileWrapper.self, from: data) {
        return wrapper.translations
    }
    
    // Formato 2: Direct { "en": {...}, "es": {...} }
    if let directTranslations = try? decoder.decode([String: [String: String]].self, from: data) {
        return directTranslations
    }
    
    return nil
}
```

El archivo puede tener dos formatos:
```json
// Formato 1
{
  "translations": {
    "en": { "cart.title": "Cart", ... },
    "es": { "cart.title": "Carrito", ... }
  }
}

// Formato 2
{
  "en": { "cart.title": "Cart", ... },
  "es": { "cart.title": "Carrito", ... }
}
```

### Qué hacer en Kotlin

1. **Crear función para cargar desde assets/resources:**
   ```kotlin
   fun loadTranslationsFromFile(context: Context, fileName: String): Map<String, Map<String, String>>? {
       return try {
           val inputStream = context.assets.open("$fileName.json")
           val jsonString = inputStream.bufferedReader().use { it.readText() }
           val json = JSONObject(jsonString)
           
           // Intentar Formato 1: { "translations": { ... } }
           if (json.has("translations")) {
               val translationsObj = json.getJSONObject("translations")
               parseTranslationsObject(translationsObj)
           } else {
               // Formato 2: Direct { "en": {...}, "es": {...} }
               parseTranslationsObject(json)
           }
       } catch (e: Exception) {
           ReachuLogger.error("Failed to load translations file: $fileName", e)
           null
       }
   }
   
   private fun parseTranslationsObject(obj: JSONObject): Map<String, Map<String, String>> {
       val result = mutableMapOf<String, Map<String, String>>()
       val keys = obj.keys()
       while (keys.hasNext()) {
           val lang = keys.next()
           val langObj = obj.getJSONObject(lang)
           val translations = mutableMapOf<String, String>()
           val langKeys = langObj.keys()
           while (langKeys.hasNext()) {
               val key = langKeys.next()
               translations[key] = langObj.getString(key)
           }
           result[lang] = translations
       }
       return result
   }
   ```

2. **Integrar en ConfigurationLoader:**
   - Cuando se carga la configuración, si existe `translationsFile`, llamar a esta función
   - Mergear las traducciones: archivo externo tiene prioridad sobre inline

**Archivos a revisar:**
- `Sources/ReachuCore/Configuration/ConfigurationLoader.swift` (líneas 640-674)
- Demo: `PregancyDemo/PregancyDemo/Configuration/reachu-translations.json` muestra el formato

**Consideraciones importantes:**
- El archivo debe estar en `res/raw/reachu-translations.json` o `assets/reachu-translations.json`
- Debe manejar ambos formatos de JSON
- El merge debe dar prioridad al archivo externo sobre traducciones inline
- Manejar errores gracefully (si el archivo no existe, usar traducciones inline o default)

---

## 4. Integrar sistema de localización en ConfigurationLoader para cargar desde reachu-config.json

### Cómo funciona en Swift

El `ConfigurationLoader` lee la sección `localization` del JSON de configuración:

```swift
// Sources/ReachuCore/Configuration/ConfigurationLoader.swift (líneas 576-622)
private static func createLocalizationConfiguration(from localizationConfig: JSONLocalizationConfiguration?, bundle: Bundle = .main) -> LocalizationConfiguration {
    guard let config = localizationConfig else { 
        return .default
    }
    
    var translations = config.translations ?? [:]
    
    // Si hay un archivo externo de traducciones, cargarlo
    if let translationsFile = config.translationsFile {
        if let externalTranslations = loadTranslationsFromFile(translationsFile, bundle: bundle) {
            // Merge: las traducciones del archivo externo tienen prioridad
            for (language, langTranslations) in externalTranslations {
                if translations[language] == nil {
                    translations[language] = [:]
                }
                translations[language]?.merge(langTranslations) { (_, new) in new }
            }
        }
    }
    
    // Si no hay traducciones, usar default English
    if translations.isEmpty {
        return LocalizationConfiguration(
            defaultLanguage: config.defaultLanguage ?? "en",
            translations: ["en": ReachuTranslationKey.defaultEnglish],
            fallbackLanguage: config.fallbackLanguage ?? "en"
        )
    }
    
    return LocalizationConfiguration(
        defaultLanguage: config.defaultLanguage ?? "en",
        translations: translations,
        fallbackLanguage: config.fallbackLanguage ?? "en"
    )
}
```

También detecta automáticamente el idioma desde el country code:
```swift
private static func languageCodeForCountry(_ countryCode: String?) -> String {
    let countryToLanguage: [String: String] = [
        "DE": "de", "AT": "de", "CH": "de",
        "US": "en", "GB": "en", "CA": "en",
        "NO": "no", "SE": "sv", "DK": "da",
        "ES": "es", "FR": "fr", "IT": "it",
        // ... más mapeos
    ]
    return countryToLanguage[countryCode?.uppercased() ?? ""] ?? "en"
}
```

### Qué hacer en Kotlin

1. **En ConfigurationLoader, leer sección `localization`:**
   ```kotlin
   data class JSONLocalizationConfiguration(
       val defaultLanguage: String? = null,
       val fallbackLanguage: String? = null,
       val translationsFile: String? = null,
       val translations: Map<String, Map<String, String>>? = null
   )
   
   private fun createLocalizationConfiguration(
       config: JSONLocalizationConfiguration?,
       context: Context
   ): LocalizationConfiguration {
       if (config == null) return LocalizationConfiguration.default
       
       var translations = config.translations ?: emptyMap()
       
       // Cargar desde archivo externo si existe
       if (config.translationsFile != null) {
           val externalTranslations = loadTranslationsFromFile(context, config.translationsFile)
           if (externalTranslations != null) {
               // Merge: archivo externo tiene prioridad
               translations = mergeTranslations(translations, externalTranslations)
           }
       }
       
       // Si no hay traducciones, usar default English
       if (translations.isEmpty()) {
           return LocalizationConfiguration(
               defaultLanguage = config.defaultLanguage ?: "en",
               translations = mapOf("en" to ReachuTranslationKey.defaultEnglish),
               fallbackLanguage = config.fallbackLanguage ?: "en"
           )
       }
       
       return LocalizationConfiguration(
           defaultLanguage = config.defaultLanguage ?: "en",
           translations = translations,
           fallbackLanguage = config.fallbackLanguage ?: "en"
       )
   }
   ```

2. **Implementar auto-detección de idioma desde country code:**
   ```kotlin
   private fun languageCodeForCountry(countryCode: String?): String {
       val countryToLanguage = mapOf(
           "DE" to "de", "AT" to "de", "CH" to "de",
           "US" to "en", "GB" to "en", "CA" to "en",
           "NO" to "no", "SE" to "sv", "DK" to "da",
           "ES" to "es", "FR" to "fr", "IT" to "it",
           // ... más mapeos
       )
       return countryToLanguage[countryCode?.uppercase()] ?: "en"
   }
   ```

3. **Configurar ReachuLocalization después de cargar:**
   ```kotlin
   val localizationConfig = createLocalizationConfiguration(jsonConfig.localization, context)
   ReachuLocalization.configure(localizationConfig)
   ```

**Archivos a revisar:**
- `Sources/ReachuCore/Configuration/ConfigurationLoader.swift` (líneas 576-622)
- Demo: `PregancyDemo/PregancyDemo/Configuration/reachu-config.json` (líneas 100-104)

**Consideraciones importantes:**
- El merge debe dar prioridad al archivo externo sobre traducciones inline
- Si no hay traducciones, siempre usar `ReachuTranslationKey.defaultEnglish` como fallback
- Auto-detectar idioma desde country code si no se especifica explícitamente
- Configurar `ReachuLocalization.shared` inmediatamente después de cargar la configuración

---

## 5. Crear CampaignManager singleton con propiedades observables y estados de campaña

### Cómo funciona en Swift

`CampaignManager` es una clase singleton con propiedades `@Published` que se observan automáticamente:

```swift
// Sources/ReachuCore/Managers/CampaignManager.swift (líneas 1-91)
@MainActor
public class CampaignManager: ObservableObject {
    public static let shared = CampaignManager()
    
    @Published public private(set) var isCampaignActive: Bool = true
    @Published public private(set) var campaignState: CampaignState = .active
    @Published public private(set) var activeComponents: [Component] = []
    @Published public private(set) var isConnected: Bool = false
    @Published public private(set) var currentCampaign: Campaign?
    
    private var campaignId: Int?
    private var webSocketManager: CampaignWebSocketManager?
    
    private init() {
        let configuredCampaignId = ReachuConfiguration.shared.liveShowConfiguration.campaignId
        
        if configuredCampaignId > 0 {
            self.campaignId = configuredCampaignId
            Task {
                await initializeCampaign()
            }
        } else {
            // No campaign configured - SDK works normally
            self.isCampaignActive = true
            self.campaignState = .active
        }
    }
    
    public func reinitialize() {
        // Re-inicializar cuando cambia configuración
    }
}
```

Los componentes UI observan estos cambios automáticamente:
```swift
@ObservedObject private var campaignManager = CampaignManager.shared
```

### Qué hacer en Kotlin

1. **Crear object singleton con StateFlow observables:**
   ```kotlin
   object CampaignManager {
       private val _isCampaignActive = MutableStateFlow(true)
       val isCampaignActive: StateFlow<Boolean> = _isCampaignActive.asStateFlow()
       
       private val _campaignState = MutableStateFlow(CampaignState.Active)
       val campaignState: StateFlow<CampaignState> = _campaignState.asStateFlow()
       
       private val _activeComponents = MutableStateFlow<List<Component>>(emptyList())
       val activeComponents: StateFlow<List<Component>> = _activeComponents.asStateFlow()
       
       private val _isConnected = MutableStateFlow(false)
       val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()
       
       private val _currentCampaign = MutableStateFlow<Campaign?>(null)
       val currentCampaign: StateFlow<Campaign?> = _currentCampaign.asStateFlow()
       
       private var campaignId: Int? = null
       private var webSocketManager: CampaignWebSocketManager? = null
       
       init {
           val configuredCampaignId = ReachuConfiguration.shared.liveShowConfiguration.campaignId
           
           if (configuredCampaignId > 0) {
               this.campaignId = configuredCampaignId
               CoroutineScope(Dispatchers.Main).launch {
                   initializeCampaign()
               }
           } else {
               // No campaign configured - SDK works normally
               _isCampaignActive.value = true
               _campaignState.value = CampaignState.Active
           }
       }
       
       fun reinitialize() {
           // Re-inicializar cuando cambia configuración
       }
   }
   ```

2. **Crear enum CampaignState:**
   ```kotlin
   enum class CampaignState {
       Upcoming,
       Active,
       Ended
   }
   ```

3. **En Compose, observar los StateFlows:**
   ```kotlin
   @Composable
   fun MyComponent() {
       val isCampaignActive by CampaignManager.isCampaignActive.collectAsState()
       val campaignState by CampaignManager.campaignState.collectAsState()
       // ...
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuCore/Managers/CampaignManager.swift` (líneas 1-91)
- Demo: `PregancyDemo/PregancyDemo/MainTabView.swift` (línea 120) muestra uso

**Consideraciones importantes:**
- Debe ser thread-safe (usar Dispatchers.Main para actualizaciones)
- Si `campaignId == 0` o no está configurado, el SDK funciona normalmente sin restricciones
- Las propiedades deben ser inmutables desde fuera (usar `private(set)` equivalente)
- `reinitialize()` debe desconectar conexiones existentes y reinicializar todo

---

## 6. Implementar fetch de información de campaña desde REST API (/api/campaigns/{id})

### Cómo funciona en Swift

El CampaignManager hace una petición HTTP GET para obtener información de la campaña:

```swift
// Sources/ReachuCore/Managers/CampaignManager.swift (líneas 213-311)
private func fetchCampaignInfo(campaignId: Int) async -> Campaign? {
    let baseURL = campaignRestAPIBaseURL
    let urlString = "\(baseURL)/api/campaigns/\(campaignId)"
    
    guard let url = URL(string: urlString) else {
        ReachuLogger.error("Invalid campaign API URL: \(urlString)")
        return nil
    }
    
    do {
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            return nil
        }
        
        if httpResponse.statusCode == 404 {
            // Campaign not found - SDK works normally
            ReachuLogger.warning("Campaign \(campaignId) not found")
            return nil
        }
        
        guard httpResponse.statusCode == 200 else {
            ReachuLogger.error("Campaign info request failed with status \(httpResponse.statusCode)")
            return nil
        }
        
        let decoder = JSONDecoder()
        let campaignResponse = try decoder.decode(CampaignResponse.self, from: data)
        
        // Determinar estado basado en fechas
        let now = Date()
        let startDate = campaignResponse.startDate
        let endDate = campaignResponse.endDate
        
        if campaignResponse.isPaused {
            campaignState = .active  // Pero isCampaignActive = false
            isCampaignActive = false
        } else if now < startDate {
            campaignState = .upcoming
            isCampaignActive = false
        } else if endDate != nil && now >= endDate {
            campaignState = .ended
            isCampaignActive = false
        } else {
            campaignState = .active
            isCampaignActive = true
        }
        
        return Campaign(
            id: campaignResponse.id,
            startDate: startDate,
            endDate: endDate,
            isPaused: campaignResponse.isPaused
        )
    } catch {
        ReachuLogger.warning("Failed to fetch campaign info: \(error)")
        return nil
    }
}
```

### Qué hacer en Kotlin

1. **Crear función suspend para fetch:**
   ```kotlin
   private suspend fun fetchCampaignInfo(campaignId: Int): Campaign? {
       val baseURL = ReachuConfiguration.shared.campaignConfiguration.restAPIBaseURL
       val url = "$baseURL/api/campaigns/$campaignId"
       
       return try {
           val response = httpClient.get(url) {
               headers {
                   append("Accept", "application/json")
               }
           }
           
           when (response.status.value) {
               404 -> {
                   // Campaign not found - SDK works normally
                   ReachuLogger.warning("Campaign $campaignId not found")
                   null
               }
               200 -> {
                   val campaignResponse = response.body<CampaignResponse>()
                   
                   // Determinar estado basado en fechas
                   val now = Instant.now()
                   val startDate = Instant.parse(campaignResponse.startDate)
                   val endDate = campaignResponse.endDate?.let { Instant.parse(it) }
                   
                   val state: CampaignState
                   val isActive: Boolean
                   
                   if (campaignResponse.isPaused) {
                       state = CampaignState.Active
                       isActive = false
                   } else if (now < startDate) {
                       state = CampaignState.Upcoming
                       isActive = false
                   } else if (endDate != null && now >= endDate) {
                       state = CampaignState.Ended
                       isActive = false
                   } else {
                       state = CampaignState.Active
                       isActive = true
                   }
                   
                   withContext(Dispatchers.Main) {
                       _campaignState.value = state
                       _isCampaignActive.value = isActive
                   }
                   
                   Campaign(
                       id = campaignResponse.id,
                       startDate = campaignResponse.startDate,
                       endDate = campaignResponse.endDate,
                       isPaused = campaignResponse.isPaused
                   )
               }
               else -> {
                   ReachuLogger.error("Campaign info request failed with status ${response.status.value}")
                   null
               }
           }
       } catch (e: Exception) {
           ReachuLogger.warning("Failed to fetch campaign info: ${e.message}")
           null
       }
   }
   ```

2. **Crear data class Campaign:**
   ```kotlin
   data class Campaign(
       val id: Int,
       val startDate: String,  // ISO 8601
       val endDate: String?,   // ISO 8601, nullable
       val isPaused: Boolean
   )
   ```

3. **Crear data class CampaignResponse para parsing:**
   ```kotlin
   @Serializable
   data class CampaignResponse(
       val id: Int,
       val startDate: String,
       val endDate: String?,
       val isPaused: Boolean
   )
   ```

**Archivos a revisar:**
- `Sources/ReachuCore/Managers/CampaignManager.swift` (líneas 213-311)
- El endpoint viene de `ReachuConfiguration.shared.campaignConfiguration.restAPIBaseURL`

**Consideraciones importantes:**
- Manejar 404 gracefully (campaña no existe, SDK funciona normalmente)
- Determinar estado basado en fechas: `now < startDate` → Upcoming, `startDate <= now < endDate` → Active, `now >= endDate` → Ended
- Si `isPaused == true`, estado es Active pero `isCampaignActive = false`
- Actualizar StateFlows en Dispatchers.Main
- Manejar errores de red gracefully

---

## 7. Implementar fetch de componentes activos desde REST API (/api/campaigns/{id}/components)

### Cómo funciona en Swift

Después de obtener la información de la campaña, se fetchean los componentes activos:

```swift
// Sources/ReachuCore/Managers/CampaignManager.swift (líneas 313-420)
private func fetchActiveComponents(campaignId: Int) async {
    let baseURL = campaignRestAPIBaseURL
    let urlString = "\(baseURL)/api/campaigns/\(campaignId)/components"
    
    guard let url = URL(string: urlString) else {
        ReachuLogger.error("Invalid components API URL")
        return
    }
    
    do {
        let (data, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            return
        }
        
        if httpResponse.statusCode == 404 {
            // No components endpoint - campaign may not have components
            ReachuLogger.info("No components endpoint found")
            return
        }
        
        guard httpResponse.statusCode == 200 else {
            ReachuLogger.error("Components request failed with status \(httpResponse.statusCode)")
            return
        }
        
        let decoder = JSONDecoder()
        let responses = try decoder.decode([ComponentResponse].self, from: data)
        
        // Filtrar solo componentes activos
        let activeComponents = responses
            .filter { $0.status == "active" }
            .compactMap { try? $0.toComponent() }
        
        await MainActor.run {
            self.activeComponents = activeComponents
            CacheManager.shared.saveComponents(activeComponents)
        }
    } catch {
        ReachuLogger.error("Failed to fetch components: \(error)")
    }
}
```

Cada `ComponentResponse` se convierte a `Component` según su tipo:
```swift
struct ComponentResponse: Codable {
    let componentId: String
    let type: String
    let status: String
    let config: JSONValue  // Dynamic JSON
}

extension ComponentResponse {
    func toComponent() throws -> Component {
        switch type {
        case "product_banner":
            let config = try JSONDecoder().decode(ProductBannerConfig.self, from: configData)
            return Component.productBanner(id: componentId, type: type, isActive: status == "active", config: config)
        case "product_carousel":
            // Similar para otros tipos
        // ...
        }
    }
}
```

### Qué hacer en Kotlin

1. **Crear función suspend para fetch:**
   ```kotlin
   private suspend fun fetchActiveComponents(campaignId: Int) {
       val baseURL = ReachuConfiguration.shared.campaignConfiguration.restAPIBaseURL
       val url = "$baseURL/api/campaigns/$campaignId/components"
       
       try {
           val response = httpClient.get(url) {
               headers {
                   append("Accept", "application/json")
               }
           }
           
           when (response.status.value) {
               404 -> {
                   // No components endpoint - campaign may not have components
                   ReachuLogger.info("No components endpoint found")
                   return
               }
               200 -> {
                   val componentResponses = response.body<List<ComponentResponse>>()
                   
                   // Filtrar solo componentes activos y convertir
                   val activeComponents = componentResponses
                       .filter { it.status == "active" }
                       .mapNotNull { it.toComponent() }
                   
                   withContext(Dispatchers.Main) {
                       _activeComponents.value = activeComponents
                       CacheManager.saveComponents(activeComponents)
                   }
               }
               else -> {
                   ReachuLogger.error("Components request failed with status ${response.status.value}")
               }
           }
       } catch (e: Exception) {
           ReachuLogger.error("Failed to fetch components: ${e.message}")
       }
   }
   ```

2. **Crear data class ComponentResponse:**
   ```kotlin
   @Serializable
   data class ComponentResponse(
       val componentId: String,
       val type: String,
       val status: String,
       val config: JsonObject  // Dynamic JSON usando kotlinx.serialization
   )
   ```

3. **Crear función de extensión para convertir:**
   ```kotlin
   fun ComponentResponse.toComponent(): Component? {
       return try {
           when (type) {
               "product_banner" -> {
                   val bannerConfig = Json.decodeFromJsonElement<ProductBannerConfig>(config)
                   Component.ProductBanner(
                       id = componentId,
                       type = type,
                       isActive = status == "active",
                       config = bannerConfig
                   )
               }
               "product_carousel" -> {
                   val carouselConfig = Json.decodeFromJsonElement<ProductCarouselConfig>(config)
                   Component.ProductCarousel(
                       id = componentId,
                       type = type,
                       isActive = status == "active",
                       config = carouselConfig
                   )
               }
               // Similar para product_store y product_spotlight
               else -> null
           }
       } catch (e: Exception) {
           ReachuLogger.error("Failed to parse component: ${e.message}")
           null
       }
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuCore/Managers/CampaignManager.swift` (líneas 313-420)
- Los componentes se parsean según tipo en `ComponentModels.swift`

**Consideraciones importantes:**
- Manejar 404 gracefully (endpoint no existe, campaña puede no tener componentes)
- Filtrar solo componentes con `status == "active"`
- Parsear `config` dinámicamente según el `type` del componente
- Guardar componentes en cache después de fetch exitoso
- Actualizar StateFlow en Dispatchers.Main

---

## 8. Implementar conexión WebSocket para eventos en tiempo real de campaña

### Cómo funciona en Swift

Swift usa un `CampaignWebSocketManager` separado para gestionar la conexión WebSocket:

```swift
// Sources/ReachuCore/Managers/CampaignWebSocketManager.swift (si existe)
// O lógica en CampaignManager.swift (líneas 420-540)

private func initializeWebSocket(campaignId: Int) async {
    let baseURL = campaignWebSocketBaseURL
    let urlString = "\(baseURL)/ws?campaignId=\(campaignId)"
    
    webSocketManager = CampaignWebSocketManager(urlString: urlString)
    
    // Configurar callbacks para eventos
    webSocketManager?.onCampaignStarted = { [weak self] event in
        Task { @MainActor in
            self?.handleCampaignStarted(event)
        }
    }
    
    webSocketManager?.onCampaignEnded = { [weak self] event in
        Task { @MainActor in
            self?.handleCampaignEnded(event)
        }
    }
    
    webSocketManager?.onComponentStatusChanged = { [weak self] event in
        Task { @MainActor in
            self?.handleComponentStatusChanged(event)
        }
    }
    
    webSocketManager?.onComponentConfigUpdated = { [weak self] event in
        Task { @MainActor in
            self?.handleComponentConfigUpdated(event)
        }
    }
    
    webSocketManager?.onConnectionStatusChanged = { [weak self] connected in
        Task { @MainActor in
            self?.isConnected = connected
        }
    }
    
    await webSocketManager?.connect()
}
```

Los eventos tienen este formato:
```json
// campaign_started
{
  "type": "campaign_started",
  "campaignId": 14,
  "startDate": "2024-01-01T00:00:00Z",
  "endDate": "2024-12-31T23:59:59Z"
}

// campaign_ended
{
  "type": "campaign_ended",
  "campaignId": 14
}

// component_status_changed
{
  "type": "component_status_changed",
  "data": {
    "componentId": 8,
    "campaignComponentId": 15,
    "componentType": "product_banner",
    "status": "active"
  }
}

// component_config_updated
{
  "type": "component_config_updated",
  "data": {
    "componentId": 8,
    "campaignComponentId": 15,
    "componentType": "product_banner",
    "config": { ... }
  }
}
```

### Qué hacer en Kotlin

1. **Crear clase CampaignWebSocketManager:**
   ```kotlin
   class CampaignWebSocketManager(private val url: String) {
       private var webSocket: WebSocket? = null
       private val client = HttpClient {
           install(WebSockets)
       }
       
       var onCampaignStarted: ((CampaignStartedEvent) -> Unit)? = null
       var onCampaignEnded: ((CampaignEndedEvent) -> Unit)? = null
       var onComponentStatusChanged: ((ComponentStatusChangedEvent) -> Unit)? = null
       var onComponentConfigUpdated: ((ComponentConfigUpdatedEvent) -> Unit)? = null
       var onConnectionStatusChanged: ((Boolean) -> Unit)? = null
       
       suspend fun connect() {
           try {
               webSocket = client.webSocketSession {
                   url(url)
               }
               
               onConnectionStatusChanged?.invoke(true)
               
               // Escuchar mensajes
               for (frame in webSocket!!.incoming) {
                   when (frame) {
                       is Frame.Text -> {
                           val text = frame.readText()
                           handleMessage(text)
                       }
                       is Frame.Close -> {
                           onConnectionStatusChanged?.invoke(false)
                           // Auto-reconnect después de delay
                           delay(5000)
                           connect()
                       }
                       else -> {}
                   }
               }
           } catch (e: Exception) {
               onConnectionStatusChanged?.invoke(false)
               ReachuLogger.error("WebSocket connection failed: ${e.message}")
               // Auto-reconnect después de delay
               delay(5000)
               connect()
           }
       }
       
       private fun handleMessage(text: String) {
           val json = Json.parseToJsonElement(text).jsonObject
           val type = json["type"]?.jsonPrimitive?.content
           
           when (type) {
               "campaign_started" -> {
                   val event = Json.decodeFromJsonElement<CampaignStartedEvent>(json)
                   onCampaignStarted?.invoke(event)
               }
               "campaign_ended" -> {
                   val event = Json.decodeFromJsonElement<CampaignEndedEvent>(json)
                   onCampaignEnded?.invoke(event)
               }
               "component_status_changed" -> {
                   val event = Json.decodeFromJsonElement<ComponentStatusChangedEvent>(json)
                   onComponentStatusChanged?.invoke(event)
               }
               "component_config_updated" -> {
                   val event = Json.decodeFromJsonElement<ComponentConfigUpdatedEvent>(json)
                   onComponentConfigUpdated?.invoke(event)
               }
           }
       }
       
       fun disconnect() {
           webSocket?.close()
           webSocket = null
           onConnectionStatusChanged?.invoke(false)
       }
   }
   ```

2. **Crear data classes para eventos:**
   ```kotlin
   @Serializable
   data class CampaignStartedEvent(
       val type: String,
       val campaignId: Int,
       val startDate: String,
       val endDate: String
   )
   
   @Serializable
   data class CampaignEndedEvent(
       val type: String,
       val campaignId: Int
   )
   
   @Serializable
   data class ComponentStatusChangedEvent(
       val type: String,
       val data: ComponentStatusData
   )
   
   @Serializable
   data class ComponentConfigUpdatedEvent(
       val type: String,
       val data: ComponentConfigData
   )
   ```

3. **Integrar en CampaignManager:**
   ```kotlin
   private suspend fun initializeWebSocket(campaignId: Int) {
       val baseURL = ReachuConfiguration.shared.campaignConfiguration.webSocketBaseURL
       val url = "$baseURL/ws?campaignId=$campaignId"
       
       webSocketManager = CampaignWebSocketManager(url)
       
       webSocketManager?.onCampaignStarted = { event ->
           CoroutineScope(Dispatchers.Main).launch {
               handleCampaignStarted(event)
           }
       }
       
       // Similar para otros eventos...
       
       webSocketManager?.connect()
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuCore/Managers/CampaignManager.swift` (líneas 420-540)
- Buscar `CampaignWebSocketManager` si existe como archivo separado

**Consideraciones importantes:**
- Usar librería WebSocket de Kotlin (OkHttp WebSocket, Ktor WebSockets, etc.)
- Auto-reconnect en caso de desconexión (después de delay de 5 segundos)
- Parsear eventos JSON según tipo
- Ejecutar handlers en Dispatchers.Main para actualizar StateFlows
- Actualizar `isConnected` cuando cambia estado de conexión

---

## 9. Implementar handlers para eventos WebSocket

### Cómo funciona en Swift

Cada tipo de evento tiene su handler específico:

```swift
// Sources/ReachuCore/Managers/CampaignManager.swift (líneas 541-790)

private func handleCampaignStarted(_ event: CampaignStartedEvent) {
    ReachuLogger.success("Campaign started: \(event.campaignId)")
    
    isCampaignActive = true
    campaignState = .active
    
    // Update campaign with new dates
    currentCampaign = Campaign(
        id: event.campaignId,
        startDate: event.startDate,
        endDate: event.endDate,
        isPaused: false
    )
    
    // Save to cache
    if let campaign = currentCampaign {
        CacheManager.shared.saveCampaign(campaign)
    }
    CacheManager.shared.saveCampaignState(campaignState, isActive: isCampaignActive)
    
    // Fetch active components now that campaign is active
    Task {
        await fetchActiveComponents(campaignId: event.campaignId)
    }
    
    // Notify observers
    NotificationCenter.default.post(
        name: .campaignStarted,
        object: nil,
        userInfo: ["campaignId": event.campaignId]
    )
}

private func handleCampaignEnded(_ event: CampaignEndedEvent) {
    ReachuLogger.info("Campaign ended: \(event.campaignId)")
    
    isCampaignActive = false
    campaignState = .ended
    
    // Clear components
    activeComponents.removeAll()
    
    // Save to cache
    CacheManager.shared.saveCampaignState(campaignState, isActive: isCampaignActive)
    
    // Disconnect WebSocket
    webSocketManager?.disconnect()
    
    // Notify observers
    NotificationCenter.default.post(
        name: .campaignEnded,
        object: nil,
        userInfo: ["campaignId": event.campaignId]
    )
}

private func handleComponentStatusChanged(_ event: ComponentStatusChangedEvent) {
    let componentId = String(event.data.campaignComponentId)
    let status = event.data.status
    
    if status == "active" {
        // Fetch and add component
        Task {
            if let component = await fetchComponent(componentId: componentId) {
                await MainActor.run {
                    if !activeComponents.contains(where: { $0.id == componentId }) {
                        activeComponents.append(component)
                        CacheManager.shared.saveComponents(activeComponents)
                    }
                }
            }
        }
    } else if status == "inactive" {
        // Remove component
        await MainActor.run {
            activeComponents.removeAll { $0.id == componentId }
            CacheManager.shared.saveComponents(activeComponents)
        }
    }
}

private func handleComponentConfigUpdated(_ event: ComponentConfigUpdatedEvent) {
    let componentId = String(event.data.campaignComponentId)
    
    do {
        let component = try event.toComponent()
        
        // Update existing component's config
        if let index = activeComponents.firstIndex(where: { $0.id == componentId }) {
            activeComponents[index] = component
            CacheManager.shared.saveComponents(activeComponents)
        } else {
            // If component doesn't exist yet, add it (only if campaign is active)
            if isCampaignActive && currentCampaign?.isPaused != true {
                activeComponents.append(component)
                CacheManager.shared.saveComponents(activeComponents)
            }
        }
    } catch {
        ReachuLogger.error("Failed to convert component event: \(error)")
    }
}
```

### Qué hacer en Kotlin

1. **Implementar handleCampaignStarted:**
   ```kotlin
   private suspend fun handleCampaignStarted(event: CampaignStartedEvent) {
       ReachuLogger.success("Campaign started: ${event.campaignId}")
       
       withContext(Dispatchers.Main) {
           _isCampaignActive.value = true
           _campaignState.value = CampaignState.Active
           
           // Update campaign with new dates
           _currentCampaign.value = Campaign(
               id = event.campaignId,
               startDate = event.startDate,
               endDate = event.endDate,
               isPaused = false
           )
           
           // Save to cache
           _currentCampaign.value?.let { campaign ->
               CacheManager.saveCampaign(campaign)
           }
           CacheManager.saveCampaignState(_campaignState.value, _isCampaignActive.value)
       }
       
       // Fetch active components now that campaign is active
       fetchActiveComponents(event.campaignId)
   }
   ```

2. **Implementar handleCampaignEnded:**
   ```kotlin
   private suspend fun handleCampaignEnded(event: CampaignEndedEvent) {
       ReachuLogger.info("Campaign ended: ${event.campaignId}")
       
       withContext(Dispatchers.Main) {
           _isCampaignActive.value = false
           _campaignState.value = CampaignState.Ended
           
           // Clear components
           _activeComponents.value = emptyList()
           
           // Save to cache
           CacheManager.saveCampaignState(_campaignState.value, _isCampaignActive.value)
       }
       
       // Disconnect WebSocket
       webSocketManager?.disconnect()
   }
   ```

3. **Implementar handleComponentStatusChanged:**
   ```kotlin
   private suspend fun handleComponentStatusChanged(event: ComponentStatusChangedEvent) {
       val componentId = event.data.campaignComponentId.toString()
       val status = event.data.status
       
       if (status == "active") {
           // Fetch and add component
           val component = fetchComponent(componentId = componentId)
           if (component != null) {
               withContext(Dispatchers.Main) {
                   val current = _activeComponents.value.toMutableList()
                   if (!current.any { it.id == componentId }) {
                       current.add(component)
                       _activeComponents.value = current
                       CacheManager.saveComponents(_activeComponents.value)
                   }
               }
           }
       } else if (status == "inactive") {
           // Remove component
           withContext(Dispatchers.Main) {
               val current = _activeComponents.value.toMutableList()
               current.removeAll { it.id == componentId }
               _activeComponents.value = current
               CacheManager.saveComponents(_activeComponents.value)
           }
       }
   }
   ```

4. **Implementar handleComponentConfigUpdated:**
   ```kotlin
   private suspend fun handleComponentConfigUpdated(event: ComponentConfigUpdatedEvent) {
       val componentId = event.data.campaignComponentId.toString()
       
       try {
           val component = event.toComponent()
           
           withContext(Dispatchers.Main) {
               val current = _activeComponents.value.toMutableList()
               val index = current.indexOfFirst { it.id == componentId }
               
               if (index >= 0) {
                   // Update existing component's config
                   current[index] = component
                   _activeComponents.value = current
                   CacheManager.saveComponents(_activeComponents.value)
               } else {
                   // If component doesn't exist yet, add it (only if campaign is active)
                   if (_isCampaignActive.value && _currentCampaign.value?.isPaused != true) {
                       current.add(component)
                       _activeComponents.value = current
                       CacheManager.saveComponents(_activeComponents.value)
                   }
               }
           }
       } catch (e: Exception) {
           ReachuLogger.error("Failed to convert component event: ${e.message}")
       }
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuCore/Managers/CampaignManager.swift` (líneas 541-790)

**Consideraciones importantes:**
- Todos los handlers deben ejecutarse en Dispatchers.Main para actualizar StateFlows
- Guardar cambios en cache después de cada actualización
- En `handleCampaignStarted`, fetch componentes después de activar campaña
- En `handleCampaignEnded`, desconectar WebSocket y limpiar componentes
- En `handleComponentStatusChanged`, solo agregar si status == "active"
- En `handleComponentConfigUpdated`, solo agregar nuevo componente si campaña está activa y no pausada

---

## 10. Crear CacheManager para persistir campaña, componentes y estado en SharedPreferences

### Cómo funciona en Swift

Swift usa `UserDefaults` para cachear datos:

```swift
// Sources/ReachuCore/Managers/CacheManager.swift
@MainActor
public class CacheManager {
    public static let shared = CacheManager()
    
    private enum CacheKeys {
        static let campaign = "reachu.cache.campaign"
        static let components = "reachu.cache.components"
        static let campaignState = "reachu.cache.campaignState"
        static let isCampaignActive = "reachu.cache.isCampaignActive"
        static let lastUpdated = "reachu.cache.lastUpdated"
    }
    
    public var cacheExpirationInterval: TimeInterval = 24 * 60 * 60  // 24 hours
    
    private let userDefaults: UserDefaults
    
    private init() {
        self.userDefaults = UserDefaults.standard
    }
    
    public func saveCampaign(_ campaign: Campaign) {
        do {
            let encoder = JSONEncoder()
            let data = try encoder.encode(campaign)
            userDefaults.set(data, forKey: CacheKeys.campaign)
            userDefaults.set(Date(), forKey: CacheKeys.lastUpdated)
        } catch {
            ReachuLogger.error("Failed to cache campaign: \(error)")
        }
    }
    
    public func loadCampaign() -> Campaign? {
        guard let data = userDefaults.data(forKey: CacheKeys.campaign),
              isCacheValid() else {
            return nil
        }
        
        do {
            let decoder = JSONDecoder()
            let campaign = try decoder.decode(Campaign.self, from: data)
            return campaign
        } catch {
            ReachuLogger.error("Failed to decode cached campaign: \(error)")
            return nil
        }
    }
    
    private func isCacheValid() -> Bool {
        guard let lastUpdated = userDefaults.object(forKey: CacheKeys.lastUpdated) as? Date else {
            return false
        }
        
        let age = Date().timeIntervalSince(lastUpdated)
        return age < cacheExpirationInterval
    }
    
    // Similar para saveComponents, loadComponents, saveCampaignState, loadCampaignState
}
```

### Qué hacer en Kotlin

1. **Crear object CacheManager:**
   ```kotlin
   object CacheManager {
       private const val PREFS_NAME = "reachu_cache"
       private const val KEY_CAMPAIGN = "campaign"
       private const val KEY_COMPONENTS = "components"
       private const val KEY_CAMPAIGN_STATE = "campaign_state"
       private const val KEY_IS_CAMPAIGN_ACTIVE = "is_campaign_active"
       private const val KEY_LAST_UPDATED = "last_updated"
       
       var cacheExpirationInterval: Long = 24 * 60 * 60 * 1000  // 24 hours in milliseconds
       
       private fun getSharedPreferences(context: Context): SharedPreferences {
           return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
       }
       
       fun saveCampaign(context: Context, campaign: Campaign) {
           try {
               val json = Json.encodeToString(campaign)
               getSharedPreferences(context).edit().apply {
                   putString(KEY_CAMPAIGN, json)
                   putLong(KEY_LAST_UPDATED, System.currentTimeMillis())
                   apply()
               }
           } catch (e: Exception) {
               ReachuLogger.error("Failed to cache campaign: ${e.message}")
           }
       }
       
       fun loadCampaign(context: Context): Campaign? {
           val prefs = getSharedPreferences(context)
           val json = prefs.getString(KEY_CAMPAIGN, null) ?: return null
           
           if (!isCacheValid(prefs)) {
               return null
           }
           
           return try {
               Json.decodeFromString<Campaign>(json)
           } catch (e: Exception) {
               ReachuLogger.error("Failed to decode cached campaign: ${e.message}")
               null
           }
       }
       
       private fun isCacheValid(prefs: SharedPreferences): Boolean {
           val lastUpdated = prefs.getLong(KEY_LAST_UPDATED, 0)
           if (lastUpdated == 0L) return false
           
           val age = System.currentTimeMillis() - lastUpdated
           return age < cacheExpirationInterval
       }
       
       fun saveComponents(context: Context, components: List<Component>) {
           try {
               val json = Json.encodeToString(components)
               getSharedPreferences(context).edit().apply {
                   putString(KEY_COMPONENTS, json)
                   putLong(KEY_LAST_UPDATED, System.currentTimeMillis())
                   apply()
               }
           } catch (e: Exception) {
               ReachuLogger.error("Failed to cache components: ${e.message}")
           }
       }
       
       fun loadComponents(context: Context): List<Component> {
           val prefs = getSharedPreferences(context)
           val json = prefs.getString(KEY_COMPONENTS, null) ?: return emptyList()
           
           if (!isCacheValid(prefs)) {
               return emptyList()
           }
           
           return try {
               Json.decodeFromString<List<Component>>(json)
           } catch (e: Exception) {
               ReachuLogger.error("Failed to decode cached components: ${e.message}")
               emptyList()
           }
       }
       
       fun saveCampaignState(context: Context, state: CampaignState, isActive: Boolean) {
           try {
               getSharedPreferences(context).edit().apply {
                   putString(KEY_CAMPAIGN_STATE, state.name)
                   putBoolean(KEY_IS_CAMPAIGN_ACTIVE, isActive)
                   putLong(KEY_LAST_UPDATED, System.currentTimeMillis())
                   apply()
               }
           } catch (e: Exception) {
               ReachuLogger.error("Failed to cache campaign state: ${e.message}")
           }
       }
       
       fun loadCampaignState(context: Context): Pair<CampaignState, Boolean>? {
           val prefs = getSharedPreferences(context)
           val stateName = prefs.getString(KEY_CAMPAIGN_STATE, null) ?: return null
           
           if (!isCacheValid(prefs)) {
               return null
           }
           
           return try {
               val state = CampaignState.valueOf(stateName)
               val isActive = prefs.getBoolean(KEY_IS_CAMPAIGN_ACTIVE, false)
               Pair(state, isActive)
           } catch (e: Exception) {
               ReachuLogger.error("Failed to decode cached campaign state: ${e.message}")
               null
           }
       }
       
       fun clearCache(context: Context) {
           getSharedPreferences(context).edit().clear().apply()
       }
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuCore/Managers/CacheManager.swift` (completo)

**Consideraciones importantes:**
- Usar SharedPreferences o DataStore para persistencia
- Cache expiration: 24 horas por defecto (configurable)
- Validar cache antes de cargar (verificar timestamp)
- Manejar errores de encoding/decoding gracefully
- El cache permite carga instantánea al iniciar app (muestra datos mientras fetch en background)
- En CampaignManager, cargar desde cache primero, luego actualizar desde API

---

## 11. Crear componente RProductBanner con estructura base y carga de configuración desde CampaignManager

### Cómo funciona en Swift

El componente observa `CampaignManager` y obtiene su configuración automáticamente:

```swift
// Sources/ReachuUI/Components/RProductBanner.swift (líneas 1-310)
public struct RProductBanner: View {
    private let componentId: String?
    
    @ObservedObject private var campaignManager = CampaignManager.shared
    
    @Environment(\.colorScheme) private var colorScheme
    
    // Get active product banner component from campaign
    private var activeComponent: Component? {
        campaignManager.getActiveComponent(type: "product_banner", componentId: componentId)
    }
    
    // Extract ProductBannerConfig from component
    private var config: ProductBannerConfig? {
        guard let component = activeComponent else {
            return nil
        }
        
        guard case .productBanner(let config) = component.config else {
            return nil
        }
        
        return config
    }
    
    // Should show component
    private var shouldShow: Bool {
        guard ReachuConfiguration.shared.shouldUseSDK else {
            return false
        }
        
        let campaignId = ReachuConfiguration.shared.liveShowConfiguration.campaignId
        guard campaignId > 0 else {
            // No campaign configured - show component (legacy behavior)
            return true
        }
        
        // Campaign must be active and not paused
        guard campaignManager.isCampaignActive,
              campaignManager.currentCampaign?.isPaused != true else {
            return false
        }
        
        // Component must exist and be active
        return activeComponent?.isActive == true && config != nil
    }
    
    public var body: some View {
        Group {
            if !shouldShow {
                EmptyView()
            } else if let config = config {
                // Show banner
                bannerContent(config: config)
            } else {
                // Show skeleton loader while loading
                skeletonView
            }
        }
        .onChange(of: campaignManager.isCampaignActive) { _ in
            // React to campaign state changes
        }
        .onChange(of: campaignManager.activeComponents.count) { _ in
            // React when components are loaded/updated
        }
    }
}
```

### Qué hacer en Kotlin

1. **Crear Composable que observa CampaignManager:**
   ```kotlin
   @Composable
   fun RProductBanner(
       componentId: String? = null,
       modifier: Modifier = Modifier
   ) {
       val isCampaignActive by CampaignManager.isCampaignActive.collectAsState()
       val activeComponents by CampaignManager.activeComponents.collectAsState()
       val currentCampaign by CampaignManager.currentCampaign.collectAsState()
       
       // Get active product banner component
       val activeComponent = remember(activeComponents, componentId) {
           CampaignManager.getActiveComponent(type = "product_banner", componentId = componentId)
       }
       
       // Extract ProductBannerConfig
       val config = remember(activeComponent) {
           when (activeComponent) {
               is Component.ProductBanner -> activeComponent.config
               else -> null
           }
       }
       
       // Should show component
       val shouldShow = remember(
           isCampaignActive,
           currentCampaign?.isPaused,
           activeComponent?.isActive,
           config
       ) {
           if (!ReachuConfiguration.shared.shouldUseSDK) return@remember false
           
           val campaignId = ReachuConfiguration.shared.liveShowConfiguration.campaignId
           if (campaignId == 0) {
               // No campaign configured - show component (legacy behavior)
               return@remember true
           }
           
           // Campaign must be active and not paused
           if (!isCampaignActive || currentCampaign?.isPaused == true) {
               return@remember false
           }
           
           // Component must exist and be active
           activeComponent?.isActive == true && config != null
       }
       
       when {
           !shouldShow -> {
               // EmptyView - component invisible
           }
           config != null -> {
               // Show banner
               BannerContent(config = config, modifier = modifier)
           }
           else -> {
               // Show skeleton loader while loading
               BannerSkeleton(modifier = modifier)
           }
       }
   }
   ```

2. **Crear función helper en CampaignManager:**
   ```kotlin
   fun getActiveComponent(type: String, componentId: String? = null): Component? {
       val components = activeComponents.value.filter { it.type == type }
       
       return if (componentId != null) {
           components.firstOrNull { it.id == componentId && it.isActive }
       } else {
           components.firstOrNull { it.isActive }
       }
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuUI/Components/RProductBanner.swift` (líneas 1-310)
- Demo: `PregancyDemo/PregancyDemo/WeeksView.swift` (línea 33) muestra uso básico

**Consideraciones importantes:**
- El componente debe reaccionar automáticamente a cambios en CampaignManager
- Usar `remember` para evitar recálculos innecesarios
- `shouldShow` debe verificar: SDK habilitado, campaña activa, componente activo
- Si no hay campaña configurada (campaignId == 0), mostrar componente normalmente (legacy behavior)
- Mostrar skeleton loader mientras `config == null`
- Mostrar EmptyView si `!shouldShow` (componente invisible)

---

## 12. Implementar caching de valores de styling parseados en RProductBanner

### Cómo funciona en Swift

Swift cachea valores parseados para evitar recalcular en cada render:

```swift
// Sources/ReachuUI/Components/RProductBanner.swift (líneas 15-204)
private struct CachedStyling {
    let imageURL: URL?
    let bannerHeight: CGFloat
    let titleFontSize: CGFloat
    let subtitleFontSize: CGFloat
    let buttonFontSize: CGFloat
    let titleColor: Color
    let subtitleColor: Color
    let buttonBackgroundColor: Color
    let buttonTextColor: Color
    let backgroundColor: Color?  // Background color overlay
    let overlayBottomOpacity: Double
    let overlayTopOpacity: Double
    let textAlignment: SwiftUI.TextAlignment
    let contentVerticalAlignment: VerticalAlignment
    let configId: String  // Used to detect config changes
    
    init(config: ProductBannerConfig, adaptiveColors: AdaptiveColors) {
        // Build full URL
        let fullImageURL = Self.buildFullURL(from: config.backgroundImageUrl)
        self.imageURL = URL(string: fullImageURL)
        
        // Cache clamped sizes
        self.bannerHeight = CGFloat(Self.getClampedSize(config.bannerHeight, min: 150, max: 400, default: 200))
        self.titleFontSize = CGFloat(Self.getClampedSize(config.titleFontSize, min: 16, max: 32, default: 24))
        // ... más sizes
        
        // Cache parsed colors
        self.titleColor = Self.getColor(from: config.titleColor, defaultColor: adaptiveColors.textPrimary)
        self.subtitleColor = Self.getColor(from: config.subtitleColor, defaultColor: adaptiveColors.textSecondary)
        // ... más colors
        
        // Parse backgroundColor (can be rgba() or hex)
        if let bgColorString = config.backgroundColor {
            self.backgroundColor = Self.parseRGBA(from: bgColorString) ?? Self.parseColor(from: bgColorString)
        }
        
        // Cache overlay opacity
        let overlayOpacity: Double
        if let bgColor = self.backgroundColor,
           let components = bgColor.cgColor?.components,
           components.count >= 4 {
            overlayOpacity = Double(components[3])  // Alpha channel
        } else {
            overlayOpacity = config.overlayOpacity ?? 0.5
        }
        self.overlayBottomOpacity = overlayOpacity
        self.overlayTopOpacity = overlayOpacity * 0.6  // Top is 60% of bottom
        
        // Parse text alignment
        switch config.textAlignment?.lowercased() {
        case "center": self.textAlignment = .center
        case "right": self.textAlignment = .trailing
        default: self.textAlignment = .leading
        }
        
        // Parse vertical alignment
        switch config.contentVerticalAlignment?.lowercased() {
        case "top": self.contentVerticalAlignment = .top
        case "center": self.contentVerticalAlignment = .center
        default: self.contentVerticalAlignment = .bottom
        }
        
        // Create unique identifier for this config
        self.configId = "\(config.productId)-\(config.backgroundImageUrl)-\(config.title)"
    }
    
    private static func parseColor(from: String, defaultColor: Color) -> Color {
        // Parse hex color (#FFFFFF or FFFFFF)
        if let color = parseHexColor(from) {
            return color
        }
        return defaultColor
    }
    
    private static func parseRGBA(from: String) -> Color? {
        // Parse rgba(255, 255, 255, 0.5)
        let pattern = #"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)"#
        // ... regex parsing
    }
    
    private static func getClampedSize(_ value: Int?, min: Int, max: Int, default: Int) -> Int {
        guard let value = value else { return `default` }
        return max(min, min(max, value))
    }
    
    private static func buildFullURL(from path: String) -> String {
        if path.hasPrefix("http://") || path.hasPrefix("https://") {
            return path
        }
        // Build full URL from base URL + path
        let baseURL = ReachuConfiguration.shared.environment.graphQLURL
            .replacingOccurrences(of: "/graphql", with: "")
        return "\(baseURL)\(path)"
    }
}
```

### Qué hacer en Kotlin

1. **Crear data class CachedStyling:**
   ```kotlin
   data class CachedStyling(
       val imageURL: String?,
       val bannerHeight: Float,
       val titleFontSize: Float,
       val subtitleFontSize: Float,
       val buttonFontSize: Float,
       val titleColor: Color,
       val subtitleColor: Color,
       val buttonBackgroundColor: Color,
       val buttonTextColor: Color,
       val backgroundColor: Color?,
       val overlayBottomOpacity: Float,
       val overlayTopOpacity: Float,
       val textAlignment: TextAlign,
       val contentVerticalAlignment: Alignment.Vertical,
       val configId: String
   ) {
       companion object {
           fun from(
               config: ProductBannerConfig,
               adaptiveColors: AdaptiveColors
           ): CachedStyling {
               // Build full URL
               val fullImageURL = buildFullURL(config.backgroundImageUrl)
               
               // Cache clamped sizes
               val bannerHeight = getClampedSize(config.bannerHeight, 150, 400, 200).toFloat()
               val titleFontSize = getClampedSize(config.titleFontSize, 16, 32, 24).toFloat()
               // ... más sizes
               
               // Cache parsed colors
               val titleColor = parseColor(config.titleColor, adaptiveColors.textPrimary)
               val subtitleColor = parseColor(config.subtitleColor, adaptiveColors.textSecondary)
               // ... más colors
               
               // Parse backgroundColor
               val backgroundColor = config.backgroundColor?.let {
                   parseRGBA(it) ?: parseColor(it, null)
               }
               
               // Cache overlay opacity
               val overlayOpacity = backgroundColor?.alpha ?: (config.overlayOpacity?.toFloat() ?: 0.5f)
               val overlayBottomOpacity = overlayOpacity
               val overlayTopOpacity = overlayOpacity * 0.6f
               
               // Parse text alignment
               val textAlignment = when (config.textAlignment?.lowercase()) {
                   "center" -> TextAlign.Center
                   "right" -> TextAlign.End
                   else -> TextAlign.Start
               }
               
               // Parse vertical alignment
               val contentVerticalAlignment = when (config.contentVerticalAlignment?.lowercase()) {
                   "top" -> Alignment.Top
                   "center" -> Alignment.CenterVertically
                   else -> Alignment.Bottom
               }
               
               // Create unique identifier
               val configId = "${config.productId}-${config.backgroundImageUrl}-${config.title}"
               
               return CachedStyling(
                   imageURL = fullImageURL,
                   bannerHeight = bannerHeight,
                   titleFontSize = titleFontSize,
                   subtitleFontSize = subtitleFontSize,
                   buttonFontSize = buttonFontSize,
                   titleColor = titleColor,
                   subtitleColor = subtitleColor,
                   buttonBackgroundColor = buttonBackgroundColor,
                   buttonTextColor = buttonTextColor,
                   backgroundColor = backgroundColor,
                   overlayBottomOpacity = overlayBottomOpacity,
                   overlayTopOpacity = overlayTopOpacity,
                   textAlignment = textAlignment,
                   contentVerticalAlignment = contentVerticalAlignment,
                   configId = configId
               )
           }
           
           private fun parseColor(hex: String?, defaultColor: Color?): Color {
               // Parse hex color (#FFFFFF or FFFFFF)
               if (hex == null) return defaultColor ?: Color.Black
               // ... implementar parsing de hex
           }
           
           private fun parseRGBA(rgba: String): Color? {
               // Parse rgba(255, 255, 255, 0.5)
               val pattern = Regex("rgba\\((\\d+),\\s*(\\d+),\\s*(\\d+),\\s*([\\d.]+)\\)")
               val match = pattern.find(rgba) ?: return null
               val (r, g, b, a) = match.destructured
               return Color(
                   red = r.toInt() / 255f,
                   green = g.toInt() / 255f,
                   blue = b.toInt() / 255f,
                   alpha = a.toFloat()
               )
           }
           
           private fun getClampedSize(value: Int?, min: Int, max: Int, default: Int): Int {
               return value?.coerceIn(min, max) ?: default
           }
           
           private fun buildFullURL(path: String): String {
               if (path.startsWith("http://") || path.startsWith("https://")) {
                   return path
               }
               val baseURL = ReachuConfiguration.shared.environment.graphQLURL
                   .replace("/graphql", "")
                   .replace("/v1/graphql", "")
               return "$baseURL$path"
           }
       }
   }
   ```

2. **Usar remember para cachear:**
   ```kotlin
   @Composable
   fun RProductBanner(...) {
       val config = // ... obtener config
       val adaptiveColors = ReachuColors.adaptive(LocalColorScheme.current)
       
       val cachedStyling = remember(config, adaptiveColors) {
           config?.let { CachedStyling.from(it, adaptiveColors) }
       }
       
       // Usar cachedStyling en el UI
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuUI/Components/RProductBanner.swift` (líneas 15-204)

**Consideraciones importantes:**
- Solo recalcular cuando `configId` cambia (usar `remember` con dependencias)
- Parsear colores hex (#FFFFFF o FFFFFF) y rgba(r, g, b, a)
- Clamp sizes entre min y max valores
- Build full URL desde path relativo o usar absoluto si ya tiene http/https
- Overlay top opacity es 60% del bottom opacity
- Cachear todo para evitar recalcular en cada recomposition

---

## 13. Implementar UI del RProductBanner con imagen de fondo, overlay gradiente, texto y botón

### Cómo funciona en Swift

El banner tiene una estructura compleja con imagen, overlay, texto y botón:

```swift
// Sources/ReachuUI/Components/RProductBanner.swift (líneas 372-638)
private func bannerContent(config: ProductBannerConfig, styling: CachedStyling) -> some View {
    ZStack {
        // Background image
        AsyncImage(url: styling.imageURL) { image in
            image
                .resizable()
                .aspectRatio(contentMode: .fill)
        } placeholder: {
            Color.gray.opacity(0.3)
        }
        .frame(height: styling.bannerHeight)
        .clipped()
        
        // Background color overlay (if exists)
        if let bgColor = styling.backgroundColor {
            bgColor
                .frame(height: styling.bannerHeight)
        }
        
        // Gradient overlay (top to bottom)
        LinearGradient(
            colors: [
                Color.black.opacity(styling.overlayTopOpacity),
                Color.black.opacity(styling.overlayBottomOpacity)
            ],
            startPoint: .top,
            endPoint: .bottom
        )
        .frame(height: styling.bannerHeight)
        
        // Content (title, subtitle, button)
        VStack(alignment: styling.textAlignment == .center ? .center : 
                          styling.textAlignment == .trailing ? .trailing : .leading) {
            Spacer()
            
            if let title = config.title {
                Text(title)
                    .font(.system(size: styling.titleFontSize, weight: .bold))
                    .foregroundColor(styling.titleColor)
                    .multilineTextAlignment(styling.textAlignment)
            }
            
            if let subtitle = config.subtitle {
                Text(subtitle)
                    .font(.system(size: styling.subtitleFontSize))
                    .foregroundColor(styling.subtitleColor)
                    .multilineTextAlignment(styling.textAlignment)
            }
            
            if let buttonText = config.buttonText {
                Button(action: {
                    // Handle button action
                }) {
                    Text(buttonText)
                        .font(.system(size: styling.buttonFontSize))
                        .foregroundColor(styling.buttonTextColor)
                        .padding(.horizontal, 20)
                        .padding(.vertical, 12)
                        .background(styling.buttonBackgroundColor)
                        .cornerRadius(8)
                }
            }
            
            Spacer()
        }
        .frame(maxWidth: .infinity, alignment: styling.textAlignment == .center ? .center :
                                                      styling.textAlignment == .trailing ? .trailing : .leading)
        .padding(.horizontal, 20)
        .padding(.vertical, styling.contentVerticalAlignment == .top ? 20 : 
                            styling.contentVerticalAlignment == .center ? 0 : 20)
    }
    .frame(height: styling.bannerHeight)
    .onTapGesture {
        // Open product detail overlay
    }
}
```

### Qué hacer en Kotlin

1. **Crear Composable BannerContent:**
   ```kotlin
   @Composable
   fun BannerContent(
       config: ProductBannerConfig,
       styling: CachedStyling,
       modifier: Modifier = Modifier,
       onBannerClick: () -> Unit = {}
   ) {
       Box(
           modifier = modifier
               .height(styling.bannerHeight.dp)
               .clickable { onBannerClick() }
       ) {
           // Background image
           AsyncImage(
               model = styling.imageURL,
               contentDescription = null,
               modifier = Modifier
                   .fillMaxWidth()
                   .height(styling.bannerHeight.dp)
                   .clip(RoundedCornerShape(0.dp)),
               contentScale = ContentScale.Crop
           )
           
           // Background color overlay (if exists)
           styling.backgroundColor?.let { bgColor ->
               Box(
                   modifier = Modifier
                       .fillMaxWidth()
                       .height(styling.bannerHeight.dp)
                       .background(bgColor)
               )
           }
           
           // Gradient overlay (top to bottom)
           Box(
               modifier = Modifier
                   .fillMaxWidth()
                   .height(styling.bannerHeight.dp)
                   .background(
                       Brush.verticalGradient(
                           colors = listOf(
                               Color.Black.copy(alpha = styling.overlayTopOpacity),
                               Color.Black.copy(alpha = styling.overlayBottomOpacity)
                           )
                       )
                   )
           )
           
           // Content (title, subtitle, button)
           Column(
               modifier = Modifier
                   .fillMaxWidth()
                   .height(styling.bannerHeight.dp)
                   .padding(horizontal = 20.dp)
                   .padding(
                       vertical = when (styling.contentVerticalAlignment) {
                           Alignment.Top -> 20.dp
                           Alignment.CenterVertically -> 0.dp
                           Alignment.Bottom -> 20.dp
                       }
                   ),
               horizontalAlignment = when (styling.textAlignment) {
                   TextAlign.Center -> Alignment.CenterHorizontally
                   TextAlign.End -> Alignment.End
                   else -> Alignment.Start
               },
               verticalArrangement = when (styling.contentVerticalAlignment) {
                   Alignment.Top -> Arrangement.Top
                   Alignment.CenterVertically -> Arrangement.Center
                   Alignment.Bottom -> Arrangement.Bottom
               }
           ) {
               Spacer(modifier = Modifier.weight(1f))
               
               config.title?.let { title ->
                   Text(
                       text = title,
                       fontSize = styling.titleFontSize.sp,
                       fontWeight = FontWeight.Bold,
                       color = styling.titleColor,
                       textAlign = styling.textAlignment
                   )
               }
               
               config.subtitle?.let { subtitle ->
                   Text(
                       text = subtitle,
                       fontSize = styling.subtitleFontSize.sp,
                       color = styling.subtitleColor,
                       textAlign = styling.textAlignment
                   )
               }
               
               config.buttonText?.let { buttonText ->
                   Button(
                       onClick = { /* Handle button action */ },
                       colors = ButtonDefaults.buttonColors(
                           backgroundColor = styling.buttonBackgroundColor
                       )
                   ) {
                       Text(
                           text = buttonText,
                           fontSize = styling.buttonFontSize.sp,
                           color = styling.buttonTextColor
                       )
                   }
               }
               
               Spacer(modifier = Modifier.weight(1f))
           }
       }
   }
   ```

2. **Integrar en RProductBanner:**
   ```kotlin
   @Composable
   fun RProductBanner(...) {
       // ... obtener config y cachedStyling
       
       when {
           config != null && cachedStyling != null -> {
               BannerContent(
                   config = config,
                   styling = cachedStyling,
                   onBannerClick = {
                       // Open product detail overlay
                   }
               )
           }
           // ... skeleton y empty view
       }
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuUI/Components/RProductBanner.swift` (líneas 372-638)
- Demo: `PregancyDemo/PregancyDemo/WeeksView.swift` (línea 33) muestra el banner funcionando

**Consideraciones importantes:**
- Usar `AsyncImage` de Coil o similar para cargar imagen de fondo
- Overlay gradiente vertical: top opacity menor que bottom (60%)
- Soporte para diferentes textAlignment (left, center, right)
- Soporte para diferentes contentVerticalAlignment (top, center, bottom)
- Height del banner: usar `bannerHeightRatio` si existe, sino `bannerHeight`
- Click en banner abre `RProductDetailOverlay` con el producto
- Skeleton loader mientras carga (shimmer effect)

---

## 14. Crear componente RProductCarousel con estructura base y carga de configuración desde CampaignManager

### Cómo funciona en Swift

Similar a RProductBanner, pero para carruseles de productos:

```swift
// Sources/ReachuUI/Components/RProductCarousel.swift (líneas 1-150)
public struct RProductCarousel: View {
    private let componentId: String?
    private let layout: String?  // Override layout
    
    @ObservedObject private var campaignManager = CampaignManager.shared
    
    private var activeComponent: Component? {
        campaignManager.getActiveComponent(type: "product_carousel", componentId: componentId)
    }
    
    private var config: ProductCarouselConfig? {
        guard let component = activeComponent,
              case .productCarousel(let config) = component.config else {
            return nil
        }
        return config
    }
    
    // Si layout se pasa como parámetro, override el del config
    private var effectiveLayout: String {
        layout ?? config?.layout ?? "full"
    }
}
```

### Qué hacer en Kotlin

1. **Crear Composable RProductCarousel:**
   ```kotlin
   @Composable
   fun RProductCarousel(
       componentId: String? = null,
       layout: String? = null,  // Override layout
       modifier: Modifier = Modifier
   ) {
       val activeComponent = CampaignManager.getActiveComponent(
           type = "product_carousel",
           componentId = componentId
       )
       
       val config = remember(activeComponent) {
           when (activeComponent) {
               is Component.ProductCarousel -> activeComponent.config
               else -> null
           }
       }
       
       val effectiveLayout = layout ?: config?.layout ?: "full"
       
       // Mostrar skeleton, contenido o empty view según shouldShow
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuUI/Components/RProductCarousel.swift` (líneas 1-150)
- Demo: `PregancyDemo/PregancyDemo/WeeksView.swift` (líneas 53-66)

**Consideraciones importantes:**
- Soporte para override de layout (parámetro tiene prioridad sobre config)
- Mostrar skeleton loader mientras carga
- Implementar `shouldShow` igual que RProductBanner

---

## 15. Implementar los 3 layouts de RProductCarousel (full, compact, horizontal)

### Cómo funciona en Swift

Cada layout tiene diferentes dimensiones y scroll direction:

```swift
// Sources/ReachuUI/Components/RProductCarousel.swift (líneas 200-500)
private func carouselContent(config: ProductCarouselConfig, layout: String) -> some View {
    switch layout {
    case "full":
        // Cards verticales full width, height = 2.0x width
        ScrollView(.vertical) {
            LazyVStack {
                ForEach(products) { product in
                    RProductCard(product: product, variant: .grid)
                        .frame(height: geometry.size.width * 2.0)
                }
            }
        }
        
    case "compact":
        // Muestra 2 cards a la vez, cada card ~47% width
        ScrollView(.vertical) {
            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())]) {
                ForEach(products) { product in
                    RProductCard(product: product, variant: .grid)
                }
            }
        }
        
    case "horizontal":
        // Cards horizontales, 90% width, 140px height
        ScrollView(.horizontal) {
            LazyHStack {
                ForEach(products) { product in
                    RProductCard(product: product, variant: .list)
                        .frame(width: geometry.size.width * 0.9, height: 140)
                }
            }
        }
    }
}
```

Auto-scroll si `autoPlay == true`:
```swift
@State private var autoScrollTimer: Timer?

.onAppear {
    if config.autoPlay {
        autoScrollTimer = Timer.scheduledTimer(withTimeInterval: config.interval / 1000.0, repeats: true) { _ in
            // Scroll automático
        }
    }
}
```

### Qué hacer en Kotlin

1. **Layout "full":**
   ```kotlin
   LazyColumn(
       modifier = Modifier.fillMaxWidth()
   ) {
       items(products) { product ->
           RProductCard(
               product = product,
               variant = RProductCard.Variant.Grid,
               modifier = Modifier
                   .fillMaxWidth()
                   .aspectRatio(0.5f)  // height = 2.0x width
           )
       }
   }
   ```

2. **Layout "compact":**
   ```kotlin
   LazyVerticalGrid(
       columns = GridCells.Fixed(2),
       modifier = Modifier.fillMaxWidth()
   ) {
       items(products) { product ->
           RProductCard(
               product = product,
               variant = RProductCard.Variant.Grid,
               modifier = Modifier
                   .fillMaxWidth()
                   .padding(horizontal = 4.dp)
           )
       }
   }
   ```

3. **Layout "horizontal":**
   ```kotlin
   LazyRow(
       modifier = Modifier.fillMaxWidth()
   ) {
       items(products) { product ->
           RProductCard(
               product = product,
               variant = RProductCard.Variant.List,
               modifier = Modifier
                   .width(LocalConfiguration.current.screenWidthDp.dp * 0.9f)
                   .height(140.dp)
           )
       }
   }
   ```

4. **Auto-scroll:**
   ```kotlin
   val listState = rememberLazyListState()
   var autoScrollJob: Job? = null
   
   LaunchedEffect(config?.autoPlay, config?.interval) {
       if (config?.autoPlay == true) {
           autoScrollJob = launch {
               while (true) {
                   delay(config.interval.toLong())
                   // Scroll automático
                   val currentIndex = listState.firstVisibleItemIndex
                   if (currentIndex < products.size - 1) {
                       listState.animateScrollToItem(currentIndex + 1)
                   } else {
                       listState.animateScrollToItem(0)
                   }
               }
           }
       } else {
           autoScrollJob?.cancel()
       }
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuUI/Components/RProductCarousel.swift` (líneas 200-500)

**Consideraciones importantes:**
- Layout "full": cards verticales, height = 2.0x width
- Layout "compact": 2 cards visibles, ~47% width cada uno
- Layout "horizontal": cards horizontales, 90% width, 140dp height
- Auto-scroll: pausar cuando usuario hace scroll manual, reanudar después de X segundos
- Cada card usa `RProductCard` con variant apropiado

---

## 16. Crear componente RProductStore con estructura base y carga de configuración desde CampaignManager

### Cómo funciona en Swift

Similar estructura a otros componentes:

```swift
// Sources/ReachuUI/Components/RProductStore.swift (líneas 1-100)
public struct RProductStore: View {
    private let componentId: String?
    
    @ObservedObject private var campaignManager = CampaignManager.shared
    @StateObject private var viewModel = RProductStoreViewModel()
    
    private var config: ProductStoreConfig? {
        guard let component = activeComponent,
              case .productStore(let config) = component.config else {
            return nil
        }
        return config
    }
    
    // Caching de config parseada
    @State private var cachedConfig: CachedConfig?
}
```

### Qué hacer en Kotlin

Similar a RProductBanner y RProductCarousel, pero con lógica de grid/list view.

**Archivos a revisar:**
- `Sources/ReachuUI/Components/RProductStore.swift` (líneas 1-100)
- Demo: `PregancyDemo/PregancyDemo/WeeksView.swift` (línea 126)

---

## 17. Implementar Grid y List views en RProductStore

### Cómo funciona en Swift

```swift
// Sources/ReachuUI/Components/RProductStore.swift (líneas 100-426)
if config.displayType == "grid" {
    LazyVGrid(
        columns: Array(repeating: GridItem(.flexible(), spacing: spacing), count: config.columns),
        spacing: spacing
    ) {
        ForEach(products) { product in
            RProductCard(product: product, variant: .grid)
        }
    }
} else {
    LazyVStack {
        ForEach(products) { product in
            RProductCard(product: product, variant: .list)
                .frame(height: 120)
        }
    }
}
```

### Qué hacer en Kotlin

1. **Grid view:**
   ```kotlin
   LazyVerticalGrid(
       columns = GridCells.Fixed(config.columns),
       modifier = Modifier.fillMaxWidth()
   ) {
       items(products) { product ->
           RProductCard(
               product = product,
               variant = RProductCard.Variant.Grid
           )
       }
   }
   ```

2. **List view:**
   ```kotlin
   LazyColumn {
       items(products) { product ->
           RProductCard(
               product = product,
               variant = RProductCard.Variant.List,
               modifier = Modifier.height(120.dp)
           )
       }
   }
   ```

**Archivos a revisar:**
- `Sources/ReachuUI/Components/RProductStore.swift` (líneas 100-426)

---

## 18-19. RProductSpotlight (similar a RProductBanner pero con badge highlight)

Seguir el mismo patrón que RProductBanner, pero:
- Usar `RProductCard` con variant especificado
- Agregar badge highlight si `highlightText` existe
- Badge en top-right corner del card

**Archivos a revisar:**
- `Sources/ReachuUI/Components/RProductSpotlight.swift`

---

## 20-22. Integración de localización en componentes UI

### Cómo funciona en Swift

Todos los strings hardcodeados se reemplazan con `RLocalizedString()`:

```swift
// Antes:
Text("Cart")

// Después:
Text(RLocalizedString(ReachuTranslationKey.cart.rawValue))
```

### Qué hacer en Kotlin

Reemplazar todos los `Text("...")` hardcodeados con `rLocalizedString()`:

```kotlin
// Antes:
Text("Cart")

// Después:
Text(rLocalizedString(ReachuTranslationKey.CART.key))
```

**Archivos a revisar:**
- `Sources/ReachuUI/Components/RCheckoutOverlay.swift` (~50+ strings)
- `Sources/ReachuUI/Components/RProductDetailOverlay.swift`
- `Sources/ReachuUI/Components/RFloatingCartIndicator.swift`
- `Sources/ReachuUI/Components/RProductCard.swift`
- `Sources/ReachuUI/Components/RProductSlider.swift`

---

## 23-24. Modelos de configuración

### Cómo funciona en Swift

Cada componente tiene su data class de configuración:

```swift
// Sources/ReachuCore/Models/OfferBannerModels.swift
public struct ProductBannerConfig: Codable {
    public let productId: String
    public let backgroundImageUrl: String
    public let title: String?
    public let subtitle: String?
    // ... más propiedades
}
```

### Qué hacer en Kotlin

Crear data classes equivalentes con `@Serializable`:

```kotlin
@Serializable
data class ProductBannerConfig(
    val productId: String,
    val backgroundImageUrl: String,
    val title: String? = null,
    val subtitle: String? = null,
    // ... más propiedades
)
```

**Archivos a revisar:**
- `Sources/ReachuCore/Models/OfferBannerModels.swift`

---

## 25. Component sealed class

### Cómo funciona en Swift

```swift
// Sources/ReachuCore/Models/CampaignModels.swift
public enum Component {
    case productBanner(id: String, type: String, isActive: Bool, config: ProductBannerConfig)
    case productCarousel(id: String, type: String, isActive: Bool, config: ProductCarouselConfig)
    // ...
}
```

### Qué hacer en Kotlin

```kotlin
sealed class Component {
    abstract val id: String
    abstract val type: String
    abstract val isActive: Boolean
    
    data class ProductBanner(
        override val id: String,
        override val type: String,
        override val isActive: Boolean,
        val config: ProductBannerConfig
    ) : Component()
    
    // Similar para otros tipos
}
```

---

## 26. Skeleton loaders

Crear composable `ShimmerEffect` y usarlo en cada componente mientras carga.

**Referencia:** Buscar `skeletonView` en `RProductBanner.swift`

---

## 27. Auto-hide de componentes

Ya implementado en `shouldShow` de cada componente. Verificar que todos los componentes lo implementen correctamente.

---

## 28. Soporte para componentId

Ya implementado en `getActiveComponent()`. Asegurar que todos los componentes acepten `componentId` como parámetro opcional.

---

## 29. Tests

Crear tests unitarios para:
- CampaignManager (fetch, cache, estados)
- Componentes (skeleton, contenido, auto-hide)
- Localización (carga, fallback, format strings)

---

## 30. Documentación

Documentar cada componente con:
- Uso básico
- Parámetros
- Configuración desde backend
- Ejemplos de código

**Referencia:** `docs/swift-sdk/client-implementation-guide.mdx` (líneas 633-982)

---

## Resumen General

### Patrones Comunes

1. **Observables:** Swift usa `@Published` y `@ObservedObject`, Kotlin usa `StateFlow` y `collectAsState()`
2. **Singleton:** Swift usa `static let shared`, Kotlin usa `object`
3. **Async/Await:** Ambos soportan, pero Kotlin usa coroutines
4. **JSON Parsing:** Swift usa `Codable`, Kotlin usa `kotlinx.serialization`
5. **UI Components:** Swift usa SwiftUI, Kotlin usa Jetpack Compose
6. **Cache:** Swift usa `UserDefaults`, Kotlin usa `SharedPreferences` o `DataStore`

### Orden de Implementación Recomendado

1. **Fase 1 - Core:** Tareas 1-4 (Localización)
2. **Fase 2 - Campaign Management:** Tareas 5-10 (CampaignManager, WebSocket, Cache)
3. **Fase 3 - Componentes Base:** Tareas 11-13 (RProductBanner)
4. **Fase 4 - Más Componentes:** Tareas 14-19 (RProductCarousel, RProductStore, RProductSpotlight)
5. **Fase 5 - Integración:** Tareas 20-22 (Localización en componentes)
6. **Fase 6 - Modelos:** Tareas 23-25 (Configs y Component sealed class)
7. **Fase 7 - Polish:** Tareas 26-30 (Skeletons, auto-hide, componentId, tests, docs)

### Referencias Clave

- **Swift SDK:** `/Users/angelo/ReachuSwiftSDK/Sources/`
- **Documentación:** `/Users/angelo/Reachu-documentation-v2/docs/swift-sdk/`
- **Demo:** `/Users/angelo/PregancyDemo/PregancyDemo/`

