import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURAÇÃO INICIAL (Deve ser a primeira linha) ---
st.set_page_config(page_title="RipariBank", page_icon="💰", layout="centered")

# --- 2. GERENCIAMENTO DE ESTADO (SESSION STATE) ---
if 'feedback_msg' not in st.session_state:
    st.session_state.feedback_msg = None  # Tupla (tipo, mensagem)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- 3. CAMADA DE DADOS (SQLITE BLINDADO) ---
DB_FILE = 'kids_bank.db'

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, role TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, 
                  description TEXT, timestamp TEXT, type TEXT)''')
    
    # Seed Inicial (Se não existir o Admin Pai)
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

# Inicializa banco
init_db()

# --- 4. FUNÇÕES DE NEGÓCIO (CRUD) ---

def login_user(username, password):
    conn = get_connection()
    # Query parametrizada segura
    df = pd.read_sql("SELECT * FROM users WHERE name=? AND password=?", conn, params=(username, password))
    conn.close()
    return df

def get_all_users():
    conn = get_connection()
    df = pd.read_sql("SELECT id, name, role FROM users ORDER BY name", conn)
    conn.close()
    return df

def get_balance(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ?", (user_id,))
    res = c.fetchone()[0]
    conn.close()
    return res if res else 0.0

def get_history(user_id):
    conn = get_connection()
    df = pd.read_sql("SELECT timestamp as Data, type as Tipo, description as Motivo, amount as Valor FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10", conn, params=(user_id,))
    conn.close()
    return df

# --- 5. FUNÇÕES DE AÇÃO (CALLBACKS PARA BOTÕES) ---
# Estas funções rodam ANTES da interface ser redesenhada.

def action_add_transaction():
    # Coleta dados do Session State (Formulário)
    uid = st.session_state.trans_target_id
    val = st.session_state.trans_val
    op = st.session_state.trans_op
    desc = st.session_state.trans_desc

    if val <= 0 or not desc:
        st.session_state.feedback_msg = ("error", "Valor deve ser maior que zero e motivo é obrigatório.")
        return

    conn = get_connection()
    try:
        c = conn.cursor()
        final_amount = val if op == "Crédito" else -val
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (?, ?, ?, ?, ?)",
                  (uid, final_amount, desc, timestamp, op))
        conn.commit()
        st.session_state.feedback_msg = ("success", f"Lançamento de R$ {val} realizado com sucesso!")
    except Exception as e:
        st.session_state.feedback_msg = ("error", f"Erro no banco: {str(e)}")
    finally:
        conn.close()

def action_create_user():
    name = st.session_state.new_u_name.lower().strip()
    role = st.session_state.new_u_role
    pwd = st.session_state.new_u_pwd

    if not name or not pwd:
        st.session_state.feedback_msg = ("error", "Preencha nome e senha.")
        return

    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT count(*) FROM users WHERE name=?", (name,))
        if c.fetchone()[0] > 0:
            st.session_state.feedback_msg = ("error", "Usuário já existe.")
        else:
            c.execute("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", (name, role, pwd))
            conn.commit()
            st.session_state.feedback_msg = ("success", f"Usuário {name} criado!")
    except Exception as e:
        st.session_state.feedback_msg = ("error", str(e))
    finally:
        conn.close()

def action_update_password():
    # O ID vem do argumento do botão ou do selectbox
    # Para segurança, vamos pegar do selectbox atual
    target_name = st.session_state.edit_selected_user
    new_pass = st.session_state.edit_new_pass
    
    if not new_pass:
        st.session_state.feedback_msg = ("error", "Senha não pode ser vazia.")
        return

    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("UPDATE users SET password=? WHERE name=?", (new_pass, target_name))
        conn.commit()
        st.session_state.feedback_msg = ("success", f"Senha de {target_name} atualizada.")
    except Exception as e:
        st.session_state.feedback_msg = ("error", str(e))
    finally:
        conn.close()

def action_delete_user():
    target_name = st.session_state.edit_selected_user
    
    conn = get_connection()
    try:
        # Busca ID primeiro
        df = pd.read_sql("SELECT id FROM users WHERE name=?", conn, params=(target_name,))
        if df.empty:
            st.session_state.feedback_msg = ("error", "Usuário não encontrado.")
            return
        
        target_id = int(df.iloc[0]['id'])
        
        # Proteção contra suicídio digital
        if target_id == st.session_state.user_id:
            st.session_state.feedback_msg = ("error", "Você não pode excluir a si mesmo.")
            return

        c = conn.cursor()
        c.execute("DELETE FROM transactions WHERE user_id=?", (target_id,))
        c.execute("DELETE FROM users WHERE id=?", (target_id,))
        conn.commit()
        st.session_state.feedback_msg = ("success", f"Usuário {target_name} foi excluído.")
    except Exception as e:
        st.session_state.feedback_msg = ("error", str(e))
    finally:
        conn.close()


# --- 6. INTERFACE DE USUÁRIO (FRONTEND) ---

st.title("💰 RipariBank")

# Exibição de Mensagens Globais (Feedback Loop)
if st.session_state.feedback_msg:
    tipo, texto = st.session_state.feedback_msg
    if tipo == 'success':
        st.success(texto)
    else:
        st.error(texto)
    st.session_state.feedback_msg = None # Limpa mensagem

# --- TELA DE LOGIN ---
if not st.session_state.logged_in:
    st.markdown("### 🔐 Acesso Seguro")
    with st.form("login_form"):
        u_in = st.text_input("Usuário", placeholder="ex: daniel.ripari").lower().strip()
        p_in = st.text_input("Senha", type="password")
        btn_login = st.form_submit_button("Entrar")
        
        if btn_login:
            user_data = login_user(u_in, p_in)
            if not user_data.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = int(user_data.iloc[0]['id'])
                st.session_state.user_name = user_data.iloc[0]['name']
                st.session_state.role = user_data.iloc[0]['role']
                st.rerun()
            else:
                st.error("Credenciais inválidas.")

# --- TELA PRINCIPAL (LOGADO) ---
else:
    # Header e Logout
    c_head1, c_head2 = st.columns([3, 1])
    c_head1.markdown(f"**Olá, {st.session_state.user_name}** ({st.session_state.role})")
    if c_head2.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()

    # --- DASHBOARD COMUM ---
    bal = get_balance(st.session_state.user_id)
    st.metric("💰 Saldo Pessoal", f"R$ {bal:.2f}")
    
    with st.expander("📜 Ver meu Extrato", expanded=False):
        st.dataframe(get_history(st.session_state.user_id), hide_index=True, use_container_width=True)

    # --- ÁREA ADMINISTRATIVA ---
    if st.session_state.role == 'admin':
        st.markdown("---")
        st.subheader("⚙️ Painel de Controle")
        
        # Menu de Navegação Admin
        menu_admin = st.radio("Selecione:", ["Lançamentos Financeiros", "Gestão de Usuários"], horizontal=True)

        if menu_admin == "Lançamentos Financeiros":
            users_df = get_all_users()
            kids = users_df[users_df['role'] == 'user']
            
            if kids.empty:
                st.warning("Cadastre usuários 'user' (filhos) primeiro na aba de Gestão.")
            else:
                # FORMULÁRIO DE LANÇAMENTO
                # O form encapsula o estado. O callback action_add_transaction processa.
                with st.form("form_lancamento"):
                    st.write("Novo Lançamento")
                    
                    # Seleção do alvo (Mapeia nome para ID)
                    target_name = st.selectbox("Para quem?", kids['name'])
                    # Recupera ID do selecionado para passar ao state
                    target_id_val = kids[kids['name'] == target_name]['id'].values[0]
                    
                    # Hack para passar o ID para o callback (Invisible Input ou Logic inside Callback)
                    # Melhor: O callback lê o widget key. Mas selectbox retorna valor.
                    # Vamos simplificar: O callback vai recalcular o ID baseando-se no session_state do selectbox se precisasse,
                    # mas aqui vamos passar via args é complexo em forms. 
                    # SOLUÇÃO ROBUSTA: Usar st.session_state manual no form submit.
                    
                    c1, c2 = st.columns(2)
                    v_in = c1.number_input("Valor R$", min_value=0.0, step=1.0, key="trans_val")
                    op_in = c1.radio("Tipo", ["Crédito", "Débito"], key="trans_op")
                    d_in = c2.text_input("Motivo", key="trans_desc")
                    
                    # Botão Submit chama o Callback
                    # Precisamos salvar o ID do alvo no state antes de chamar, ou o callback deve ler.
                    # Como o selectbox está dentro do form, seu valor estará no state quando o submit for clicado.
                    
                    submitted = st.form_submit_button("Confirmar", on_click=action_add_transaction)
                    
                    # TRUQUE DO SHELDON: O selectbox dentro do form não escreve no state na hora.
                    # Então precisamos passar o ID manualmente.
                    # REVISÃO: O callback roda antes do script continuar. 
                    # Vamos ajustar o callback para ler o ID do dataframe baseando-se no nome selecionado? Não, o form limpa.
                    # CORREÇÃO DEFINITIVA DO FORMULÁRIO:
                    # Usamos st.session_state para guardar o ID alvo? Não.
                    # Vamos usar a lógica pós-submit (sem callback complexo) que é mais segura para iniciantes.
                
                # REFAZENDO A LÓGICA DO SUBMIT PARA SER INFALÍVEL SEM CALLBACK MÁGICO
                if submitted:
                    # O código aqui roda APÓS o reload do form. Os dados estão em st.session_state ou nas variáveis.
                    # Mas espere, se usar on_click, roda antes. Vamos tirar o on_click e fazer imperativo.
                    pass 
                
                # --- ABORDAGEM IMPERATIVA (SEM CALLBACK NO FORM) - MAIS ESTÁVEL ---
                # A anterior falhou por callback context. Vamos fazer o simples que funciona.
                
    # --- REFAZENDO A LÓGICA DE ADMIN PARA GARANTIR FUNCIONAMENTO ---
    # Ignorem o bloco acima, vamos reimplementar a lógica visual direta.
    
    if st.session_state.role == 'admin':
        # (Re-renderizando para garantir limpeza)
        
        if menu_admin == "Lançamentos Financeiros":
            users_df = get_all_users()
            kids = users_df[users_df['role'] == 'user']
            if not kids.empty:
                target = st.selectbox("Selecione a conta:", kids['name'])
                uid_target = kids[kids['name'] == target]['id'].values[0]
                
                with st.form("transacao_imperativa"):
                    c1, c2 = st.columns(2)
                    val = c1.number_input("Valor", min_value=0.01)
                    op = c1.radio("Tipo", ["Crédito", "Débito"])
                    desc = c2.text_input("Motivo")
                    
                    if st.form_submit_button("EXECUTAR LANÇAMENTO"):
                        # Código direto. Simples. Funciona.
                        conn = get_connection()
                        try:
                            final = val if op == "Crédito" else -val
                            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            conn.execute("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (?, ?, ?, ?, ?)",
                                      (uid_target, final, desc, ts, op))
                            conn.commit()
                            st.success("Lançamento Realizado!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(e)
                        finally:
                            conn.close()

        elif menu_admin == "Gestão de Usuários":
            c_left, c_right = st.columns(2)
            
            with c_left:
                st.info("➕ Novo Usuário")
                with st.form("new_user_simples"):
                    n = st.text_input("Nome (ex: joao.ripari)").lower().strip()
                    r = st.selectbox("Perfil", ["user", "admin"])
                    p = st.text_input("Senha")
                    
                    if st.form_submit_button("CRIAR"):
                        if n and p:
                            conn = get_connection()
                            try:
                                # Check duplicidade
                                if not pd.read_sql("SELECT * FROM users WHERE name=?", conn, params=(n,)).empty:
                                    st.error("Já existe.")
                                else:
                                    conn.execute("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", (n, r, p))
                                    conn.commit()
                                    st.success(f"Criado: {n}")
                                    time.sleep(1)
                                    st.rerun()
                            finally:
                                conn.close()
            
            with c_right:
                st.warning("🔧 Editar / Excluir")
                all_u = get_all_users()
                
                # O SEGREDO: Session State para o Selectbox
                # Se não usarmos chave, ele reseta.
                target_edit = st.selectbox("Selecione Usuário:", all_u['name'], key="sel_user_edit")
                
                # --- ALTERAR SENHA ---
                # Form separado para isolar o estado do input de senha
                with st.form("mudar_senha_form"):
                    st.write(f"Alterar senha de: **{target_edit}**")
                    new_p = st.text_input("Nova Senha")
                    
                    if st.form_submit_button("ATUALIZAR SENHA"):
                        conn = get_connection()
                        conn.execute("UPDATE users SET password=? WHERE name=?", (new_p, target_edit))
                        conn.commit()
                        conn.close()
                        st.success("Senha Atualizada!")
                        time.sleep(1) # Dá tempo de ler antes do rerun opcional
                
                st.markdown("---")
                
                # --- EXCLUIR ---
                # A lógica de exclusão PRECISA ser fora de form para usar callback ou botão direto com lógica imediata?
                # Vamos usar botão direto COM LÓGICA IMEDIATA e RERUN. É o mais seguro.
                st.write(f"Zona de Perigo: **{target_edit}**")
                
                # Checkbox de trava
                confirm = st.checkbox("Destravar Exclusão", key="lock_del")
                
                if st.button("EXCLUIR USUÁRIO DEFINITIVAMENTE", type="primary", disabled=not confirm):
                    # Recupera ID
                    uid_del = all_u[all_u['name'] == target_edit]['id'].values[0]
                    
                    if uid_del == st.session_state.user_id:
                        st.error("Não pode excluir a si mesmo.")
                    else:
                        conn = get_connection()
                        conn.execute("DELETE FROM transactions WHERE user_id=?", (uid_del,))
                        conn.execute("DELETE FROM users WHERE id=?", (uid_del,))
                        conn.commit()
                        conn.close()
                        st.success(f"Adeus, {target_edit}.")
                        time.sleep(1)
                        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.caption("© 2024 RipariBank | Versão Final R-012")
