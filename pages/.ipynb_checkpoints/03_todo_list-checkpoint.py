import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 認証情報の設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

# Google Sheetを開く
sheet = client.open("app").worksheet("todo")

# Google SheetをPandas DataFrameに読み込む
def load_data():
    df= pd.DataFrame(sheet.get_all_values(),columns = ['todo_list'])
    data = df[1:]
    data.index = data.index+1
    data.reset_index(drop=True, inplace=True)
    return data

# Streamlitアプリの構築
st.title('ToDoリスト')
data = load_data()

#####################
# Streamlitのsession_stateを使ってチェック状態を追跡
if 'checked_state' not in st.session_state:
    st.session_state.checked_state = [False] * (len(data) + 1)  # インデックスが1始まりのため

# DataFrameの各行にチェックボックスを表示
for idx, row in data.iterrows():
    st.session_state.checked_state[idx] = st.checkbox(
        row['todo_list'], key=f'checkbox_{idx}', value=st.session_state.checked_state[idx])

# 「削除実行」ボタン
if st.button('Delete Selected'):
    # 選択された項目のインデックスを取得
    indices_to_delete = [idx + 2 for idx, checked in enumerate(st.session_state.checked_state) if checked]
    # インデックスを逆順にして削除
    indices_to_delete.reverse()  # インデックスを逆順にソート
    for idx in indices_to_delete:
        sheet.delete_rows(idx)  # Google スプレッドシートの行を削除
    
    st.success(f"Selected rows deleted successfully! {len(indices_to_delete)} rows removed.")
    st.experimental_rerun()  # 画面を再読み込み
#####################

st.markdown(
    """
    <style>
    .dataframe-container{
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
#st.write(data)

# データの追加
with st.form("add_data_form"):
    new_data = [st.text_input('todo_list')]
    submit_add = st.form_submit_button("Add Data")
    if submit_add:
        sheet.append_row(new_data)
        st.success("Data added successfully!")
        st.experimental_rerun()

# # データの削除
# with st.form("delete_data_form"):
#     row_number = st.number_input('Enter row number to delete', min_value=1, value=1, step=1)
#     submit_delete = st.form_submit_button("Delete Data")
#     if submit_delete:
#         sheet.delete_rows(int(row_number))
#         st.success("Data deleted successfully!")
#         st.experimental_rerun()
