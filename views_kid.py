# -*- coding: utf-8 -*-
import streamlit as st
from database import run_query
from utils import t, get_balance
from datetime import datetime
import time

def render_kid_view():
    """
    Interface do Usuário (Kid) v13.7 - Banco Riparitech.
    Foco: Português do Brasil (PT-BR), Câmbio USD/EUR e Transferências.
    """
    uid = st.session_state.user_id
    balance = get_balance(uid)
    
    # --- SEÇÃO HERO: SALDO CENTRAL ---
    # Layout disruptivo com foco no saldo em Reais
    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">{t('bal')}</div>
        <div class="hero-value">R$ {balance:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (PADRÃO PT-BR) ---
    t_extrato, t_missoes, t_transferencia, t_cambio = st.tabs([
        t('home'),      # Extrato e Histórico
        t('missions'),  # Missões
        t('transfer'),  # Transferir
        t('tools')      # Câmbio
    ])
    
    # --- ABA 1: EXTRATO (HISTÓRICO) ---
    with t_extrato:
        st.markdown("##### Últimas Movimentações")
        hist = run_query("""
            SELECT description, amount, timestamp 
            FROM transactions 
            WHERE user_id=:u 
            ORDER BY id DESC LIMIT 5
        """, {'u': uid})
        
        if hist is not None and not hist.empty:
            # Container com borda para evitar erro visual de "barra vazia"
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
            st.info("Ainda não há movimentações em sua conta.")

    # --- ABA 2: MISSÕES ATIVAS ---
    with t_missoes:
        st.markdown(f"##### {t('active_missions')}")
        m = run_query("""
            SELECT * FROM chores 
            WHERE assigned_to=:u AND status='open' 
            ORDER BY deadline ASC
        """, {'u': uid})
        
        if m is not None and not m.empty:
            for _, c in m.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{c['description']}**")
                    st.write(f"Recompensa: **R$ {c['reward']:.2f}**")
                    # Botão para sinalizar conclusão ao admin
                    if st.button("MARCAR COMO FEITO", key=f"c_{c['id']}", use_container_width=True):
                        run_query("UPDATE chores SET status='pending' WHERE id=:id", {'id':c['id']}, commit=True)
                        st.toast("Enviado para aprovação do Comando! 🚀")
                        st.rerun()
        else:
            st.markdown("<div class='liquid-card' style='text-align:center; opacity:0.6;'>Tudo pronto! Você não tem missões pendentes. 🏖️</div>", unsafe_allow_html=True)

    # --- ABA 3: TRANSFERÊNCIA ENTRE USUÁRIOS ---
    with t_transferencia:
        st.markdown(f"##### {t('send_money')}")
        # Busca outros usuários (irmãos/irmãs)
        siblings = run_query("SELECT id, name FROM users WHERE role='user' AND id != :uid", {'uid': uid})
        
        if siblings is not None and not siblings.empty:
            with st.container(border=True):
                with st.form("transfer_form_liquid", clear_on_submit=True):
                    target_name = st.selectbox(t('to_whom'), siblings['name'].tolist())
                    amount = st.number_input(t('how_much'), min_value=1.0, step=1.0)
                    reason = st.text_input(t('reason'), placeholder="Ex: Pagamento de lanche")
                    
                    if st.form_submit_button(t('send_now'), use_container_width=True):
                        if amount > balance:
                            st.error("Saldo insuficiente.")
                        else:
                            target_id = siblings[siblings['name'] == target_name]['id'].values[0]
                            # Registro da transação de saída (Débito)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Transferência Enviada')", 
                                      {'u': uid, 'a': -amount, 'd': f"Para {target_name}: {reason}"}, commit=True)
                            # Registro da transação de entrada (Crédito)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Transferência Recebida')", 
                                      {'u': int(target_id), 'a': amount, 'd': f"De {st.session_state.user_name}: {reason}"}, commit=True)
                            
                            st.success(f"Você enviou R$ {amount:.2f} para {target_name}!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info(t('no_transfer'))

    # --- ABA 4: CÂMBIO (USD E EUR) ---
    with t_cambio:
        st.markdown("##### Conversão de Moedas")
        # Taxas de conversão simuladas
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

    # Rodapé institucional atualizado
    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>BANCO RIPARITECH • v13.7</div>", unsafe_allow_html=True)
