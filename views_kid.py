# -*- coding: utf-8 -*-
import streamlit as st
from database import run_query
from utils import t, get_balance
from datetime import datetime

def render_kid_view():
    """
    Interface da Criança v13.1.
    FIX: Remoção de componentes vazios e ícones duplicados.
    """
    uid = st.session_state.user_id
    balance = get_balance(uid)
    
    # --- SEÇÃO HERO: SALDO CENTRAL ---
    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">{t('bal')}</div>
        <div class="hero-value">R$ {balance:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (FIX: Usando apenas t(key) para evitar ícones duplicados) ---
    t_extrato, t_missoes, t_cambio = st.tabs([
        t('home'),      # 'Extrato e Histórico' (ícone já vem do utils.py)
        t('missions'),  # 'Missões'
        t('tools')      # 'Ferramentas'
    ])
    
    # --- ABA 1: EXTRATO ---
    with t_extrato:
        # FIX: Removida a div liquid-card manual que causava a barra vazia
        st.markdown("##### Últimas Movimentações")
        hist = run_query("""
            SELECT description, amount, timestamp 
            FROM transactions 
            WHERE user_id=:u 
            ORDER BY id DESC LIMIT 5
        """, {'u': uid})
        
        if hist is not None and not hist.empty:
            # Usamos o container nativo com borda para envelopar o conteúdo Streamlit corretamente
            with st.container(border=True):
                for _, r in hist.iterrows():
                    cor = "#00f2ff" if r['amount'] >= 0 else "#ff4b4b"
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <div style="font-size:0.9rem;">{r['description']}</div>
                        <div style="color:{cor}; font-weight:700; font-family:'JetBrains Mono';">R$ {r['amount']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma movimentação encontrada.")

    # --- ABA 2: MISSÕES ---
    with t_missoes:
        st.markdown("##### Minhas Missões Ativas")
        m = run_query("SELECT * FROM chores WHERE assigned_to=:u AND status='open'", {'u': uid})
        
        if m is not None and not m.empty:
            for _, c in m.iterrows():
                # FIX: st.container(border=True) evita o componente vazio na renderização
                with st.container(border=True):
                    st.markdown(f"**{c['description']}**")
                    st.write(f"Recompensa: **R$ {c['reward']:.2f}**")
                    if st.button("CONCLUIR TAREFA", key=f"c_{c['id']}", use_container_width=True):
                        run_query("UPDATE chores SET status='pending' WHERE id=:id", {'id':c['id']}, commit=True)
                        st.toast("Enviado para aprovação! 🚀")
                        st.rerun()
        else:
            st.markdown("<div class='liquid-card' style='text-align:center; opacity:0.6;'>Tudo em dia por aqui! 🏖️</div>", unsafe_allow_html=True)

    # --- ABA 3: FERRAMENTAS (CÂMBIO) ---
    with t_cambio:
        usd = 5.05
        # Elementos HTML puros podem continuar usando liquid-card sem problemas
        st.markdown(f"""
        <div class='liquid-card' style='text-align:center;'>
            <div class='hero-label'>PATRIMÔNIO EM DÓLAR</div>
            <div style='font-size:2rem; font-weight:800; color:#00f2ff; font-family:JetBrains Mono;'>US$ {balance/usd:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>OBSIDIAN LIQUID UI • v13.1</div>", unsafe_allow_html=True)
