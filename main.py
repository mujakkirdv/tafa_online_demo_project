import streamlit as st
import pandas as pd
from io import BytesIO
import os
import plotly.express as px
from PIL import Image
import datetime
from datetime import datetime as dt
import matplotlib.pyplot as plt



# ✅ Excel file paths
sales_data = "sales_register.xlsx"
cashbook_data = "cashbook.xlsx"
bankbook_data = "bankbook.xlsx"
purchase_data = "purchase_sales_demo.xlsx"

# Page configuration
st.set_page_config(
    page_title="TAFA Women's Cooperative",
    page_icon="📊",
    layout="wide"
)

# ✅ Load data functions
@st.cache_data
def load_sales():
    return pd.read_excel(sales_data)

@st.cache_data
def load_cashbook():
    return pd.read_excel(cashbook_data)

@st.cache_data
def load_bankbook():
    return pd.read_excel(bankbook_data)

@st.cache_data
def load_purchase():
    return pd.read_excel(purchase_data)

# ✅ Store data in separate variables
df_sales = load_sales()

df_cash = load_cashbook()
df_bank = load_bankbook()
df_purchase = load_purchase()


# Sidebar navigation
page = st.sidebar.radio(
    "✨ Menu",
    (
        "🏠 Home",
        "📍 Dashboard",
        "💸 Sales Analysis",
        "🏦 Bankbook",
        "💵 Cashbook",
        "🧾 Purchase",
        "📉 Liability",
        "📈 Profit & Loss",
        "📊 Charts",
        "📚 About",
    )
)

# ✅ Example: Show preview depending on menu
if page == "🏠 Home":
    st.title("🏠 TAFA Women's Cooperative")
    st.header("Tafa Finance and Accounting Dashboard")

    # --- Company Info ---
    st.subheader("🏢 Company Information")
    st.write("""
    **Company Name:** TAFA Women's Cooperative  
    **Address:** Dhaka, Bangladesh  
    **Established:** 2025  
    **Business:** Women's Clothing & Accessories  
    """)

    # --- Date Filter ---
    st.subheader("📅 Select Date Range")
    start_date = st.date_input("Start Date", pd.to_datetime(df_sales["date"]).min())
    end_date = st.date_input("End Date", pd.to_datetime(df_sales["date"]).max())

    # Filter data
    df_sales["date"] = pd.to_datetime(df_sales["date"])
    sales_filtered = df_sales[(df_sales["date"] >= pd.to_datetime(start_date)) & (df_sales["date"] <= pd.to_datetime(end_date))]

    # --- KPIs ---
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Sales", f"{sales_filtered['total_amount'].sum():,.2f}")
    col2.metric("🧾 Outstanding", f"{sales_filtered.loc[sales_filtered['payment_status']!='Paid','total_amount'].sum():,.2f}")
    col3.metric("📊 Transactions", f"{len(sales_filtered)} invoices")

    col4, col5, col6 = st.columns(3)
    col4.metric("💵 Total Income", f"{df_cash['Cash_In'].sum():,.2f}") 
    col5.metric("📉 Total Expense", f"{(df_cash['Cash_In'][df_cash['Type']=='Expense']).sum():,.2f}" if "Type" in df_cash else "Need 'Type' column")
    col6.metric("🏦 Bank Deposit", f"{df_bank['Deposit_Amount'].sum():,.2f}" if "Deposit_Amount" in df_bank else "Need 'Deposit_Amount' column")

    col7, col8 = st.columns(2)
    col7.metric("🏦 Bank Withdrawal", f"{df_bank['Withdrawal_Amount'].sum():,.2f}" if "Withdrawal_Amount" in df_bank else "Need 'Withdrawal_Amount' column")
    col8.metric("📱 Mobile Banking", f"{sales_filtered.loc[sales_filtered['payment_method'].isin(['bKash','Nagad','Rocket']), 'total_amount'].sum():,.2f}")


elif page == "📍 Dashboard":
    st.title("📍 Dashboard Overview")

    # --- Sales KPIs ---
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Sales", f"{df_sales['total_amount'].sum():,.2f}")
    col2.metric("📦 Total Products Sold", f"{df_sales['quantity'].sum():,.0f}")
    col3.metric("🧾 Total Invoices", len(df_sales))

    # --- Category-wise Product Sales ---
    st.subheader("📊 Category-wise Product Sales")
    cat_sales = df_sales.groupby("category")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False)
    fig1 = px.bar(cat_sales, x="category", y="total_amount", color="category", title="Sales by Category")
    st.plotly_chart(fig1, use_container_width=True)

    # --- Cashbook Analysis (Income vs Expense by Category) ---
    st.subheader("💵 Cashbook: Income & Expense by Category")
    cash_summary = df_cash.groupby("Payment_category")[["Cash_In","Cash_Out"]].sum().reset_index()

    fig2 = px.bar(
        cash_summary.melt(id_vars="Payment_category", value_vars=["Cash_In","Cash_Out"]),
        x="Payment_category", y="value", color="variable",
        barmode="group", title="Cashbook Income vs Expense by Category"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- Bankbook Analysis (Deposit vs Withdrawal by Category) ---
    if "Cash_In" in df_bank.columns and "Cash_Out" in df_bank.columns:
        st.subheader("🏦 Bankbook: Deposit vs Withdrawal by Category")
        bank_summary = df_bank.groupby("Payment_category")[["Cash_In","Cash_Out"]].sum().reset_index()

        fig3 = px.bar(
            bank_summary.melt(id_vars="Payment_category", value_vars=["Cash_In","Cash_Out"]),
            x="Payment_category", y="value", color="variable",
            barmode="group", title="Bankbook Deposit vs Withdrawal"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # --- Extra Insights ---
    st.subheader("📈 Additional Insights")
    col4, col5 = st.columns(2)
    top_customer = df_sales.groupby("customer_name")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False).head(1)
    col4.metric("👤 Top Customer", f"{top_customer.iloc[0]['customer_name']} ({top_customer.iloc[0]['total_amount']:,.2f})")

    top_product = df_sales.groupby("product_name")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False).head(1)
    col5.metric("⭐ Best Product", f"{top_product.iloc[0]['product_name']} ({top_product.iloc[0]['total_amount']:,.2f})")


# ----------------- SALES ANALYSIS PAGE -----------------
elif page == "💸 Sales Analysis":
    st.header("💸 Sales Analysis")

    # ---- Date Range Filter ----
    df_sales['date'] = pd.to_datetime(df_sales['date'], errors='coerce')
    min_date, max_date = df_sales['date'].min(), df_sales['date'].max()
    start_date, end_date = st.date_input(
        "Select Date Range", [min_date, max_date]
    )
    mask = (df_sales['date'] >= pd.to_datetime(start_date)) & (df_sales['date'] <= pd.to_datetime(end_date))
    filtered_df = df_sales.loc[mask]

    if filtered_df.empty:
        st.warning("No sales records found for this date range.")
    else:
        # ---- Total Sales ----
        total_sales = filtered_df['total_amount'].sum() 
        st.metric("💰 Total Sales", f"{total_sales:,.2f}")

        # ---- Sold_by Wise Sales ----
        if "Sold_By" in filtered_df.columns:
            sold_by_sales = filtered_df.groupby("Sold_By")['total_amount'].sum().reset_index()
            st.subheader("👨‍💼 Sales by Modarator & Executive")
            st.dataframe(sold_by_sales)

            fig = px.bar(sold_by_sales, x="Sold_By", y="total_amount", title="Sales by Seller", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

        # ---- Category Wise Product Sales & Income ----
        if "Category" in filtered_df.columns and "quantity" in filtered_df.columns:
            cat_sales = filtered_df.groupby("category").agg(
                Total_Sales=("total_amount", "sum"),
                Total_Quantity=("quantity", "sum")
            ).reset_index()

            st.subheader("📦 Category-wise Sales & Income")
            st.dataframe(cat_sales)

            # Bar chart for Sales
            fig1 = px.bar(cat_sales, x="category", y="Total_Sales",
                          title="Category-wise Total Sales", text_auto=True)
            st.plotly_chart(fig1, use_container_width=True)

            # Bar chart for Quantity
            fig2 = px.bar(cat_sales, x="category", y="Total_Quantity",
                          title="Category-wise Total Quantity Sold", text_auto=True)
            st.plotly_chart(fig2, use_container_width=True)

        # ---- Drill-Down Button ----
        st.subheader("🔍 Drill-Down Report")
        drill = st.selectbox("Select Drill-Down Dimension", ["category", "Sold_By", "Date"])
        
        if drill:
            drill_df = filtered_df.groupby(drill).agg(
                Total_Sales=("total_amount", "sum"),
                Total_Quantity=("quantity", "sum")
            ).reset_index()
            st.dataframe(drill_df)

            fig3 = px.bar(drill_df, x=drill, y="Total_Sales",
                          title=f"{drill}-wise Sales Drilldown", text_auto=True)
            st.plotly_chart(fig3, use_container_width=True)



# ----------------- BANKBOOK MANAGEMENT PAGE -----------------

# 🏦 Bankbook Page
elif page == "🏦 Bankbook":
    st.title("🏦 Bankbook Analysis")

    # Load Bankbook
    @st.cache_data
    def load_bankbook():
        df = pd.read_excel(bankbook_data)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df

    bank_df = load_bankbook()

    # 📅 Date filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", bank_df["Date"].min())
    with col2:
        end_date = st.date_input("End Date", bank_df["Date"].max())

    mask = (bank_df["Date"] >= pd.to_datetime(start_date)) & (bank_df["Date"] <= pd.to_datetime(end_date))
    bank_df = bank_df.loc[mask]

    # 📊 Metrics
    total_deposit = bank_df["Deposit_Amount"].sum()
    total_withdrawal = bank_df["Withdrawal_Amount"].sum()
    net_balance = total_deposit - total_withdrawal

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Deposits", f"{total_deposit:,.0f}")
    c2.metric("💸 Total Withdrawals", f"{total_withdrawal:,.0f}")
    c3.metric("📌 Net Cashflow", f"{net_balance:,.0f}")

    # 🔍 Fund Source Wise Summary
    st.subheader("📍 Fund Source Breakdown")
    fund_summary = bank_df.groupby("fund_source").agg(
        Deposits=("Deposit_Amount", "sum"),
        Withdrawals=("Withdrawal_Amount", "sum"),
        Net=("Balance", "last")
    ).reset_index()

    st.dataframe(fund_summary)

    # 📊 Bar Charts
    st.subheader("📊 Deposits vs Withdrawals by Fund Source")
    fig, ax = plt.subplots()
    fund_summary.set_index("fund_source")[["Deposits", "Withdrawals"]].plot(kind="bar", ax=ax)
    st.pyplot(fig)

    # 📈 Trend Over Time
    st.subheader("📈 Bank Transactions Over Time")
    time_summary = bank_df.groupby("Date").agg(
        Deposits=("Deposit_Amount", "sum"),
        Withdrawals=("Withdrawal_Amount", "sum")
    ).reset_index()

    fig2, ax2 = plt.subplots()
    ax2.plot(time_summary["Date"], time_summary["Deposits"], label="Deposits", marker="o")
    ax2.plot(time_summary["Date"], time_summary["Withdrawals"], label="Withdrawals", marker="o", color="red")
    ax2.legend()
    ax2.set_title("Daily Bank Transactions")
    st.pyplot(fig2)

    # 📂 Drill-down
    with st.expander("🔎 View Detailed Transactions"):
        st.dataframe(bank_df)



elif page == "💵 Cashbook":
    st.title("💵 Cashbook")

    # Load data
    cashbook = load_cashbook()
    
    # Debug: Show available columns
    st.write("📊 Available columns:", list(cashbook.columns))

    # Ensure all required columns exist, if not create them
    required_cols = ["Date", "Voucher_No", "Description", "Name", "Payment_category", "Reference", "Cash_In", "Cash_Out"]
    
    for col in required_cols:
        if col not in cashbook.columns:
            if col in ["Cash_In", "Cash_Out"]:
                cashbook[col] = 0.0
            else:
                cashbook[col] = ""

    # Ensure correct datetime format
    cashbook["Date"] = pd.to_datetime(cashbook["Date"], errors="coerce")

    # Fill NaN values in category column with "Uncategorized"
    cashbook["Payment_category"] = cashbook["Payment_category"].fillna("Uncategorized")

    # Convert numeric columns safely
    cashbook["Cash_In"] = pd.to_numeric(cashbook["Cash_In"], errors="coerce").fillna(0)
    cashbook["Cash_Out"] = pd.to_numeric(cashbook["Cash_Out"], errors="coerce").fillna(0)

    # Calculate Balance
    cashbook["Balance"] = cashbook["Cash_In"] - cashbook["Cash_Out"]

    # Categorize the categories into broader groups for better analysis
    def categorize_payment(payment_type):
        payment_type = str(payment_type).lower()
        if payment_type in ['sales']:
            return 'Income'
        elif payment_type in ['expense', 'payable']:
            return 'Expenses'
        elif payment_type in ['receivedable', 'receivable']:
            return 'Receivables'
        elif payment_type in ['laibility', 'liability']:
            return 'Liabilities'
        else:
            return 'Other'

    cashbook["Category_Group"] = cashbook["Payment_category"].apply(categorize_payment)

    # Date filter
    min_date = cashbook["Date"].min().date() if not cashbook.empty else datetime.date.today()
    max_date = cashbook["Date"].max().date() if not cashbook.empty else datetime.date.today()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    # Filter by date range
    mask = (cashbook["Date"] >= pd.to_datetime(start_date)) & (cashbook["Date"] <= pd.to_datetime(end_date))
    filtered = cashbook.loc[mask]

    if not filtered.empty:
        # ✅ Detailed Category-wise summary
        st.subheader("📊 Detailed Category-wise Analysis")
        
        cat_summary = filtered.groupby("Payment_category").agg({
            "Cash_In": "sum",
            "Cash_Out": "sum",
            "Date": "count"
        }).rename(columns={"Date": "Transaction_Count"}).reset_index()

        cat_summary["Net_Cash_Flow"] = cat_summary["Cash_In"] - cat_summary["Cash_Out"]
        cat_summary = cat_summary.sort_values("Net_Cash_Flow", ascending=False)

        # ✅ Broad Category Group summary
        group_summary = filtered.groupby("Category_Group").agg({
            "Cash_In": "sum",
            "Cash_Out": "sum",
            "Date": "count"
        }).rename(columns={"Date": "Transaction_Count"}).reset_index()

        group_summary["Net_Cash_Flow"] = group_summary["Cash_In"] - group_summary["Cash_Out"]
        group_summary = group_summary.sort_values("Net_Cash_Flow", ascending=False)

        # Show metrics
        total_in = filtered["Cash_In"].sum()
        total_out = filtered["Cash_Out"].sum()
        net_balance = total_in - total_out

        st.subheader("💰 Overall Cash Flow Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cash In", f"৳{total_in:,.2f}")
        col2.metric("Total Cash Out", f"৳{total_out:,.2f}")
        col3.metric("Net Balance", f"৳{net_balance:,.2f}")
        col4.metric("Total Transactions", f"{len(filtered)}")

        # Display both summaries side by side
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Detailed Categories")
            display_cat = cat_summary.copy()
            display_cat["Cash_In"] = display_cat["Cash_In"].apply(lambda x: f"৳{x:,.2f}")
            display_cat["Cash_Out"] = display_cat["Cash_Out"].apply(lambda x: f"৳{x:,.2f}")
            display_cat["Net_Cash_Flow"] = display_cat["Net_Cash_Flow"].apply(lambda x: f"৳{x:,.2f}")
            st.dataframe(display_cat, use_container_width=True, height=300)

        with col2:
            st.subheader("📋 Category Groups")
            display_group = group_summary.copy()
            display_group["Cash_In"] = display_group["Cash_In"].apply(lambda x: f"৳{x:,.2f}")
            display_group["Cash_Out"] = display_group["Cash_Out"].apply(lambda x: f"৳{x:,.2f}")
            display_group["Net_Cash_Flow"] = display_group["Net_Cash_Flow"].apply(lambda x: f"৳{x:,.2f}")
            st.dataframe(display_group, use_container_width=True, height=300)

        # Visualizations
        st.subheader("📈 Visual Analysis")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Detailed Categories", "Category Groups", "Income vs Expenses", "Cash Flow Trend"])

        with tab1:
            fig1 = px.bar(
                cat_summary,
                x="Payment_category", 
                y=["Cash_In", "Cash_Out"],
                barmode="group",
                title="Detailed Category-wise Cash Flow",
                labels={"value": "Amount (৳)", "variable": "Type", "Payment_category": "Category"}
            )
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            fig2 = px.bar(
                group_summary,
                x="Category_Group", 
                y=["Cash_In", "Cash_Out"],
                barmode="group",
                title="Broad Category Group Cash Flow",
                labels={"value": "Amount (৳)", "variable": "Type", "Category_Group": "Category Group"}
            )
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            # Income vs Expenses pie chart
            income_expense = group_summary[group_summary["Category_Group"].isin(["Income", "Expenses"])]
            fig3 = px.pie(
                income_expense,
                values="Net_Cash_Flow",
                names="Category_Group",
                title="Income vs Expenses Distribution"
            )
            st.plotly_chart(fig3, use_container_width=True)

        with tab4:
            # Daily trend
            daily_trend = filtered.groupby("Date").agg({
                "Cash_In": "sum",
                "Cash_Out": "sum"
            }).reset_index()
            daily_trend["Net_Cash_Flow"] = daily_trend["Cash_In"] - daily_trend["Cash_Out"]
            
            fig4 = px.line(
                daily_trend,
                x="Date",
                y=["Cash_In", "Cash_Out", "Net_Cash_Flow"],
                title="Daily Cash Flow Trend",
                labels={"value": "Amount (৳)", "variable": "Type"}
            )
            st.plotly_chart(fig4, use_container_width=True)

        # Detailed transactions with advanced filtering
        st.subheader("📋 Transaction Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_categories = st.multiselect(
                "Filter by Payment Category",
                options=filtered["Payment_category"].unique(),
                default=filtered["Payment_category"].unique()
            )
        
        with col2:
            selected_groups = st.multiselect(
                "Filter by Category Group",
                options=filtered["Category_Group"].unique(),
                default=filtered["Category_Group"].unique()
            )
        
        with col3:
            selected_names = st.multiselect(
                "Filter by Name",
                options=filtered["Name"].unique(),
                default=filtered["Name"].unique()
            )
        
        detailed_view = filtered[
            (filtered["Payment_category"].isin(selected_categories)) &
            (filtered["Category_Group"].isin(selected_groups)) &
            (filtered["Name"].isin(selected_names))
        ]
        
        if not detailed_view.empty:
            # Format display
            detailed_display = detailed_view.copy()
            detailed_display["Cash_In"] = detailed_display["Cash_In"].apply(lambda x: f"৳{x:,.2f}" if x > 0 else "")
            detailed_display["Cash_Out"] = detailed_display["Cash_Out"].apply(lambda x: f"৳{x:,.2f}" if x > 0 else "")
            detailed_display["Date"] = detailed_display["Date"].dt.date
            
            st.dataframe(
                detailed_display[[
                    "Date", "Voucher_No", "Payment_category", "Category_Group", 
                    "Name", "Description", "Cash_In", "Cash_Out", "Balance"
                ]].sort_values("Date", ascending=False),
                use_container_width=True,
                height=400
            )
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                csv_detail = detailed_view.to_csv(index=False)
                st.download_button(
                    label="📥 Download Transactions",
                    data=csv_detail,
                    file_name="cashbook_detailed.csv",
                    mime="text/csv"
                )
            with col2:
                csv_summary = cat_summary.to_csv(index=False)
                st.download_button(
                    label="📥 Download Category Summary",
                    data=csv_summary,
                    file_name="cashbook_category_summary.csv",
                    mime="text/csv"
                )
        else:
            st.info("No transactions found for the selected filters.")

        # Financial Insights
        st.subheader("💡 Financial Insights")
        
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            # Top performing categories
            st.write("**🏆 Top Performing Categories:**")
            top_3_income = cat_summary.nlargest(3, "Cash_In")
            for _, row in top_3_income.iterrows():
                st.success(f"• {row['Payment_category']}: ৳{row['Cash_In']:,.2f} income")
            
            st.write("**📉 Highest Expense Categories:**")
            top_3_expense = cat_summary.nlargest(3, "Cash_Out")
            for _, row in top_3_expense.iterrows():
                st.error(f"• {row['Payment_category']}: ৳{row['Cash_Out']:,.2f} expense")
        
        with insights_col2:
            # Cash flow insights
            st.write("**💰 Cash Flow Analysis:**")
            income_total = group_summary[group_summary["Category_Group"] == "Income"]["Cash_In"].sum()
            expense_total = group_summary[group_summary["Category_Group"] == "Expenses"]["Cash_Out"].sum()
            
            if income_total > 0:
                expense_ratio = (expense_total / income_total) * 100
                st.info(f"• Expense to Income Ratio: {expense_ratio:.1f}%")
            
            net_positive = cat_summary[cat_summary["Net_Cash_Flow"] > 0]
            net_negative = cat_summary[cat_summary["Net_Cash_Flow"] < 0]
            
            st.info(f"• Profitable Categories: {len(net_positive)}")
            st.warning(f"• Loss-making Categories: {len(net_negative)}")

    else:
        st.warning("No transactions found in the selected date range!")



elif page == "📉 Liability":
    st.title("📉 Liability Management")

    # Load purchase data
    purchase_df = load_purchase()

    # Ensure required columns exist
    required_cols = [
        "Date", "Vouchar_no", "Supplier_name", "Product_name", "Product_Category",
        "Payment_cetagory", "Purchase_rate", "Discount", "Amount", "Payable", "Receivedable"
    ]
    for col in required_cols:
        if col not in purchase_df.columns:
            if col in ["Purchase_rate", "Discount", "Amount", "Payable", "Receivedable"]:
                purchase_df[col] = 0.0
            else:
                purchase_df[col] = ""

    # Clean and convert data types
    purchase_df["Date"] = pd.to_datetime(purchase_df["Date"], format="%d-%m-%Y", errors="coerce")
    numeric_cols = ["Purchase_rate", "Discount", "Amount", "Payable", "Receivedable"]
    for col in numeric_cols:
        purchase_df[col] = pd.to_numeric(purchase_df[col], errors="coerce").fillna(0)

    # Calculate outstanding amount
    purchase_df["Outstanding"] = purchase_df["Payable"] - purchase_df["Receivedable"]

    # ---------------- FILTER OPTIONS ----------------
    st.sidebar.header("🔍 Filter Options")

    # Safe min/max dates
    if not purchase_df["Date"].isnull().all():
        min_date_val = purchase_df["Date"].min()
        max_date_val = purchase_df["Date"].max()
        if pd.isna(min_date_val):
            min_date_val = datetime.date.today()
        if pd.isna(max_date_val):
            max_date_val = datetime.date.today()
        min_date = min_date_val.date()
        max_date = max_date_val.date()
    else:
        min_date = datetime.date.today()
        max_date = datetime.date.today()

    # Date filter
    start_date, end_date = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Supplier filter
    suppliers = st.sidebar.multiselect(
        "Select Suppliers",
        options=purchase_df["Supplier_name"].dropna().unique().tolist(),
        default=purchase_df["Supplier_name"].dropna().unique().tolist()
    )

    # Category filter
    categories = st.sidebar.multiselect(
        "Select Product Categories",
        options=purchase_df["Product_Category"].dropna().unique().tolist(),
        default=purchase_df["Product_Category"].dropna().unique().tolist()
    )

    # Outstanding status filter
    outstanding_filter = st.sidebar.selectbox(
        "Outstanding Status",
        options=["All", "With Outstanding", "Fully Paid", "Overpaid"]
    )

    # Apply filters
    filtered_df = purchase_df[
        (purchase_df["Date"] >= pd.to_datetime(start_date)) &
        (purchase_df["Date"] <= pd.to_datetime(end_date)) &
        (purchase_df["Supplier_name"].isin(suppliers)) &
        (purchase_df["Product_Category"].isin(categories))
    ]
    if outstanding_filter == "With Outstanding":
        filtered_df = filtered_df[filtered_df["Outstanding"] > 0]
    elif outstanding_filter == "Fully Paid":
        filtered_df = filtered_df[filtered_df["Outstanding"] == 0]
    elif outstanding_filter == "Overpaid":
        filtered_df = filtered_df[filtered_df["Outstanding"] < 0]

    # ---------------- FINANCIAL OVERVIEW ----------------
    st.header("💰 Financial Overview")
    total_payable = filtered_df["Payable"].sum()
    total_received = filtered_df["Receivedable"].sum()
    total_outstanding = filtered_df["Outstanding"].sum()
    total_purchases = filtered_df["Amount"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Purchases", f"৳{total_purchases:,.2f}")
    col2.metric("Total Payable", f"৳{total_payable:,.2f}")
    col3.metric("Total Received", f"৳{total_received:,.2f}")
    col4.metric(
        "Total Outstanding",
        f"৳{total_outstanding:,.2f}",
        delta_color="inverse" if total_outstanding > 0 else "normal"
    )

    # ---------------- SUPPLIER SUMMARY ----------------
    st.header("📊 Supplier-wise Summary")
    supplier_summary = filtered_df.groupby("Supplier_name").agg({
        "Payable": "sum",
        "Receivedable": "sum",
        "Outstanding": "sum",
        "Vouchar_no": "count"
    }).rename(columns={"Vouchar_no": "Transaction_Count"}).reset_index()
    supplier_summary = supplier_summary.sort_values("Outstanding", ascending=False)

    st.dataframe(
        supplier_summary.style.format({
            "Payable": "৳{:.2f}",
            "Receivedable": "৳{:.2f}",
            "Outstanding": "৳{:.2f}"
        }),
        use_container_width=True,
        height=300
    )

    # ---------------- OUTSTANDING ANALYSIS ----------------
    st.header("📈 Outstanding Analysis")
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(
            supplier_summary.nlargest(10, "Outstanding"),
            x="Supplier_name",
            y="Outstanding",
            color="Outstanding",
            color_continuous_scale=["red", "orange", "green"],
            title="Top 10 Suppliers by Outstanding Amount"
        )
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        status_counts = filtered_df["Outstanding"].apply(
            lambda x: "Fully Paid" if x == 0 else ("Overpaid" if x < 0 else "With Outstanding")
        ).value_counts()
        fig2 = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Payment Status Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------- DETAILED TRANSACTIONS ----------------
    st.header("📋 Detailed Transactions")
    display_df = filtered_df.copy()
    display_df["Date"] = display_df["Date"].dt.date
    display_df["Payment_Status"] = display_df["Outstanding"].apply(
        lambda x: "✅ Fully Paid" if x == 0 else ("⚠️ Overpaid" if x < 0 else "❌ Outstanding")
    )
    display_df = display_df[[
        "Date", "Vouchar_no", "Supplier_name", "Product_name", "Product_Category",
        "Purchase_rate", "Discount", "Amount", "Payable", "Receivedable", "Outstanding", "Payment_Status"
    ]].sort_values("Date", ascending=False)

    st.dataframe(
        display_df.style.format({
            "Purchase_rate": "৳{:.2f}",
            "Discount": "৳{:.2f}",
            "Amount": "৳{:.2f}",
            "Payable": "৳{:.2f}",
            "Receivedable": "৳{:.2f}",
            "Outstanding": "৳{:.2f}"
        }),
        use_container_width=True,
        height=400
    )

    # ---------------- RECORD PAYMENT ----------------
    st.header("💳 Record Payment")


elif page == "📈 Profit & Loss":
    st.title("📈 Profit & Loss Analysis")

    # Load sales data
    sales_df = load_sales()

    # Ensure date column is in datetime format
    sales_df["date"] = pd.to_datetime(sales_df["date"], errors="coerce")

    # Filter by date range
    min_date = sales_df["date"].min().date() if not sales_df.empty else datetime.date.today()
    max_date = sales_df["date"].max().date() if not sales_df.empty else datetime.date.today()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

    mask = (sales_df["date"] >= pd.to_datetime(start_date)) & (sales_df["date"] <= pd.to_datetime(end_date))
    filtered_sales = sales_df.loc[mask]

    if filtered_sales.empty:
        st.warning("No sales records found for this date range.")
    else:
        # Calculate total income and expenses
        total_income = filtered_sales["total_amount"].sum()
        total_expenses = df_cash[df_cash["Type"] == "Expense"]["Cash_Out"].sum() if "Type" in df_cash else 0.0

        # Calculate profit or loss
        profit_loss = total_income - total_expenses

        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"৳{total_income:,.2f}")
        col2.metric("Total Expenses", f"৳{total_expenses:,.2f}")
        col3.metric("Profit/Loss", f"৳{profit_loss:,.2f}", delta_color="inverse" if profit_loss < 0 else "normal")

        # Category-wise income analysis
        category_income = filtered_sales.groupby("category")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False)

        st.subheader("📊 Category-wise Income Analysis")
        fig1 = px.bar(category_income, x="category", y="total_amount", color="category", title="Income by Category")
        st.plotly_chart(fig1, use_container_width=True)

elif page == "📊 Charts":
    st.title("📊 Charts & Visualizations")

    # Load all data
    sales_df = load_sales()
    cash_df = load_cashbook()
    bank_df = load_bankbook()
    purchase_df = load_purchase()

    # Standardize date columns
    if "date" in sales_df.columns:
        sales_df.rename(columns={"date": "Date"}, inplace=True)
    if "date" in bank_df.columns:
        bank_df.rename(columns={"date": "Date"}, inplace=True)
    if "date" in cash_df.columns:
        cash_df.rename(columns={"date": "Date"}, inplace=True)
    if "date" in purchase_df.columns:
        purchase_df.rename(columns={"date": "Date"}, inplace=True)

    # Ensure Date columns are datetime
    for df in [sales_df, cash_df, bank_df, purchase_df]:
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Handle empty datasets safely
    min_date = min(
        d.min() for d in [
            sales_df["Date"], cash_df["Date"], bank_df["Date"], purchase_df["Date"]
        ] if not d.empty
    ).date()
    max_date = max(
        d.max() for d in [
            sales_df["Date"], cash_df["Date"], bank_df["Date"], purchase_df["Date"]
        ] if not d.empty
    ).date()

    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

    # Filter data by date range
    sales_filtered = sales_df[(sales_df["Date"] >= pd.to_datetime(start_date)) & (sales_df["Date"] <= pd.to_datetime(end_date))]
    cash_filtered = cash_df[(cash_df["Date"] >= pd.to_datetime(start_date)) & (cash_df["Date"] <= pd.to_datetime(end_date))]
    bank_filtered = bank_df[(bank_df["Date"] >= pd.to_datetime(start_date)) & (bank_df["Date"] <= pd.to_datetime(end_date))]
    purchase_filtered = purchase_df[(purchase_df["Date"] >= pd.to_datetime(start_date)) & (purchase_df["Date"] <= pd.to_datetime(end_date))]

    if sales_filtered.empty and cash_filtered.empty and bank_filtered.empty and purchase_filtered.empty:
        st.warning("No data found for the selected date range.")
    else:
        # ------------------- SALES -------------------
        if not sales_filtered.empty:
            st.subheader("📈 Sales Overview")
            sales_summary = sales_filtered.groupby("category")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False)
            fig_sales = px.bar(sales_summary, x="category", y="total_amount",
                               color="category", title="Sales by Category")
            st.plotly_chart(fig_sales, use_container_width=True)

            st.subheader("Upccoming Features")
            '''
        # ------------------- CASHBOOK -------------------
        if not cash_filtered.empty:
            st.subheader("💵 Cashbook Overview")
            cash_summary = cash_filtered.groupby("Payment_category").agg(
                Cash_In=("Cash_In", "sum"),
                Cash_Out=("Cash_Out", "sum")
            ).reset_index()
            cash_summary["Net_Cash_Flow"] = cash_summary["Cash_In"] - cash_summary["Cash_Out"]
            fig_cash = px.bar(cash_summary, x="Payment_category", y=["Cash_In", "Cash_Out"],
                              barmode="group", title="Cashbook Income vs Expense by Category")
            st.plotly_chart(fig_cash, use_container_width=True)
        else:

            st.write("This page undergoes continuous development. Please check back later for more features and improvements. ️")


        # ------------------- BANKBOOK -------------------
        if not bank_filtered.empty:
            st.subheader("🏦 Bankbook Overview")
            bank_summary = bank_filtered.groupby("Payment_category").agg(
                Cash_In=("Deposit_Amount", "sum"),
                Cash_Out=("Withdrawal_Amount", "sum")
            ).reset_index()
            bank_summary["Net_Cash_Flow"] = bank_summary["Cash_In"] - bank_summary["Cash_Out"]
            fig_bank = px.bar(bank_summary, x="Payment_category", y=["Cash_In", "Cash_Out"],
                              barmode="group", title="Bankbook Deposit vs Withdrawal by Category")
            st.plotly_chart(fig_bank, use_container_width=True)

        # ------------------- PURCHASE -------------------
        if not purchase_filtered.empty:
            st.subheader("📦 Purchase Overview")
            purchase_summary = purchase_filtered.groupby("Product_Category").agg(
                Total_Purchase=("Amount", "sum"),
                Total_Payable=("Payable", "sum"),
                Total_Receivedable=("Receivedable", "sum")
            ).reset_index()
            purchase_summary["Outstanding"] = purchase_summary["Total_Payable"] - purchase_summary["Total_Receivedable"]
            fig_purchase = px.bar(purchase_summary, x="Product_Category", y=["Total_Purchase", "Total_Payable"],
                                  barmode="group", title="Purchase by Category")
            st.plotly_chart(fig_purchase, use_container_width=True)

        # ------------------- BANK TREND -------------------
        if not bank_filtered.empty:
            st.subheader("🏦 Bankbook Deposit vs Withdrawal Over Time")
            bank_trend = bank_filtered.groupby("Date").agg(
                Deposit_Amount=("Deposit_Amount", "sum"),
                Withdrawal_Amount=("Withdrawal_Amount", "sum")
            ).reset_index()
            bank_trend["Net_Cash_Flow"] = bank_trend["Deposit_Amount"] - bank_trend["Withdrawal_Amount"]
            fig_bank_trend = px.line(bank_trend, x="Date", y=["Deposit_Amount", "Withdrawal_Amount", "Net_Cash_Flow"],
                                     title="Bank Transactions Over Time")
            st.plotly_chart(fig_bank_trend, use_container_width=True)

        # ------------------- COMBINED SALES & CASH -------------------
        if not sales_filtered.empty and not cash_filtered.empty:
            st.subheader("📈 Combined Sales and Cashbook Income vs Expense")
            combined_summary = pd.DataFrame({"Date": sales_filtered["Date"].dt.date.unique()})

            combined_summary["Sales_Income"] = combined_summary["Date"].map(
                sales_filtered.groupby(sales_filtered["Date"].dt.date)["total_amount"].sum()
            )
            combined_summary["Cash_In"] = combined_summary["Date"].map(
                cash_filtered.groupby(cash_filtered["Date"].dt.date)["Cash_In"].sum()
            )
            combined_summary["Cash_Out"] = combined_summary["Date"].map(
                cash_filtered.groupby(cash_filtered["Date"].dt.date)["Cash_Out"].sum()
            )
            combined_summary = combined_summary.fillna(0)

            combined_summary["Net_Cash_Flow"] = combined_summary["Sales_Income"] + combined_summary["Cash_In"] - combined_summary["Cash_Out"]
            fig_combined = px.line(combined_summary, x="Date", y=["Sales_Income", "Cash_In", "Cash_Out", "Net_Cash_Flow"],
                                   title="Combined Sales and Cashbook Income vs Expense")
            st.plotly_chart(fig_combined, use_container_width=True)

        # ------------------- SELLER-WISE SALES -------------------
        if "Sold_By" in sales_filtered.columns and "total_amount" in sales_filtered.columns:
            seller_sales = sales_filtered.groupby("Sold_By").agg(
                Total_Sales=("total_amount", "sum"),
                Total_Quantity=("quantity", "sum")
            ).reset_index()

            st.subheader("👨‍💼 Seller-wise Sales & Income")
            st.dataframe(seller_sales)

            fig_seller = px.bar(seller_sales, x="Sold_By", y="Total_Sales",
                                title="Seller-wise Total Sales", text_auto=True)
            st.plotly_chart(fig_seller, use_container_width=True)

            fig_quantity = px.bar(seller_sales, x="Sold_By", y="Total_Quantity",
                                  title="Seller-wise Total Quantity Sold", text_auto=True)
            st.plotly_chart(fig_quantity, use_container_width=True)

        # ------------------- DRILL-DOWN -------------------
        st.subheader("🔍 Sales Drill-Down Report")
        drill = st.selectbox("Select Drill-down Category", options=["None"] + list(sales_filtered.columns))
        if drill != "None":
            drill_df = sales_filtered.groupby(drill).agg(
                Total_Sales=("total_amount", "sum")
            ).reset_index()

            st.dataframe(drill_df)
            fig_drill = px.bar(drill_df, x=drill, y="Total_Sales", title=f"Sales by {drill}")
            st.plotly_chart(fig_drill, use_container_width=True)

            '''
elif page == "📚 About":
    st.title("📚 About V2TAFA")

    st.markdown("""
    **V2TAFA** is a comprehensive financial management tool designed to help businesses track their sales, cash flow, bank transactions, and liabilities effectively. 

    ### Features:
    - **Sales Tracking**: Monitor sales by category, seller, and date.
    - **Cashbook Management**: Analyze cash inflow and outflow with detailed category breakdowns.
    - **Bankbook Overview**: Keep track of deposits and withdrawals with visual insights.
    - **Liability Management**: Manage supplier payments and outstanding amounts efficiently.
    - **Profit & Loss Analysis**: Gain insights into overall financial health with income and expense tracking.
    - **Charts & Visualizations**: Interactive charts for better understanding of financial data.

    ### Technologies Used:
    - Streamlit for web interface
    - Pandas for data manipulation
    - Plotly for interactive visualizations
    - Excel for data storage

    ### Future Enhancements:
    - Integration with external APIs for real-time data updates.
    - Advanced analytics features like forecasting and trend analysis.
    - User authentication and role-based access control.

    Thank you for using V2TAFA! For any issues or feature requests, please contact the development team.
    """)

# Footer
st.markdown("---")  
st.markdown("Made with ❤️ by [Mujakkir Ahmad](https://webmujakkir.streamlit.app/)")
st.markdown("For more information, visit [GitHub Repository](https://github.com/mujakkirdv)")
st.markdown("Follow me on [LinkedIn](https://www.linkedin.com/in/mujakkirdv/)")
st.markdown("© August 2025 TAFA Version: 1.1.0. All rights reserved.")

st.markdown("---")
