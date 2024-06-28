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


# category = {'ライフ':'食料品','ユタカ':'日用品','ＡＭＡＺＯＮ．ＣＯ．ＪＰ（買物）':'日用品'}
# # Google SheetをPandas DataFrameに読み込む
# def load_data():
#     df= pd.DataFrame(sheet.get_all_values(),columns = ['日付','場所','値段','分類','ID'])
    
#     data = df[1:]
#     return data
# data = load_data()

# for i in range(1,len(data)+1):
#     data_ct = category.get(data['場所'][i])
#     if data['分類'][i] == "":
#         data['分類'][i] = data_ct

#     data = data.fillna('その他')
def load_data():
    df= pd.DataFrame(sheet.get_all_values(),columns = ['日付','場所','値段','分類','ID'])
    
    data = df[1:]
    return data
data = load_data()
data.columns = ['日付','場所','値段','分類','ID']

classification_rules = {
    'ＡＭＡＺＯＮ': '日用品',
    'ライフ': '食料品',
    'フレスコ': '食料品',
    'ファミリーマート': '日用品',
    'セブン－イレブン': '日用品',
    'ローソン':'日用品',
    'サイゼ': '交際費'
}
# 分類ルールを適用する関数（空の分類のみ更新）
def categorize(row):
    if row['分類']:  # すでに分類が存在する場合はその値を保持
        return row['分類']
    for key, value in classification_rules.items():
        if key in row['場所']:
            return value
    return 'その他'  # 辞書に該当しない場所の場合または分類が空の場合

# 分類列の更新
data['分類'] = data.apply(categorize, axis=1)



now_y = datetime.today().year
now_m = datetime.today().month
now_d = datetime.today().day
now_today = str(now_y)+"/"+str(now_m)+"/"+str(now_d)

# '日付'列を日付型に変換
data['日付'] = pd.to_datetime(data['日付'],errors='coerce')
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

uploaded_file = st.file_uploader("明細のアップロード", type=['csv'])
    # DataFrameをスプレッドシートに書き込む関数
def df_to_sheet(df, worksheet):
    # DataFrameをリスト形式に変換
    values = [df.columns.tolist()] + df.values.tolist()
    # スプレッドシートに書き込み
    worksheet.update('A1', values)

if uploaded_file is not None:
    # ファイルがアップロードされた場合、Pandasでデータを読み込む
    df_cred = pd.read_csv(uploaded_file, encoding='cp932',names = ('日付','場所(詳細)','値段','1','2','3','4'))
    df_cred = df_cred.iloc[:,0:6]
    sheet_ha = client.open("app").worksheet("household_account")
    df_ha= pd.DataFrame(sheet_ha.get_all_values())

    df_credit = df_cred.iloc[:,0:3]
    df_credit.columns = ['日付','場所(詳細)','値段']
    df_ha.columns = ['日付','場所','値段','分類','ID']
    merged_df = pd.merge(df_ha, df_credit, on=['日付', '値段'], how='outer')
    
    # 場所を場所(詳細)で更新（場所(詳細)が存在する場合）
    merged_df['場所'] = merged_df.apply(lambda x: x['場所(詳細)'] if pd.notna(x['場所(詳細)']) else x['場所'], axis=1)
    
    # 不要な列の削除
    merged_df.drop('場所(詳細)', axis=1, inplace=True)
    
    df = merged_df.iloc[0:len(df_ha)]
    df = df.iloc[1:]
    df_to_sheet(df, sheet_ha)
    
