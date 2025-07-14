# ⚡ Energy Consumption Dashboard

An interactive Streamlit dashboard for visualizing and analyzing cleaned energy usage data from the UK-DALE dataset (or similar format). It supports multiple appliances, anomaly detection, custom date filtering, and automated PDF report generation.

---

## 📌 Features

- 🗕️ **Custom Date Range Selection**
- 🧰 **Multi-Appliance Selection** with optional "Select All"
- 📉 **Interactive Line Charts** using Plotly
- 🚨 **Anomaly Detection** via Z-score method (excluding aggregate)
- 📊 **Usage Metrics & Summary Stats**
- 🖼️ **Auto-Generated Visuals**: Line Plot, Bar Chart, and Heatmap
- 📄 **PDF Report Export** with embedded visualizations

---

## 📷 Screenshot

!()

---

## 📁 Directory Structure

```
project/
│
├── cleaned_house1/              # Folder with .dat files and labels.dat
│   ├── channel_1.dat
│   ├── channel_2.dat
│   └── labels.dat
│
├── dashboard.py                 # Main Streamlit app file
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/energy-dashboard.git
cd energy-dashboard
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit App

```bash
streamlit run dashboard.py
```

Make sure your `.dat` files are inside a folder named `cleaned_house1/` in the same directory.

---

## 🧪 Example Dataset Format

Ensure your `cleaned_house1/` folder includes:

- `labels.dat`:

  ```
  1 aggregate
  2 kettle
  3 microwave
  ```

- `channel_1.dat`, `channel_2.dat`, ...:

  ```
  1351534170 180
  1351534230 190
  ```

---

## 📦 Requirements

- Python 3.8+
- Streamlit
- Pandas
- Plotly
- Seaborn
- Matplotlib
- SciPy
- FPDF
- pathlib

You can install everything with:

```bash
pip install -r requirements.txt
```

---

## 📄 PDF Report

Click the **📄 Generate Analysis Report** button in the app to generate a downloadable PDF report with:

- Summary stats
- Line chart
- Bar chart
- Heatmap
- Anomaly summary

---

## Credits

Created by [Babatunde Joseph](https://github.com/Joshluk3328j)

### contributors: 
- [Maria](https://github.com/CodeMorpheus0)
- Musa Jafar
- Dorris
- Kelechi
- [Bethel](https://github.com/nnajibethel)

Uses data in the format of [UK-DALE Dataset](https://jack-kelly.com/data/)

---

## 📓 License

This project is licensed under the [MIT License](LICENSE).
