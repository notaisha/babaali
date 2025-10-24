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

# Toggle: enforce Hanan works Tue, Thu & Sat only
hanan_special = "Hanan" in carers and st.toggle("Hanan has work", value=True)

# --- ensure total shifts + breaks == carers ---
off_days = len(carers) - len(shifts)
if off_days > 0:
    days_off_list = [("Break" if i == 0 else f"Break{i+1}") for i in range(off_days)]
    shifts = shifts + days_off_list

"_______"

date_range = pd.Series(pd.date_range(start_date, end_date, freq="D"))
dow_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

# ---- base rotation (unchanged) ----
rows = []
for d_idx, ts in enumerate(date_range):
    d = ts.date()
    weekday_str = dow_map[d.weekday()]
    day_assign = [carers[(j + d_idx) % len(carers)] for j in range(len(shifts))]
    rows.append({"Dates": d.strftime("%d/%m/%Y"), "Day": weekday_str,
                 **{shifts[i]: day_assign[i] for i in range(len(shifts))}})

df = pd.DataFrame(rows)
df.index = df["Dates"]
df = df.drop("Dates", axis=1)

# ---- helpers ----
shift_cols = [c for c in df.columns if c != "Day"]
work_cols  = [c for c in shift_cols if not str(c).lower().startswith("break")]
break_cols = [c for c in shift_cols if     str(c).lower().startswith("break")]
first_work_col = work_cols[0] if work_cols else None
last_work_col  = work_cols[-1] if work_cols else None

def find_col(idx, person, cols):
    for c in cols:
        if str(df.at[idx, c]) == person:
            return c
    return None

# ---- enforce: Hanan works Tue (last), Thu (last), Sat (first) only ----
if hanan_special and "Hanan" in carers and work_cols:
    if not break_cols:
        st.warning("No Break columns detected. I can place Hanan on Tue/Thu/Sat, but can’t force her off other days without a Break column.")
    for ridx in df.index:
        day = df.at[ridx, "Day"]
        is_target = day in ["Tue", "Thu", "Sat"]

        # Determine which edge she should be on for target days
        target_edge = None
        if day in ["Tue", "Thu"]:   # weekdays → last work shift
            target_edge = last_work_col
        elif day == "Sat":          # weekend → first work shift
            target_edge = first_work_col

        if is_target and target_edge is not None:
            h_any = find_col(ridx, "Hanan", shift_cols)
            if h_any is None:
                # bring Hanan in by parking current edge person in a Break
                if break_cols:
                    bcol = break_cols[0]
                    displaced = df.at[ridx, target_edge]
                    df.at[ridx, target_edge] = "Hanan"
                    df.at[ridx, bcol] = displaced
            else:
                # move Hanan to the correct edge work column if needed
                if h_any != target_edge:
                    df.at[ridx, h_any], df.at[ridx, target_edge] = df.at[ridx, target_edge], df.at[ridx, h_any]
        else:
            # Non-target days → move Hanan to Break if she’s on a working shift
            h_work = find_col(ridx, "Hanan", work_cols)
            if h_work and break_cols:
                bcol = break_cols[0]
                df.at[ridx, h_work], df.at[ridx, bcol] = df.at[ridx, bcol], df.at[ridx, h_work]

# ---- visuals ----
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

wrapped_headers = list(df.columns)
table = ax.table(cellText=df.values, colLabels=wrapped_headers, rowLabels=df.index, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.scale(xscale=1, yscale=2)

for (row, col), cell in table.get_celld().items():
    if row > 0 and col >= 0:
        cell.set_fontsize(font_size)
        text = cell.get_text().get_text()
        bg = colors.get(text, colors["Break"] if str(text).lower().startswith("break") else "#FFFFFF")
        cell.set_facecolor(bg)

st.pyplot(fig)
