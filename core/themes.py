# -*- coding: utf-8 -*-

THEMES = {
    'default': {
        'name': 'Obsidian (Padrão)',
        'css': """
            :root {
                --accent-color-1: #00d2ff;
                --accent-color-2: #3a7bd5;
                --accent-color-3: #ffffff;
                --accent-color-4: #000000;
            }
            .stApp { background: radial-gradient(circle at 50% -20%, #1a1a2e 0%, #020203 80%) !important; }
        """
    },
    'cyberpunk': {
        'name': 'Cyberpunk Neon',
        'css': """
            :root {
                --accent-color-1: #ff00ff;
                --accent-color-2: #00ffff;
                --accent-color-3: #f0f0f0;
                --accent-color-4: #121212;
            }
            .stApp { background: radial-gradient(circle at 50% -20%, #2b002b 0%, #050505 80%) !important; }
        """
    },
    'nature': {
        'name': 'Floresta Mística',
        'css': """
            :root {
                --accent-color-1: #00ff87;
                --accent-color-2: #60efff;
                --accent-color-3: #ffffff;
                --accent-color-4: #002200;
            }
            .stApp { background: radial-gradient(circle at 50% -20%, #0f2027 0%, #203a43 80%) !important; }
        """
    },
    'sunset': {
        'name': 'Pôr do Sol',
        'css': """
            :root {
                --accent-color-1: #ff512f;
                --accent-color-2: #dd2476;
                --accent-color-3: #ffffff;
                --accent-color-4: #2e0e0e;
            }
            .stApp { background: radial-gradient(circle at 50% -20%, #2c3e50 0%, #000000 80%) !important; }
        """
    },
    'ocean': {
        'name': 'Profundezas do Oceano',
        'css': """
            :root {
                --accent-color-1: #2b5876;
                --accent-color-2: #4e4376;
                --accent-color-3: #e0e0e0;
                --accent-color-4: #000011;
            }
            .stApp { background: radial-gradient(circle at 50% -20%, #141e30 0%, #243b55 80%) !important; }
        """
    }
}

def get_theme_css(theme_key):
    """Retorna o CSS específico do tema ou o default se não encontrado"""
    if theme_key not in THEMES:
        theme_key = 'default'
    return THEMES[theme_key]['css']