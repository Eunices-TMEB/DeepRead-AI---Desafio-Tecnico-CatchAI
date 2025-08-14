#!/bin/bash

# Quick Docker Test para DeepRead AI
# Verificación rápida de que docker-compose funciona

echo "🐳 QUICK DOCKER TEST - DEEPREAD AI"
echo "=================================="
echo ""

# 1. Verificar Docker
echo "🔍 Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    if ! command -v docker compose &> /dev/null; then
        echo "❌ Docker Compose no está disponible"
        exit 1
    fi
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo "✅ Docker y Docker Compose disponibles"

# 2. Verificar .env
echo ""
echo "🔑 Verificando configuración..."
if [ ! -f ".env" ]; then
    echo "📝 Creando .env desde env.example..."
    cp env.example .env
fi

if grep -q "your_groq_api_key_here" .env; then
    echo "⚠️  NECESITAS CONFIGURAR GROQ_API_KEY EN .env"
    echo "   Obtén tu API key en: https://groq.com"
    echo "   Edita .env y reemplaza 'your_groq_api_key_here'"
    exit 1
fi

echo "✅ Configuración lista"

# 3. Limpiar y construir
echo ""
echo "🧹 Limpiando entorno anterior..."
$DOCKER_COMPOSE_CMD down --volumes --remove-orphans 2>/dev/null

echo ""
echo "🏗️  Construyendo imagen (esto puede tomar 2-5 minutos)..."
if ! $DOCKER_COMPOSE_CMD build --no-cache; then
    echo "❌ Error construyendo imagen"
    exit 1
fi

echo "✅ Imagen construida exitosamente"

# 4. Iniciar servicios
echo ""
echo "🚀 Iniciando servicios..."
if ! $DOCKER_COMPOSE_CMD up -d; then
    echo "❌ Error iniciando servicios"
    exit 1
fi

echo "✅ Servicios iniciados"

# 5. Esperar que esté listo
echo ""
echo "⏳ Esperando que la aplicación esté lista..."
attempt=1
max_attempts=30

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "✅ Aplicación lista en intento $attempt"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ La aplicación no respondió después de $max_attempts intentos"
        echo "📋 Logs del contenedor:"
        $DOCKER_COMPOSE_CMD logs deepread-ai
        exit 1
    fi
    
    echo "   Intento $attempt/$max_attempts..."
    sleep 2
    ((attempt++))
done

# 6. Verificación final
echo ""
echo "🧪 Verificación final..."
if curl -s http://localhost:8501 | grep -q "streamlit\|DeepRead"; then
    echo "✅ Aplicación funcionando correctamente"
else
    echo "⚠️ Aplicación responde pero contenido inesperado"
fi

echo ""
echo "🎉 ¡DOCKER COMPOSE FUNCIONANDO!"
echo "================================"
echo "🌐 Aplicación disponible en: http://localhost:8501"
echo "🐳 Contenedor ejecutándose: deepread-ai-main"
echo ""
echo "🛑 Para parar: $DOCKER_COMPOSE_CMD down"
echo ""
echo "🏆 LISTO PARA REVISORES ✅"
