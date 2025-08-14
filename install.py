#!/usr/bin/env python3
"""
Script de instalación robusta para DeepRead AI
Maneja diferentes versiones de Python y sistemas operativos
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    
    if version.minor >= 12:
        print("⚠️ Python 3.12+ detectado, usando instalación compatible")
        return "modern"
    
    return True

def install_package(package, fallback=None):
    """Instalar paquete con fallback"""
    try:
        print(f"📦 Instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        if fallback:
            print(f"⚠️ Falló {package}, probando {fallback}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", fallback])
                return True
            except subprocess.CalledProcessError:
                print(f"❌ Falló instalando {package} y {fallback}")
                return False
        return False

def install_dependencies():
    """Instalar dependencias de manera robusta"""
    
    python_check = check_python_version()
    if not python_check:
        return False
    
    # Actualizar pip primero
    print("🔄 Actualizando pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    except:
        print("⚠️ No se pudo actualizar pip, continuando...")
    
    # Lista de paquetes esenciales con fallbacks
    essential_packages = [
        ("streamlit>=1.28.0", "streamlit"),
        ("groq>=0.4.0", "groq"),
        ("python-dotenv>=1.0.0", "python-dotenv"),
        ("PyPDF2>=3.0.0", "PyPDF2"),
        ("pdfplumber>=0.10.0", "pdfplumber"),
        ("pandas>=2.0.0", "pandas"),
        ("plotly>=5.0.0", "plotly"),
    ]
    
    # Paquetes que pueden requerir compilación
    complex_packages = [
        ("chromadb>=0.4.0", "chromadb"),
        ("sentence-transformers>=2.0.0", "sentence-transformers"),
        ("langchain>=0.1.0", "langchain"),
        ("langchain-community>=0.0.10", "langchain-community"),
        ("langchain-text-splitters>=0.0.1", "langchain-text-splitters"),
    ]
    
    if python_check == "modern":
        # Para Python 3.12+, instalar versiones más flexibles
        numpy_package = "numpy"
        matplotlib_package = "matplotlib"
        networkx_package = "networkx"
    else:
        numpy_package = "numpy>=1.21.0"
        matplotlib_package = "matplotlib>=3.5.0"
        networkx_package = "networkx>=3.0.0"
    
    # Instalar paquetes esenciales
    print("📦 Instalando paquetes esenciales...")
    for package, fallback in essential_packages:
        if not install_package(package, fallback):
            print(f"❌ Error crítico instalando {package}")
            return False
    
    # Instalar numpy separadamente (problemático en 3.12+)
    print("🔢 Instalando numpy...")
    if not install_package(numpy_package):
        print("❌ Error instalando numpy")
        return False
    
    # Instalar matplotlib
    print("📊 Instalando matplotlib...")
    if not install_package(matplotlib_package):
        print("⚠️ matplotlib falló, pero no es crítico")
    
    # Instalar networkx
    print("🕸️ Instalando networkx...")
    if not install_package(networkx_package):
        print("⚠️ networkx falló, pero no es crítico")
    
    # Instalar paquetes complejos
    print("🧠 Instalando paquetes de IA...")
    for package, fallback in complex_packages:
        if not install_package(package, fallback):
            print(f"⚠️ {package} falló, pero continuando...")
    
    return True

def verify_installation():
    """Verificar que la instalación funcionó"""
    print("🧪 Verificando instalación...")
    
    required_modules = [
        "streamlit",
        "groq", 
        "dotenv",
        "PyPDF2",
        "pdfplumber",
        "pandas",
        "plotly"
    ]
    
    optional_modules = [
        "chromadb",
        "sentence_transformers",
        "langchain",
        "numpy",
        "matplotlib",
        "networkx"
    ]
    
    # Verificar módulos requeridos
    missing_required = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_required.append(module)
            print(f"❌ {module}")
    
    # Verificar módulos opcionales
    missing_optional = []
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_optional.append(module)
            print(f"⚠️ {module} (opcional)")
    
    if missing_required:
        print(f"\n❌ Faltan módulos críticos: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️ Módulos opcionales faltantes: {', '.join(missing_optional)}")
        print("La aplicación funcionará pero algunas funciones pueden estar limitadas")
    
    print("\n✅ Instalación verificada exitosamente")
    return True

def create_env_file():
    """Crear archivo .env si no existe"""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            print("📝 Creando archivo .env...")
            with open('env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ Archivo .env creado")
            print("🔑 IMPORTANTE: Edita .env y agrega tu GROQ_API_KEY")
            print("   Obtén tu API key gratuita en: https://groq.com")
        else:
            print("⚠️ env.example no encontrado")

def main():
    """Función principal"""
    print("🚀 INSTALACIÓN DE DEEPREAD AI")
    print("=" * 40)
    
    if not install_dependencies():
        print("\n❌ Instalación falló")
        sys.exit(1)
    
    if not verify_installation():
        print("\n⚠️ Instalación incompleta pero funcional")
    
    create_env_file()
    
    print("\n🎉 INSTALACIÓN COMPLETADA")
    print("=" * 40)
    print("📝 Próximos pasos:")
    print("1. Edita .env y agrega tu GROQ_API_KEY")
    print("2. Ejecuta: streamlit run main.py")
    print("3. Abre: http://localhost:8501")
    print("\n🏆 ¡DeepRead AI está listo para usar!")

if __name__ == "__main__":
    main()
