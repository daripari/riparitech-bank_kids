# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from database import run_query

TRANSLATIONS = {
    'pt': {
        'bal': 'Saldo Atual', 'missions': 'Missões', 'tools': 'Ferramentas', 'admin': 'Comando', 'logout': 'Sair',
        'home': 'Início', 'transfer': 'Transferir', 'last_mov': 'Últimas Movimentações',
        'active_missions': 'Suas Missões Ativas', 'send_money': 'Enviar Dinheiro', 'to_whom': 'Para quem?',
        'how_much': 'Quanto?', 'reason': 'Motivo', 'send_now': 'ENVIAR AGORA 💸', 'no_transfer': 'Ninguém para transferir.',
        'calc': 'Calculadora', 'fx': 'Câmbio', 'panel': 'Painel', 'new_task': 'Nova Tarefa', 'mgmt': 'Gestão', 'cashier': 'Caixa',
        'late_tasks': 'Tarefas Atrasadas', 'apply_fine': 'Aplicar Multa', 'approve': 'Aprovar', 'reject': 'Recusar',
        'desc': 'Descrição', 'value': 'Valor', 'date': 'Data', 'time': 'Hora', 'schedule': 'AGENDAR',
        'manual_entry': 'Lançamento Manual', 'deposit': 'Depósito', 'withdraw': 'Retirada', 'execute': 'Executar'
    },
    'en': {
        'bal': 'Current Balance', 'missions': 'Missions', 'tools': 'Tools', 'admin': 'Command', 'logout': 'Logout',
        'home': 'Home', 'transfer': 'Transfer', 'last_mov': 'Recent Transactions',
        'active_missions': 'Your Active Missions', 'send_money': 'Send Money', 'to_whom': 'To whom?',
        'how_much': 'Amount?', 'reason': 'Reason', 'send_now': 'SEND NOW 💸', 'no_transfer': 'No users found.',
        'calc': 'Calculator', 'fx': 'Exchange', 'panel': 'Panel', 'new_task': 'New Task', 'mgmt': 'Manage', 'cashier': 'Cashier',
        'late_tasks': 'Overdue Tasks', 'apply_fine': 'Apply Fine', 'approve': 'Approve', 'reject': 'Reject',
        'desc': 'Description', 'value': 'Value', 'date': 'Date', 'time': 'Time', 'schedule': 'SCHEDULE',
        'manual_entry': 'Manual Entry', 'deposit': 'Deposit', 'withdraw': 'Withdraw', 'execute': 'Execute'
    },
    'es': {
        'bal': 'Saldo Actual', 'missions': 'Misiones', 'tools': 'Herramientas', 'admin': 'Comando', 'logout': 'Salir',
        'home': 'Inicio', 'transfer': 'Transferir', 'last_mov': 'Últimos Movimientos',
        'active_missions': 'Tus Misiones Activas', 'send_money': 'Enviar Dinero', 'to_whom': '¿A quién?',
        'how_much': '¿Cuánto?', 'reason': 'Motivo', 'send_now': 'ENVIAR AHORA 💸', 'no_transfer': 'Nadie para transferir.',
        'calc': 'Calculadora', 'fx': 'Cambio', 'panel': 'Panel', 'new_task': 'Nueva Tarea', 'mgmt': 'Gestión', 'cashier': 'Caja',
        'late_tasks': 'Tareas Atrasadas', 'apply_fine': 'Aplicar Multa', 'approve': 'Aprobar', 'reject': 'Rechazar',
        'desc': 'Descripción', 'value': 'Valor', 'date': 'Fecha', 'time': 'Hora', 'schedule': 'AGENDAR',
        'manual_entry': 'Entrada Manual', 'deposit': 'Depósito', 'withdraw': 'Retiro', 'execute': 'Ejecutar'
    }
}

def t(key):
    lang = st.session_state.get('lang', 'pt')
    return TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, key)

@st.cache_data(ttl=600)
def get_balance(uid):
    res = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': uid})
    val = res.iloc[0]['total'] if res is not None and not res.empty and pd.notnull(res.iloc[0]['total']) else 0.0
    return val
