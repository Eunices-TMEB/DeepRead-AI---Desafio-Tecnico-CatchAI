#!/bin/bash

# Script para detener CatchAI v2.0
# Uso: ./scripts/stop.sh

echo "🛑 Deteniendo CatchAI v2.0..."

# Detener y remover contenedores
docker-compose down

echo "✅ Servicios detenidos correctamente"
echo ""
echo "🛠️  Opciones adicionales:"
echo "   Limpiar todo:           docker-compose down -v --remove-orphans"
echo "   Limpiar imágenes:       docker system prune -f"
echo "   Ver contenedores:       docker ps -a"
