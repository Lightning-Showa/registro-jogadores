import streamlit as st
import pandas as pd
import plotly.express as px
from st_oauth import OAuth2Component  # Biblioteca para login com Discord

# Configurações do Discord OAuth
CLIENT_ID = "1380981932107759666"
CLIENT_SECRET = "vOg1cbkQvdXmS-QVQkzOx3KJH0nl9dWF"
AUTHORIZE_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"
REVOKE_URL = "https://discord.com/api/oauth2/token/revoke"
REDIRECT_URI = "https://seu-app.streamlit.app"  # Altere para sua URL

# IDs dos administradores (obtenha no Discord)
ADMIN_IDS = ["450677997184221185", "414636718235320341", "238847241240969227", "1265190976465535010", "277048408689213440", "1240788028352495668"]  # Substitua pelos IDs reais

# Carrega dados
@st.cache_data
def load_data():
    try:
        return pd.read_csv("jogadores.csv")
    except:
        return pd.DataFrame(columns=["Nick", "IP", "Classe"])

df = load_data()

# Classes disponíveis (personalize conforme necessário)
CLASSES_DISPONIVEIS = [
    "Main Tank", "Off Tank", "Arcano Elevado", "Arcano Silence",
    "Main Healer", "Raiz Férrea", "Quebra Reinos", "Incubus",
    "Bruxo", "Frost", "Fire", "Águia", "X Bow", "Scout", "Roletroll"
]

# Página Pública (para jogadores se registrarem)
def pagina_publica():
    st.title("🎮 Registro de Jogadores")
    with st.form("registro_form"):
        nick = st.text_input("Nick no Jogo", max_chars=20)
        ip = st.number_input("Item Power (IP)", min_value=0)
        classe = st.selectbox("Classe", CLASSES_DISPONIVEIS)
        
        if st.form_submit_button("Registrar"):
            if nick in df["Nick"].values:
                st.error("❌ Este nick já está registrado!")
            else:
                novo_jogador = pd.DataFrame([[nick, ip, classe]], columns=df.columns)
                global df
                df = pd.concat([df, novo_jogador], ignore_index=True)
                df.to_csv("jogadores.csv", index=False)
                st.success("✅ Registro concluído!")

# Página Admin (com filtros e visualização)
def pagina_admin():
    st.title("👑 Painel Administrativo")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        classe_filtro = st.selectbox("Filtrar por Classe", ["Todas"] + CLASSES_DISPONIVEIS)
    with col2:
        ip_minimo = st.slider("IP Mínimo", 0, 2000, 0)
    
    # Aplica filtros
    dados_filtrados = df.copy()
    if classe_filtro != "Todas":
        dados_filtrados = dados_filtrados[dados_filtrados["Classe"] == classe_filtro]
    dados_filtrados = dados_filtrados[dados_filtrados["IP"] >= ip_minimo]
    
    # Ordena por Classe e IP (decrescente)
    dados_filtrados = dados_filtrados.sort_values(by=["Classe", "IP"], ascending=[True, False])
    
    # Exibe tabela e gráfico
    st.dataframe(dados_filtrados)
    
    fig = px.pie(dados_filtrados, names="Classe", title="Distribuição por Classe")
    st.plotly_chart(fig, use_container_width=True)
    
    # Ferramentas admin
    with st.expander("⚙️ Gerenciar Jogadores"):
        jogadores_remover = st.multiselect("Selecione jogadores para remover", df["Nick"])
        if st.button("Remover Selecionados"):
            df = df[~df["Nick"].isin(jogadores_remover)]
            df.to_csv("jogadores.csv", index=False)
            st.success(f"✅ {len(jogadores_remover)} jogadores removidos!")

# Configuração do OAuth2
oauth = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL,
    TOKEN_URL,
    REVOKE_URL,
)

# Verificação de login
def verificar_login():
    if 'auth' not in st.session_state:
        # Cria botão de login
        auth_result = oauth.authorize_button(
            name="Login com Discord",
            icon="https://cdn-icons-png.flaticon.com/512/2111/2111370.png",
            redirect_uri=REDIRECT_URI,
            scope="identify",
            key="discord_login",
        )
        
        if auth_result:
            st.session_state.auth = auth_result
            st.rerun()
        return False
    return True

# Página principal
if verificar_login():
    user_id = st.session_state.auth["user"]["id"]
    
    if user_id in ADMIN_IDS:
        pagina_admin()
    else:
        pagina_publica()
else:
    pagina_publica()
