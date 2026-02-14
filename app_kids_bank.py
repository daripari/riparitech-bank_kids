import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="RipariBank", page_icon="💰", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = 'kids_bank.db'

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    # Tabela de Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, role TEXT, password TEXT)''')
    # Tabela de Transações
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, 
                  description TEXT, timestamp TEXT, type TEXT)''')
    
    # Inserir dados iniciais se vazio
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        # Novas credenciais solicitadas por Daniel Ripari
        initial_users = [
            ('daniel.ripari', 'admin', '1234'),
            ('ligia.ripari', 'admin', '1234'),
            ('murilo.ripari', 'user', 'kids1'),
            ('cecilia.ripari', 'user', 'kids2')
        ]
        c.executemany("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", initial_users)
    conn.commit()
    return conn

# Criar conexão global para a sessão
if 'conn' not in st.session_state:
    st.session_state.conn = init_db()

conn = st.session_state.conn

# --- FUNÇÕES DE LÓGICA ---
def get_users():
    return pd.read_sql("SELECT id, name, role FROM users", conn)

def get_balance(user_id):
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ?", (user_id,))
    res = c.fetchone()[0]
    return res if res else 0.0

def add_transaction(user_id, amount, description, t_type):
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_amount = amount if t_type == "Crédito" else -amount
    c.execute("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (?, ?, ?, ?, ?)",
              (user_id, final_amount, description, timestamp, t_type))
    conn.commit()

# --- INTERFACE ---
st.title("💰 RipariBank")
st.subheader("Controle Financeiro Familiar")

# Simulação de Login simples
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container():
        st.write("### 🔐 Acesso ao Sistema")
        user_select = st.selectbox("Quem é você?", get_users()['name'])
        password = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            # Usando parâmetros para evitar SQL Injection (cortesia do Snape)
            u_data = pd.read_sql(f"SELECT * FROM users WHERE name=? AND password=?", conn, params=(user_select, password))
            if not u_data.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = u_data.iloc[0]['id']
                st.session_state.user_name = u_data.iloc[0]['name']
                st.session_state.role = u_data.iloc[0]['role']
                st.success(f"Bem-vindo(a), {st.session_state.user_name}!")
                st.rerun()
            else:
                st.error("Senha incorreta!")
else:
    # Sidebar de Logout e Info
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=100)
    st.sidebar.write(f"Usuário: **{st.session_state.user_name}**")
    st.sidebar.write(f"Perfil: *{st.session_state.role.upper()}*")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD ---
    balance = get_balance(st.session_state.user_id)
    
    col_bal, col_info = st.columns([1, 1])
    with col_bal:
        st.metric("Saldo Disponível", f"R$ {balance:.2f}")
    
    with col_info:
        st.info("Ensino financeiro para a próxima geração Ripari.")

    # --- HISTÓRICO ---
    st.write("#### 📜 Histórico de Lançamentos")
    history = pd.read_sql(f"SELECT timestamp as Data, type as Tipo, description as Motivo, amount as Valor FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", conn, params=(st.session_state.user_id,))
    
    if not history.empty:
        st.dataframe(history, use_container_width=True, hide_index=True)
    else:
        st.write("Nenhum lançamento registrado nesta conta.")

    # --- VISÃO DOS PAIS (ADMIN) ---
    if st.session_state.role == 'admin':
        st.markdown("---")
        st.write("### 🛠️ Gestão de Saldos (Painel Administrativo)")
        
        # Filtra apenas os filhos para o selectbox
        users_df = get_users()
        kids_only = users_df[users_df['role'] == 'user']
        
        target_user = st.selectbox("Escolher conta do filho:", kids_only['name'])
        target_id = kids_only[kids_only['name'] == target_user]['id'].values[0]
        
        with st.expander(f"Realizar Lançamento para {target_user}"):
            c1, c2 = st.columns(2)
            with c1:
                val = st.number_input("Valor R$", min_value=0.0, step=1.0)
                op = st.radio("Tipo de Lançamento", ["Crédito", "Débito"])
            with c2:
                motivo = st.text_input("Descrição", placeholder="Ex: Lavou a louça, Presente...")
                confirmar = st.button("Executar Transação", type="primary")
            
            if confirmar:
                if val > 0 and motivo:
                    add_transaction(target_id, val, motivo, op)
                    st.success(f"Sucesso! R$ {val} ({op}) registrado para {target_user}.")
                    st.rerun()
                else:
                    st.warning("Preencha o valor e o motivo.")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2024 RipariBank | Gestão Estratégica Familiar")
