"""
Funcionalidades Premium para CatchAI v2.0
Personalidades configurables, preguntas sugeridas, comparación visual y reportes inteligentes
"""

import streamlit as st
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import io
import base64
import json
from dataclasses import dataclass
import pandas as pd


@dataclass
class PersonalityConfig:
    """Configuración de personalidad del chat"""
    name: str
    description: str
    prompt_prefix: str
    tone: str
    example_response: str


class PersonalityManager:
    """Gestión de personalidades configurables del chat"""
    
    def __init__(self):
        self.personalities = {
            'formal': PersonalityConfig(
                name="🏛️ Formal (Abogado)",
                description="Respuestas precisas y profesionales con terminología legal",
                prompt_prefix="""Responde de manera formal y profesional, como un abogado experimentado. 
                Usa terminología precisa, cita cláusulas cuando sea relevante, y estructura la respuesta 
                de forma clara con puntos numerados. Mantén un tono respetuoso y técnico.""",
                tone="Formal y preciso",
                example_response="Conforme al análisis del documento..."
            ),
            'technical': PersonalityConfig(
                name="⚙️ Técnico (Ingeniero)",
                description="Explicaciones detalladas con enfoque técnico y datos específicos",
                prompt_prefix="""Responde como un ingeniero técnico experto. Proporciona detalles específicos,
                datos técnicos, números exactos y explicaciones paso a paso. Usa terminología técnica apropiada 
                y estructura la información de manera lógica y sistemática.""",
                tone="Técnico y detallado",
                example_response="Según los datos técnicos identificados..."
            ),
            'executive': PersonalityConfig(
                name="📊 Ejecutivo (Gerente)",
                description="Resúmenes concisos enfocados en puntos clave y decisiones",
                prompt_prefix="""Responde como un ejecutivo senior. Enfócate en puntos clave, implicaciones
                de negocio, riesgos y oportunidades. Sé conciso pero completo. Usa bullet points y 
                destaca información crítica para toma de decisiones.""",
                tone="Estratégico y conciso",
                example_response="Puntos clave para consideración ejecutiva:"
            ),
            'simple': PersonalityConfig(
                name="🎓 Simple (Profesor)",
                description="Explicaciones claras y didácticas, fáciles de entender",
                prompt_prefix="""Responde como un profesor paciente y didáctico. Explica conceptos complejos
                de manera simple y clara. Usa analogías cuando sea útil, proporciona contexto y 
                asegúrate de que cualquier persona pueda entender la respuesta.""",
                tone="Educativo y claro",
                example_response="Te explico de manera sencilla..."
            ),
            'creative': PersonalityConfig(
                name="🎨 Creativo (Innovador)",
                description="Respuestas creativas con analogías y perspectivas únicas",
                prompt_prefix="""Responde de manera creativa e innovadora. Usa analogías interesantes,
                metáforas útiles y proporciona perspectivas únicas. Mantén la precisión pero 
                agrega elementos creativos que hagan la información más memorable.""",
                tone="Creativo y memorable",
                example_response="Imagina que este documento es como..."
            )
        }
        self.current_personality = 'simple'  # Por defecto
    
    def get_current_personality(self) -> PersonalityConfig:
        """Obtener personalidad actual"""
        return self.personalities[self.current_personality]
    
    def set_personality(self, personality_key: str):
        """Establecer personalidad activa"""
        if personality_key in self.personalities:
            self.current_personality = personality_key
    
    def get_personality_prompt(self, user_question: str) -> str:
        """Generar prompt con personalidad aplicada"""
        personality = self.get_current_personality()
        
        enhanced_prompt = f"""
{personality.prompt_prefix}

PREGUNTA DEL USUARIO: {user_question}

INSTRUCCIONES ESPECÍFICAS DE PERSONALIDAD:
- Tono: {personality.tone}
- Estilo de respuesta similar a: "{personality.example_response}"

Responde manteniendo esta personalidad consistentemente:
"""
        return enhanced_prompt


class QuestionSuggester:
    """Generador de preguntas sugeridas inteligentes"""
    
    def __init__(self, chat_manager):
        self.chat_manager = chat_manager
    
    def extract_key_topics(self, text: str) -> List[str]:
        """Extraer temas clave del texto"""
        # Patrones para diferentes tipos de información importante
        patterns = {
            'dates': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'money': r'\$\d+[.,]?\d*|\d+[.,]?\d*\s*(?:euros?|dolares?|pesos?)',
            'people': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'companies': r'\b[A-Z][a-z]*\s+(?:Inc|LLC|Corp|SA|SL|Ltd)\.?\b',
            'percentages': r'\d+[.,]?\d*\s*%',
            'legal_terms': r'\b(?:contrato|acuerdo|cláusula|artículo|párrafo|sección)\b',
        }
        
        topics = []
        for category, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                topics.extend(matches[:3])  # Máximo 3 por categoría
        
        return topics[:10]  # Máximo 10 temas
    
    def generate_contextual_questions(self, last_response: str, user_question: str) -> List[str]:
        """Generar preguntas contextuales basadas en la última respuesta"""
        topics = self.extract_key_topics(last_response)
        
        # Templates de preguntas por tipo de contenido
        question_templates = [
            "¿Podrías explicar más sobre {topic}?",
            "¿Qué implicaciones tiene {topic}?",
            "¿Hay más información sobre {topic} en otros documentos?",
            "¿Cómo se relaciona {topic} con el contexto general?",
            "¿Cuáles son los riesgos asociados con {topic}?",
            "¿Qué alternativas existen para {topic}?",
        ]
        
        # Preguntas generales inteligentes
        general_questions = [
            "¿Cuáles son los puntos más críticos de este documento?",
            "¿Qué aspectos requieren más atención?",
            "¿Hay información contradictoria entre documentos?",
            "¿Qué recomendaciones darías basado en esta información?",
            "¿Puedes hacer un resumen de los hallazgos principales?",
            "¿Qué preguntas importantes no hemos explorado aún?",
        ]
        
        suggestions = []
        
        # Generar preguntas basadas en temas extraídos
        for topic in topics[:2]:  # Máximo 2 preguntas por tema
            template = question_templates[len(suggestions) % len(question_templates)]
            suggestions.append(template.format(topic=topic))
        
        # Agregar preguntas generales
        remaining_slots = 4 - len(suggestions)
        if remaining_slots > 0:
            suggestions.extend(general_questions[:remaining_slots])
        
        return suggestions[:4]  # Máximo 4 sugerencias
    
    def generate_smart_questions(self, document_content: str = None) -> List[str]:
        """Generar preguntas inteligentes basadas en el contexto del documento"""
        if not document_content:
            return [
                "¿Cuál es el propósito principal de este documento?",
                "¿Qué aspectos son más importantes de analizar?",
                "¿Hay información crítica que deba destacar?",
                "¿Puedes hacer un resumen ejecutivo?"
            ]
        
        # Detectar tipo de documento
        doc_type = self._detect_document_type(document_content)
        
        type_questions = {
            'contract': [
                "¿Cuáles son las obligaciones principales de cada parte?",
                "¿Qué cláusulas de terminación existen?",
                "¿Hay penalizaciones o multas especificadas?",
                "¿Cuáles son los plazos más importantes?"
            ],
            'financial': [
                "¿Cuáles son las cifras más significativas?",
                "¿Qué tendencias se pueden identificar?",
                "¿Hay riesgos financieros evidentes?",
                "¿Cómo se compara con períodos anteriores?"
            ],
            'technical': [
                "¿Cuáles son las especificaciones técnicas clave?",
                "¿Qué requisitos de sistema se mencionan?",
                "¿Hay limitaciones técnicas importantes?",
                "¿Qué estándares se deben cumplir?"
            ],
            'legal': [
                "¿Cuáles son los puntos legales más críticos?",
                "¿Qué regulaciones son aplicables?",
                "¿Hay precedentes legales mencionados?",
                "¿Qué implicaciones legales son más relevantes?"
            ]
        }
        
        return type_questions.get(doc_type, type_questions['contract'])
    
    def _detect_document_type(self, content: str) -> str:
        """Detectar tipo de documento basado en el contenido"""
        content_lower = content.lower()
        
        type_indicators = {
            'contract': ['contrato', 'acuerdo', 'partes', 'cláusula', 'obligación'],
            'financial': ['balance', 'ingresos', 'gastos', 'financiero', 'estados', 'utilidad'],
            'technical': ['sistema', 'software', 'técnico', 'especificación', 'código'],
            'legal': ['ley', 'artículo', 'legal', 'jurídico', 'normativa', 'regulación']
        }
        
        scores = {}
        for doc_type, indicators in type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            scores[doc_type] = score
        
        return max(scores, key=scores.get) if scores else 'contract'


class VisualComparator:
    """Comparador visual lado a lado de documentos"""
    
    def __init__(self, embedder):
        self.embedder = embedder
    
    def prepare_comparison_data(self, doc1_name: str, doc2_name: str) -> Dict[str, Any]:
        """Preparar datos para comparación visual"""
        collection_data = self.embedder.collection.get()
        
        # Filtrar chunks por documento
        doc1_chunks = []
        doc2_chunks = []
        
        for doc, metadata in zip(collection_data['documents'], collection_data['metadatas']):
            source = metadata.get('source', '')
            if doc1_name in source:
                doc1_chunks.append(doc)
            elif doc2_name in source:
                doc2_chunks.append(doc)
        
        return {
            'doc1': {'name': doc1_name, 'chunks': doc1_chunks, 'content': '\n\n'.join(doc1_chunks)},
            'doc2': {'name': doc2_name, 'chunks': doc2_chunks, 'content': '\n\n'.join(doc2_chunks)}
        }
    
    def find_similarities_and_differences(self, doc1_content: str, doc2_content: str) -> Dict[str, List[str]]:
        """Encontrar similitudes y diferencias entre documentos"""
        
        # Dividir en oraciones para análisis
        doc1_sentences = [s.strip() for s in re.split(r'[.!?]\s*', doc1_content) if len(s.strip()) > 10]
        doc2_sentences = [s.strip() for s in re.split(r'[.!?]\s*', doc2_content) if len(s.strip()) > 10]
        
        # Encontrar similitudes (oraciones muy parecidas)
        similarities = []
        differences_doc1 = []
        differences_doc2 = []
        
        for sent1 in doc1_sentences[:20]:  # Limitar para rendimiento
            found_similar = False
            for sent2 in doc2_sentences[:20]:
                # Similitud simple basada en palabras comunes
                words1 = set(sent1.lower().split())
                words2 = set(sent2.lower().split())
                
                if len(words1 & words2) / max(len(words1), len(words2), 1) > 0.7:
                    similarities.append(f"📍 Similar: {sent1[:100]}...")
                    found_similar = True
                    break
            
            if not found_similar and len(similarities) < 5:
                differences_doc1.append(f"📄 Solo en {doc1_content[:20]}: {sent1[:100]}...")
        
        for sent2 in doc2_sentences[:10]:
            found_similar = False
            for sent1 in doc1_sentences:
                words1 = set(sent1.lower().split())
                words2 = set(sent2.lower().split())
                
                if len(words1 & words2) / max(len(words1), len(words2), 1) > 0.7:
                    found_similar = True
                    break
            
            if not found_similar and len(differences_doc2) < 5:
                differences_doc2.append(f"📄 Solo en {doc2_content[:20]}: {sent2[:100]}...")
        
        return {
            'similarities': similarities[:5],
            'differences_doc1': differences_doc1[:5],
            'differences_doc2': differences_doc2[:5]
        }


class IntelligentReportGenerator:
    """Generador de reportes de inteligencia avanzados"""
    
    def __init__(self, chat_manager):
        self.chat_manager = chat_manager
    
    def analyze_document_intelligence(self, content: str, filename: str) -> Dict[str, Any]:
        """Análisis completo de inteligencia del documento"""
        
        # Prompt para análisis integral
        analysis_prompt = f"""
Analiza este documento de manera exhaustiva y proporciona un informe de inteligencia:

DOCUMENTO: {filename}
CONTENIDO: {content[:3000]}...

Proporciona un análisis estructurado que incluya:

1. RESUMEN EJECUTIVO (máximo 150 palabras)

2. PUNTOS CLAVE IDENTIFICADOS (máximo 5 puntos)

3. RIESGOS DETECTADOS (máximo 5 riesgos)

4. OPORTUNIDADES IDENTIFICADAS (máximo 3 oportunidades)

5. TÉRMINOS CRÍTICOS Y DEFINICIONES (máximo 5)

6. RECOMENDACIONES DE ACCIÓN (máximo 4)

7. NIVEL DE PRIORIDAD (Alto/Medio/Bajo) con justificación

Formatea la respuesta de manera clara y profesional.
"""
        
        try:
            analysis = self.chat_manager.generate_response(analysis_prompt)
            return {
                'filename': filename,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat(),
                'word_count': len(content.split()),
                'char_count': len(content)
            }
        except Exception as e:
            return {
                'filename': filename,
                'analysis': f"Error en análisis: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'word_count': 0,
                'char_count': 0
            }
    
    def create_intelligence_report_html(self, analyses: List[Dict[str, Any]]) -> str:
        """Crear reporte de inteligencia en HTML"""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Informe de Inteligencia - CatchAI</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; padding: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{ 
                    background: white; 
                    border-radius: 15px; 
                    padding: 30px; 
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{ margin: 0; font-size: 2.5em; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                .document-analysis {{ 
                    margin: 30px 0; 
                    padding: 25px; 
                    border-left: 5px solid #667eea; 
                    background: #f8f9fa;
                    border-radius: 10px;
                }}
                .document-title {{ 
                    font-size: 1.4em; 
                    font-weight: bold; 
                    color: #667eea; 
                    margin-bottom: 15px;
                }}
                .analysis-content {{ 
                    line-height: 1.6; 
                    color: #333;
                }}
                .stats {{ 
                    display: flex; 
                    gap: 20px; 
                    margin: 20px 0;
                    flex-wrap: wrap;
                }}
                .stat-box {{ 
                    background: #e9ecef; 
                    padding: 15px 20px; 
                    border-radius: 10px; 
                    text-align: center;
                    flex: 1;
                    min-width: 150px;
                }}
                .stat-number {{ 
                    font-size: 1.8em; 
                    font-weight: bold; 
                    color: #667eea; 
                }}
                .stat-label {{ 
                    font-size: 0.9em; 
                    color: #666; 
                    margin-top: 5px;
                }}
                .footer {{ 
                    text-align: center; 
                    margin-top: 40px; 
                    padding: 20px; 
                    background: #f8f9fa; 
                    border-radius: 10px;
                    color: #666;
                }}
                .priority-high {{ border-left-color: #dc3545; }}
                .priority-medium {{ border-left-color: #ffc107; }}
                .priority-low {{ border-left-color: #28a745; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧠 Informe de Inteligencia Documental</h1>
                    <p>Análisis Integral Generado por CatchAI v2.0</p>
                    <p>{datetime.now().strftime('%d de %B de %Y - %H:%M:%S')}</p>
                </div>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{len(analyses)}</div>
                        <div class="stat-label">Documentos Analizados</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{sum(a.get('word_count', 0) for a in analyses):,}</div>
                        <div class="stat-label">Palabras Procesadas</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{sum(a.get('char_count', 0) for a in analyses):,}</div>
                        <div class="stat-label">Caracteres Analizados</div>
                    </div>
                </div>
        """
        
        for i, analysis in enumerate(analyses, 1):
            priority_class = "priority-medium"  # Por defecto
            if "alto" in analysis.get('analysis', '').lower():
                priority_class = "priority-high"
            elif "bajo" in analysis.get('analysis', '').lower():
                priority_class = "priority-low"
            
            html_content += f"""
                <div class="document-analysis {priority_class}">
                    <div class="document-title">
                        📄 Documento {i}: {analysis.get('filename', 'Sin nombre')}
                    </div>
                    <div class="analysis-content">
                        {analysis.get('analysis', 'Sin análisis disponible').replace('\n', '<br>')}
                    </div>
                    <div style="margin-top: 15px; font-size: 0.9em; color: #666;">
                        📊 {analysis.get('word_count', 0):,} palabras | 
                        🕒 {analysis.get('timestamp', '')[:19].replace('T', ' ')}
                    </div>
                </div>
            """
        
        html_content += """
                <div class="footer">
                    <h3>🚀 Generado por CatchAI v2.0</h3>
                    <p>Copiloto Conversacional de Inteligencia Documental</p>
                    <p>Powered by Groq + Llama 3.1 70B + ChromaDB + Análisis Avanzado</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def create_executive_summary(self, analyses: List[Dict[str, Any]]) -> str:
        """Crear resumen ejecutivo consolidado"""
        
        all_analyses = "\n\n".join([a.get('analysis', '') for a in analyses])
        
        summary_prompt = f"""
Basándote en todos estos análisis de documentos, crea un RESUMEN EJECUTIVO CONSOLIDADO:

{all_analyses}

El resumen debe incluir:

1. SITUACIÓN GENERAL (2-3 líneas)
2. HALLAZGOS PRINCIPALES (máximo 5 puntos)
3. RIESGOS CONSOLIDADOS (máximo 3 riesgos críticos)
4. RECOMENDACIONES ESTRATÉGICAS (máximo 4 acciones)
5. PRÓXIMOS PASOS SUGERIDOS (máximo 3 pasos)

Mantén un tono ejecutivo, conciso y orientado a la acción.
"""
        
        try:
            return self.chat_manager.generate_response(summary_prompt)
        except Exception as e:
            return f"Error generando resumen ejecutivo: {str(e)}"
