import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Setup minimalist page config
st.set_page_config(
    page_title="Data Explorer Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply some custom minimal CSS using st.markdown
STYLING = """
<style>
    .css-18e3th9 {
        padding-top: 1rem;
    }
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #1E293B;
    }
    .stDataFrame {
        border-radius: 8px;
    }
</style>
"""
st.markdown(STYLING, unsafe_allow_html=True)

st.title("Data Explorer Studio 📊")
st.markdown("A lightweight and interactive tool for quickly understanding and visualizing your datasets.")

# Sidebar for controls
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV or Excel file", 
    type=['csv', 'xlsx', 'xls']
)

@st.cache_data
def load_data(file_bytes, file_name):
    # Using file bytes and name to cache successfully independent of the UploadedFile object state
    try:
        if file_name.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))
        return df
    except Exception as e:
        return str(e)


if uploaded_file is not None:
    # Load and cache raw data efficiently
    with st.spinner("Loading data..."):
        file_bytes = uploaded_file.getvalue()
        raw_data = load_data(file_bytes, uploaded_file.name)
        
    if isinstance(raw_data, str):
        st.error(f"Error loading file: {raw_data}")
    else:
        st.sidebar.success("File successfully loaded!")
        
        # Initialize session state for mutable data frame
        if 'file_name' not in st.session_state or st.session_state.file_name != uploaded_file.name:
            st.session_state.data = raw_data.copy()
            st.session_state.file_name = uploaded_file.name
        
        # We work with the session_state copy so the user can wipe/clean iteratively
        data = st.session_state.data
        
        # Tools in sidebar for basic cleaning
        st.sidebar.header("2. Quick Cleaning")
        if st.sidebar.button("Remove Duplicate Rows"):
            st.session_state.data = st.session_state.data.drop_duplicates()
            st.rerun()
            
        drop_na_col = st.sidebar.selectbox("Select column to check missing values (Optional)", options=["None"] + list(data.columns))
        if drop_na_col != "None":
            if st.sidebar.button(f"Drop Missing in '{drop_na_col}'"):
                st.session_state.data = st.session_state.data.dropna(subset=[drop_na_col])
                st.rerun()
                
        if st.sidebar.button("Reset All Changes"):
            st.session_state.data = raw_data.copy()
            st.rerun()

        # Main Workspace - Using Tabs for a clean, minimalist layout
        tab1, tab2, tab3 = st.tabs(["📋 Data Overview", "📈 Visualizations", "💡 Summary Stats"])
        
        with tab1:
            st.subheader("Data Preview")
            if data.empty:
                st.warning("The dataset is currently empty (perhaps all rows were dropped).")
            else:
                st.markdown(f"**Shape:** {data.shape[0]} rows and {data.shape[1]} columns")
                # Show a limited number of rows by default to keep the UI clean
                max_rows = max(10, min(1000, data.shape[0]))
                rows_to_show = st.slider("Number of rows to display", min_value=1, max_value=max_rows, value=min(10, data.shape[0]))
                st.dataframe(data.head(rows_to_show), use_container_width=True)
                
                with st.expander("Show Column Data Types"):
                    st.dataframe(data.dtypes.astype(str).reset_index().rename(columns={'index': 'Column', 0: 'Type'}), use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("Chart Builder")
            st.markdown("Select variables to uncover insights.")
            
            if data.empty:
                st.info("No data available to plot.")
            else:
                col1, col2, col3 = st.columns(3)
                with col1:
                    plot_type = st.selectbox("Select Chart Type", ["Scatter Plot", "Line Chart", "Bar Chart", "Histogram", "Box Plot"])
                with col2:
                    x_axis = st.selectbox("X-Axis Variable", options=data.columns, index=0)
                with col3:
                    # Add a 'None' option for Y-axis for plots like histograms
                    y_options = ["None"] + list(data.columns)
                    # Select the second column for Y axis (index 2 in y_options array) if there is more than 1 column. 
                    default_y_index = 2 if len(data.columns) > 1 else 1 
                    y_axis = st.selectbox("Y-Axis Variable", options=y_options, index=default_y_index)
                    
                color_by = st.selectbox("Color By (Optional)", options=["None"] + list(data.columns))
                
                # Generate Plotly Chart
                try:
                    color_arg = color_by if color_by != "None" else None
                    y_arg = y_axis if y_axis != "None" else None
                    
                    if plot_type == "Scatter Plot" and y_arg:
                        fig = px.scatter(data, x=x_axis, y=y_arg, color=color_arg, template="plotly_white")
                    elif plot_type == "Line Chart" and y_arg:
                        fig = px.line(data, x=x_axis, y=y_arg, color=color_arg, template="plotly_white")
                    elif plot_type == "Bar Chart" and y_arg:
                        fig = px.bar(data, x=x_axis, y=y_arg, color=color_arg, template="plotly_white")
                    elif plot_type == "Histogram":
                        fig = px.histogram(data, x=x_axis, color=color_arg, template="plotly_white")
                    elif plot_type == "Box Plot" and y_arg:
                        fig = px.box(data, x=x_axis, y=y_arg, color=color_arg, template="plotly_white")
                    else:
                        st.warning("Please select a Y-Axis variable for this chart type.")
                        fig = None
                        
                    if fig:
                        fig.update_layout(
                            margin=dict(l=20, r=20, t=30, b=20),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                        )
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not generate plot. Note that plot type mapping expects certain datatypes. Error detail: {e}")

        with tab3:
            st.subheader("Statistical Summary")
            if data.empty:
                st.info("No data available to summarize.")
            else:
                st.markdown("Descriptive statistics for numerical columns.")
                # We use try/except as describe can fail on purely categorical data if not handled
                try:
                    st.dataframe(data.describe().T, use_container_width=True)
                except Exception:
                    st.info("No numerical columns found to describe.")
                
                st.subheader("Missing Values")
                missing_data = data.isnull().sum().reset_index().rename(columns={'index': 'Column', 0: 'Missing Values'})
                missing_data = missing_data[missing_data['Missing Values'] > 0]
                if missing_data.empty:
                    st.success("No missing values found in the dataset! 🎉")
                else:
                    st.dataframe(missing_data, use_container_width=True, hide_index=True)

else:
    # Minimalist empty state
    st.info("👈 Please upload a CSV or Excel file from the sidebar to get started.")
