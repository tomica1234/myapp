import streamlit as st
import streamlit_calendar as st_calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, WEEKLY, MO, TU, WE


# 現在の日付を取得
now = datetime.now()

# 今月の初日と来月の初日を計算
this_month_start = datetime(now.year, now.month, 1)
next_month_start = this_month_start + relativedelta(months=+1)
two_months_later_start = next_month_start + relativedelta(months=+1)

# 今月と来月の水曜日の全日にちを取得
wednesdays = list(rrule(freq=WEEKLY, dtstart=this_month_start, until=two_months_later_start, byweekday=WE))
wednesday_dates = [d.date() for d in wednesdays if d < two_months_later_start]


# 今月と来月の木曜日の全日にちを取得
thursdays = list(rrule(freq=WEEKLY, dtstart=this_month_start, until=two_months_later_start, byweekday=TH))
thursday_dates = [d.date() for d in thursdays if d < two_months_later_start]


# 今月と来月の第1, 第3火曜日の日にちを取得
first_tuesdays = list(rrule(freq=MONTHLY, dtstart=this_month_start, until=two_months_later_start, byweekday=TU(1)))
third_tuesdays = list(rrule(freq=MONTHLY, dtstart=this_month_start, until=two_months_later_start, byweekday=TU(3)))

# rrule オブジェクトの結果を結合
first_third_tuesdays = first_tuesdays + third_tuesdays
first_third_tuesday_dates = [d.date() for d in first_third_tuesdays if d < two_months_later_start]

event_list = []
for wed in range(len(wednesday_dates)):
    event = {
        'id': str(wed),
        'title':'缶瓶ペットボトル',
        'start':str(wednesday_dates[wed])
    }
    event_list.append(event)

for thu in range(len(thursday_dates)):
    event = {
        'id': str(thu+len(wednesday_dates)),
        'title':'プラスチック',
        'start':str(thursday_dates[thu])
    }
    event_list.append(event)

for tue in range(len(first_third_tuesday_dates)):
    event = {
        'id': str(tue+len(wednesday_dates)+len(thursday_dates)),
        'title':'資源ごみ',
        'start':str(first_third_tuesday_dates[tue])
    }
    event_list.append(event)

st.title('ゴミ出しカレンダー')
st_calendar.calendar(events=event_list)
