# -*- coding: utf-8 -*-
import streamlit as st
from .themes import get_theme_css

def apply_styles(theme_name='default'):
    """Aplica a interface Obsidian Liquid UI v13.0 - Disruptiva e Responsiva"""
    
    theme_css = get_theme_css(theme_name)
    
    st.markdown(f"""
    <style>
        {theme_css}
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* --- RESET & ESTRUTURA GLOBAL --- */
        html, body, [class*="css"] {{
            font-family: 'Outfit', sans-serif;
            background: #020203;
            color: #f0f0f0;
        }}
        
        .stApp {{
            background: radial-gradient(circle at 50% -20%, #1a1a2e 0%, #020203 80%);
        }}
        
        h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {{
            color: #e0e0e0 !important;
        }}
        
        /* --- TEXTOS GERAIS E TABELAS --- */
        p, .stMarkdown p, [data-testid="stDataFrame"] *, [data-testid="stTable"] * {{
            color: #e0e0e0 !important;
        }}
        
        header, footer, #MainMenu {{ visibility: hidden !important; }}
        .block-container {{ padding: 1rem !important; max-width: 1200px !important; }}

        /* --- HEADER FLUTUANTE (DISRUPTIVO) --- */
        .main-header {{
            position: sticky; top: 0; z-index: 1000;
            background: rgba(10, 10, 15, 0.7);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding: 15px 20px;
            margin: -1rem -1rem 1.5rem -1rem;
            display: flex; justify-content: space-between; align-items: center;
        }}
        
        .logo-text {{
            font-weight: 800; font-size: 1.4rem; letter-spacing: -1.5px;
            background: linear-gradient(135deg, var(--accent-color-1), var(--accent-color-2));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}

        /* --- CARDS LIQUID GLASS --- */
        .liquid-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 28px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }}
        .liquid-card:hover {{
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.05);
            border-color: color-mix(in srgb, var(--accent-color-1) 30%, transparent);
            box-shadow: 0 20px 40px color-mix(in srgb, var(--accent-color-1) 10%, transparent);
        }}

        /* --- TIPOGRAFIA DE SALDO --- */
        .hero-balance {{
            text-align: center; padding: 2rem 0;
        }}
        .hero-label {{
            font-size: 0.75rem; color: #e0e0e0; text-transform: uppercase; letter-spacing: 4px; font-weight: 600;
        }}
        .hero-value {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 4rem; font-weight: 800; color: #fff;
            margin: 10px 0; letter-spacing: -3px;
        }}
        
        /* --- BOTÕES PREMIUM --- */
        .stButton button, div[data-testid="stPopover"] button {{
            border-radius: 18px !important;
            height: 52px !important;
            font-weight: 800 !important;
            font-size: 0.9rem !important;
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #fff !important;
            transition: all 0.3s ease !important;
            width: 100% !important;
            text-transform: none; letter-spacing: 0px;
            white-space: nowrap !important;
        }}
        .stButton button:hover, div[data-testid="stPopover"] button:hover {{
            background: var(--accent-color-3) !important;
            color: var(--accent-color-4) !important;
            transform: scale(1.02);
        }}
        
        div[data-testid="stFormSubmitButton"] button {{
            background: linear-gradient(135deg, var(--accent-color-1), var(--accent-color-2)) !important;
            color: #fff !important;
            border: none !important;
            font-weight: 800 !important;
        }}

        /* --- GRID RESPONSIVO --- */
        @media (max-width: 768px) {{
            .hero-value {{ font-size: 2.8rem; }}
            .logo-text {{ font-size: 1.1rem; }}
            .liquid-card {{ padding: 16px; border-radius: 20px; }}
            .main-header {{ padding: 10px 15px; }}
        }}

        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; gap: 8px; flex-wrap: wrap; }}
        .stTabs [data-baseweb="tab"] {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 14px;
            padding: 8px 16px;
            color: #e0e0e0;
        }}
        .stTabs [aria-selected="true"] {{
            background: var(--accent-color-3) !important;
            color: #000000 !important;
            border: none !important;
        }}
        .stTabs [aria-selected="true"] p {{
            color: #000000 !important;
        }}
        
        /* --- POPOVER (MULTAS) --- */
        [data-testid="stPopoverBody"] * {{
            color: #1a1a1a !important;
        }}
        
        /* Botão dentro do popover deve ser escuro para contraste e consistência */
        [data-testid="stPopoverBody"] button {{
            background: #1a1a2e !important;
            color: #fff !important;
        }}
        /* Garante que o conteúdo interno dos botões (texto OK, símbolos +/-) seja branco */
        [data-testid="stPopoverBody"] button * {{
            color: #fff !important;
        }}

        [data-testid="stPopoverBody"] button:hover {{
            background: #999 !important;
            color: #1a1a1a !important;
        }}
        [data-testid="stPopoverBody"] button:hover * {{
            color: #1a1a1a !important;
        }}
    </style>
    """, unsafe_allow_html=True)
