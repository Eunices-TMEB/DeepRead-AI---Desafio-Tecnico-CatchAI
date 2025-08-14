# Dockerfile para DeepRead AI - Desafío Técnico CatchAI
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias (con fallback)
COPY requirements.txt .
COPY requirements_simple.txt ./requirements_simple.txt

# Actualizar pip e instalar wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instalar dependencias con fallback robusto
RUN pip install --no-cache-dir -r requirements.txt || \
    pip install --no-cache-dir -r requirements_simple.txt || \
    (pip install streamlit groq python-dotenv PyPDF2 pdfplumber pandas plotly && \
     pip install chromadb sentence-transformers langchain --no-deps)

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p data chroma_db logs

# Configurar variables de entorno por defecto
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Exponer puerto
EXPOSE 8501

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
