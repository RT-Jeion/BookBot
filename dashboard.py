# dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from orders import get_orders, update_order_status
from courier import book_shipment
import time

def init_session_state():
    if "orders" not in st.session_state:
        st.session_state.orders = []
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = datetime.now()

def load_orders():
    orders = get_orders()
    df = pd.DataFrame(orders)
    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.sort_values('created_at', ascending=False)
    return df

# === PAGE CONFIG ===
st.set_page_config(page_title="BookBot Admin", layout="wide")
init_session_state()

# Header
col1, col2 = st.columns([3,1])
with col1:
    st.title("📚 BookBot Admin Dashboard")
with col2:
    if st.button("🔄 Refresh"):
        st.session_state.last_refresh = datetime.now()
        st.experimental_rerun()

st.caption(f"Last refreshed: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")

# Stats
df = load_orders()
if not df.empty:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", len(df))
    with col2:
        pending = len(df[df['status'] == 'Pending'])
        st.metric("Pending Orders", pending)
    with col3:
        completed = len(df[df['status'] == 'Delivered'])
        st.metric("Completed Orders", completed)
    
    # Orders Table
    st.subheader("Recent Orders")
    
    # Filter controls
    col1, col2 = st.columns([2,2])
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=df['status'].unique()
        )
    with col2:
        date_filter = st.date_input(
            "Filter by Date",
            value=(datetime.now() - timedelta(days=7))
        )
    
    # Apply filters
    filtered_df = df
    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
    if date_filter:
        filtered_df = filtered_df[filtered_df['created_at'].dt.date >= date_filter]
    
    # Display orders
    st.dataframe(
        filtered_df,
        column_config={
            "order_id": st.column_config.TextColumn("Order ID"),
            "created_at": st.column_config.DatetimeColumn("Created"),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Pending", "Processing", "Shipped", "Delivered"]
            )
        },
        hide_index=True
    )
    
else:
    st.info("No orders found. Start taking orders via Telegram!")