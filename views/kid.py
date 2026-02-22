# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import time
# Importando módulos do core
from core.database import run_query
from core.themes import THEMES
from core.utils import t, get_balance

def render_kid_view():
    """
    Interface do Usuário (Kids) v14.1 - Banco Riparitech.
    Foco: Suporte multi-idioma e integração com o Comando Admin.
    """
    uid = st.session_state.user_id
    balance = get_balance(uid)
    
    # Verifica se tem mesada configurada
    allowance = run_query("SELECT amount, day_of_month FROM allowances WHERE user_id=:uid", {'uid': uid})
    allowance_info = ""
    if allowance is not None and not allowance.empty:
        day = allowance.iloc[0]['day_of_month']
        amt = allowance.iloc[0]['amount']
        allowance_info = f"<div style='font-size:0.8rem; color:var(--accent-color-1); margin-top:-10px; opacity:0.8;'>📅 {t('next_allowance')}: Dia {day} (R$ {amt:.0f})</div>"

    # --- SEÇÃO HERO: SALDO CENTRAL ---
    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">{t('bal')}</div>
        <div class="hero-value">R$ {balance:,.2f}</div>
        {allowance_info}
    </div>
    """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (TABS) ---
    t_ext, t_mis, t_tra, t_cam, t_prof = st.tabs([f"📜 {t('home')}", f"🎯 {t('missions')}", f"💸 {t('transfer')}", f"💱 {t('tools')}", f"👤 {t('profile_tab')}"])
    
    # --- ABA 1: EXTRATO ---
    with t_ext:
        st.markdown(f"##### {t('last_mov')}")
        hist = run_query("""
            SELECT description, amount, timestamp 
            FROM transactions 
            WHERE user_id=:u 
            ORDER BY id DESC LIMIT 5
        """, {'u': uid})
        
        if hist is not None and not hist.empty:
            with st.container(border=True):
                for _, r in hist.iterrows():
                    cor = "var(--accent-color-1)" if r['amount'] >= 0 else "#ff4b4b"
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <div style="font-size:0.9rem; color:#e0e0e0;">{r['description']}</div>
                        <div style="color:{cor}; font-weight:700;">R$ {r['amount']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(t('history_empty'))

    # --- ABA 2: MISSÕES ---
    with t_mis:
        st.markdown(f"##### {t('active_missions')}")
        m = run_query("""
            SELECT * FROM chores 
            WHERE assigned_to=:u AND status='open' 
            ORDER BY deadline ASC
        """, {'u': uid})
        
        if m is not None and not m.empty:
            for _, c in m.iterrows():
                with st.container(border=True):
                    dl = pd.to_datetime(c['deadline'])
                    st.markdown(f"**{c['description']}**")
                    st.caption(f"{t('deadline')}: {dl.strftime('%d/%m/%Y %H:%M') if not pd.isna(dl) else t('no_deadline')} | {t('value')}: **R$ {c['reward']:.2f}**")
                    
                    if st.button(t('mark_done'), key=f"c_{c['id']}", use_container_width=True):
                        # v14.1: Registra completed_at para auditoria de atraso no Admin
                        run_query("UPDATE chores SET status='pending', completed_at=NOW() WHERE id=:id", {'id': c['id']}, commit=True)
                        st.toast(t('sent_approval'))
                        time.sleep(0.5)
                        st.rerun()
        else:
            st.markdown(f"<div class='liquid-card' style='text-align:center; opacity:0.6;'>{t('no_active_miss')}</div>", unsafe_allow_html=True)

    # --- ABA 3: TRANSFERIR ---
    with t_tra:
        st.markdown(f"##### {t('send_money')}")
        siblings = run_query("SELECT id, name FROM users WHERE role='user' AND id != :uid", {'uid': uid})
        
        if siblings is not None and not siblings.empty:
            with st.container(border=True):
                with st.form("transfer_v14_1", clear_on_submit=True):
                    target = st.selectbox(t('to_whom'), siblings['name'].tolist())
                    amt = st.number_input(t('how_much'), min_value=1.0)
                    reason = st.text_input(t('reason'), placeholder="...")
                    
                    if st.form_submit_button(t('send_now'), use_container_width=True):
                        if amt > balance:
                            st.error(t('insufficient'))
                        else:
                            tid = siblings[siblings['name'] == target]['id'].values[0]
                            # Fluxo P2P: Débito e Crédito
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Envio')", 
                                      {'u': uid, 'a': -amt, 'd': f"{t('transfer')}: {target} - {reason}"}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Recebimento')", 
                                      {'u': int(tid), 'a': amt, 'd': f"{t('transfer')}: {st.session_state.user_name} - {reason}"}, commit=True)
                            st.success(t('transfer_done'))
                            time.sleep(1)
                            st.rerun()
        else:
            st.info(t('no_transfer'))

    # --- ABA 4: CÂMBIO ---
    with t_cam:
        st.markdown(f"##### {t('fx')}")
        usd, eur = 5.05, 5.45
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='liquid-card' style='text-align:center;'><div class='hero-label'>DÓLAR (USD)</div><div style='font-size:1.8rem; font-weight:800; color:var(--accent-color-1);'>US$ {balance/usd:,.2f}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='liquid-card' style='text-align:center;'><div class='hero-label'>EURO (EUR)</div><div style='font-size:1.8rem; font-weight:800; color:var(--accent-color-2);'>€ {balance/eur:,.2f}</div></div>", unsafe_allow_html=True)

    # --- ABA 5: PERFIL ---
    with t_prof:
        st.markdown(f"##### {t('theme_select')}")
        
        theme_names = {k: v['name'] for k, v in THEMES.items()}
        current_theme_key = st.session_state.get('user_theme', 'default')
        
        # Fallback de segurança: se o tema salvo não existir, usa default
        if current_theme_key not in theme_names:
            current_theme_key = 'default'
        
        # Encontra o índice do tema atual para pré-selecionar no selectbox
        current_theme_index = list(theme_names.keys()).index(current_theme_key)
        
        selected_theme_name = st.selectbox(
            label=t('theme_select'), 
            options=list(theme_names.values()), 
            index=current_theme_index,
            label_visibility="collapsed",
            key="kid_theme_selector"
        )
        
        # Encontra a chave interna do tema a partir do nome selecionado
        selected_theme_key = [k for k, v in theme_names.items() if v == selected_theme_name][0]

        if selected_theme_key != current_theme_key:
            st.session_state.user_theme = selected_theme_key
            run_query("UPDATE users SET theme=:theme WHERE id=:id", 
                      {'theme': selected_theme_key, 'id': st.session_state.user_id}, commit=True)
            st.toast(t('theme_changed'))
            time.sleep(0.5)
            st.rerun()

    # Rodapé Institucional
    st.markdown(f"<div style='text-align:center; color:#e0e0e0; opacity:0.5; font-size:0.6rem; margin-top:50px;'>BANCO RIPARITECH • v14.1 PREMIUM</div>", unsafe_allow_html=True)
