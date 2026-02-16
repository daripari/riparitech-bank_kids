# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time, timedelta
import time
from database import run_query
from utils import t, get_family_balances

def cleanup_old_tasks():
    """Apaga registros concluídos ou cancelados há mais de 14 dias"""
    run_query("""
        DELETE FROM chores 
        WHERE status IN ('paid', 'canceled') 
        AND deadline < NOW() - INTERVAL '14 days'
    """, commit=True)

def render_admin_view():
    """
    Interface do Administrador v13.8 - Comando Riparitech.
    Foco: Gestão completa de tarefas, Multas e Limpeza Automática.
    """
    # Executa a limpeza automática ao carregar a página
    cleanup_old_tasks()
    
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
    
    # --- NAVEGAÇÃO POR ABAS ---
    t_tarefas, t_lancamentos, t_usuarios = st.tabs([
        t('panel'),     # 🔎 Tarefas
        t('cashier'),   # 💸 Lançamentos
        t('mgmt')       # ⚙️ Usuários
    ])
    
    # --- ABA 1: GESTÃO DE TAREFAS (MISSÕES) ---
    with t_tarefas:
        # Sub-abas para organizar a gestão
        st_pendentes, st_lista, st_nova = st.tabs(["Aprovação", "Monitoramento Geral", "Nova Missão"])

        with st_pendentes:
            st.markdown("##### Missões Aguardando Validação")
            pending = run_query("""
                SELECT c.id, c.description, c.reward, u.name, u.id as uid 
                FROM chores c JOIN users u ON c.assigned_to = u.id 
                WHERE c.status='pending'
            """)
            
            if pending is not None and not pending.empty:
                for _, p in pending.iterrows():
                    with st.container(border=True):
                        st.write(f"**{p['name'].title()}** entregou: *{p['description']}*")
                        st.write(f"Recompensa: **R$ {p['reward']:.2f}**")
                        
                        col_ok, col_no = st.columns(2)
                        if col_ok.button(f"✅ Aprovar Pagamento", key=f"app_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='paid' WHERE id=:id", {'id': p['id']}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Tarefa')", 
                                      {'u': p['uid'], 'a': p['reward'], 'd': f"Missão: {p['description']}"}, commit=True)
                            st.success("Pagamento Efetuado!")
                            time.sleep(0.5); st.rerun()
                            
                        if col_no.button(f"❌ Recusar e Abrir", key=f"rej_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='open' WHERE id=:id", {'id': p['id']}, commit=True)
                            st.warning("Recusado. Missão reaberta para correção.")
                            time.sleep(0.5); st.rerun()
            else:
                st.info("Nenhuma missão pendente de aprovação.")

        with st_lista:
            st.markdown("##### Status de Todas as Missões")
            all_chores = run_query("""
                SELECT c.id, c.description, c.reward, c.status, c.deadline, u.name as kid_name, u.id as uid
                FROM chores c 
                JOIN users u ON c.assigned_to = u.id
                ORDER BY c.deadline DESC
            """)
            
            if all_chores is not None and not all_chores.empty:
                for _, chore in all_chores.iterrows():
                    deadline_dt = chore['deadline']
                    is_overdue = deadline_dt < datetime.now() and chore['status'] == 'open'
                    
                    with st.container(border=True):
                        c_info, c_actions = st.columns([0.7, 0.3])
                        
                        with c_info:
                            status_map = {'open': '🟢 Aberta', 'pending': '🟡 Pendente', 'paid': '🔵 Paga', 'canceled': '🔴 Cancelada'}
                            status_label = status_map.get(chore['status'], chore['status'])
                            overdue_warn = " ⚠️ **ATRASADA**" if is_overdue else ""
                            
                            st.markdown(f"**{chore['kid_name'].title()}**: {chore['description']} {overdue_warn}")
                            st.caption(f"Vencimento: {deadline_dt.strftime('%d/%m/%Y %H:%M')} | Valor: R$ {chore['reward']:.2f} | Status: {status_label}")
                        
                        with c_actions:
                            # Ação 1: Cancelar (Só se não estiver paga)
                            if chore['status'] not in ['paid', 'canceled']:
                                if st.button("Cancelar", key=f"can_{chore['id']}", use_container_width=True):
                                    run_query("UPDATE chores SET status='canceled' WHERE id=:id", {'id': chore['id']}, commit=True)
                                    st.rerun()
                            
                            # Ação 2: Aplicar Multa (Livre ou se estiver atrasada)
                            with st.popover("Aplicar Multa", use_container_width=True):
                                multa_val = st.number_input("Valor da Multa (R$)", min_value=0.5, value=1.0, key=f"mv_{chore['id']}")
                                if st.button("Confirmar Multa", key=f"btn_m_{chore['id']}", use_container_width=True):
                                    run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Multa')", 
                                              {'u': chore['uid'], 'a': -multa_val, 'd': f"Multa: {chore['description']} (Atraso/Indisciplina)"}, commit=True)
                                    st.toast(f"Multa de R$ {multa_val:.2f} aplicada a {chore['kid_name']}!")
                                    time.sleep(0.5); st.rerun()
            else:
                st.write("Sem missões registradas no momento.")

        with st_nova:
            st.markdown("##### Agendar Nova Missão")
            kids = run_query("SELECT id, name FROM users WHERE role='user'")
            if kids is not None:
                with st.form("new_mission_form", clear_on_submit=True):
                    desc = st.text_input("O que deve ser feito?")
                    reward = st.number_input("Valor da Recompensa (R$)", min_value=0.5, step=0.5)
                    who = st.selectbox("Para quem?", kids['name'].tolist())
                    d_date = st.date_input("Data Limite")
                    d_time = st.time_input("Hora Limite", value=dt_time(23, 59))
                    
                    if st.form_submit_button("LANÇAR MISSÃO NO SISTEMA", use_container_width=True):
                        kid_id = kids[kids['name'] == who]['id'].values[0]
                        deadline = datetime.combine(d_date, d_time)
                        run_query("INSERT INTO chores (description, reward, assigned_to, created_at, deadline) VALUES (:d, :r, :uid, NOW(), :dl)",
                                  params={'d': desc, 'r': reward, 'uid': int(kid_id), 'dl': deadline}, commit=True)
                        st.success("Missão agendada!")
                        time.sleep(0.5); st.rerun()

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
                        time.sleep(0.5); st.rerun()

    # --- ABA 3: GESTÃO DE USUÁRIOS ---
    with t_usuarios:
        col_u1, col_u2 = st.columns([0.6, 0.4])
        with col_u1:
            st.markdown("##### Usuários Cadastrados")
            all_users = run_query("SELECT id, name, role FROM users ORDER BY role, name")
            if all_users is not None:
                st.dataframe(all_users, use_container_width=True, hide_index=True)
            
            st.markdown("---")
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
                        else: st.error("Impossível excluir própria conta.")

        with col_u2:
            st.markdown("##### Adicionar Usuário")
            with st.form("new_user_admin"):
                n_name = st.text_input("Login").lower().strip()
                n_pass = st.text_input("Senha")
                n_role = st.selectbox("Perfil", ["user", "admin"])
                if st.form_submit_button("CRIAR CONTA", use_container_width=True):
                    run_query("INSERT INTO users (name, password, role) VALUES (:n, :p, :r)", 
                              {'n': n_name, 'p': n_pass, 'r': n_role}, commit=True)
                    st.success(f"Usuário {n_name} criado!")
                    time.sleep(0.5); st.rerun()

    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>RIPARITECH COMMAND ENGINE • v13.8</div>", unsafe_allow_html=True)
