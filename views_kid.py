# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from database import run_query
from utils import t, get_balance

def render_kid_view():
    uid = st.session_state.user_id
    user_bal = get_balance(uid)
    
    # Hero Section
    st.markdown(f"""
    <div class="glass-card balance-container">
        <div class="balance-label">{t('bal')}</div>
        <div class="balance-value">R$ {user_bal:,.2f}</div>
        <div style="margin-top:10px; font-size:0.75rem; color:#10B981;">● CONEXÃO SEGURA</div>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs([f"🏠 {t('home')}", f"📝 {t('missions')}", f"💸 {t('transfer')}", f"🧰 {t('tools')}"])
    
    # --- TAB 1: EXTRATO ---
    with tabs[0]:
        st.markdown(f"<h4 style='margin-bottom:15px;'>{t('last_mov')}</h4>", unsafe_allow_html=True)
        hist = run_query("SELECT timestamp, description, amount, type FROM transactions WHERE user_id=:uid ORDER BY id DESC LIMIT 5", params={'uid': uid})
        if hist is not None and not hist.empty:
            for _, h in hist.iterrows():
                color = "#10B981" if h['amount'] >= 0 else "#EF4444"
                icon = "⬇️" if h['amount'] >= 0 else "⬆️"
                st.markdown(f"""
                <div style="background:#111113; border-radius:12px; padding:12px; margin-bottom:8px; border-left: 3px solid {color}; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-weight:600; font-size:0.9rem;">{h['description']}</div>
                        <div style="font-size:0.7rem; color:#6B7280;">{h['timestamp'].strftime('%d/%m %H:%M')}</div>
                    </div>
                    <div style="font-family:'JetBrains Mono'; font-weight:700; color:{color};">{icon} R$ {abs(h['amount']):,.2f}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Nenhuma movimentação encontrada.")

    # --- TAB 2: MISSÕES ---
    with tabs[1]:
        st.markdown(f"<h4 style='margin-bottom:15px;'>{t('active_missions')}</h4>", unsafe_allow_html=True)
        open_chores = run_query("SELECT * FROM chores WHERE status = 'open' AND assigned_to = :uid ORDER BY deadline ASC", params={'uid': uid})
        
        if open_chores is not None and not open_chores.empty:
            for _, chore in open_chores.iterrows():
                is_late = False
                deadline_str = ""
                if pd.notnull(chore['deadline']):
                    dl = pd.to_datetime(chore['deadline'])
                    deadline_str = dl.strftime("%d/%m às %H:%M")
                    if dl < datetime.now(): is_late = True
                
                border = "#EF4444" if is_late else "#00C6FF"
                badge = f"<span class='badge-late'>ATRASADA!</span>" if is_late else f"<span class='badge-pending'>{deadline_str}</span>"
                
                st.markdown(f"""
                <div class="glass-card" style="border-left: 4px solid {border}; padding: 1rem;">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <div style="font-size:1.1rem; font-weight:700;">{chore['description']}</div>
                            <div style="margin-top:5px;">{badge}</div>
                        </div>
                        <div style="font-family:'JetBrains Mono'; font-size:1.2rem; font-weight:800; color:#10B981;">R$ {chore['reward']:,.2f}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                
                if st.button("✅ ENTREGAR TAREFA", key=f"do_{chore['id']}", use_container_width=True):
                    run_query("UPDATE chores SET status='pending' WHERE id=:cid", params={'cid': chore['id']}, commit=True)
                    st.toast("Tarefa enviada para análise!"); time.sleep(1); st.rerun()
        else:
            st.info("Nenhuma missão pendente no momento.")

    # --- TAB 3: TRANSFERIR ---
    with tabs[2]:
        st.markdown(f"<h4 style='margin-bottom:15px;'>{t('send_money')}</h4>", unsafe_allow_html=True)
        siblings = run_query("SELECT id, name FROM users WHERE role='user' AND id != :uid", params={'uid': uid})
        if siblings is not None and not siblings.empty:
            with st.container():
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                target = st.selectbox(t('to_whom'), siblings['name'].tolist())
                amt = st.number_input(t('how_much'), min_value=0.0, step=1.0)
                reason = st.text_input(t('reason'))
                if st.button(t('send_now'), use_container_width=True, type="primary"):
                    if amt > user_bal:
                        st.error("Saldo insuficiente para transferência.")
                    elif amt > 0 and reason:
                        dest_id = siblings[siblings['name'] == target]['id'].values[0]
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, 'Transferência Enviada')", params={'uid': uid, 'amt': -amt, 'desc': f"Para: {target} | {reason}", 'ts': datetime.now()}, commit=True)
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, 'Transferência Recebida')", params={'uid': int(dest_id), 'amt': amt, 'desc': f"De: {st.session_state.user_name} | {reason}", 'ts': datetime.now()}, commit=True)
                        st.success("Dinheiro enviado!"); time.sleep(1); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info(t('no_transfer'))

    # --- TAB 4: FERRAMENTAS ---
    with tabs[3]:
        c_calc, c_fx = st.tabs([f"🧮 {t('calc')}", f"🌍 {t('fx')}"])
        
        with c_calc:
            st.markdown(f"<div class='display-calc'>{st.session_state.calc_expr if st.session_state.calc_expr else '0'}</div>", unsafe_allow_html=True)
            def kp(k): st.session_state.calc_expr += str(k)
            def kc(): st.session_state.calc_expr = ""
            def ks():
                try: st.session_state.calc_expr = str(eval(st.session_state.calc_expr.replace('×', '*').replace('÷', '/')))
                except: st.session_state.calc_expr = "Erro"
            
            c1, c2, c3, c4 = st.columns(4)
            c1.button("7", on_click=kp, args=("7",)); c2.button("8", on_click=kp, args=("8",)); c3.button("9", on_click=kp, args=("9",)); c4.button("÷", on_click=kp, args=("/",))
            c1.button("4", on_click=kp, args=("4",)); c2.button("5", on_click=kp, args=("5",)); c3.button("6", on_click=kp, args=("6",)); c4.button("×", on_click=kp, args=("*",))
            c1.button("1", on_click=kp, args=("1",)); c2.button("2", on_click=kp, args=("2",)); c3.button("3", on_click=kp, args=("3",)); c4.button("-", on_click=kp, args=("-",))
            c1.button("0", on_click=kp, args=("0",)); c2.button(".", on_click=kp, args=(".",)); c3.button("C", on_click=kc); c4.button("=", on_click=ks)
        
        with c_fx:
            usd, eur = 5.05, 5.45
            st.markdown(f"""
            <div class='glass-card'>
                <div style="display:flex; justify-content:space-between;">
                    <span>🇺🇸 Dólar (USD)</span>
                    <span style="color:#00C6FF; font-weight:700;">$ {(user_bal/usd):,.2f}</span>
                </div>
                <hr style="border:0; border-top:1px solid #222; margin: 10px 0;">
                <div style="display:flex; justify-content:space-between;">
                    <span>🇪🇺 Euro (EUR)</span>
                    <span style="color:#00C6FF; font-weight:700;">€ {(user_bal/eur):,.2f}</span>
                </div>
            </div>""", unsafe_allow_html=True)
