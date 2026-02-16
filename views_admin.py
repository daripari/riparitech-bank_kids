# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time
import time
from database import run_query
from utils import t, get_family_balances

def render_admin_view():
    """
    Interface do Administrador v13.7 - Comando Riparitech.
    Foco: Português do Brasil (PT-BR) e visual limpo.
    """
    
    # --- CABEÇALHO DO PAINEL ---
    st.markdown("<h4 style='letter-spacing:2px; font-weight:300; margin-bottom:20px;'>COMANDO RIPARITECH</h4>", unsafe_allow_html=True)
    
    # --- GRID DE SALDOS DA FAMÍLIA ---
    df_saldos = get_family_balances()
    if df_saldos is not None and not df_saldos.empty:
        cols = st.columns(len(df_saldos))
        for i, row in df_saldos.iterrows():
            with cols[i]:
                st.markdown(f"""
                <div class="liquid-card" style="text-align:center; padding:20px 10px;">
                    <div class="hero-label">{row['name'].upper()}</div>
                    <div style="font-size:1.8rem; font-weight:800; color:#00f2ff; font-family:'JetBrains Mono'; margin:10px 0;">
                        R$ {row['balance']:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (PT-BR) ---
    t_tarefas, t_lancamentos, t_usuarios = st.tabs([
        t('panel'),     # 🔎 Tarefas
        t('cashier'),   # 💸 Lançamentos
        t('mgmt')       # ⚙️ Usuários
    ])
    
    # --- ABA 1: GESTÃO DE TAREFAS (MISSÕES) ---
    with t_tarefas:
        c1, c2 = st.columns([0.6, 0.4])
        
        with c1:
            st.markdown("##### Monitoramento de Missões")
            pending = run_query("""
                SELECT c.id, c.description, c.reward, u.name, u.id as uid 
                FROM chores c JOIN users u ON c.assigned_to = u.id 
                WHERE c.status='pending'
            """)
            
            if pending is not None and not pending.empty:
                st.info(f"Existem {len(pending)} missões aguardando validação.")
                for _, p in pending.iterrows():
                    with st.container(border=True):
                        st.write(f"**{p['name'].title()}** entregou: *{p['description']}*")
                        st.write(f"Recompensa: **R$ {p['reward']:.2f}**")
                        
                        col_ok, col_no = st.columns(2)
                        if col_ok.button(f"✅ Aprovar", key=f"app_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='paid' WHERE id=:id", {'id': p['id']}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Tarefa')", 
                                      {'u': p['uid'], 'a': p['reward'], 'd': f"Missão: {p['description']}"}, commit=True)
                            st.success("Missão Paga!")
                            time.sleep(1); st.rerun()
                            
                        if col_no.button(f"❌ Recusar", key=f"rej_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='open' WHERE id=:id", {'id': p['id']}, commit=True)
                            st.warning("Recusado. A missão voltou para 'Aberta'.")
                            time.sleep(1); st.rerun()
            else:
                st.markdown("<div class='liquid-card' style='text-align:center; opacity:0.5;'>Nenhuma missão pendente para aprovação.</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("##### Nova Missão")
            kids = run_query("SELECT id, name FROM users WHERE role='user'")
            if kids is not None:
                with st.form("new_mission_admin", clear_on_submit=True):
                    desc = st.text_input("O que deve ser feito?")
                    reward = st.number_input("Valor (R$)", min_value=0.5, step=0.5)
                    who = st.selectbox("Para quem?", kids['name'].tolist())
                    
                    if st.form_submit_button("AGENDAR MISSÃO", use_container_width=True):
                        kid_id = kids[kids['name'] == who]['id'].values[0]
                        run_query("INSERT INTO chores (description, reward, assigned_to, created_at) VALUES (:d, :r, :uid, NOW())",
                                  params={'d': desc, 'r': reward, 'uid': int(kid_id)}, commit=True)
                        st.success("Missão agendada!")
                        time.sleep(1); st.rerun()

    # --- ABA 2: LANÇAMENTOS (CASHIER) ---
    with t_lancamentos:
        st.markdown("##### Lançamento Financeiro Direto")
        kids = run_query("SELECT id, name FROM users WHERE role='user'")
        if kids is not None:
            with st.container(border=True):
                with st.form("cashier_admin_form", clear_on_submit=True):
                    target = st.selectbox("Conta da Criança", kids['name'].tolist())
                    val = st.number_input("Valor R$", min_value=0.0, step=1.0)
                    op_type = st.radio("Operação", ["Depósito", "Retirada"], horizontal=True)
                    note = st.text_input("Motivo", placeholder="Ex: Ajuste Riparitech")
                    
                    if st.form_submit_button("EXECUTAR LANÇAMENTO", use_container_width=True):
                        kid_id = kids[kids['name'] == target]['id'].values[0]
                        final_amt = val if op_type == "Depósito" else -val
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, NOW(), :t)",
                                  params={'uid': int(kid_id), 'amt': final_amt, 'desc': note, 't': op_type}, commit=True)
                        st.success("Saldo atualizado!")
                        time.sleep(1); st.rerun()

    # --- ABA 3: GESTÃO DE USUÁRIOS ---
    with t_usuarios:
        col_u1, col_u2 = st.columns([0.6, 0.4])
        
        with col_u1:
            st.markdown("##### Usuários Cadastrados")
            all_users = run_query("SELECT id, name, role FROM users ORDER BY role, name")
            if all_users is not None:
                st.dataframe(all_users, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.markdown("##### Ações de Conta")
            sel_u_name = st.selectbox("Selecionar Usuário", all_users['name'].tolist() if all_users is not None else [])
            
            if sel_u_name:
                u_row = all_users[all_users['name'] == sel_u_name].iloc[0]
                u_id = int(u_row['id'])
                
                c_pw, c_del = st.columns(2)
                with c_pw:
                    with st.popover("Trocar Senha", use_container_width=True):
                        new_p = st.text_input("Nova Senha", type="password")
                        if st.button("Confirmar"):
                            run_query("UPDATE users SET password=:p WHERE id=:id", {'p': new_p, 'id': u_id}, commit=True)
                            st.success("Senha alterada!")
                with c_del:
                    if st.button("EXCLUIR USUÁRIO", key="del_user_btn", use_container_width=True):
                        if u_id != st.session_state.user_id:
                            run_query("DELETE FROM users WHERE id=:id", {'id': u_id}, commit=True)
                            st.rerun()
                        else:
                            st.error("Não pode excluir sua própria conta.")

        with col_u2:
            st.markdown("##### Adicionar Usuário")
            with st.form("new_user_admin"):
                n_name = st.text_input("Nome de Usuário").lower().strip()
                n_pass = st.text_input("Senha")
                n_role = st.selectbox("Perfil", ["user", "admin"])
                if st.form_submit_button("CRIAR CONTA", use_container_width=True):
                    run_query("INSERT INTO users (name, password, role) VALUES (:n, :p, :r)", 
                              {'n': n_name, 'p': n_pass, 'r': n_role}, commit=True)
                    st.success(f"Usuário {n_name} criado!")
                    time.sleep(1); st.rerun()

    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>RIPARITECH COMMAND ENGINE • v13.7</div>", unsafe_allow_html=True)
