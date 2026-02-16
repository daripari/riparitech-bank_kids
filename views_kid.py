# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from database import run_query
from utils import t, get_balance

def render_kid_view():
    """
    Renderiza a interface da criança com o design Obsidian Liquid UI v13.0.
    Focado em cartões de vidro, tipografia premium e responsividade.
    """
    uid = st.session_state.user_id
    balance = get_balance(uid)
    
    # --- SEÇÃO HERO: SALDO CENTRAL ---
    # Utiliza as classes hero-balance, hero-label e hero-value do styles.py
    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">{t('bal')}</div>
        <div class="hero-value">R$ {balance:,.2f}</div>
        <div style="font-size: 0.7rem; opacity: 0.5; letter-spacing: 2px; margin-top: -10px;">
            ATUALIZADO AGORA
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (TABS DISRUPTIVAS) ---
    # As tabs foram estilizadas no styles.py para parecerem botões flutuantes
    t_hist, t_miss, t_transf, t_tools = st.tabs([
        f"📊 {t('home')}", 
        f"🎯 {t('missions')}", 
        f"💸 {t('transfer')}", 
        f"🧰 {t('tools')}"
    ])
    
    # --- ABA 1: EXTRATO E HISTÓRICO ---
    with t_hist:
        st.markdown("<div class='liquid-card'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:600; margin-bottom:15px; letter-spacing:1px;'>{t('last_mov')}</div>", unsafe_allow_html=True)
        
        hist = run_query("""
            SELECT timestamp, description, amount, type 
            FROM transactions 
            WHERE user_id=:uid 
            ORDER BY id DESC LIMIT 8
        """, {'uid': uid})
        
        if hist is not None and not hist.empty:
            for _, r in hist.iterrows():
                is_positive = r['amount'] >= 0
                color = "#00f2ff" if is_positive else "#ff4b4b"
                icon = "↓" if is_positive else "↑"
                
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                    <div>
                        <div style="font-size:0.9rem; font-weight:600;">{r['description']}</div>
                        <div style="font-size:0.7rem; color:#888;">{r['timestamp'].strftime('%d %b, %H:%M')}</div>
                    </div>
                    <div style="color:{color}; font-weight:700; font-family:'JetBrains Mono';">
                        {icon} R$ {abs(r['amount']):,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Nenhuma movimentação encontrada.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- ABA 2: MISSÕES (TAREFAS) ---
    with t_miss:
        st.markdown(f"<div style='font-weight:600; margin-bottom:15px; letter-spacing:1px;'>{t('active_missions')}</div>", unsafe_allow_html=True)
        
        chores = run_query("""
            SELECT * FROM chores 
            WHERE assigned_to=:uid AND status='open' 
            ORDER BY deadline ASC
        """, {'uid': uid})
        
        if chores is not None and not chores.empty:
            for _, c in chores.iterrows():
                deadline_dt = pd.to_datetime(c['deadline'])
                is_late = deadline_dt < datetime.now()
                
                with st.container():
                    st.markdown(f"<div class='liquid-card' style='border-left: 4px solid {'#ff4b4b' if is_late else '#7000ff'};'>", unsafe_allow_html=True)
                    c1, c2 = st.columns([0.7, 0.3])
                    with c1:
                        st.markdown(f"<b>{c['description']}</b>", unsafe_allow_html=True)
                        st.markdown(f"<small style='color:{'#ff4b4b' if is_late else '#888'};'>Prazo: {deadline_dt.strftime('%d/%m %H:%M')}</small>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<div style='text-align:right; color:#10B981; font-weight:800;'>R$ {c['reward']:.2f}</div>", unsafe_allow_html=True)
                    
                    if st.button(f"ENTREGAR MISSÃO", key=f"chore_{c['id']}", use_container_width=True):
                        run_query("UPDATE chores SET status='pending' WHERE id=:id", {'id': c['id']}, commit=True)
                        st.toast("Missão enviada para aprovação! 🚀")
                        time.sleep(1)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='liquid-card' style='text-align:center; opacity:0.6;'>Nenhuma missão pendente. Aproveite o descanso! 🏖️</div>", unsafe_allow_html=True)

    # --- ABA 3: TRANSFERÊNCIA ---
    with t_transf:
        st.markdown("<div class='liquid-card'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-weight:600; margin-bottom:15px; letter-spacing:1px;'>{t('send_money')}</div>", unsafe_allow_html=True)
        
        siblings = run_query("SELECT id, name FROM users WHERE role='user' AND id != :uid", {'uid': uid})
        if siblings is not None and not siblings.empty:
            with st.form("transfer_liquid_form", clear_on_submit=True):
                target_name = st.selectbox(t('to_whom'), siblings['name'].tolist())
                amount = st.number_input(t('how_much'), min_value=0.0, step=1.0)
                reason = st.text_input(t('reason'), placeholder="Ex: Pagamento de lanche")
                
                if st.form_submit_button(t('send_now'), use_container_width=True):
                    if amount > balance:
                        st.error("Saldo insuficiente.")
                    elif amount <= 0:
                        st.warning("Insira um valor válido.")
                    else:
                        target_id = siblings[siblings['name'] == target_name]['id'].values[0]
                        # Retira do remetente
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Envio')", 
                                  {'u': uid, 'a': -amount, 'd': f"Para {target_name}: {reason}"}, commit=True)
                        # Adiciona ao destinatário
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Recebimento')", 
                                  {'u': int(target_id), 'a': amount, 'd': f"De {st.session_state.user_name}: {reason}"}, commit=True)
                        st.success("Transferência realizada com sucesso!")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info(t('no_transfer'))
        st.markdown("</div>", unsafe_allow_html=True)

    # --- ABA 4: FERRAMENTAS (CÂMBIO) ---
    with t_tools:
        st.markdown("<div style='font-weight:600; margin-bottom:15px; letter-spacing:1px;'>INVESTIMENTOS E CÂMBIO</div>", unsafe_allow_html=True)
        
        c_usd, c_eur = st.columns(2)
        usd_rate = 5.05
        eur_rate = 5.45
        
        with c_usd:
            st.markdown(f"""
            <div class="liquid-card" style="text-align:center;">
                <div class="hero-label">DÓLAR (USD)</div>
                <div style="font-size:1.8rem; font-weight:800; color:#00f2ff; font-family:'JetBrains Mono'; margin:10px 0;">$ {balance/usd_rate:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_eur:
            st.markdown(f"""
            <div class="liquid-card" style="text-align:center;">
                <div class="hero-label">EURO (EUR)</div>
                <div style="font-size:1.8rem; font-weight:800; color:#7000ff; font-family:'JetBrains Mono'; margin:10px 0;">€ {balance/eur_rate:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

    # Rodapé de Versão
    st.markdown("<div style='text-align:center; opacity:0.2; font-size:0.6rem; margin-top:40px;'>OBSIDIAN LIQUID UI ENGINE v13.0</div>", unsafe_allow_html=True)
