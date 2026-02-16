# -*- coding: utf-8 -*-
import streamlit as st
from database import run_query
from utils import t, get_balance
from datetime import datetime
import time

def render_kid_view():
    """
    Interface da Criança v13.6 - Banco Riparitech.
    - Notificações removidas.
    - Câmbio USD/EUR integrado.
    - Transferências entre utilizadores restauradas.
    - Design Liquid UI sem componentes vazios.
    """
    uid = st.session_state.user_id
    balance = get_balance(uid)
    
    # --- SECÇÃO HERO: EXIBIÇÃO DO SALDO CENTRAL ---
    # Foco na legibilidade e impacto visual do património
    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">{t('bal')}</div>
        <div class="hero-value">R$ {balance:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (TABS) ---
    # Nomes extraídos dinamicamente do utils.py
    t_extrato, t_missoes, t_transfer, t_cambio = st.tabs([
        t('home'),      # Extracto e Histórico
        t('missions'),  # Missões
        t('transfer'),  # Transferir
        t('tools')      # Câmbio
    ])
    
    # --- ABA 1: EXTRACTO E MOVIMENTAÇÕES ---
    with t_extrato:
        st.markdown("##### Últimas Movimentações")
        hist = run_query("""
            SELECT description, amount, timestamp 
            FROM transactions 
            WHERE user_id=:u 
            ORDER BY id DESC LIMIT 5
        """, {'u': uid})
        
        if hist is not None and not hist.empty:
            # Uso de container com borda para garantir um layout limpo
            with st.container(border=True):
                for _, r in hist.iterrows():
                    cor = "#00f2ff" if r['amount'] >= 0 else "#ff4b4b"
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <div style="font-size:0.9rem; opacity:0.8;">{r['description']}</div>
                        <div style="color:{cor}; font-weight:700; font-family:'JetBrains Mono';">R$ {r['amount']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Ainda não existem movimentações registadas.")

    # --- ABA 2: MISSÕES (TAREFAS DISPONÍVEIS) ---
    with t_missoes:
        st.markdown("##### As Tuas Missões Activas")
        m = run_query("SELECT * FROM chores WHERE assigned_to=:u AND status='open' ORDER BY created_at DESC", {'u': uid})
        
        if m is not None and not m.empty:
            for _, c in m.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{c['description']}**")
                    st.write(f"Recompensa: **R$ {c['reward']:.2f}**")
                    if st.button("CONCLUIR MISSÃO", key=f"c_{c['id']}", use_container_width=True):
                        run_query("UPDATE chores SET status='pending' WHERE id=:id", {'id':c['id']}, commit=True)
                        st.toast("Enviado para o Comando! 🚀")
                        st.rerun()
        else:
            st.markdown("<div class='liquid-card' style='text-align:center; opacity:0.6;'>Tudo em dia por agora! 🏖️</div>", unsafe_allow_html=True)

    # --- ABA 3: TRANSFERÊNCIA ENTRE CONTAS ---
    with t_transfer:
        st.markdown(f"##### {t('send_money')}")
        # Procura outros utilizadores do tipo 'user'
        siblings = run_query("SELECT id, name FROM users WHERE role='user' AND id != :uid", {'uid': uid})
        
        if siblings is not None and not siblings.empty:
            with st.container(border=True):
                with st.form("transfer_form_liquid", clear_on_submit=True):
                    target_name = st.selectbox(t('to_whom'), siblings['name'].tolist())
                    amount = st.number_input(t('how_much'), min_value=1.0, step=1.0)
                    reason = st.text_input(t('reason'), placeholder="Ex: Pagamento de lanche")
                    
                    if st.form_submit_button(t('send_now'), use_container_width=True):
                        if amount > balance:
                            st.error("Saldo insuficiente para esta operação.")
                        else:
                            target_id = siblings[siblings['name'] == target_name]['id'].values[0]
                            
                            # Execução da transacção dupla (Débito e Crédito)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Envio')", 
                                      {'u': uid, 'a': -amount, 'd': f"Para {target_name}: {reason}"}, commit=True)
                            
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Recebimento')", 
                                      {'u': int(target_id), 'a': amount, 'd': f"De {st.session_state.user_name}: {reason}"}, commit=True)
                            
                            st.success(f"Transferência de R$ {amount:.2f} realizada!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info(t('no_transfer'))

    # --- ABA 4: CÂMBIO (SIMULADOR USD/EUR) ---
    with t_cambio:
        st.markdown("##### Conversão de Património")
        # Taxas de referência para simulação
        usd_rate, eur_rate = 5.05, 5.45
        
        c_usd, c_eur = st.columns(2)
        
        with c_usd:
            st.markdown(f"""
            <div class='liquid-card' style='text-align:center;'>
                <div class='hero-label'>DÓLAR (USD)</div>
                <div style='font-size:1.8rem; font-weight:800; color:#00f2ff; font-family:JetBrains Mono; margin-top:10px;'>
                    US$ {balance/usd_rate:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_eur:
            st.markdown(f"""
            <div class='liquid-card' style='text-align:center;'>
                <div class='hero-label'>EURO (EUR)</div>
                <div style='font-size:1.8rem; font-weight:800; color:#7000ff; font-family:JetBrains Mono; margin-top:10px;'>
                    € {balance/eur_rate:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Rodapé institucional v13.6
    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>BANCO RIPARITECH • v13.6</div>", unsafe_allow_html=True)
