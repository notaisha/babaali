import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta
from collections import Counter
import matplotlib.pyplot as plt

st.title("Baba Ali Scheduler :calendar:")

start_date = st.date_input("Start date:", format="DD/MM/YYYY")
end_date = st.date_input("End date:", value = start_date + timedelta(days=30), format="DD/MM/YYYY")
number_of_days = (end_date - start_date).days
#number_of_days

st.info(":bulb: The first person in the list below will have the first shift on the first day selected. The second person will have the second shift on the first day, and so on.")
carers = st.multiselect("Care providers:", ["Nawal","Nemat", "Mohammad", "Hanan", "Amal", "Amina", "Other"], default = ["Nawal", "Nemat", "Hanan", "Amina"])
shifts = st.multiselect("Shifts:", ["11:00am-2:30pm", "2:30pm-6:00pm", "6:00-10:00", "Shift1", "Shift2", "Shift3", "Shift4","Other"], default = ["11:00am-2:30pm", "2:30pm-6:00pm", "6:00-10:00"]) 
off_days = int(len(carers)-len(shifts))
days_off_list = ["Break"]*off_days
if off_days > 1:
    days_off_list = [ f"{a}{c[a]}" for c in [Counter()] for a in days_off_list if [c.update([a])] ]
shifts= shifts+days_off_list 


"_______"

date_range = pd.Series(pd.date_range(start_date, end_date, freq="d"))
days_of_the_week = {"0":"Monday" , "1":"Tuesday" , "2":"Wednesday" , "3":"Thursday" , "4":"Friday" , "5":"Saturday" , "6":"Sunday" }


df = pd.DataFrame()
dates = []
weekdays = []
for date in list(date_range.dt.date):
    weekdays.append(days_of_the_week[str(date.weekday())])
    dates.append(date.strftime('%d/%m/%Y'))
df["Dates"] = dates
df["Days"] = weekdays



dict={}
for shift in shifts:
    i = shifts.index(shift)
    for weekday in weekdays:
        if weekday == "Thursday":
            if shift in dict:
                dict[shift].append("-")
            else:
                dict[shift]=["-"]
        else:
            if shift in dict:
                dict[shift].append(carers[i])
            else:
                dict[shift]=[carers[i]]
            i=(i+1)%len(carers)
            #st.write(weekday, shift, i)
        
for item in dict:
    df[item]=dict[item] 
df.index = df["Dates"]
df = df.drop("Dates", axis=1)
st.dataframe(df, use_container_width=True)


fig, ax = plt.subplots()
# hide axes
fig.patch.set_visible(False)
ax.axis('off')
#ax.axis('tight')
ax.table(cellText=df.values, colLabels=df.columns, rowLabels=df.index, loc='center')

#fig.tight_layout()
#image_name = f"Baba_Ali_schedule_{start_date.strftime('%d-%m-%Y')}_to_{end_date.strftime('%d-%m-%Y')}"
#fig.savefig(image_name)
fig
