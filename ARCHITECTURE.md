# 🏛️ Arquitetura do Sistema - Banco Riparitech (Kids Bank)

## 1. Visão Geral
O **Banco Riparitech** é uma aplicação web de *Home Banking* gamificado, desenvolvida para promover a educação financeira de crianças. O sistema opera sob uma arquitetura **Monolítica Modular** baseada em Python, utilizando o framework **Streamlit** para renderização de interface e **PostgreSQL (via Supabase)** para persistência de dados.

A aplicação se divide em dois perfis de acesso distintos:
1.  **Admin (Pais):** Controle total, gestão de tarefas, pagamentos e auditoria.
2.  **Kid (Filhos):** Visualização de saldo, execução de tarefas, transferências e personalização.

---

## 2. Stack Tecnológico

| Componente | Tecnologia | Função |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.11+ | Lógica de backend e frontend. |
| **Frontend** | Streamlit | Renderização reativa da interface web. |
| **Banco de Dados** | PostgreSQL (Supabase) | Armazenamento relacional (via `st.connection`). |
| **ORM/Query** | SQLAlchemy / Pandas | Manipulação de dados e execução de queries SQL. |
| **Estilização** | CSS3 (Injected) | Customização visual ("Obsidian Liquid UI"). |
| **Processamento** | Pandas | Manipulação de DataFrames para relatórios e lógica. |

---

## 3. Estrutura de Diretórios e Módulos

A aplicação segue uma organização modular para separar a lógica de visualização, regras de negócio e acesso a dados.

```text
riparitech-bank_kids/
├── app_kids_bank.py       # 🚀 Entry Point: Roteamento, Login e Configuração Global
├── batch_allowance.py     # ⚙️ Processamento Batch: Lógica de pagamento de mesadas
├── views/                 # 🖼️ Camada de Apresentação (Frontend Logic)
│   ├── admin.py           # Interface do Administrador (Gestão, Auditoria)
│   └── kid.py             # Interface da Criança (Extrato, Missões, Avatar)
├── core/                  # 🧠 Camada de Núcleo (Backend Logic & Utils)
│   ├── database.py        # Abstração do Banco de Dados e Migrações
│   ├── styles.py          # Injeção de CSS e Lógica de Temas
│   ├── themes.py          # Definição dos esquemas de cores (Temas)
│   ├── utils.py           # Internacionalização (i18n) e Helpers
│   └── avatars.py         # Gerador de Avatares SVG dinâmicos
├── locales/               # 🌐 Arquivos de Internacionalização (i18n)
│   ├── pt.json            # Traduções para Português
│   └── en.json            # Traduções para Inglês, etc.
└── .devcontainer/         # Configuração de ambiente de desenvolvimento
```

---

## 4. Detalhamento dos Componentes

### 4.1. Entry Point (`app_kids_bank.py`)
Atua como o **Controlador Principal**.
*   **Gerenciamento de Sessão:** Inicializa variáveis de estado (`st.session_state`) como login, role, idioma e tema.
*   **Roteamento:** Decide qual visualização renderizar (`views_admin` ou `views_kid`) com base no `user_role`.
*   **Orquestrador de Batches:** Executa a função `run_daily_batches()` a cada carregamento para verificar se há mesadas pendentes, garantindo que o processamento ocorra mesmo sem um servidor de cronjob dedicado.
*   **Autenticação:** Realiza o login consultando a tabela `users` e validando o hash SHA-256 da senha.

### 4.2. Camada de Dados (`core/database.py`)
Gerencia a conexão com o Supabase.
*   **Conexão:** Utiliza `st.connection("supabase", type="sql")` para pool de conexões.
*   **Auto-Migração (`init_db`):** Ao iniciar, verifica a existência das tabelas e aplica "Patches de Migração" (blocos `try/except` com `ALTER TABLE`) para evoluir o esquema do banco sem perda de dados.
*   **Cache:** Implementa limpeza inteligente de cache (`st.cache_data.clear()`) após operações de escrita (INSERT/UPDATE/DELETE) para garantir consistência na interface.

### 4.3. Camada Visual e Estilização (`core/styles.py` & `core/themes.py`)
A aplicação não usa o visual padrão do Streamlit.
*   **Liquid UI:** Injeta CSS personalizado para criar cartões com efeito de vidro ("glassmorphism"), gradientes e fontes personalizadas (Outfit, JetBrains Mono).
*   **Temas Dinâmicos:** Permite a troca de paletas de cores em tempo real.
*   **Background Personalizado:** Suporta injeção de CSS para renderizar imagens de fundo (Base64) definidas pelo usuário.

### 4.4. Gamificação e Avatares (`core/avatars.py`)
*   **Renderização SVG:** Gera strings SVG dinamicamente combinando partes do corpo (rosto, cabelo, roupa) baseadas na configuração salva no banco (`avatar_config`). Isso evita a necessidade de armazenar milhares de imagens estáticas.

### 4.5. Internacionalização (`core/utils.py`)
*   **Sistema i18n:** Utiliza um dicionário central (`TRANSLATIONS`) suportando 9 idiomas (PT, EN, ES, FR, DE, IT, JA, ZH, HI). A função `t(key)` resolve a string baseada no idioma da sessão.

---

## 5. Modelo de Dados (Schema)

O banco de dados relacional possui as seguintes tabelas principais:

1.  **`users`**:
    *   Armazena credenciais, perfil (`admin`/`user`), preferências (idioma, tema, avatar) e a imagem de fundo (Base64).
2.  **`transactions`**:
    *   Log imutável de todas as movimentações financeiras (Entradas, Saídas, Transferências, Multas).
    *   Usa `DOUBLE PRECISION` para evitar erros de arredondamento em grandes valores.
3.  **`chores`** (Tarefas):
    *   Gerencia o ciclo de vida das missões: `open` -> `pending` (feito) -> `paid` (aprovado) ou `canceled`.
    *   Registra `deadline` (prazo) e `completed_at` (data de entrega) para auditoria de atrasos.
4.  **`allowances`** (Mesadas):
    *   Configuração de pagamentos recorrentes (Diário, Semanal, Mensal).
    *   Controla `last_paid` para evitar pagamentos duplicados.
5.  **`batch_control`**:
    *   Tabela de controle interno para garantir que os scripts de automação (mesadas) rodem apenas uma vez por dia/período.

---

## 6. Fluxos de Negócio Principais

### A. Fluxo de Tarefas (Gamificação)
1.  **Admin** cria uma tarefa (`chores`) com valor e prazo.
2.  **Kid** visualiza na aba "Missões" e marca como feita (`status='pending'`, `completed_at=NOW()`).
3.  **Admin** visualiza na aba "Aprovações".
    *   Se aprovar: O status muda para `paid` e uma transação de crédito é criada.
    *   Se rejeitar: O status volta para `open`.
4.  **Auditoria:** O sistema destaca visualmente tarefas entregues com atraso, permitindo ao Admin aplicar multas (transação de débito).

### B. Fluxo de Mesada (Automação)
1.  O `app_kids_bank.py` chama `run_daily_batches()` na inicialização.
2.  O sistema verifica em `batch_control` a data da última execução.
3.  Se a data for anterior a hoje, chama `process_allowances_for_date` (em `batch_allowance.py`).
4.  O script verifica frequência (mensal/semanal/diária) e dia configurado. Se coincidir, gera a transação e atualiza `last_paid`.

### C. Personalização (Avatar e Fundo)
1.  **Upload de Imagem:** O usuário envia uma imagem. O Python (Pillow) redimensiona para 1024x1024 e comprime em JPEG para otimizar performance.
2.  **Persistência:** A imagem é convertida para Base64 e salva na coluna `background_url` da tabela `users`.
3.  **Renderização:** O `core/styles.py` lê essa string e a injeta como `background-image` no CSS da página.
