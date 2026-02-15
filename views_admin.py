# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time
import time
from database import run_query
from utils import t, get_family_balances

def render_admin_view():
    # 1. Visualização de Saldos das Crianças (O Cockpit)
    st.markdown(f"### {t('family_bal')}")
    df_saldos = get_family_balances()
    if df_saldos is not None and not df_saldos.empty:
        st.markdown("<div class='glass-card' style='padding: 10px 1.5rem;'>", unsafe_allow_html=True)
        for _, row in df_saldos.iterrows():
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #1A1A1E;">
                <span style="font-weight:600;">{row['name'].title()}</span>
                <span style="color:#00C6FF; font-family:'JetBrains Mono'; font-weight:700;">R$ {row['balance']:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. Navegação por Tabs com Nomes Intuitivos
    tabs = st.tabs([t('panel'), t('new_task'), t('mgmt'), t('cashier')])
    
    # --- TAB 1: MONITOR DE TAREFAS ---
    with tabs[0]:
        st.markdown("#### Monitorização de Estado")
        
        # Secção de Punição por Atraso (Lógica de Multas)
        overdue = run_query("""
            SELECT c.id, c.description, c.reward, u.name, u.id as uid 
            FROM chores c JOIN users u ON c.assigned_to = u.id 
            WHERE c.status='open' AND c.deadline < NOW()
        """)
        if overdue is not None and not overdue.empty:
            st.error(f"🚨 Tarefas em Atraso Identificadas")
            for _, o in overdue.iterrows():
                with st.expander(f"🔴 Punir {o['name'].title()} - {o['description']}"):
                    val_multa = st.number_input(f"Valor da Multa", value=float(o['reward']), key=f"m_{o['id']}")
                    if st.button(t('apply_fine'), key=f"bm_{o['id']}"):
                         run_query("UPDATE chores SET status='failed' WHERE id=:id", params={'id': o['id']}, commit=True)
                         run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, NOW(), 'Multa')", 
                                   params={'uid': int(o['uid']), 'amt': -val_multa, 'desc': f"Multa: {o['description']}"}, commit=True)
                         st.rerun()

        # Aprovação de Tarefas Concluídas
        pending = run_query("""
            SELECT c.id, c.description, c.reward, u.name, u.id as uid 
            FROM chores c JOIN users u ON c.assigned_to = u.id 
            WHERE c.status='pending'
        """)
        if pending is not None and not pending.empty:
            st.info(f"⏳ {len(pending)} Tarefas para Validar")
            for _, p in pending.iterrows():
                c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
                c1.write(f"**{p['name']}**: {p['description']}")
                if c2.button("✅", key=f"ok_{p['id']}"):
                    run_query("UPDATE chores SET status='paid' WHERE id=:id", params={'id': p['id']}, commit=True)
                    run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, NOW(), 'Tarefa')", 
                              params={'uid': int(p['uid']), 'amt': p['reward'], 'desc': f"Conclusão: {p['description']}"}, commit=True)
                    st.rerun()
                if c3.button("❌", key=f"no_{p['id']}"):
                    run_query("UPDATE chores SET status='open' WHERE id=:id", params={'id': p['id']}, commit=True)
                    st.rerun()

        st.markdown("---")
        st.caption("LISTA COMPLETA DE MISSÕES")
        df_all = run_query("SELECT u.name as Criança, c.description as Tarefa, c.reward as Valor, c.status as Status, c.deadline as Prazo FROM chores c JOIN users u ON c.assigned_to = u.id ORDER BY c.deadline DESC")
        st.dataframe(df_all, use_container_width=True, hide_index=True)

    # --- TAB 2: NOVA TAREFA ---
    with tabs[1]:
        kids = run_query("SELECT id, name FROM users WHERE role='user'")
        if kids is not None:
            with st.form("new_task_f"):
                desc = st.text_input(t('desc'))
                rew = st.number_input(t('value'), min_value=0.5, step=0.5)
                who = st.selectbox(t('to_whom'), kids['name'].tolist())
                d_date = st.date_input(t('date'))
                d_time = st.time_input(t('time'), value=dt_time(23, 59))
                if st.form_submit_button(t('schedule'), use_container_width=True):
                    kid_id = kids[kids['name'] == who]['id'].values[0]
                    dl = datetime.combine(d_date, d_time)
                    run_query("INSERT INTO chores (description, reward, assigned_to, created_at, deadline) VALUES (:d, :r, :uid, NOW(), :dl)",
                              params={'d': desc, 'r': rew, 'uid': int(kid_id), 'dl': dl}, commit=True)
                    st.success("Missão Agendada!")

    # --- TAB 3: GESTÃO DE UTILIZADORES (FUNCIONALIDADE COMPLETA) ---
    with tabs[2]:
        st.markdown("#### Gestão de Acessos")
        sub_list, sub_add = st.tabs(["Lista e Ações", "Novo Registo"])
        
        with sub_list:
            all_u = run_query("SELECT id, name, role FROM users ORDER BY name")
            st.dataframe(all_u, use_container_width=True, hide_index=True)
            
            sel_user = st.selectbox("Escolher Utilizador", all_u['name'].tolist())
            u_data = all_u[all_u['name'] == sel_user].iloc[0]
            
            c_pw, c_del = st.columns(2)
            with c_pw:
                with st.popover("Alterar Senha"):
                    n_pw = st.text_input("Nova Senha", type="password")
                    if st.button("Guardar Senha"):
                        run_query("UPDATE users SET password=:p WHERE id=:id", params={'p': n_pw, 'id': int(u_data['id'])}, commit=True)
                        st.success("Senha alterada!")
            with c_del:
                if st.button("APAGAR UTILIZADOR", key="del_u"):
                    if int(u_data['id']) != st.session_state.user_id:
                        run_query("DELETE FROM users WHERE id=:id", params={'id': int(u_data['id'])}, commit=True)
                        st.rerun()
                    else: st.error("Não podes apagar a tua própria conta.")

        with sub_add:
            with st.form("add_u"):
                n_name = st.text_input("Nome de Utilizador").lower().strip()
                n_pass = st.text_input("Senha Inicial")
                n_role = st.selectbox("Perfil", ["user", "admin"])
                if st.form_submit_button("REGISTAR UTILIZADOR"):
                    run_query("INSERT INTO users (name, password, role) VALUES (:n, :p, :r)", params={'n': n_name, 'p': n_pass, 'r': n_role}, commit=True)
                    st.success("Conta criada!")

    # --- TAB 4: LANÇAMENTOS FINANCEIROS ---
    with tabs[3]:
        st.markdown(f"#### {t('manual_entry')}")
        kids = run_query("SELECT id, name FROM users WHERE role='user'")
        if kids is not None:
            with st.form("cashier_f"):
                k_target = st.selectbox("Utilizador Alvo", kids['name'].tolist())
                val = st.number_input("Valor R$", min_value=0.0)
                op_type = st.radio("Tipo de Movimento", [t('deposit'), t('withdraw')], horizontal=True)
                note = st.text_input(t('reason'))
                if st.form_submit_button(t('execute'), use_container_width=True):
                    kid_id = kids[kids['name'] == k_target]['id'].values[0]
                    final_amt = val if op_type == t('deposit') else -val
                    run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, NOW(), :t)",
                              params={'uid': int(kid_id), 'amt': final_amt, 'desc': note, 't': op_type}, commit=True)
                    st.success("Lançamento efetuado com sucesso!")
