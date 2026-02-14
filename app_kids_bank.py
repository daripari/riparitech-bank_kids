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
    return conn

# Criar conexão global para a sessão
if 'conn' not in st.session_state:
    st.session_state.conn = init_db()

conn = st.session_state.conn

# --- FUNÇÕES DE LÓGICA DE NEGÓCIO ---
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

# --- FUNÇÕES DE GESTÃO DE USUÁRIOS (ADMIN ONLY) ---
def create_user(name, role, password):
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", (name.lower().strip(), role, password))
        conn.commit()
        return True
    except Exception as e:
        return False

def delete_user(user_id):
    c = conn.cursor()
    # Impede deletar o usuário logado
    if user_id == st.session_state.user_id:
        return False, "Você não pode excluir a si próprio!"
    
    try:
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        c.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,)) # Limpa histórico
        conn.commit()
        return True, "Usuário removido com sucesso."
    except Exception as e:
        return False, f"Erro ao deletar: {str(e)}"

def update_password(user_id, new_password):
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    return True

# --- INTERFACE ---
st.title("💰 RipariBank")
st.subheader("Controle Financeiro Familiar")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container():
        st.write("### 🔐 Acesso ao Sistema")
        user_input = st.text_input("Usuário", placeholder="ex: nome.sobrenome").lower().strip()
        password = st.text_input("Senha", type="password")
        
        if st.button("Entrar", type="primary"):
            u_data = pd.read_sql(f"SELECT * FROM users WHERE name=? AND password=?", conn, params=(user_input, password))
            if not u_data.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = u_data.iloc[0]['id']
                st.session_state.user_name = u_data.iloc[0]['name']
                st.session_state.role = u_data.iloc[0]['role']
                st.success(f"Bem-vindo(a), {st.session_state.user_name}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
else:
    # SIDEBAR
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=80)
    st.sidebar.write(f"Usuário: **{st.session_state.user_name}**")
    st.sidebar.write(f"Perfil: *{st.session_state.role.upper()}*")
    
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()

    # --- DASHBOARD DO USUÁRIO ---
    balance = get_balance(st.session_state.user_id)
    st.metric("Saldo Disponível", f"R$ {balance:.2f}")

    st.write("#### 📜 Histórico de Lançamentos")
    history = pd.read_sql(f"SELECT timestamp as Data, type as Tipo, description as Motivo, amount as Valor FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", conn, params=(st.session_state.user_id,))
    
    if not history.empty:
        st.dataframe(history, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lançamento nesta conta.")

    # --- ÁREA ADMINISTRATIVA ---
    if st.session_state.role == 'admin':
        st.markdown("---")
        st.write("### ⚙️ Painel de Administração")
        
        tab_finance, tab_users = st.tabs(["💰 Gestão Financeira", "👤 Gestão de Usuários"])
        
        # --- TAB: GESTÃO FINANCEIRA ---
        with tab_finance:
            users_df = get_users()
            kids_only = users_df[users_df['role'] == 'user']
            
            if not kids_only.empty:
                target_user = st.selectbox("Escolher conta para lançar:", kids_only['name'], key="select_kid_trans")
                target_id = kids_only[kids_only['name'] == target_user]['id'].values[0]
                
                with st.expander(f"Lançamento Rápido: {target_user}", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        val = st.number_input("Valor R$", min_value=0.0, step=1.0, key="val_trans")
                        op = st.radio("Tipo", ["Crédito", "Débito"], key="op_trans")
                    with c2:
                        motivo = st.text_input("Descrição", placeholder="Ex: Tarefas", key="motivo_trans")
                        if st.button("Confirmar Lançamento", type="primary", key="btn_confirm_trans"):
                            if val > 0 and motivo:
                                add_transaction(target_id, val, motivo, op)
                                st.success("Transação concluída!")
                                st.rerun()
            else:
                st.warning("Nenhum usuário do tipo 'filho' cadastrado.")

        # --- TAB: GESTÃO DE USUÁRIOS ---
        with tab_users:
            all_users = get_users()
            st.write("#### Usuários Cadastrados")
            st.dataframe(all_users[['name', 'role']], use_container_width=True, hide_index=True)
            
            col_add, col_edit = st.columns(2)
            
            # Incluir Usuário
            with col_add:
                with st.expander("➕ Incluir Novo Usuário"):
                    new_name = st.text_input("Nome de Usuário", key="new_user_name")
                    new_role = st.selectbox("Perfil", ["user", "admin"], key="new_user_role")
                    new_pwd = st.text_input("Senha Inicial", type="password", key="new_user_pwd")
                    if st.button("Salvar Novo Usuário", key="btn_save_user"):
                        if new_name and new_pwd:
                            if create_user(new_name, new_role, new_pwd):
                                st.success("Usuário criado!")
                                st.rerun()
                            else:
                                st.error("Erro ao criar usuário.")
                        else:
                            st.warning("Preencha todos os campos.")

            # Alterar Senha / Excluir
            with col_edit:
                with st.expander("🔧 Alterar ou Excluir"):
                    edit_user = st.selectbox("Selecionar Usuário", all_users['name'], key="select_user_edit")
                    edit_id = all_users[all_users['name'] == edit_user]['id'].values[0]
                    
                    new_pwd_edit = st.text_input("Nova Senha", type="password", key="new_pwd_edit_val")
                    
                    if st.button("Alterar Senha", key="btn_update_pwd"):
                        if new_pwd_edit:
                            update_password(edit_id, new_pwd_edit)
                            st.success("Senha alterada com sucesso!")
                        else:
                            st.warning("Digite a nova senha.")
                    
                    st.markdown("---")
                    st.write("⚠️ **Zona de Perigo**")
                    confirm_delete = st.checkbox(f"Confirmo que desejo excluir {edit_user}", key="chk_confirm_del")
                    
                    if st.button("🗑️ Excluir Usuário", type="secondary", key="btn_delete_user", disabled=not confirm_delete):
                        success, msg = delete_user(edit_id)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

# --- FOOTER ---
st.markdown("---")
st.caption("© 2024 RipariBank | Módulo de Governança Ativo")
