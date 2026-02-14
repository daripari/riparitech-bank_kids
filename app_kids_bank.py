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
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, role TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, 
                  description TEXT, timestamp TEXT, type TEXT)''')
    
    # Verifica existência do admin principal
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

# Inicializa o banco
init_db()

# --- FUNÇÕES DE NEGÓCIO ---
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

# --- FUNÇÕES ADMIN (CORE) ---

def create_user_logic(name, role, password):
    conn = get_connection()
    c = conn.cursor()
    try:
        # Verifica duplicidade
        c.execute("SELECT count(*) FROM users WHERE name = ?", (name,))
        if c.fetchone()[0] > 0:
            return False, "Usuário já existe!"
        
        c.execute("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", (name.lower().strip(), role, password))
        conn.commit()
        return True, "Usuário criado com sucesso!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_password_logic(user_id, new_password):
    if not new_password:
        return False, "A senha não pode ser vazia."
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
        conn.commit()
        return True, "Senha atualizada com sucesso!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Callback de Exclusão (Mantido pois funciona bem para botões fora de form)
def callback_delete_user(user_id_to_delete):
    if user_id_to_delete == st.session_state.user_id:
        st.session_state.feedback = ("error", "Você não pode se auto-excluir!")
        return

    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM transactions WHERE user_id = ?", (user_id_to_delete,))
        c.execute("DELETE FROM users WHERE id = ?", (user_id_to_delete,))
        conn.commit()
        st.session_state.feedback = ("success", "Usuário deletado.")
    except Exception as e:
        st.session_state.feedback = ("error", str(e))
    finally:
        conn.close()

# --- INTERFACE ---
st.title("💰 RipariBank")

# Gestão de Estado de Feedback
if 'feedback' not in st.session_state:
    st.session_state.feedback = None

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Renderiza Feedback Global
feedback_placeholder = st.empty()
if st.session_state.feedback:
    tipo, msg = st.session_state.feedback
    if tipo == 'success':
        feedback_placeholder.success(msg)
    else:
        feedback_placeholder.error(msg)
    st.session_state.feedback = None # Limpa após exibir

# --- TELA DE LOGIN ---
if not st.session_state.logged_in:
    with st.container():
        st.write("### 🔐 Login")
        with st.form("login_form"):
            user_input = st.text_input("Usuário", placeholder="ex: daniel.ripari").lower().strip()
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
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
                    st.error("Dados inválidos.")

# --- TELA PRINCIPAL ---
else:
    # Sidebar
    st.sidebar.write(f"Olá, **{st.session_state.user_name}**")
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()

    # Dashboard Geral
    balance = get_balance(st.session_state.user_id)
    st.metric("Saldo", f"R$ {balance:.2f}")

    st.write("#### 📜 Extrato")
    conn = get_connection()
    history = pd.read_sql(f"SELECT timestamp as Data, type as Tipo, description as Motivo, amount as Valor FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", conn, params=(st.session_state.user_id,))
    conn.close()
    
    if not history.empty:
        st.dataframe(history, use_container_width=True, hide_index=True)
    else:
        st.caption("Sem histórico.")

    # --- ÁREA ADMIN ---
    if st.session_state.role == 'admin':
        st.markdown("---")
        st.subheader("⚙️ Painel Admin")
        
        mode = st.radio("Opção:", ["💸 Lançamentos", "👥 Gestão de Usuários"], horizontal=True)
        
        # MODO 1: LANÇAMENTOS
        if mode == "💸 Lançamentos":
            all_users = get_users_df()
            kids = all_users[all_users['role'] == 'user']
            
            if not kids.empty:
                # Selectbox fora do form para atualizar a UI se mudar o filho
                target_name = st.selectbox("Selecione o Filho(a):", kids['name'])
                target_id = kids[kids['name'] == target_name]['id'].values[0]
                
                # Form blinda a entrada de dados
                with st.form("transaction_form"):
                    st.write(f"Lançando para: **{target_name}**")
                    c1, c2 = st.columns(2)
                    with c1:
                        val = st.number_input("Valor R$", min_value=0.0, step=1.0)
                        op = st.radio("Tipo", ["Crédito", "Débito"])
                    with c2:
                        desc = st.text_input("Motivo")
                    
                    if st.form_submit_button("Confirmar Lançamento"):
                        if val > 0 and desc:
                            add_transaction(target_id, val, desc, op)
                            st.session_state.feedback = ("success", "Lançamento realizado!")
                            st.rerun()
                        else:
                            st.warning("Preencha todos os campos.")
            else:
                st.info("Cadastre filhos primeiro.")

        # MODO 2: GESTÃO DE USUÁRIOS
        elif mode == "👥 Gestão de Usuários":
            users = get_users_df()
            
            col_a, col_b = st.columns(2)
            
            # COLUNA A: CRIAR
            with col_a:
                st.info("Novo Usuário")
                with st.form("create_user_form"):
                    new_n = st.text_input("Nome (ex: joao.ripari)")
                    new_r = st.selectbox("Perfil", ["user", "admin"])
                    new_p = st.text_input("Senha")
                    
                    if st.form_submit_button("Criar Usuário"):
                        if new_n and new_p:
                            suc, msg = create_user_logic(new_n, new_r, new_p)
                            if suc:
                                st.session_state.feedback = ("success", msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.warning("Preencha tudo.")

            # COLUNA B: EDITAR / EXCLUIR
            with col_b:
                st.warning("Editar / Excluir")
                if not users.empty:
                    edit_name = st.selectbox("Selecione:", users['name'].unique())
                    edit_id = users[users['name'] == edit_name]['id'].values[0]
                    
                    # FORMULÁRIO DE SENHA (A solução do problema 2)
                    # A chave do form inclui o ID para garantir unicidade
                    with st.form(key=f"pwd_form_{edit_id}"):
                        st.write(f"Alterar senha de **{edit_name}**")
                        new_pwd_val = st.text_input("Nova Senha", type="password")
                        if st.form_submit_button("Salvar Nova Senha"):
                            suc, msg = update_password_logic(edit_id, new_pwd_val)
                            if suc:
                                st.session_state.feedback = ("success", msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    
                    st.divider()
                    st.write(f"Excluir **{edit_name}**?")
                    # Botão de exclusão (Mantém on_click pois é atômico)
                    st.button(
                        "Confirmar Exclusão", 
                        type="primary", 
                        key=f"del_btn_{edit_id}",
                        on_click=callback_delete_user,
                        args=(edit_id,)
                    )

# --- FOOTER ---
st.markdown("---")
st.caption("© 2024 RipariBank | System v2.0 (Forms Secured)")
