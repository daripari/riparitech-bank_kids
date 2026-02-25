# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import json
import os
import io
import base64
from PIL import Image
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

def process_background_upload(uploaded_file, user_id):
    """
    Processa o upload de imagem de fundo de forma segura.
    Verifica se o arquivo já foi processado para evitar loops de feedback (bug do toast repetido).
    """
    if uploaded_file is None:
        return

    # Cria um ID único para o arquivo baseado em nome e tamanho
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # Verifica no session_state se este arquivo específico já foi processado
    if st.session_state.get('last_bg_upload_id') == file_id:
        return # Já processado, não faz nada

    try:
        # Processamento da Imagem (Redimensionar e Comprimir para otimização)
        image = Image.open(uploaded_file)
        if image.mode in ('RGBA', 'P'): image = image.convert('RGB')
        image.thumbnail((1024, 1024)) # Limita a 1024px
        
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=80)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        bg_url = f"data:image/jpeg;base64,{img_str}"
        
        # Persistência no Banco de Dados
        run_query("UPDATE users SET background_url = :bg WHERE id = :uid", 
                  params={'bg': bg_url, 'uid': user_id}, commit=True)
        
        # Atualiza Estado da Sessão e Marca como Processado
        st.session_state.user_background = bg_url
        st.session_state.last_bg_upload_id = file_id
        
        # Feedback (Toast) - Aparecerá apenas uma vez por arquivo
        st.toast(t('bg_updated'), icon='🎨')
        
    except Exception as e:
        st.error(f"Erro ao processar imagem: {e}")
