import streamlit as st
import pandas as pd
import tweepy
import io

# --- Idiomas disponibles ---
translations = {
    "en": {
        "title": "🐦 Multi-Account Twitter Bot",
        "description": "Post tweets from multiple Twitter/X accounts. Choose how you want to provide your credentials and paste your tweets.",
        "lang_label": "🌐 Select Language",
        "tab_upload": "📁 Upload CSV File",
        "tab_paste": "📝 Paste CSV Text",
        "upload_sub": "Upload a CSV file with your Twitter credentials",
        "upload_instructions": "CSV must include the columns: api_key, api_secret, access_token, access_secret",
        "paste_sub": "Paste your credentials as raw CSV text",
        "textarea_placeholder": "api_key,api_secret,access_token,access_secret\nKEY1,SECRET1,TOKEN1,ACCESS_SECRET1",
        "tweet_header": "✍️ Write your Tweets",
        "tweet_area_label": "Enter one tweet per line:",
        "tweet_preview": "**Tweets Preview:**",
        "post_button": "🚀 Post Tweets",
        "no_creds": "⚠️ Please provide valid credentials above.",
        "post_success": "✅ Posted {count} tweets from {accounts} accounts.",
        "modal_title": "How to Use This App",
        "modal_body": """
1. Choose your language using the dropdown above.
2. Provide your Twitter API credentials via a CSV **file** or by pasting the text.
3. Write one tweet per line.
4. Click **Post Tweets** to publish from all accounts.
        """,
        "modal_close": "Close Guide"
    },
    "es": {
        "title": "🐦 Bot de Twitter Multi-Cuenta",
        "description": "Publica tweets desde varias cuentas de Twitter/X. Elige cómo ingresar tus credenciales y escribe tus tweets.",
        "lang_label": "🌐 Selecciona idioma",
        "tab_upload": "📁 Subir archivo CSV",
        "tab_paste": "📝 Pegar texto CSV",
        "upload_sub": "Sube un archivo CSV con tus credenciales de Twitter",
        "upload_instructions": "El CSV debe incluir las columnas: api_key, api_secret, access_token, access_secret",
        "paste_sub": "Pega tus credenciales como texto CSV sin procesar",
        "textarea_placeholder": "api_key,api_secret,access_token,access_secret\nKEY1,SECRET1,TOKEN1,ACCESS_SECRET1",
        "tweet_header": "✍️ Escribe tus Tweets",
        "tweet_area_label": "Ingresa un tweet por línea:",
        "tweet_preview": "**Vista previa de tweets:**",
        "post_button": "🚀 Publicar Tweets",
        "no_creds": "⚠️ Primero debes cargar credenciales válidas.",
        "post_success": "✅ Se publicaron {count} tweets desde {accounts} cuentas.",
        "modal_title": "¿Cómo usar esta app?",
        "modal_body": """
1. Elige tu idioma en el menú superior.
2. Ingresa las credenciales vía archivo **CSV** o pegando texto.
3. Escribe un tweet por línea.
4. Haz clic en **Publicar Tweets** para enviarlos desde todas las cuentas.
        """,
        "modal_close": "Cerrar Guía"
    },
    "pt": {
        "title": "🐦 Bot do Twitter Multi-Conta",
        "description": "Publique tweets de várias contas do Twitter/X. Escolha como fornecer suas credenciais e escreva seus tweets.",
        "lang_label": "🌐 Escolha o idioma",
        "tab_upload": "📁 Enviar arquivo CSV",
        "tab_paste": "📝 Colar texto CSV",
        "upload_sub": "Envie um arquivo CSV com suas credenciais do Twitter",
        "upload_instructions": "O CSV deve conter as colunas: api_key, api_secret, access_token, access_secret",
        "paste_sub": "Cole suas credenciais como texto CSV puro",
        "textarea_placeholder": "api_key,api_secret,access_token,access_secret\nKEY1,SECRET1,TOKEN1,ACCESS_SECRET1",
        "tweet_header": "✍️ Escreva seus Tweets",
        "tweet_area_label": "Digite um tweet por linha:",
        "tweet_preview": "**Pré-visualização dos tweets:**",
        "post_button": "🚀 Publicar Tweets",
        "no_creds": "⚠️ Forneça credenciais válidas acima.",
        "post_success": "✅ Publicados {count} tweets de {accounts} contas.",
        "modal_title": "Como usar este aplicativo",
        "modal_body": """
1. Escolha seu idioma no menu acima.
2. Forneça credenciais via arquivo **CSV** ou colando texto.
3. Escreva um tweet por linha.
4. Clique em **Publicar Tweets** para enviar de todas as contas.
        """,
        "modal_close": "Fechar Guia"
    }
}

# --- Language Selection ---
lang = st.selectbox("🌐 Select Language / Selecciona idioma / Escolha o idioma", ["en", "es", "pt"])
T = translations[lang]

st.title(T["title"])
st.markdown(T["description"])

# --- Modal Help Overlay ---
if "show_help" not in st.session_state:
    st.session_state.show_help = True

if st.session_state.show_help:
    with st.expander(f"ℹ️ {T['modal_title']}", expanded=True):
        st.markdown(T["modal_body"])
        if st.button(f"❌ {T['modal_close']}"):
            st.session_state.show_help = False

# --- Tabs for credential input ---
tab1, tab2 = st.tabs([T["tab_upload"], T["tab_paste"]])
credentials = []

with tab1:
    st.subheader(T["upload_sub"])
    st.caption(T["upload_instructions"])
    file = st.file_uploader("CSV", type="csv")
    if file:
        try:
            df = pd.read_csv(file)
            required = {"api_key", "api_secret", "access_token", "access_secret"}
            if not required.issubset(df.columns):
                st.error(T["upload_instructions"])
            else:
                credentials = df.to_dict(orient="records")
                st.success(f"✅ {len(credentials)} loaded.")
        except Exception as e:
            st.error(str(e))

with tab2:
    st.subheader(T["paste_sub"])
    text = st.text_area("CSV", placeholder=T["textarea_placeholder"], height=150)
    if text.strip():
        try:
            df = pd.read_csv(io.StringIO(text.strip()))
            required = {"api_key", "api_secret", "access_token", "access_secret"}
            if not required.issubset(df.columns):
                st.error(T["upload_instructions"])
            else:
                credentials = df.to_dict(orient="records")
                st.success(f"✅ {len(credentials)} loaded from text.")
        except Exception as e:
            st.error(str(e))

# --- Tweet input ---
st.header(T["tweet_header"])
tweet_input = st.text_area(T["tweet_area_label"], height=200)
tweets = [line.strip() for line in tweet_input.splitlines() if line.strip()]

if tweets:
    st.markdown(T["tweet_preview"])
    for tweet in tweets:
        st.markdown(f"- {tweet}")

    if st.button(T["post_button"]):
        if not credentials:
            st.warning(T["no_creds"])
        else:
            total = 0
            for cred in credentials:
                try:
                    auth = tweepy.OAuth1UserHandler(
                        cred["api_key"],
                        cred["api_secret"],
                        cred["access_token"],
                        cred["access_secret"]
                    )
                    api = tweepy.API(auth)

                    for tweet in tweets:
                        api.update_status(tweet)
                        total += 1
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            st.success(T["post_success"].format(count=total, accounts=len(credentials)))
else:
    st.info("⬆️ " + T["tweet_area_label"])
