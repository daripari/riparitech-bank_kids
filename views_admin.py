# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time
from database import run_query
from utils import t

def render_admin_view():
    tabs = st.tabs([f"🔎 {t('panel')}", f"➕ {t('new_task')}", f"⚙️ {t('mgmt')}", f"💸 {t('cashier')}"])
    
    # --- TAB 1: PAINEL ---
    with tabs[0]:
        st.markdown("#### Painel de Controle")
        # Punição
        overdue = run_query("SELECT c.id, c.description, c.reward, u.name FROM chores c JOIN users u ON c.assigned_to = u.id WHERE c.status='open' AND c.deadline < NOW()")
        if overdue is not None and not overdue.empty:
            st.error(f"🚨 {len(overdue)} {t('late_tasks')}")
            for _, o in overdue.iterrows():
                with st.expander(f"🔴 {o['name']} - {o['description']}", expanded=True):
                    val_multa = st.number_input(f"{t('apply_fine')} R$", value=float(o['reward']), key=f"m_{o['id']}")
                    if st.button("Aplicar", key=f"bm_{o['id']}"):
                         run_query("UPDATE chores SET status='failed' WHERE id=:id", params={'id': o['id']}, commit=True)
                         run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, 'Multa')", 
                                   params={'uid': run_query(f"SELECT id FROM users WHERE name='{o['name']}'").iloc[0]['id'], 'amt': -val_multa, 'desc': f"Multa: {o['description']}", 'ts': datetime.now()}, commit=True)
                         st.rerun()

        # Aprovação
        pending = run_query("SELECT c.id, c.description, c.reward, u.name, u.id as uid FROM chores c JOIN users u ON c.assigned_to = u.id WHERE c.status='pending'")
        if pending is not None and not pending.empty:
            st.info(f"⏳ {len(pending)} Pendentes")
            for _, p in pending.iterrows():
                c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
                c1.write(f"**{p['name']}**: {p['description']} (R$ {p['reward']})")
                if c2.button("✅", key=f"ok_{p['id']}"):
                    run_query("UPDATE chores SET status='paid' WHERE id=:id", params={'id': p['id']}, commit=True)
                    run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, 'Pagamento')", 
                              params={'uid': int(p['uid']), 'amt': p['reward'], 'desc': f"Tarefa: {p['description']}", 'ts': datetime.now()}, commit=True)
                    st.rerun()
                if c3.button("❌", key=f"no_{p['id']}"):
                    run_query("UPDATE chores SET status='open' WHERE id=:id", params={'id': p['id']}, commit=True); st.rerun()

        st.markdown("---")
        df_all = run_query("SELECT u.name, c.description, c.reward, c.status, c.deadline FROM chores c JOIN users u ON c.assigned_to = u.id ORDER BY c.deadline DESC")
        if df_all is not None: st.dataframe(df_all, use_container_width=True, hide_index=True)
        
        if st.button("Limpar Histórico (>14 dias)"):
            run_query("DELETE FROM chores WHERE status IN ('paid', 'failed') AND deadline < NOW() - INTERVAL '14 days'", commit=True)
            st.success("Limpo.")

    # --- TAB 2: NOVA TAREFA ---
    with tabs[1]:
        kids = run_query("SELECT name FROM users WHERE role='user'")
        if kids is not None:
            with st.container():
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                desc = st.text_input(t('desc'))
                rew = st.number_input(f"{t('value')} R$", min_value=0.5, step=0.5)
                who = st.selectbox(t('to_whom'), kids['name'].tolist())
                d_date = st.date_input(t('date'))
                d_time = st.time_input(t('time'), value=dt_time(23, 59))
                
                if st.button(t('schedule'), use_container_width=True, type="primary"):
                    kid_id = run_query(f"SELECT id FROM users WHERE name='{who}'").iloc[0]['id']
                    dl = datetime.combine(d_date, d_time)
                    run_query("INSERT INTO chores (description, reward, status, assigned_to, created_at, deadline) VALUES (:d, :r, 'open', :uid, :ts, :dl)",
                              params={'d': desc, 'r': rew, 'uid': int(kid_id), 'ts': datetime.now(), 'dl': dl}, commit=True)
                    st.success("Criada!")
                st.markdown("</div>", unsafe_allow_html=True)

    # --- TAB 3: GESTÃO ---
    with tabs[2]:
        all_users = run_query("SELECT id, name, role FROM users")
        st.dataframe(all_users, use_container_width=True)

    # --- TAB 4: CAIXA ---
    with tabs[3]:
        st.write(t('manual_entry'))
        kids = run_query("SELECT name FROM users WHERE role='user'")
        if kids is not None:
            k_sel = st.selectbox("User", kids['name'].tolist())
            val = st.number_input("R$", 0.0)
            op = st.radio("Op", [t('deposit'), t('withdraw')], horizontal=True)
            motivo = st.text_input(t('reason'))
            if st.button(t('execute')):
                kid_id = run_query(f"SELECT id FROM users WHERE name='{k_sel}'").iloc[0]['id']
                amt = val if op == t('deposit') else -val
                run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, :t)",
                          params={'uid': int(kid_id), 'amt': amt, 'desc': motivo, 'ts': datetime.now(), 't': op}, commit=True)
                st.success("OK")
