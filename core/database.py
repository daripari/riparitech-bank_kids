# -*- coding: utf-8 -*-
import streamlit as st
from sqlalchemy import text
import pandas as pd

@st.cache_resource
def get_connection():
    """Estabelece conexão com o banco de dados Supabase via Streamlit Connection"""
    try:
        return st.connection("supabase", type="sql")
    except Exception:
        # Em caso de erro na conexão, retorna None para tratamento posterior
        return None

def run_query(query_str, params=None, commit=False):
    """
    Executa queries SQL no banco de dados.
    - query_str: A string da consulta SQL.
    - params: Dicionário de parâmetros para a query.
    - commit: Se True, executa commit (INSERT, UPDATE, DELETE).
    """
    conn = get_connection()
    if not conn:
        return None
        
    try:
        if commit:
            with conn.session as s:
                s.execute(text(query_str), params if params else {})
                s.commit()
            # Limpa o cache após alterações para garantir dados atualizados
            st.cache_data.clear()
            return True
        else:
            # Retorna um DataFrame para consultas SELECT
            return conn.query(query_str, params=params if params else {}, ttl=0)
    except Exception as e:
        # Log de erro silencioso para não expor dados sensíveis no frontend
        return None

def init_db():
    """
    Inicializa as tabelas essenciais e aplica migrações de schema de forma versionada e segura.
    """
    conn = get_connection()
    if not conn:
        st.error("Falha na conexão com o banco de dados. A aplicação pode não funcionar corretamente.")
        return

    # 1. Definição do Schema Base (estado final esperado das tabelas)
    #    A utilização de CREATE TABLE IF NOT EXISTS é segura e idempotente.
    base_tables_creation_queries = [
        '''CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY, name TEXT NOT NULL, role TEXT, password TEXT,
            language TEXT DEFAULT 'pt', theme TEXT DEFAULT 'default',
            avatar_config TEXT DEFAULT 'default,default,default', background_url TEXT
        );''',
        '''CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY, user_id INTEGER, amount DOUBLE PRECISION, description TEXT,
            timestamp TIMESTAMP DEFAULT NOW(), type TEXT
        );''',
        '''CREATE TABLE IF NOT EXISTS chores (
            id SERIAL PRIMARY KEY, description TEXT, reward DOUBLE PRECISION, status TEXT DEFAULT 'open',
            assigned_to INTEGER, created_at TIMESTAMP DEFAULT NOW(), deadline TIMESTAMP,
            completed_at TIMESTAMP
        );''',
        '''CREATE TABLE IF NOT EXISTS allowances (
            id SERIAL PRIMARY KEY, user_id INTEGER, amount DOUBLE PRECISION, day_of_month INTEGER,
            last_paid DATE, frequency TEXT DEFAULT 'monthly'
        );''',
        '''CREATE TABLE IF NOT EXISTS batch_control (
            id SERIAL PRIMARY KEY, batch_name TEXT UNIQUE NOT NULL, last_run_date DATE
        );''',
        '''CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_on TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );'''
    ]
    for query in base_tables_creation_queries:
        run_query(query, commit=True)

    # 2. Sistema de Migração Versionado para aplicar alterações em schemas antigos
    applied_migrations_df = run_query("SELECT version FROM schema_migrations")
    applied_versions = set(applied_migrations_df['version']) if applied_migrations_df is not None and not applied_migrations_df.empty else set()

    # Define todas as migrações conhecidas, em ordem de versão
    migrations = {
        'v14_1_add_completed_at_to_chores': "ALTER TABLE chores ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;",
        'v14_3_add_frequency_to_allowances': "ALTER TABLE allowances ADD COLUMN IF NOT EXISTS frequency TEXT DEFAULT 'monthly';",
        'v14_4_add_theme_to_users': "ALTER TABLE users ADD COLUMN IF NOT EXISTS theme TEXT DEFAULT 'default';",
        'v14_5_add_avatar_config_to_users': "ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_config TEXT DEFAULT 'default,default,default';",
        'v14_6_change_to_double_precision': [
            "ALTER TABLE transactions ALTER COLUMN amount TYPE DOUBLE PRECISION;",
            "ALTER TABLE chores ALTER COLUMN reward TYPE DOUBLE PRECISION;",
            "ALTER TABLE allowances ALTER COLUMN amount TYPE DOUBLE PRECISION;"
        ],
        'v14_7_add_background_url_to_users': "ALTER TABLE users ADD COLUMN IF NOT EXISTS background_url TEXT;"
    }

    # Aplica as migrações pendentes em ordem alfabética/de versão
    for version in sorted(migrations.keys()):
        if version not in applied_versions:
            print(f"Applying database migration: {version}...")
            queries = migrations[version]
            try:
                # Garante que 'queries' seja sempre uma lista para simplificar o loop
                if not isinstance(queries, list):
                    queries = [queries]
                
                for query in queries:
                    run_query(query, commit=True)
                
                # Registra a migração como bem-sucedida
                run_query("INSERT INTO schema_migrations (version) VALUES (:v)", params={'v': version}, commit=True)
                print(f"Successfully applied migration: {version}")
            except Exception as e:
                # Loga o erro e para o processo para evitar inconsistências
                print(f"ERROR applying migration {version}: {e}")
                st.error(f"Falha crítica ao atualizar o banco de dados para a versão {version}. A aplicação pode ficar instável.")
                break
