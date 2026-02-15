# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO DE TEMA ---
st.set_page_config(page_title="Banco da Família Obsidian", page_icon="💎", layout="centered")

# --- 2. DICIONÁRIO DE TRADUÇÃO (i18n) ---
TRANSLATIONS = {
    'pt': {
        'protocol': 'Banco da Família v11.5',
        'user': 'Usuário',
        'password': 'Senha',
        'auth_btn': 'AUTENTICAR',
        'login_err': 'Acesso Negado.',
        'bal_family': 'Monitoramento de Ativos',
        'quick_tr': '💸 LANÇAMENTO TÁTICO',
        'target_acc': 'Conta de Destino:',
        'amount': 'Montante (R$)',
        'op': 'Operação',
        'op_dep': 'Depósito',
        'op_ret': 'Retirada',
        'reason': 'Motivo',
        'exec': 'EXECUTAR',
        'tr_success': 'Transação Confirmada.',
        'user_mgmt': '⚙️ COMANDO DE USUÁRIOS',
        'tab_list': 'Gerenciar',
        'tab_add': 'Novo Registro',
        'lvl': 'Nível',
        'create_acc': 'CADASTRAR',
        'bal_acc': 'Saldo em Conta',
        'enc_conn': '● CONEXÃO SEGURA',
        'tab_hist': '📊 Histórico',
        'tab_calc': '🧮 Calculadora',
        'tab_fx': '🌍 Câmbio',
        'tab_transf': '💸 Transferir',
        'tab_chores': '📝 Tarefas',
        'no_reg': 'Sem registros no momento.',
        'calc_btn': 'CALCULAR',
        'fx_title': 'Conversão Internacional',
        'fx_usd': 'Dólar Americano',
        'fx_eur': 'Euro',
        'fx_ref': 'Ref: R$',
        'fx_cap': 'Taxas de câmbio referenciais.',
        'logout': 'Sair',
        'refresh': 'Atualizar',
        'welcome': 'Olá',
        'actions': 'Ações',
        'del_user': 'Excluir Usuário',
        'change_pw': 'Trocar Senha',
        'notif_title': 'Notificações',
        'notif_empty': 'Sem alertas novos 🔕',
        'notif_clear': 'Limpar Tudo',
        'notif_new': 'Você tem novas mensagens! 🔔',
        'msg_gain': 'Você recebeu um acréscimo de',
        'msg_loss': 'Houve uma retirada de',
        'tr_dest': 'Para quem?',
        'tr_desc_lbl': 'Para que é isso?',
        'tr_desc_ph': 'Ex: Pagamento da Pizza',
        'tr_btn_send': 'ENVIAR AGORA',
        'tr_err_bal': 'Saldo Insuficiente para essa operação.',
        'tr_msg_sent': 'Você enviou',
        'tr_msg_recv': 'Você recebeu',
        'tr_self_err': 'Você não pode transferir para si mesmo.',
        'chore_mgmt': '📋 GESTÃO DE TAREFAS',
        'chore_new_title': 'Atribuir Tarefa',
        'chore_desc': 'Descrição da Tarefa',
        'chore_val': 'Recompensa (R$)',
        'chore_assignee': 'Responsável (Quem fará?)',
        'chore_deadline_d': 'Data Limite',
        'chore_deadline_t': 'Hora Limite',
        'chore_create': 'AGENDAR TAREFA',
        'chore_pending': '⏳ Aprovações',
        'chore_list_admin': '🔎 Painel Unificado',
        'chore_approve': 'APROVAR PAGAMENTO',
        'chore_reject': 'Recusar',
        'chore_list_avail': 'Minhas Missões',
        'chore_btn_do': '✅ ENTREGAR TAREFA',
        'chore_doing': 'Em Análise pelo Admin...',
        'chore_done_msg': 'Tarefa entregue! Aguarde validação.',
        'chore_paid_msg': 'Pagamento por tarefa realizada',
        'chore_clean_btn': '🗑️ Limpar Concluídas (>14 dias)',
        'chore_clean_success': 'Limpeza realizada com sucesso!',
        'chore_filter_status': 'Filtrar Status:',
        'chore_filter_kid': 'Filtrar Criança:',
        'status_open': 'Aberto',
        'status_pending': 'Em Análise',
        'status_paid': 'Concluído',
        'status_failed': 'Falhou (Multa)',
        'punish_zone': '🚨 ZONA DE PUNIÇÃO (ATRASOS)',
        'punish_days': 'dias de atraso',
        'punish_val': 'Valor da Multa (R$)',
        'punish_btn': 'APLICAR MULTA & ENCERRAR',
        'punish_msg': 'Multa aplicada por não cumprimento de tarefa'
    },
    'en': {
        'protocol': 'Family Bank v11.5',
        'user': 'User',
        'password': 'Password',
        'auth_btn': 'AUTHENTICATE',
        'login_err': 'Access Denied.',
        'bal_family': 'Asset Monitoring',
        'quick_tr': '💸 TACTICAL TRANSACTION',
        'target_acc': 'Target Account:',
        'amount': 'Amount (R$)',
        'op': 'Operation',
        'op_dep': 'Deposit',
        'op_ret': 'Withdrawal',
        'reason': 'Reason',
        'exec': 'EXECUTE',
        'tr_success': 'Transaction Confirmed.',
        'user_mgmt': '⚙️ USER COMMAND',
        'tab_list': 'Manage',
        'tab_add': 'New Registry',
        'lvl': 'Level',
        'create_acc': 'REGISTER',
        'bal_acc': 'Account Balance',
        'enc_conn': '● SECURE CONNECTION',
        'tab_hist': '📊 History',
        'tab_calc': '🧮 Calculator',
        'tab_fx': '🌍 Exchange',
        'tab_transf': '💸 Transfer',
        'tab_chores': '📝 Chores',
        'no_reg': 'No records found.',
        'calc_btn': 'CALCULATE',
        'fx_title': 'International Conversion',
        'fx_usd': 'US Dollar',
        'fx_eur': 'Euro',
        'fx_ref': 'Ref: BRL',
        'fx_cap': 'Exchange rates based on market reference.',
        'logout': 'Logout',
        'refresh': 'Refresh',
        'welcome': 'Hello',
        'actions': 'Actions',
        'del_user': 'Delete User',
        'change_pw': 'Change Password',
        'notif_title': 'Notifications',
        'notif_empty': 'No new alerts 🔕',
        'notif_clear': 'Clear All',
        'notif_new': 'You have new messages! 🔔',
        'msg_gain': 'You received an increase of',
        'msg_loss': 'There was a decrease of',
        'tr_dest': 'To whom?',
        'tr_desc_lbl': 'What is this for?',
        'tr_desc_ph': 'Ex: Pizza payment',
        'tr_btn_send': 'SEND NOW',
        'tr_err_bal': 'Insufficient funds.',
        'tr_msg_sent': 'You sent',
        'tr_msg_recv': 'You received',
        'tr_self_err': 'You cannot transfer to yourself.',
        'chore_mgmt': '📋 CHORE MANAGEMENT',
        'chore_new_title': 'Assign Chore',
        'chore_desc': 'Chore Description',
        'chore_val': 'Reward (R$)',
        'chore_assignee': 'Assignee (Who?)',
        'chore_deadline_d': 'Deadline Date',
        'chore_deadline_t': 'Deadline Time',
        'chore_create': 'SCHEDULE CHORE',
        'chore_pending': '⏳ Approvals',
        'chore_list_admin': '🔎 Unified Panel',
        'chore_approve': 'APPROVE PAYMENT',
        'chore_reject': 'Reject',
        'chore_list_avail': 'My Missions',
        'chore_btn_do': '✅ SUBMIT CHORE',
        'chore_doing': 'Under Review...',
        'chore_done_msg': 'Chore submitted! Wait for validation.',
        'chore_paid_msg': 'Payment for completed chore',
        'chore_clean_btn': '🗑️ Clean Completed (>14 days)',
        'chore_clean_success': 'Cleanup successful!',
        'chore_filter_status': 'Filter Status:',
        'chore_filter_kid': 'Filter Child:',
        'status_open': 'Open',
        'status_pending': 'Pending',
        'status_paid': 'Done',
        'status_failed': 'Failed (Fined)',
        'punish_zone': '🚨 PUNISHMENT ZONE (OVERDUE)',
        'punish_days': 'days overdue',
        'punish_val': 'Fine Amount (R$)',
        'punish_btn': 'APPLY FINE & CLOSE',
        'punish_msg': 'Fine applied for failed chore'
    },
    'es': {
        'protocol': 'Banco de la Familia v11.5',
        'user': 'Usuario',
        'password': 'Contraseña',
        'auth_btn': 'AUTENTICAR',
        'login_err': 'Acceso Denegado.',
        'bal_family': 'Monitoreo de Activos',
        'quick_tr': '💸 LANZAMIENTO TÁCTICO',
        'target_acc': 'Cuenta Destino:',
        'amount': 'Monto (R$)',
        'op': 'Operación',
        'op_dep': 'Depósito',
        'op_ret': 'Retiro',
        'reason': 'Motivo',
        'exec': 'EJECUTAR',
        'tr_success': 'Transacción Confirmada.',
        'user_mgmt': '⚙️ COMANDO DE USUARIOS',
        'tab_list': 'Gestionar',
        'tab_add': 'Nuevo Registro',
        'lvl': 'Nivel',
        'create_acc': 'REGISTRAR',
        'bal_acc': 'Saldo en Cuenta',
        'enc_conn': '● CONEXIÓN SEGURA',
        'tab_hist': '📊 Historial',
        'tab_calc': '🧮 Calculadora',
        'tab_fx': '🌍 Cambio',
        'tab_transf': '💸 Transferir',
        'tab_chores': '📝 Tareas',
        'no_reg': 'Sin registros por ahora.',
        'calc_btn': 'CALCULAR',
        'fx_title': 'Conversión Internacional',
        'fx_usd': 'Dólar Americano',
        'fx_eur': 'Euro',
        'fx_ref': 'Ref: R$',
        'fx_cap': 'Tasas de cambio basadas en referencias.',
        'logout': 'Salir',
        'refresh': 'Actualizar',
        'welcome': 'Hola',
        'actions': 'Acciones',
        'del_user': 'Eliminar Usuario',
        'change_pw': 'Cambiar Contraseña',
        'notif_title': 'Notificaciones',
        'notif_empty': 'Sin alertas nuevas 🔕',
        'notif_clear': 'Limpiar Todo',
        'notif_new': '¡Tienes nuevos mensajes! 🔔',
        'msg_gain': 'Recibiste un incremento de',
        'msg_loss': 'Hubo un decrecimiento de',
        'tr_dest': '¿A quién?',
        'tr_desc_lbl': '¿Para qué es esto?',
        'tr_desc_ph': 'Ej: Pago de Pizza',
        'tr_btn_send': 'ENVIAR AHORA',
        'tr_err_bal': 'Fondos insuficientes.',
        'tr_msg_sent': 'Enviaste',
        'tr_msg_recv': 'Recibiste',
        'tr_self_err': 'No puedes transferirte a ti mismo.',
        'chore_mgmt': '📋 GESTIÓN DE TAREAS',
        'chore_new_title': 'Asignar Tarea',
        'chore_desc': 'Descripción',
        'chore_val': 'Recompensa (R$)',
        'chore_assignee': 'Responsable (¿Quién?)',
        'chore_deadline_d': 'Fecha Límite',
        'chore_deadline_t': 'Hora Límite',
        'chore_create': 'AGENDAR TAREA',
        'chore_pending': '⏳ Aprobaciones',
        'chore_list_admin': '🔎 Panel Unificado',
        'chore_approve': 'APROBAR PAGO',
        'chore_reject': 'Rechazar',
        'chore_list_avail': 'Mis Misiones',
        'chore_btn_do': '✅ ENTREGAR TAREA',
        'chore_doing': 'En Revisión...',
        'chore_done_msg': '¡Tarea entregada! Espera validación.',
        'chore_paid_msg': 'Pago por tarea completada',
        'chore_clean_btn': '🗑️ Limpiar Viejas (>14 días)',
        'chore_clean_success': 'Limpieza realizada con éxito!',
        'chore_filter_status': 'Filtrar Estado:',
        'chore_filter_kid': 'Filtrar Niño:',
        'status_open': 'Abierto',
        'status_pending': 'Pendiente',
        'status_paid': 'Concluido',
        'status_failed': 'Falló (Multa)',
        'punish_zone': '🚨 ZONA DE CASTIGO (ATRASOS)',
        'punish_days': 'días de retraso',
        'punish_val': 'Monto Multa (R$)',
        'punish_btn': 'APLICAR MULTA Y CERRAR',
        'punish_msg': 'Multa aplicada por tarea fallida'
    }
}

def t(key):
    lang = st.session_state.get('lang', 'pt')
    return TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, key)

# --- CSS REFINADO & RESPONSIVO (V11.5) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #080809;
        color: #F0F0F0;
    }
    
    .stApp { background-color: #080809; }
    
    #MainMenu, footer { visibility: hidden !important; }
    header { background-color: transparent !important; }

    .block-container { padding-top: 1.5rem !important; max-width: 500px !important; }

    .obsidian-logo {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        color: #00E5FF;
        background: linear-gradient(135deg, #00E5FF 0%, #007BFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        white-space: nowrap;
    }
    
    .obsidian-card {
        background: #111114;
        border: 1px solid #222226;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }

    .row-item {
        border-bottom: 1px solid #1A1A1E;
        padding: 14px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .label-caption {
        color: #D1D5DB;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .value-main {
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -2px;
    }

    .stButton>button {
        border-radius: 12px !important;
        background: #1A1A1D !important;
        color: #F0F0F0 !important;
        border: 1px solid #2D2D32 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        height: 44px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton>button:hover {
        border-color: #00E5FF !important;
        color: #00E5FF !important;
        background: #1F1F23 !important;
        transform: translateY(-1px);
    }

    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #00E5FF 0%, #007BFF 100%) !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 700 !important;
    }

    button[key*="del_"], button[key*="punish_"] {
        border-color: #EF4444 !important;
        color: #EF4444 !important;
    }
    button[key*="del_"]:hover, button[key*="punish_"]:hover {
        background: #EF4444 !important;
        color: white !important;
    }
    
    /* Botão de Concluir Tarefa */
    button[key*="done_"] {
        border-color: #10B981 !important;
        color: #10B981 !important;
    }
    button[key*="done_"]:hover {
        background: #10B981 !important;
        color: white !important;
    }
    
    /* Botão de Limpeza */
    button[key="btn_clean_chores"] {
        border-color: #A1A1AA !important;
        color: #A1A1AA !important;
    }

    .notif-badge {
        background-color: #EF4444; color: white; border-radius: 50%; padding: 2px 6px; font-size: 0.6rem;
    }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #111114 !important; border: 1px solid #222226 !important; border-radius: 20px !important; height: 32px !important; font-size: 0.75rem !important;
    }

    .display-calc {
        background-color: #050506; border: 2px solid #1F1F23; border-radius: 16px; padding: 20px;
        text-align: right; font-size: 2.2rem; font-family: 'JetBrains Mono', monospace;
        color: #00E5FF; margin-bottom: 15px; min-height: 80px;
        display: flex; align-items: center; justify-content: flex-end;
        box-shadow: inset 0 2px 15px rgba(0,0,0,0.9);
    }

    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #222226; gap: 4px; }
    .stTabs [data-baseweb="tab"] { color: #A1A1AA; font-weight: 600; font-size: 0.8rem; }
    .stTabs [aria-selected="true"] { color: #00E5FF !important; border-bottom-color: #00E5FF !important; }
    .stTextInput input, .stNumberInput input { background-color: #0F0F12 !important; border: 1px solid #222226 !important; border-radius: 12px !important; }
    hr { border: 0; border-top: 1px solid #222226; margin: 1.5rem 0; }
    
    /* Data/Hora Picker Override */
    div[data-baseweb="calendar"] { background-color: #111114 !important; }
    div[data-baseweb="timepicker"] { background-color: #111114 !important; }

    /* --- OVERLAY DE ROTAÇÃO OBRIGATÓRIA --- */
    #rotate-overlay { display: none; }

    @media only screen and (max-width: 900px) and (orientation: portrait) {
        #rotate-overlay {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background-color: #080809; z-index: 99999;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            text-align: center; padding: 20px;
        }
        .rotate-icon { font-size: 4rem; margin-bottom: 20px; animation: rotate-anim 2s infinite ease-in-out; }
        .rotate-text { font-family: 'Inter', sans-serif; color: #00E5FF; font-weight: 700; font-size: 1.2rem; margin-bottom: 10px; }
        .rotate-sub { color: #6B7280; font-size: 0.9rem; }
        @keyframes rotate-anim {
            0% { transform: rotate(0deg); } 25% { transform: rotate(-90deg); } 50% { transform: rotate(-90deg); } 100% { transform: rotate(0deg); }
        }
    }
    
    @media only screen and (max-width: 900px) and (orientation: landscape) {
        .block-container { max-width: 800px !important; padding-top: 1rem !important; }
        div[data-testid="column"] { min-width: 0 !important; }
        .stButton>button { height: 55px !important; font-size: 1.1rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE DADOS SEGURO ---
@st.cache_resource
def get_connection():
    try:
        return st.connection("supabase", type="sql")
    except Exception:
        return None

conn = get_connection()

def run_query(query_str, params=None, commit=False):
    if not conn: return None
    try:
        if commit:
            with conn.session as s:
                s.execute(text(query_str), params if params else {})
                s.commit()
            st.cache_data.clear()
            return True
        else:
            return conn.query(query_str, params=params if params else {}, ttl=0)
    except Exception:
        return None

def init_db():
    if not conn: return
    run_query('''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, role TEXT, password TEXT, language TEXT DEFAULT 'pt');''', commit=True)
    run_query('''CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, user_id INTEGER, amount REAL, description TEXT, timestamp TIMESTAMP, type TEXT);''', commit=True)
    run_query('''CREATE TABLE IF NOT EXISTS notifications (id SERIAL PRIMARY KEY, user_id INTEGER, message TEXT, is_read BOOLEAN DEFAULT FALSE, timestamp TIMESTAMP);''', commit=True)
    # Tabela de Tarefas (Chores) - Atualizada com Deadline
    run_query('''CREATE TABLE IF NOT EXISTS chores (id SERIAL PRIMARY KEY, description TEXT, reward REAL, status TEXT DEFAULT 'open', assigned_to INTEGER, created_at TIMESTAMP, deadline TIMESTAMP);''', commit=True)
    try:
        # Patch de Migração para v11.2 (Adicionar deadline se não existir)
        run_query("ALTER TABLE chores ADD COLUMN IF NOT EXISTS deadline TIMESTAMP;", commit=True)
    except: pass
    try: run_query("ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'pt';", commit=True)
    except: pass

if conn:
    init_db()

@st.cache_data(ttl=600)
def get_cached_balance(uid):
    res = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': uid})
    return res.iloc[0]['total'] if res is not None and not res.empty and pd.notnull(res.iloc[0]['total']) else 0.0

@st.cache_data(ttl=600)
def get_cached_family_balances():
    query = """
        SELECT u.id, u.name, COALESCE(SUM(t.amount), 0) as balance 
        FROM users u 
        LEFT JOIN transactions t ON u.id = t.user_id 
        WHERE u.role = 'user' 
        GROUP BY u.name, u.id ORDER BY u.name
    """
    return run_query(query)

@st.cache_data(ttl=600)
def get_cached_history(uid):
    return run_query("SELECT timestamp as data, description as motivo, amount as valor FROM transactions WHERE user_id=:uid ORDER BY id DESC LIMIT 15", params={'uid': uid})

def get_unread_notifs(uid):
    return run_query("SELECT * FROM notifications WHERE user_id=:uid AND is_read=FALSE ORDER BY timestamp DESC", params={'uid': uid})

# --- 4. ESTADO ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'calc_expr' not in st.session_state: st.session_state.calc_expr = ""
if 'lang' not in st.session_state: st.session_state.lang = 'pt'
if 'show_notifs' not in st.session_state: st.session_state.show_notifs = False

# --- 5. LOGIN ---
if not st.session_state.logged_in:
    if not conn:
        st.error("Erro: Base de dados não configurada.")
        st.stop()
        
    st.markdown(f"<div style='margin-top:5rem; text-align:center;'><h1 class='obsidian-logo'>💎 Banco da Família</h1><p style='color:#A1A1AA; font-weight:600; font-size:0.8rem;'>{t('protocol')}</p></div>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        u = st.text_input(t('user')).lower().strip()
        p = st.text_input(t('password'), type="password").strip()
        if st.form_submit_button(t('auth_btn'), use_container_width=True):
            df = run_query("SELECT * FROM users WHERE lower(name)=:u AND password=:p", params={'u': u, 'p': p})
            if df is not None and not df.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = int(df.iloc[0]['id'])
                st.session_state.user_name = df.iloc[0]['name']
                st.session_state.role = df.iloc[0]['role']
                st.session_state.lang = df.iloc[0]['language'] if 'language' in df.columns else 'pt'
                st.cache_data.clear()
                st.rerun()
            else: 
                st.toast(t('login_err'))

# --- 6. DASHBOARD ---
else:
    # --- NAVBAR ---
    n_col1, n_col2, n_col_bell, n_col3, n_col4 = st.columns([1.3, 0.7, 0.3, 0.3, 0.3])
    with n_col1:
        st.markdown("<div class='obsidian-logo'>💎 Banco da Família</div>", unsafe_allow_html=True)
    
    with n_col2:
        options = {'🇧🇷 PT': 'pt', '🇺🇸 EN': 'en', '🇪🇸 ES': 'es'}
        inv_options = {v: k for k, v in options.items()}
        curr_lang = st.session_state.lang if st.session_state.lang in inv_options else 'pt'
        new_lang_label = st.selectbox("", options.keys(), index=list(options.values()).index(curr_lang), label_visibility="collapsed", key="lang_pill")
        new_lang_code = options[new_lang_label]
        if new_lang_code != st.session_state.lang:
            st.session_state.lang = new_lang_code
            run_query("UPDATE users SET language=:l WHERE id=:id", params={'l': new_lang_code, 'id': st.session_state.user_id}, commit=True)
            st.rerun()

    unread = get_unread_notifs(st.session_state.user_id)
    count = len(unread) if unread is not None else 0
    
    with n_col_bell:
        bell_icon = "🔔" if count > 0 else "🔕"
        if st.button(bell_icon, key="bell_btn"):
            st.session_state.show_notifs = not st.session_state.show_notifs

    with n_col3:
        if st.button("🔄", key="ref"):
            st.cache_data.clear(); st.rerun()
    with n_col4:
        if st.button("🚪", key="out"):
            st.session_state.logged_in = False; st.cache_data.clear(); st.rerun()

    if st.session_state.show_notifs:
        with st.container():
            st.markdown(f"<div class='obsidian-card' style='border-color:#00E5FF;'>", unsafe_allow_html=True)
            st.markdown(f"<div class='label-caption'>{t('notif_title')}</div>", unsafe_allow_html=True)
            if count > 0:
                for _, n in unread.iterrows():
                    st.markdown(f"<div style='font-size:0.85rem; padding:5px 0;'>• {n['message']} <br><small style='color:#6B7280;'>{n['timestamp'].strftime('%H:%M:%S')}</small></div>", unsafe_allow_html=True)
                if st.button(t('notif_clear'), key="clear_notif"):
                    run_query("UPDATE notifications SET is_read=TRUE WHERE user_id=:uid", params={'uid': st.session_state.user_id}, commit=True)
                    st.session_state.show_notifs = False; st.rerun()
            else:
                st.markdown(f"<div style='font-size:0.85rem; color:#6B7280;'>{t('notif_empty')}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.role == 'admin':
        st.markdown("<div class='obsidian-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='label-caption'>{t('bal_family')}</div>", unsafe_allow_html=True)
        df_saldos = get_cached_family_balances()
        if df_saldos is not None and not df_saldos.empty:
            for _, row in df_saldos.iterrows():
                st.markdown(f"<div class='row-item'><span style='font-weight:600;'>{row['name'].title()}</span><span style='color:#00E5FF; font-family:monospace; font-weight:700;'>R$ {row['balance']:,.2f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # --- GESTÃO DE TAREFAS (ADMIN - v11.5) ---
        with st.expander(t('chore_mgmt')):
            ct1, ct2, ct3 = st.tabs([t('chore_new_title'), t('chore_pending'), t('chore_list_admin')])
            
            # 1. ATRIBUIR TAREFA
            with ct1:
                kids_df = run_query("SELECT id, name FROM users WHERE role='user'")
                if kids_df is not None and not kids_df.empty:
                    with st.form("new_chore_admin"):
                        c_desc = st.text_input(t('chore_desc'))
                        c_val = st.number_input(t('chore_val'), min_value=0.5, step=0.5)
                        
                        c_assignee = st.selectbox(t('chore_assignee'), kids_df['name'].tolist())
                        col_d, col_t = st.columns(2)
                        d_date = col_d.date_input(t('chore_deadline_d'))
                        d_time = col_t.time_input(t('chore_deadline_t'), value=dt_time(23, 59))
                        
                        if st.form_submit_button(t('chore_create'), use_container_width=True):
                            if c_desc and c_val > 0:
                                kid_id = kids_df[kids_df['name'] == c_assignee]['id'].values[0]
                                deadline_dt = datetime.combine(d_date, d_time)
                                
                                run_query("INSERT INTO chores (description, reward, status, assigned_to, created_at, deadline) VALUES (:d, :r, 'open', :uid, :ts, :dl)",
                                          params={'d': c_desc, 'r': c_val, 'uid': int(kid_id), 'ts': datetime.now(), 'dl': deadline_dt}, commit=True)
                                
                                run_query("INSERT INTO notifications (user_id, message, timestamp) VALUES (:uid, :msg, :ts)",
                                          params={'uid': int(kid_id), 'msg': f"📋 Nova Tarefa: {c_desc} (R$ {c_val})", 'ts': datetime.now()}, commit=True)
                                
                                st.success("OK")
                                st.rerun()
                else:
                    st.warning("Cadastre crianças primeiro.")
            
            # 2. APROVAR PENDENTES
            with ct2:
                pending_chores = run_query("SELECT c.id, c.description, c.reward, u.name as kid_name, u.id as kid_id FROM chores c JOIN users u ON c.assigned_to = u.id WHERE c.status = 'pending'")
                if pending_chores is not None and not pending_chores.empty:
                    for _, pc in pending_chores.iterrows():
                        st.markdown(f"""
                        <div class='row-item'>
                            <div>
                                <div style='font-size:0.9rem; font-weight:700;'>{pc['kid_name'].title()}</div>
                                <div style='font-size:0.8rem; color:#A1A1AA;'>{pc['description']}</div>
                            </div>
                            <div style='color:#00E5FF; font-weight:700;'>R$ {pc['reward']:,.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        ac1, ac2 = st.columns(2)
                        if ac1.button(t('chore_approve'), key=f"appr_{pc['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='paid' WHERE id=:cid", params={'cid': pc['id']}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, 'Pagamento Tarefa')", 
                                      params={'uid': int(pc['kid_id']), 'amt': pc['reward'], 'desc': f"{t('chore_paid_msg')}: {pc['description']}", 'ts': datetime.now()}, commit=True)
                            run_query("INSERT INTO notifications (user_id, message, timestamp) VALUES (:uid, :msg, :ts)",
                                      params={'uid': int(pc['kid_id']), 'msg': f"💰 {t('chore_paid_msg')}: R$ {pc['reward']}", 'ts': datetime.now()}, commit=True)
                            st.rerun()
                            
                        if ac2.button(t('chore_reject'), key=f"rej_{pc['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='open' WHERE id=:cid", params={'cid': pc['id']}, commit=True)
                            st.rerun()
                else:
                    st.info("Nenhuma tarefa aguardando aprovação.")
            
            # 3. MONITORAMENTO UNIFICADO + PUNIÇÃO (v11.5)
            with ct3:
                # --- ZONA DE PUNIÇÃO (Novo) ---
                overdue_chores = run_query("""
                    SELECT c.id, c.description, c.reward, c.deadline, u.name as kid_name, u.id as kid_id 
                    FROM chores c JOIN users u ON c.assigned_to = u.id 
                    WHERE c.status = 'open' AND c.deadline < NOW()
                """)
                
                if overdue_chores is not None and not overdue_chores.empty:
                    st.markdown(f"""
                    <div style='background-color:#2A1215; border:1px solid #EF4444; border-radius:12px; padding:15px; margin-bottom:20px;'>
                        <div style='color:#EF4444; font-weight:800; font-size:0.9rem; display:flex; align-items:center; gap:8px;'>
                            🚨 {t('punish_zone')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for _, oc in overdue_chores.iterrows():
                        days_late = (datetime.now() - pd.to_datetime(oc['deadline'])).days
                        with st.container():
                            st.markdown(f"""
                            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;'>
                                <div>
                                    <span style='font-weight:700; color:#EF4444;'>{oc['kid_name'].title()}</span>: {oc['description']}
                                </div>
                                <div style='font-size:0.8rem; color:#A1A1AA;'>{days_late} {t('punish_days')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            pc1, pc2 = st.columns([0.6, 0.4])
                            p_val = pc1.number_input(t('punish_val'), min_value=0.0, step=0.5, value=float(oc['reward']), key=f"pval_{oc['id']}")
                            if pc2.button(t('punish_btn'), key=f"punish_{oc['id']}", use_container_width=True):
                                # 1. Atualizar tarefa para FAILED
                                run_query("UPDATE chores SET status='failed' WHERE id=:cid", params={'cid': oc['id']}, commit=True)
                                
                                # 2. Aplicar Multa Financeira (Débito)
                                if p_val > 0:
                                    run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, 'Multa por Atraso')", 
                                              params={'uid': int(oc['kid_id']), 'amt': -p_val, 'desc': f"{t('punish_msg')}: {oc['description']}", 'ts': datetime.now()}, commit=True)
                                    
                                    # 3. Notificar
                                    run_query("INSERT INTO notifications (user_id, message, timestamp) VALUES (:uid, :msg, :ts)",
                                              params={'uid': int(oc['kid_id']), 'msg': f"🚨 MULTA APLICADA: R$ {p_val} ({oc['description']} não realizada)", 'ts': datetime.now()}, commit=True)
                                
                                st.warning("Punição aplicada com sucesso.")
                                time.sleep(1.5)
                                st.rerun()
                    st.markdown("---")

                # --- FILTROS E TABELA UNIFICADA ---
                kids_df = run_query("SELECT id, name FROM users WHERE role='user'")
                if kids_df is not None and not kids_df.empty:
                    f_col1, f_col2 = st.columns(2)
                    
                    status_opts = {'open': t('status_open'), 'pending': t('status_pending'), 'paid': t('status_paid'), 'failed': t('status_failed')}
                    inv_status = {v: k for k, v in status_opts.items()}
                    
                    with f_col1:
                        sel_status_label = st.multiselect(t('chore_filter_status'), options=list(status_opts.values()), default=list(status_opts.values()))
                        sel_status_db = [inv_status[l] for l in sel_status_label]
                    
                    with f_col2:
                        sel_kids = st.multiselect(t('chore_filter_kid'), options=kids_df['name'].tolist(), default=kids_df['name'].tolist())

                    if sel_status_db and sel_kids:
                        base_sql = "SELECT u.name as kid_name, c.description, c.reward, c.status, c.deadline FROM chores c JOIN users u ON c.assigned_to = u.id WHERE 1=1"
                        all_chores_raw = run_query(base_sql)
                        
                        if all_chores_raw is not None and not all_chores_raw.empty:
                            filtered_df = all_chores_raw[
                                (all_chores_raw['status'].isin(sel_status_db)) &
                                (all_chores_raw['kid_name'].isin(sel_kids))
                            ].copy()
                            
                            if not filtered_df.empty:
                                filtered_df['reward'] = filtered_df['reward'].apply(lambda x: f"R$ {x:.2f}")
                                filtered_df['deadline'] = pd.to_datetime(filtered_df['deadline']).dt.strftime('%d/%m %H:%M')
                                filtered_df['status'] = filtered_df['status'].map(status_opts)
                                
                                filtered_df = filtered_df.rename(columns={'kid_name': 'Criança', 'description': 'Tarefa', 'reward': 'Valor', 'status': 'Estado', 'deadline': 'Prazo'})
                                st.dataframe(filtered_df[['Criança', 'Tarefa', 'Valor', 'Prazo', 'Estado']], use_container_width=True, hide_index=True)
                            else:
                                st.info("Nenhum registro com esses filtros.")
                        else:
                            st.info("Sem dados no sistema.")
                    else:
                        st.warning("Selecione os filtros.")

                    st.markdown("---")
                    if st.button(t('chore_clean_btn'), key="btn_clean_chores"):
                        clean_sql = "DELETE FROM chores WHERE status IN ('paid', 'failed') AND ((deadline IS NOT NULL AND deadline < NOW() - INTERVAL '14 days') OR (deadline IS NULL AND created_at < NOW() - INTERVAL '14 days'))"
                        run_query(clean_sql, commit=True)
                        st.success(t('chore_clean_success'))
                        time.sleep(1.5)
                        st.rerun()


        with st.expander(t('quick_tr')):
            users_df = run_query("SELECT id, name FROM users WHERE role='user'")
            if users_df is not None and not users_df.empty:
                with st.form("new_trans_p"):
                    target = st.selectbox(t('target_acc'), users_df['name'].tolist())
                    val = st.number_input(t('amount'), min_value=0.0, step=1.0)
                    tipo = st.radio(t('op'), [t('op_dep'), t('op_ret')], horizontal=True)
                    desc = st.text_input(t('reason'))
                    if st.form_submit_button(t('exec'), use_container_width=True):
                        if val > 0 and desc:
                            u_target_id = users_df[users_df['name'] == target]['id'].values[0]
                            db_t = 'Depósito' if tipo == t('op_dep') else 'Retirada'
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, :t)", 
                                      params={'uid': int(u_target_id), 'amt': val if db_t == 'Depósito' else -val, 'desc': desc, 'ts': datetime.now(), 't': db_t}, commit=True)
                            prefix = t('msg_gain') if db_t == 'Depósito' else t('msg_loss')
                            msg = f"{prefix} R$ {val:,.2f} ({desc})"
                            run_query("INSERT INTO notifications (user_id, message, timestamp) VALUES (:uid, :msg, :ts)", 
                                      params={'uid': int(u_target_id), 'msg': msg, 'ts': datetime.now()}, commit=True)
                            st.success(t('tr_success')); time.sleep(1); st.rerun()

        with st.expander(t('user_mgmt')):
            t_l, t_a = st.tabs([t('tab_list'), t('tab_add')])
            with t_l:
                all_u = run_query("SELECT id, name, role FROM users ORDER BY name")
                if all_u is not None and not all_u.empty:
                    st.dataframe(all_u, use_container_width=True, hide_index=True)
                    sel_user_name = st.selectbox(t('user'), all_u['name'].tolist(), key="sel_mod")
                    sel_u_data = all_u[all_u['name'] == sel_user_name].iloc[0]
                    c_pw, c_del = st.columns(2)
                    with c_pw:
                        with st.popover(t('change_pw'), use_container_width=True):
                            new_pw = st.text_input(t('password'), type="password", key="new_pw_f")
                            if st.button(t('exec'), key="btn_pw"):
                                run_query("UPDATE users SET password=:p WHERE id=:id", params={'p': new_pw, 'id': int(sel_u_data['id'])}, commit=True)
                                st.success("OK")
                    with c_del:
                        if st.button(t('del_user'), key=f"del_{sel_u_data['id']}", use_container_width=True):
                            if int(sel_u_data['id']) != st.session_state.user_id:
                                run_query("DELETE FROM notifications WHERE user_id=:id", params={'id': int(sel_u_data['id'])}, commit=True)
                                run_query("DELETE FROM transactions WHERE user_id=:id", params={'id': int(sel_u_data['id'])}, commit=True)
                                run_query("DELETE FROM users WHERE id=:id", params={'id': int(sel_u_data['id'])}, commit=True)
                                st.rerun()

    else:
        if count > 0: st.toast(t('notif_new'))
        
        saldo_brl = get_cached_balance(st.session_state.user_id)
        st.markdown(f"""
        <div class="obsidian-card">
            <div class="label-caption">{t('bal_acc')} | {st.session_state.user_name.upper()}</div>
            <div class="value-main">R$ {saldo_brl:,.2f}</div>
            <div style="margin-top:10px; font-size:0.6rem; color:#00E5FF; font-weight:700;">{t('enc_conn')}</div>
        </div>
        """, unsafe_allow_html=True)

        # --- TABS REORGANIZADOS (HISTORICO, TRANSFERIR, TAREFAS, CALCULADORA, CAMBIO) ---
        tabs = st.tabs([t('tab_hist'), t('tab_transf'), t('tab_chores'), t('tab_calc'), t('tab_fx')])
        
        with tabs[0]:
            df_h = get_cached_history(st.session_state.user_id)
            if df_h is not None and not df_h.empty: st.dataframe(df_h, use_container_width=True, hide_index=True)
            else: st.info(t('no_reg'))
        
        # --- ABA TRANSFERIR ---
        with tabs[1]:
            st.markdown(f"<div class='label-caption' style='margin-bottom:10px;'>{t('quick_tr')}</div>", unsafe_allow_html=True)
            siblings = run_query("SELECT id, name FROM users WHERE role='user' AND id != :uid", params={'uid': st.session_state.user_id})
            
            if siblings is not None and not siblings.empty:
                with st.form("p2p_transfer"):
                    target_sibling = st.selectbox(t('tr_dest'), siblings['name'].tolist())
                    amt_send = st.number_input(t('amount'), min_value=0.0, step=1.0)
                    desc_send = st.text_input(t('tr_desc_lbl'), placeholder=t('tr_desc_ph'))
                    
                    if st.form_submit_button(t('tr_btn_send'), use_container_width=True):
                        if amt_send > saldo_brl:
                            st.error(t('tr_err_bal'))
                        elif amt_send > 0 and desc_send:
                            dest_id = siblings[siblings['name'] == target_sibling]['id'].values[0]
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, 'Transferência Enviada')", 
                                      params={'uid': st.session_state.user_id, 'amt': -amt_send, 'desc': f"Para: {target_sibling.title()} | {desc_send}", 'ts': datetime.now()}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, 'Transferência Recebida')", 
                                      params={'uid': int(dest_id), 'amt': amt_send, 'desc': f"De: {st.session_state.user_name.title()} | {desc_send}", 'ts': datetime.now()}, commit=True)
                            run_query("INSERT INTO notifications (user_id, message, timestamp) VALUES (:uid, :msg, :ts)",
                                      params={'uid': st.session_state.user_id, 'msg': f"{t('tr_msg_sent')} R$ {amt_send} -> {target_sibling.title()}", 'ts': datetime.now()}, commit=True)
                            run_query("INSERT INTO notifications (user_id, message, timestamp) VALUES (:uid, :msg, :ts)",
                                      params={'uid': int(dest_id), 'msg': f"{t('tr_msg_recv')} R$ {amt_send} <- {st.session_state.user_name.title()}", 'ts': datetime.now()}, commit=True)
                            st.success(t('tr_success')); time.sleep(1.5); st.rerun()
            else:
                st.info("Nenhum outro usuário disponível para transferência.")
        
        # --- ABA TAREFAS (USER - Somente Atribuídas a Mim) ---
        with tabs[2]:
            st.markdown(f"<div class='label-caption' style='margin-bottom:10px;'>{t('chore_list_avail')}</div>", unsafe_allow_html=True)
            
            # Tarefas Abertas (Atribuídas a este User)
            open_chores = run_query("SELECT * FROM chores WHERE status = 'open' AND assigned_to = :uid ORDER BY deadline ASC", params={'uid': st.session_state.user_id})
            
            if open_chores is not None and not open_chores.empty:
                for _, chore in open_chores.iterrows():
                    with st.container():
                        # Lógica de Prazo
                        deadline_str = ""
                        is_late = False
                        if pd.notnull(chore['deadline']):
                            dl = pd.to_datetime(chore['deadline'])
                            deadline_str = dl.strftime("%d/%m %H:%M")
                            if dl < datetime.now(): is_late = True
                        
                        color_border = "#EF4444" if is_late else "#00E5FF"
                        late_badge = "🔴 ATRASADA!" if is_late else f"📅 {deadline_str}"
                        
                        st.markdown(f"""
                        <div class='obsidian-card' style='padding:1rem; border-color:{color_border};'>
                            <div style='display:flex; justify-content:space-between; align-items:center;'>
                                <div>
                                    <div style='font-size:0.9rem; font-weight:700;'>{chore['description']}</div>
                                    <div style='font-size:0.75rem; color:#A1A1AA; margin-top:2px;'>{late_badge}</div>
                                </div>
                                <div style='font-size:0.9rem; color:#10B981; font-weight:700;'>R$ {chore['reward']:,.2f}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(t('chore_btn_do'), key=f"done_{chore['id']}", use_container_width=True):
                            run_query("UPDATE chores SET status='pending' WHERE id=:cid", params={'cid': chore['id']}, commit=True)
                            st.toast(t('chore_done_msg'))
                            time.sleep(1)
                            st.rerun()
            else:
                st.markdown(f"<div style='text-align:center; color:#6B7280; font-size:0.8rem; padding:20px;'>Tudo limpo por aqui! Nenhuma tarefa pendente. 🌟</div>", unsafe_allow_html=True)
            
            # Tarefas em Análise (Minhas)
            my_pending = run_query("SELECT * FROM chores WHERE status = 'pending' AND assigned_to = :uid", params={'uid': st.session_state.user_id})
            if my_pending is not None and not my_pending.empty:
                st.markdown("---")
                st.caption(t('chore_doing'))
                for _, mp in my_pending.iterrows():
                    st.markdown(f"⏳ {mp['description']} (R$ {mp['reward']:,.2f})")

        # --- TAB CALCULADORA ---
        with tabs[3]:
            st.markdown("""
            <div id="rotate-overlay">
                <div class="rotate-icon">📱</div>
                <div class="rotate-text">MODO PAISAGEM REQUERIDO</div>
                <div class="rotate-sub">Para acessar a Calculadora Tática, por favor gire seu dispositivo.</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<div class='display-calc'>{st.session_state.calc_expr if st.session_state.calc_expr else '0'}</div>", unsafe_allow_html=True)
            def k_p(k): st.session_state.calc_expr += str(k)
            def k_c(): st.session_state.calc_expr = ""
            def k_s():
                try: st.session_state.calc_expr = str(eval(st.session_state.calc_expr.replace('×', '*').replace('÷', '/')))
                except: st.session_state.calc_expr = "Error"
            c1, c2, c3, c4 = st.columns(4)
            c1.button("7", key="k7", on_click=k_p, args=("7",))
            c2.button("8", key="k8", on_click=k_p, args=("8",))
            c3.button("9", key="k9", on_click=k_p, args=("9",))
            c4.button("_÷_", key="kdiv", on_click=k_p, args=("/",))
            c1.button("4", key="k4", on_click=k_p, args=("4",))
            c2.button("5", key="k5", on_click=k_p, args=("5",))
            c3.button("6", key="k6", on_click=k_p, args=("6",))
            c4.button("_×_", key="kmul", on_click=k_p, args=("*",))
            c1.button("1", key="k1", on_click=k_p, args=("1",))
            c2.button("2", key="k2", on_click=k_p, args=("2",))
            c3.button("3", key="k3", on_click=k_p, args=("3",))
            c4.button("_-_", key="ksub", on_click=k_p, args=("-",))
            c1.button("0", key="k0", on_click=k_p, args=("0",))
            c2.button(".", key="kdot", on_click=k_p, args=(".",))
            c3.button("C", key="kclr", on_click=k_c)
            c4.button("_+_", key="kadd", on_click=k_p, args=("+",))
            st.button(t('calc_btn'), key="nsolve", type="primary", use_container_width=True, on_click=k_s)

        # --- TAB CÂMBIO ---
        with tabs[4]:
            usd, eur = 5.05, 5.45
            s_u, s_e = saldo_brl / usd, saldo_brl / eur
            st.markdown(f"""
            <div class='obsidian-card'>
                <div class='label-caption'>{t('fx_title')}</div>
                <div class="row-item">
                    <div style="display:flex; align-items:center; gap:12px;"><span style="font-size:1.4rem;">🇺🇸</span><div><div style="font-size:0.9rem; font-weight:600;">{t('fx_usd')}</div><div style="font-size:0.6rem; color:#A1A1AA;">{t('fx_ref')} {usd:,.2f}</div></div></div>
                    <div style="font-family:'JetBrains Mono'; font-weight:700; color:#00E5FF;">$ {s_u:,.2f}</div>
                </div>
                <div class="row-item" style="border:none;">
                    <div style="display:flex; align-items:center; gap:12px;"><span style="font-size:1.4rem;">🇪🇺</span><div><div style="font-size:0.9rem; font-weight:600;">{t('fx_eur')}</div><div style="font-size:0.6rem; color:#A1A1AA;">{t('fx_ref')} {eur:,.2f}</div></div></div>
                    <div style="font-family:'JetBrains Mono'; font-weight:700; color:#00E5FF;">€ {s_e:,.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(t('fx_cap'))

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; color:#4B5563; font-size:0.65rem; margin-top:3rem;'>Banco da Família v11.5 • Criado por RipariTech • 2026</div>", unsafe_allow_html=True)
