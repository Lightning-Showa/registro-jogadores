import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import base64
import json

# Configurações do Discord OAuth
CLIENT_ID = st.secrets["DISCORD"]["CLIENT_ID"]
CLIENT_SECRET = st.secrets["DISCORD"]["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["DISCORD"]["REDIRECT_URI"]

# IDs dos administradores
ADMIN_IDS = ["450677997184221185", "414636718235320341", "238847241240969227", 
            "1265190976465535010", "277048408689213440", "1240788028352495668"]

# Carrega dados
if 'df' not in st.session_state:
    try:
        st.session_state.df = pd.read_csv("jogadores.csv")
    except:
        st.session_state.df = pd.DataFrame(columns=["Nick", "IP", "Classe"])

CLASSES_DISPONIVEIS = [
    "Main Tank", "Off Tank", "Arcano Elevado", "Arcano Silence",
    "Main Healer", "Raiz Férrea", "Quebra Reinos", "Incubus",
    "Bruxo", "Frost", "Fire", "Águia", "X Bow", "Scout", "Roletroll"
]

def pagina_publica():
    st.title("🎮 Registro de Jogadores")
    with st.form("registro_form"):
        nick = st.text_input("Nick no Jogo", max_chars=20)
        ip = st.number_input("Item Power (IP)", min_value=0)
        classe = st.selectbox("Classe", CLASSES_DISPONIVEIS)
        
        if st.form_submit_button("Registrar"):
            if nick in st.session_state.df["Nick"].values:
                st.error("❌ Este nick já está registrado!")
            else:
                novo_jogador = pd.DataFrame([[nick, ip, classe]], columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, novo_jogador], ignore_index=True)
                st.session_state.df.to_csv("jogadores.csv", index=False)
                st.success("✅ Registro concluído!")
                st.rerun()

def pagina_admin():
    st.title("👑 Painel Administrativo")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        classe_filtro = st.selectbox("Filtrar por Classe", ["Todas"] + CLASSES_DISPONIVEIS)
    with col2:
        ip_minimo = st.slider("IP Mínimo", 0, 2000, 0)
    
    # Aplica filtros
    dados_filtrados = st.session_state.df.copy()
    if classe_filtro != "Todas":
        dados_filtrados = dados_filtrados[dados_filtrados["Classe"] == classe_filtro]
    dados_filtrados = dados_filtrados[dados_filtrados["IP"] >= ip_minimo]
    
    # Ordena e exibe
    dados_filtrados = dados_filtrados.sort_values(by=["Classe", "IP"], ascending=[True, False])
    st.dataframe(dados_filtrados)
    
    fig = px.pie(dados_filtrados, names="Classe", title="Distribuição por Classe")
    st.plotly_chart(fig, use_container_width=True)
    
    # Ferramentas admin
    with st.expander("⚙️ Gerenciar Jogadores"):
        jogadores_remover = st.multiselect("Selecione jogadores para remover", st.session_state.df["Nick"])
        if st.button("Remover Selecionados"):
            st.session_state.df = st.session_state.df[~st.session_state.df["Nick"].isin(jogadores_remover)]
            st.session_state.df.to_csv("jogadores.csv", index=False)
            st.success(f"✅ {len(jogadores_remover)} jogadores removidos!")
            st.rerun()

# Implementação manual do OAuth2
def verificar_login():
    if 'discord_user' not in st.session_state:
        query_params = st.experimental_get_query_params()
        
        # Se recebemos o código de autorização
        if 'code' in query_params:
            code = query_params['code'][0]
            
            # Troca o código por um token de acesso
            data = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'scope': 'identify'
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
            token_data = response.json()
            
            if 'access_token' in token_data:
                # Obtém informações do usuário
                headers = {
                    'Authorization': f'Bearer {token_data["access_token"]}'
                }
                user_response = requests.get('https://discord.com/api/users/@me', headers=headers)
                user_data = user_response.json()
                
                if 'id' in user_data:
                    st.session_state.discord_user = user_data
                    st.experimental_set_query_params()
                    st.rerun()
                else:
                    st.error("Falha ao obter informações do usuário")
            else:
                st.error("Falha na autenticação: " + token_data.get('error', 'Erro desconhecido'))
        
        # Se não está logado, mostra o botão de login
        else:
            auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
            st.markdown(f'[Login com Discord]({auth_url})', unsafe_allow_html=True)
            return False
        
    return True

# Página principal
if verificar_login():
    user_id = st.session_state.discord_user['id']
    if str(user_id) in ADMIN_IDS:
        pagina_admin()
    else:
        pagina_publica()
else:
    pagina_publica()
