# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from database import run_query

# Dicionário de traduções simplificado conforme solicitado (PT-BR)
TRANSLATIONS = {
    'pt': {
        'bal': 'Meu Saldo', 
        'family_bal': '💰 Monitoramento de Ativos (Saldos)',
        'missions': 'Missões', 
        'tools': 'Ferramentas', 
        'admin': 'Comando', 
        'logout': 'Sair',
        'home': 'Extrato e Histórico', 
        'transfer': 'Transferir', 
        'last_mov': 'Últimas Movimentações',
        'active_missions': 'Suas Missões Ativas', 
        'send_money': 'Enviar Dinheiro', 
        'to_whom': 'Destinatário',
        'how_much': 'Valor (R$)', 
        'reason': 'Motivo', 
        'send_now': 'ENVIAR AGORA 💸', 
        'no_transfer': 'Ninguém disponível para transferência.',
        'calc': 'Calculadora', 
        'fx': 'Câmbio', 
        'panel': '🔎 Monitor de Tarefas', 
        'new_task': '➕ Nova Tarefa', 
        'mgmt': '⚙️ Usuários', 
        'cashier': '💸 Lançamentos',
        'late_tasks': 'Tarefas Atrasadas', 
        'apply_fine': 'Aplicar Multa', 
        'approve': 'Aprovar', 
        'reject': 'Recusar',
        'desc': 'O que deve ser feito?', 
        'value': 'Recompensa (R$)', 
        'date': 'Data Limite', 
        'time': 'Hora Limite', 
        'schedule': 'AGENDAR MISSÃO',
        'manual_entry': 'Lançamento Manual (Depósito/Retirada)', 
        'deposit': 'Depósito', 
        'withdraw': 'Retirada', 
        'execute': 'EXECUTAR LANÇAMENTO'
    }
}

def t(key):
    """Função de tradução baseada no estado da sessão (PT-BR)"""
    lang = st.session_state.get('lang', 'pt')
    return TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, key)

@st.cache_data(ttl=600)
def get_balance(uid):
    """Calcula o saldo individual de um usuário"""
    res = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': uid})
    val = res.iloc[0]['total'] if res is not None and not res.empty and pd.notnull(res.iloc[0]['total']) else 0.0
    return val

def get_family_balances():
    """Obtém o saldo de todos os usuários com perfil 'user' para o Admin"""
    query = """
        SELECT u.id, u.name, COALESCE(SUM(t.amount), 0) as balance 
        FROM users u 
        LEFT JOIN transactions t ON u.id = t.user_id 
        WHERE u.role = 'user' 
        GROUP BY u.name, u.id ORDER BY u.name
    """
    return run_query(query)
