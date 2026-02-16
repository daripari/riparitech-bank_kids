# -*- coding: utf-8 -*-
import streamlit as st
from database import run_query
from utils import t, get_balance
from datetime import datetime
import time

def render_kid_view():
    """
    Interface da Criança v13.4.
    REBRANDED: BANCO RIPARITECH.
    FIX: Remoção de componentes vazios e ícones duplicados.
    UPDATED: Aba de câmbio com conversão USD/EUR.
    """
    uid = st.session_state.user_id
    balance = get_balance(uid)
    
    # --- SECÇÃO HERO: EXIBIÇÃO DO SALDO CENTRAL ---
    # Utiliza as classes de CSS definidas no styles.py para o efeito de profundidade
    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">{t('bal')}</div>
        <div class="hero-value">R$ {balance:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (TABS LIQUID) ---
    # Os nomes das abas são extraídos dinamicamente do utils.py
    t_extrato, t_missoes, t_transfer, t_cambio = st.tabs([
        t('home'),      # 'Extrato e Histórico'
        t('missions'),  # 'Missões'
        t('transfer'),  # 'Transferir'
        t('tools')      # 'Câmbio'
    ])
    
    # --- ABA 1: EXTRATO ---
    with t_extrato:
        st.markdown("##### Últimas Movimentações")
        hist = run_query("""
            SELECT description, amount, timestamp 
            FROM transactions 
            WHERE user_id=:u 
            ORDER BY id DESC LIMIT 5
        """, {'u': uid})
        
        if hist is not None and not hist.empty:
            # Container nativo com borda para evitar artefactos visuais
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
                with st.container(border=True):
                    st.markdown(f"**{c['description']}**")
                    st.write(f"Recompensa: **R$ {c['reward']:.2f}**")
                    if st.button("CONCLUIR TAREFA", key=f"c_{c['id']}", use_container_width=True):
                        run_query("UPDATE chores SET status='pending' WHERE id=:id", {'id':c['id']}, commit=True)
                        st.toast("Enviado para aprovação do Comando! 🚀")
                        st.rerun()
        else:
            st.markdown("<div class='liquid-card' style='text-align:center; opacity:0.6;'>Tudo em dia por aqui! 🏖️</div>", unsafe_allow_html=True)

    # --- ABA 3: TRANSFERÊNCIA ---
    with t_transfer:
        st.markdown(f"##### {t('send_money')}")
        siblings = run_query("SELECT id, name FROM users WHERE role='user' AND id != :uid", {'uid': uid})
        
        if siblings is not None and not siblings.empty:
            with st.container(border=True):
                with st.form("transfer_form_liquid", clear_on_submit=True):
                    target_name = st.selectbox(t('to_whom'), siblings['name'].tolist())
                    amount = st.number_input(t('how_much'), min_value=0.0, step=1.0)
                    reason = st.text_input(t('reason'), placeholder="Ex: Pagamento de lanche")
                    
                    if st.form_submit_button(t('send_now'), use_container_width=True):
                        if amount > balance:
                            st.error("Saldo insuficiente para esta transferência.")
                        elif amount <= 0:
                            st.warning("Insira um valor válido.")
                        else:
                            target_id = siblings[siblings['name'] == target_name]['id'].values[0]
                            # Débito no remetente
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Transferência Enviada')", 
                                      {'u': uid, 'a': -amount, 'd': f"Para {target_name}: {reason}"}, commit=True)
                            # Crédito no destinatário
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Transferência Recebida')", 
                                      {'u': int(target_id), 'a': amount, 'd': f"De {st.session_state.user_name}: {reason}"}, commit=True)
                            st.success(f"Enviado com sucesso para {target_name}!")
                            time.sleep(1); st.rerun()
        else:
            st.info(t('no_transfer'))

    # --- ABA 4: CÂMBIO ---
    with t_cambio:
        st.markdown("##### Conversão de Património")
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

    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>RIPARITECH LIQUID UI • v13.4</div>", unsafe_allow_html=True)
