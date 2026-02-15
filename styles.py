# -*- coding: utf-8 -*-
import streamlit as st

def apply_styles():
    """Aplica o CSS Moderno v12.6 com foco em botões premium"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* --- BASE & TEMA ESCURO --- */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #050505;
            color: #E5E5E5;
        }
        .stApp { background-color: #050505; }
        #MainMenu, footer, header { visibility: hidden !important; }
        .block-container { padding-top: 2rem !important; max-width: 600px !important; }

        /* --- LOGO GRADIENTE --- */
        .obsidian-logo {
            font-size: 1.8rem; font-weight: 800; letter-spacing: -1px;
            background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem; text-align: center;
        }
        
        /* --- GLASS CARDS --- */
        .glass-card {
            background: rgba(20, 20, 23, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 24px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }

        /* --- 🚀 UPGRADE DE BOTÕES (O FOCO AQUI) --- */
        
        /* Botão Padrão (Secundário) */
        .stButton>button {
            border-radius: 14px !important;
            height: 48px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            background-color: #121214 !important;
            color: #D1D1D1 !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
            width: 100% !important;
        }

        .stButton>button:hover {
            border-color: #00C6FF !important;
            color: #00C6FF !important;
            background-color: #1A1A1E !important;
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 198, 255, 0.15) !important;
        }

        .stButton>button:active {
            transform: translateY(1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        }

        /* Botão Primário (Formulários) */
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #00C6FF 0%, #0072FF 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0, 114, 255, 0.3) !important;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            background: linear-gradient(135deg, #00D2FF 0%, #0082FF 100%) !important;
            box-shadow: 0 6px 20px rgba(0, 114, 255, 0.5) !important;
            transform: translateY(-2px) scale(1.01);
        }

        /* --- SALDO HERO --- */
        .balance-container { text-align: center; padding: 1.5rem 0; }
        .balance-label { font-size: 0.8rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }
        .balance-value { 
            font-family: 'JetBrains Mono', monospace; 
            font-size: 3.2rem; font-weight: 800; 
            color: #FFFFFF; letter-spacing: -2px;
            text-shadow: 0 0 30px rgba(0, 198, 255, 0.4);
        }

        /* --- INPUTS MODERNOS --- */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #0A0A0C !important;
            border: 1px solid rgba(255,255,255,0.08) !important;
            border-radius: 14px !important;
            color: white !important;
            height: 45px !important;
        }
        .stTextInput input:focus { border-color: #00C6FF !important; }

        /* --- TABS --- */
        .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #27272A; gap: 10px; }
        .stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; color: #6B7280; font-weight: 600; }
        .stTabs [aria-selected="true"] { color: #00C6FF !important; border-bottom: 2px solid #00C6FF !important; }

        /* --- CALCULADORA --- */
        .display-calc {
            background-color: #000000; border: 1px solid #1F1F23; border-radius: 16px; padding: 20px;
            text-align: right; font-size: 2.2rem; font-family: 'JetBrains Mono', monospace;
            color: #00E5FF; margin-bottom: 15px; min-height: 80px;
            display: flex; align-items: center; justify-content: flex-end;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.8);
        }
    </style>
    """, unsafe_allow_html=True)
