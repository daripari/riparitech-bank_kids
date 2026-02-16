# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from database import run_query

# Dicionário de traduções v13.7 - Padrão RIGOROSO PT-BR
# Termos corrigidos: Atualizar, Extrato, Retirada, Usuário, etc.
TRANSLATIONS = {
    'pt': {
        'bal': 'Meu Saldo', 
        'family_bal': '💰 Monitoramento de Ativos',
        'missions': 'Missões', 
        'tools': 'Câmbio', 
        'admin': 'Comando', 
        'logout': 'Sair',
        'refresh': 'Atualizar',
        'home': 'Extrato e Histórico', 
        'transfer': 'Transferir', 
        'last_mov': 'Últimas Movimentações',
        'active_missions': 'Missões Ativas', 
        'send_money': 'Enviar Dinheiro', 
        'to_whom': 'Destinatário',
        'how_much': 'Valor (R$)', 
        'reason': 'Motivo', 
        'send_now': 'ENVIAR AGORA 💸', 
        'no_transfer': 'Ninguém disponível para transferência.',
        'calc': 'Calculadora', 
        'fx': 'Câmbio', 
        'panel': '🔎 Tarefas', 
        'new_task': '➕ Nova Tarefa', 
        'mgmt': '⚙️ Usuários', 
        'cashier': '💸 Lançamentos',
        'late_tasks': 'Tarefas Atrasadas', 
        'approve': 'Aprovar', 
        'reject': 'Recusar',
        'desc': 'Descrição', 
        'value': 'Recompensa (R$)', 
        'date': 'Data Limite', 
        'time': 'Hora Limite', 
        'schedule': 'AGENDAR MISSÃO',
        'manual_entry': 'Lançamento Manual (Depósito/Retirada)', 
        'deposit': 'Depósito', 
        'withdraw': 'Retirada', 
        'execute': 'EXECUTAR LANÇAMENTO',
        'lang_sel': 'Idioma'
    },
    'en': {
        'bal': 'My Balance', 
        'family_bal': '💰 Asset Monitoring',
        'missions': 'Missions', 
        'tools': 'Exchange',
        'admin': 'Command', 
        'logout': 'Logout',
        'refresh': 'Refresh',
        'home': 'History', 
        'transfer': 'Transfer', 
        'last_mov': 'Recent Transactions',
        'active_missions': 'Active Missions', 
        'send_money': 'Send Money', 
        'to_whom': 'Recipient',
        'how_much': 'Amount ($)', 
        'reason': 'Reason', 
        'send_now': 'SEND NOW 💸', 
        'no_transfer': 'No one available.',
        'calc': 'Calculator', 
        'fx': 'Exchange', 
        'panel': '🔎 Tasks', 
        'new_task': '➕ New Task', 
        'mgmt': '⚙️ Users', 
        'cashier': '💸 Entries',
        'late_tasks': 'Overdue Tasks', 
        'approve': 'Approve', 
        'reject': 'Reject',
        'desc': 'Description', 
        'value': 'Reward', 
        'date': 'Due Date', 
        'time': 'Due Time', 
        'schedule': 'SCHEDULE',
        'manual_entry': 'Manual Entry', 
        'deposit': 'Deposit', 
        'withdraw': 'Withdraw', 
        'execute': 'EXECUTE',
        'lang_sel': 'Language'
    },
    'es': {
        'bal': 'Mi Saldo', 
        'family_bal': '💰 Monitoreo de Activos',
        'missions': 'Misiones', 
        'tools': 'Cambio',
        'admin': 'Comando', 
        'logout': 'Salir',
        'refresh': 'Actualizar',
        'home': 'Historial', 
        'transfer': 'Transferir', 
        'last_mov': 'Últimos Movimientos',
        'active_missions': 'Misiones Activas', 
        'send_money': 'Enviar Dinero', 
        'to_whom': 'Destinatario',
        'how_much': 'Monto ($)', 
        'reason': 'Motivo', 
        'send_now': 'ENVIAR AHORA 💸', 
        'no_transfer': 'Nadie disponible.',
        'calc': 'Calculadora', 
        'fx': 'Cambio', 
        'panel': '🔎 Tareas', 
        'new_task': '➕ Nueva Tarea', 
        'mgmt': '⚙️ Usuarios', 
        'cashier': '💸 Lanzamientos',
        'late_tasks': 'Tareas Atrasadas', 
        'approve': 'Aprovar', 
        'reject': 'Rechazar',
        'desc': 'Descripción', 
        'value': 'Recompensa', 
        'date': 'Fecha', 
        'time': 'Hora', 
        'schedule': 'AGENDAR',
        'manual_entry': 'Lanzamiento Manual', 
        'deposit': 'Depósito', 
        'withdraw': 'Retiro', 
        'execute': 'EJECUTAR',
        'lang_sel': 'Idioma'
    }
}

def t(key):
    """Retorna a tradução da chave solicitada com base no idioma da sessão (Padrão PT-BR)."""
    lang = st.session_state.get('lang', 'pt')
    return TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, key)

@st.cache_data(ttl=600)
def get_balance(uid):
    """Calcula o saldo de um usuário somando todas as suas transações."""
    res = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': uid})
    val = res.iloc[0]['total'] if res is not None and not res.empty and pd.notnull(res.iloc[0]['total']) else 0.0
    return val

def get_family_balances():
    """Retorna o saldo consolidado de todos os usuários com papel 'user'."""
    query = """
        SELECT u.id, u.name, COALESCE(SUM(t.amount), 0) as balance 
        FROM users u 
        LEFT JOIN transactions t ON u.id = t.user_id 
        WHERE u.role = 'user' 
        GROUP BY u.name, u.id ORDER BY u.name
    """
    return run_query(query)
