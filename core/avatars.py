# -*- coding: utf-8 -*-
import streamlit as st

# --- ASSETS SVG ---
# SVGs são definidos com um viewBox="0 0 100 100" para fácil dimensionamento e posicionamento.

AVATAR_PARTS = {
    'face': {
        'default': '<circle cx="50" cy="50" r="40" fill="#f0e4d4"/>', # Base skin tone
        'rosto_sorrindo': '<g><circle cx="50" cy="50" r="40" fill="#f0e4d4"/><path d="M 35 60 Q 50 75 65 60" stroke="black" fill="none" stroke-width="2"/><circle cx="40" cy="45" r="3"/><circle cx="60" cy="45" r="3"/></g>',
        'rosto_feliz': '<g><circle cx="50" cy="50" r="40" fill="#f0e4d4"/><path d="M 30 65 C 40 75, 60 75, 70 65" stroke="black" fill="white" stroke-width="2"/><path d="M 35 40 Q 40 35 45 40" stroke="black" fill="none" stroke-width="2"/><path d="M 55 40 Q 60 35 65 40" stroke="black" fill="none" stroke-width="2"/></g>',
    },
    'hair': {
        'default': '', # Calvo por padrão
        'cabelo_curto': '<path d="M 20 30 Q 50 10 80 30 L 80 40 Q 50 20 20 40 Z" fill="#3b3b3b"/>',
        'cabelo_longo': '<path d="M 20 30 Q 50 10 80 30 L 90 70 Q 50 80 10 70 Z" fill="#8d4925"/>',
        'topete': '<path d="M 35 25 Q 50 5 65 25 T 50 20 Z" fill="#e6c86e"/>',
    },
    'clothes': {
        'default': '<path d="M 25 85 L 75 85 L 70 95 L 30 95 Z" fill="#3a7bd5"/>', # Camiseta azul simples
        'camiseta_vermelha': '<path d="M 25 85 L 75 85 L 70 95 L 30 95 Z" fill="#ff4b4b"/>',
        'regata_verde': '<path d="M 30 85 L 70 85 L 65 95 L 35 95 Z" fill="#00ff87"/>',
    }
}

def get_avatar_part_names(part_type):
    """Retorna os nomes amigáveis para as partes do avatar."""
    return list(AVATAR_PARTS.get(part_type, {}).keys())

def render_avatar(config_string="default,default,default", size=100):
    """
    Renderiza um avatar SVG com base em uma string de configuração.
    A ordem de renderização é Rosto -> Roupa -> Cabelo.
    """
    if not config_string or len(config_string.split(',')) != 3:
        config_string = "default,default,default"
        
    face_key, hair_key, clothes_key = config_string.split(',')

    face_svg = AVATAR_PARTS['face'].get(face_key, AVATAR_PARTS['face']['default'])
    hair_svg = AVATAR_PARTS['hair'].get(hair_key, AVATAR_PARTS['hair']['default'])
    clothes_svg = AVATAR_PARTS['clothes'].get(clothes_key, AVATAR_PARTS['clothes']['default'])

    svg_code = f"""
    <svg width="{size}" height="{size}" viewBox="0 0 100 100" style="overflow: visible;">
        <g>
            {face_svg}
            {clothes_svg}
            {hair_svg}
        </g>
    </svg>
    """
    return svg_code