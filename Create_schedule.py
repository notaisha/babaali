import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.title("Baba Ali Scheduler :calendar:")

start_date = st.date_input("Start date:", format="DD/MM/YYYY")
end_date = st.date_input("End date:", value=start_date + timedelta(days=30), format="DD/MM/YYYY")
number_of_days = (end_date - start_date).days

st.info(":bulb: The first person in the list below will have the first shift on the first day selected. The second person will have the second shift on the first day, and so on.")
carers = st.multiselect("Care providers:", ["Nawal", "Nemat", "Mohammad", "Hanan", "Amal", "Amina", "Other"], default=["Nawal", "Hanan", "Nemat", "Amina"])
shifts = st.multiselect("Shifts:", ["12:00-3:30", "3:30-7:00", "7:00-10:00", "Shift1", "Shift2", "Shift3", "Shift4", "Other"], default=["12:00-3:30", "3:30-7:00", "7:00-10:00"])

off_days = int(len(carers) - len(shifts))
days_off_list = ["Break"] * off_days
if off_days > 1:
    days_off_list = [f"Break{i}" for i in range(1, off_days)]
shifts = shifts + days_off_list

"_______"

date_range = pd.Series(pd.date_range(start_date, end_date, freq="d"))
days_of_the_week = {"0": "Monday", "1": "Tuesday", "2": "Wednesday", "3": "Thursday", "4": "Friday", "5": "Saturday", "6": "Sunday"}

df = pd.DataFrame()
dates = []
weekdays = []
for date in list(date_range.dt.date):
    weekdays.append(days_of_the_week[str(date.weekday())])
    dates.append(date.strftime('%d/%m/%Y'))
df["Dates"] = dates
df["Days"] = weekdays

dict = {}
for shift in shifts:
    i = shifts.index(shift)
    for weekday in weekdays:
        if weekday == "Thursday":
            if shift in dict:
                dict[shift].append("-")
            else:
                dict[shift] = ["-"]
        else:
            if shift in dict:
                dict[shift].append(carers[i])
            else:
                dict[shift] = [carers[i]]
            i = (i + 1) % len(carers)

font_size = st.number_input("Table picture font size:", value=12)

for item in dict:
    df[item] = dict[item]
df.index = df["Dates"]
df = df.drop("Dates", axis=1)

show_table = st.toggle("Show table", value=False)
if show_table:
    st.dataframe(df, use_container_width=True)

fig, ax = plt.subplots()
# hide axes
fig.patch.set_visible(False)
ax.axis('off')

# Define colors for each caregiver
colors = {
    "Nawal": "#CCFFCC",
    "Nemat": "#c6b2d2",
    "Mohammad": "#CCCCFF",
    "Hanan": "#FFFFCC",
    "Amal": "#FFCCFF",
    "Amina": "#CCE5FF",
    "Other": "#D3D3D3",
    "Break": "#FFFFFF",  # White for break/off days
}

# Create the table
wrapped_headers = [header for header in df.columns]
table = ax.table(cellText=df.values, colLabels=wrapped_headers, rowLabels=df.index, loc='center')
table.auto_set_font_size(False)
table.scale(xscale=1, yscale=2)

# Apply font size, bold text, and background colors
for (row, col), cell in table.get_celld().items():
    if row > 0 and col > 0:  # Skip header row and column
        cell.set_fontsize(font_size)
        cell.set_text_props(fontweight='bold')
        caregiver = cell.get_text().get_text()  # Get cell text
        cell.set_facecolor(colors.get(caregiver, "#FFFFFF"))  # Set color based on caregiver

st.pyplot(fig)
