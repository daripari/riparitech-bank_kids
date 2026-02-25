# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import json
import os
from .database import run_query

@st.cache_data
def load_translations(lang: str) -> dict:
    """
    Carrega um arquivo de idioma do diretório 'locales'.
    Faz fallback para 'pt' se o arquivo do idioma solicitado não existir.
    """
    # O caminho é relativo à raiz do projeto, onde o app Streamlit é executado
    path = f"locales/{lang}.json"
    if not os.path.exists(path):
        path = "locales/pt.json"
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Em caso de erro (ex: pt.json não encontrado), retorna um dict vazio para evitar que a app quebre.
        return {}

def t(key: str) -> str:
    """Obtém uma string de tradução para uma chave específica, com base no idioma da sessão."""
    lang = st.session_state.get('lang', 'pt')
    translations = load_translations(lang)
    return translations.get(key, key)

@st.cache_data(ttl=600)
def get_balance(uid):
    res = run_query("SELECT SUM(amount) as total FROM transactions WHERE user_id=:uid", params={'uid': uid})
    val = res.iloc[0]['total'] if res is not None and not res.empty and pd.notnull(res.iloc[0]['total']) else 0.0
    return val

def get_family_balances():
    query = """
        SELECT u.id, u.name, u.avatar_config, COALESCE(SUM(t.amount), 0) as balance 
        FROM users u 
        LEFT JOIN transactions t ON u.id = t.user_id 
        WHERE u.role = 'user' 
        GROUP BY u.id, u.name, u.avatar_config ORDER BY u.name
    """
    return run_query(query)
