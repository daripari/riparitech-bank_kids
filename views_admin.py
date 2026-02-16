# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time
import time
from database import run_query
from utils import t, get_family_balances

def render_admin_view():
    """
    Interface do Administrador v13.1 - FIX: Remoção de componentes vazios e ícones duplicados.
    """
    st.markdown("<h4 style='letter-spacing:2px; font-weight:300; margin-bottom:20px;'>PAINEL DE COMANDO</h4>", unsafe_allow_html=True)
    
    # --- GRID DE SALDOS DA FAMÍLIA ---
    df_saldos = get_family_balances()
    if df_saldos is not None and not df_saldos.empty:
        cols = st.columns(len(df_saldos))
        for i, row in df_saldos.iterrows():
            with cols[i]:
                # Cartões de métricas sem divs vazias
                st.markdown(f"""
                <div class="liquid-card" style="text-align:center; padding:20px 10px;">
                    <div class="hero-label">{row['name'].upper()}</div>
                    <div style="font-size:1.8rem; font-weight:800; color:#00f2ff; font-family:'JetBrains Mono'; margin:10px 0;">
                        R$ {row['balance']:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (FIX: Sem ícones manuais para evitar duplicidade) ---
    t_tarefas, t_lancamentos, t_usuarios = st.tabs([
        t('panel'),     # Puxa direto '🔎 Tarefas' do utils
        t('cashier'),   # Puxa direto '💸 Lançamentos' do utils
        t('mgmt')       # Puxa direto '⚙️ Usuários' do utils
    ])
    
    with t_tarefas:
        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            st.markdown("##### Monitoramento de Missões")
            pending = run_query("SELECT c.id, c.description, c.reward, u.name, u.id as uid FROM chores c JOIN users u ON c.assigned_to = u.id WHERE c.status='pending'")
            
            if pending is not None and not pending.empty:
                for _, p in pending.iterrows():
                    # Usando container para evitar a barra vazia da div liquid-card
                    with st.container(border=True):
                        st.write(f"**{p['name'].title()}** entregou: *{p['description']}*")
                        st.write(f"Recompensa: **R$ {p['reward']:.2f}**")
                        col_ok, col_no = st.columns(2)
                        if col_ok.button(f"✅ Aprovar", key=f"app_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='paid' WHERE id=:id", {'id': p['id']}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Tarefa')", {'u': p['uid'], 'a': p['reward'], 'd': f"Missão: {p['description']}"}, commit=True)
                            st.rerun()
                        if col_no.button(f"❌ Recusar", key=f"rej_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='open' WHERE id=:id", {'id': p['id']}, commit=True)
                            st.rerun()
            else:
                st.markdown("<div class='liquid-card' style='text-align:center; opacity:0.5;'>Nenhuma missão pendente.</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("##### Nova Missão")
            kids = run_query("SELECT id, name FROM users WHERE role='user'")
            if kids is not None:
                with st.form("new_mission_liquid", clear_on_submit=True):
                    desc = st.text_input("O que deve ser feito?")
                    reward = st.number_input("Recompensa (R$)", min_value=0.5, step=0.5)
                    who = st.selectbox("Para quem?", kids['name'].tolist())
                    d_date = st.date_input("Data Limite")
                    d_time = st.time_input("Hora", value=dt_time(23, 59))
                    if st.form_submit_button("AGENDAR", use_container_width=True):
                        kid_id = kids[kids['name'] == who]['id'].values[0]
                        run_query("INSERT INTO chores (description, reward, assigned_to, created_at, deadline) VALUES (:d, :r, :uid, NOW(), :dl)",
                                  params={'d': desc, 'r': reward, 'uid': int(kid_id), 'dl': datetime.combine(d_date, d_time)}, commit=True)
                        st.rerun()

    with t_lancamentos:
        # Removida a div liquid-card que causava o componente vazio
        st.markdown("##### Lançamento Financeiro Direto")
        kids = run_query("SELECT id, name FROM users WHERE role='user'")
        if kids is not None:
            with st.container(border=True):
                with st.form("cashier_liquid_form", clear_on_submit=True):
                    target = st.selectbox("Conta", kids['name'].tolist())
                    val = st.number_input("Valor R$", min_value=0.0)
                    op_type = st.radio("Tipo", ["Depósito", "Retirada"], horizontal=True)
                    note = st.text_input("Motivo")
                    if st.form_submit_button("EXECUTAR", use_container_width=True):
                        kid_id = kids[kids['name'] == target]['id'].values[0]
                        final_amt = val if op_type == "Depósito" else -val
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, NOW(), :t)",
                                  params={'uid': int(kid_id), 'amt': final_amt, 'desc': note, 't': op_type}, commit=True)
                        st.rerun()

    with t_usuarios:
        st.markdown("##### Usuários Cadastrados")
        all_users = run_query("SELECT id, name, role FROM users ORDER BY role, name")
        st.dataframe(all_users, use_container_width=True, hide_index=True)
        # ... resto do código de gestão permanece igual ...

    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>PAINEL DE COMANDO v13.1</div>", unsafe_allow_html=True)
