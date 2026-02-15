# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO DE TEMA ---
st.set_page_config(page_title="RipariBank Obsidian", page_icon="💎", layout="centered")

# --- 2. DICIONÁRIO DE TRADUÇÃO (i18n) ---
TRANSLATIONS = {
    'pt': {
        'protocol': 'Modern Obsidian v9.0',
        'user': 'Usuário',
        'password': 'Senha',
        'auth_btn': 'AUTENTICAR',
        'login_err': 'Acesso Negado.',
        'bal_family': 'Monitoramento de Ativos',
        'quick_tr': '💸 LANÇAMENTO TÁTICO',
        'target_acc': 'Conta Destino:',
        'amount': 'Montante (R$)',
        'op': 'Operação',
        'op_dep': 'Depósito',
        'op_ret': 'Retirada',
        'reason': 'Motivo',
        'exec': 'EXECUTAR',
        'tr_success': 'Transação Confirmada.',
        'user_mgmt': '⚙️ COMANDO DE USUÁRIOS',
        'tab_list': 'Listagem',
        'tab_add': 'Novo Registro',
        'lvl': 'Nível',
        'create_acc': 'CADASTRAR',
        'bal_acc': 'Saldo em Conta',
        'enc_conn': '● CONEXÃO SEGURA',
        'tab_hist': '📊 Histórico',
        'tab_evo': '📈 Evolução',
        'tab_calc': '🧮 Calculadora',
        'tab_fx': '🌍 Câmbio',
        'no_reg': 'Sem registros no momento.',
        'calc_btn': 'CALCULAR',
        'fx_title': 'Conversão Internacional',
        'fx_usd': 'Dólar Americano',
        'fx_eur': 'Euro',
        'fx_ref': 'Ref: R$',
        'fx_cap': 'Taxas de câmbio referenciais.',
        'logout': 'Sair',
        'refresh': 'Atualizar',
        'welcome': 'Olá'
    },
    'en': {
        'protocol': 'Modern Obsidian v9.0',
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
        'tab_list': 'List',
        'tab_add': 'New Registry',
        'lvl': 'Level',
        'create_acc': 'REGISTER',
        'bal_acc': 'Account Balance',
        'enc_conn': '● SECURE CONNECTION',
        'tab_hist': '📊 History',
        'tab_evo': '📈 Analysis',
        'tab_calc': '🧮 Calculator',
        'tab_fx': '🌍 Exchange',
        'no_reg': 'No records found.',
        'calc_btn': 'CALCULATE',
        'fx_title': 'International Conversion',
        'fx_usd': 'US Dollar',
        'fx_eur': 'Euro',
        'fx_ref': 'Ref: BRL',
        'fx_cap': 'Exchange rates based on market reference.',
        'logout': 'Logout',
        'refresh': 'Refresh',
        'welcome': 'Hello'
    },
    'es': {
        'protocol': 'Modern Obsidian v9.0',
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
        'tab_list': 'Listado',
        'tab_add': 'Nuevo Registro',
        'lvl': 'Nivel',
        'create_acc': 'REGISTRAR',
        'bal_acc': 'Saldo en Cuenta',
        'enc_conn': '● CONEXIÓN SEGURA',
        'tab_hist': '📊 Historial',
        'tab_evo': '📈 Evolución',
        'tab_calc': '🧮 Calculadora',
        'tab_fx': '🌍 Cambio',
        'no_reg': 'Sin registros por ahora.',
        'calc_btn': 'CALCULAR',
        'fx_title': 'Conversión Internacional',
        'fx_usd': 'Dólar Americano',
        'fx_eur': 'Euro',
        'fx_ref': 'Ref: R$',
        'fx_cap': 'Tasas de cambio basadas en referencias.',
        'logout': 'Salir',
        'refresh': 'Actualizar',
        'welcome': 'Hola'
    }
}

def t(key):
    lang = st.session_state.get('lang', 'pt')
    return TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, key)

# --- CSS MODERN OBSIDIAN UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0A0A0B;
        color: #F0F0F0;
    }
    
    .stApp { background-color: #0A0A0B; }
    
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding-top: 2rem !important; max-width: 480px !important; }

    /* Header e Logo */
    .obsidian-logo {
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #00E5FF;
        background: linear-gradient(135deg, #00E5FF 0%, #007BFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    
    /* Obsidian Cards com profundidade */
    .obsidian-card {
        background: linear-gradient(165deg, #1A1A1D 0%, #111113 100%);
        border: 1px solid #2D2D32;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
    }

    .row-item {
        border-bottom: 1px solid #222225;
        padding: 12px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .label-caption {
        color: #8E8E93;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .value-main {
        font-size: 2.4rem;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -2px;
    }

    /* Botões Otimizados */
    .stButton>button {
        border-radius: 10px !important;
        background-color: #1A1A1D !important;
        color: #FFFFFF !important;
        border: 1px solid #333338 !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        height: 52px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #00E5FF 0%, #007BFF 100%) !important;
        border-color: transparent !important;
        color: #000000 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 229, 255, 0.3);
    }

    /* Botão Primário e Formulários */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #00E5FF 0%, #007BFF 100%) !important;
        color: #000000 !important;
        border: none !important;
    }

    /* Calculadora Estilo Teclado */
    .display-calc {
        background-color: #050505;
        border: 2px solid #2D2D32;
        border-radius: 12px;
        padding: 20px;
        text-align: right;
        font-size: 2.2rem;
        font-family: 'JetBrains Mono', monospace;
        color: #00E5FF;
        margin-bottom: 15px;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        box-shadow: inset 0 2px 10px rgba(0,0,0,0.8);
    }

    /* Estilo de Abas Obsidian */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 2px solid #2D2D32; gap: 10px; }
    .stTabs [data-baseweb="tab"] { color: #8E8E93; font-weight: 700; background: transparent; }
    .stTabs [aria-selected="true"] { color: #00E5FF !important; border-bottom-color: #00E5FF !important; }

    /* Inputs Modernos */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #0F0F11 !important;
        border: 1px solid #333338 !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }

    hr { border: 0; border-top: 1px solid #2D2D32; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE DADOS ---
@st.cache_resource
def get_connection():
    return st.connection("supabase", type="sql")

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
    run_query('''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, role TEXT, password TEXT, language TEXT DEFAULT 'pt');''', commit=True)
    run_query('''CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, user_id INTEGER, amount REAL, description TEXT, timestamp TIMESTAMP, type TEXT);''', commit=True)
    try: run_query("ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'pt';", commit=True)
    except: pass

init_db()

@st.cache_data(ttl=600)
def get_cached_balance(uid):
    res = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': uid})
    return res.iloc[0]['total'] if res is not None and not res.empty and pd.notnull(res.iloc[0]['total']) else 0.0

@st.cache_data(ttl=600)
def get_cached_family_balances():
    query = """
        SELECT u.name, COALESCE(SUM(t.amount), 0) as balance 
        FROM users u 
        LEFT JOIN transactions t ON u.id = t.user_id 
        WHERE u.role = 'user' 
        GROUP BY u.name, u.id ORDER BY u.name
    """
    return run_query(query)

@st.cache_data(ttl=600)
def get_cached_history(uid):
    return run_query("SELECT timestamp as data, description as motivo, amount as valor FROM transactions WHERE user_id=:uid ORDER BY id DESC LIMIT 15", params={'uid': uid})

# --- 4. ESTADO ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'calc_expr' not in st.session_state: st.session_state.calc_expr = ""
if 'lang' not in st.session_state: st.session_state.lang = 'pt'

# --- 5. LOGIN ---
if not st.session_state.logged_in:
    st.markdown(f"<div style='margin-top:5rem; text-align:center;'><h1 class='obsidian-logo'>💎 RipariBank</h1><p style='color:#636366; font-weight:600;'>{t('protocol')}</p></div>", unsafe_allow_html=True)
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
            else: st.toast(t('login_err'))

# --- 6. DASHBOARD ---
else:
    # --- NAVBAR ---
    h_col1, h_col2, h_col3, h_col4 = st.columns([1.8, 0.6, 0.3, 0.3])
    with h_col1:
        st.markdown("<div class='obsidian-logo'>💎 RipariBank</div>", unsafe_allow_html=True)
    
    with h_col2:
        options = {'🇧🇷 PT': 'pt', '🇺🇸 EN': 'en', '🇪🇸 ES': 'es'}
        current_idx = list(options.values()).index(st.session_state.lang)
        new_lang_label = st.selectbox("", options.keys(), index=current_idx, label_visibility="collapsed")
        new_lang_code = options[new_lang_label]
        if new_lang_code != st.session_state.lang:
            st.session_state.lang = new_lang_code
            run_query("UPDATE users SET language=:l WHERE id=:id", params={'l': new_lang_code, 'id': st.session_state.user_id}, commit=True)
            st.rerun()

    with h_col3:
        if st.button("🔄", key="ref", help=t('refresh')):
            st.cache_data.clear(); st.rerun()
    with h_col4:
        if st.button("🚪", key="out", help=t('logout')):
            st.session_state.logged_in = False; st.cache_data.clear(); st.rerun()

    if st.session_state.role == 'admin':
        st.markdown("<div class='obsidian-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='label-caption'>{t('bal_family')}</div>", unsafe_allow_html=True)
        df_saldos = get_cached_family_balances()
        if df_saldos is not None and not df_saldos.empty:
            for _, row in df_saldos.iterrows():
                st.markdown(f"""
                <div class='row-item'>
                    <span style='font-weight:600; font-size:1.1rem;'>{row['name'].title()}</span>
                    <span style='color:#00E5FF; font-family:monospace; font-weight:700;'>R$ {row['balance']:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
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
                            st.success(t('tr_success')); time.sleep(1); st.rerun()

        with st.expander(t('user_mgmt')):
            t_l, t_a = st.tabs([t('tab_list'), t('tab_add')])
            with t_l:
                all_u = run_query("SELECT id, name, role, language FROM users ORDER BY name")
                st.dataframe(all_u, use_container_width=True, hide_index=True)
            with t_a:
                with st.form("add_user_form"):
                    nn = st.text_input(t('user')).lower().strip()
                    np = st.text_input(t('password'))
                    nr = st.selectbox(t('lvl'), ["user", "admin"])
                    if st.form_submit_button(t('create_acc')):
                        run_query("INSERT INTO users (name, role, password, language) VALUES (:n, :r, :p, 'pt')", params={'n': nn, 'r': nr, 'p': np}, commit=True)
                        st.rerun()

    else:
        saldo_brl = get_cached_balance(st.session_state.user_id)
        st.markdown(f"""
        <div class="obsidian-card">
            <div class="label-caption">{t('bal_acc')} | {st.session_state.user_name.upper()}</div>
            <div class="value-main">R$ {saldo_brl:,.2f}</div>
            <div style="margin-top:10px; font-size:0.65rem; color:#00E5FF; font-weight:700;">{t('enc_conn')}</div>
        </div>
        """, unsafe_allow_html=True)

        tabs = st.tabs([t('tab_hist'), t('tab_evo'), t('tab_calc'), t('tab_fx')])
        
        with tabs[0]:
            df_h = get_cached_history(st.session_state.user_id)
            if df_h is not None and not df_h.empty: st.dataframe(df_h, use_container_width=True, hide_index=True)
            else: st.info(t('no_reg'))
        
        with tabs[1]:
            if df_h is not None and not df_h.empty: st.area_chart(df_h.set_index('data')['valor'], color="#00E5FF")
        
        with tabs[2]:
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

        with tabs[3]:
            usd, eur = 5.05, 5.45
            s_u, s_e = saldo_brl / usd, saldo_brl / eur
            st.markdown(f"""
            <div class='obsidian-card'>
                <div class='label-caption'>{t('fx_title')}</div>
                <div class="row-item">
                    <div style="display:flex; align-items:center; gap:12px;"><span style="font-size:1.6rem;">🇺🇸</span><div><div style="font-weight:600;">{t('fx_usd')}</div><div style="font-size:0.6rem; color:#636366;">{t('fx_ref')} {usd:,.2f}</div></div></div>
                    <div style="font-family:'JetBrains Mono'; font-weight:700; color:#00E5FF;">$ {s_u:,.2f}</div>
                </div>
                <div class="row-item" style="border:none;">
                    <div style="display:flex; align-items:center; gap:12px;"><span style="font-size:1.6rem;">🇪🇺</span><div><div style="font-weight:600;">{t('fx_eur')}</div><div style="font-size:0.6rem; color:#636366;">{t('fx_ref')} {eur:,.2f}</div></div></div>
                    <div style="font-family:'JetBrains Mono'; font-weight:700; color:#00E5FF;">€ {s_e:,.2f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.caption(t('fx_cap'))

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; color:#2D2D32; font-size:0.65rem; margin-top:4rem;'>RIPARIBANK OBSIDIAN v9.0 • 2024</div>", unsafe_allow_html=True)
