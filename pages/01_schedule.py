import streamlit as st
import pandas as pd
import datetime



# Google Sheetを開く
sheet =  {
    "時間": ["8:45~10:15", "10:30~12:00", "13:15~14:45", "15:00~16:30", "16:45~18:15"],
    "月": ["情報基礎演習", None, "基礎化学実験", "基礎化学実験", None],
    "火": [None, "法学", "線形代数学(講義)", "自然現象と数学", None],
    "水": [None, None, "微分積分学(講義)", "基礎物理化学", "物理工学総論"],
    "木": ["物理学基礎論", "中国語", "英語ライリス", None, None],
    "金": ["数学演義", "英語リーディング", "中国語", None, "憲法上の権利"]
}

# Google SheetをPandas DataFrameに読み込む
def load_data():
    data = pd.DataFrame(sheet)
    data.index = data.index+1
    return data

now = datetime.datetime.now()

# 曜日を取得して文字列としてフォーマット
weekdays = ["月", "火", "水", "木", "金", "土", "日"]
weekday_str = ["時間",weekdays[now.weekday()]]
data = load_data()
# Streamlitアプリの構築
st.title('時間割')
st.write(data)