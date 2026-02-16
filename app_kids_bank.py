# -*- coding: utf-8 -*-
import streamlit as st
import styles
import database
import utils
import views_kid
import views_admin
from database import run_query
from utils import t

# 1. CONFIGURAÇÃO INICIAL DO STREAMLIT
# O set_page_config deve ser sempre a primeira instrução Streamlit executada.
st.set_page_config(
    page_title="Banco da Família Obsidian", 
    page_icon="💎", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inicializar Tabelas do Banco de Dados
database.init_db()

# Aplicar Identidade Visual (CSS Moderno v12.5)
styles.apply_styles()

# 2. INICIALIZAÇÃO DO ESTADO DA SESSÃO (SESSION STATE)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = ''
if 'lang' not in st.session_state:
    st.session_state.lang = 'pt'
if 'calc_expr' not in st.session_state:
    st.session_state.calc_expr = ""

# 3. COMPONENTES DE INTERFACE COMPARTILHADOS (HEADER)
def render_header():
    """Renderiza o topo do App com Logo, Idioma, Refresh e Sair"""
    # Colunas: [Logo, Espaço, Idioma, Refresh, Sair]
    c1, c2, c3, c4, c5 = st.columns([1.0, 0.1, 0.4, 0.15, 0.15])
    
    with c1:
        st.markdown(f"<div class='obsidian-logo' style='text-align:left;'>💎 BANCO DA FAMÍLIA</div>", unsafe_allow_html=True)
    
    with c3:
        # Seletor de Idioma Internacional
        lang_options = {'🇧🇷 PT': 'pt', '🇺🇸 EN': 'en', '🇪🇸 ES': 'es'}
        inv_lang = {v: k for k, v in lang_options.items()}
        
        # Garante que o índice atual seja válido
        try:
            current_idx = list(lang_options.values()).index(st.session_state.lang)
        except ValueError:
            current_idx = 0
            
        selected_lang_label = st.selectbox(
            "Language", 
            options=list(lang_options.keys()), 
            index=current_idx,
            label_visibility="collapsed",
            key="global_lang_selector"
        )
        
        new_lang = lang_options[selected_lang_label]
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            # Se logado, tenta persistir a preferência no banco
            if st.session_state.logged_in:
                run_query("UPDATE users SET language=:l WHERE id=:id", 
                          params={'l': new_lang, 'id': st.session_state.user_id}, commit=True)
            st.rerun()

    with c4:
        # Botão de Refresh Tático (Limpa Cache e Atualiza)
        if st.button("🔄", help="Atualizar Dados"):
            st.cache_data.clear()
            st.rerun()

    with c5:
        # Botão de Logout (Sair)
        if st.button("🚪", help=t('logout')):
            st.session_state.logged_in = False
            st.rerun()

def render_login():
    """Interface de Autenticação Centralizada"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div class='obsidian-logo'>💎 BANCO DA FAMÍLIA</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6B7280; font-size:0.9rem;'>Sistema Financeiro Modular v12.5</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        u = st.text_input("Usuário", placeholder="Seu nome").lower().strip()
        p = st.text_input("Senha", type="password", placeholder="••••••").strip()
        
        if st.button("AUTENTICAR", use_container_width=True, type="primary"):
            df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
            if df is not None and not df.empty:
                # Carregar perfil do usuário para a sessão
                st.session_state.logged_in = True
                st.session_state.user_id = int(df.iloc[0]['id'])
                st.session_state.user_name = df.iloc[0]['name']
                st.session_state.user_role = df.iloc[0]['role']
                # Carregar idioma preferencial salvo
                if 'language' in df.columns and df.iloc[0]['language']:
                    st.session_state.lang = df.iloc[0]['language']
                st.rerun()
            else:
                st.error("Acesso Negado: Usuário ou Senha incorretos.")
        st.markdown("</div>", unsafe_allow_html=True)

# 4. ORQUESTRADOR PRINCIPAL
def main():
    """Função mestre que decide qual visão carregar"""
    if not st.session_state.logged_in:
        render_login()
    else:
        render_header()
        
        # Direcionamento baseado no cargo (Role)
        if st.session_state.user_role == 'admin':
            views_admin.render_admin_view()
        else:
            views_kid.render_kid_view()

# Início da Execução
if __name__ == "__main__":
    main()
