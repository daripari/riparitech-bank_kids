import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="RipariBank", page_icon="💰", layout="centered")

# --- DATABASE SETUP ---
DB_FILE = 'kids_bank.db'

def get_connection():
    """Garante uma conexão estável e isolada para cada operação"""
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Tabela de Usuários
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, role TEXT, password TEXT)''')
    # Tabela de Transações
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, 
                  description TEXT, timestamp TEXT, type TEXT)''')
    
    # Lógica de Migração/Inserção de Usuários Iniciais
    c.execute("SELECT COUNT(*) FROM users WHERE name = 'daniel.ripari'")
    if c.fetchone()[0] == 0:
        initial_users = [
            ('daniel.ripari', 'admin', '1234'),
            ('ligia.ripari', 'admin', '1234'),
            ('murilo.ripari', 'user', 'kids1'),
            ('cecilia.ripari', 'user', 'kids2')
        ]
        c.executemany("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", initial_users)
    
    conn.commit()
    conn.close()

# Inicializa o banco na primeira execução
init_db()

# --- FUNÇÕES DE LÓGICA DE NEGÓCIO ---
def get_users_df():
    conn = get_connection()
    df = pd.read_sql("SELECT id, name, role FROM users", conn)
    conn.close()
    return df

def get_balance(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ?", (user_id,))
    res = c.fetchone()[0]
    conn.close()
    return res if res else 0.0

def add_transaction(user_id, amount, description, t_type):
    conn = get_connection()
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_amount = amount if t_type == "Crédito" else -amount
    c.execute("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (?, ?, ?, ?, ?)",
              (user_id, final_amount, description, timestamp, t_type))
    conn.commit()
    conn.close()

# --- FUNÇÕES DE GESTÃO (CALLBACKS) ---
def callback_delete_user(user_id_to_delete):
    """Callback atômico para exclusão"""
    if user_id_to_delete == st.session_state.user_id:
        st.session_state.feedback_msg = ("error", "Você não pode excluir a sua própria conta logada!")
        return

    conn = get_connection()
    c = conn.cursor()
    try:
        # 1. Limpa transações
        c.execute("DELETE FROM transactions WHERE user_id = ?", (user_id_to_delete,))
        # 2. Remove usuário
        c.execute("DELETE FROM users WHERE id = ?", (user_id_to_delete,))
        conn.commit()
        st.session_state.feedback_msg = ("success", "Usuário e histórico removidos definitivamente.")
    except Exception as e:
        st.session_state.feedback_msg = ("error", f"Erro técnico: {str(e)}")
    finally:
        conn.close()

def create_user(name, role, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", (name.lower().strip(), role, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def update_password(user_id, new_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    conn.close()
    return True

# --- INTERFACE ---
st.title("💰 RipariBank")
st.subheader("Controle Financeiro Familiar")

# Inicializa estado de feedback se não existir
if 'feedback_msg' not in st.session_state:
    st.session_state.feedback_msg = None

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Exibe mensagens de feedback pendentes
if st.session_state.feedback_msg:
    tipo, msg = st.session_state.feedback_msg
    if tipo == 'success':
        st.success(msg)
    else:
        st.error(msg)
    st.session_state.feedback_msg = None

if not st.session_state.logged_in:
    with st.container():
        st.write("### 🔐 Acesso ao Sistema")
        user_input = st.text_input("Usuário", placeholder="ex: nome.sobrenome").lower().strip()
        password = st.text_input("Senha", type="password")
        
        if st.button("Entrar", type="primary"):
            conn = get_connection()
            u_data = pd.read_sql(f"SELECT * FROM users WHERE name=? AND password=?", conn, params=(user_input, password))
            conn.close()
            
            if not u_data.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = u_data.iloc[0]['id']
                st.session_state.user_name = u_data.iloc[0]['name']
                st.session_state.role = u_data.iloc[0]['role']
                st.rerun()
            else:
                st.error("Credenciais inválidas.")
else:
    # SIDEBAR
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=80)
    st.sidebar.write(f"Olá, **{st.session_state.user_name}**")
    if st.sidebar.button("Terminar Sessão"):
        st.session_state.logged_in = False
        st.rerun()

    # DASHBOARD GERAL (Visível para todos)
    balance = get_balance(st.session_state.user_id)
    st.metric("Saldo Atual", f"R$ {balance:.2f}")

    st.write("#### 📜 Movimentações Recentes")
    conn = get_connection()
    history = pd.read_sql(f"SELECT timestamp as Data, type as Tipo, description as Motivo, amount as Valor FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", conn, params=(st.session_state.user_id,))
    conn.close()
    
    if not history.empty:
        st.dataframe(history, use_container_width=True, hide_index=True)
    else:
        st.info("Sem histórico disponível.")

    # --- ADMIN PANEL ---
    if st.session_state.role == 'admin':
        st.markdown("---")
        st.write("### ⚙️ Painel de Comando")
        
        # MUDANÇA CRÍTICA: Substituição de Tabs por Radio Button para estabilidade de estado
        admin_mode = st.radio(
            "Selecione a Operação:", 
            ["💸 Lançamentos Financeiros", "👥 Gestão de Usuários"], 
            horizontal=True
        )
        
        st.markdown("---")

        if admin_mode == "💸 Lançamentos Financeiros":
            all_users = get_users_df()
            kids = all_users[all_users['role'] == 'user']
            if not kids.empty:
                target = st.selectbox("Filho(a):", kids['name'], key="sel_k_fin")
                t_id = kids[kids['name'] == target]['id'].values[0]
                
                with st.form("trans_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        v = st.number_input("Valor R$", min_value=0.0, step=1.0)
                        o = st.radio("Operação", ["Crédito", "Débito"], horizontal=True)
                    with c2:
                        m = st.text_input("Motivo")
                        if st.form_submit_button("Efetuar Lançamento", type="primary"):
                            if v > 0 and m:
                                add_transaction(t_id, v, m, o)
                                st.success("Lançamento efetuado!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.warning("Preencha valor e motivo.")
            else:
                st.warning("Nenhum usuário 'filho' cadastrado.")

        elif admin_mode == "👥 Gestão de Usuários":
            users_list = get_users_df()
            
            c_add, c_edit = st.columns(2)
            
            # Coluna 1: Adicionar
            with c_add:
                st.info("➕ Novo Usuário")
                with st.form("new_user_form"):
                    n = st.text_input("Username (ex: nome.sobrenome)")
                    r = st.selectbox("Perfil", ["user", "admin"])
                    p = st.text_input("Senha Inicial", type="password")
                    if st.form_submit_button("Criar"):
                        if n and p:
                            if create_user(n, r, p):
                                st.success("Usuário Criado!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Erro ao criar.")

            # Coluna 2: Editar / Excluir
            with c_edit:
                st.warning("🔧 Editar / Excluir")
                if not users_list.empty:
                    # Selectbox com chave fixa para evitar resets
                    target_edit_name = st.selectbox("Selecionar Usuário:", users_list['name'].unique(), key="user_select_edit")
                    
                    # Recupera ID
                    u_id_to_edit = users_list[users_list['name'] == target_edit_name]['id'].values[0]
                    
                    # Alterar Senha
                    new_p = st.text_input("Nova Senha", type="password", key="new_pwd_input")
                    if st.button("Atualizar Senha", key="btn_upd_pwd"):
                        if new_p:
                            update_password(u_id_to_edit, new_p)
                            st.success("Senha atualizada!")
                    
                    st.divider()
                    
                    # Excluir com Callback (CRÍTICO)
                    st.write(f"🗑️ Excluir **{target_edit_name}**?")
                    st.button(
                        "Confirmar Exclusão", 
                        type="secondary",
                        on_click=callback_delete_user,
                        args=(u_id_to_edit,)
                    )
                else:
                    st.info("Lista vazia.")

# --- FOOTER ---
st.markdown("---")
st.caption("© 2024 RipariBank | Engine v1.3 (Stable UI)")
