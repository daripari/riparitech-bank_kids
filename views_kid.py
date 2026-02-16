# -*- coding: utf-8 -*-
import streamlit as st
from database import run_query
from utils import t, get_balance
from datetime import datetime
import time

def render_kid_view():
    """
    Interface da Criança v13.2.
    RESTORED: Funcionalidade de transferência entre kids.
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
    # Adicionada a aba de transferência (t_transfer)
    t_extrato, t_missoes, t_transfer, t_cambio = st.tabs([
        t('home'),      # 'Extrato e Histórico'
        t('missions'),  # 'Missões'
        t('transfer'),  # 'Transferir'
        t('tools')      # 'Ferramentas'
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
                        st.toast("Enviado para aprovação! 🚀")
                        st.rerun()
        else:
            st.markdown("<div class='liquid-card' style='text-align:center; opacity:0.6;'>Tudo em dia por aqui! 🏖️</div>", unsafe_allow_html=True)

    # --- ABA 3: TRANSFERÊNCIA (RESTORED) ---
    with t_transfer:
        st.markdown(f"##### {t('send_money')}")
        # Buscar outros usuários kids (role user) para transferência
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
                            st.warning("Insira um valor maior que zero.")
                        else:
                            target_id = siblings[siblings['name'] == target_name]['id'].values[0]
                            
                            # Transação de saída para o remetente
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Transferência Enviada')", 
                                      {'u': uid, 'a': -amount, 'd': f"Para {target_name}: {reason}"}, commit=True)
                            
                            # Transação de entrada para o destinatário
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Transferência Recebida')", 
                                      {'u': int(target_id), 'a': amount, 'd': f"De {st.session_state.user_name}: {reason}"}, commit=True)
                            
                            st.success(f"R$ {amount:.2f} enviados para {target_name}!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info(t('no_transfer'))

    # --- ABA 4: FERRAMENTAS (CÂMBIO) ---
    with t_cambio:
        usd = 5.05
        st.markdown(f"""
        <div class='liquid-card' style='text-align:center;'>
            <div class='hero-label'>PATRIMÔNIO EM DÓLAR</div>
            <div style='font-size:2rem; font-weight:800; color:#00f2ff; font-family:JetBrains Mono;'>US$ {balance/usd:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>OBSIDIAN LIQUID UI • v13.2</div>", unsafe_allow_html=True)
