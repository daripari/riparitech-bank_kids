# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from database import run_query

# Dicionário de traduções v13.5 - Marca Riparitech e terminologia de Portugal (PT-PT)
TRANSLATIONS = {
    'pt': {
        'bal': 'O Meu Saldo', 
        'family_bal': '💰 Monitorização de Ativos (Saldos)',
        'missions': 'Missões', 
        'tools': 'Câmbio', # Alterado de 'Ferramentas' para 'Câmbio'
        'admin': 'Comando', 
        'logout': 'Sair',
        'refresh': 'Actualizar',
        'notifs': 'Notificações',
        'home': 'Extracto e Histórico', 
        'transfer': 'Transferir', 
        'last_mov': 'Últimas Movimentações',
        'active_missions': 'As Tuas Missões Activas', 
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
        'mgmt': '⚙️ Utilizadores', 
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
        'manual_entry': 'Lançamento Manual (Depósito/Levantamento)', 
        'deposit': 'Depósito', 
        'withdraw': 'Levantamento', 
        'execute': 'EXECUTAR LANÇAMENTO',
        'lang_sel': 'Idioma'
    },
    'en': {
        'bal': 'My Balance', 
        'family_bal': '💰 Asset Monitoring (Balances)',
        'missions': 'Missions', 
        'tools': 'Exchange',
        'admin': 'Command', 
        'logout': 'Logout',
        'refresh': 'Refresh',
        'notifs': 'Notifications',
        'home': 'History', 
        'transfer': 'Transfer', 
        'last_mov': 'Recent Transactions',
        'active_missions': 'Your Active Missions', 
        'send_money': 'Send Money', 
        'to_whom': 'Recipient',
        'how_much': 'Amount ($)', 
        'reason': 'Reason', 
        'send_now': 'SEND NOW 💸', 
        'no_transfer': 'No one available for transfer.',
        'calc': 'Calculator', 
        'fx': 'Exchange', 
        'panel': '🔎 Tasks', 
        'new_task': '➕ New Task', 
        'mgmt': '⚙️ Users', 
        'cashier': '💸 Entries',
        'late_tasks': 'Overdue Tasks', 
        'apply_fine': 'Apply Fine', 
        'approve': 'Approve', 
        'reject': 'Reject',
        'desc': 'What needs to be done?', 
        'value': 'Reward ($)', 
        'date': 'Due Date', 
        'time': 'Due Time', 
        'schedule': 'SCHEDULE MISSION',
        'manual_entry': 'Manual Entry', 
        'deposit': 'Deposit', 
        'withdraw': 'Withdraw', 
        'execute': 'EXECUTE ENTRY',
        'lang_sel': 'Language'
    },
    'es': {
        'bal': 'Mi Saldo', 
        'family_bal': '💰 Monitoreo de Activos (Saldos)',
        'missions': 'Misiones', 
        'tools': 'Cambio',
        'admin': 'Comando', 
        'logout': 'Salir',
        'refresh': 'Actualizar',
        'notifs': 'Notificaciones',
        'home': 'Historial', 
        'transfer': 'Transferir', 
        'last_mov': 'Últimos Movimientos',
        'active_missions': 'Tus Misiones Activas', 
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
        'apply_fine': 'Aplicar Multa', 
        'approve': 'Aprovar', 
        'reject': 'Rechazar',
        'desc': '¿Qué hay que hacer?', 
        'value': 'Recompensa ($)', 
        'date': 'Fecha Límite', 
        'time': 'Hora Límite', 
        'schedule': 'AGENDAR MISIÓN',
        'manual_entry': 'Lanzamiento Manual', 
        'deposit': 'Depósito', 
        'withdraw': 'Retiro', 
        'execute': 'EJECUTAR LANZAMIENTO',
        'lang_sel': 'Idioma'
    }
}

def t(key):
    """Retorna a tradução da chave solicitada com base no idioma da sessão."""
    lang = st.session_state.get('lang', 'pt')
    return TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, key)

@st.cache_data(ttl=600)
def get_balance(uid):
    """Calcula o saldo total de um utilizador específico."""
    res = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': uid})
    val = res.iloc[0]['total'] if res is not None and not res.empty and pd.notnull(res.iloc[0]['total']) else 0.0
    return val

def get_family_balances():
    """Recupera o saldo de todos os utilizadores com o perfil 'user'."""
    query = """
        SELECT u.id, u.name, COALESCE(SUM(t.amount), 0) as balance 
        FROM users u 
        LEFT JOIN transactions t ON u.id = t.user_id 
        WHERE u.role = 'user' 
        GROUP BY u.name, u.id ORDER BY u.name
    """
    return run_query(query)
