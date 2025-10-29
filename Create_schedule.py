import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import random

st.title("Baba Ali Scheduler :calendar:")

# ---- inputs ----
start_date = st.date_input("Start date:", format="DD/MM/YYYY")
end_date = st.date_input("End date:", value=start_date + timedelta(days=30), format="DD/MM/YYYY")

st.info(":bulb: The first person in the list below will have the first shift on the first day selected. The second person will have the second shift on the first day, and so on.")

carers = st.multiselect(
    "Care providers:",
    ["Nawal", "Nemat", "Mohammad", "Hanan", "Amal", "Amina", "Other"],
    default=["Nawal", "Hanan", "Nemat", "Amina"],
)

shifts = st.multiselect(
    "Shifts:",
    ["12:00-3:30", "3:30-7:00", "7:00-10:00", "Shift1", "Shift2", "Shift3", "Shift4", "Other"],
    default=["Shift1", "Shift2"],
)

hanan_special = "Hanan" in carers and st.toggle("Hanan has work (random N days per week)", value=True)
days_per_week = int(st.number_input("Hanan days per week (random, Sun–Sat)", min_value=0, max_value=7, value=3, step=1))

# ---- ensure total shifts + breaks == carers ----
off_needed = len(carers) - len(shifts)
if off_needed > 0:
    breaks_to_add = [("Break" if i == 0 else f"Break{i+1}") for i in range(off_needed)]
    shifts = shifts + breaks_to_add

# ---- prepare dates and helpers ----
date_range = pd.date_range(start_date, end_date, freq="D")
dow_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

def sunday_of_week(d: date) -> date:
    # Mon=0..Sun=6  → Sunday start
    return d - timedelta(days=(d.weekday() + 1) % 7)

# split into Sunday-start weeks
weeks = {}
for d in date_range:
    key = sunday_of_week(d.date())
    weeks.setdefault(key, []).append(d.date())

# columns split
work_cols = [c for c in shifts if not str(c).lower().startswith("break")]
break_cols = [c for c in shifts if     str(c).lower().startswith("break")]
first_work_col = work_cols[0] if work_cols else None
last_work_col  = work_cols[-1] if work_cols else None

if hanan_special and "Hanan" in carers and not break_cols:
    st.warning("No Break columns detected. On non-workdays, Hanan cannot be moved to Break; she'll simply not be placed on those days.")

# decide Hanan's workdays randomly per week (allow back-to-back)
hanan_workdays = set()
if hanan_special and "Hanan" in carers:
    for wk_start, days in weeks.items():
        k = min(days_per_week, len(days))
        chosen = set(random.sample(days, k)) if k > 0 else set()
        hanan_workdays |= chosen

# rotation over NON-Hanan carers only
others = [c for c in carers if c != "Hanan"]
rot_idx = 0  # rotates one step per day

# ---- build schedule day-by-day with "assign Hanan first, then fill others" ----
rows = []
for d in date_range:
    d0 = d.date()
    day_name = dow_map[d0.weekday()]
    row_assign = {col: None for col in shifts}

    # 1) Place Hanan
    if hanan_special and "Hanan" in carers:
        if d0 in hanan_workdays:
            # On workdays: weekend(Fri/Sat) -> first work col; else -> last work col
            target_col = first_work_col if day_name in ["Fri", "Sat"] else last_work_col
            if target_col is not None:
                row_assign[target_col] = "Hanan"
        else:
            # On off days: move Hanan to a Break if available
            if break_cols:
                row_assign[break_cols[0]] = "Hanan"
            # else: no placement for Hanan today

    # 2) Fill remaining cells with rotating "others"
    cols_in_order = list(shifts)
    for col in cols_in_order:
        if row_assign[col] is not None:
            continue
        if not others:
            # nothing to place (only Hanan exists)
            row_assign[col] = "Break" if str(col).lower().startswith("break") else "Other"
            continue
        row_assign[col] = others[rot_idx % len(others)]
        rot_idx = (rot_idx + 1) % len(others)

    # advance rotation ONE step per day overall to keep day-to-day fairness
    rot_idx = (rot_idx + 1) % max(1, len(others)) if others else 0

    rows.append({
        "Date": d0.strftime("%d/%m/%Y"),
        "Day": day_name,
        **row_assign
    })

df = pd.DataFrame(rows)
df.index = df["Date"]
df = df.drop(columns=["Date"])

# ---- UI: table + plot ----
font_size = st.number_input("Table picture font size:", value=15)

show_table = st.toggle("Show table", value=False)
if show_table:
    st.dataframe(df, use_container_width=True)

# Plot as a colored table
fig, ax = plt.subplots()
fig.patch.set_visible(False)
ax.axis('off')

colors = {
    "Nawal": "#E5FFE5",
    "Nemat": "#D6E4FF",
    "Mohammad": "#CCCCFF",
    "Hanan": "#FFF3E6",
    "Amal": "#FFCCFF",
    "Amina": "#FFE6F2",
    "Other": "#D3D3D3",
    "Break": "#FFFFFF",
}

wrapped_headers = list(df.columns)
table = ax.table(cellText=df.values, colLabels=wrapped_headers, rowLabels=df.index, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.scale(xscale=1, yscale=2)

for (row, col), cell in table.get_celld().items():
    if row > 0 and col >= 0:
        cell.set_fontsize(font_size)
        text = cell.get_text().get_text()
        # any unknown label gets white
        bg = colors.get(text, "#FFFFFF")
        cell.set_facecolor(bg)

st.pyplot(fig)
