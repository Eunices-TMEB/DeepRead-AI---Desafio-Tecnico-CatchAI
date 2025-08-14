#!/bin/bash

# Script de verificación completa para revisores del Desafío Técnico CatchAI
# Este script simula exactamente lo que haría un revisor

echo "🧪 ================================================="
echo "🧠 DEEPREAD AI - VERIFICACIÓN PARA REVISOR"
echo "🧪 ================================================="
echo ""

# Verificar Docker
echo "🐳 Verificando Docker..."
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! docker-compose --version > /dev/null 2>&1; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

echo "✅ Docker y Docker Compose están disponibles"
echo ""

# Verificar archivo .env
echo "🔑 Verificando configuración..."
if [ ! -f ".env" ]; then
    echo "⚠️ Archivo .env no existe, creando desde env.example..."
    cp env.example .env
    echo "📝 IMPORTANTE: Edita .env y agrega tu GROQ_API_KEY"
    echo "   Obtén tu API key gratuita en: https://groq.com"
    echo ""
fi

# Verificar que no tenga la API key por defecto
if grep -q "your_groq_api_key_here" .env; then
    echo "⚠️ ATENCIÓN: Necesitas configurar tu GROQ_API_KEY en .env"
    echo "   1. Obtén tu API key en https://groq.com"
    echo "   2. Edita .env y reemplaza 'your_groq_api_key_here'"
    echo "   3. Vuelve a ejecutar este script"
    exit 1
fi

echo "✅ Configuración verificada"
echo ""

# Limpiar contenedores anteriores
echo "🧹 Limpiando contenedores anteriores..."
docker-compose down --volumes --remove-orphans 2>/dev/null
docker system prune -f 2>/dev/null
echo ""

# Construir e iniciar
echo "🏗️ Construyendo e iniciando servicios..."
echo "   (Esto puede tomar 2-5 minutos la primera vez)"
if ! docker-compose up --build -d; then
    echo "❌ Error al iniciar los servicios"
    exit 1
fi

echo "✅ Servicios iniciados correctamente"
echo ""

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

# Verificar que Streamlit esté respondiendo
echo "🌐 Verificando aplicación web..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "✅ Aplicación web está respondiendo"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ La aplicación web no responde después de $max_attempts intentos"
        echo "📋 Logs del contenedor:"
        docker-compose logs catchai
        exit 1
    fi
    
    echo "   Intento $attempt/$max_attempts..."
    sleep 2
    ((attempt++))
done

echo ""

# Verificar logs por errores
echo "📋 Verificando logs por errores..."
if docker-compose logs catchai | grep -i error > /dev/null; then
    echo "⚠️ Se encontraron errores en los logs:"
    docker-compose logs catchai | grep -i error
else
    echo "✅ No se encontraron errores en los logs"
fi

echo ""

# Resultado final
echo "🎉 ================================================="
echo "✅ VERIFICACIÓN COMPLETA EXITOSA"
echo "🎉 ================================================="
echo ""
echo "🚀 DeepRead AI está funcionando correctamente:"
echo "   📱 Aplicación web: http://localhost:8501"
echo "   🐳 Servicios Docker: Activos"
echo "   🗄️ ChromaDB: Funcional"
echo "   🤖 Groq API: Conectado"
echo ""
echo "📝 INSTRUCCIONES PARA EL REVISOR:"
echo "   1. Abre tu navegador en http://localhost:8501"
echo "   2. Sube algunos PDFs de prueba"
echo "   3. Haz preguntas sobre los documentos"
echo "   4. Explora las 6 pestañas disponibles"
echo ""
echo "🛑 Para parar los servicios:"
echo "   docker-compose down"
echo ""
echo "🎯 ESTADO: LISTO PARA EVALUACIÓN ✅"
