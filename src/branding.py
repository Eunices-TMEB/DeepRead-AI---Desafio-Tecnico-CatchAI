"""
Sistema de marca de agua y branding para CatchAI v3.0
"""

import streamlit as st
import base64
from datetime import datetime
from typing import Optional


class WatermarkManager:
    """Gestor de marcas de agua y branding"""
    
    def __init__(self):
        self.brand_name = "DeepRead AI"
        self.brand_tagline = "Desafío Técnico CatchAI"
        self.author = "Desarrollado para Eunices Trujillo - Desafío Técnico CatchAI"
        
    def render_floating_watermark(self):
        """Marca de agua flotante en esquina superior derecha"""
        watermark_css = """
        <style>
        .watermark-floating {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 9999;
            background: rgba(102, 126, 234, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 15px;
            padding: 8px 15px;
            font-size: 12px;
            font-weight: 600;
            color: #667eea;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .watermark-floating:hover {
            background: rgba(102, 126, 234, 0.2);
            transform: scale(1.05);
            transition: all 0.3s ease;
        }
        </style>
        <div class="watermark-floating">
            🧠 DeepRead AI
        </div>
        """
        st.markdown(watermark_css, unsafe_allow_html=True)
    
    def render_background_watermark(self):
        """Marca de agua de fondo sutil"""
        background_css = """
        <style>
        .main .block-container::before {
            content: "DeepRead AI";
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 8rem;
            font-weight: 900;
            color: rgba(102, 126, 234, 0.03);
            z-index: -1;
            pointer-events: none;
            user-select: none;
        }
        </style>
        """
        st.markdown(background_css, unsafe_allow_html=True)
    
    def render_premium_header(self):
        """Header premium con marca de agua elegante"""
        header_css = """
        <style>
        .premium-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        
        .premium-header::before {
            content: "";
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.1"/><circle cx="10" cy="50" r="1" fill="white" opacity="0.1"/><circle cx="90" cy="30" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            animation: drift 20s linear infinite;
            pointer-events: none;
        }
        
        @keyframes drift {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-50%, -50%); }
        }
        
        .header-content {
            position: relative;
            z-index: 2;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .brand-title {
            font-size: 2.5rem;
            font-weight: 900;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .brand-subtitle {
            font-size: 1rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        .version-badge {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 25px;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            font-weight: 600;
        }
        </style>
        
        <div class="premium-header">
            <div class="header-content">
                <div>
                    <div class="brand-title">🧠 DeepRead AI</div>
                    <div class="brand-subtitle">Desafío Técnico CatchAI - Copiloto Conversacional Inteligente para PDFs</div>
                </div>
                <div class="version-badge">
                    🏆 Desafío Técnico
                </div>
            </div>
        </div>
        """
        st.markdown(header_css, unsafe_allow_html=True)
    
    def render_footer_branding(self):
        """Footer minimalista con información de marca"""
        st.divider()
        
        # Footer simple y elegante
        footer_css = """
        <style>
        .minimal-footer {
            text-align: center;
            padding: 1.5rem;
            margin-top: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            font-size: 0.9rem;
        }
        .footer-brand {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        </style>
        """
        
        footer_html = """
        <div class="minimal-footer">
            <div class="footer-brand">🧠 DeepRead AI</div>
            <div>Eunices - Desafío Técnico CatchAI</div>
        </div>
        """
        
        st.markdown(footer_css, unsafe_allow_html=True)
        st.markdown(footer_html, unsafe_allow_html=True)
    
    def render_sidebar_branding(self):
        """Marca de agua en el sidebar"""
        sidebar_css = """
        <style>
        .sidebar-brand {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            text-align: center;
        }
        
        .sidebar-brand h3 {
            color: #667eea;
            margin: 0 0 0.5rem 0;
            font-size: 1.1rem;
        }
        
        .sidebar-brand p {
            margin: 0;
            font-size: 0.8rem;
            color: #666;
        }
        
        .version-info {
            background: rgba(102, 126, 234, 0.1);
            border-radius: 5px;
            padding: 0.5rem;
            margin-top: 0.5rem;
            font-size: 0.7rem;
            color: #667eea;
            font-weight: 600;
        }
        </style>
        
        <div class="sidebar-brand">
            <h3>🧠 DeepRead AI</h3>
            <p>Desafío Técnico CatchAI</p>
            <div class="version-info">
                🏆 Todas las funciones desbloqueadas
            </div>
        </div>
        """
        st.sidebar.markdown(sidebar_css, unsafe_allow_html=True)
    
    def render_document_watermark(self, content: str) -> str:
        """Agregar marca de agua a documentos generados"""
        watermark_text = f"""
        
---
*Generado por DeepRead AI - Desafío Técnico CatchAI*  
*Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*  
*Powered by Groq + Llama 3.1 70B + ChromaDB*  
*© 2025 DeepRead AI - Inteligencia Documental Avanzada*
---
        """
        return content + watermark_text
    
    def render_loading_splash(self):
        """Splash screen con marca de agua durante carga"""
        splash_css = """
        <style>
        .loading-splash {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            color: white;
            animation: fadeOut 3s ease-in-out forwards;
        }
        
        @keyframes fadeOut {
            0%, 80% { opacity: 1; }
            100% { opacity: 0; pointer-events: none; }
        }
        
        .splash-logo {
            font-size: 4rem;
            font-weight: 900;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 1rem;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .splash-subtitle {
            font-size: 1.5rem;
            opacity: 0.9;
            margin-bottom: 2rem;
        }
        
        .loading-bar {
            width: 300px;
            height: 4px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 2px;
            overflow: hidden;
        }
        
        .loading-progress {
            height: 100%;
            background: linear-gradient(90deg, #fff, #f0f0f0);
            border-radius: 2px;
            animation: loading 2s ease-in-out forwards;
        }
        
        @keyframes loading {
            0% { width: 0%; }
            100% { width: 100%; }
        }
        </style>
        
        <div class="loading-splash">
            <div class="splash-logo">🧠 DeepRead AI</div>
            <div class="splash-subtitle">Desafío Técnico CatchAI - Iniciando...</div>
            <div class="loading-bar">
                <div class="loading-progress"></div>
            </div>
        </div>
        """
        return splash_css
    
    def render_success_badge(self, message: str):
        """Badge de éxito con marca"""
        badge_css = """
        <style>
        .success-badge {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
            animation: successPulse 0.6s ease-out;
        }
        
        @keyframes successPulse {
            0% { transform: scale(0.8); opacity: 0; }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .success-badge .main-text {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .success-badge .sub-text {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        </style>
        """
        
        badge_html = f"""
        <div class="success-badge">
            <div class="main-text">✅ {message}</div>
            <div class="sub-text">Powered by DeepRead AI</div>
        </div>
        """
        
        st.markdown(badge_css + badge_html, unsafe_allow_html=True)


# Funciones de utilidad para aplicar marcas de agua
def apply_watermarks():
    """Aplicar todas las marcas de agua al sistema"""
    watermark = WatermarkManager()
    
    # Marca de agua flotante (siempre visible)
    watermark.render_floating_watermark()
    
    # Marca de agua de fondo sutil
    watermark.render_background_watermark()
    
    # Marca de agua en sidebar
    watermark.render_sidebar_branding()
    
    return watermark


def show_splash_screen():
    """Mostrar splash screen de carga"""
    watermark = WatermarkManager()
    return watermark.render_loading_splash()


def watermark_document(content: str) -> str:
    """Agregar marca de agua a contenido de documento"""
    watermark = WatermarkManager()
    return watermark.render_document_watermark(content)
