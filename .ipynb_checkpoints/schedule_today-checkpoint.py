import streamlit as st
import pandas as pd
import datetime
from zoneinfo import ZoneInfo



# 時間割、場所、持ち物のデータを設定
sheet_sch = {
    "時間": ["8:45~10:15", "10:30~12:00", "13:15~14:45", "15:00~16:30", "16:45~18:15"],
    "月": [None, "日本語の時間表現の諸相", "物理学実験", "物理学実験", "言学Ⅱ"],
    "火": [None, None, "線形代数学(講義)", "裁判制度入門", None],
    "水": [None, None, "微分積分学(講義)", "基礎物理化学(量子論)", None],
    "木": ["物理学基礎論", "中国語", "英語ライリス", "情報基礎", "物理工学総論"],
    "金": ["数学演義", "英語リーディング", "中国語", None, None]
}

sheet_bel = {
    "持ち物(月)": [None, None, None, None, None],
    "持ち物(火)": [None, None, None, None, None],
    "持ち物(水)": [None, None, None, None, None],
    "持ち物(木)": [None, None, None, None, None],
    "持ち物(金)": [None, None, None, None, None]
}

sheet_pla = {
    "場所(月)": [None, "1共03", "2共 物理学実験室", "2共 物理学実験室", "共東21"],
    "場所(火)": [None, None, "共北32", "共西11", None],
    "場所(水)": [None, None, "共北32", "共北25", None],
    "場所(木)": ["4共21", "総人1305", "1共23", "工学部物理系校舎313", "総合研究3号館155"],
    "場所(金)": ["共北32", "共北3C", "4共33", None, None]
}

def load_sch():
    sch = pd.DataFrame(sheet_sch)
    sch.index = sch.index + 1
    return sch

def load_place():
    place = pd.DataFrame(sheet_pla)
    place.index = place.index + 1
    return place    

def load_bel():
    bel = pd.DataFrame(sheet_bel)
    bel.index = bel.index + 1
    return bel   

def next_class_info(sheet_sch, weekday_str,zone):
    now = datetime.datetime.now(ZoneInfo(zone))
    current_time = now.time()

    day_schedule = sheet_sch[weekday_str[1]]
    time_slots = sheet_sch["時間"]
    next_class_period = None
    next_index = len(day_schedule)

    for index, times in enumerate(time_slots):
        start_time_str, end_time_str = times.split('~')
        start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
        end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()

        if current_time > end_time:
            continue

        if start_time <= current_time <= end_time:
            next_index = index + 1
        elif current_time < start_time:
            next_index = index
            break

    while next_index < len(day_schedule) and day_schedule[next_index] is None:
        next_index += 1

    if next_index < len(day_schedule):
        next_class_period = next_index + 1
    else:
        return "今日の授業はこれで終わりです。"

    return next_class_period

# 曜日を取得して文字列としてフォーマット
zone = 'Asia/Tokyo'
now = datetime.datetime.now(ZoneInfo(zone))
weekdays = ["月", "火", "水", "木", "金", "土", "日"]
weekday_str = ["時間", weekdays[now.weekday()]]

# Streamlitアプリの構築
st.title('今日の時間割')
sch = load_sch()
pla = load_place()
bel = load_bel()

if weekdays[now.weekday()] in ['土', '日']:
    st.write("今日はおやすみ")
else:
    data = pd.concat([sch[weekday_str], pla[f'場所({weekdays[now.weekday()]})'], bel[f'持ち物({weekdays[now.weekday()]})']], axis=1)
    next_class_info = next_class_info(sheet_sch, weekday_str,zone)

    if isinstance(next_class_info, int):
        st.markdown(f'次の授業:**{next_class_info}**限 **{data.iloc[next_class_info-1,1]}**　場所:**{data.iloc[next_class_info-1,2]}**')
    else:
        st.markdown(next_class_info)

    st.write("今日の時間割")
    st.write(data)
    
