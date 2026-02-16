# -*- coding: utf-8 -*-
import streamlit as st
import styles
import database
import utils
import views_kid
import views_admin
from database import run_query
from utils import t

# 1. CONFIGURAÇÃO INICIAL (DEVE SER A PRIMEIRA LINHA)
# O layout "wide" é obrigatório para que os botões com texto caibam sem quebrar linhas
st.set_page_config(
    page_title="Banco da Família", 
    page_icon="💎", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Inicializar Banco de Dados e Estilos
database.init_db()
styles.apply_styles()

# 2. INICIALIZAÇÃO DO ESTADO DA SESSÃO
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'lang' not in st.session_state: 
    st.session_state.lang = 'pt'
if 'show_notifs' not in st.session_state: 
    st.session_state.show_notifs = False
if 'calc_expr' not in st.session_state: 
    st.session_state.calc_expr = ""

# 3. CABEÇALHO REESTRUTURADO (TEXTO + ÍCONE)
def render_header():
    """Renderiza o cabeçalho com proporções corrigidas para evitar quebras visuais"""
    # Proporções calculadas para dar espaço ao texto dos botões
    c_logo, c_notif, c_lang, c_ref, c_out = st.columns([1.5, 0.8, 0.6, 0.7, 0.5])
    
    with c_logo:
        # Logo em duas linhas para economizar espaço horizontal
        st.markdown("<div class='obsidian-logo'>💎 BANCO<br>DA FAMÍLIA</div>", unsafe_allow_html=True)
    
    with c_notif:
        # Botão Notificações
        if st.button(f"🔔 {t('notifs')}", key="h_notif", use_container_width=True):
            st.session_state.show_notifs = not st.session_state.show_notifs
    
    with c_lang:
        # Seletor de Idioma
        langs = {'🇧🇷 PT': 'pt', '🇺🇸 EN': 'en', '🇪🇸 ES': 'es'}
        curr = st.session_state.lang
        idx = list(langs.values()).index(curr) if curr in langs.values() else 0
        sel = st.selectbox("L", options=list(langs.keys()), index=idx, label_visibility="collapsed", key="h_lang")
        
        if langs[sel] != st.session_state.lang:
            st.session_state.lang = langs[sel]
            if st.session_state.logged_in:
                run_query("UPDATE users SET language=:l WHERE id=:id", params={'l': langs[sel], 'id': st.session_state.user_id}, commit=True)
            st.rerun()

    with c_ref:
        # Botão Atualizar
        if st.button(f"🔄 {t('refresh')}", key="h_ref", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with c_out:
        # Botão Sair
        if st.button(f"🚪 {t('logout')}", key="h_out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # Overlay de Notificações
    if st.session_state.show_notifs:
        st.markdown(f"""
            <div class='glass-card' style='border-color:#00C6FF; padding:10px; margin-top:5px;'>
                <b style='color:#00C6FF;'>{t('notifs')}</b><br>
                <small style='color:#9CA3AF;'>Nenhum alerta novo no momento.</small>
            </div>
        """, unsafe_allow_html=True)

def render_login():
    """Tela de Autenticação Centralizada"""
    st.markdown("<div style='text-align:center; padding:50px 0;'><div class='obsidian-logo' style='font-size:3.5rem;'>💎 BANCO DA FAMÍLIA</div></div>", unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1, 1.2, 1])
    with col_mid:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        u = st.text_input("Usuário", placeholder="Digite seu nome").lower().strip()
        p = st.text_input("Senha", type="password", placeholder="••••••").strip()
        
        if st.button("ENTRAR NO SISTEMA", use_container_width=True, type="primary"):
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
                st.error("Acesso Negado: Usuário ou Senha incorretos.")
        st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Orquestrador de Visão"""
    if not st.session_state.logged_in:
        render_login()
    else:
        render_header()
        if st.session_state.user_role == 'admin':
            views_admin.render_admin_view()
        else:
            views_kid.render_kid_view()

if __name__ == "__main__":
    main()
