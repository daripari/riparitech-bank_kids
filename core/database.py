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
    Inicializa as tabelas essenciais v14.0 do Banco Riparitech.
    Inclui a coluna 'completed_at' na tabela 'chores' para rastrear a data de realização.
    """
    conn = get_connection()
    if conn:
        # Tabela de Usuários (Login e Preferências)
        run_query('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY, 
                name TEXT NOT NULL, 
                role TEXT, 
                password TEXT, 
                language TEXT DEFAULT 'pt'
            );
        ''', commit=True)
        
        # Tabela de Transações Financeiras (Extrato)
        run_query('''
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY, 
                user_id INTEGER, 
                amount REAL, 
                description TEXT, 
                timestamp TIMESTAMP DEFAULT NOW(), 
                type TEXT
            );
        ''', commit=True)
        
        # Tabela de Missões/Tarefas (Gestão e Prazos)
        # v14.0: Adição de completed_at para auditoria de atrasos
        run_query('''
            CREATE TABLE IF NOT EXISTS chores (
                id SERIAL PRIMARY KEY, 
                description TEXT, 
                reward REAL, 
                status TEXT DEFAULT 'open', 
                assigned_to INTEGER, 
                created_at TIMESTAMP DEFAULT NOW(), 
                deadline TIMESTAMP,
                completed_at TIMESTAMP
            );
        ''', commit=True)
        
        # Tabela de Mesadas (Agendamento Automático) v14.2
        run_query('''
            CREATE TABLE IF NOT EXISTS allowances (
                id SERIAL PRIMARY KEY, 
                user_id INTEGER, 
                amount REAL, 
                day_of_month INTEGER, 
                last_paid DATE,
                frequency TEXT DEFAULT 'monthly'
            );
        ''', commit=True)
        
        # Tabela de Controle de Execução de Batches v14.3
        run_query('''
            CREATE TABLE IF NOT EXISTS batch_control (
                id SERIAL PRIMARY KEY,
                batch_name TEXT UNIQUE NOT NULL,
                last_run_date DATE
            );
        ''', commit=True)
        
        # Patch de Migração v14.3: Adicionar suporte a frequência
        try:
            run_query("ALTER TABLE allowances ADD COLUMN IF NOT EXISTS frequency TEXT DEFAULT 'monthly';", commit=True)
        except: pass
        
        # Patch de Migração v14.1: Garantir que completed_at existe em tabelas antigas
        try:
            run_query("ALTER TABLE chores ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP;", commit=True)
        except: pass
