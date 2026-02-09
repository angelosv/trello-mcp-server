#!/usr/bin/env python3
"""
Analiza el SDK de Kotlin para ver qué tiene implementado relacionado con Engagement.
"""
import os
import subprocess
import json

KOTLIN_SDK_PATH = "/Users/angelo/Documents/GitHub/ReachuKotlinSDK"

def check_module_exists(module_name):
    """Verifica si un módulo existe en el SDK."""
    module_path = os.path.join(KOTLIN_SDK_PATH, "library/io/reachu", module_name)
    return os.path.exists(module_path)

def find_files_with_pattern(pattern, directory):
    """Busca archivos que contengan un patrón."""
    result = subprocess.run(
        ["grep", "-r", "-l", pattern, directory],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def analyze_kotlin_sdk():
    """Analiza el SDK de Kotlin."""
    print("="*80)
    print("ANÁLISIS DEL SDK DE KOTLIN")
    print("="*80)
    
    # Verificar módulos existentes
    print("\n📦 Módulos existentes en el SDK:")
    modules = [
        "ReachuCore",
        "ReachuDesignSystem",
        "ReachuLiveShow",
        "ReachuLiveUI",
        "ReachuNetwork",
        "ReachuUI",
        "ReachuTesting",
        "ReachuEngagementSystem",
        "ReachuEngagementUI"
    ]
    
    for module in modules:
        exists = check_module_exists(module)
        status = "✓" if exists else "✗"
        print(f"   {status} {module}")
    
    # Buscar referencias a Engagement
    print("\n🔍 Buscando referencias a Engagement/Poll/Contest:")
    library_path = os.path.join(KOTLIN_SDK_PATH, "library")
    
    patterns = ["Engagement", "Poll", "Contest", "engagement", "poll", "contest"]
    found_files = []
    for pattern in patterns:
        files = find_files_with_pattern(pattern, library_path)
        found_files.extend(files)
    
    if found_files:
        unique_files = list(set(found_files))
        print(f"   Encontrados {len(unique_files)} archivo(s) con referencias:")
        for file in unique_files[:10]:  # Mostrar solo los primeros 10
            rel_path = os.path.relpath(file, KOTLIN_SDK_PATH)
            print(f"     - {rel_path}")
        if len(unique_files) > 10:
            print(f"     ... y {len(unique_files) - 10} más")
    else:
        print("   ✗ No se encontraron referencias a Engagement/Poll/Contest")
    
    # Verificar estructura de directorios
    print("\n📁 Estructura de directorios principales:")
    library_io_reachu = os.path.join(KOTLIN_SDK_PATH, "library/io/reachu")
    if os.path.exists(library_io_reachu):
        dirs = [d for d in os.listdir(library_io_reachu) 
                if os.path.isdir(os.path.join(library_io_reachu, d))]
        for dir_name in sorted(dirs):
            print(f"   - {dir_name}")
    
    print("\n" + "="*80)
    print("CONCLUSIÓN")
    print("="*80)
    
    engagement_exists = check_module_exists("ReachuEngagementSystem")
    engagement_ui_exists = check_module_exists("ReachuEngagementUI")
    
    if not engagement_exists and not engagement_ui_exists:
        print("\n⚠️  Los módulos ReachuEngagementSystem y ReachuEngagementUI NO existen")
        print("   Esto confirma que el desarrollador aún no ha comenzado a implementarlos")
        print("   Las tarjetas en 'Doing' están pendientes de implementación")
    else:
        print("\n✓ Se encontraron módulos de Engagement")
        if engagement_exists:
            print("   - ReachuEngagementSystem existe")
        if engagement_ui_exists:
            print("   - ReachuEngagementUI existe")

if __name__ == "__main__":
    analyze_kotlin_sdk()
