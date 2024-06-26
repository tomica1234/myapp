import streamlit as st
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
import plotly.express as px
import matplotlib.pyplot as plt


###時刻テスト用###
#now = pd.Timestamp(year=2024,month=5,day=22,hour=18,minute=0,second=0,tz='Asia/Tokyo')
# 現在時刻の取得
now = pd.Timestamp.now(tz='Asia/Tokyo')
# if now.hour < 9:
#     now = now - pd.Timedelta(days=1)
#     now_today = now + pd.Timedelta(days=1)
    
# セッションの設定
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


# APIパラメータ
url = "https://api.open-meteo.com/v1/forecast"
params_rain = {
    "latitude": 35.0211,
    "longitude": 135.7538,
    "hourly": "precipitation",
    "past_days": 1,
    "forecast_days": 3
}

params_temp = {
    "latitude": 35.0211,
    "longitude": 135.7538,
    "hourly": "temperature_2m",
    "past_days": 1,
    "forecast_days": 3
}

# API降水量からデータ取得
responses_rain = openmeteo.weather_api(url, params=params_rain)
response_rain = responses_rain[0]

# API気温からデータ取得
responses_temp = openmeteo.weather_api(url, params=params_temp)
response_temp = responses_temp[0]

# 時間データの処理
hourly_rain = response_rain.Hourly()
hourly_precipitation = hourly_rain.Variables(0).ValuesAsNumpy()

hourly_temp = response_temp.Hourly()
hourly_temperature = hourly_temp.Variables(0).ValuesAsNumpy()



# 日付データの生成
hourly_rain_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly_rain.Time()+54000, unit="s", utc=True),
        end=pd.to_datetime(hourly_rain.TimeEnd()+54000, unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly_rain.Interval()),
        inclusive="left"
    )
}


hourly_temp_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly_temp.Time()+54000, unit="s", utc=True),
        end=pd.to_datetime(hourly_temp.TimeEnd()+54000, unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly_temp.Interval()),
        inclusive="left"
    )
}

# タイムゾーンの変換と日付フォーマット
hourly_rain_data["date"] = hourly_rain_data["date"][0:24].tz_convert('Asia/Tokyo').strftime('%Y-%m-%d %H:%M')
hourly_rain_data["precipitation"] = hourly_precipitation[15:39]
hourly_rain_data["precipitation"] = hourly_rain_data["precipitation"]

hourly_temp_data["date"] = hourly_temp_data["date"][0:24].tz_convert('Asia/Tokyo').strftime('%Y-%m-%d %H:%M')
hourly_temp_data["temperature_2m"] = hourly_temperature[15:39]
hourly_temp_data["temperature_2m"]=hourly_temp_data["temperature_2m"]
# データフレームの作成
hourly_rain_dataframe = pd.DataFrame(data=hourly_rain_data)
hourly_rain_dataframe['precipitation'] = hourly_rain_dataframe['precipitation'].astype(float).round(1)
hourly_temp_dataframe = pd.DataFrame(data=hourly_temp_data)
hourly_temp_dataframe['temperature_2m'] = hourly_temp_dataframe['temperature_2m'].astype(float).round(1)

# 当日のデータ抽出
# if now.hour < 9:
#     df_rain_now_yesterday = hourly_rain_dataframe.iloc[int(now.strftime('%H'))+15:24].copy().reset_index()
#     df_rain_now_today = hourly_rain_dataframe.iloc[int(now_today.strftime('%H')):15].copy().reset_index()
#     df_rain_now = pd.concat([df_rain_now_yesterday,df_rain_now_today])
#     df_temp_now_yesterday = hourly_temp_dataframe.iloc[int(now.strftime('%H'))+15:24].copy().reset_index()
#     df_temp_now_today = hourly_temp_dataframe.iloc[int(now_today.strftime('%H')):15].copy().reset_index()
#     df_temp_now = pd.concat([df_temp_now_yesterday,df_temp_now_today])
# else:
#     df_rain_now = hourly_rain_dataframe.iloc[int(now.strftime('%H')) - 9:int(now.strftime('%H'))+15].copy().reset_index()
#     df_temp_now = hourly_temp_dataframe.iloc[int(now.strftime('%H')) - 9:int(now.strftime('%H'))+15].copy().reset_index()
df_rain_now = hourly_rain_dataframe.iloc[int(now.strftime('%H')) :int(now.strftime('%H'))+24].copy().reset_index()
df_temp_now = hourly_temp_dataframe.iloc[int(now.strftime('%H')):int(now.strftime('%H'))+24].copy().reset_index()

df_rain_now['date'] = pd.to_datetime(df_rain_now['date'], format='%Y-%m-%d %H:%M')
df_temp_now['date'] = pd.to_datetime(df_temp_now['date'], format='%Y-%m-%d %H:%M')

# グラフの作成
fig_rain = px.bar(df_rain_now, x='date', y='precipitation', title='予想降水量', labels={'Precipitation': '降水量 (mm)', 'Date': '時間'})

fig_temp = px.line(df_temp_now, x='date', y='temperature_2m', title='予想気温', labels={'Temperature_2m':'気温','Date': '時間'})


st.title("京都の天気")

city_code = "260010"
zone = "Asia/Tokyo"
url = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"

response_weather = requests.get(url)
weather_json = response_weather.json()
now_hour = datetime.now(ZoneInfo(zone)).hour

# 時間帯による降水確率の判断
time_periods = ['T00_06', 'T06_12', 'T12_18', 'T18_24']
current_period = time_periods[now_hour // 6]
chance_of_rain_now = weather_json['forecasts'][0]['chanceOfRain'][current_period]
#temp_now = str(int(hourly_temp_dataframe.iloc[int(now.strftime('%H')) - 9:int(now.strftime('%H'))-8]['temperature_2m'].copy()))
temp_now = str(int(df_temp_now.iloc[0:1]['temperature_2m'].copy()))
rain_now = str(float(round(df_rain_now.iloc[0:1]['precipitation'].copy(),2)))

max_temp = weather_json['forecasts'][0]['temperature']['max'].get('celsius', 'データなし')

if max_temp != None:
    weather_now_text ="降水確率 : " + chance_of_rain_now + " 今日の最高気温 : "+ max_temp + "℃" +"現在の気温："+temp_now+"℃"+" "+"現在の降水量："+rain_now+"mm"
    st.write(weather_now_text)
else:
    st.write("現在の降水確率 : " + chance_of_rain_now +" "+ "現在の気温："+temp_now+"℃"+" "+"現在の降水量："+rain_now+"mm")

# DataFrameの作成
def create_temperature_df(forecast_data):
    temp_data = {
        '最低気温 (°C)': [forecast_data['temperature']['min'].get('celsius', 'データなし')],
        '最高気温 (°C)': [forecast_data['temperature']['max'].get('celsius', 'データなし')]
    }
    return pd.DataFrame(temp_data, index=[forecast_data['dateLabel']])

df_temp_today = create_temperature_df(weather_json['forecasts'][0])
df_temp_tomorrow = create_temperature_df(weather_json['forecasts'][1])

# 降水確率のDataFrame作成
def display_weather_icon(forecast_data):
    icon_url = forecast_data['image']['url']
    if forecast_data['temperature']['max'].get('celsius', 'データなし') == None:
        return st.image(icon_url)
    else:
        return st.image(icon_url, caption='最高気温: ' + forecast_data['temperature']['max'].get('celsius', 'データなし') + '℃')

# 今日と明日の天気アイコンを表示
for forecast in weather_json['forecasts'][:2]:  # 最初の2つの要素、つまり今日と明日だけを処理
    st.subheader(f"{forecast['dateLabel']}の天気")
    display_weather_icon(forecast)



st.write(fig_rain)
st.write(fig_temp)

st.write(df_rain_now)
st.write(df_temp_now)