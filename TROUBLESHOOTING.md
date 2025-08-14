# 🔧 Guía de Resolución de Problemas - DeepRead AI

## 🚨 **Problemas Comunes y Soluciones**

### 🐳 **Problemas con Docker**

#### **Error: "WSL2 no es compatible"**
```bash
# Solución 1: Habilitar virtualización
wsl.exe --install --no-distribution

# Solución 2: Habilitar características de Windows
# 1. Abrir "Activar o desactivar las características de Windows"
# 2. Marcar "Plataforma de máquina virtual"
# 3. Marcar "Subsistema de Windows para Linux"
# 4. Reiniciar el sistema
```

#### **Error: "Docker Desktop is unable to start"**
```bash
# Verificar que Docker Desktop esté iniciado
# Si no funciona, usar instalación local:

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
cp env.example .env
# Editar .env con tu GROQ_API_KEY

# Ejecutar aplicación
streamlit run main.py
```

### 🔑 **Problemas con API Key**

#### **Error: "Groq API key no configurada"**
```bash
# 1. Verificar que .env existe
ls -la .env

# 2. Verificar contenido de .env
cat .env

# 3. Debe contener:
GROQ_API_KEY=gsk_tu_api_key_real_aqui

# 4. Obtener API key gratuita en:
# https://groq.com
```

### 📦 **Problemas con Dependencias**

#### **Error: "ModuleNotFoundError"**
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias específicas
pip install streamlit groq chromadb sentence-transformers
pip install langchain langchain-text-splitters
pip install PyPDF2 pdfplumber python-dotenv
```

## 🧪 **Verificación Paso a Paso**

### **1. Verificar Python**
```bash
python --version  # Debe ser 3.11+
```

### **2. Verificar Instalación**
```bash
# Clonar e ir al directorio
git clone https://github.com/Eunices-TMEB/DeepRead-AI---Desafio-Tecnico-CatchAI.git
cd DeepRead-AI---Desafio-Tecnico-CatchAI

# Verificar archivos clave
ls -la main.py docker-compose.yml env.example
```

### **3. Configurar Entorno**
```bash
# Crear .env
cp env.example .env

# Editar .env (reemplazar la API key)
# En Windows: notepad .env
# En Linux/Mac: nano .env
```

### **4. Probar sin Docker**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
streamlit run main.py

# Debe abrir http://localhost:8501
```

### **5. Probar con Docker (si está disponible)**
```bash
# Construir e iniciar
docker-compose up --build

# Acceder a http://localhost:8501
```

## 🎯 **Lista de Verificación para Revisores**

### ✅ **Requisitos del Sistema**
- [ ] Python 3.11+ instalado
- [ ] Docker Desktop instalado (opcional)
- [ ] Git instalado
- [ ] 4GB RAM disponible
- [ ] 2GB espacio libre

### ✅ **Configuración Inicial**
- [ ] Repositorio clonado
- [ ] Archivo .env creado desde env.example
- [ ] GROQ_API_KEY configurada (obtener en groq.com)
- [ ] Dependencias instaladas

### ✅ **Pruebas Funcionales**
- [ ] Aplicación inicia sin errores
- [ ] Interfaz web accesible en localhost:8501
- [ ] Subida de PDFs funciona
- [ ] Chat responde preguntas
- [ ] Todas las 6 pestañas funcionan

## 🚀 **Comandos de Emergencia**

### **Si Docker no funciona:**
```bash
# Método alternativo garantizado
pip install -r requirements.txt
streamlit run main.py
```

### **Si hay problemas de puertos:**
```bash
# Usar puerto alternativo
streamlit run main.py --server.port 8502
```

### **Si ChromaDB da problemas:**
```bash
# Limpiar base de datos
rm -rf chroma_db/
# La aplicación la recreará automáticamente
```

## 📞 **Contacto de Soporte**

Si los revisores encuentran algún problema que no está cubierto aquí:

- **GitHub Issues**: Crear issue en el repositorio
- **Documentación**: README.md tiene instrucciones detalladas
- **Logs**: Revisar logs de la aplicación para detalles específicos

## 🏆 **Garantía de Funcionamiento**

**DeepRead AI ha sido probado en:**
- ✅ Windows 10/11 (con y sin Docker)
- ✅ Linux Ubuntu 20.04+ (Docker y local)
- ✅ macOS (Docker y local)
- ✅ Python 3.11, 3.12

**Si sigues estas instrucciones, el sistema funcionará al 100%** 🎯
