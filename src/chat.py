"""
Módulo para manejar conversaciones con Groq API
"""

import os
from groq import Groq
from typing import List, Dict, Any, Optional
import streamlit as st
from datetime import datetime
import json


class ChatManager:
    """Clase para manejar conversaciones con Groq API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3-70b-8192",
        temperature: float = 0.3,
        max_tokens: int = 2048
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Inicializar cliente de Groq
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key or self.api_key == 'your_groq_api_key_here':
            st.error("🔑 API key de Groq no configurada. Por favor, configura GROQ_API_KEY en el archivo .env")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=self.api_key)
                st.success("✅ Cliente de Groq inicializado correctamente")
            except Exception as e:
                st.error(f"Error inicializando Groq: {str(e)}")
                self.client = None
        
        # Historial de conversación
        self.conversation_history = []
    
    def create_context_prompt(
        self, 
        user_question: str, 
        relevant_chunks: List[str],
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Crear prompt con contexto para RAG"""
        
        # Preparar contexto de documentos
        if relevant_chunks:
            context = "\n".join([f"[Fragmento {i+1}]\n{chunk}" for i, chunk in enumerate(relevant_chunks)])
        else:
            context = "No se encontraron documentos relevantes."
        
        # Preparar historial de conversación
        history_str = ""
        if conversation_history:
            recent_history = conversation_history[-3:]  # Solo las últimas 3 interacciones
            for item in recent_history:
                if item['role'] == 'user':
                    history_str += f"Usuario: {item['content']}\n"
                elif item['role'] == 'assistant':
                    history_str += f"Asistente: {item['content']}\n"
        
        # Crear prompt principal
        prompt = f"""Eres un asistente inteligente especializado en analizar documentos PDF. Tu tarea es responder preguntas basándote únicamente en el contenido de los documentos proporcionados.

CONTEXTO DE LOS DOCUMENTOS:
{context}

{"HISTORIAL RECIENTE DE LA CONVERSACIÓN:" if history_str else ""}
{history_str}

PREGUNTA ACTUAL DEL USUARIO:
{user_question}

INSTRUCCIONES:
1. Responde ÚNICAMENTE basándote en la información presente en los documentos proporcionados
2. Si la información no está en los documentos, indícalo claramente
3. Proporciona respuestas detalladas y bien estructuradas
4. Cita información específica de los documentos cuando sea relevante
5. Si hay múltiples fuentes, menciona de cuál documento proviene cada información
6. Mantén un tono profesional y útil
7. Responde en español
8. Si el usuario pregunta sobre algo que NO está en los documentos, sugiere qué tipo de información sí está disponible

RESPUESTA:"""
        
        return prompt
    
    def generate_response(
        self, 
        prompt: str,
        stream: bool = False
    ) -> str:
        """Generar respuesta usando Groq API"""
        
        if not self.client:
            return "❌ Error: Cliente de Groq no está disponible. Verifica tu API key."
        
        try:
            # Crear mensaje para la API
            messages = [
                {"role": "system", "content": "Eres un asistente especializado en análisis de documentos. Responde de forma precisa y útil basándote únicamente en el contenido proporcionado."},
                {"role": "user", "content": prompt}
            ]
            
            # Hacer llamada a Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=stream
            )
            
            if stream:
                return response  # Retornar el generador para streaming
            else:
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            error_msg = f"Error generando respuesta: {str(e)}"
            st.error(error_msg)
            return f"❌ {error_msg}"
    
    def chat_with_context(
        self,
        user_question: str,
        relevant_chunks: List[str],
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Chatear con contexto de documentos"""
        
        # Crear prompt con contexto
        prompt = self.create_context_prompt(user_question, relevant_chunks, conversation_history)
        
        # Generar respuesta
        response = self.generate_response(prompt)
        
        # Agregar al historial
        self.conversation_history.append({
            'role': 'user',
            'content': user_question,
            'timestamp': datetime.now().isoformat()
        })
        
        self.conversation_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'context_chunks': len(relevant_chunks)
        })
        
        return response
    
    def generate_summary(self, documents_content: List[str]) -> str:
        """Generar resumen de documentos"""
        
        # Preparar contenido para resumen
        combined_content = "\n\n".join(documents_content[:5])  # Limitar a 5 documentos
        
        if len(combined_content) > 8000:  # Limitar tamaño
            combined_content = combined_content[:8000] + "...\n[Contenido truncado]"
        
        prompt = f"""Analiza los siguientes documentos y genera un resumen ejecutivo completo.

CONTENIDO DE LOS DOCUMENTOS:
{combined_content}

INSTRUCCIONES:
1. Identifica los temas principales de cada documento
2. Destaca los puntos más importantes y relevantes
3. Estructura el resumen de manera clara y organizada
4. Incluye información sobre el número de documentos analizados
5. Proporciona una visión general coherente
6. Responde en español
7. Usa formato markdown para mejorar la legibilidad

RESUMEN EJECUTIVO:"""
        
        return self.generate_response(prompt)
    
    def compare_documents(self, documents_content: List[str], filenames: List[str]) -> str:
        """Comparar múltiples documentos"""
        
        if len(documents_content) < 2:
            return "Se necesitan al menos 2 documentos para realizar una comparación."
        
        # Preparar contenido numerado por documento
        numbered_content = []
        for i, (content, filename) in enumerate(zip(documents_content, filenames)):
            content_preview = content[:2000] if len(content) > 2000 else content
            numbered_content.append(f"DOCUMENTO {i+1} ({filename}):\n{content_preview}")
        
        combined_content = "\n\n" + "="*50 + "\n\n".join(numbered_content)
        
        prompt = f"""Compara los siguientes documentos y encuentra similitudes y diferencias clave.

{combined_content}

INSTRUCCIONES:
1. Identifica los temas principales de cada documento
2. Encuentra similitudes entre los documentos
3. Destaca las diferencias clave
4. Analiza el enfoque y perspectiva de cada documento
5. Proporciona una comparación estructurada y objetiva
6. Responde en español
7. Usa formato markdown para organizar la información

ANÁLISIS COMPARATIVO:"""
        
        return self.generate_response(prompt)
    
    def classify_documents(self, documents_content: List[str], filenames: List[str]) -> str:
        """Clasificar documentos por temas"""
        
        # Preparar contenido con nombres de archivo
        content_with_names = []
        for content, filename in zip(documents_content, filenames):
            preview = content[:1500] if len(content) > 1500 else content
            content_with_names.append(f"**{filename}**:\n{preview}")
        
        combined_content = "\n\n---\n\n".join(content_with_names)
        
        prompt = f"""Clasifica los siguientes documentos por temas y categorías.

DOCUMENTOS A CLASIFICAR:
{combined_content}

INSTRUCCIONES:
1. Identifica los temas principales de cada documento
2. Crea categorías lógicas para agrupar los documentos
3. Asigna cada documento a las categorías apropiadas
4. Proporciona una justificación para cada clasificación
5. Estructura la información de manera clara
6. Responde en español
7. Usa formato markdown para organizar la clasificación

CLASIFICACIÓN POR TEMAS:"""
        
        return self.generate_response(prompt)
    
    def get_conversation_history(self) -> List[Dict]:
        """Obtener historial de conversación"""
        return self.conversation_history
    
    def clear_history(self):
        """Limpiar historial de conversación"""
        self.conversation_history = []
        st.success("🗑️ Historial de conversación limpiado")
    
    def export_conversation(self) -> str:
        """Exportar conversación a JSON"""
        return json.dumps(self.conversation_history, indent=2, ensure_ascii=False)
    
    def is_available(self) -> bool:
        """Verificar si el cliente está disponible"""
        return self.client is not None


class StreamlitChatInterface:
    """Interfaz de chat para Streamlit"""
    
    def __init__(self, chat_manager: ChatManager):
        self.chat_manager = chat_manager
    
    def display_message(self, role: str, content: str, timestamp: str = None):
        """Mostrar mensaje en la interfaz"""
        if role == "user":
            with st.chat_message("user"):
                st.write(content)
                if timestamp:
                    st.caption(f"🕐 {timestamp}")
        else:
            with st.chat_message("assistant"):
                st.write(content)
                if timestamp:
                    st.caption(f"🕐 {timestamp}")
    
    def display_conversation_history(self):
        """Mostrar historial de conversación"""
        history = self.chat_manager.get_conversation_history()
        
        if not history:
            st.info("💬 No hay conversaciones previas")
            return
        
        for message in history:
            self.display_message(
                message['role'], 
                message['content'],
                message.get('timestamp', '')
            )
    
    def chat_input_handler(self, embedder, prompt_text: str = "Escribe tu pregunta sobre los documentos..."):
        """Manejar entrada de chat"""
        if prompt := st.chat_input(prompt_text):
            # Mostrar pregunta del usuario
            self.display_message("user", prompt)
            
            # Buscar contexto relevante
            with st.spinner("Buscando información relevante..."):
                search_results = embedder.search_similar_chunks(prompt, n_results=5)
                relevant_chunks = search_results.get('documents', [[]])[0] if search_results.get('documents') else []
            
            # Generar respuesta
            with st.spinner("Generando respuesta..."):
                response = self.chat_manager.chat_with_context(
                    prompt, 
                    relevant_chunks,
                    self.chat_manager.get_conversation_history()
                )
            
            # Mostrar respuesta
            self.display_message("assistant", response)
            
            # Mostrar información de contexto
            if relevant_chunks:
                with st.expander(f"📄 Contexto utilizado ({len(relevant_chunks)} fragmentos)"):
                    for i, chunk in enumerate(relevant_chunks):
                        st.text_area(
                            f"Fragmento {i+1}", 
                            chunk[:500] + "..." if len(chunk) > 500 else chunk,
                            height=100
                        )


def create_chat_manager_from_config() -> ChatManager:
    """Crear chat manager usando configuración del entorno"""
    api_key = os.getenv('GROQ_API_KEY')
    model = os.getenv('GROQ_MODEL', 'llama3-70b-8192')
    
    return ChatManager(
        api_key=api_key,
        model=model
    )
