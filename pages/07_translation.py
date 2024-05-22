import requests
import streamlit as st

st.title("翻訳")
# DeepLのAPIキーを設定
api_key = st.secrets["deepl"]["api_key"]

option = st.selectbox(
    '何語に翻訳しますか？',
    ('日本語', 'English','华语')
)
lang_dict = {
    "日本語": "JA",
    "English": "EN",
    "华语": "ZH"
}
lang = lang_dict.get(option)

# 翻訳関数の定義
def translate_text(text, target_language=lang):
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": api_key,
        "text": text,
        "target_lang": target_language
    }
    
    response = requests.post(url, data=params)
    
    # レスポンスのステータスコードを確認
    if response.status_code != 200:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
    
    try:
        result = response.json()
        return result["translations"][0]["text"]
    except requests.exceptions.JSONDecodeError:
        raise Exception("Failed to decode JSON response: " + response.text)

# 翻訳の実行
text = st.text_input('翻訳したい文章を入力してください')
try:
    translated_text = translate_text(text)
    st.write(translated_text)
except Exception as e:
    st.write('入力してください')
    
