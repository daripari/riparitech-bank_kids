# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from database import run_query
from utils import t, get_family_balances

def cleanup_old_tasks():
    """
    Protocolo de Higiene: Apaga tarefas pagas ou canceladas há mais de 14 dias.
    Garante a performance do banco de dados e limpa o histórico antigo.
    """
    try:
        run_query("""
            DELETE FROM chores 
            WHERE status IN ('paid', 'canceled') 
            AND (deadline < NOW() - INTERVAL '14 days' OR completed_at < NOW() - INTERVAL '14 days')
        """, commit=True)
    except Exception:
        # Falha silenciosa para não interromper a experiência do usuário
        pass

def render_admin_view():
    """
    Interface do Administrador v14.0 - Comando Riparitech.
    Foco: Acompanhamento de Prazos, Multas Inteligentes e Gestão PT-BR.
    """
    # Executa a limpeza automática de registros antigos
    cleanup_old_tasks()
    
    st.markdown("<h4 style='letter-spacing:2px; font-weight:300; margin-bottom:20px;'>COMANDO RIPARITECH</h4>", unsafe_allow_html=True)
    
    # --- PAINEL DE SALDOS EM TEMPO REAL ---
    df_saldos = get_family_balances()
    if df_saldos is not None and not df_saldos.empty:
        cols = st.columns(len(df_saldos))
        for i, row in df_saldos.iterrows():
            with cols[i]:
                st.markdown(f"""
                <div class="liquid-card" style="text-align:center;">
                    <div class="hero-label">{row['name'].upper()}</div>
                    <div style="font-size:1.8rem; font-weight:800; color:#00f2ff; font-family:'JetBrains Mono';">
                        R$ {row['balance']:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # --- ABAS DE COMANDO ---
    t_tarefas, t_lancamentos, t_usuarios = st.tabs([t('panel'), t('cashier'), t('mgmt')])
    
    with t_tarefas:
        # Sub-abas: Aprovações, Acompanhar (ex-Monitoramento) e Criação
        st_pendentes, st_acompanhar, st_nova = st.tabs(["✅ Aprovações", "📊 Acompanhar", "➕ Nova Missão"])

        with st_pendentes:
            st.markdown("##### Validar Conclusões")
            pending = run_query("""
                SELECT c.id, c.description, c.reward, u.name, u.id as uid 
                FROM chores c JOIN users u ON c.assigned_to = u.id 
                WHERE c.status='pending'
            """)
            if pending is not None and not pending.empty:
                for _, p in pending.iterrows():
                    with st.container(border=True):
                        st.write(f"**{p['name'].title()}** avisou que terminou: *{p['description']}*")
                        c_ok, c_no = st.columns(2)
                        if c_ok.button(f"Pagar R$ {p['reward']:.2f}", key=f"app_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='paid' WHERE id=:id", {'id': p['id']}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Tarefa')", 
                                      {'u': p['uid'], 'a': p['reward'], 'd': f"Missão: {p['description']}"}, commit=True)
                            st.success("Pagamento realizado!")
                            time.sleep(0.5); st.rerun()
                        if c_no.button("Reabrir Missão", key=f"rej_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='open' WHERE id=:id", {'id': p['id']}, commit=True)
                            st.warning("Tarefa devolvida para o usuário.")
                            time.sleep(0.5); st.rerun()
            else:
                st.info("Nenhuma tarefa aguardando aprovação.")

        with st_acompanhar:
            st.markdown("##### Auditoria de Prazos e Status")
            all_chores = run_query("""
                SELECT c.id, c.description, c.reward, c.status, c.deadline, c.completed_at, u.name as kid_name, u.id as uid 
                FROM chores c JOIN users u ON c.assigned_to = u.id 
                ORDER BY c.deadline ASC
            """)
            
            if all_chores is not None and not all_chores.empty:
                # Garantir que as colunas são tratadas como datetime pelo pandas
                all_chores['deadline'] = pd.to_datetime(all_chores['deadline'])
                all_chores['completed_at'] = pd.to_datetime(all_chores['completed_at'])
                now = datetime.now()

                for _, chore in all_chores.iterrows():
                    deadline = chore['deadline']
                    completed = chore['completed_at']
                    status = chore['status']
                    
                    # --- LÓGICA DE MULTA E CANCELAMENTO v14.0 ---
                    # 1. Está vencida e ainda não foi concluída (Status Aberto)
                    is_overdue_open = (not pd.isna(deadline) and deadline < now and status == 'open')
                    # 2. Foi concluída, mas a data de aviso é posterior ao prazo
                    is_late_delivery = (not pd.isna(deadline) and not pd.isna(completed) and completed > deadline)
                    
                    can_fine = is_overdue_open or is_late_delivery
                    can_cancel = (status == 'open')

                    with st.container(border=True):
                        c_info, c_actions = st.columns([0.65, 0.35])
                        
                        with c_info:
                            st.markdown(f"**{chore['kid_name'].title()}**: {chore['description']}")
                            d_str = deadline.strftime('%d/%m/%Y %H:%M') if not pd.isna(deadline) else "Não definido"
                            r_str = completed.strftime('%d/%m/%Y %H:%M') if not pd.isna(completed) else "Pendente"
                            
                            st.caption(f"📅 Vencimento: {d_str}")
                            st.caption(f"🕒 Realização: {r_str}")
                            st.caption(f"Valor: R$ {chore['reward']:.2f} | Status: {status.upper()}")
                            if is_overdue_open: st.markdown("<span style='color:#ff4b4b; font-size:0.7rem;'>⚠️ ATRASO DETECTADO</span>", unsafe_allow_html=True)
                            if is_late_delivery: st.markdown("<span style='color:#ffa500; font-size:0.7rem;'>⌛ ENTREGUE COM ATRASO</span>", unsafe_allow_html=True)
                        
                        with c_actions:
                            # Cancelar missões que não foram concluídas
                            if can_cancel:
                                if st.button("🚫 Cancelar", key=f"can_{chore['id']}", use_container_width=True):
                                    run_query("UPDATE chores SET status='canceled' WHERE id=:id", {'id': chore['id']}, commit=True)
                                    st.rerun()
                            
                            # Aplicar multa por indisciplina de prazo
                            if can_fine:
                                with st.popover("💸 Aplicar Multa", use_container_width=True):
                                    val_multa = st.number_input("Valor da Multa (R$)", min_value=0.5, value=1.0, step=0.5, key=f"f_{chore['id']}")
                                    if st.button("Confirmar Multa", key=f"fb_{chore['id']}", use_container_width=True):
                                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Retirada')", 
                                                  {'u': int(chore['uid']), 'a': -val_multa, 'd': f"Multa: Atraso na missão {chore['description']}"}, commit=True)
                                        st.toast("Punição financeira aplicada!")
                                        time.sleep(0.5); st.rerun()
                            elif status not in ['paid', 'canceled']:
                                st.success("No prazo ✅")
            else:
                st.info("Nenhum registro de missão para acompanhar.")

        with st_nova:
            st.markdown("##### Agendar Nova Missão")
            kids = run_query("SELECT id, name FROM users WHERE role='user'")
            if kids is not None:
                with st.form("new_mission_form_v14", clear_on_submit=True):
                    desc = st.text_input("O que deve ser feito?")
                    val = st.number_input("Recompensa (R$)", min_value=0.5, step=0.5)
                    who = st.selectbox("Responsável", kids['name'].tolist())
                    d_date = st.date_input("Data de Vencimento")
                    d_time = st.time_input("Hora de Vencimento", value=datetime.now().time())
                    
                    if st.form_submit_button("LANÇAR NO SISTEMA", use_container_width=True):
                        deadline = datetime.combine(d_date, d_time)
                        run_query("INSERT INTO chores (description, reward, assigned_to, created_at, deadline) VALUES (:d, :r, :u, NOW(), :dl)", 
                                  {'d': desc, 'r': val, 'u': int(kids[kids['name']==who]['id'].values[0]), 'dl': deadline}, commit=True)
                        st.success("Missão agendada!")
                        time.sleep(0.5); st.rerun()

    # --- ABA 2: LANÇAMENTOS DIRETOS ---
    with t_lancamentos:
        st.markdown("##### Ajuste de Saldo Manual")
        kids = run_query("SELECT id, name FROM users WHERE role='user'")
        if kids is not None:
            with st.container(border=True):
                with st.form("admin_cashier_direct"):
                    target = st.selectbox("Escolher Conta", kids['name'].tolist())
                    val = st.number_input("Valor (R$)", min_value=0.0)
                    op = st.radio("Tipo de Operação", ["Depósito", "Retirada"], horizontal=True)
                    motivo = st.text_input("Motivo do Lançamento")
                    if st.form_submit_button("EXECUTAR", use_container_width=True):
                        kid_id = kids[kids['name']==target]['id'].values[0]
                        final_amt = val if op == "Depósito" else -val
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), :t)", 
                                  {'u': int(kid_id), 'a': final_amt, 'd': motivo, 't': op}, commit=True)
                        st.success("Operação concluída!")
                        time.sleep(0.5); st.rerun()

    # --- ABA 3: GESTÃO DE USUÁRIOS ---
    with t_usuarios:
        st.markdown("##### Usuários Ativos")
        all_users = run_query("SELECT id, name, role FROM users ORDER BY role, name")
        st.dataframe(all_users, use_container_width=True, hide_index=True)

    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>RIPARITECH COMMAND v14.0</div>", unsafe_allow_html=True)
