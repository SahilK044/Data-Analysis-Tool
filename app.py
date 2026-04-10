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
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        return df
    except Exception as e:
        return str(e)


if uploaded_file is not None:
    # Load and cache data
    with st.spinner("Loading data..."):
        data = load_data(uploaded_file)
        
    if isinstance(data, str):
        st.error(f"Error loading file: {data}")
    else:
        st.sidebar.success("File successfully loaded!")
        
        # Tools in sidebar for basic cleaning
        st.sidebar.header("2. Quick Cleaning")
        if st.sidebar.button("Remove Duplicate Rows"):
            original_len = len(data)
            data.drop_duplicates(inplace=True)
            new_len = len(data)
            st.sidebar.caption(f"Dropped {original_len - new_len} duplicate rows.")
            
        drop_na_col = st.sidebar.selectbox("Drop missing values in column (Optional)", options=["None"] + list(data.columns))
        if drop_na_col != "None":
            original_len = len(data)
            data.dropna(subset=[drop_na_col], inplace=True)
            new_len = len(data)
            st.sidebar.caption(f"Dropped {original_len - new_len} rows with missing values in '{drop_na_col}'.")
            

        # Main Workspace - Using Tabs for a clean, minimalist layout
        tab1, tab2, tab3 = st.tabs(["📋 Data Overview", "📈 Visualizations", "💡 Summary Stats"])
        
        with tab1:
            st.subheader("Data Preview")
            st.markdown(f"**Shape:** {data.shape[0]} rows and {data.shape[1]} columns")
            # Show a limited number of rows by default to keep the UI clean
            rows_to_show = st.slider("Number of rows to display", min_value=5, max_value=max(100, min(500, data.shape[0])), value=10)
            st.dataframe(data.head(rows_to_show), use_container_width=True)
            
            with st.expander("Show Column Data Types"):
                st.dataframe(data.dtypes.astype(str).reset_index().rename(columns={'index': 'Column', 0: 'Type'}), use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("Chart Builder")
            st.markdown("Select variables to uncover insights.")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                plot_type = st.selectbox("Select Chart Type", ["Scatter Plot", "Line Chart", "Bar Chart", "Histogram", "Box Plot"])
            with col2:
                x_axis = st.selectbox("X-Axis Variable", options=data.columns, index=0)
            with col3:
                # Add a 'None' option for Y-axis for plots like histograms
                y_options = ["None"] + list(data.columns)
                default_y_index = 1 if len(data.columns) > 1 else 0
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
                st.error(f"Could not generate plot. Error: {e}")

        with tab3:
            st.subheader("Statistical Summary")
            st.markdown("Descriptive statistics for numerical columns.")
            st.dataframe(data.describe().T, use_container_width=True)
            
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
