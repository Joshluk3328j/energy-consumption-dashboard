# ⚡ Cleaned Energy Dashboard – UK-DALE

This project presents an interactive energy monitoring dashboard and reporting tool built with **Streamlit**, using appliance-level data from the [UK-DALE (UK Domestic Appliance-Level Electricity)](https://jack-kelly.com/data/) dataset. It provides real-time insights, visualizations, and downloadable reports based on cleaned and manually processed energy usage data.

---

## 📁 Dataset Overview

- **Source**: UK-DALE (UK Domestic Appliance-Level Electricity)
- **House**: House 1 (November 2012 – April 2013)
- **Granularity**:
  - Appliance readings: 1-second resolution
  - Converted to VAh (Volt-Ampere-Hours)
- **Channels**: Over 50 sub-metered appliances (kettle, fridge, laptop, dishwasher, etc.)
- **Aggregate Channel**: Reconstructed manually as the sum of all appliances

---

## 🎯 Project Goals

- ✅ Clean and align raw `.dat` appliance files
- ✅ Reconstruct aggregate usage
- ✅ Convert apparent power readings (VA) to energy (VAh)
- ✅ Visualize energy usage per appliance over time
- ✅ Detect anomalies in appliance consumption
- ✅ Generate downloadable visual PDF reports
- ✅ Deliver insights via an interactive Streamlit dashboard

---

## 🛠️ Tools & Technologies

| Tool         | Purpose                                  |
|--------------|-------------------------------------------|
| `pandas`     | Data processing and wrangling             |
| `matplotlib` | Static plotting for reports               |
| `plotly`     | Interactive charts in dashboard           |
| `seaborn`    | Heatmaps and statistical visuals          |
| `scipy`      | Anomaly detection (Z-score)               |
| `Streamlit`  | Web interface and dashboard framework     |
| `FPDF`       | PDF report generation                     |

---

## 🧪 Workflow Summary

### 🔹 Data Cleaning & Processing
- All `.dat` files were parsed individually and aligned using a shared timestamp window.
- VA values were converted to VAh assuming 1-second sampling intervals:

  \[
  \text{VAh} = \frac{\text{VA}}{3600}
  \]

- New aggregate was generated as the sum of all appliances.
- Files were exported into a new cleaned format (`cleaned_house1/`).

### 🔹 Dashboard Features

#### 📊 Tab 1: Dashboard
- Appliance selection and time-based resampling (Hourly, Daily, Weekly, Monthly)
- Line chart of consumption
- Key metrics (total usage, average per appliance, top consumer)
- Anomaly detection using Z-score
- Raw data viewer

#### 📋 Tab 2: Report Generator
- Generates a **visual PDF report** including:
  - Power usage line chart
  - Top 10 consumers bar chart
  - Appliance usage heatmap
  - Summary stats and anomaly table
- Allows download of the report

---

## 📦 Folder Structure

