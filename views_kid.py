# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import time
from datetime import datetime
from database import run_query
from utils import t, get_balance

def render_kid_view():
    """
    Interface do Usuário (Kids) v14.0 - Banco Riparitech.
    Foco: Português do Brasil (PT-BR) e Monitoramento de Prazos.
    Funcionalidades: Saldo Hero, Extrato, Missões, Transferências e Câmbio.
    """
    uid = st.session_state.user_id
    balance = get_balance(uid)
    
    # --- SEÇÃO HERO: EXIBIÇÃO DO SALDO CENTRAL ---
    # Design premium com foco no patrimônio acumulado
    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">{t('bal')}</div>
        <div class="hero-value">R$ {balance:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (PADRÃO PT-BR) ---
    t_extrato, t_missoes, t_transferencia, t_cambio = st.tabs([
        t('home'),      # Extrato e Histórico
        t('missions'),  # Missões
        t('transfer'),  # Transferir
        t('tools')      # Câmbio
    ])
    
    # --- ABA 1: EXTRATO (HISTÓRICO FINANCEIRO) ---
    with t_extrato:
        st.markdown("##### Últimas Movimentações")
        hist = run_query("""
            SELECT description, amount, timestamp 
            FROM transactions 
            WHERE user_id=:u 
            ORDER BY id DESC LIMIT 5
        """, {'u': uid})
        
        if hist is not None and not hist.empty:
            with st.container(border=True):
                for _, r in hist.iterrows():
                    cor = "#00f2ff" if r['amount'] >= 0 else "#ff4b4b"
                    # Exibição limpa de cada transação
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <div style="font-size:0.9rem; opacity:0.8;">{r['description']}</div>
                        <div style="color:{cor}; font-weight:700; font-family:'JetBrains Mono';">R$ {r['amount']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Nenhum registro de movimentação encontrado.")

    # --- ABA 2: MISSÕES (TAREFAS DISPONÍVEIS) ---
    with t_missoes:
        st.markdown(f"##### {t('active_missions')}")
        m = run_query("""
            SELECT * FROM chores 
            WHERE assigned_to=:u AND status='open' 
            ORDER BY deadline ASC
        """, {'u': uid})
        
        if m is not None and not m.empty:
            for _, c in m.iterrows():
                with st.container(border=True):
                    # Tratamento de datas para evitar erros visuais
                    deadline_val = pd.to_datetime(c['deadline'])
                    due_str = deadline_val.strftime('%d/%m/%Y %H:%M') if not pd.isna(deadline_val) else "Sem prazo definido"
                    
                    st.markdown(f"**{c['description']}**")
                    st.caption(f"Prazo final: {due_str} | Recompensa: **R$ {c['reward']:.2f}**")
                    
                    if st.button("MARCAR COMO CONCLUÍDO", key=f"c_{c['id']}", use_container_width=True):
                        # v14.0: Agora salva NOW() no completed_at para auditoria do admin
                        run_query("""
                            UPDATE chores 
                            SET status='pending', completed_at=NOW() 
                            WHERE id=:id
                        """, {'id': c['id']}, commit=True)
                        st.toast("Sucesso! O Comando foi avisado da sua conclusão. 🚀")
                        time.sleep(0.5)
                        st.rerun()
        else:
            st.markdown("<div class='liquid-card' style='text-align:center; opacity:0.6;'>Parabéns! Você não tem missões pendentes no momento. 🏖️</div>", unsafe_allow_html=True)

    # --- ABA 3: TRANSFERIR (P2P FAMILY) ---
    with t_transferencia:
        st.markdown(f"##### {t('send_money')}")
        # Localiza outros usuários para transferência interna
        siblings = run_query("SELECT id, name FROM users WHERE role='user' AND id != :uid", {'uid': uid})
        
        if siblings is not None and not siblings.empty:
            with st.container(border=True):
                with st.form("transfer_form_liquid", clear_on_submit=True):
                    target_name = st.selectbox(t('to_whom'), siblings['name'].tolist())
                    amount = st.number_input(t('how_much'), min_value=1.0, step=1.0)
                    reason = st.text_input(t('reason'), placeholder="Ex: Pagamento de lanche ou dívida")
                    
                    if st.form_submit_button(t('send_now'), use_container_width=True):
                        if amount > balance:
                            st.error("Saldo insuficiente para realizar esta transferência.")
                        else:
                            target_id = siblings[siblings['name'] == target_name]['id'].values[0]
                            # Execução do fluxo financeiro: Saída da conta atual e entrada na conta destino
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Transferência Enviada')", 
                                      {'u': uid, 'a': -amount, 'd': f"Para {target_name}: {reason}"}, commit=True)
                            
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Transferência Recebida')", 
                                      {'u': int(target_id), 'a': amount, 'd': f"De {st.session_state.user_name}: {reason}"}, commit=True)
                            
                            st.success(f"Transferência de R$ {amount:.2f} enviada para {target_name}!")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("Não existem outros usuários cadastrados para transferência.")

    # --- ABA 4: CÂMBIO (PLANEJAMENTO FINANCEIRO) ---
    with t_cambio:
        st.markdown("##### Conversão de Patrimônio")
        # Taxas de referência simuladas
        usd_rate, eur_rate = 5.05, 5.45
        
        c_usd, c_eur = st.columns(2)
        with c_usd:
            st.markdown(f"""
            <div class='liquid-card' style='text-align:center;'>
                <div class='hero-label'>DÓLAR (USD)</div>
                <div style='font-size:1.8rem; font-weight:800; color:#00f2ff; font-family:JetBrains Mono; margin-top:10px;'>
                    US$ {balance/usd_rate:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_eur:
            st.markdown(f"""
            <div class='liquid-card' style='text-align:center;'>
                <div class='hero-label'>EURO (EUR)</div>
                <div style='font-size:1.8rem; font-weight:800; color:#7000ff; font-family:JetBrains Mono; margin-top:10px;'>
                    € {balance/eur_rate:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Rodapé Institucional
    st.markdown("<div style='text-align:center; opacity:0.1; font-size:0.6rem; margin-top:50px;'>BANCO RIPARITECH • v14.0 PREMIUM</div>", unsafe_allow_html=True)
