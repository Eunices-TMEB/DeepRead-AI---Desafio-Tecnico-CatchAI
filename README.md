# 🧠 DeepRead AI - Desafío Técnico CatchAI

Un sistema avanzado de análisis conversacional de documentos PDF usando **Groq API** con **Llama 3.1 70B**, **ChromaDB** y **Streamlit**.

## ✨ Características

- 📄 **Carga múltiple de PDFs** (hasta 5 archivos, 200MB total)
- 🤖 **IA avanzada** con Groq + Llama 3.1 70B (súper rápido)
- 🔍 **Búsqueda semántica** con ChromaDB local
- 💬 **Chat conversacional** con contexto
- 📊 **Funciones extras**: resumen, comparación, clasificación
- 🎨 **Interfaz moderna** con Streamlit

## 🛠️ Stack Tecnológico

- **LLM**: Groq API + Llama 3.1 70B
- **Vector Store**: ChromaDB (local)
- **Embeddings**: SentenceTransformers
- **PDF Processing**: PyPDF2 + pdfplumber
- **Framework**: LangChain
- **Frontend**: Streamlit
- **Chunking**: RecursiveCharacterTextSplitter (1000 tokens, 100 overlap)

## 📦 Instalación

### 🐳 Opción 1: Con Docker (Recomendado para pruebas técnicas)

```bash
cd groq_system

# 1. Configurar API Key
cp env.example .env
# Editar .env y agregar: GROQ_API_KEY=gsk_tu_api_key_aqui

# 2. Ejecutar con script automático
./scripts/start.sh

# O manualmente:
docker-compose up --build -d
```

**Acceso:** http://localhost:8501

### 💻 Opción 2: Instalación Local

```bash
cd groq_system

# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar API Key
cp env.example .env
# Editar .env y agregar tu API key de Groq

# 3. Ejecutar aplicación
streamlit run main.py
```

### 🔑 Obtener API Key de Groq

1. Ve a https://console.groq.com/
2. Crea una cuenta gratuita
3. Genera tu API key
4. Pégala en el archivo `.env`

## 🎯 Uso

### 1. Subir Documentos
- Arrastra archivos PDF a la interfaz
- Máximo 5 archivos, 40MB cada uno
- El sistema extraerá y vectorizará el contenido

### 2. Hacer Preguntas
- Escribe preguntas en lenguaje natural
- El sistema buscará contexto relevante
- Recibirás respuestas basadas en tus documentos

### 3. Funciones Adicionales
- **📋 Resumen**: Genera resumen ejecutivo
- **🔍 Comparar**: Analiza similitudes y diferencias
- **🏷️ Clasificar**: Agrupa por temas

## 📁 Estructura del Proyecto

```
groq_system/
├── main.py                   # Interfaz principal Streamlit
├── requirements.txt          # Dependencias
├── env.example              # Configuración de ejemplo
├── README.md                # Este archivo
├── PRUEBA_TECNICA.md        # Documentación técnica completa
├── Dockerfile               # Imagen Docker optimizada
├── docker-compose.yml       # Orquestación de servicios
├── .dockerignore           # Optimización de build
├── src/
│   ├── __init__.py         # Módulo Python
│   ├── loader.py           # Carga y extracción de PDFs
│   ├── embedder.py         # Embeddings y ChromaDB
│   ├── chat.py             # Conversación con Groq
│   └── advanced_features.py # Funciones avanzadas
├── scripts/
│   ├── start.sh            # Script de inicio automático
│   └── stop.sh             # Script de parada
├── data/                   # Archivos temporales
├── chroma_db/              # Base de datos vectorial
└── logs/                   # Logs de aplicación
```

## ⚙️ Configuración Avanzada

### Variables de Entorno (`.env`)

```env
# API Key de Groq (REQUERIDO)
GROQ_API_KEY=gsk_tu_api_key_aqui

# Modelo de Groq
GROQ_MODEL=llama3-70b-8192

# Configuración de ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db
COLLECTION_NAME=pdf_documents

# Procesamiento de texto
CHUNK_SIZE=1000
CHUNK_OVERLAP=100

# Límites de archivos
MAX_FILE_SIZE_MB=40
MAX_TOTAL_SIZE_MB=200
MAX_FILES=5

# Interfaz Streamlit
PAGE_TITLE=CatchAI - Copiloto PDF
PAGE_ICON=📚
```

## 🚀 Características Avanzadas

### Arquitectura Modular
- **loader.py**: Manejo de PDFs con PyPDF2 y pdfplumber
- **embedder.py**: Vectorización con SentenceTransformers
- **chat.py**: Conversación inteligente con Groq

### Optimizaciones
- ✅ Chunking inteligente con solapamiento
- ✅ Embeddings locales eficientes
- ✅ Búsqueda semántica rápida
- ✅ Interfaz responsiva
- ✅ Gestión de memoria optimizada

### Funciones Inteligentes
- **RAG (Retrieval Augmented Generation)**: Respuestas basadas en contexto
- **Historial conversacional**: Mantiene contexto de la conversación
- **Análisis comparativo**: Encuentra similitudes y diferencias
- **Clasificación automática**: Agrupa documentos por temas

## 🐳 Docker Commands

### Comandos Básicos
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f catchai

# Parar servicios
docker-compose down

# Reconstruir imagen
docker-compose build --no-cache

# Limpiar todo (incluyendo volúmenes)
docker-compose down -v --remove-orphans
```

### Estado de Servicios
```bash
# Ver contenedores activos
docker-compose ps

# Verificar salud del servicio
docker-compose exec catchai curl http://localhost:8501/_stcore/health

# Acceder al contenedor
docker-compose exec catchai bash
```

### Persistencia de Datos
- **ChromaDB**: `./chroma_db/` (base de datos vectorial)
- **Datos de sesión**: `./data/` (archivos temporales)
- **Logs**: `./logs/` (registros de aplicación)

## 🔧 Solución de Problemas

### Error: "API key no configurada"
- Verifica que el archivo `.env` existe
- Confirma que `GROQ_API_KEY` tiene tu API key real
- Reinicia la aplicación

### Error: "No se puede extraer texto del PDF"
- El PDF podría ser una imagen escaneada
- Prueba con PDFs que contengan texto seleccionable
- Verifica que el archivo no esté corrupto

### Error: "Modelo no encontrado"
- Verifica que tienes acceso al modelo en Groq
- Prueba cambiando `GROQ_MODEL` a `llama3-8b-8192`

## 📊 Rendimiento

### Velocidad de Groq
- **Llama 3.1 70B**: ~800 tokens/segundo
- **Respuesta típica**: 2-4 segundos
- **Procesamiento PDF**: 1-3 segundos por archivo

### Uso de Memoria
- **Modelo embeddings**: ~500MB
- **ChromaDB**: Escala con documentos
- **Streamlit**: ~200MB base

## 🆚 Comparación con OpenAI

| Característica | CatchAI + Groq | OpenAI |
|---------------|----------------|---------|
| **Velocidad** | ⚡ Súper rápido | 🐌 Más lento |
| **Costo** | 💰 Muy barato | 💸 Más caro |
| **Límites** | 🔄 Generosos | ⚠️ Restrictivos |
| **Modelos** | 🦙 Llama 3.1 70B | 🤖 GPT-4 |
| **Privacidad** | 🔒 Respeta datos | ❓ Menos claro |


