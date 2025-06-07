import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Registro de Jogadores", page_icon="🎮")
st.title("🎮 Registro de Jogadores")

# Carrega ou cria o arquivo de dados
try:
    df = pd.read_csv("jogadores.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=["Nick", "IP", "Classe"])

# Classes e limites (personalize conforme sua necessidade)
CLASSES_DISPONIVEIS = [
    "Main Tank", "Off Tank", "Arcano Elevado", "Arcano Silence",
    "Main Healer", "Raiz Férrea", "Quebra Reinos", "Incubus",
    "Bruxo", "Frost", "Fire", "Águia", "X Bow", "Scout", "Roletroll"
]

LIMITES_CLASSE = {
    "Raiz Férrea": 3,
    "X Bow": 4,
    # Outras classes não têm limite (podem ser adicionadas aqui se necessário)
}

# Função para validar e adicionar jogador
def adicionar_jogador(nick, ip, classe):
    global df  # 🔥 Declaração global ANTES de usar df!

    # Verifica se o Nick já existe
    if nick in df["Nick"].values:
        return "❌ Este Nick já está registrado!"
    
    # Verifica se a classe está dentro do limite
    if classe in LIMITES_CLASSE:
        jogadores_da_classe = df[df["Classe"] == classe].shape[0]
        if jogadores_da_classe >= LIMITES_CLASSE[classe]:
            return f"❌ Limite de {LIMITES_CLASSE[classe]} jogadores para {classe} já foi atingido!"
    
    # Adiciona o jogador ao DataFrame
    novo_jogador = pd.DataFrame([[nick, ip, classe]], columns=df.columns)
    df = pd.concat([df, novo_jogador], ignore_index=True)
    df.to_csv("jogadores.csv", index=False)
    return "✅ Jogador registrado com sucesso!"

# Formulário interativo
with st.form("form_jogador"):
    st.subheader("Adicionar Novo Jogador")
    
    nick = st.text_input("Nick do Jogador", max_chars=20)
    ip = st.number_input("Item Power (IP)", min_value=0, max_value=9999)
    classe = st.selectbox("Classe", CLASSES_DISPONIVEIS)
    
    if st.form_submit_button("Registrar"):
        mensagem = adicionar_jogador(nick, ip, classe)
        st.success(mensagem if "✅" in mensagem else mensagem)

# Mostra a tabela de jogadores cadastrados
st.subheader("Jogadores Registrados")
st.dataframe(df)

# Botão para baixar os dados em CSV
st.download_button(
    label="📥 Baixar Dados (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="jogadores.csv",
    mime="text/csv"
)
