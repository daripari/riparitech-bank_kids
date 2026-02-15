# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import text
import time

# --- 1. CONFIGURAÇÃO DE TEMA ---
st.set_page_config(page_title="RipariBank Stealth", page_icon="💎", layout="centered")

# --- 2. DICIONÁRIO DE TRADUÇÃO (i18n) ---
TRANSLATIONS = {
    'pt': {
        'protocol': 'Protocolo de Segurança v8.5',
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
        'enc_conn': '● CONEXÃO CRIPTOGRAFADA',
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
        'fx_cap': 'Taxas de câmbio baseadas em valores de referência.',
        'logout': 'Sair',
        'refresh': 'Atualizar',
        'welcome': 'Olá'
    },
    'en': {
        'protocol': 'Security Protocol v8.5',
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
        'enc_conn': '● ENCRYPTED CONNECTION',
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
        'protocol': 'Protocolo de Seguridad v8.5',
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
        'enc_conn': '● CONEXIÓN CIFRADA',
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
        'fx_cap': 'Tasas de cambio basadas en referencias de mercado.',
        'logout': 'Salir',
        'refresh': 'Actualizar',
        'welcome': 'Hola'
    }
}

def t(key):
    lang = st.session_state.get('lang', 'pt')
    return TRANSLATIONS.get(lang, TRANSLATIONS['pt']).get(key, key)

# --- CSS STEALTH GRAPHITE UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #080808;
        color: #FFFFFF;
    }
    
    .stApp { background-color: #080808; }
    
    #MainMenu, footer, header { visibility: hidden !important; }
    .block-container { padding-top: 2rem !important; max-width: 450px !important; }

    .stealth-logo {
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        color: #3B82F6;
        text-transform: uppercase;
    }
    
    .stealth-card {
        background-color: #121214;
        border: 1px solid #222224;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.6);
    }

    .currency-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #1A1A1C;
    }
    
    .admin-row {
        background-color: #121214;
        border-bottom: 1px solid #1A1A1C;
        padding: 12px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .label-minor {
        color: #636366;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .val-major {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
    }

    .stButton>button {
        border-radius: 8px !important;
        background-color: #1C1C1E !important;
        color: #FFFFFF !important;
        border: 1px solid #2C2C2E !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        height: 50px !important;
        transition: 0.1s;
    }
    
    .stButton>button:hover {
        background-color: #3B82F6 !important;
        border-color: #3B82F6 !important;
    }

    div[data-testid="stFormSubmitButton"] button {
        background-color: #3B82F6 !important;
        border: none !important;
    }

    .calc-box {
        background-color: #000000;
        border: 2px solid #1C1C1E;
        border-radius: 8px;
        padding: 15px;
        text-align: right;
        font-size: 2rem;
        font-family: 'JetBrains Mono', monospace;
        color: #3B82F6;
        margin-bottom: 15px;
        min-height: 70px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
    }

    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 1px solid #1C1C1E; }
    .stTabs [data-baseweb="tab"] { color: #636366; font-size: 0.8rem; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #3B82F6 !important; }

    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #121214 !important;
        border: 1px solid #2C2C2E !important;
        border-radius: 8px !important;
    }

    hr { border: 0; border-top: 1px solid #1C1C1E; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE DADOS ---
@st.cache_resource
def get_connection():
    return st.connection("supabase", type="sql")

conn = get_connection()

def run_query(query_str, params=None, commit=False):
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
    # Criação de Tabelas e Injeção de Colunas i18n
    run_query('''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, role TEXT, password TEXT);''', commit=True)
    run_query('''CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, user_id INTEGER, amount REAL, description TEXT, timestamp TIMESTAMP, type TEXT);''', commit=True)
    try:
        run_query("ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'pt';", commit=True)
    except:
        pass

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
    st.markdown(f"<div style='margin-top:4rem; text-align:center;'><h1 class='stealth-logo'>💎 RipariBank</h1><p style='color:#444;'>Security Protocol v8.5</p></div>", unsafe_allow_html=True)
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
    # --- HEADER ---
    h_col1, h_col2, h_col3, h_col4 = st.columns([2, 0.5, 0.4, 0.4])
    with h_col1:
        st.markdown("<div class='stealth-logo'>💎 RipariBank</div>", unsafe_allow_html=True)
    
    with h_col2:
        # Seletor de Idioma Persistente
        options = {'🇧🇷 PT': 'pt', '🇺🇸 EN': 'en', '🇪🇸 ES': 'es'}
        inv_options = {v: k for k, v in options.items()}
        current_idx = list(options.values()).index(st.session_state.lang)
        
        new_lang_label = st.selectbox("", options.keys(), index=current_idx, label_visibility="collapsed")
        new_lang_code = options[new_lang_label]
        
        if new_lang_code != st.session_state.lang:
            st.session_state.lang = new_lang_code
            run_query("UPDATE users SET language=:l WHERE id=:id", params={'l': new_lang_code, 'id': st.session_state.user_id}, commit=True)
            st.rerun()

    with h_col3:
        if st.button("🔄", key="ref", help=t('refresh')):
            st.cache_data.clear()
            st.rerun()
    with h_col4:
        if st.button("🚪", key="out", help=t('logout')):
            st.session_state.logged_in = False
            st.cache_data.clear()
            st.rerun()

    if st.session_state.role == 'admin':
        st.markdown("<div class='stealth-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='label-minor'>{t('bal_family')}</div>", unsafe_allow_html=True)
        df_saldos = get_cached_family_balances()
        if df_saldos is not None and not df_saldos.empty:
            for _, row in df_saldos.iterrows():
                st.markdown(f"""
                <div class='admin-row'>
                    <span style='font-weight:600;'>{row['name'].title()}</span>
                    <span style='color:#3B82F6; font-family:monospace; font-weight:700;'>R$ {row['balance']:,.2f}</span>
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
                            db_type = 'Depósito' if tipo == t('op_dep') else 'Retirada'
                            final_val = val if db_type == 'Depósito' else -val
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:uid, :amt, :desc, :ts, :t)", 
                                      params={'uid': int(u_target_id), 'amt': final_val, 'desc': desc, 'ts': datetime.now(), 't': db_type}, commit=True)
                            st.success(t('tr_success'))
                            time.sleep(1); st.rerun()

        with st.expander(t('user_mgmt')):
            tab_list, tab_add = st.tabs([t('tab_list'), t('tab_add')])
            with tab_list:
                all_u = run_query("SELECT id, name, role, language FROM users ORDER BY name")
                st.dataframe(all_u, use_container_width=True, hide_index=True)
            with tab_add:
                with st.form("add_user_form"):
                    nn = st.text_input(t('user')).lower().strip()
                    np = st.text_input(t('password'))
                    nr = st.selectbox(t('lvl'), ["user", "admin"])
                    if st.form_submit_button(t('create_acc')):
                        run_query("INSERT INTO users (name, role, password, language) VALUES (:n, :r, :p, 'pt')", params={'n': nn, 'r': nr, 'p': np}, commit=True)
                        st.rerun()

    else:
        # --- VISÃO DO USUÁRIO ---
        saldo_brl = get_cached_balance(st.session_state.user_id)
        
        st.markdown(f"""
        <div class="stealth-card">
            <div class="label-minor">{t('bal_acc')} | {st.session_state.user_name.upper()}</div>
            <div class="val-major">R$ {saldo_brl:,.2f}</div>
            <div style="margin-top:10px; font-size:0.6rem; color:#3B82F6;">{t('enc_conn')}</div>
        </div>
        """, unsafe_allow_html=True)

        tabs = st.tabs([t('tab_hist'), t('tab_evo'), t('tab_calc'), t('tab_fx')])
        
        with tabs[0]:
            df_hist = get_cached_history(st.session_state.user_id)
            if df_hist is not None and not df_hist.empty:
                st.dataframe(df_hist, use_container_width=True, hide_index=True)
            else: st.info(t('no_reg'))
        
        with tabs[1]:
            if df_hist is not None and not df_hist.empty:
                st.area_chart(df_hist.set_index('data')['valor'], color="#3B82F6")
        
        with tabs[2]:
            st.markdown(f"<div class='calc-box'>{st.session_state.calc_expr if st.session_state.calc_expr else '0'}</div>", unsafe_allow_html=True)
            
            def k_press(k): st.session_state.calc_expr += str(k)
            def k_clr(): st.session_state.calc_expr = ""
            def k_solve():
                try: st.session_state.calc_expr = str(eval(st.session_state.calc_expr.replace('×', '*').replace('÷', '/')))
                except: st.session_state.calc_expr = "Erro"

            c1, c2, c3, c4 = st.columns(4)
            c1.button("7", key="n7", on_click=k_press, args=("7",))
            c2.button("8", key="n8", on_click=k_press, args=("8",))
            c3.button("9", key="n9", on_click=k_press, args=("9",))
            c4.button("_÷_", key="ndiv", on_click=k_press, args=("/",))

            c1.button("4", key="n4", on_click=k_press, args=("4",))
            c2.button("5", key="n5", on_click=k_press, args=("5",))
            c3.button("6", key="n6", on_click=k_press, args=("6",))
            c4.button("_×_", key="nmul", on_click=k_press, args=("*",))

            c1.button("1", key="n1", on_click=k_press, args=("1",))
            c2.button("2", key="n2", on_click=k_press, args=("2",))
            c3.button("3", key="n3", on_click=k_press, args=("3",))
            c4.button("_-_", key="nsub", on_click=k_press, args=("-",))

            c1.button("0", key="n0", on_click=k_press, args=("0",))
            c2.button(".", key="ndot", on_click=k_press, args=(".",))
            c3.button("C", key="nclr", on_click=k_clr)
            c4.button("_+_", key="nadd", on_click=k_press, args=("+",))

            st.button(t('calc_btn'), key="nsolve", type="primary", use_container_width=True, on_click=k_solve)

        with tabs[3]:
            usd_rate, eur_rate = 5.05, 5.45
            saldo_usd, saldo_eur = saldo_brl / usd_rate, saldo_brl / eur_rate
            
            st.markdown("<div class='stealth-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='label-minor'>{t('fx_title')}</div>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="currency-row">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:1.5rem;">🇺🇸</span>
                    <div>
                        <div style="font-size:0.9rem; font-weight:600;">{t('fx_usd')}</div>
                        <div style="font-size:0.6rem; color:#636366;">{t('fx_ref')} {usd_rate:,.2f}</div>
                    </div>
                </div>
                <div style="font-family:'JetBrains Mono'; font-weight:700; color:#3B82F6;">$ {saldo_usd:,.2f}</div>
            </div>
            
            <div class="currency-row" style="border:none;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:1.5rem;">🇪🇺</span>
                    <div>
                        <div style="font-size:0.9rem; font-weight:600;">{t('fx_eur')}</div>
                        <div style="font-size:0.6rem; color:#636366;">{t('fx_ref')} {eur_rate:,.2f}</div>
                    </div>
                </div>
                <div style="font-family:'JetBrains Mono'; font-weight:700; color:#3B82F6;">€ {saldo_eur:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.caption(t('fx_cap'))

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; color:#1A1A1C; font-size:0.6rem; margin-top:4rem;'>RIPARIBANK STEALTH CORE v8.5</div>", unsafe_allow_html=True)
