import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURAÇÃO (Deve ser a primeira linha) ---
st.set_page_config(page_title="RipariBank", page_icon="💰", layout="centered")

# --- 2. BANCO DE DADOS (CONEXÃO DIRETA) ---
DB_FILE = 'kids_bank.db'

def run_query(query, params=(), commit=False):
    """Função única para tocar o banco de dados com segurança."""
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute(query, params)
        if commit:
            conn.commit()
            return True
        else:
            return c.fetchall()
    except Exception as e:
        st.error(f"Erro de Banco de Dados: {e}")
        return None
    finally:
        conn.close()

def init_db():
    # Criação de tabelas
    run_query('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, role TEXT, password TEXT)''', commit=True)
    run_query('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, 
                  description TEXT, timestamp TEXT, type TEXT)''', commit=True)
    
    # Verifica admin inicial
    users = run_query("SELECT count(*) FROM users WHERE name = 'daniel.ripari'")
    if users and users[0][0] == 0:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        initial_users = [
            ('daniel.ripari', 'admin', '1234'),
            ('ligia.ripari', 'admin', '1234'),
            ('murilo.ripari', 'user', 'kids1'),
            ('cecilia.ripari', 'user', 'kids2')
        ]
        c.executemany("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", initial_users)
        conn.commit()
        conn.close()

# Inicializa banco
init_db()

# --- 3. VARIÁVEIS DE SESSÃO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 4. TELA DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown("## 🔐 RipariBank - Acesso")
    with st.form("login_form"):
        user_input = st.text_input("Usuário").lower().strip()
        pass_input = st.text_input("Senha", type="password")
        
        if st.form_submit_button("ENTRAR"):
            res = run_query("SELECT * FROM users WHERE name=? AND password=?", (user_input, pass_input))
            if res:
                # Mapeia colunas pelo índice: 0=id, 1=name, 2=role
                st.session_state.logged_in = True
                st.session_state.user_id = res[0][0]
                st.session_state.user_name = res[0][1]
                st.session_state.role = res[0][2]
                st.rerun()
            else:
                st.error("Acesso Negado.")

# --- 5. SISTEMA PRINCIPAL (LOGADO) ---
else:
    # --- HEADER ---
    c1, c2 = st.columns([3,1])
    c1.markdown(f"### Olá, {st.session_state.user_name}")
    if c2.button("SAIR"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()

    # --- DASHBOARD (Comum a todos) ---
    res_bal = run_query("SELECT SUM(amount) FROM transactions WHERE user_id=?", (st.session_state.user_id,))
    saldo = res_bal[0][0] if res_bal and res_bal[0][0] else 0.0
    st.metric("Meu Saldo", f"R$ {saldo:.2f}")

    with st.expander("Ver Extrato"):
        df_hist = pd.read_sql_query("SELECT timestamp as Data, description as Descrição, amount as Valor, type as Tipo FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", 
                                    sqlite3.connect(DB_FILE), params=(st.session_state.user_id,))
        st.dataframe(df_hist, hide_index=True, use_container_width=True)

    # --- ÁREA DE ADMINISTRAÇÃO (A Lógica "Imperativa") ---
    if st.session_state.role == 'admin':
        st.markdown("---")
        st.subheader("⚙️ Painel de Controle")

        # Seletor de Modo (Radio Button é mais estável que Tabs)
        modo = st.radio("Opção:", ["Lançamentos", "Gestão de Usuários"], horizontal=True)

        # ---------------------------------------------------------
        # MODO 1: LANÇAMENTOS FINANCEIROS
        # ---------------------------------------------------------
        if modo == "Lançamentos":
            # Carrega usuários 'user' (filhos)
            filhos = pd.read_sql_query("SELECT id, name FROM users WHERE role='user'", sqlite3.connect(DB_FILE))
            
            if filhos.empty:
                st.warning("Cadastre usuários do tipo 'user' primeiro.")
            else:
                with st.form("form_lancamento"):
                    target_name = st.selectbox("Conta Destino:", filhos['name'].tolist())
                    c1, c2 = st.columns(2)
                    val = c1.number_input("Valor R$", min_value=0.01, step=1.0)
                    op = c2.radio("Operação", ["Crédito", "Débito"])
                    desc = st.text_input("Motivo")
                    
                    # AÇÃO DIRETA NO SUBMIT
                    if st.form_submit_button("CONFIRMAR LANÇAMENTO"):
                        # Busca ID baseado no nome selecionado
                        target_id = filhos[filhos['name'] == target_name]['id'].values[0]
                        final_val = val if op == "Crédito" else -val
                        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (?, ?, ?, ?, ?)", 
                                  (int(target_id), final_val, desc, ts, op), commit=True)
                        
                        st.success(f"Lançamento para {target_name} realizado!")
                        time.sleep(1)
                        st.rerun()

        # ---------------------------------------------------------
        # MODO 2: GESTÃO DE USUÁRIOS
        # ---------------------------------------------------------
        elif modo == "Gestão de Usuários":
            c_add, c_edit = st.columns(2)

            # --- CRIAR USUÁRIO ---
            with c_add:
                st.info("Novo Usuário")
                with st.form("form_add_user"):
                    new_n = st.text_input("Nome (ex: joao)").lower().strip()
                    new_r = st.selectbox("Perfil", ["user", "admin"])
                    new_p = st.text_input("Senha")
                    
                    if st.form_submit_button("CRIAR"):
                        if new_n and new_p:
                            check = run_query("SELECT * FROM users WHERE name=?", (new_n,))
                            if check:
                                st.error("Usuário já existe!")
                            else:
                                run_query("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", 
                                          (new_n, new_r, new_p), commit=True)
                                st.success(f"Usuário {new_n} criado!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.warning("Preencha todos os campos.")

            # --- EDITAR / EXCLUIR ---
            with c_edit:
                st.warning("Gerenciar Existentes")
                all_users = pd.read_sql_query("SELECT id, name FROM users ORDER BY name", sqlite3.connect(DB_FILE))
                
                # Selectbox fora do form para atualizar dinamicamente
                target_user = st.selectbox("Selecione:", all_users['name'].unique())
                # Pega o ID
                target_uid = all_users[all_users['name'] == target_user]['id'].values[0]

                # FORMULÁRIO DE SENHA (ISOLADO)
                with st.form("form_senha"):
                    st.write(f"Alterar senha de **{target_user}**")
                    new_pass = st.text_input("Nova Senha")
                    if st.form_submit_button("ATUALIZAR SENHA"):
                        if new_pass:
                            run_query("UPDATE users SET password=? WHERE id=?", (new_pass, int(target_uid)), commit=True)
                            st.success("Senha alterada!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Senha vazia.")

                st.markdown("---")
                
                # BOTÃO DE EXCLUSÃO (FORA DE FORMULÁRIO PARA AÇÃO IMEDIATA)
                st.write(f"Zona de Perigo: **{target_user}**")
                # Checkbox de segurança
                confirm = st.checkbox("Liberar Exclusão", key=f"del_{target_uid}")
                
                if st.button("EXCLUIR USUÁRIO", type="primary", disabled=not confirm):
                    if target_uid == st.session_state.user_id:
                        st.error("Você não pode excluir a si mesmo.")
                    else:
                        # 1. Apaga Transações
                        run_query("DELETE FROM transactions WHERE user_id=?", (int(target_uid),), commit=True)
                        # 2. Apaga Usuário
                        run_query("DELETE FROM users WHERE id=?", (int(target_uid),), commit=True)
                        
                        st.success(f"Usuário {target_user} excluído.")
                        time.sleep(1)
                        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.caption("© 2024 RipariBank | Versão Final e Completa")
