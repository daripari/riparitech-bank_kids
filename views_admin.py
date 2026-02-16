# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time, timedelta
import time
from database import run_query
from utils import t, get_family_balances

def cleanup_old_tasks():
    """Protocolo de Limpeza: Apaga registros concluídos ou cancelados há mais de 14 dias"""
    try:
        run_query("""
            DELETE FROM chores 
            WHERE status IN ('paid', 'canceled') 
            AND deadline < (NOW() - INTERVAL '14 days')
        """, commit=True)
    except Exception:
        pass # Ignora falhas silenciosas na limpeza para não travar o app

def render_admin_view():
    """
    Interface do Administrador v13.9 - Comando Riparitech.
    FIX: Tratamento de NaT (Not-a-Time) para evitar erro ValueError no strftime.
    Foco: Monitoramento, Multas, Cancelamento e PT-BR.
    """
    # 1. Executa a limpeza de 14 dias
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
    
    # --- NAVEGAÇÃO POR ABAS (PT-BR) ---
    t_tarefas, t_lancamentos, t_usuarios = st.tabs([
        t('panel'),     # 🔎 Tarefas
        t('cashier'),   # 💸 Lançamentos
        t('mgmt')       # ⚙️ Usuários
    ])
    
    # --- ABA 1: GESTÃO DE TAREFAS (MISSÕES) ---
    with t_tarefas:
        st_pendentes, st_monitor, st_nova = st.tabs(["✅ Aprovações", "📊 Monitoramento Geral", "➕ Nova Missão"])

        with st_pendentes:
            st.markdown("##### Validar Entregas")
            pending = run_query("""
                SELECT c.id, c.description, c.reward, u.name, u.id as uid 
                FROM chores c JOIN users u ON c.assigned_to = u.id 
                WHERE c.status='pending'
            """)
            
            if pending is not None and not pending.empty:
                for _, p in pending.iterrows():
                    with st.container(border=True):
                        st.write(f"**{p['name'].title()}** entregou: *{p['description']}*")
                        st.caption(f"Valor a ser pago: R$ {p['reward']:.2f}")
                        
                        col_ok, col_no = st.columns(2)
                        if col_ok.button(f"Pagar R$ {p['reward']:.2f}", key=f"app_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='paid' WHERE id=:id", {'id': p['id']}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Tarefa')", 
                                      {'u': p['uid'], 'a': p['reward'], 'd': f"Tarefa: {p['description']}"}, commit=True)
                            st.success("Pagamento efetuado!")
                            time.sleep(0.5); st.rerun()
                        
                        if col_no.button(f"Recusar / Reabrir", key=f"rej_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='open' WHERE id=:id", {'id': p['id']}, commit=True)
                            st.warning("Tarefa reaberta.")
                            time.sleep(0.5); st.rerun()
            else:
                st.info("Nenhuma entrega aguardando aprovação.")

        with st_monitor:
            st.markdown("##### Monitoramento de Todas as Tarefas")
            all_chores = run_query("""
                SELECT c.id, c.description, c.reward, c.status, c.deadline, u.name as kid_name, u.id as uid
                FROM chores c
                JOIN users u ON c.assigned_to = u.id
                ORDER BY c.deadline ASC
            """)
            
            if all_chores is not None and not all_chores.empty:
                # Converter para datetime para garantir compatibilidade
                all_chores['deadline'] = pd.to_datetime(all_chores['deadline'])
                
                for _, chore in all_chores.iterrows():
                    with st.container(border=True):
                        c_info, c_actions = st.columns([0.7, 0.3])
                        
                        # --- FIX: TRATAMENTO DE NAT (DESSA MANEIRA NÃO OCORRE O VALUEERROR) ---
                        if pd.isna(chore['deadline']):
                            due_str = "Sem prazo"
                            is_overdue = False
                        else:
                            due_str = chore['deadline'].strftime('%d/%m/%Y %H:%M')
                            is_overdue = chore['deadline'] < datetime.now() and chore['status'] == 'open'

                        with c_info:
                            status_map = {'open': '🟢 Aberta', 'pending': '🟡 Pendente', 'paid': '🔵 Paga', 'canceled': '🔴 Cancelada'}
                            status_label = status_map.get(chore['status'], chore['status'])
                            overdue_warn = " ⚠️ **ATRASADA**" if is_overdue else ""
                            
                            st.markdown(f"**{chore['kid_name'].title()}**: {chore['description']} {overdue_warn}")
                            st.caption(f"Vencimento: {due_str} | Valor: R$ {chore['reward']:.2f} | Status: {status_label}")
                        
                        with c_actions:
                            # Ação de Cancelar (Apenas se não estiver concluída)
                            if chore['status'] in ['open', 'pending']:
                                if st.button("🚫 Cancelar", key=f"can_{chore['id']}", use_container_width=True):
                                    run_query("UPDATE chores SET status='canceled' WHERE id=:id", {'id': chore['id']}, commit=True)
                                    st.rerun()
                            
                            # Ação de Multa (Popover para segurança)
                            with st.popover("💸 Multar", use_container_width=True):
                                multa_val = st.number_input("Valor da Multa (R$)", min_value=0.5, value=1.0, step=0.5, key=f"mv_{chore['id']}")
                                if st.button("Confirmar Multa", key=f"btn_m_{chore['id']}", use_container_width=True):
                                    run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Retirada')", 
                                              {'u': int(chore['uid']), 'a': -multa_val, 'd': f"Multa: {chore['description']}"}, commit=True)
                                    st.toast(f"Multa de R$ {multa_val:.2f} aplicada!")
                                    time.sleep(0.5); st.rerun()
            else:
                st.info("Nenhuma missão registrada.")

        with st_nova:
            st.markdown("##### Lançar Nova Missão")
            kids = run_query("SELECT id, name FROM users WHERE role='user'")
            if kids is not None:
                with st.form("admin_new_mission", clear_on_submit=True):
                    desc = st.text_input("Descrição da tarefa")
                    val = st.number_input("Valor da Recompensa (R$)", min_value=0.5, step=0.5)
                    who = st.selectbox("Quem deve executar?", kids['name'].tolist())
                    d_date = st.date_input("Data de Vencimento")
                    d_time = st.time_input("Hora de Vencimento", value=dt_time(20, 0))
                    
                    if st.form_submit_button("CRIAR MISSÃO", use_container_width=True):
                        target_id = kids[kids['name'] == who]['id'].values[0]
                        deadline = datetime.combine(d_date, d_time)
                        run_query("INSERT INTO chores (description, reward, assigned_to, created_at, deadline) VALUES (:d, :r, :u, NOW(), :dl)",
                                  {'d': desc, 'r': val, 'u': int(target_id), 'dl': deadline}, commit=True)
                        st.success("Missão agendada com sucesso!")
                        time.sleep(0.5); st.rerun()

    # --- ABA 2: LANÇAMENTOS DIRETOS ---
    with t_lancamentos:
        st.markdown("##### Ajuste de Saldo Manual")
        kids = run_query("SELECT id, name FROM users WHERE role='user'")
        if kids is not None:
            with st.container(border=True):
                with st.form("admin_cashier", clear_on_submit=True):
                    target = st.selectbox("Conta da Criança", kids['name'].tolist())
                    val = st.number_input("Valor (R$)", min_value=0.0)
                    op_type = st.radio("Operação", ["Depósito", "Retirada"], horizontal=True)
                    note = st.text_input("Motivo", placeholder="Ex: Presente / Ajuste")
                    
                    if st.form_submit_button("EXECUTAR LANÇAMENTO", use_container_width=True):
                        kid_id = kids[kids['name'] == target]['id'].values[0]
                        amt = val if op_type == "Depósito" else -val
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), :t)",
                                  {'u': int(kid_id), 'a': amt, 'd': note, 't': op_type}, commit=True)
                        st.success("Lançamento concluído!")
                        time.sleep(0.5); st.rerun()

    # --- ABA 3: GESTÃO DE USUÁRIOS ---
    with t_usuarios:
        col_u1, col_u2 = st.columns([0.6, 0.4])
        with col_u1:
            st.markdown("##### Usuários no Sistema")
            all_users = run_query("SELECT id, name, role FROM users ORDER BY role, name")
            st.dataframe(all_users, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            sel_user = st.selectbox("Gerenciar Usuário", all_users['name'].tolist() if all_users is not None else [])
            if sel_user:
                u_id = int(all_users[all_users['name'] == sel_user]['id'].values[0])
                c_pw, c_del = st.columns(2)
                with c_pw:
                    with st.popover("Trocar Senha"):
                        new_p = st.text_input("Nova Senha", type="password")
                        if st.button("Salvar Senha"):
                            run_query("UPDATE users SET password=:p WHERE id=:id", {'p': new_p, 'id': u_id}, commit=True)
                            st.success("Senha alterada!")
                with c_del:
                    if st.button("EXCLUIR CONTA", use_container_width=True):
                        if u_id != st.session_state.user_id:
                            run_query("DELETE FROM users WHERE id=:id", {'id': u_id}, commit=True)
                            st.rerun()
                        else: st.error("Não pode excluir a si mesmo.")

        with col_u2:
            st.markdown("##### Novo Usuário")
            with st.form("admin_new_user"):
                n_name = st.text_input("Nome").lower().strip()
                n_pass = st.text_input("Senha")
                n_role = st.selectbox("Perfil", ["user", "admin"])
                if st.form_submit_button("CRIAR"):
                    run_query("INSERT INTO users (name, password, role) VALUES (:n, :p, :r)", 
                              {'n': n_name, 'p': n_pass, 'r': n_role}, commit=True)
                    st.success("Criado!")
                    time.sleep(0.5); st.rerun()

    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>RIPARITECH COMMAND v13.9</div>", unsafe_allow_html=True)
