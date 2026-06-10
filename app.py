
import streamlit as st
import os
import subprocess
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

st.set_page_config(page_title="RPA Monitor", layout="wide")

# Atualiza a app a cada 2 segundos
st_autorefresh(interval=2000, key="datarefresh")

st.title("🤖 RPA SYSTEM")

DATA_DIR = "data"
STATUS_FILE = f"{DATA_DIR}/status.txt"
LIVE_IMG = f"{DATA_DIR}/live.png"
ERRO_IMG = f"{DATA_DIR}/erro_debug.png"
EXCEL_FILE = f"{DATA_DIR}/posts_extraidos.xlsx"
LOG_FILE = f"{DATA_DIR}/processo.log"

def inicializar_consola():
    if "logs" not in st.session_state:
        st.session_state.logs = ["> SYSTEM INITIALIZED... READY"]

    # CSS Futurista Injetado
    st.markdown("""
        <style>
        .stConsole {
            background-color: #050a0e;
            border: 2px solid #ff3131;
            border-radius: 5px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            box-shadow: inset 0 0 10px #00f2ff22, 0 0 15px #00f2ff44;
            display: flex;
            flex-direction: column-reverse; /* Mantém os logs novos no topo ou fundo */
        }
        .log-entry {
            color: #e0e0e0;
            font-size: 11px;
            margin-bottom: 5px;
            border-left: 3px solid #00f2ff;
            padding-left: 10px;
            text-shadow: 0 0 5px #00f2ff;
            animation: glitch 0.3s ease-in-out;
        }
        .log-time { color: #555; margin-right: 8px; }
        @keyframes glitch {
            0% { transform: translateX(-2px); opacity: 0.5; }
            100% { transform: translateX(0); opacity: 1; }
        }
                
        /* Container das Tabs */
        button[data-baseweb="tab"] {
            background-color: #1a1a1a !important; /* Cinza muito escuro */
            border: 1px solid #333 !important; /* Borda grafite subtil */
            border-radius: 4px 4px 0px 0px !important;
            color: #666 !important; /* Texto cinza apagado */
            font-family: 'Courier New', monospace !important;
            margin-right: 4px !important;
            margin-top:10px;    
            padding: 10px 20px !important;
            transition: all 0.2s ease-in-out !important;
            text-transform: uppercase; /* Estilo comando */
        }

        /* Tab Selecionada (Ativa) - Efeito Aço */
        button[aria-selected="true"] {
            background-color: #333 !important; /* Cinza médio */
            border: 1px solid #888 !important; /* Borda clara (aço) */
            color: #ffffff !important; /* Texto branco puro para contraste */
            box-shadow: none !important; /* Remove qualquer neon */
        }

        /* Tab quando passas o rato (Hover) */
        button[data-baseweb="tab"]:hover {
            color: #bbbbbb !important;
            border-color: #666 !important;
            background-color: #252525 !important;
        }

        /* Linha de base que une as tabs */
        div[data-baseweb="tab-list"] {
            gap: 0px !important;
            background-color: transparent !important;
            border-bottom: 2px solid #333 !important; /* Linha divisória industrial */
        }

        /* Ajuste opcional: Remove a linha vermelha/colorida padrão do Streamlit */
        div[data-testid="stMarker"] {
            display: none !important;
        }
                
        /* Barra de Rodapé Fixa */
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #1a1a1a; /* Cinza escuro industrial */
            color: #888888; /* Cinza médio */
            text-align: center;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            border-top: 1px solid #333; /* Linha subtil */
            z-index: 999;
        }

        .footer a {
            color: #ffffff; /* Site em branco para destaque */
            text-decoration: none;
            font-weight: bold;
        }

        .footer a:hover {
            color: #bbbbbb;
        }

        /* Espaço extra no fundo para o conteúdo não ficar tapado pela barra */
        .main .block-container {
            padding-bottom: 60px !important;
        }
                
        /* Fundo estilizado para os Headers (H2) */
        h2 {
            background-color: #1a1a1a !important; /* Cinza quase preto */
            color: #d1d1d1 !important;           /* Letras em cinza claro */
            padding: 10px 15px !important;       /* Espaço interno */
            border-left: 5px solid #888 !important; /* "Ripa" lateral em aço */
            border-radius: 0px 4px 4px 0px !important;
            font-family: 'Courier New', monospace !important;
            font-size: 18px !important;
            text-transform: uppercase;           /* Sempre em maiúsculas */
            letter-spacing: 2px;                 /* Espaçamento técnico */
            width: 100%;                         /* Ocupa a largura total da coluna */
        }        

        .linha-estilizada {
            /* Degradê que simula metal escovado/aço */
            background: linear-gradient(180deg, #111 0%, #444 50%, #111 100%);
            width: 4px;             /* Espessura da haste */
            height: 90vh;           /* Ocupa 90% da altura da página */
            margin: 0 auto;
            border-radius: 2px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.5); /* Sombra para dar relevo */
            position: relative;  
        }

        /* Detalhe: Pequenos parafusos ou marcas técnicas na linha */
        .linha-estilizada::before {
            content: "";
            position: absolute;
            top: 10%; left: -2px; width: 8px; height: 2px;
            background: #888; /* Marca de parafuso */
            box-shadow: 0 100px 0 #888, 0 200px 0 #888, 0 300px 0 #888;
        }  

        /* 3. Remove o espaço extra que o título ou o primeiro elemento cria */
        #root > div:nth-child(1) > div > div > div > div > section > div {
            padding-top: 0rem !important;
        }                                           

        </style>
    """, unsafe_allow_html=True)

def escrever_log(mensagem):
    hora = datetime.now().strftime("%H:%M:%S")
    nova_linha = f"<div class='log-entry'><span class='log-time'>[{hora}]</span> {mensagem.upper()}</div>"
    st.session_state.logs.insert(0, nova_linha) # Adiciona no início


col1, col_sep, col2 = st.columns([1, 0.1, 2]) 

# ==========================
# COLUNA ESQUERDA — CONTROLOS
# ==========================
with col1:

    st.header("⚙️ Control Painel")

    em_execucao = os.path.exists(STATUS_FILE) and "A executar" in open(STATUS_FILE).read()

    inicializar_consola()

    if st.button("📎 LAUNCH ROBOT SYSTEM", disabled=em_execucao):
        st.info("Robot em execução...")

        # Limpeza de estado anterior
        for f in [ERRO_IMG, LIVE_IMG, STATUS_FILE, EXCEL_FILE, LOG_FILE]:
            if os.path.exists(f):
                os.remove(f)
        
        # 2. Limpa a variável de estado do Streamlit (se estiveres a usar)
        if "logs" in st.session_state:
            st.session_state.logs = []

        # Limpa o log para começar do zero
        with open(LOG_FILE, "w") as f: f.write("🚀 Iniciando...\n")

        # Marca execução
        with open(STATUS_FILE, "w") as f:
            f.write("A executar...")

        # Dispara o robô com username
        subprocess.Popen(
            ["python", "main.py"]
        )

    st.subheader("📟 Robot terminal")
    # log_container = st.container(height=300, border=True)

    # Área onde os logs aparecem
    log_container = st.empty()
    with log_container.container():
        logs_html = f"<div class='stConsole'>{''.join(st.session_state.logs)}</div>"
        st.markdown(logs_html, unsafe_allow_html=True)

    
    # 2. Lógica de leitura simples
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            conteudo = f.readlines()
            # Coloca a linha mais recente no TOPO
            # Assim o "scroll" é natural para o utilizador
            for linha in conteudo:
                escrever_log(linha.strip())

    else:
        escrever_log(f"🕒 Aguardando início do processo...")

    st.divider()

    st.subheader("🛰️ State")

    # Estado textual
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            status = f.read()

        if "Sucesso" in status:
            st.success(status)
        elif "Erro" in status or "Falha" in status:
            st.error(status)
        else:
            st.warning(status)

with col_sep:
    # Esta coluna apenas desenha a linha
    st.markdown('<div class="linha-estilizada"></div>', unsafe_allow_html=True)

# ==========================
# COLUNA DIREITA — MONITOR
# ==========================
with col2:
    
    st.header("👁️‍🗨️ ROBOT VIEW")

     # Criar as Tabs dentro da coluna 2
    tab_visao, tab_dados = st.tabs(["📸 SCREEN", "📊 DATA RECORDS"])

     # --- TAB 1: VISUALIZAÇÃO EM TEMPO REAL ---
    with tab_visao:

        # Estado inicial
        if not os.path.exists(LIVE_IMG) and not os.path.exists(ERRO_IMG):
            with st.spinner("O robô está a preparar o browser ou a carregar o Lavbella..."):
                pass
        
        if os.path.exists(LIVE_IMG):
            st.image(
                LIVE_IMG,
                caption="Última captura do robô"
            )

        # Screenshot de erro
        if os.path.exists(ERRO_IMG):
            st.error("❌ Erro detetado na última execução")
            st.image(ERRO_IMG)

    # --- TAB 2: TABELA DE DADOS (EXCEL) ---
    with tab_dados:

        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            st.dataframe(df, height=500)
        else:
            st.info("Ainda não existem dados extraídos.")

st.markdown(
    """
    <div class="footer">
        DEVELOPED BY <a href="https://lavbella.com" target="_blank">Lavbella.com</a> | © 2026 ROBOT_SYSTEM_V1
    </div>
    """, 
    unsafe_allow_html=True
)
   


