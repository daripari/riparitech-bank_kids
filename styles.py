# -*- coding: utf-8 -*-
import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* --- RESET & BASE --- */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #050505;
            color: #E5E5E5;
        }
        .stApp { background-color: #050505; }
        
        /* --- ESCONDER ITENS PADRÃO --- */
        #MainMenu, footer, header { visibility: hidden !important; }
        .block-container { padding-top: 2rem !important; max-width: 600px !important; }
    
        /* --- LOGO & BRANDING --- */
        .obsidian-logo {
            font-size: 1.8rem; font-weight: 800; letter-spacing: -1px;
            background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem; text-align: center;
        }
        
        /* --- CARDS & CONTAINERS --- */
        .glass-card {
            background: rgba(20, 20, 23, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease;
        }
        .glass-card:hover { border-color: rgba(0, 198, 255, 0.3); }
    
        /* --- SALDO EM DESTAQUE --- */
        .balance-container { text-align: center; padding: 2rem 0; }
        .balance-label { font-size: 0.8rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; }
        .balance-value { 
            font-family: 'JetBrains Mono', monospace; 
            font-size: 3.5rem; font-weight: 800; 
            color: #FFFFFF; letter-spacing: -2px;
            text-shadow: 0 0 40px rgba(0, 198, 255, 0.3);
        }
        
        /* --- BOTÕES OTIMIZADOS --- */
        .stButton>button {
            border-radius: 16px !important;
            height: 50px !important;
            font-weight: 600 !important;
            border: none !important;
            background-color: #1A1A1E !important;
            color: #FFFFFF !important;
            transition: all 0.2s !important;
        }
        .stButton>button:hover {
            background-color: #27272A !important;
            transform: scale(1.02);
            color: #00C6FF !important;
        }
        /* Botão Primário */
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(90deg, #00C6FF 0%, #0072FF 100%) !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 15px rgba(0, 114, 255, 0.4);
        }
    
        /* --- INPUTS --- */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #0A0A0C !important;
            border: 1px solid #27272A !important;
            border-radius: 12px !important;
            color: white !important;
        }
    
        /* --- TABS CLEAN --- */
        .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #27272A; gap: 10px; }
        .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; color: #6B7280; font-weight: 600; font-size: 0.9rem; padding: 10px 15px; }
        .stTabs [aria-selected="true"] { color: #00C6FF !important; background-color: rgba(0, 198, 255, 0.05); border-bottom: 2px solid #00C6FF !important; }
    
        /* --- STATUS BADGES --- */
        .badge-done { background: rgba(16, 185, 129, 0.2); color: #10B981; padding: 4px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
        .badge-pending { background: rgba(245, 158, 11, 0.2); color: #F59E0B; padding: 4px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
        .badge-late { background: rgba(239, 68, 68, 0.2); color: #EF4444; padding: 4px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
        
        /* --- CALCULADORA --- */
        .display-calc {
            background-color: #050506; border: 2px solid #1F1F23; border-radius: 16px; padding: 20px;
            text-align: right; font-size: 2.2rem; font-family: 'JetBrains Mono', monospace;
            color: #00E5FF; margin-bottom: 15px; min-height: 80px;
            display: flex; align-items: center; justify-content: flex-end;
            box-shadow: inset 0 2px 15px rgba(0,0,0,0.9);
        }
    </style>
    """, unsafe_allow_html=True)
