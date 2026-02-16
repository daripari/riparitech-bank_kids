# -*- coding: utf-8 -*-
import streamlit as st
import styles
import database
import utils
import views_kid
import views_admin
from database import run_query

# 1. Configurar Página e Estilos
# Nota: set_page_config já foi chamado em styles.py ou deve ser chamado aqui como primeira linha.
# Como já quebramos, vamos deixar aqui.
# st.set_page_config... (já está no styles ou vamos assumir que styles é só CSS)
# Ajuste: set_page_config deve ser a primeira instrução Streamlit.
# Então, movemos para cá se styles for apenas string, mas styles.apply_styles() funciona bem.

# Inicializar Banco
database.init_db()

# Aplicar CSS
styles.apply_styles()

# 2. Inicializar Estado
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_role' not in st.session_state: st.session_state.user_role = ''
if 'calc_expr' not in st.session_state: st.session_state.calc_expr = ""

# 3. Componentes de UI Compartilhados
def render_header():
    c1, c2 = st.columns([0.8, 0.2])
    with c1: st.markdown(f"<div class='obsidian-logo' style='text-align:left;'>💎 BANCO DA FAMÍLIA</div>", unsafe_allow_html=True)
    with c2:
        if st.button("🚪", key="logout_main"): 
            st.session_state.logged_in = False
            st.rerun()

def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div class='obsidian-logo'>💎 BANCO DA FAMÍLIA</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6B7280; font-size:0.9rem;'>Sistema Modular v12.2</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        u = st.text_input("Usuário", placeholder="Digite seu nome").lower().strip()
        p = st.text_input("Senha", type="password", placeholder="••••••").strip()
        
        if st.button("ACESSAR SISTEMA", use_container_width=True, type="primary"):
            df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
            if df is not None and not df.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = int(df.iloc[0]['id'])
                st.session_state.user_name = df.iloc[0]['name']
                st.session_state.user_role = df.iloc[0]['role']
                st.rerun()
            else:
                st.error("Credenciais Inválidas")
        st.markdown("</div>", unsafe_allow_html=True)

# 4. Loop Principal
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
