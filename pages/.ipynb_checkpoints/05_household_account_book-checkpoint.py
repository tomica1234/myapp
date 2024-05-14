import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import plotly.express as px



# 認証情報の設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = st.secrets["google_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

# Google Sheetを開く
sheet = client.open("app").worksheet("household_account")

category = {'ライフ':'食料品','ユタカ':'日用品','ＡＭＡＺＯＮ．ＣＯ．ＪＰ（買物）':'日用品'}
# Google SheetをPandas DataFrameに読み込む
def load_data():
    df= pd.DataFrame(sheet.get_all_values(),columns = ['日付','場所','値段','分類','ID'])
    
    data = df[1:]
    return data
data = load_data()

for i in range(1,len(data)+1):
    data_ct = category.get(data['場所'][i])
    if data['分類'][i] == "":
        data['分類'][i] = data_ct

    data = data.fillna('その他')



now_y = datetime.today().year
now_m = datetime.today().month
now_d = datetime.today().day
now_today = str(now_y)+"/"+str(now_m)+"/"+str(now_d)

# '日付'列を日付型に変換
data['日付'] = pd.to_datetime(data['日付'])
# 年と月の情報を抽出して整数型に変換
data['年'] = data['日付'].dt.strftime('%Y').fillna(0).astype(int)  # 年をYYYY形式で抽出し、整数型に変換
data['月'] = data['日付'].dt.strftime('%m').fillna(0).astype(int)  # 月をMM形式で抽出し、整数型に変換
data['日付'] = pd.to_datetime(data['日付']).dt.date

st.title("家計簿")

store = ['ライフ','ユタカ','paypay','その他']
category = ["食料品", "日用品", "交際費","光熱費","生協食堂","その他"]

with st.form("add_data_form"):
    col1, col2 = st.columns(2)

    with col1:
        selected_category = st.selectbox("分類", category,index=0)
    with col2:
        price = st.text_input("値段")

    #new_data = [st.text_input('追加')]
    submit_add = st.form_submit_button("追加")
    if submit_add:
        sheet.append_row([now_today,'--',price,selected_category])
        st.success("Data added successfully!")
        st.experimental_rerun()
        
col1, col2, col3 = st.columns(3)

# それぞれのカラムにセレクトボックスを配置
year = []
for years in range(2024,now_y+1):
    year.append(years)
month = ['01','02','03','04','05','06','07','08','09','10','11','12']

with col1:
    selected_year = st.selectbox("年", year,index=now_y-2024)
with col2:
    selected_month = st.selectbox("月", month,index=now_m-1)
with col3:
    selected_category = st.selectbox("分類", ["全て","食料品", "日用品", "交際費","光熱費","生協食堂","その他"])
    
# 選択されたオプションの表示
if selected_category == "全て":
    filtered_data = data[
    (data['年'].astype(int) == int(selected_year)) & (data['月'].astype(int) ==int(selected_month))
    ]
else:
    filtered_data = data[
        (data['年'].astype(int) == int(selected_year)) & (data['月'].astype(int) ==int(selected_month)) & (data['分類']==selected_category)
    ]

filtered_data['値段'] =filtered_data['値段'].astype(int)
sum_price = filtered_data['値段'].sum()
st.write(f'{selected_year}年{selected_month}月の{selected_category}の合計は{sum_price}円です。')
fig = px.bar(filtered_data, x='日付', y='値段', title='家計簿', labels={'値段': '金額', '日付': '日付'},color='分類')

        
st.write(fig)
st.dataframe(filtered_data[['日付','分類','値段']].iloc[:,:4])
