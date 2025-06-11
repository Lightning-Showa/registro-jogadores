import streamlit as st
import pandas as pd
from st_oauth import OAuth2Component

# Tentar importar Plotly com fallback
try:
    import plotly.express as px
    PLOTLY_INSTALLED = True
except ImportError:
    PLOTLY_INSTALLED = False
    st.warning("Plotly não instalado. Gráficos serão desabilitados.")

# Configurações (REMOVA SUAS CHAVES ANTES DE COMPARTILHAR!)
CLIENT_ID = st.secrets.get("discord", {}).get("CLIENT_ID", "1380981932107759666")
CLIENT_SECRET = st.secrets.get("discord", {}).get("CLIENT_SECRET", "vOg1cbkQvdXmS-QVQkzOx3KJH0nl9dWF")
REDIRECT_URI = "https://seu-app.streamlit.app"

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
    
    # Gráfico apenas se Plotly estiver instalado
    if PLOTLY_INSTALLED:
        fig = px.pie(dados_filtrados, names="Classe", title="Distribuição por Classe")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Instale o Plotly para ver os gráficos")
    
    # Ferramentas admin
    with st.expander("⚙️ Gerenciar Jogadores"):
        jogadores_remover = st.multiselect("Selecione jogadores para remover", st.session_state.df["Nick"])
        if st.button("Remover Selecionados"):
            st.session_state.df = st.session_state.df[~st.session_state.df["Nick"].isin(jogadores_remover)]
            st.session_state.df.to_csv("jogadores.csv", index=False)
            st.success(f"✅ {len(jogadores_remover)} jogadores removidos!")
            st.rerun()

# Configuração do OAuth2
oauth = OAuth2Component(
    CLIENT_ID,
    CLIENT_SECRET,
    "https://discord.com/api/oauth2/authorize",
    "https://discord.com/api/oauth2/token",
    "https://discord.com/api/oauth2/token",
    "https://discord.com/api/oauth2/token/revoke",
)

def verificar_login():
    if 'auth' not in st.session_state:
        try:
            auth_result = oauth.authorize_button(
                name="Login com Discord",
                icon="discord",
                redirect_uri=REDIRECT_URI,
                scope="identify",
                key="discord_login",
            )
            if auth_result:
                st.session_state.auth = auth_result
                st.rerun()
            return False
        except Exception as e:
            st.error(f"Erro no login: {str(e)}")
            return False
    return True

# Página principal
try:
    if verificar_login():
        user_id = st.session_state.auth["user"]["id"]
        if str(user_id) in ADMIN_IDS:
            pagina_admin()
        else:
            pagina_publica()
    else:
        pagina_publica()
except Exception as e:
    st.error(f"Ocorreu um erro: {str(e)}")
    st.info("Tente recarregar a página")
