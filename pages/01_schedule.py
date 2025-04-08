import streamlit as st
import pandas as pd
import datetime




sheet = {
    "時間": ["8:45~10:15", "10:30~12:00", "13:15~14:45", "15:00~16:30", "16:45~18:15"],
    "月": ["確率論基礎", "日本国憲法", "機械設計制作", None, None],
    "火": [None, "都市空間論", None, "振動波動論", None],
    "水": ["材料力学", "卓球", None, None, None],
    "木": [None, None, "ベクトル解析", None, None],
    "金": ["熱力学", None, None, "シェイクスピア", None]
}


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
