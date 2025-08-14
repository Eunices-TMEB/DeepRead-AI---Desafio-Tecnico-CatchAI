#!/bin/bash

# Script de inicio rápido para CatchAI v2.0 con Docker
# Uso: ./scripts/start.sh

echo "🚀 Iniciando CatchAI v2.0 - Copiloto Conversacional con Groq"
echo "=============================================================="

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor, instala Docker primero."
    echo "   Visita: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor, instala Docker Compose primero."
    echo "   Visita: https://docs.docker.com/compose/install/"
    exit 1
fi

# Verificar si existe el archivo .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado. Creando desde env.example..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Archivo .env creado."
        echo ""
        echo "🔑 IMPORTANTE: Configura tu GROQ_API_KEY en el archivo .env"
        echo "   1. Ve a: https://console.groq.com/"
        echo "   2. Crea una cuenta gratuita"
        echo "   3. Genera tu API key"
        echo "   4. Edita .env y configura: GROQ_API_KEY=gsk_tu_api_key_aqui"
        echo ""
        read -p "¿Has configurado tu API key? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Por favor, configura tu API key antes de continuar."
            exit 1
        fi
    else
        echo "❌ Archivo env.example no encontrado."
        exit 1
    fi
fi

# Verificar si la API key está configurada
if grep -q "your_groq_api_key_here" .env; then
    echo "❌ API key de Groq no configurada."
    echo "   Por favor, edita el archivo .env y configura GROQ_API_KEY."
    echo "   Ejemplo: GROQ_API_KEY=gsk_tu_api_key_real_aqui"
    exit 1
fi

echo "✅ Configuración verificada correctamente"

# Crear directorios necesarios
mkdir -p chroma_db data logs

# Construir y levantar los servicios
echo "🔨 Construyendo imagen Docker..."
docker-compose build --no-cache

echo "🚀 Levantando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 20

# Verificar el estado de los servicios
echo "🔍 Verificando estado de los servicios..."

# Verificar CatchAI
echo "📊 Estado de contenedores:"
docker-compose ps

# Verificar logs
echo ""
echo "📋 Últimos logs:"
docker-compose logs --tail=10 catchai

# Verificar si el servicio está respondiendo
echo ""
echo "🌐 Verificando conectividad..."
if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ CatchAI funcionando en http://localhost:8501"
else
    echo "⚠️  CatchAI puede estar aún iniciando. Espera unos momentos más."
fi

echo ""
echo "🎉 ¡CatchAI v2.0 está ejecutándose!"
echo "📱 Accede a: http://localhost:8501"
echo ""
echo "🛠️  Comandos útiles:"
echo "   Ver logs:     docker-compose logs -f catchai"
echo "   Parar:        docker-compose down"
echo "   Reiniciar:    docker-compose restart"
echo "   Limpiar todo: docker-compose down -v --remove-orphans"
echo ""
echo "📚 Funcionalidades disponibles:"
echo "   • Subida de hasta 5 PDFs (200MB total)"
echo "   • Chat conversacional con Groq + Llama 3.1 70B"
echo "   • Búsqueda semántica con ChromaDB"
echo "   • Resumen automático de documentos"
echo "   • Comparación entre documentos"
echo "   • Clasificación por temas"
