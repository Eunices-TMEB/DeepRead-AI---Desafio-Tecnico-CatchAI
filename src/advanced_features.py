"""
Funcionalidades avanzadas para CatchAI v2.0
"""

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional, Tuple
import re
from collections import Counter
import numpy as np
from datetime import datetime
import io
import base64
try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False


class HybridSearch:
    """Búsqueda híbrida: semántica + keyword"""
    
    def __init__(self, embedder):
        self.embedder = embedder
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extraer palabras clave importantes"""
        # Patrones para códigos, números, fechas
        patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # Fechas
            r'\b[A-Z]{2,}\d+\b',                     # Códigos (ej: ABC123)
            r'\b\d+[.,]\d+\b',                       # Números decimales
            r'\$\d+[.,]?\d*',                        # Montos
            r'\b\d{4,}\b'                            # Números largos
        ]
        
        keywords = []
        for pattern in patterns:
            keywords.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Agregar palabras importantes (sustantivos en mayúscula, etc.)
        important_words = re.findall(r'\b[A-Z][a-z]{3,}\b', text)
        keywords.extend(important_words)
        
        return list(set(keywords))
    
    def keyword_search(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Búsqueda por palabras clave exactas"""
        query_keywords = self.extract_keywords(query)
        results = []
        
        for doc in documents:
            content = doc.get('documents', [''])[0] if doc.get('documents') else ''
            doc_keywords = self.extract_keywords(content)
            
            # Calcular coincidencias exactas
            matches = set(query_keywords) & set(doc_keywords)
            if matches:
                score = len(matches) / max(len(query_keywords), 1)
                results.append({
                    'content': content,
                    'metadata': doc.get('metadatas', [{}])[0],
                    'keyword_score': score,
                    'matched_keywords': list(matches)
                })
        
        return sorted(results, key=lambda x: x['keyword_score'], reverse=True)
    
    def hybrid_search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Combinar búsqueda semántica y por keywords"""
        # Búsqueda semántica
        semantic_results = self.embedder.search_similar_chunks(query, n_results=n_results)
        
        # Búsqueda por keywords
        all_docs = self.embedder.collection.get()
        structured_docs = []
        for i in range(len(all_docs.get('ids', []))):
            structured_docs.append({
                'documents': [all_docs['documents'][i]] if i < len(all_docs['documents']) else [''],
                'metadatas': [all_docs['metadatas'][i]] if i < len(all_docs['metadatas']) else [{}]
            })
        
        keyword_results = self.keyword_search(query, structured_docs)
        
        # Combinar resultados
        combined_results = {
            'semantic': semantic_results,
            'keyword': keyword_results,
            'hybrid_summary': {
                'semantic_count': len(semantic_results.get('documents', [[]])[0] if semantic_results.get('documents') else []),
                'keyword_count': len(keyword_results),
                'total_unique': len(set([doc['content'] for doc in keyword_results] + 
                                       (semantic_results.get('documents', [[]])[0] if semantic_results.get('documents') else [])))
            }
        }
        
        return combined_results


class VisualAnalyzer:
    """Análisis y resumen visual de documentos"""
    
    @staticmethod
    def create_word_cloud(texts: List[str]) -> str:
        """Crear nube de palabras"""
        if not WORDCLOUD_AVAILABLE:
            return None
            
        combined_text = ' '.join(texts)
        
        # Limpiar texto
        cleaned_text = re.sub(r'[^\w\s]', ' ', combined_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Generar wordcloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            colormap='viridis'
        ).generate(cleaned_text)
        
        # Convertir a base64
        img_buffer = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        plt.close()
        
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def create_concept_map(texts: List[str], filenames: List[str]) -> go.Figure:
        """Crear mapa conceptual de relaciones entre documentos"""
        G = nx.Graph()
        
        # Extraer conceptos clave de cada documento
        concepts_by_doc = {}
        for i, (text, filename) in enumerate(zip(texts, filenames)):
            # Extraer sustantivos importantes
            concepts = re.findall(r'\b[A-Z][a-z]{4,}\b', text)
            concepts = [c for c in concepts if len(c) > 4]  # Filtrar palabras muy cortas
            concepts_counter = Counter(concepts)
            top_concepts = [concept for concept, count in concepts_counter.most_common(10)]
            concepts_by_doc[filename] = top_concepts
            
            # Agregar nodo para el documento
            G.add_node(filename, node_type='document', size=20)
            
            # Agregar nodos para conceptos
            for concept in top_concepts:
                G.add_node(concept, node_type='concept', size=10)
                G.add_edge(filename, concept)
        
        # Conectar documentos que comparten conceptos
        for i, (doc1, concepts1) in enumerate(concepts_by_doc.items()):
            for j, (doc2, concepts2) in enumerate(concepts_by_doc.items()):
                if i < j:  # Evitar duplicados
                    shared_concepts = set(concepts1) & set(concepts2)
                    if shared_concepts:
                        G.add_edge(doc1, doc2, weight=len(shared_concepts))
        
        # Crear layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Preparar datos para Plotly
        edge_x, edge_y = [], []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Nodos de documentos
        doc_x = [pos[node][0] for node in G.nodes() if G.nodes[node].get('node_type') == 'document']
        doc_y = [pos[node][1] for node in G.nodes() if G.nodes[node].get('node_type') == 'document']
        doc_text = [node for node in G.nodes() if G.nodes[node].get('node_type') == 'document']
        
        # Nodos de conceptos
        concept_x = [pos[node][0] for node in G.nodes() if G.nodes[node].get('node_type') == 'concept']
        concept_y = [pos[node][1] for node in G.nodes() if G.nodes[node].get('node_type') == 'concept']
        concept_text = [node for node in G.nodes() if G.nodes[node].get('node_type') == 'concept']
        
        # Crear figura
        fig = go.Figure()
        
        # Agregar aristas
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))
        
        # Agregar nodos de documentos
        fig.add_trace(go.Scatter(
            x=doc_x, y=doc_y,
            mode='markers+text',
            hoverinfo='text',
            text=doc_text,
            textposition='middle center',
            marker=dict(
                size=30,
                color='lightblue',
                line=dict(width=2, color='darkblue')
            ),
            name='Documentos'
        ))
        
        # Agregar nodos de conceptos
        fig.add_trace(go.Scatter(
            x=concept_x, y=concept_y,
            mode='markers+text',
            hoverinfo='text',
            text=concept_text,
            textposition='top center',
            marker=dict(
                size=15,
                color='lightgreen',
                line=dict(width=1, color='darkgreen')
            ),
            name='Conceptos'
        ))
        
        fig.update_layout(
            title="Mapa Conceptual de Documentos",
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[
                dict(
                    text="Los documentos están conectados por conceptos compartidos",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002,
                    xanchor='left', yanchor='bottom',
                    font=dict(color='gray', size=12)
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    @staticmethod
    def document_similarity_heatmap(embedder, filenames: List[str]) -> go.Figure:
        """Crear mapa de calor de similitud entre documentos"""
        if len(filenames) < 2:
            return None
        
        # Obtener embeddings promedio por documento
        collection_data = embedder.collection.get()
        doc_embeddings = {}
        
        for i, (doc, metadata) in enumerate(zip(collection_data['documents'], collection_data['metadatas'])):
            source = metadata.get('source', 'unknown')
            if source not in doc_embeddings:
                doc_embeddings[source] = []
            
            # Generar embedding para este chunk
            embedding = embedder.generate_embeddings([doc])[0]
            doc_embeddings[source].append(embedding)
        
        # Calcular embedding promedio por documento
        avg_embeddings = {}
        for source, embeddings in doc_embeddings.items():
            avg_embeddings[source] = np.mean(embeddings, axis=0)
        
        # Calcular matriz de similitud
        sources = list(avg_embeddings.keys())
        n = len(sources)
        similarity_matrix = np.zeros((n, n))
        
        for i, source1 in enumerate(sources):
            for j, source2 in enumerate(sources):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    # Similitud coseno
                    vec1 = avg_embeddings[source1]
                    vec2 = avg_embeddings[source2]
                    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
                    similarity_matrix[i][j] = similarity
        
        # Crear heatmap
        fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            x=sources,
            y=sources,
            colorscale='RdYlBu',
            colorbar=dict(title="Similitud"),
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Mapa de Similitud entre Documentos",
            xaxis_title="Documentos",
            yaxis_title="Documentos",
            width=600,
            height=600
        )
        
        return fig


class SmartClassifier:
    """Clasificación inteligente y etiquetado automático"""
    
    def __init__(self, chat_manager):
        self.chat_manager = chat_manager
        
        # Categorías predefinidas con palabras clave
        self.categories = {
            'Legal': ['contrato', 'clausula', 'derecho', 'legal', 'ley', 'tribunal', 'demanda'],
            'Financiero': ['dinero', 'costo', 'precio', 'factura', 'pago', 'banco', 'inversión'],
            'Técnico': ['sistema', 'software', 'tecnología', 'código', 'desarrollo', 'API'],
            'Académico': ['estudio', 'investigación', 'universidad', 'tesis', 'académico'],
            'Médico': ['paciente', 'médico', 'hospital', 'tratamiento', 'diagnóstico', 'salud'],
            'Corporativo': ['empresa', 'negocio', 'estrategia', 'mercado', 'cliente', 'ventas']
        }
    
    def classify_document(self, content: str, filename: str) -> Dict[str, Any]:
        """Clasificar documento automáticamente"""
        content_lower = content.lower()
        
        # Clasificación por keywords
        category_scores = {}
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            category_scores[category] = score / len(keywords)  # Normalizar
        
        # Obtener categoría principal
        primary_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[primary_category]
        
        # Clasificación con IA si hay suficiente confianza
        ai_classification = None
        if confidence > 0.1 and self.chat_manager.is_available():
            prompt = f"""Analiza este documento y clasifícalo en una categoría específica.

Documento: {filename}
Contenido (primeras 1000 caracteres):
{content[:1000]}

Categorías posibles: {', '.join(self.categories.keys())}

Responde solo con:
1. Categoría principal
2. Subcategoría específica (ej: "Contrato de trabajo", "Estado financiero")
3. Nivel de confianza (1-10)
4. Palabras clave principales (máximo 5)

Formato:
Categoría: [categoría]
Subcategoría: [subcategoría específica]
Confianza: [número]/10
Keywords: [palabra1, palabra2, palabra3]"""

            ai_response = self.chat_manager.generate_response(prompt)
            ai_classification = ai_response
        
        return {
            'filename': filename,
            'primary_category': primary_category,
            'confidence': confidence,
            'category_scores': category_scores,
            'ai_classification': ai_classification,
            'suggested_tags': self._extract_tags(content),
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extraer tags automáticamente"""
        # Extraer entidades importantes
        patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Nombres propios
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # Fechas
            r'\$\d+[.,]?\d*',  # Montos
            r'\b[A-Z]{2,}\b'   # Acrónimos
        ]
        
        tags = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            tags.extend(matches)
        
        # Filtrar y limpiar tags
        tags = list(set(tags))[:10]  # Máximo 10 tags
        return tags


class ReportGenerator:
    """Generador de informes descargables"""
    
    @staticmethod
    def create_session_report(
        documents: List[Dict], 
        conversation_history: List[Dict],
        classifications: List[Dict] = None
    ) -> str:
        """Crear informe de sesión en HTML"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Informe de Sesión - CatchAI</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #667eea; color: white; padding: 20px; border-radius: 10px; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #667eea; }}
                .document {{ background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .conversation {{ background: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .user {{ background: #d4edda; }}
                .assistant {{ background: #cce5ff; }}
                .stats {{ display: flex; gap: 20px; }}
                .stat-box {{ background: #f1f3f4; padding: 15px; border-radius: 5px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📚 Informe de Sesión - CatchAI</h1>
                <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Estadísticas de la Sesión</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>{len(documents)}</h3>
                        <p>Documentos Procesados</p>
                    </div>
                    <div class="stat-box">
                        <h3>{len(conversation_history)}</h3>
                        <p>Interacciones</p>
                    </div>
                    <div class="stat-box">
                        <h3>{sum(doc.get('word_count', 0) for doc in documents):,}</h3>
                        <p>Palabras Analizadas</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📁 Documentos Procesados</h2>
        """
        
        for doc in documents:
            html_content += f"""
                <div class="document">
                    <h3>📄 {doc.get('filename', 'Sin nombre')}</h3>
                    <p><strong>Palabras:</strong> {doc.get('word_count', 0):,}</p>
                    <p><strong>Caracteres:</strong> {doc.get('char_count', 0):,}</p>
                    <p><strong>Hash:</strong> {doc.get('file_hash', 'N/A')[:16]}...</p>
                </div>
            """
        
        html_content += """
            </div>
            
            <div class="section">
                <h2>💬 Historial de Conversación</h2>
        """
        
        for msg in conversation_history:
            role_class = "user" if msg.get('role') == 'user' else "assistant"
            role_icon = "👤" if msg.get('role') == 'user' else "🤖"
            html_content += f"""
                <div class="conversation {role_class}">
                    <strong>{role_icon} {msg.get('role', 'Unknown').title()}:</strong>
                    <p>{msg.get('content', '')}</p>
                    <small>{msg.get('timestamp', '')}</small>
                </div>
            """
        
        if classifications:
            html_content += """
            </div>
            
            <div class="section">
                <h2>🏷️ Clasificaciones Automáticas</h2>
            """
            
            for classification in classifications:
                html_content += f"""
                    <div class="document">
                        <h3>{classification.get('filename', 'Sin nombre')}</h3>
                        <p><strong>Categoría:</strong> {classification.get('primary_category', 'N/A')}</p>
                        <p><strong>Confianza:</strong> {classification.get('confidence', 0):.2%}</p>
                        <p><strong>Tags:</strong> {', '.join(classification.get('suggested_tags', []))}</p>
                    </div>
                """
        
        html_content += """
            </div>
            
            <div class="section">
                <h2>🚀 Generado por CatchAI v2.0</h2>
                <p>Copiloto conversacional inteligente para análisis de documentos PDF</p>
                <p>Powered by Groq + Llama 3.1 70B + ChromaDB</p>
            </div>
        </body>
        </html>
        """
        
        return html_content


class PersistentContext:
    """Contexto persistente para conversaciones fluidas"""
    
    def __init__(self):
        if 'conversation_context' not in st.session_state:
            st.session_state.conversation_context = {
                'current_topic': None,
                'referenced_documents': [],
                'key_entities': [],
                'conversation_flow': []
            }
    
    def update_context(self, user_question: str, ai_response: str, sources: List[str]):
        """Actualizar contexto basado en nueva interacción"""
        context = st.session_state.conversation_context
        
        # Detectar entidades en la pregunta
        entities = self._extract_entities(user_question)
        context['key_entities'].extend(entities)
        context['key_entities'] = list(set(context['key_entities']))[-10:]  # Mantener últimas 10
        
        # Actualizar documentos referenciados
        for source in sources:
            if source not in context['referenced_documents']:
                context['referenced_documents'].append(source)
        
        # Agregar al flujo de conversación
        context['conversation_flow'].append({
            'question': user_question,
            'response': ai_response[:200] + '...' if len(ai_response) > 200 else ai_response,
            'timestamp': datetime.now().isoformat(),
            'entities': entities
        })
        
        # Mantener solo últimas 20 interacciones
        context['conversation_flow'] = context['conversation_flow'][-20:]
        
        # Detectar tema actual
        if entities:
            context['current_topic'] = entities[0] if entities else context['current_topic']
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extraer entidades importantes del texto"""
        patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Nombres propios
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # Fechas
            r'\b[A-Z]{2,}\b',  # Acrónimos
            r'\$\d+[.,]?\d*'   # Montos
        ]
        
        entities = []
        for pattern in patterns:
            entities.extend(re.findall(pattern, text))
        
        return list(set(entities))[:5]  # Máximo 5 entidades
    
    def get_context_prompt(self) -> str:
        """Generar prompt con contexto para el LLM"""
        context = st.session_state.conversation_context
        
        if not context['conversation_flow']:
            return ""
        
        context_prompt = "\n=== CONTEXTO DE LA CONVERSACIÓN ===\n"
        
        if context['current_topic']:
            context_prompt += f"Tema actual: {context['current_topic']}\n"
        
        if context['key_entities']:
            context_prompt += f"Entidades clave: {', '.join(context['key_entities'][-5:])}\n"
        
        if context['referenced_documents']:
            context_prompt += f"Documentos referenciados: {', '.join(context['referenced_documents'][-3:])}\n"
        
        # Últimas 3 interacciones
        recent_flow = context['conversation_flow'][-3:]
        if recent_flow:
            context_prompt += "\nÚltimas interacciones:\n"
            for i, interaction in enumerate(recent_flow, 1):
                context_prompt += f"{i}. Q: {interaction['question']}\n"
                context_prompt += f"   R: {interaction['response']}\n"
        
        context_prompt += "=== FIN DEL CONTEXTO ===\n\n"
        
        return context_prompt
