import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# โหลดข้อมูล
df = pd.read_parquet("merged_cleaned_data_small.parquet") 
# โหลดข้อมูลการพยากรณ์จากไฟล์ CSV
forecast_df = pd.read_parquet("forecast_df.parquet")

# สร้างยอดขายรายปี
forecast_df["year"] = forecast_df["date"].dt.year
annual_sales = forecast_df.groupby(["year", "model"])["sales"].sum().reset_index()


# Sidebar: Filter options
st.sidebar.header("📊 Filter Options")

# ✅ แสดงช่วงวันที่ของข้อมูล
st.sidebar.markdown(f"**🗓 Data available from:** `{df['date'].min().date()}` to `{df['date'].max().date()}`")

# เลือกตัวกรองร้าน/คลัสเตอร์/สินค้า
store_types = st.sidebar.multiselect("Store Type", options=df["type"].unique(), default=df["type"].unique())
clusters = st.sidebar.multiselect("Cluster", options=df["cluster"].unique(), default=df["cluster"].unique())
families = st.sidebar.multiselect("Product Family", options=df["family"].unique(), default=df["family"].unique())

# Date Picker
min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Apply filters
df_filtered = df[
    df["type"].isin(store_types) &
    df["cluster"].isin(clusters) &
    df["family"].isin(families) &
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1]))
]

# Title
st.title("📈 Sales Dashboard - Favorita Dataset")

# KPI Section
st.subheader("📌 Key Performance Indicators")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🛒 Total Sales", f"${df_filtered['sales'].sum():,.0f}")
with col2:
    st.metric("📆 Avg Daily Sales", f"${df_filtered.groupby('date')['sales'].sum().mean():,.2f}")
with col3:
    st.metric("🏪 Active Stores", df_filtered["store_nbr"].nunique())

# Chart 1: Total Sales Over Time
# 🔄 สร้างกราฟที่ดูง่ายขึ้น
# 🔄 กราฟแนวโน้มยอดขายรายวัน + ค่าเฉลี่ย 7 วัน
st.subheader("🕒 Total Sales Over Time (with 7-day Rolling Average)")
daily_sales = df_filtered.groupby("date")["sales"].sum().reset_index()
daily_sales["rolling_sales"] = daily_sales["sales"].rolling(window=7).mean()

# กราฟเส้นปกติ
fig1 = px.line(daily_sales, x="date", y="sales", title="Total Sales by Day", 
               labels={"sales": "Daily Sales", "date": "Date"})

# ปรับความโปร่งของกราฟเส้นรายวัน
fig1.update_traces(opacity=0.3, name="Daily Sales", line=dict(color="lightblue"))

# เพิ่มเส้นค่าเฉลี่ย 7 วัน
fig1.add_scatter(x=daily_sales["date"], y=daily_sales["rolling_sales"], 
                 mode="lines", name="7-Day Avg", line=dict(color="orange", width=3))

# ปรับ layout
fig1.update_layout(
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    hovermode="x unified"
)

st.plotly_chart(fig1, use_container_width=True)


# Chart 2: Average Sales by Store Type
st.subheader("🏪 Average Sales per Store Type")
avg_sales_type = df_filtered.groupby("type")["sales"].mean().reset_index()
fig2 = px.bar(avg_sales_type, x="type", y="sales", title="Average Sales by Store Type", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Total Sales by Product Family
st.subheader("🧺 Total Sales by Product Family")
family_sales = df_filtered.groupby("family")["sales"].sum().reset_index().sort_values("sales", ascending=True)
fig3 = px.bar(family_sales, x="sales", y="family", orientation="h", title="Total Sales by Product Family")
st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Top 10 Performing Stores
st.subheader("🏆 Top 10 Stores by Total Sales")
top_stores = df_filtered.groupby("store_nbr")["sales"].sum().reset_index().sort_values("sales", ascending=False).head(10)
fig4 = px.bar(top_stores, x="store_nbr", y="sales", title="Top 10 Stores by Sales", text_auto=True)
st.plotly_chart(fig4, use_container_width=True)

# Chart 5: Seasonality Trend
st.subheader("📆 Seasonality Trend: Sales by Month")
monthly = df_filtered.groupby(df_filtered["date"].dt.to_period("M"))["sales"].sum().reset_index()
monthly["date"] = monthly["date"].astype(str)
fig5 = px.line(monthly, x="date", y="sales", title="Monthly Sales Trend", markers=True)
st.plotly_chart(fig5, use_container_width=True)

# Chart 6: Sales Share by Cluster
st.subheader("🧩 Sales Proportion by Cluster")
sales_cluster = df_filtered.groupby("cluster")["sales"].sum().reset_index()
fig6 = px.pie(sales_cluster, names="cluster", values="sales", title="Sales Share by Cluster")
st.plotly_chart(fig6, use_container_width=True)

# Heatmap
# 🔥 Sales Heatmap: Day of Week vs Month
st.subheader("🔥 Sales Heatmap: Day of Week vs Month")

# เพิ่มการเรียงวันให้ถูกต้อง
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
df_filtered["dayofweek"] = pd.Categorical(df_filtered["date"].dt.day_name(), categories=days_order, ordered=True)
df_filtered["month"] = df_filtered["date"].dt.strftime("%b")

# สร้างตาราง heatmap
heatmap_data = df_filtered.groupby(["dayofweek", "month"])["sales"].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index="dayofweek", columns="month", values="sales")

# เรียงเดือนตามลำดับ
months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
heatmap_pivot = heatmap_pivot[months_order]  # เรียง column ใหม่

# แสดงตารางพร้อมการจัดสีสวยงาม
st.write(
    heatmap_pivot.style
        .format("{:,.0f}")
        .background_gradient(cmap='Blues', axis=None)
        .set_properties(**{'text-align': 'center'})
        .set_table_styles([{
            'selector': 'th',
            'props': [('text-align', 'center')]
        }])
)

import plotly.express as px
import streamlit as st
import pandas as pd

st.subheader("📅 Annual Sales Forecast (2017–2027) by Model")

fig_forecast = px.line(
    annual_sales,
    x="year",
    y="sales",
    color="model",
    markers=True,
    title="Predicted Annual Sales by Model (Next 10 Years)"
)

fig_forecast.update_layout(
    xaxis_title="Year",
    yaxis_title="Total Predicted Sales",
    hovermode="x unified"
)

st.plotly_chart(fig_forecast, use_container_width=True)
# เพิ่มฟีเจอร์เดือนและปี
df["year_month"] = df["date"].dt.to_period("M").dt.to_timestamp()

# สรุปยอดขายรายเดือนแต่ละ cluster
monthly_cluster_sales = df.groupby(["year_month", "cluster"])["sales"].sum().reset_index()
monthly_cluster_sales["prev_sales"] = monthly_cluster_sales.groupby("cluster")["sales"].shift(1)
monthly_cluster_sales["change_percent"] = ((monthly_cluster_sales["sales"] - monthly_cluster_sales["prev_sales"]) / monthly_cluster_sales["prev_sales"]) * 100

# เพิ่มคำแนะนำเชิงกลยุทธ์
def recommend_strategy(row):
    if pd.isna(row["change_percent"]):
        return "N/A"
    elif row["change_percent"] < -10:
        return "🔻 โปรโมชัน/จัดรายการกระตุ้นยอดขาย"
    elif row["change_percent"] > 10:
        return "📈 ขยายสต็อก/ขยายสาขา"
    else:
        return "✅ รักษาระดับตามแผน"

monthly_cluster_sales["recommendation"] = monthly_cluster_sales.apply(recommend_strategy, axis=1)

# Dashboard ส่วนใหม่
st.subheader("📉 Cluster Monthly KPI Monitor")

# กราฟเปรียบเทียบยอดขาย
fig_cluster_line = px.line(
    monthly_cluster_sales,
    x="year_month",
    y="sales",
    color="cluster",
    title="ยอดขายรายเดือนแยกตาม Cluster",
    markers=True,
)
st.plotly_chart(fig_cluster_line, use_container_width=True)

# ตาราง Insight พร้อมคำแนะนำ
st.subheader("📋 สรุปยอดขายรายเดือนพร้อมคำแนะนำเชิงกลยุทธ์")
st.dataframe(
    monthly_cluster_sales[["year_month", "cluster", "sales", "change_percent", "recommendation"]]
    .sort_values(by=["year_month", "cluster"]),
    use_container_width=True
)
# เพิ่มเข้าไปในส่วนท้ายของ dashboard เดิม (เช่น หลังจาก section แรก ๆ ที่ plot graph รายวัน/รายปี)

import pandas as pd
import plotly.express as px

# --- เตรียมข้อมูล ---
df["year_month"] = df["date"].dt.to_period("M").astype(str)

monthly_cluster_sales = (
    df.groupby(["cluster", "year_month"])["sales"]
    .sum()
    .reset_index()
)

top_n = 5  # จำนวน cluster สูงสุดที่จะนำมาแสดง
top_clusters = (
    monthly_cluster_sales.groupby("cluster")["sales"]
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .index.tolist()
)

filtered_df = monthly_cluster_sales[monthly_cluster_sales["cluster"].isin(top_clusters)]

# --- สร้างกราฟ ---
fig_cluster_line = px.line(
    filtered_df,
    x="year_month",
    y="sales",
    color="cluster",
    title=f"📊 ยอดขายรายเดือน (Top {top_n} Cluster เท่านั้น)",
    markers=True,
)

fig_cluster_line.update_layout(
    xaxis_title="เดือน",
    yaxis_title="ยอดขายรวม",
    legend_title="Cluster",
    height=500,
    template="plotly_dark",
)

fig_cluster_line.update_traces(mode="lines+markers", line=dict(width=3))

# --- แสดงกราฟบน Dashboard ---
st.plotly_chart(fig_cluster_line, use_container_width=True)
st.subheader("🧠 Strategic Insights by Cluster")

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔼 Cluster 3, 5, 8")
        st.success(
            """
            **Insight:** Strong and growing sales.  
            **Strategy:**  
            - Expand inventory capacity  
            - Run loyalty & VIP programs  
            - Target high-spending customers  
            """
        )

    with col2:
        st.markdown("### 🔁 Cluster 2, 6, 10")
        st.info(
            """
            **Insight:** Sales are steady but flat.  
            **Strategy:**  
            - A/B test promotions  
            - Update product selection  
            - Monitor competitor activity  
            """
        )

    with col3:
        st.markdown("### 🔻 Cluster 1, 7, 11")
        st.warning(
            """
            **Insight:** Sales declining over time.  
            **Strategy:**  
            - Investigate churn causes  
            - Offer aggressive discounts  
            - Launch reactivation campaigns  
            """
        )

# Optional separator or summary
st.markdown("---")
st.markdown("""
📌 **Note:** These strategic suggestions are based on historical trends. Regularly monitor KPIs and validate via experiments.
""")
# 📌 ส่วน: Simulate Strategy
st.subheader("🧪 Strategy Simulation")

increase_pct = st.slider("📈 เพิ่มยอดขาย (%)", min_value=0, max_value=100, value=10, step=5)

simulate = st.button("🚀 Simulate Strategy")
if simulate:
    df_simulated = df_filtered.copy()
    df_simulated["sales"] = df_simulated["sales"] * (1 + increase_pct / 100)

    monthly_before = df_filtered.groupby(df_filtered["date"].dt.to_period("M"))["sales"].sum().reset_index()
    monthly_before["date"] = monthly_before["date"].astype(str)
    monthly_before["strategy"] = "Before"

    monthly_after = df_simulated.groupby(df_simulated["date"].dt.to_period("M"))["sales"].sum().reset_index()
    monthly_after["date"] = monthly_after["date"].astype(str)
    monthly_after["strategy"] = "After"

    compare_df = pd.concat([monthly_before, monthly_after])

    fig_sim = px.line(compare_df, x="date", y="sales", color="strategy",
                      title="📊 Monthly Sales: Before vs After Strategy",
                      markers=True)

    st.plotly_chart(fig_sim, use_container_width=True)

    delta = monthly_after["sales"].sum() - monthly_before["sales"].sum()
    percent_change = (delta / monthly_before["sales"].sum()) * 100

    st.success(f"✅ ยอดขายเพิ่มขึ้น {percent_change:.2f}% จากการจำลองกลยุทธ์")
else:
    st.info("กดปุ่ม 🚀 Simulate Strategy เพื่อดูผลกระทบจากกลยุทธ์ใหม่")

