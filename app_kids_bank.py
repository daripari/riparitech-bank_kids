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
st.set_page_config(
    page_title="Banco da Família Obsidian", 
    page_icon="💎", 
    layout="wide", # Layout Wide é obrigatório para o novo cabeçalho
    initial_sidebar_state="collapsed"
)

# Inicializar Banco e Estilos
database.init_db()
styles.apply_styles()

# 2. ESTADO DA SESSÃO
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = ''
if 'lang' not in st.session_state:
    st.session_state.lang = 'pt'
if 'show_notifs' not in st.session_state:
    st.session_state.show_notifs = False
if 'calc_expr' not in st.session_state:
    st.session_state.calc_expr = ""

# 3. CABEÇALHO (HEADER FIX)
def render_header():
    """Renderiza o cabeçalho com botões visíveis (Texto + Ícone)"""
    # Colunas com espaçamento generoso para evitar que os botões desapareçam
    c_logo, c_notif, c_lang, c_ref, c_out = st.columns([1.5, 0.7, 0.6, 0.7, 0.5])
    
    with c_logo:
        st.markdown(f"<div class='obsidian-logo' style='text-align:left; padding-top:10px;'>💎 BANCO DA FAMÍLIA</div>", unsafe_allow_html=True)
    
    with c_notif:
        if st.button(f"🔔 {t('notifs')}", key="h_notif", use_container_width=True):
            st.session_state.show_notifs = not st.session_state.show_notifs
    
    with c_lang:
        langs = {'🇧🇷 PT': 'pt', '🇺🇸 EN': 'en', '🇪🇸 ES': 'es'}
        curr_lang = st.session_state.lang
        idx = list(langs.values()).index(curr_lang) if curr_lang in langs.values() else 0
        
        sel = st.selectbox("L", options=list(langs.keys()), index=idx, label_visibility="collapsed", key="h_lang")
        if langs[sel] != st.session_state.lang:
            st.session_state.lang = langs[sel]
            if st.session_state.logged_in:
                run_query("UPDATE users SET language=:l WHERE id=:id", params={'l': langs[sel], 'id': st.session_state.user_id}, commit=True)
            st.rerun()

    with c_ref:
        if st.button(f"🔄 {t('refresh')}", key="h_ref", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    with c_out:
        if st.button(f"🚪 {t('logout')}", key="h_out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # Janela de Notificações
    if st.session_state.show_notifs:
        st.markdown(f"<div class='glass-card' style='border-color:#00C6FF; margin-top:5px;'><b>{t('notifs')}</b><br><small>Nenhum alerta novo.</small></div>", unsafe_allow_html=True)

def render_login():
    """Tela de Login Centralizada"""
    st.markdown("<div style='text-align:center; padding-top:50px;'><div class='obsidian-logo' style='font-size:3rem;'>💎 BANCO DA FAMÍLIA</div></div>", unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1, 1.5, 1])
    with col_mid:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        u = st.text_input("Usuário").lower().strip()
        p = st.text_input("Senha", type="password").strip()
        if st.button("AUTENTICAR", use_container_width=True, type="primary"):
            df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
            if df is not None and not df.empty:
                st.session_state.update({
                    'logged_in': True, 'user_id': int(df.iloc[0]['id']),
                    'user_name': df.iloc[0]['name'], 'user_role': df.iloc[0]['role'],
                    'lang': df.iloc[0]['language'] or 'pt'
                })
                st.rerun()
            else: st.error("Dados incorretos.")
        st.markdown("</div>", unsafe_allow_html=True)

def main():
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
