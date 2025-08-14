"""
Módulo para generar embeddings y gestionar ChromaDB
"""

import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Optional
import streamlit as st
import uuid
import numpy as np
from datetime import datetime


class DocumentEmbedder:
    """Clase para generar embeddings y gestionar vectores en ChromaDB"""
    
    def __init__(
        self, 
        persist_directory: str = "./chroma_db",
        collection_name: str = "pdf_documents",
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 100
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Inicializar modelo de embeddings
        self._init_embedding_model(model_name)
        
        # Inicializar ChromaDB
        self._init_chroma_client()
        
        # Inicializar text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def _init_embedding_model(self, model_name: str):
        """Inicializar modelo de embeddings"""
        try:
            with st.spinner("Cargando modelo de embeddings..."):
                self.embedding_model = SentenceTransformer(model_name)
                self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
            st.success(f"✅ Modelo de embeddings cargado: {model_name}")
        except Exception as e:
            st.error(f"Error cargando modelo de embeddings: {str(e)}")
            raise
    
    def _init_chroma_client(self):
        """Inicializar cliente de ChromaDB"""
        try:
            # Crear directorio si no existe
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Configurar ChromaDB
            self.chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Obtener o crear colección
            try:
                self.collection = self.chroma_client.get_collection(name=self.collection_name)
                st.info(f"📂 Colección existente cargada: {self.collection_name}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "PDF documents embeddings"}
                )
                st.success(f"✨ Nueva colección creada: {self.collection_name}")
                
        except Exception as e:
            st.error(f"Error inicializando ChromaDB: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generar embeddings para una lista de textos"""
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            st.error(f"Error generando embeddings: {str(e)}")
            return []
    
    def split_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Dividir documentos en chunks"""
        chunks = []
        
        for doc in documents:
            # Dividir texto en chunks
            text_chunks = self.text_splitter.split_text(doc['content'])
            
            # Crear chunks con metadata
            for i, chunk_text in enumerate(text_chunks):
                if chunk_text.strip():  # Solo chunks no vacíos
                    chunk = {
                        'id': f"{doc['file_hash']}_{i}",
                        'content': chunk_text,
                        'source': doc['filename'],
                        'chunk_index': i,
                        'total_chunks': len(text_chunks),
                        'metadata': {
                            **doc['metadata'],
                            'chunk_index': i,
                            'total_chunks': len(text_chunks),
                            'chunk_size': len(chunk_text),
                            'timestamp': datetime.now().isoformat()
                        }
                    }
                    chunks.append(chunk)
        
        return chunks
    
    def add_documents_to_vectorstore(self, documents: List[Dict[str, Any]]) -> bool:
        """Agregar documentos a la base de datos vectorial"""
        try:
            # Dividir en chunks
            with st.spinner("Dividiendo documentos en chunks..."):
                chunks = self.split_documents(documents)
            
            if not chunks:
                st.warning("No se generaron chunks válidos")
                return False
            
            st.info(f"📝 Generados {len(chunks)} chunks de texto")
            
            # Verificar si algunos chunks ya existen
            existing_ids = set()
            try:
                existing_data = self.collection.get()
                existing_ids = set(existing_data['ids'])
            except:
                pass
            
            # Filtrar chunks nuevos
            new_chunks = [chunk for chunk in chunks if chunk['id'] not in existing_ids]
            
            if not new_chunks:
                st.info("Todos los documentos ya están en la base de datos")
                return True
            
            st.info(f"📥 Agregando {len(new_chunks)} chunks nuevos...")
            
            # Extraer datos para ChromaDB
            chunk_ids = [chunk['id'] for chunk in new_chunks]
            chunk_texts = [chunk['content'] for chunk in new_chunks]
            chunk_metadatas = [chunk['metadata'] for chunk in new_chunks]
            
            # Generar embeddings
            with st.spinner("Generando embeddings..."):
                embeddings = self.generate_embeddings(chunk_texts)
            
            if not embeddings:
                st.error("No se pudieron generar embeddings")
                return False
            
            # Agregar a ChromaDB
            with st.spinner("Almacenando en base de datos vectorial..."):
                self.collection.add(
                    ids=chunk_ids,
                    embeddings=embeddings,
                    documents=chunk_texts,
                    metadatas=chunk_metadatas
                )
            
            st.success(f"✅ {len(new_chunks)} chunks almacenados exitosamente")
            return True
            
        except Exception as e:
            st.error(f"Error agregando documentos: {str(e)}")
            return False
    
    def search_similar_chunks(
        self, 
        query: str, 
        n_results: int = 5,
        where_filter: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Buscar chunks similares a una consulta"""
        try:
            # Generar embedding de la consulta
            query_embedding = self.generate_embeddings([query])
            
            if not query_embedding:
                return {'documents': [], 'metadatas': [], 'distances': []}
            
            # Buscar en ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=where_filter
            )
            
            return results
            
        except Exception as e:
            st.error(f"Error en búsqueda: {str(e)}")
            return {'documents': [], 'metadatas': [], 'distances': []}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la colección"""
        try:
            # Obtener datos de la colección
            data = self.collection.get()
            
            if not data['ids']:
                return {
                    'total_chunks': 0,
                    'unique_documents': 0,
                    'collection_name': self.collection_name
                }
            
            # Extraer fuentes únicas
            sources = set()
            for metadata in data['metadatas']:
                if 'source' in metadata:
                    sources.add(metadata['source'])
            
            return {
                'total_chunks': len(data['ids']),
                'unique_documents': len(sources),
                'sources': list(sources),
                'collection_name': self.collection_name,
                'embedding_dimension': self.embedding_dimension
            }
            
        except Exception as e:
            st.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}
    
    def clear_collection(self) -> bool:
        """Limpiar toda la colección"""
        try:
            # Obtener todos los IDs
            data = self.collection.get()
            
            if data['ids']:
                # Eliminar todos los documentos
                self.collection.delete(ids=data['ids'])
                st.success("🗑️ Colección limpiada exitosamente")
            else:
                st.info("La colección ya está vacía")
            
            return True
            
        except Exception as e:
            st.error(f"Error limpiando colección: {str(e)}")
            return False
    
    def delete_document_by_source(self, source: str) -> bool:
        """Eliminar todos los chunks de un documento específico"""
        try:
            # Buscar chunks del documento
            results = self.collection.get(where={"source": source})
            
            if results['ids']:
                # Eliminar chunks encontrados
                self.collection.delete(ids=results['ids'])
                st.success(f"🗑️ Eliminado documento: {source}")
                return True
            else:
                st.warning(f"No se encontraron chunks para: {source}")
                return False
                
        except Exception as e:
            st.error(f"Error eliminando documento: {str(e)}")
            return False
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Obtener un chunk específico por ID"""
        try:
            result = self.collection.get(ids=[chunk_id])
            
            if result['ids']:
                return {
                    'id': result['ids'][0],
                    'content': result['documents'][0],
                    'metadata': result['metadatas'][0]
                }
            return None
            
        except Exception as e:
            st.error(f"Error obteniendo chunk: {str(e)}")
            return None


def create_embedder_from_config() -> DocumentEmbedder:
    """Crear embedder usando configuración del entorno"""
    persist_dir = os.getenv('CHROMA_PERSIST_DIRECTORY', './chroma_db')
    collection_name = os.getenv('COLLECTION_NAME', 'pdf_documents')
    chunk_size = int(os.getenv('CHUNK_SIZE', 1000))
    chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 100))
    
    return DocumentEmbedder(
        persist_directory=persist_dir,
        collection_name=collection_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
