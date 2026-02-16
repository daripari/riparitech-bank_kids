# -*- coding: utf-8 -*-
import streamlit as st
import styles
import database
import utils
import views_kid
import views_admin
from database import run_query
from utils import t

# 1. CONFIGURAÇÃO INICIAL DO AMBIENTE
# O layout 'wide' é obrigatório para a fluidez da interface Liquid UI v13.0
st.set_page_config(
    page_title="Banco Obsidian",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar o Motor de Banco de Dados e carregar Estilos Globais
database.init_db()
styles.apply_styles()

# 2. GESTÃO DE ESTADO DA SESSÃO (SESSION STATE)
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
    """Renderiza o cabeçalho fixo com a ordem de botões atualizada: Idioma seguido de Notificações"""
    st.markdown(f"""
    <div class="main-header">
        <div class="logo-text">💎 BANCO OBSIDIAN</div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span style="font-size: 0.7rem; opacity: 0.4; letter-spacing: 1px;">V13.0 PREMIUM</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Barra de Ferramentas (Grid de controlo logo abaixo do Header)
    # Proporções: [Espaço, Idioma, Notificações, Refresh, Sair]
    c_spacer, c_lang, c_notif, c_ref, c_out = st.columns([1.2, 0.5, 0.6, 0.5, 0.4])
    
    with c_lang:
        # Seletor de Idioma (Invertido para a primeira posição de controlos)
        langs = {'🇧🇷 PT': 'pt', '🇺🇸 EN': 'en', '🇪🇸 ES': 'es'}
        curr = st.session_state.lang
        idx = list(langs.values()).index(curr) if curr in langs.values() else 0
        sel = st.selectbox("Idioma", options=list(langs.keys()), index=idx, label_visibility="collapsed", key="liquid_lang")
        
        if langs[sel] != st.session_state.lang:
            st.session_state.lang = langs[sel]
            if st.session_state.logged_in:
                run_query("UPDATE users SET language=:l WHERE id=:id", 
                          params={'l': langs[sel], 'id': st.session_state.user_id}, commit=True)
            st.rerun()

    with c_notif:
        # Botão de Notificações (Invertido para a segunda posição de controlos)
        if st.button(f"🔔 {t('notifs')}", key="liquid_notif", use_container_width=True):
            st.toast("Central de notificações em manutenção 🛠️")

    with c_ref:
        # Botão de Sincronização/Refresh
        if st.button(f"🔄 {t('refresh')}", key="liquid_refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with c_out:
        # Botão de Logout
        if st.button(f"🚪 {t('logout')}", key="liquid_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

def render_login_liquid():
    """Interface de Autenticação com estética Glassmorphism centrada"""
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1, 1.2, 1])
    
    with col_mid:
        st.markdown("<div class='logo-text' style='text-align:center; font-size:3.5rem; margin-bottom:1.5rem;'>OBSIDIAN</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#888; margin-top:-20px; margin-bottom:30px; letter-spacing:2px;'>FAMILY BANKING</p>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='liquid-card'>", unsafe_allow_html=True)
            u = st.text_input("USUÁRIO", placeholder="Introduza o seu nome...").lower().strip()
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
                    st.error("Dados de acesso inválidos. Verifique o utilizador e a senha.")
            st.markdown("</div>", unsafe_allow_html=True)

# 4. ORQUESTRADOR PRINCIPAL (MAIN LOOP)
def main():
    if not st.session_state.logged_in:
        render_login_liquid()
    else:
        render_liquid_header()
        
        # Seleção da visão baseada no perfil do utilizador
        if st.session_state.user_role == 'admin':
            views_admin.render_admin_view()
        else:
            views_kid.render_kid_view()

if __name__ == "__main__":
    main()
