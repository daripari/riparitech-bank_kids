# -*- coding: utf-8 -*-
import streamlit as st

def apply_styles():
    """Aplica o CSS v12.8 - Correção de Layout de Botões e Design Premium"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* --- CONFIGURAÇÃO DE BASE --- */
        html, body, [class*="css"] { 
            font-family: 'Inter', sans-serif; 
            background-color: #050505; 
            color: #E5E5E5; 
        }
        .stApp { background-color: #050505; }
        header, footer, #MainMenu { visibility: hidden !important; }

        /* --- LOGO IMPACTANTE --- */
        .obsidian-logo {
            font-size: 1.6rem; font-weight: 800; letter-spacing: -1px;
            background: linear-gradient(90deg, #00C6FF, #0072FF);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            line-height: 1.1;
        }
        
        /* --- GLASS CARDS --- */
        .glass-card {
            background: rgba(25, 25, 28, 0.7);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        /* --- 🚀 BOTÕES PREMIUM (CORREÇÃO DE QUEBRA DE TEXTO) --- */
        .stButton>button {
            border-radius: 12px !important;
            height: 42px !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            background: rgba(30, 30, 35, 0.6) !important;
            color: #FFFFFF !important;
            transition: all 0.2s ease-in-out !important;
            /* IMPEDE A QUEBRA DE TEXTO */
            white-space: nowrap !important;
            overflow: visible !important;
            padding: 0 15px !important;
            width: 100% !important;
        }

        .stButton>button:hover {
            border-color: #00C6FF !important;
            color: #00C6FF !important;
            background: rgba(40, 40, 45, 0.8) !important;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 198, 255, 0.2) !important;
        }

        /* BOTÃO PRIMÁRIO (LOGIN/LANÇAMENTOS) */
        div[data-testid="stFormSubmitButton"] button, .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #00C6FF, #0072FF) !important;
            border: none !important;
            font-weight: 700 !important;
        }

        /* --- AJUSTE PARA O SELETOR DE IDIOMA (COMBO) --- */
        .stSelectbox div[data-baseweb="select"] {
            background-color: #121214 !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            height: 42px !important;
        }

        /* --- MÉTRICAS --- */
        div[data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 700 !important;
            color: #00C6FF !important;
        }
    </style>
    """, unsafe_allow_html=True)
