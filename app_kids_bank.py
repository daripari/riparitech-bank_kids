# -*- coding: utf-8 -*-
import streamlit as st
import styles
import database
import utils
import views_kid
import views_admin
from database import run_query
from utils import t

# 1. SETUP DE PÁGINA (BRANDING RIPARITECH)
st.set_page_config(
    page_title="Banco Riparitech", 
    page_icon="💎", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Inicializar Banco de Dados e carregar Estilos Globais
database.init_db()
styles.apply_styles()

# 2. GESTÃO DE ESTADO DA SESSÃO
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'user_role' not in st.session_state: 
    st.session_state.user_role = ''
if 'lang' not in st.session_state: 
    st.session_state.lang = 'pt'
if 'user_name' not in st.session_state: 
    st.session_state.user_name = ''
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# 3. COMPONENTES DE INTERFACE (LIQUID HEADER)
def render_liquid_header():
    """Cabeçalho Riparitech PT-BR v13.7"""
    st.markdown(f"""
    <div class="main-header">
        <div class="logo-text">💎 BANCO RIPARITECH</div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span style="font-size: 0.7rem; opacity: 0.4; letter-spacing: 1px;">V13.7 PREMIUM</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra de Ferramentas: [Espaço, Idioma, Atualizar, Sair]
    c_spacer, c_lang, c_ref, c_out = st.columns([1.8, 0.5, 0.5, 0.4])
    
    with c_lang:
        langs = {'🇧🇷 PT': 'pt', '🇺🇸 EN': 'en', '🇪🇸 ES': 'es'}
        curr = st.session_state.lang
        idx = list(langs.values()).index(curr) if curr in langs.values() else 0
        sel = st.selectbox("L", options=list(langs.keys()), index=idx, label_visibility="collapsed", key="liquid_lang")
        
        if langs[sel] != st.session_state.lang:
            st.session_state.lang = langs[sel]
            if st.session_state.logged_in:
                run_query("UPDATE users SET language=:l WHERE id=:id", 
                          params={'l': langs[sel], 'id': st.session_state.user_id}, commit=True)
            st.rerun()

    with c_ref:
        if st.button(f"🔄 {t('refresh')}", key="liquid_refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with c_out:
        if st.button(f"🚪 {t('logout')}", key="liquid_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

def render_login_liquid():
    """Tela de Login Riparitech PT-BR"""
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<div class='logo-text' style='text-align:center; font-size:3rem; margin-bottom:1rem;'>RIPARITECH</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888; margin-top:-10px; margin-bottom:30px; letter-spacing:2px;'>FAMILY BANKING</p>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='liquid-card'>", unsafe_allow_html=True)
            u = st.text_input("USUÁRIO", placeholder="Seu nome...").lower().strip()
            p = st.text_input("SENHA", type="password", placeholder="••••••").strip()
            
            if st.button("AUTENTICAR", use_container_width=True, type="primary"):
                df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
                if df is not None and not df.empty:
                    st.session_state.update({
                        'logged_in': True, 
                        'user_id': int(df.iloc[0]['id']),
                        'user_name': df.iloc[0]['name'], 
                        'user_role': df.iloc[0]['role'],
                        'lang': df.iloc[0]['language'] or 'pt'
                    })
                    st.rerun()
                else:
                    st.error("Acesso Negado. Verifique os dados.")
            st.markdown("</div>", unsafe_allow_html=True)

def main():
    if not st.session_state.logged_in:
        render_login_liquid()
    else:
        render_liquid_header()
        if st.session_state.user_role == 'admin':
            views_admin.render_admin_view()
        else:
            views_kid.render_kid_view()

if __name__ == "__main__":
    main()
