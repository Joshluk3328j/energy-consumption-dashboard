import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import zscore
from pathlib import Path
from fpdf import FPDF
import tempfile
import datetime

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(page_title="Energy Dashboard", layout="wide")
st.title("⚡ Cleaned Energy Data Interface")

# -----------------------
# Load from .dat Files
# -----------------------
@st.cache_data
def load_house_data(path: Path) -> pd.DataFrame:
    label_path = path / "labels.dat"
    if not label_path.exists():
        raise FileNotFoundError("labels.dat not found!")

    # Build mapping from labels.dat
    channel_map : dict[int, str] = {}
    with open(label_path, "r") as f:
        for line in f:
            ch, label = line.strip().split(" ", 1)
            channel_map[int(ch)] = label

    # Read all available .dat files
    df_dict : dict[str, pd.DataFrame] = {}
    for ch, label in channel_map.items():
        file = path / f"channel_{ch}.dat"
        if file.exists():
            try:
                df = pd.read_csv(file, sep=" ", names=["timestamp", label])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
                df.set_index("timestamp", inplace=True)
                df_dict[label] = df
            except Exception as e:
                st.warning(f"⚠️ Could not load {label}: {e}")

    if not df_dict:
        raise ValueError("No valid .dat files were loaded.")

    # Combine all into one dataframe
    df_all = pd.concat(df_dict.values(), axis=1).fillna(0)

    return df_all

# -----------------------
# Load Data
# -----------------------
data_path = Path("cleaned_house1")
try:
    df_vah = load_house_data(data_path)
except Exception as e:
    st.error(f"❌ Failed to load cleaned data: {e}")
    st.stop()

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.title("🔍 Filter Options")

# Show available date range
st.sidebar.markdown(f"🗓️ **Available data:** `{df_vah.index.min().date()}` to `{df_vah.index.max().date()}`")

# Select Date Range
min_date = df_vah.index.min().date()
max_date = df_vah.index.max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=[min_date, max_date],  # Default to full range
    min_value=min_date,
    max_value=max_date
)

# Appliance Selection with Select All
all_appliances = df_vah.columns.tolist()
select_all = st.sidebar.checkbox("Select All Appliances", value=False)

if select_all:
    appliances = st.sidebar.multiselect("Appliances", all_appliances, default=all_appliances)
else:
    appliances = st.sidebar.multiselect("Appliances", all_appliances, default=["aggregate"])

# Validate appliance selection
if not appliances:
    st.error("❌ Please select at least one appliance.")
    st.stop()

# Validate and slice date
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    print(date_range)
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    # Include the full end date
    print(start_date, end_date)
    # end_date = end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    # Get subset of data within date *range* (even if start or end days have missing timestamps)
    df_filtered = df_vah.loc[(df_vah.index.date >= start_date.date()) & (df_vah.index.date <= end_date.date()), appliances]

    if df_filtered.empty:
        st.error(f"❌ No data available between {start_date.date()} and {end_date.date()}.")
        st.stop()


    # Determine resampling frequency
    days = (end_date - start_date).days + 1
    if days <= 1:
        freq = "h"
    elif days <= 7:
        freq = "h"
    elif days <= 30:
        freq = "d"
    else:
        freq = "d"

    df_resampled = df_filtered.resample(freq).sum()
    df_resampled = df_resampled[(df_resampled.index.date >= start_date.date()) & (df_resampled.index.date <= end_date.date())]
    
else:
    st.warning("⚠️ Please select a valid date range (start and end dates).")
    st.stop()


# -----------------------
# Tabs
# -----------------------
tab1, tab2 = st.tabs(["📊 Dashboard", "📋 Report"])

# -----------------------
# Tab 1: Dashboard
# -----------------------
with tab1:
    st.subheader("Power Consumption Dashboard")

    # Display limited chart data to avoid size issues
    df_display = df_resampled[(df_resampled.sum(axis=1) > 0)]

    anomalies = {}
    for appliance in appliances:
        if appliance == "aggregate":
            pass
        else:
            z = zscore(df_resampled[appliance])
            outliers = df_resampled[(z > 3) | (z < -3)][[appliance]]
            if not outliers.empty:
                anomalies[appliance] = outliers

    if anomalies:
        # st.subheader("Anomaly Detection")
        with st.expander("View Anomalies"):
            for appliance, outliers in anomalies.items():
                st.warning(f"{len(outliers)} anomalies in **{appliance}**")
                st.dataframe(outliers)

    st.plotly_chart(
        px.line(df_display, labels={"value": "VAh", "timestamp": "Time"}, title="Energy Usage Over Time"),
        use_container_width=True
    )
    if len(df_resampled.columns) > 1 and "aggregate" in df_resampled.columns:
        st.metric("Total Consumption", f"{df_resampled.drop('aggregate', axis=1).sum().sum():,.2f} VAh")
        st.metric("⚖️ Average per Appliance", f"{df_resampled.drop('aggregate', axis=1).mean().mean():,.2f} VAh")
        appliance_sum = df_resampled.drop("aggregate", axis=1).sum()

        top_appliance = appliance_sum.idxmax()
        top_val = appliance_sum.max()
        st.success(f"Highest Consumer: **{top_appliance}** with **{top_val:.2f} VAh**")
    elif len(df_resampled.columns) > 1:
        st.metric("Total Consumption", f"{df_resampled.sum().sum():,.2f} VAh")
        st.metric("⚖️ Average per Appliance", f"{df_resampled.mean().mean():,.2f} VAh")
        appliance_sum = df_resampled.sum()

        top_appliance = appliance_sum.idxmax()
        top_val = appliance_sum.max()
        st.success(f"Highest Consumer: **{top_appliance}** with **{top_val:.2f} VAh**")
    elif len(df_resampled.columns) == 1 and ("aggregate" in df_resampled.columns):
        st.metric("Total Consumption", f"{df_resampled.sum().sum():,.2f} VAh")

    with st.expander("View Raw Data Table"):
        st.dataframe(df_resampled.tail(100).reset_index())

# -----------------------
# Tab 2: Report
# -----------------------
with tab2:
    st.subheader("📋 Analysis Report")

    if st.button("📄 Generate PDF Report"):
        # -----------------------
        # Prepare Report Data
        # -----------------------
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        selected_appliances = ', '.join(appliances)
        date_range = f"{df_resampled.index.min().date()} to {df_resampled.index.max().date()}"
        stats = df_resampled.describe().T.round(2)
        appliance_sum = df_resampled.sum()
        top_appliance = appliance_sum.idxmax()
        top_val = appliance_sum.max()

        # # Detect anomalies
        # anomalies = {}
        # for appliance in appliances:
        #     if appliance == "aggregate":
        #         continue
        #     z = zscore(df_resampled[appliance])
        #     outliers = df_resampled[(z > 3) | (z < -3)][[appliance]]
        #     if not outliers.empty:
        #         anomalies[appliance] = outliers

        anomaly_summary = pd.DataFrame({
            "Appliance": list(anomalies.keys()),
            "Anomalies": [len(v) for v in anomalies.values()]
        })

        # -----------------------
        # Create Visual Assets
        # -----------------------

        # Line Plot
        fig_line = px.line(df_resampled, title="Appliance Power Usage Over Time", labels={"value": "VAh"})
        line_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        fig_line.write_image(line_img_path, width=1000, height=400)

        # Bar Chart - Top Consumers
        top_n = 10
        top_appliances = appliance_sum.sort_values(ascending=False).head(top_n)
        fig_bar, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x=top_appliances.values, y=top_appliances.index, palette="viridis", ax=ax)
        ax.set_title(f"Top {top_n} Consuming Appliances")
        ax.set_xlabel("Total VAh")
        bar_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        fig_bar.tight_layout()
        fig_bar.savefig(bar_img_path, dpi=100)
        plt.close(fig_bar)

        # Heatmap
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(df_resampled.T, cmap="YlGnBu", cbar_kws={"label": "VAh"}, ax=ax)
        ax.set_title("Appliance Usage Heatmap")
        plt.tight_layout()
        heatmap_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        fig.savefig(heatmap_img_path, dpi=100)
        plt.close(fig)

        # -----------------------
        # Build PDF
        # -----------------------
        class VisualPDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 14)
                self.cell(0, 10, "Visual Energy Usage Report", ln=True, align="C")
                self.set_font("Arial", "", 10)
                self.cell(0, 8, f"Generated: {timestamp}", ln=True, align="C")
                self.ln(5)

        pdf = VisualPDF()
        pdf.add_page()

        # Line Plot
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Power Usage Over Time", ln=True)
        pdf.image(line_img_path, w=180)

        # Top N Bar
        pdf.ln(5)
        pdf.cell(0, 10, f"Top {top_n} Energy Consumers", ln=True)
        pdf.image(bar_img_path, w=160)

        # Heatmap
        pdf.ln(5)
        pdf.cell(0, 10, "Usage Heatmap", ln=True)
        pdf.image(heatmap_img_path, w=180)

        # Summary Stats
        pdf.ln(5)
        pdf.cell(0, 10, "Quick Stats", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 8, f"Top Appliance: {top_appliance} ({top_val:.2f} VAh)\nSelected Appliances: {selected_appliances}\nTimeframe: {date_range}")

        # Anomaly Table
        if not anomaly_summary.empty:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Anomaly Summary", ln=True)
            pdf.set_font("Arial", "", 10)
            for i, row in anomaly_summary.iterrows():
                pdf.cell(0, 8, f"- {row['Appliance']}: {row['Anomalies']} anomalies", ln=True)

        # Export PDF
        temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        pdf.output(temp_pdf_path)

        with open(temp_pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Visual PDF Report",
                data=f,
                file_name="energy_visual_report.pdf",
                mime="application/pdf"
            )

    else:
        st.info("⏳ Click the button above to generate a PDF report with visual insights.")
