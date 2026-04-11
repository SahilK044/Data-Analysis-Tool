
import streamlit as st
import pandas as pd
import plotly.express as px
import io
import base64

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Data Explorer Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM STYLING ======================
STYLING = """
<style>
    .css-18e3th9 { padding-top: 1rem; }
    .st-emotion-cache-1y4p8pa { padding-top: 2rem; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: #1E293B; }
    .stDataFrame { border-radius: 8px; }
    .reportview-container .main .block-container { padding-top: 2rem; }
</style>
"""
st.markdown(STYLING, unsafe_allow_html=True)

st.title("Data Explorer Studio 📊")
st.markdown("**Professional • Interactive • Future-Proof** — Your all-in-one data analysis workbench.")

# ====================== THEME TOGGLE ======================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

if st.sidebar.button("🌗 Toggle Dark/Light Theme"):
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

# ====================== SAMPLE DATASETS ======================
SAMPLE_DATASETS = {
    "Iris (Classic)": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
    "Titanic": "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv",
    "Tips (Restaurant)": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv",
    "Penguins": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",
    "Cars (mtcars)": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mtcars.csv"
}

# ====================== SIDEBAR ======================
st.sidebar.header("📂 1. Load Data")

# Sample dataset selector
use_sample = st.sidebar.checkbox("Use Sample Dataset instead of upload")
if use_sample:
    dataset_name = st.sidebar.selectbox("Choose Sample Dataset", options=list(SAMPLE_DATASETS.keys()))
    if st.sidebar.button("🚀 Load Sample"):
        with st.spinner(f"Loading {dataset_name}..."):
            df_sample = pd.read_csv(SAMPLE_DATASETS[dataset_name])
            st.session_state.data = df_sample.copy()
            st.session_state.file_name = dataset_name + ".csv"
            st.sidebar.success(f"✅ {dataset_name} loaded!")
            st.rerun()
else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel", 
        type=['csv', 'xlsx', 'xls']
    )

@st.cache_data
def load_data(file_bytes: bytes, file_name: str) -> pd.DataFrame | str:
    try:
        if file_name.lower().endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
        return df
    except Exception as e:
        return f"Error: {str(e)}"

# ====================== MAIN LOGIC ======================
if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.file_name = None

# Load uploaded file
if not use_sample and uploaded_file is not None and st.session_state.data is None:
    with st.spinner("Loading your file..."):
        file_bytes = uploaded_file.getvalue()
        result = load_data(file_bytes, uploaded_file.name)
        if isinstance(result, str):
            st.error(result)
        else:
            st.session_state.data = result.copy()
            st.session_state.file_name = uploaded_file.name
            st.sidebar.success("✅ File loaded successfully!")

data = st.session_state.data

if data is not None:
    st.sidebar.success(f"✅ Working with: **{st.session_state.file_name}**")
    
    # Show file metadata
    st.sidebar.markdown(f"**Rows:** {data.shape[0]:,} | **Columns:** {data.shape[1]}")
    
    # ====================== CLEANING & TRANSFORMATION ======================
    st.sidebar.header("🧼 2. Clean & Transform")
    
    # Drop duplicates
    if st.sidebar.button("🧹 Remove Duplicates"):
        st.session_state.data = st.session_state.data.drop_duplicates().reset_index(drop=True)
        st.rerun()
    
    # Drop columns
    if st.sidebar.checkbox("Drop Columns"):
        cols_to_drop = st.sidebar.multiselect("Select columns to drop", options=data.columns)
        if cols_to_drop and st.sidebar.button("❌ Drop Selected Columns"):
            st.session_state.data = st.session_state.data.drop(columns=cols_to_drop).reset_index(drop=True)
            st.rerun()
    
    # Missing value handling
    if st.sidebar.checkbox("Handle Missing Values"):
        col_for_na = st.sidebar.selectbox("Column", options=["All Columns"] + list(data.columns))
        method = st.sidebar.selectbox("Method", ["Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode", "Fill with 0"])
        
        if st.sidebar.button("Apply Missing Value Fix"):
            if col_for_na == "All Columns":
                if method == "Drop Rows":
                    st.session_state.data = st.session_state.data.dropna().reset_index(drop=True)
                elif method == "Fill with Mean":
                    st.session_state.data = st.session_state.data.fillna(data.mean(numeric_only=True))
                elif method == "Fill with Median":
                    st.session_state.data = st.session_state.data.fillna(data.median(numeric_only=True))
                elif method == "Fill with Mode":
                    st.session_state.data = st.session_state.data.fillna(data.mode().iloc[0])
                elif method == "Fill with 0":
                    st.session_state.data = st.session_state.data.fillna(0)
            else:
                if method == "Drop Rows":
                    st.session_state.data = st.session_state.data.dropna(subset=[col_for_na]).reset_index(drop=True)
                elif method == "Fill with Mean" and pd.api.types.is_numeric_dtype(data[col_for_na]):
                    st.session_state.data[col_for_na] = st.session_state.data[col_for_na].fillna(data[col_for_na].mean())
                elif method == "Fill with Median" and pd.api.types.is_numeric_dtype(data[col_for_na]):
                    st.session_state.data[col_for_na] = st.session_state.data[col_for_na].fillna(data[col_for_na].median())
                elif method == "Fill with Mode":
                    st.session_state.data[col_for_na] = st.session_state.data[col_for_na].fillna(data[col_for_na].mode().iloc[0])
                elif method == "Fill with 0":
                    st.session_state.data[col_for_na] = st.session_state.data[col_for_na].fillna(0)
            st.rerun()
    
    # Column rename & type conversion
    if st.sidebar.checkbox("Rename Columns / Change Types"):
        col_to_edit = st.sidebar.selectbox("Column to edit", options=data.columns)
        new_name = st.sidebar.text_input("New Column Name", value=col_to_edit)
        if new_name and new_name != col_to_edit and st.sidebar.button("Rename"):
            st.session_state.data = st.session_state.data.rename(columns={col_to_edit: new_name})
            st.rerun()
        
        new_type = st.sidebar.selectbox("Convert to", ["int", "float", "string", "datetime", "category"])
        if st.sidebar.button("Convert Type"):
            try:
                if new_type == "datetime":
                    st.session_state.data[col_to_edit] = pd.to_datetime(st.session_state.data[col_to_edit])
                else:
                    st.session_state.data[col_to_edit] = st.session_state.data[col_to_edit].astype(new_type)
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Conversion failed: {e}")
    
    # Data Filter (multiple conditions possible)
    st.sidebar.header("🔎 3. Filter Data")
    if st.sidebar.checkbox("Enable Advanced Filter"):
        filter_col = st.sidebar.selectbox("Filter Column", options=data.columns)
        operator = st.sidebar.selectbox("Operator", ["==", ">", "<", ">=", "<=", "!=", "contains"])
        value = st.sidebar.text_input("Value")
        
        if st.sidebar.button("Apply Filter"):
            try:
                if operator == "==":
                    st.session_state.data = st.session_state.data[st.session_state.data[filter_col] == value]
                elif operator == ">":
                    st.session_state.data = st.session_state.data[st.session_state.data[filter_col] > float(value)]
                elif operator == "<":
                    st.session_state.data = st.session_state.data[st.session_state.data[filter_col] < float(value)]
                elif operator == ">=":
                    st.session_state.data = st.session_state.data[st.session_state.data[filter_col] >= float(value)]
                elif operator == "<=":
                    st.session_state.data = st.session_state.data[st.session_state.data[filter_col] <= float(value)]
                elif operator == "!=":
                    st.session_state.data = st.session_state.data[st.session_state.data[filter_col] != value]
                elif operator == "contains":
                    st.session_state.data = st.session_state.data[st.session_state.data[filter_col].astype(str).str.contains(value, case=False)]
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Filter error: {e}")
    
    if st.sidebar.button("🔄 Reset to Original"):
        if use_sample:
            st.session_state.data = pd.read_csv(SAMPLE_DATASETS[dataset_name]).copy()
        else:
            # Re-load original file (simple reset)
            st.session_state.data = None
            st.rerun()
    
    # ====================== EXPORT ======================
    st.sidebar.header("💾 4. Export")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.sidebar.button("📥 Cleaned CSV"):
            csv = st.session_state.data.to_csv(index=False).encode()
            st.sidebar.download_button("Download CSV", csv, f"cleaned_{st.session_state.file_name}.csv", "text/csv")
    with col2:
        if st.sidebar.button("📄 Full HTML Report"):
            html = st.session_state.data.to_html()
            b64 = base64.b64encode(html.encode()).decode()
            href = f'data:text/html;base64,{b64}'
            st.sidebar.markdown(f'<a href="{href}" download="data_report.html" target="_blank">Download Report</a>', unsafe_allow_html=True)
    
    # ====================== TABS ======================
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "📈 Visualizations", "💡 Summary", "🔍 Insights"])
    
    # TAB 1: Overview
    with tab1:
        st.subheader("Data Preview")
        if data.empty:
            st.warning("Dataset is empty.")
        else:
            st.markdown(f"**Shape:** {data.shape[0]:,} rows × {data.shape[1]} columns")
            rows_to_show = st.slider("Rows to display", 5, min(500, len(data)), 10)
            st.dataframe(data.head(rows_to_show), use_container_width=True)
            
            with st.expander("Column Info"):
                info = pd.DataFrame({
                    "Column": data.columns,
                    "Dtype": data.dtypes.astype(str),
                    "Unique": data.nunique(),
                    "Missing": data.isnull().sum(),
                    "Min": data.min(numeric_only=True),
                    "Max": data.max(numeric_only=True)
                })
                st.dataframe(info, use_container_width=True, hide_index=True)
    
    # TAB 2: Visualizations
    with tab2:
        st.subheader("Interactive Chart Builder")
        if data.empty:
            st.info("No data to plot.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                plot_type = st.selectbox("Chart Type", ["Scatter", "Line", "Bar", "Histogram", "Box", "Violin"])
            with c2:
                x = st.selectbox("X Axis", data.columns, index=0)
            with c3:
                y_options = ["None"] + list(data.columns)
                y = st.selectbox("Y Axis", y_options, index=2 if len(data.columns)>1 else 1)
            
            color = st.selectbox("Color By", ["None"] + list(data.columns))
            color_arg = color if color != "None" else None
            y_arg = y if y != "None" else None
            
            try:
                if plot_type == "Scatter" and y_arg:
                    fig = px.scatter(data, x=x, y=y_arg, color=color_arg, template="plotly_white")
                elif plot_type == "Line" and y_arg:
                    fig = px.line(data, x=x, y=y_arg, color=color_arg, template="plotly_white")
                elif plot_type == "Bar" and y_arg:
                    fig = px.bar(data, x=x, y=y_arg, color=color_arg, template="plotly_white")
                elif plot_type == "Histogram":
                    fig = px.histogram(data, x=x, color=color_arg, template="plotly_white")
                elif plot_type == "Box" and y_arg:
                    fig = px.box(data, x=x, y=y_arg, color=color_arg, template="plotly_white")
                elif plot_type == "Violin" and y_arg:
                    fig = px.violin(data, x=x, y=y_arg, color=color_arg, template="plotly_white")
                else:
                    fig = None
                
                if fig:
                    fig.update_layout(margin=dict(l=20,r=20,t=40,b=20), title=f"{plot_type} Plot")
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Plot error: {e}")
    
    # TAB 3: Summary
    with tab3:
        st.subheader("Statistical Summary")
        if not data.empty:
            st.dataframe(data.describe().T, use_container_width=True)
            
            st.subheader("Missing Values")
            missing = data.isnull().sum().reset_index()
            missing.columns = ["Column", "Count"]
            missing = missing[missing["Count"] > 0]
            if missing.empty:
                st.success("✅ No missing values!")
            else:
                st.dataframe(missing, use_container_width=True, hide_index=True)
    
    # TAB 4: Insights (NEW)
    with tab4:
        st.subheader("Advanced Insights")
        if data.empty:
            st.info("No data.")
        else:
            # Correlation Heatmap
            st.markdown("**Correlation Heatmap** (Numerical Columns)")
            num_cols = data.select_dtypes(include=["number"]).columns
            if len(num_cols) > 1:
                corr = data[num_cols].corr()
                fig_heat = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="RdBu")
                st.plotly_chart(fig_heat, use_container_width=True)
            else:
                st.info("Need at least 2 numeric columns for correlation.")
            
            # Value Counts Explorer
            st.subheader("Value Counts Explorer")
            cat_col = st.selectbox("Select Column", options=data.columns, key="valuecount")
            if st.button("Show Top 15 Values"):
                vc = data[cat_col].value_counts().head(15).reset_index()
                vc.columns = [cat_col, "Count"]
                st.dataframe(vc, use_container_width=True)
                fig_vc = px.bar(vc, x=cat_col, y="Count", title=f"Top values in {cat_col}")
                st.plotly_chart(fig_vc, use_container_width=True)
    
else:
    st.info("👈 Upload a file **or** enable Sample Dataset in the sidebar to begin exploring!")

st.caption("Data Explorer Studio v2 • Built with ❤️ for powerful, instant data analysis")
