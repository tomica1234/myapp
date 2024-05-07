import streamlit as st
import streamlit_calendar as st_calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, WEEKLY, TH, TU, WE
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 認証情報の設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

# Google Sheetを開く
sheet = client.open("app").worksheet("calendar")

# Google SheetをPandas DataFrameに読み込む
def load_data():
    df= pd.DataFrame(sheet.get_all_values(),columns = ['date','start_time','end_time','purpose'])
    data = df[1:]
    data.index = data.index+1
    data.reset_index(drop=True, inplace=True)
    return data

# セッション状態に event_list を初期化
if 'event_list' not in st.session_state:
    st.session_state.event_list = []

st.title('カレンダー')

###ゴミ出し###
now = datetime.now()

this_month_start = datetime(now.year, now.month, 1)
next_month_start = this_month_start + relativedelta(months=+1)
two_months_later_start = next_month_start + relativedelta(months=+1)

wednesdays = list(rrule(freq=WEEKLY, dtstart=this_month_start, until=two_months_later_start, byweekday=WE))
wednesday_dates = [d.date() for d in wednesdays if d < two_months_later_start]

thursdays = list(rrule(freq=WEEKLY, dtstart=this_month_start, until=two_months_later_start, byweekday=TH))
thursday_dates = [d.date() for d in thursdays if d < two_months_later_start]

first_tuesdays = list(rrule(freq=MONTHLY, dtstart=this_month_start, until=two_months_later_start, byweekday=TU(1)))
third_tuesdays = list(rrule(freq=MONTHLY, dtstart=this_month_start, until=two_months_later_start, byweekday=TU(3)))

first_third_tuesdays = first_tuesdays + third_tuesdays
first_third_tuesday_dates = [d.date() for d in first_third_tuesdays if d < two_months_later_start]


with st.form("add_data_form"):
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("日時")
        start_time = st.time_input("開始時間")
        end_time = st.time_input("終了時間")
    with col2:
        options = ["レスカ京大", "レスカ東山"]
        # selectboxでオプションを選択
        choice1 = st.selectbox("選択してください", options)
        # ユーザーに二つの入力フィールドを提供
        choice2 = st.text_input("入力してください")

        # 入力値を判定し、選択された値を代入
        if choice1 and not choice2:
            selected_purpose = choice1
        else:
            selected_purpose = choice2


    submit_add = st.form_submit_button("追加")
    if submit_add:
        new_data = [str(selected_date),str(start_time),str(end_time),str(selected_purpose)]
        sheet.append_row(new_data)
        st.success("Data added successfully!")
        st.experimental_rerun()
data = load_data()

if len(st.session_state.event_list) == 0:

    for wed in wednesday_dates:
        st.session_state.event_list.append({
            'id': str(len(st.session_state.event_list)),
            'title': '缶瓶ペットボトル',
            'start': str(wed)
        })
    for thu in thursday_dates:
        st.session_state.event_list.append({
            'id': str(len(st.session_state.event_list)),
            'title': 'プラスチック',
            'start': str(thu)
        })
    for tue in first_third_tuesday_dates:
        st.session_state.event_list.append({
            'id': str(len(st.session_state.event_list)),
            'title': '資源ごみ',
            'start': str(tue)
        })
        
    for datas in range(len(data)):
        st.session_state.event_list.append({
            'id': str(len(st.session_state.event_list) + datas),
            'title': str(data['purpose'][datas]),
            'start': str(data['date'][datas])+"T"+str(data['start_time'][datas]),
            'end': str(data['date'][datas])+"T"+str(data['end_time'][datas])
        })

options = {
    'initialView': 'timeGridWeek'
}
st_calendar.calendar(events=st.session_state.event_list, options=options)
