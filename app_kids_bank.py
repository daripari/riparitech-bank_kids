import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- 1. CONFIGURAÇÃO VISUAL & CSS (Upgrade de Layout) ---
st.set_page_config(page_title="RipariBank", page_icon="🏦", layout="centered")

# CSS Customizado para Mobile-First e Estética Premium
st.markdown("""
<style>
    /* Ajuste de padding para mobile ganhar espaço */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    /* Botões com largura total e bordas arredondadas (Melhor para toque) */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        font-weight: bold;
    }
    /* Estilo para métricas */
    div[data-testid="stMetric"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    /* Dark mode support override (opcional, ajusta o fundo da metrica se estiver escuro) */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMetric"] {
            background-color: #262730;
            border: 1px solid #464b5f;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS (CONEXÃO DIRETA BLINDADA) ---
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
    run_query('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, role TEXT, password TEXT)''', commit=True)
    run_query('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, 
                  description TEXT, timestamp TEXT, type TEXT)''', commit=True)
    
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

init_db()

# --- 3. VARIÁVEIS DE SESSÃO ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- 4. TELA DE LOGIN (LAYOUT CENTRALIZADO) ---
if not st.session_state.logged_in:
    # Espaçamento para centralizar no Desktop
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🏦 RipariBank</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Gestão de Patrimônio Familiar</p>", unsafe_allow_html=True)
        st.divider()
        
        with st.form("login_form"):
            user_input = st.text_input("Usuário", placeholder="ex: daniel.ripari").lower().strip()
            pass_input = st.text_input("Senha", type="password")
            
            # Espaço vertical
            st.markdown("###")
            if st.form_submit_button("ACESSAR CONTA"):
                res = run_query("SELECT * FROM users WHERE name=? AND password=?", (user_input, pass_input))
                if res:
                    st.session_state.logged_in = True
                    st.session_state.user_id = res[0][0]
                    st.session_state.user_name = res[0][1]
                    st.session_state.role = res[0][2]
                    st.rerun()
                else:
                    st.error("Credenciais não conferem.")

# --- 5. SISTEMA PRINCIPAL (LAYOUT RESPONSIVO) ---
else:
    # --- SIDEBAR (PERFIL) ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/9322/9322127.png", width=80)
        st.write(f"Olá, **{st.session_state.user_name.title()}**")
        st.caption(f"Perfil: {st.session_state.role.upper()}")
        st.divider()
        if st.button("SAIR / LOGOUT", type="secondary"):
            st.session_state.logged_in = False
            st.rerun()

    # --- DASHBOARD (Comum a todos) ---
    st.markdown(f"### 📊 Visão Geral")
    
    # Busca Saldo
    res_bal = run_query("SELECT SUM(amount) FROM transactions WHERE user_id=?", (st.session_state.user_id,))
    saldo = res_bal[0][0] if res_bal and res_bal[0][0] else 0.0
    
    # Card de Saldo
    st.metric("Saldo Disponível", f"R$ {saldo:,.2f}")

    # Gráfico e Extrato
    tab_extrato, tab_grafico = st.tabs(["📜 Extrato Detalhado", "📈 Análise Visual"])

    with tab_extrato:
        df_hist = pd.read_sql_query(
            "SELECT timestamp, description, type, amount FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 15", 
            sqlite3.connect(DB_FILE), params=(st.session_state.user_id,)
        )
        
        if not df_hist.empty:
            # Formatação Visual da Tabela
            st.dataframe(
                df_hist, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "timestamp": st.column_config.DatetimeColumn("Data", format="DD/MM HH:mm"),
                    "description": "Motivo",
                    "type": "Tipo",
                    "amount": st.column_config.NumberColumn("Valor", format="R$ %.2f")
                }
            )
        else:
            st.info("Nenhuma movimentação recente.")

    with tab_grafico:
        if not df_hist.empty:
            # Gráfico Simples de Barras por Tipo
            chart_data = df_hist.groupby("type")["amount"].sum().reset_index()
            # Ajusta valores para serem todos positivos para visualização de volume
            chart_data['amount'] = chart_data['amount'].abs()
            st.bar_chart(chart_data, x="type", y="amount", color="type", use_container_width=True)
        else:
            st.caption("Sem dados para gráficos.")

    # --- ÁREA DE ADMINISTRAÇÃO (Painel de Comando) ---
    if st.session_state.role == 'admin':
        st.markdown("---")
        st.subheader("🛠️ Console Administrativo")
        
        # Expander para economizar espaço no mobile
        with st.expander("💸 Realizar Lançamento (Crédito/Débito)", expanded=True):
            # Carrega usuários 'user' (filhos)
            filhos = pd.read_sql_query("SELECT id, name FROM users WHERE role='user'", sqlite3.connect(DB_FILE))
            
            if filhos.empty:
                st.warning("Nenhum filho cadastrado.")
            else:
                with st.form("form_lancamento"):
                    target_name = st.selectbox("Conta Destino:", filhos['name'].tolist())
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        # Passo 1.0 facilita digitar no celular
                        val = st.number_input("Valor (R$)", min_value=0.00, step=1.0) 
                    with c2:
                        op = st.radio("Operação", ["Crédito", "Débito"])
                    
                    desc = st.text_input("Motivo da transação")
                    
                    submitted = st.form_submit_button("CONFIRMAR TRANSAÇÃO")
                    if submitted:
                        if val > 0 and desc:
                            target_id = filhos[filhos['name'] == target_name]['id'].values[0]
                            final_val = val if op == "Crédito" else -val
                            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (?, ?, ?, ?, ?)", 
                                      (int(target_id), final_val, desc, ts, op), commit=True)
                            
                            st.success("✅ Sucesso!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Preencha valor e motivo.")

        with st.expander("👥 Gestão de Usuários (Configurações)"):
            tab_add, tab_edit = st.tabs(["Novo Usuário", "Editar Existente"])
            
            with tab_add:
                with st.form("form_add_user"):
                    st.caption("Cadastrar novo membro")
                    new_n = st.text_input("Nome.Sobrenome").lower().strip()
                    new_r = st.selectbox("Perfil", ["user", "admin"])
                    new_p = st.text_input("Senha Inicial")
                    
                    if st.form_submit_button("CRIAR MEMBRO"):
                        if new_n and new_p:
                            check = run_query("SELECT * FROM users WHERE name=?", (new_n,))
                            if check:
                                st.error("Usuário já existe.")
                            else:
                                run_query("INSERT INTO users (name, role, password) VALUES (?, ?, ?)", 
                                          (new_n, new_r, new_p), commit=True)
                                st.success(f"Bem-vindo(a) {new_n}!")
                                time.sleep(0.5)
                                st.rerun()

            with tab_edit:
                all_users = pd.read_sql_query("SELECT id, name FROM users ORDER BY name", sqlite3.connect(DB_FILE))
                target_user = st.selectbox("Editar quem?", all_users['name'].unique())
                target_uid = all_users[all_users['name'] == target_user]['id'].values[0]

                # Formulário de Senha
                with st.form("form_senha"):
                    new_pass = st.text_input(f"Nova Senha para {target_user}")
                    if st.form_submit_button("SALVAR NOVA SENHA"):
                        if new_pass:
                            run_query("UPDATE users SET password=? WHERE id=?", (new_pass, int(target_uid)), commit=True)
                            st.success("Senha atualizada.")
                            time.sleep(0.5)
                            st.rerun()
                
                st.markdown("###")
                # Botão de Exclusão Direta
                col_del_check, col_del_btn = st.columns([2, 3])
                with col_del_check:
                    confirm = st.checkbox("Liberar Exclusão", key=f"del_{target_uid}")
                with col_del_btn:
                    if st.button("🗑️ EXCLUIR CONTA", type="primary", disabled=not confirm):
                        if target_uid == st.session_state.user_id:
                            st.error("Proibido auto-exclusão.")
                        else:
                            run_query("DELETE FROM transactions WHERE user_id=?", (int(target_uid),), commit=True)
                            run_query("DELETE FROM users WHERE id=?", (int(target_uid),), commit=True)
                            st.success("Conta removida.")
                            time.sleep(0.5)
                            st.rerun()

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 0.8em;'>© 2024 RipariBank | Technology by RipariTech</p>", unsafe_allow_html=True)
