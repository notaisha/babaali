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
shifts = st.multiselect("Shifts:", ["12:00-3:30", "3:30-7:00", "7:00-10:00", "Shift1", "Shift2", "Shift3", "Shift4", "Other"], default=["Shift1", "Shift2"])

# Hanan preference toggle (default ON)
hanan_special = "Hanan" in carers and st.toggle(
    "Hanan rule: if she works that day → Sun–Thu last working shift, Fri/Sat first working shift",
    value=True
)

# Pad shifts to match carers with break columns (does NOT force/avoid Hanan breaks)
off_days = int(len(carers) - len(shifts))
days_off_list = ["Break"] * off_days
if off_days > 1:
    days_off_list = [f"Break{i}" for i in range(1, off_days)]
shifts = shifts + days_off_list

"_______"

date_range = pd.Series(pd.date_range(start_date, end_date, freq="D"))
dow_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

# ---- base rotation (unchanged) ----
rows = []
for d_idx, ts in enumerate(date_range):
    date_obj = ts.date()
    weekday_str = dow_map[date_obj.weekday()]
    # assign by shift position: shift j gets carers[(j + d_idx) % len(carers)]
    day_assign = [carers[(j + d_idx) % len(carers)] for j in range(len(shifts))]
    rows.append({"Dates": date_obj.strftime("%d/%m/%Y"), "Day": weekday_str, **{shifts[i]: day_assign[i] for i in range(len(shifts))}})

df = pd.DataFrame(rows)
df.index = df["Dates"]
df = df.drop("Dates", axis=1)

# ---- post-assignment reordering for Hanan ONLY (no change to who is off) ----
if hanan_special and "Hanan" in carers:
    shift_cols = [c for c in df.columns if c != "Day"]
    work_cols = [c for c in shift_cols if not str(c).lower().startswith("break")]
    if work_cols:
        first_work_col = work_cols[0]
        last_work_col = work_cols[-1]

        for ridx in df.index:
            # if Hanan isn't assigned at all that day, skip
            # also skip if Hanan is assigned to a Break column (she keeps that break)
            # find her current working-shift column (if any)
            hanan_work_col = None
            for c in work_cols:
                if str(df.at[ridx, c]) == "Hanan":
                    hanan_work_col = c
                    break
            if not hanan_work_col:
                continue  # not working that day (either off or not scheduled)

            is_weekend = df.at[ridx, "Day"] in ["Fri", "Sat"]
            target_col = first_work_col if is_weekend else last_work_col

            if hanan_work_col != target_col:
                # swap assignments between her current work col and target work col
                curr_val = df.at[ridx, hanan_work_col]
                target_val = df.at[ridx, target_col]
                df.at[ridx, hanan_work_col] = target_val
                df.at[ridx, target_col] = curr_val

font_size = st.number_input("Table picture font size:", value=15)

show_table = st.toggle("Show table", value=False)
if show_table:
    st.dataframe(df, use_container_width=True)

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
    "Break": "#FFFFFF",  # for any Break*
}

wrapped_headers = [header for header in df.columns]
table = ax.table(cellText=df.values, colLabels=wrapped_headers, rowLabels=df.index, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.scale(xscale=1, yscale=2)

for (row, col), cell in table.get_celld().items():
    if row > 0 and col >= 0:
        cell.set_fontsize(font_size)
        text = cell.get_text().get_text()
        # color by caregiver, treat any Break* as Break
        bg = colors.get(text, colors["Break"] if str(text).lower().startswith("break") else "#FFFFFF")
        cell.set_facecolor(bg)

st.pyplot(fig)
