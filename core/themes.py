# -*- coding: utf-8 -*-

THEMES = {
    'default': {
        'name': 'Cyber Blue',
        'accent1': '#00f2ff',
        'accent2': '#7000ff',
        'accent3': '#999',
        'accent4': '#1a1a1a',
    },
    'neon_pink': {
        'name': 'Neon Pink',
        'accent1': '#ff00ff',
        'accent2': '#ff6ec7',
        'accent3': '#ff6ec7',
        'accent4': '#1a1a1a',
    },
    'emerald_green': {
        'name': 'Emerald Green',
        'accent1': '#00ff7f',
        'accent2': '#00c853',
        'accent3': '#00c853',
        'accent4': '#ffffff',
    },
    'solar_orange': {
        'name': 'Solar Orange',
        'accent1': '#ffab00',
        'accent2': '#ff6d00',
        'accent3': '#ffab00',
        'accent4': '#1a1a1a',
    }
}

def get_theme_css(theme_name='default'):
    """Gera o bloco CSS com as variáveis de cor para o tema selecionado."""
    theme = THEMES.get(theme_name, THEMES['default'])
    return f"""
    :root {{
        --accent-color-1: {theme['accent1']};
        --accent-color-2: {theme['accent2']};
        --accent-color-3: {theme['accent3']};
        --accent-color-4: {theme['accent4']};
    }}
    """