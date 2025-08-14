"""
Módulo para cargar y extraer texto de documentos PDF
"""

import os
import PyPDF2
import pdfplumber
from typing import List, Dict, Any, Optional
import streamlit as st
from io import BytesIO
import hashlib
import tempfile


class PDFLoader:
    """Clase para cargar y procesar documentos PDF"""
    
    def __init__(self, max_file_size_mb: int = 40, max_total_size_mb: int = 200, max_files: int = 5):
        self.max_file_size_mb = max_file_size_mb
        self.max_total_size_mb = max_total_size_mb
        self.max_files = max_files
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.max_total_size_bytes = max_total_size_mb * 1024 * 1024
    
    def validate_files(self, files: List[Any]) -> tuple[bool, str]:
        """Validar archivos subidos"""
        if not files:
            return False, "No se han subido archivos"
        
        if len(files) > self.max_files:
            return False, f"Máximo {self.max_files} archivos permitidos"
        
        total_size = 0
        for file in files:
            # Verificar extensión
            if not file.name.lower().endswith('.pdf'):
                return False, f"El archivo '{file.name}' no es un PDF válido"
            
            # Verificar tamaño individual
            file_size = len(file.getvalue())
            if file_size > self.max_file_size_bytes:
                return False, f"El archivo '{file.name}' excede el tamaño máximo de {self.max_file_size_mb}MB"
            
            total_size += file_size
        
        # Verificar tamaño total
        if total_size > self.max_total_size_bytes:
            return False, f"El tamaño total excede el máximo de {self.max_total_size_mb}MB"
        
        return True, "Archivos válidos"
    
    def extract_text_pypdf2(self, pdf_content: bytes) -> str:
        """Extraer texto usando PyPDF2"""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            
            return text.strip()
        except Exception as e:
            st.error(f"Error con PyPDF2: {str(e)}")
            return ""
    
    def extract_text_pdfplumber(self, pdf_content: bytes) -> str:
        """Extraer texto usando pdfplumber (mejor para PDFs complejos)"""
        try:
            with pdfplumber.open(BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                
                return text.strip()
        except Exception as e:
            st.error(f"Error con pdfplumber: {str(e)}")
            return ""
    
    def extract_text_from_pdf(self, pdf_content: bytes, filename: str) -> str:
        """Extraer texto de PDF usando múltiples métodos"""
        
        # Intentar primero con pdfplumber (mejor para PDFs complejos)
        text = self.extract_text_pdfplumber(pdf_content)
        
        # Si pdfplumber no funciona bien, intentar con PyPDF2
        if not text or len(text) < 100:
            text = self.extract_text_pypdf2(pdf_content)
        
        # Si aún no hay texto suficiente, mostrar advertencia
        if not text:
            st.warning(f"No se pudo extraer texto del archivo '{filename}'. El PDF podría ser una imagen escaneada.")
            return f"[Archivo: {filename} - No se pudo extraer texto]"
        
        if len(text) < 50:
            st.warning(f"Se extrajo muy poco texto del archivo '{filename}'. Verifica que no sea una imagen escaneada.")
        
        return text
    
    def generate_file_hash(self, content: bytes) -> str:
        """Generar hash único para el archivo"""
        return hashlib.md5(content).hexdigest()
    
    def load_documents(self, uploaded_files: List[Any]) -> List[Dict[str, Any]]:
        """Cargar y procesar múltiples documentos PDF"""
        
        # Validar archivos
        is_valid, message = self.validate_files(uploaded_files)
        if not is_valid:
            st.error(message)
            return []
        
        documents = []
        
        # Procesar cada archivo
        for file in uploaded_files:
            with st.spinner(f"Procesando {file.name}..."):
                
                # Leer contenido
                content = file.getvalue()
                file_hash = self.generate_file_hash(content)
                
                # Extraer texto
                text = self.extract_text_from_pdf(content, file.name)
                
                if text and len(text.strip()) > 0:
                    # Crear documento
                    document = {
                        'filename': file.name,
                        'content': text,
                        'file_hash': file_hash,
                        'file_size': len(content),
                        'word_count': len(text.split()),
                        'char_count': len(text),
                        'metadata': {
                            'source': file.name,
                            'type': 'pdf',
                            'hash': file_hash
                        }
                    }
                    
                    documents.append(document)
                    st.success(f"✅ {file.name}: {document['word_count']} palabras extraídas")
                else:
                    st.error(f"❌ No se pudo procesar {file.name}")
        
        if documents:
            total_words = sum(doc['word_count'] for doc in documents)
            st.info(f"📊 **Total procesado:** {len(documents)} archivos, {total_words:,} palabras")
        
        return documents
    
    def get_document_stats(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Obtener estadísticas de los documentos cargados"""
        if not documents:
            return {}
        
        total_files = len(documents)
        total_words = sum(doc['word_count'] for doc in documents)
        total_chars = sum(doc['char_count'] for doc in documents)
        total_size = sum(doc['file_size'] for doc in documents)
        
        avg_words = total_words / total_files if total_files > 0 else 0
        
        return {
            'total_files': total_files,
            'total_words': total_words,
            'total_characters': total_chars,
            'total_size_mb': total_size / (1024 * 1024),
            'average_words_per_file': avg_words,
            'filenames': [doc['filename'] for doc in documents]
        }


def create_sample_document() -> Dict[str, Any]:
    """Crear un documento de ejemplo para pruebas"""
    sample_text = """
    Este es un documento de ejemplo para probar el sistema CatchAI.
    
    El sistema permite:
    1. Subir documentos PDF
    2. Extraer texto automáticamente
    3. Hacer preguntas en lenguaje natural
    4. Obtener respuestas contextuales
    
    Características principales:
    - Procesamiento inteligente de documentos
    - Búsqueda semántica avanzada
    - Interfaz conversacional intuitiva
    - Respuestas basadas en el contenido real
    
    Este documento contiene información de prueba para demostrar
    las capacidades del sistema de análisis de documentos.
    """
    
    return {
        'filename': 'documento_ejemplo.pdf',
        'content': sample_text.strip(),
        'file_hash': 'example_hash_123',
        'file_size': len(sample_text.encode()),
        'word_count': len(sample_text.split()),
        'char_count': len(sample_text),
        'metadata': {
            'source': 'documento_ejemplo.pdf',
            'type': 'pdf',
            'hash': 'example_hash_123'
        }
    }
