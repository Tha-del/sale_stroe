# 🧠 Favorita Sales Forecasting Dashboard

Interactive dashboard for analyzing and forecasting sales data from the Favorita dataset.  
Built with **Streamlit** and **Plotly**, it provides insights, trends, and strategy simulations to help businesses boost performance.

---

## 📂 Dataset Overview

### 1. `merged_cleaned_data_full.parquet`

ข้อมูลนี้คือชุดรวมของ:
- Historical sales
- Store metadata
- Holidays
- Transactions
- Oil prices

| Column         | Description                                  |
|----------------|----------------------------------------------|
| `date`         | วันที่ขายสินค้า (format: YYYY-MM-DD)         |
| `store_nbr`    | หมายเลขร้านค้า                              |
| `family`       | หมวดหมู่ของสินค้า                            |
| `sales`        | ยอดขาย (ในหน่วยดอลลาร์)                     |
| `onpromotion`  | จำนวนสินค้าที่จัดโปรโมชั่นในวันนั้น         |
| `city`         | เมืองที่ตั้งร้าน                             |
| `state`        | รัฐ/จังหวัด                                  |
| `type`         | ประเภทของร้านค้า (A, B, C, D, E)            |
| `cluster`      | กลุ่มร้านที่มีลักษณะคล้ายกัน               |
| `transactions` | จำนวนธุรกรรมที่เกิดขึ้นในวันนั้น             |
| `dcoilwtico`   | ราคาน้ำมันดิบ (WTI oil price)                |
| `holiday_type` | ประเภทวันหยุด (Holiday / Event / Transfer) |
| `day_of_week`  | ชื่อวันในสัปดาห์ (Monday–Sunday)           |
| `month`        | เดือนที่เกิดยอดขาย                          |
| `year`         | ปีของการขาย                                  |

---

### 2. `forecast_df.parquet`

ข้อมูลยอดขายในอนาคตที่สร้างจาก Time Series Models  
มีการใช้หลายโมเดล (เช่น Prophet, ARIMA, LightGBM ฯลฯ) ในการพยากรณ์ยอดขายไปอีก 10 ปีข้างหน้า (2017–2027)

| Column | Description             |
|--------|-------------------------|
| `date` | วันที่พยากรณ์           |
| `sales`| ยอดขายที่พยากรณ์ไว้     |
| `model`| ชื่อโมเดลที่ใช้พยากรณ์ |

---

## 📊 Features

- Filter by store type, cluster, product family, and time range
- Show real-time KPIs
- Daily & monthly sales trend
- Heatmap: sales by weekday/month
- Sales share by cluster
- Forecasting from multiple ML models
- 💡 Strategy simulation with before-after comparison
- 🔁 Recommendations per cluster based on KPI trend

---

