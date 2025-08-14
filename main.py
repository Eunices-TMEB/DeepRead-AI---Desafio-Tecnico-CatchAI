"""
CatchAI - Copiloto Conversacional sobre PDFs
Interfaz principal con Streamlit
"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import time
from datetime import datetime

# Agregar directorio src al path
sys.path.append(str(Path(__file__).parent / "src"))

# Importar módulos locales
from loader import PDFLoader, create_sample_document
from embedder import DocumentEmbedder, create_embedder_from_config
from chat import ChatManager, StreamlitChatInterface, create_chat_manager_from_config
from advanced_features import (
    HybridSearch, VisualAnalyzer, SmartClassifier, 
    ReportGenerator, PersistentContext
)
from premium_features import (
    PersonalityManager, QuestionSuggester, VisualComparator,
    IntelligentReportGenerator
)
from branding import apply_watermarks, show_splash_screen, watermark_document

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title=os.getenv('PAGE_TITLE', 'DeepRead AI - Desafío Técnico CatchAI'),
    page_icon=os.getenv('PAGE_ICON', '🧠'),
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stats-container {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .feature-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Inicializar estado de la sesión"""
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    if 'embedder' not in st.session_state:
        st.session_state.embedder = None
    if 'chat_manager' not in st.session_state:
        st.session_state.chat_manager = None
    if 'chat_interface' not in st.session_state:
        st.session_state.chat_interface = None
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False
    if 'hybrid_search' not in st.session_state:
        st.session_state.hybrid_search = None
    if 'smart_classifier' not in st.session_state:
        st.session_state.smart_classifier = None
    if 'persistent_context' not in st.session_state:
        st.session_state.persistent_context = None
    if 'document_classifications' not in st.session_state:
        st.session_state.document_classifications = []
    if 'personality_manager' not in st.session_state:
        st.session_state.personality_manager = None
    if 'question_suggester' not in st.session_state:
        st.session_state.question_suggester = None
    if 'visual_comparator' not in st.session_state:
        st.session_state.visual_comparator = None
    if 'intelligence_generator' not in st.session_state:
        st.session_state.intelligence_generator = None
    if 'suggested_questions' not in st.session_state:
        st.session_state.suggested_questions = []
    if 'last_response' not in st.session_state:
        st.session_state.last_response = ""


def initialize_system():
    """Inicializar el sistema completo"""
    if st.session_state.system_initialized:
        return True
    
    try:
        with st.spinner("🚀 Inicializando sistema..."):
            # Inicializar embedder
            st.session_state.embedder = create_embedder_from_config()
            
            # Inicializar chat manager
            st.session_state.chat_manager = create_chat_manager_from_config()
            
            # Inicializar interfaz de chat
            st.session_state.chat_interface = StreamlitChatInterface(st.session_state.chat_manager)
            
            # Inicializar funciones avanzadas
            st.session_state.hybrid_search = HybridSearch(st.session_state.embedder)
            st.session_state.smart_classifier = SmartClassifier(st.session_state.chat_manager)
            st.session_state.persistent_context = PersistentContext()
            
            # Inicializar funciones premium
            st.session_state.personality_manager = PersonalityManager()
            st.session_state.question_suggester = QuestionSuggester(st.session_state.chat_manager)
            st.session_state.visual_comparator = VisualComparator(st.session_state.embedder)
            st.session_state.intelligence_generator = IntelligentReportGenerator(st.session_state.chat_manager)
            
            st.session_state.system_initialized = True
            
        return True
        
    except Exception as e:
        st.error(f"Error inicializando sistema: {str(e)}")
        return False


def render_header():
    """Renderizar encabezado principal"""
    st.markdown("""
    <div class="main-header">
        <h1>📚 CatchAI - Copiloto Conversacional</h1>
        <p>Analiza documentos PDF con inteligencia artificial usando Groq + Llama 3.1 70B</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Renderizar barra lateral"""
    with st.sidebar:
        st.header("🛠️ Panel de Control")
        
        # Información del sistema
        if st.session_state.system_initialized:
            st.success("✅ Sistema inicializado")
            
            # Estadísticas de ChromaDB
            if st.session_state.embedder:
                stats = st.session_state.embedder.get_collection_stats()
                if stats:
                    st.markdown("### 📊 Base de Datos")
                    st.metric("Total chunks", stats.get('total_chunks', 0))
                    st.metric("Documentos únicos", stats.get('unique_documents', 0))
                    
                    if stats.get('sources'):
                        with st.expander("📁 Documentos cargados"):
                            for source in stats['sources']:
                                st.write(f"• {source}")
            
            # Estado de Groq
            if st.session_state.chat_manager:
                if st.session_state.chat_manager.is_available():
                    st.success("🤖 Groq API conectado")
                    st.write(f"Modelo: {st.session_state.chat_manager.model}")
                else:
                    st.error("❌ Groq API no disponible")
        else:
            st.warning("⚠️ Sistema no inicializado")
        
        st.divider()
        
        # Controles de gestión
        st.header("⚙️ Gestión")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Limpiar DB", help="Eliminar todos los documentos"):
                if st.session_state.embedder:
                    st.session_state.embedder.clear_collection()
                    st.rerun()
        
        with col2:
            if st.button("💬 Limpiar Chat", help="Borrar historial de conversación"):
                if st.session_state.chat_manager:
                    st.session_state.chat_manager.clear_history()
                    st.rerun()
        
        # Configuración avanzada
        with st.expander("🔧 Configuración"):
            st.write("**Variables de entorno:**")
            st.code(f"""
GROQ_MODEL: {os.getenv('GROQ_MODEL', 'llama3-70b-8192')}
CHUNK_SIZE: {os.getenv('CHUNK_SIZE', 1000)}
CHUNK_OVERLAP: {os.getenv('CHUNK_OVERLAP', 100)}
MAX_FILES: {os.getenv('MAX_FILES', 5)}
            """)


def render_upload_section():
    """Renderizar sección de subida de archivos"""
    st.header("📁 Subir Documentos PDF")
    
    # Información sobre límites
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Máx. archivos", os.getenv('MAX_FILES', 5))
    with col2:
        st.metric("Máx. por archivo", f"{os.getenv('MAX_FILE_SIZE_MB', 40)}MB")
    with col3:
        st.metric("Máx. total", f"{os.getenv('MAX_TOTAL_SIZE_MB', 200)}MB")
    
    # Widget de subida
    uploaded_files = st.file_uploader(
        "Selecciona archivos PDF",
        type=['pdf'],
        accept_multiple_files=True,
        help="Puedes subir hasta 5 archivos PDF (máx. 40MB cada uno)"
    )
    
    if uploaded_files:
        # Botón para procesar archivos
        if st.button("🚀 Procesar Documentos", type="primary"):
            if not st.session_state.system_initialized:
                st.error("Sistema no inicializado. Revisa la configuración.")
                return
            
            # Crear loader
            loader = PDFLoader(
                max_file_size_mb=int(os.getenv('MAX_FILE_SIZE_MB', 40)),
                max_total_size_mb=int(os.getenv('MAX_TOTAL_SIZE_MB', 200)),
                max_files=int(os.getenv('MAX_FILES', 5))
            )
            
            # Cargar documentos
            documents = loader.load_documents(uploaded_files)
            
            if documents:
                # Agregar a la base de datos vectorial
                success = st.session_state.embedder.add_documents_to_vectorstore(documents)
                
                if success:
                    st.session_state.documents.extend(documents)
                    st.success("🎉 ¡Documentos procesados exitosamente!")
                    
                    # Mostrar estadísticas
                    stats = loader.get_document_stats(documents)
                    if stats:
                        st.markdown("### 📈 Estadísticas de procesamiento")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Archivos procesados", stats['total_files'])
                        with col2:
                            st.metric("Total palabras", f"{stats['total_words']:,}")
                        with col3:
                            st.metric("Tamaño total", f"{stats['total_size_mb']:.1f} MB")
                    
                    time.sleep(1)
                    st.rerun()


def render_chat_section():
    """Renderizar sección de chat"""
    st.header("💬 Conversación")
    
    if not st.session_state.system_initialized:
        st.warning("⚠️ Inicializa el sistema primero")
        return
    
    if not st.session_state.chat_manager.is_available():
        st.error("❌ Groq API no disponible. Verifica tu API key.")
        return
    
    # Verificar si hay documentos
    stats = st.session_state.embedder.get_collection_stats()
    if not stats or stats.get('total_chunks', 0) == 0:
        st.info("📁 Sube algunos documentos PDF para comenzar a hacer preguntas")
        
        # Opción para cargar documento de ejemplo
        if st.button("📝 Cargar documento de ejemplo"):
            sample_doc = create_sample_document()
            success = st.session_state.embedder.add_documents_to_vectorstore([sample_doc])
            if success:
                st.success("✅ Documento de ejemplo cargado")
                st.rerun()
        return
    
    # Mostrar historial de conversación
    st.session_state.chat_interface.display_conversation_history()
    
    # Input de chat
    st.session_state.chat_interface.chat_input_handler(
        st.session_state.embedder,
        "Escribe tu pregunta sobre los documentos..."
    )


def render_extras_section():
    """Renderizar funciones extras"""
    st.header("🔧 Funciones Adicionales")
    
    if not st.session_state.system_initialized:
        st.warning("⚠️ Inicializa el sistema primero")
        return
    
    if not st.session_state.chat_manager.is_available():
        st.error("❌ Groq API no disponible")
        return
    
    # Verificar documentos
    stats = st.session_state.embedder.get_collection_stats()
    if not stats or stats.get('total_chunks', 0) == 0:
        st.info("📁 Necesitas subir documentos primero")
        return
    
    # Obtener contenido de documentos
    collection_data = st.session_state.embedder.collection.get()
    documents_content = []
    filenames = []
    
    # Agrupar chunks por documento
    doc_chunks = {}
    for doc, metadata in zip(collection_data['documents'], collection_data['metadatas']):
        source = metadata.get('source', 'unknown')
        if source not in doc_chunks:
            doc_chunks[source] = []
        doc_chunks[source].append(doc)
    
    # Combinar chunks por documento
    for source, chunks in doc_chunks.items():
        combined_content = "\n\n".join(chunks)
        documents_content.append(combined_content)
        filenames.append(source)
    
    if not documents_content:
        st.warning("No se encontró contenido de documentos")
        return
    
    # Botones para funciones extras
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Generar Resumen", type="secondary"):
            with st.spinner("Generando resumen..."):
                summary = st.session_state.chat_manager.generate_summary(documents_content)
                st.markdown("### 📋 Resumen Ejecutivo")
                st.markdown(summary)
    
    with col2:
        if st.button("🔍 Comparar Documentos", type="secondary"):
            if len(documents_content) < 2:
                st.warning("Se necesitan al menos 2 documentos para comparar")
            else:
                with st.spinner("Comparando documentos..."):
                    comparison = st.session_state.chat_manager.compare_documents(documents_content, filenames)
                    st.markdown("### 🔍 Comparación de Documentos")
                    st.markdown(comparison)
    
    with col3:
        if st.button("🏷️ Clasificar por Temas", type="secondary"):
            with st.spinner("Clasificando documentos..."):
                classification = st.session_state.chat_manager.classify_documents(documents_content, filenames)
                st.markdown("### 🏷️ Clasificación por Temas")
                st.markdown(classification)


def render_visual_analysis_section():
    """Renderizar sección de análisis visual"""
    st.header("📊 Análisis Visual Avanzado")
    
    if not st.session_state.system_initialized:
        st.warning("⚠️ Inicializa el sistema primero")
        return
    
    # Verificar documentos
    stats = st.session_state.embedder.get_collection_stats()
    if not stats or stats.get('total_chunks', 0) == 0:
        st.info("📁 Necesitas subir documentos primero")
        return
    
    # Obtener contenido de documentos
    collection_data = st.session_state.embedder.collection.get()
    documents_content = []
    filenames = []
    
    # Agrupar chunks por documento
    doc_chunks = {}
    for doc, metadata in zip(collection_data['documents'], collection_data['metadatas']):
        source = metadata.get('source', 'unknown')
        if source not in doc_chunks:
            doc_chunks[source] = []
        doc_chunks[source].append(doc)
    
    # Combinar chunks por documento
    for source, chunks in doc_chunks.items():
        combined_content = "\n\n".join(chunks[:5])  # Limitar chunks por documento
        documents_content.append(combined_content)
        filenames.append(source)
    
    if not documents_content:
        st.warning("No se encontró contenido de documentos")
        return
    
    # Opciones de análisis visual
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("☁️ Generar Nube de Palabras", type="secondary"):
            with st.spinner("Generando nube de palabras..."):
                wordcloud_img = VisualAnalyzer.create_word_cloud(documents_content)
                if wordcloud_img:
                    st.markdown("### ☁️ Nube de Palabras")
                    st.markdown(f'<img src="{wordcloud_img}" style="width:100%">', unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Instala 'wordcloud' para esta función: `pip install wordcloud`")
    
    with col2:
        if st.button("🗺️ Mapa Conceptual", type="secondary"):
            if len(documents_content) >= 2:
                with st.spinner("Creando mapa conceptual..."):
                    concept_map = VisualAnalyzer.create_concept_map(documents_content, filenames)
                    st.markdown("### 🗺️ Mapa Conceptual")
                    st.plotly_chart(concept_map, use_container_width=True)
            else:
                st.warning("Se necesitan al menos 2 documentos para el mapa conceptual")
    
    # Mapa de similitud
    if len(filenames) >= 2:
        if st.button("🔥 Mapa de Similitud", type="secondary"):
            with st.spinner("Calculando similitudes..."):
                similarity_map = VisualAnalyzer.document_similarity_heatmap(
                    st.session_state.embedder, filenames
                )
                if similarity_map:
                    st.markdown("### 🔥 Mapa de Similitud entre Documentos")
                    st.plotly_chart(similarity_map, use_container_width=True)
    
    # Clasificación automática
    st.markdown("### 🏷️ Clasificación Automática de Documentos")
    
    if st.button("🤖 Clasificar Todos los Documentos"):
        classifications = []
        progress_bar = st.progress(0)
        
        for i, (content, filename) in enumerate(zip(documents_content, filenames)):
            with st.spinner(f"Clasificando {filename}..."):
                classification = st.session_state.smart_classifier.classify_document(content, filename)
                classifications.append(classification)
                progress_bar.progress((i + 1) / len(documents_content))
        
        st.session_state.document_classifications = classifications
        
        # Mostrar resultados
        for classification in classifications:
            with st.expander(f"📄 {classification['filename']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Categoría Principal", classification['primary_category'])
                    st.metric("Confianza", f"{classification['confidence']:.1%}")
                with col2:
                    if classification['suggested_tags']:
                        st.write("**Tags Sugeridos:**")
                        for tag in classification['suggested_tags'][:5]:
                            st.badge(tag)
                
                if classification['ai_classification']:
                    st.write("**Análisis IA:**")
                    st.write(classification['ai_classification'])


def render_reports_section():
    """Renderizar sección de reportes"""
    st.header("📋 Generación de Reportes")
    
    if not st.session_state.system_initialized:
        st.warning("⚠️ Inicializa el sistema primero")
        return
    
    # Verificar si hay datos para el reporte
    if not st.session_state.documents:
        st.info("📁 Necesitas subir documentos primero")
        return
    
    conversation_history = st.session_state.chat_manager.get_conversation_history() if st.session_state.chat_manager else []
    
    st.markdown("### 📊 Estadísticas de la Sesión")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Documentos", len(st.session_state.documents))
    with col2:
        total_words = sum(doc.get('word_count', 0) for doc in st.session_state.documents)
        st.metric("Palabras", f"{total_words:,}")
    with col3:
        st.metric("Conversaciones", len(conversation_history))
    with col4:
        classifications_count = len(st.session_state.document_classifications)
        st.metric("Clasificaciones", classifications_count)
    
    # Opciones de reporte
    st.markdown("### 📋 Generar Reporte")
    
    include_classifications = st.checkbox("Incluir clasificaciones automáticas", value=True)
    
    if st.button("📄 Generar Reporte HTML", type="primary"):
        with st.spinner("Generando reporte..."):
            # Preparar datos
            classifications = st.session_state.document_classifications if include_classifications else None
            
            # Generar reporte con marca de agua
            html_report = ReportGenerator.create_session_report(
                st.session_state.documents,
                conversation_history,
                classifications
            )
            
            # Aplicar marca de agua al reporte
            html_report = watermark_document(html_report)
            
            # Crear botón de descarga
            st.download_button(
                label="⬇️ Descargar Reporte HTML",
                data=html_report,
                file_name=f"reporte_catchai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
            
            st.success("✅ Reporte generado exitosamente")
    
    # Búsqueda híbrida
    st.markdown("### 🔍 Búsqueda Híbrida (Semántica + Keywords)")
    
    search_query = st.text_input("Buscar en documentos (combina significado y palabras exactas):")
    
    if search_query and st.button("🔍 Buscar"):
        with st.spinner("Realizando búsqueda híbrida..."):
            results = st.session_state.hybrid_search.hybrid_search(search_query, n_results=5)
            
            # Mostrar resultados
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🧠 Resultados Semánticos")
                semantic_docs = results['semantic'].get('documents', [[]])[0] if results['semantic'].get('documents') else []
                for i, doc in enumerate(semantic_docs[:3]):
                    with st.expander(f"Resultado {i+1}"):
                        st.write(doc[:300] + "..." if len(doc) > 300 else doc)
            
            with col2:
                st.markdown("#### 🔑 Resultados por Keywords")
                keyword_results = results['keyword'][:3]
                for i, result in enumerate(keyword_results):
                    with st.expander(f"Resultado {i+1}"):
                        st.write(f"**Score:** {result['keyword_score']:.2f}")
                        st.write(f"**Keywords:** {', '.join(result['matched_keywords'])}")
                        st.write(result['content'][:300] + "..." if len(result['content']) > 300 else result['content'])
            
            # Resumen de búsqueda
            summary = results['hybrid_summary']
            st.info(f"📊 Encontrados: {summary['semantic_count']} resultados semánticos, "
                   f"{summary['keyword_count']} por keywords, "
                   f"{summary['total_unique']} únicos total")


def render_premium_features_section():
    """Renderizar sección de funciones premium"""
    st.header("🚀 Funciones Premium")
    
    if not st.session_state.system_initialized:
        st.warning("⚠️ Inicializa el sistema primero")
        return
    
    # Verificar documentos
    stats = st.session_state.embedder.get_collection_stats()
    if not stats or stats.get('total_chunks', 0) == 0:
        st.info("📁 Necesitas subir documentos primero")
        return
    
    # Pestañas para diferentes funciones premium
    premium_tab1, premium_tab2, premium_tab3 = st.tabs([
        "🎭 Personalidades IA", 
        "🔍 Comparador Visual", 
        "🧠 Reportes Inteligencia"
    ])
    
    with premium_tab1:
        st.markdown("### 🎭 Configurar Personalidad de la IA")
        
        # Selector de personalidad
        personalities = st.session_state.personality_manager.personalities
        personality_names = [config.name for config in personalities.values()]
        
        selected_name = st.selectbox(
            "Elige cómo quieres que te responda la IA:",
            personality_names,
            index=3  # Simple por defecto
        )
        
        # Encontrar la clave correspondiente
        selected_key = None
        for key, config in personalities.items():
            if config.name == selected_name:
                selected_key = key
                break
        
        if selected_key:
            st.session_state.personality_manager.set_personality(selected_key)
            current_personality = st.session_state.personality_manager.get_current_personality()
            
            # Mostrar información de la personalidad
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Descripción:** {current_personality.description}")
            with col2:
                st.success(f"**Tono:** {current_personality.tone}")
            
            st.markdown(f"**Ejemplo de respuesta:** *{current_personality.example_response}*")
        
        # Test de personalidad
        st.markdown("### 🧪 Prueba la Personalidad")
        test_question = st.text_input("Haz una pregunta de prueba:")
        
        if st.button("🎯 Responder con Personalidad", disabled=not test_question):
            if test_question:
                with st.spinner("Generando respuesta personalizada..."):
                    enhanced_prompt = st.session_state.personality_manager.get_personality_prompt(test_question)
                    response = st.session_state.chat_manager.generate_response(enhanced_prompt)
                    
                    st.markdown("### 🤖 Respuesta:")
                    st.markdown(response)
                    
                    # Generar preguntas sugeridas
                    suggested = st.session_state.question_suggester.generate_contextual_questions(
                        response, test_question
                    )
                    
                    if suggested:
                        st.markdown("### 💡 Preguntas Sugeridas:")
                        for i, q in enumerate(suggested):
                            st.markdown(f"{i+1}. {q}")
    
    with premium_tab2:
        st.markdown("### 🔍 Comparador Visual de Documentos")
        
        # Obtener lista de documentos
        collection_data = st.session_state.embedder.collection.get()
        doc_sources = set()
        for metadata in collection_data.get('metadatas', []):
            source = metadata.get('source', 'unknown')
            if source != 'unknown':
                doc_sources.add(source)
        
        doc_list = list(doc_sources)
        
        if len(doc_list) < 2:
            st.warning("⚠️ Necesitas al menos 2 documentos para comparar")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                doc1 = st.selectbox("Documento 1:", doc_list, key="doc1_select")
            with col2:
                doc2 = st.selectbox("Documento 2:", [d for d in doc_list if d != doc1], key="doc2_select")
            
            if st.button("🔍 Comparar Documentos", type="primary"):
                with st.spinner("Comparando documentos..."):
                    # Preparar datos de comparación
                    comparison_data = st.session_state.visual_comparator.prepare_comparison_data(doc1, doc2)
                    
                    # Encontrar similitudes y diferencias
                    analysis = st.session_state.visual_comparator.find_similarities_and_differences(
                        comparison_data['doc1']['content'],
                        comparison_data['doc2']['content']
                    )
                    
                    # Mostrar resultados
                    st.markdown("### 📊 Resultados de la Comparación")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"#### 📄 {doc1}")
                        st.text_area("Contenido (muestra):", 
                                   comparison_data['doc1']['content'][:500] + "...", 
                                   height=200, key="doc1_content")
                        
                        if analysis['differences_doc1']:
                            st.markdown("**Único en este documento:**")
                            for diff in analysis['differences_doc1']:
                                st.markdown(f"- {diff}")
                    
                    with col2:
                        st.markdown(f"#### 📄 {doc2}")
                        st.text_area("Contenido (muestra):", 
                                   comparison_data['doc2']['content'][:500] + "...", 
                                   height=200, key="doc2_content")
                        
                        if analysis['differences_doc2']:
                            st.markdown("**Único en este documento:**")
                            for diff in analysis['differences_doc2']:
                                st.markdown(f"- {diff}")
                    
                    # Similitudes
                    if analysis['similarities']:
                        st.markdown("### 🤝 Similitudes Encontradas")
                        for sim in analysis['similarities']:
                            st.markdown(f"- {sim}")
    
    with premium_tab3:
        st.markdown("### 🧠 Generador de Reportes de Inteligencia")
        
        # Opciones de análisis
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Análisis de Inteligencia Individual", type="secondary"):
                with st.spinner("Analizando documentos..."):
                    # Obtener contenido de documentos
                    collection_data = st.session_state.embedder.collection.get()
                    
                    # Agrupar por documento
                    doc_contents = {}
                    for doc, metadata in zip(collection_data['documents'], collection_data['metadatas']):
                        source = metadata.get('source', 'unknown')
                        if source not in doc_contents:
                            doc_contents[source] = []
                        doc_contents[source].append(doc)
                    
                    # Analizar cada documento
                    analyses = []
                    progress_bar = st.progress(0)
                    
                    for i, (filename, chunks) in enumerate(doc_contents.items()):
                        content = "\n\n".join(chunks)
                        analysis = st.session_state.intelligence_generator.analyze_document_intelligence(
                            content, filename
                        )
                        analyses.append(analysis)
                        progress_bar.progress((i + 1) / len(doc_contents))
                    
                    # Mostrar resultados
                    for analysis in analyses:
                        with st.expander(f"🧠 Análisis: {analysis['filename']}"):
                            st.markdown(analysis['analysis'])
                    
                    # Generar reporte descargable
                    if st.button("📄 Generar Reporte de Inteligencia HTML"):
                        html_report = st.session_state.intelligence_generator.create_intelligence_report_html(analyses)
                        
                        # Aplicar marca de agua al reporte de inteligencia
                        html_report = watermark_document(html_report)
                        
                        st.download_button(
                            label="⬇️ Descargar Reporte de Inteligencia",
                            data=html_report,
                            file_name=f"inteligencia_catchai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html"
                        )
        
        with col2:
            if st.button("📋 Resumen Ejecutivo Consolidado", type="secondary"):
                with st.spinner("Generando resumen ejecutivo..."):
                    # Generar análisis de todos los documentos
                    collection_data = st.session_state.embedder.collection.get()
                    
                    doc_contents = {}
                    for doc, metadata in zip(collection_data['documents'], collection_data['metadatas']):
                        source = metadata.get('source', 'unknown')
                        if source not in doc_contents:
                            doc_contents[source] = []
                        doc_contents[source].append(doc)
                    
                    analyses = []
                    for filename, chunks in doc_contents.items():
                        content = "\n\n".join(chunks)
                        analysis = st.session_state.intelligence_generator.analyze_document_intelligence(
                            content, filename
                        )
                        analyses.append(analysis)
                    
                    # Generar resumen ejecutivo
                    executive_summary = st.session_state.intelligence_generator.create_executive_summary(analyses)
                    
                    st.markdown("### 📊 Resumen Ejecutivo Consolidado")
                    st.markdown(executive_summary)


def main():
    """Función principal"""
    # Inicializar estado de sesión
    init_session_state()
    
    # Aplicar sistema de marcas de agua
    watermark_manager = apply_watermarks()
    
    # Mostrar splash screen solo la primera vez
    if 'splash_shown' not in st.session_state:
        st.markdown(show_splash_screen(), unsafe_allow_html=True)
        st.session_state.splash_shown = True
    
    # Header premium con marca de agua
    watermark_manager.render_premium_header()
    
    # Renderizar encabezado tradicional (comentado para usar el premium)
    # render_header()
    
    # Verificar configuración
    if not os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY') == 'your_groq_api_key_here':
        st.error("""
        🔑 **Configuración requerida:**
        
        1. Copia `env.example` a `.env`
        2. Obtén tu API key de Groq: https://console.groq.com/
        3. Configura `GROQ_API_KEY` en el archivo `.env`
        4. Reinicia la aplicación
        """)
        st.stop()
    
    # Inicializar sistema
    if not st.session_state.system_initialized:
        if not initialize_system():
            st.stop()
    
    # Renderizar barra lateral
    render_sidebar()
    
    # Crear tabs principales
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📁 Subir Documentos", 
        "💬 Conversación Plus", 
        "🔧 Funciones Extras",
        "📊 Análisis Visual",
        "📋 Reportes",
        "🚀 Premium Features"
    ])
    
    with tab1:
        render_upload_section()
    
    with tab2:
        render_chat_section()
    
    with tab3:
        render_extras_section()
    
    with tab4:
        render_visual_analysis_section()
    
    with tab5:
        render_reports_section()
    
    with tab6:
        render_premium_features_section()
    
    # Footer con marca de agua premium
    watermark_manager.render_footer_branding()


if __name__ == "__main__":
    main()
