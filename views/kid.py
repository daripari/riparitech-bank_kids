# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import time
# Importando módulos do core
from core.database import run_query
from core.themes import THEMES
from core.utils import t, get_balance
from core.avatars import render_avatar, get_avatar_part_names

def render_kid_view():
    """
    Interface do Usuário (Kids) v14.1 - Banco Riparitech.
    Foco: Suporte multi-idioma e integração com o Comando Admin.
    """
    uid = st.session_state.user_id
    balance = get_balance(uid)
    
    # Verifica se tem mesada configurada
    allowance = run_query("SELECT amount, day_of_month FROM allowances WHERE user_id=:uid", {'uid': uid})
    allowance_info = ""
    if allowance is not None and not allowance.empty:
        day = allowance.iloc[0]['day_of_month']
        amt = allowance.iloc[0]['amount']
        allowance_info = f"<div style='font-size:0.8rem; color:var(--accent-color-1); margin-top:-10px; opacity:0.8;'>📅 {t('next_allowance')}: Dia {day} (R$ {amt:.0f})</div>"

    # --- SEÇÃO HERO: SALDO CENTRAL ---
    st.markdown(f"""
    <div class="hero-balance">
        <div class="hero-label">{t('bal')}</div>
        <div class="hero-value">R$ {balance:,.2f}</div>
        {allowance_info}
    </div>
    """, unsafe_allow_html=True)
    
    # --- NAVEGAÇÃO POR ABAS (TABS) ---
    t_ext, t_mis, t_tra, t_cam, t_prof = st.tabs([f"📜 {t('home')}", f"🎯 {t('missions')}", f"💸 {t('transfer')}", f"💱 {t('tools')}", f"👤 {t('profile_tab')}"])
    
    # --- ABA 1: EXTRATO ---
    with t_ext:
        st.markdown(f"##### {t('last_mov')}")
        hist = run_query("""
            SELECT description, amount, timestamp 
            FROM transactions 
            WHERE user_id=:u 
            ORDER BY id DESC LIMIT 5
        """, {'u': uid})
        
        if hist is not None and not hist.empty:
            with st.container(border=True):
                for _, r in hist.iterrows():
                    cor = "var(--accent-color-1)" if r['amount'] >= 0 else "#ff4b4b"
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <div style="font-size:0.9rem; color:#e0e0e0;">{r['description']}</div>
                        <div style="color:{cor}; font-weight:700;">R$ {r['amount']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(t('history_empty'))

    # --- ABA 2: MISSÕES ---
    with t_mis:
        st.markdown(f"##### {t('active_missions')}")
        m = run_query("""
            SELECT * FROM chores 
            WHERE assigned_to=:u AND status='open' 
            ORDER BY deadline ASC
        """, {'u': uid})
        
        if m is not None and not m.empty:
            for _, c in m.iterrows():
                with st.container(border=True):
                    dl = pd.to_datetime(c['deadline'])
                    st.markdown(f"**{c['description']}**")
                    st.caption(f"{t('deadline')}: {dl.strftime('%d/%m/%Y %H:%M') if not pd.isna(dl) else t('no_deadline')} | {t('value')}: **R$ {c['reward']:.2f}**")
                    
                    if st.button(t('mark_done'), key=f"c_{c['id']}", use_container_width=True):
                        # v14.1: Registra completed_at para auditoria de atraso no Admin
                        run_query("UPDATE chores SET status='pending', completed_at=NOW() WHERE id=:id", {'id': c['id']}, commit=True)
                        st.toast(t('sent_approval'))
                        time.sleep(0.5)
                        st.rerun()
        else:
            st.markdown(f"<div class='liquid-card' style='text-align:center; opacity:0.6;'>{t('no_active_miss')}</div>", unsafe_allow_html=True)

    # --- ABA 3: TRANSFERIR ---
    with t_tra:
        st.markdown(f"##### {t('send_money')}")
        siblings = run_query("SELECT id, name FROM users WHERE role='user' AND id != :uid", {'uid': uid})
        
        if siblings is not None and not siblings.empty:
            with st.container(border=True):
                with st.form("transfer_v14_1", clear_on_submit=True):
                    target = st.selectbox(t('to_whom'), siblings['name'].tolist())
                    amt = st.number_input(t('how_much'), min_value=1.0)
                    reason = st.text_input(t('reason'), placeholder="...")
                    
                    if st.form_submit_button(t('send_now'), use_container_width=True):
                        if amt > balance:
                            st.error(t('insufficient'))
                        else:
                            tid = siblings[siblings['name'] == target]['id'].values[0]
                            # Fluxo P2P: Débito e Crédito
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Envio')", 
                                      {'u': uid, 'a': -amt, 'd': f"{t('transfer')}: {target} - {reason}"}, commit=True)
                            run_query("INSERT INTO transactions (user_id, amount, description, timestamp, type) VALUES (:u, :a, :d, NOW(), 'Recebimento')", 
                                      {'u': int(tid), 'a': amt, 'd': f"{t('transfer')}: {st.session_state.user_name} - {reason}"}, commit=True)
                            st.success(t('transfer_done'))
                            time.sleep(1)
                            st.rerun()
        else:
            st.info(t('no_transfer'))

    # --- ABA 4: CÂMBIO ---
    with t_cam:
        st.markdown(f"##### {t('fx_title')}")
        
        # Taxas de câmbio (1 unidade da moeda estrangeira = X BRL)
        rates = {
            'EUR': {'name': 'EURO', 'rate': 5.45, 'symbol': '€'},
            'GBP': {'name': 'LIBRA ESTERLINA', 'rate': 6.60, 'symbol': '£'},
            'CHF': {'name': 'FRANCO SUÍÇO', 'rate': 5.60, 'symbol': 'CHF'},
            'USD': {'name': 'DÓLAR AMERICANO', 'rate': 5.05, 'symbol': 'US$'},
            'CAD': {'name': 'DÓLAR CANADENSE', 'rate': 3.70, 'symbol': 'C$'},
            'AUD': {'name': 'DÓLAR AUSTRALIANO', 'rate': 3.40, 'symbol': 'A$'},
            'CNY': {'name': 'YUAN CHINÊS', 'rate': 0.70, 'symbol': '¥'},
            'UYU': {'name': 'PESO URUGUAIO', 'rate': 0.13, 'symbol': '$U'},
            'INR': {'name': 'RUPIA INDIANA', 'rate': 0.064, 'symbol': '₹'},
            'JPY': {'name': 'IENE JAPONÊS', 'rate': 0.032, 'symbol': '¥'},
            'ARS': {'name': 'PESO ARGENTINO', 'rate': 0.0057, 'symbol': '$'},
            'KRW': {'name': 'WON SUL-COREANO', 'rate': 0.0037, 'symbol': '₩'},
            'CLP': {'name': 'PESO CHILENO', 'rate': 0.0053, 'symbol': '$'},
            'MXN': {'name': 'PESO MEXICANO', 'rate': 0.30, 'symbol': '$'},
            'CUP': {'name': 'PESO CUBANO', 'rate': 0.21, 'symbol': '$'},
            'VES': {'name': 'BOLÍVAR VENEZUELANO', 'rate': 0.14, 'symbol': 'Bs.'},
            'BOB': {'name': 'BOLIVIANO', 'rate': 0.73, 'symbol': 'Bs.'},
            'COP': {'name': 'PESO COLOMBIANO', 'rate': 0.0013, 'symbol': '$'},
        }

        # Layout em 3 colunas
        col_definitions = st.columns(3)
        # Repete a lista de colunas para criar um grid
        cols = col_definitions * (len(rates) // 3 + 1) 

        for i, (code, data) in enumerate(rates.items()):
            with cols[i]:
                converted_value = balance / data['rate']
                # Alterna as cores para variedade visual
                color = 'var(--accent-color-1)' if i % 2 == 0 else 'var(--accent-color-2)'
                st.markdown(f"""
                <div class='liquid-card' style='text-align:center;'>
                    <div class='hero-label'>{data['name']} ({code})</div>
                    <div style='font-size:1.8rem; font-weight:800; color:{color}; font-family: "JetBrains Mono", monospace;'>
                        {data['symbol']} {converted_value:,.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # --- ABA 5: PERFIL ---
    with t_prof:
        st.markdown(f"### {t('avatar_builder')}")

        # Layout: Coluna para o preview, coluna para as opções
        col_preview, col_options = st.columns([1, 1.5])

        with col_options:
            with st.form("avatar_form"):
                # Carrega a configuração atual
                raw_config = st.session_state.get('user_avatar_config', 'default,default,default')
                if not isinstance(raw_config, str): raw_config = 'default,default,default'
                
                current_config = raw_config.split(',')
                if len(current_config) != 3: current_config = ['default', 'default', 'default']
                
                # Seletores para cada parte do avatar
                face_options = get_avatar_part_names('face')
                hair_options = get_avatar_part_names('hair')
                clothes_options = get_avatar_part_names('clothes')

                # Índices seguros (se a opção salva não existir mais, usa a primeira/default)
                idx_face = face_options.index(current_config[0]) if current_config[0] in face_options else 0
                idx_hair = hair_options.index(current_config[1]) if current_config[1] in hair_options else 0
                idx_clothes = clothes_options.index(current_config[2]) if current_config[2] in clothes_options else 0

                selected_face = st.selectbox(t('face'), face_options, index=idx_face)
                selected_hair = st.selectbox(t('hair'), hair_options, index=idx_hair)
                selected_clothes = st.selectbox(t('clothes'), clothes_options, index=idx_clothes)

                if st.form_submit_button(f"💾 {t('save_avatar')}", use_container_width=True):
                    new_config_string = f"{selected_face},{selected_hair},{selected_clothes}"
                    
                    # Atualiza o banco de dados
                    run_query("UPDATE users SET avatar_config=:config WHERE id=:id", 
                              {'config': new_config_string, 'id': st.session_state.user_id}, commit=True)
                    
                    # Atualiza o estado da sessão
                    st.session_state.user_avatar_config = new_config_string
                    
                    st.toast("Avatar salvo com sucesso! ✨")
                    time.sleep(0.5)
                    st.rerun()

        with col_preview:
            st.markdown("<div style='display: flex; justify-content: center; align-items: center; height: 100%;'>", unsafe_allow_html=True)
            st.markdown(render_avatar(st.session_state.user_avatar_config, size=200), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"##### {t('theme_select')}")
        theme_names = {k: v['name'] for k, v in THEMES.items()}
        current_theme_key = st.session_state.get('user_theme', 'default')
        if current_theme_key not in theme_names: current_theme_key = 'default'
        current_theme_index = list(theme_names.keys()).index(current_theme_key)
        selected_theme_name = st.selectbox(label=t('theme_select'), options=list(theme_names.values()), index=current_theme_index, label_visibility="collapsed", key="kid_theme_selector")
        selected_theme_key = [k for k, v in theme_names.items() if v == selected_theme_name][0]
        if selected_theme_key != current_theme_key:
            st.session_state.user_theme = selected_theme_key
            run_query("UPDATE users SET theme=:theme WHERE id=:id", {'theme': selected_theme_key, 'id': st.session_state.user_id}, commit=True)
            st.toast(t('theme_changed'))
            time.sleep(0.5)
            st.rerun()

        st.markdown("---")
        st.markdown(f"##### {t('bg_image_label')}")
        
        uploaded_file = st.file_uploader(
            t('bg_image_label'), 
            type=['png', 'jpg', 'jpeg', 'gif', 'webp'], 
            label_visibility="collapsed",
            key="bg_uploader_kid"
        )

        if uploaded_file is not None:
            import base64
            import io
            from PIL import Image
            
            # Otimização de Imagem: Redimensionar e Comprimir para evitar instabilidade
            image = Image.open(uploaded_file)
            if image.mode in ('RGBA', 'P'): image = image.convert('RGB')
            image.thumbnail((1920, 1080)) # Limita a Full HD
            
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=70) # Comprime para JPEG leve
            
            base64_encoded = base64.b64encode(buffered.getvalue()).decode()
            data_uri = f"data:image/jpeg;base64,{base64_encoded}"

            run_query("UPDATE users SET background_url=:bg WHERE id=:id", {'bg': data_uri, 'id': st.session_state.user_id}, commit=True)
            st.session_state.user_background = data_uri
            st.toast(t('bg_updated'))
            time.sleep(0.5)
            st.rerun()

        if st.session_state.get('user_background'):
            if st.button(f"🗑️ {t('remove_bg')}", use_container_width=True, key="remove_bg_kid"):
                run_query("UPDATE users SET background_url=NULL WHERE id=:id", {'id': st.session_state.user_id}, commit=True)
                st.session_state.user_background = None
                st.toast(t('bg_removed'))
                time.sleep(0.5)
                st.rerun()

    # Rodapé Institucional
    st.markdown(f"<div style='text-align:center; color:#e0e0e0; opacity:0.5; font-size:0.6rem; margin-top:50px;'>BANCO RIPARITECH • v14.1 PREMIUM</div>", unsafe_allow_html=True)
