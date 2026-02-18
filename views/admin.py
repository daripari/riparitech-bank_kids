# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import time
# Importando módulos do core
from core.database import run_query
from core.themes import THEMES
from core.utils import t, get_family_balances

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
    Interface do Administrador v14.1 - Comando Riparitech.
    Foco: Acompanhamento de Prazos, Multas Inteligentes e Suporte Multi-idioma.
    """
    # Executa a limpeza automática de registros antigos
    cleanup_old_tasks()
    
    st.markdown(f"<h4 style='letter-spacing:2px; font-weight:300; margin-bottom:20px;'>{t('cmd_header')}</h4>", unsafe_allow_html=True)
    
    # --- PAINEL DE SALDOS EM TEMPO REAL ---
    df_saldos = get_family_balances()
    if df_saldos is not None and not df_saldos.empty:
        cols = st.columns(len(df_saldos))
        for i, row in df_saldos.iterrows():
            with cols[i]:
                st.markdown(f"""
                <div class="liquid-card" style="text-align:center;">
                    <div class="hero-label">{row['name'].upper()}</div>
                    <div style="font-size:1.8rem; font-weight:800; color: 
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # --- ABAS DE COMANDO (MULTI-IDIOMA) ---
    t_tarefas, t_lancamentos, t_mesada, t_usuarios = st.tabs([t('panel'), t('cashier'), t('allowance_tab'), t('mgmt')])
    
    with t_tarefas:
        # Sub-abas: Aprovações, Acompanhar e Criação
        st_pendentes, st_acompanhar, st_nova = st.tabs([f"✅ {t('tab_approvals')}", f"📊 {t('missions')}", f"➕ {t('tab_new_mission')}"])

        with st_pendentes:
            st.markdown(f"##### {t('validate_delivery')}")
            pending = run_query("""
                SELECT c.id, c.description, c.reward, u.name, u.id as uid 
                FROM chores c JOIN users u ON c.assigned_to = u.id 
                WHERE c.status='pending'
            """)
            if pending is not None and not pending.empty:
                for _, p in pending.iterrows():
                    with st.container(border=True):
                        st.write(f"**{p['name'].title()}**: *{p['description']}*")
                        c_ok, c_no = st.columns(2)
                        if c_ok.button(f"{t('pay_btn')} R$ {p['reward']:.2f}", key=f"app_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='paid' WHERE id=:id", {'id': p['id']}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Tarefa')", 
                                      {'u': p['uid'], 'a': p['reward'], 'd': f"{t('missions')}: {p['description']}"}, commit=True)
                            st.success(t('fine_applied_toast') if 'fine' in p['description'] else t('confirm'))
                            time.sleep(0.5); st.rerun()
                        if c_no.button(t('reopen_btn'), key=f"rej_{p['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='open' WHERE id=:id", {'id': p['id']}, commit=True)
                            st.rerun()
            else:
                st.info(t('no_pending'))

        with st_acompanhar:
            st.markdown(f"##### {t('audit_title')}")
            all_chores = run_query("""
                SELECT c.id, c.description, c.reward, c.status, c.deadline, c.completed_at, u.name as kid_name, u.id as uid 
                FROM chores c JOIN users u ON c.assigned_to = u.id
                ORDER BY c.deadline ASC
            """)
            
            if all_chores is not None and not all_chores.empty:
                all_chores['deadline'] = pd.to_datetime(all_chores['deadline'])
                all_chores['completed_at'] = pd.to_datetime(all_chores['completed_at'])
                now = datetime.now()

                # Cabeçalho da Tabela
                c1, c2, c3, c4, c5, c6 = st.columns([1.5, 2.5, 1.2, 1.2, 1, 1])
                c1.markdown(f"**{t('col_responsible')}**")
                c2.markdown(f"**{t('col_task')}**")
                c3.markdown(f"**{t('deadline')}**")
                c4.markdown(f"**{t('col_completion')}**")
                c5.markdown(f"**{t('status')}**")
                c6.markdown(f"**{t('col_actions')}**")
                st.divider()

                for _, chore in all_chores.iterrows():
                    deadline = chore['deadline']
                    completed = chore['completed_at']
                    status = chore['status']
                    
                    is_overdue_open = (not pd.isna(deadline) and deadline < now and status == 'open')
                    is_late_delivery = (not pd.isna(deadline) and not pd.isna(completed) and completed > deadline)
                    
                    can_fine = is_overdue_open or is_late_delivery
                    can_cancel = (status == 'open')

                    r1, r2, r3, r4, r5, r6 = st.columns([1.5, 2.5, 1.2, 1.2, 1, 1])
                    
                    with r1: st.write(chore['kid_name'].split()[0])
                    with r2: st.write(f"{chore['description']} (R$ {chore['reward']:.2f})")
                    
                    with r3:
                        d_str = deadline.strftime('%d/%m %H:%M') if not pd.isna(deadline) else "-"
                        if is_overdue_open: st.markdown(f"<span style='color:#ff4b4b'>{d_str}</span>", unsafe_allow_html=True)
                        else: st.write(d_str)
                    
                    with r4:
                        r_str = completed.strftime('%d/%m %H:%M') if not pd.isna(completed) else "-"
                        if is_late_delivery: st.markdown(f"<span style='color:#ffa500'>{r_str}</span>", unsafe_allow_html=True)
                        else: st.write(r_str)
                    
                    with r5:
                        # Cores para facilitar a identificação visual dos status
                        s_colors = {'open': 'var(--accent-color-1)', 'pending': 
                        st.markdown(f"<span style='color:{color}; font-weight:bold;'>{t(f'status_{status}')}</span>", unsafe_allow_html=True)
                    
                    with r6:
                        if can_cancel:
                            if st.button(t('cancel_btn'), key=f"can_{chore['id']}", use_container_width=True):
                                run_query("UPDATE chores SET status='canceled' WHERE id=:id", {'id': chore['id']}, commit=True)
                                st.rerun()
                        if can_fine:
                            with st.popover(t('btn_fine'), use_container_width=True):
                                val_multa = st.number_input("R$", min_value=0.5, value=1.0, step=0.5, key=f"f_{chore['id']}")
                                if st.button("✅ OK", key=f"fb_{chore['id']}"):
                                    run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Retirada')", 
                                              {'u': int(chore['uid']), 'a': -val_multa, 'd': f"Multa: {chore['description']}"}, commit=True)
                                    st.toast(t('fine_applied_toast'))
                                    time.sleep(0.5); st.rerun()
                    
                    st.markdown("<hr style='margin:0.2rem 0; opacity:0.1;'>", unsafe_allow_html=True)
            else:
                st.info(t('no_pending'))

        with st_nova:
            st.markdown(f"##### {t('tab_new_mission')}")
            kids = run_query("SELECT id, name FROM users WHERE role='user'")
            if kids is not None:
                with st.form("new_mission_v14_1", clear_on_submit=True):
                    desc = st.text_input(t('desc'))
                    val = st.number_input(t('value'), min_value=0.5, step=0.5)
                    who = st.selectbox(t('mgmt'), kids['name'].tolist())
                    d_date = st.date_input(t('date'))
                    d_time = st.time_input(t('time'), value=datetime.now().time())
                    
                    if st.form_submit_button(t('execute'), use_container_width=True):
                        deadline = datetime.combine(d_date, d_time)
                        run_query("INSERT INTO chores (description, reward, assigned_to, created_at, deadline) VALUES (:d, :r, :u, NOW(), :dl)", 
                                  {'d': desc, 'r': val, 'u': int(kids[kids['name']==who]['id'].values[0]), 'dl': deadline}, commit=True)
                        st.success(t('confirm'))
                        time.sleep(0.5); st.rerun()

    # --- ABA 2: LANÇAMENTOS DIRETOS ---
    with t_lancamentos:
        st.markdown(f"##### {t('manual_adjust')}")
        kids = run_query("SELECT id, name FROM users WHERE role='user'")
        if kids is not None:
            with st.container(border=True):
                with st.form("admin_cashier_direct"):
                    target = st.selectbox(t('target_acc'), kids['name'].tolist())
                    val = st.number_input(t('value'), min_value=0.0)
                    op = st.radio(t('op_type'), [t('deposit'), t('withdraw')], horizontal=True)
                    motivo = st.text_input(t('reason'))
                    if st.form_submit_button(t('execute'), use_container_width=True):
                        kid_id = kids[kids['name']==target]['id'].values[0]
                        final_amt = val if op == t('deposit') else -val
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), :t)", 
                                  {'u': int(kid_id), 'a': final_amt, 'd': motivo, 't': op}, commit=True)
                        st.success(t('confirm'))
                        time.sleep(0.5); st.rerun()

    # --- ABA 3: MESADA AUTOMÁTICA ---
    with t_mesada:
        st.markdown(f"##### {t('allowance_title')}")
        kids = run_query("SELECT id, name FROM users WHERE role='user'")
        
        # Interface Reativa (Sem st.form para permitir atualização dinâmica dos campos)
        c_k, c_f, c_d, c_v, c_b = st.columns([2, 1.5, 1.5, 1, 1])
        
        with c_k: 
            target = st.selectbox(t('target_acc'), kids['name'].tolist() if kids is not None else [], key="al_target")
        
        with c_f: 
            # Mapeamento de labels para valores internos
            freq_map = {t('freq_monthly'): 'monthly', t('freq_weekly'): 'weekly', t('freq_daily'): 'daily'}
            freq_label = st.selectbox(t('frequency'), list(freq_map.keys()), key="al_freq")
            freq_val = freq_map[freq_label]
        
        with c_d:
            # Lógica condicional para o campo de data baseada na frequência selecionada
            day = 0
            if freq_val == 'monthly':
                day = st.number_input(t('day_of_month'), min_value=1, max_value=28, value=1, key="al_day_m")
            elif freq_val == 'weekly':
                day_label = st.selectbox(t('day_of_week'), t('weekdays'), key="al_day_w")
                day = t('weekdays').index(day_label)
            else: # daily
                st.text_input(t('day_of_month'), value="-", disabled=True, key="al_day_d")
        
        with c_v: 
            val = st.number_input(t('value'), min_value=1.0, step=5.0, key="al_val")
            
        with c_b:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True) # Spacer para alinhar com inputs
            if st.button(t('execute'), use_container_width=True, key="al_btn"):
                kid_id = kids[kids['name']==target]['id'].values[0]
                # Remove anterior se existir para evitar duplicidade
                run_query("DELETE FROM allowances WHERE user_id=:u", {'u': int(kid_id)}, commit=True)
                run_query("INSERT INTO allowances (user_id, amount, day_of_month, frequency) VALUES (:u, :a, :d, :f)", 
                          {'u': int(kid_id), 'a': val, 'd': day, 'f': freq_val}, commit=True)
                st.success(t('confirm'))
                time.sleep(0.5); st.rerun()
        
        st.divider()
        
        # Listagem de Mesadas Ativas
        active_allowances = run_query("""
            SELECT a.id, u.name, a.amount, a.day_of_month, a.last_paid, a.frequency 
            FROM allowances a JOIN users u ON a.user_id = u.id
        """)
        if active_allowances is not None and not active_allowances.empty:
            for _, row in active_allowances.iterrows():
                c1, c2, c3 = st.columns([3, 2, 1])
                
                # Lógica de exibição na lista
                freq_map_inv = {'monthly': t('freq_monthly'), 'weekly': t('freq_weekly'), 'daily': t('freq_daily')}
                freq_display = freq_map_inv.get(row['frequency'], row['frequency'])
                
                if row['frequency'] == 'daily':
                    day_display = "-"
                elif row['frequency'] == 'monthly':
                    day_display = f"Dia {row['day_of_month']}"
                else:
                    day_display = t('weekdays')[int(row['day_of_month'])]
                
                c1.write(f"**{row['name']}**: R$ {row['amount']:.2f}")
                c1.caption(f"{freq_display} - {day_display}")
                c2.caption(f"Último pgto: {row['last_paid'] if row['last_paid'] else '-'}")
                if c3.button("🗑️", key=f"del_al_{row['id']}"):
                    run_query("DELETE FROM allowances WHERE id=:id", {'id': row['id']}, commit=True)
                    st.rerun()

    # --- ABA 3: GESTÃO DE USUÁRIOS ---
    with t_usuarios:
        st.markdown(f"##### {t('active_users')}")
        all_users = run_query("SELECT id, name, role FROM users ORDER BY role, name")
        if all_users is not None:
            st.dataframe(all_users, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            sel_user = st.selectbox(t('mgmt'), all_users['name'].tolist())
            if sel_user:
                u_id = int(all_users[all_users['name'] == sel_user]['id'].values[0])
                
                # Busca o tema atual do usuário selecionadoECT theme FROM users WHERE id=:id", params={'id': u_id})
                current_theme_key = 'default'
                if user_data is not None and not user_data.empty:
                    current_theme_key = user_data.iloc[0].get('theme', 'default') or 'default'

                c_pw, c_theme, c_del = st.columns([1.5, 2, 1.5])
                with c_pw:
                    with st.popover(t('change_pass')): # Usando chave específica
                        new_p = st.text_input(t('new_pass'), type="password") # Usando chave genérica
                        if st.button(f"💾 {t('confirm')}"):
                            hashed_pw = hashlib.sha256(new_p.encode()).hexdigest()
                            run_query("UPDATE users SET password=:p WHERE id=:id", {'p': hashed_pw, 'id': u_id}, commit=True)
                            st.success(t('pass_changed'))
                
                with c_theme:
                    theme_names = {k: v['name'] for k, v in THEMES.items()}
                    current_theme_index = list(theme_names.keys()).index(current_theme_key)
                    
                    selected_theme_name = st.selectbox(
                        label=t('theme_select'), 
                        options=list(theme_names.values()), 
                        index=current_theme_index,
                        key=f"theme_sel_{u_id}"
                    )
                    selected_theme_key = [k for k, v in theme_names.items() if v == selected_theme_name][0]

                    if selected_theme_key != current_theme_key:
                        run_query("UPDATE users SET theme=:theme WHERE id=:id", {'theme': selected_theme_key, 'id': u_id}, commit=True)
                        st.toast(t('theme_changed'))
                        if u_id == st.session_state.user_id:
                            st.session_state.user_theme = selected_theme_key
                        time.sleep(0.5); st.rerun()

                with c_del:
                    if st.button(t('delete_acc'), use_container_width=True):
                        if u_id != st.session_state.user_id:
                            run_query("DELETE FROM users WHERE id=:id", {'id': u_id}, commit=True)
                            st.rerun()
                        else: st.error(t('cancel'))

    st.markdown(f"<div style='text-align:center; color:#e0e0e0; opacity:0.5; font-size:0.6rem; margin-top:50px;'>RIPARITECH COMMAND v14.1</div>", unsafe_allow_html=True)
