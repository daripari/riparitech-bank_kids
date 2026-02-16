# -*- coding: utf-8 -*-
import streamlit as st
from sqlalchemy import text
import pandas as pd

@st.cache_resource
def get_connection():
    try:
        return st.connection("supabase", type="sql")
    except Exception:
        return None

def run_query(query_str, params=None, commit=False):
    conn = get_connection()
    if not conn: return None
    try:
        if commit:
            with conn.session as s:
                s.execute(text(query_str), params if params else {})
                s.commit()
            st.cache_data.clear()
            return True
        else:
            return conn.query(query_str, params=params if params else {}, ttl=0)
    except Exception as e:
        return None

def init_db():
    """Inicializa as tabelas essenciais (Notificações removidas)"""
    conn = get_connection()
    if conn:
        run_query('''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT NOT NULL, role TEXT, password TEXT, language TEXT DEFAULT 'pt');''', commit=True)
        run_query('''CREATE TABLE IF NOT EXISTS transactions (id SERIAL PRIMARY KEY, user_id INTEGER, amount REAL, description TEXT, timestamp TIMESTAMP, type TEXT);''', commit=True)
        # Tabela de notificações removida do protocolo de inicialização
        run_query('''CREATE TABLE IF NOT EXISTS chores (id SERIAL PRIMARY KEY, description TEXT, reward REAL, status TEXT DEFAULT 'open', assigned_to INTEGER, created_at TIMESTAMP, deadline TIMESTAMP);''', commit=True)
