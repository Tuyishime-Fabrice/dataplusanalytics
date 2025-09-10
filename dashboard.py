import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
import os

# -------------------------
# 🔐 Secure credential handling
# -------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY") or st.secrets.get("SUPABASE_ANON_KEY")
PASSWORD = st.secrets.get("DASHBOARD_PASSWORD")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# -------------------------
# 🔹 PASSWORD PROTECTION
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔒 Enter Password")
    pwd_input = st.text_input("Password:", type="password")
    if st.button("Login"):
        if pwd_input == PASSWORD:
            st.session_state.logged_in = True
            st.success("✅ Access granted")
            st.rerun()  # Changed from st.experimental_rerun() to st.rerun()
        else:
            st.error("❌ Incorrect password")
else:
    # -------------------------
    # 🔹 Streamlit page config
    # -------------------------
    st.set_page_config(page_title="Courses & Applications Dashboard", layout="wide")

    # Custom CSS for better styling with green as primary color
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(90deg, #4CAF50 0%, #2E7D32 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2rem;
        }
        .section-header {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2E4057;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #4CAF50;
            margin: 1rem 0;
        }
        .stDataFrame {
            background-color: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    # Add logo to the top of the page
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://ppycnugwogonwcteeyff.supabase.co/storage/v1/object/public/images/dataplus%20logggg.jpg", width=200)

    st.markdown('<h1 class="main-header">         DATA PLUS RWANDA ANALYSIS</h1>', unsafe_allow_html=True)

    # -------------------------
    # 🔹 Data Fetching
    # -------------------------
    with st.spinner('Loading data...'):
        courses_resp = supabase.table("courses").select("*").execute()
        courses_df = pd.DataFrame(courses_resp.data)
        
        apps_resp = supabase.table("course_applications").select("*").execute()
        apps_df = pd.DataFrame(apps_resp.data)

    # -------------------------
    # 🔹 Key Metrics Dashboard
    # -------------------------
    st.markdown('<div class="section-header">📈 Key Metrics Overview</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Courses", len(courses_df))
    with col2:
        st.metric("Total Applications", len(apps_df))
    with col3:
        st.metric("Unique Applicants", apps_df['email'].nunique())
    with col4:
        total_capacity = courses_df['students_count'].sum() if 'students_count' in courses_df.columns else 0
        st.metric("Total Course Capacity", total_capacity)

    # -------------------------
    # 🔹 Data Processing
    # -------------------------
    merged_df = apps_df.merge(
        courses_df[['title','students_count']], 
        left_on='course_name', 
        right_on='title', 
        how='left'
    )

    # -------------------------
    # 🔹 PIE CHARTS SECTION (2-column layout)
    # -------------------------
    st.markdown('<div class="section-header">🥧 Distribution Analysis</div>', unsafe_allow_html=True)

    pie_col1, pie_col2 = st.columns(2)

    with pie_col1:
        # Education Level Distribution
        edu_dist = merged_df['education_level'].value_counts().reset_index()
        edu_dist.columns = ['education_level','count']
        fig_edu = px.pie(
            edu_dist, 
            names='education_level', 
            values='count', 
            title="🎓 Education Level Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.3
        )
        fig_edu.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_edu, use_container_width=True)

    with pie_col2:
        # Python Experience Level
        exp_dist = merged_df['python_experience_level'].value_counts().reset_index()
        exp_dist.columns = ['experience_level','count']
        fig_exp = px.pie(
            exp_dist, 
            names='experience_level', 
            values='count', 
            title="💻 Python Experience Levels",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.3
        )
        fig_exp.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_exp, use_container_width=True)

    # Second row of pie charts
    pie_col3, pie_col4 = st.columns(2)

    with pie_col3:
        # Participation Preference
        pref_dist = merged_df['participation_preference'].value_counts().reset_index()
        pref_dist.columns = ['preference','count']
        fig_pref = px.pie(
            pref_dist, 
            names='preference', 
            values='count', 
            title="🏫 Participation Preference",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.3
        )
        fig_pref.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_pref, use_container_width=True)

    with pie_col4:
        # Gender Distribution (Overall)
        gender_overall = merged_df['gender'].value_counts().reset_index()
        gender_overall.columns = ['gender','count']
        fig_gender_pie = px.pie(
            gender_overall, 
            names='gender', 
            values='count', 
            title="👥 Overall Gender Distribution",
            color_discrete_sequence=px.colors.qualitative.Safe,
            hole=0.3
        )
        fig_gender_pie.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig_gender_pie, use_container_width=True)

    # -------------------------
    # 🔹 BAR CHARTS SECTION (2-column layout)
    # -------------------------
    st.markdown('<div class="section-header">📊 Course Performance Analysis</div>', unsafe_allow_html=True)

    bar_col1, bar_col2 = st.columns(2)

    with bar_col1:
        # Number of Applicants per Course
        app_count = merged_df.groupby('course_name')['email'].count().reset_index().rename(columns={'email':'num_applicants'})
        fig_apps = px.bar(
            app_count, 
            x='num_applicants', 
            y='course_name', 
            orientation='h',
            title="📈 Applicants per Course",
            color='num_applicants',
            color_continuous_scale='Greens'
        )
        fig_apps.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_apps, use_container_width=True)

    with bar_col2:
        # Gender Distribution per Course
        gender_dist = merged_df.groupby(['course_name','gender']).size().reset_index(name='count')
        fig_gender = px.bar(
            gender_dist, 
            x='count', 
            y='course_name', 
            color='gender', 
            orientation='h',
            title="👥 Gender Distribution by Course",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig_gender.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_gender, use_container_width=True)

    # Second row of bar charts
    bar_col3, bar_col4 = st.columns(2)

    with bar_col3:
        # Course Capacity Analysis
        if 'students_count' in courses_df.columns:
            capacity_df = merged_df.groupby('course_name').agg({'email':'count','students_count':'first'}).reset_index()
            capacity_df.columns = ['course_name', 'applicants', 'capacity']
            capacity_df['remaining_slots'] = capacity_df['capacity'] - capacity_df['applicants']
            capacity_df['utilization_rate'] = (capacity_df['applicants'] / capacity_df['capacity'] * 100).round(1)
            
            fig_capacity = px.bar(
                capacity_df, 
                x='course_name', 
                y=['applicants', 'remaining_slots'],
                title="📋 Course Capacity vs Applications",
                color_discrete_sequence=['#4CAF50', '#8BC34A'],
                barmode='stack'
            )
            fig_capacity.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_capacity, use_container_width=True)

    with bar_col4:
        # How people heard about DataPlus
        if 'how_did_you_know_dataplus' in merged_df.columns:
            source_dist = merged_df['how_did_you_know_dataplus'].value_counts().reset_index()
            source_dist.columns = ['source','count']
            fig_source = px.bar(
                source_dist, 
                x='count', 
                y='source', 
                orientation='h',
                title="📢 How Applicants Found DataPlus",
                color='count',
                color_continuous_scale='Greens'
            )
            fig_source.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_source, use_container_width=True)
        else:
            st.info("📝 Marketing source data not available in current dataset")

    # -------------------------
    # 🔹 DETAILED TABLES SECTION
    # -------------------------
    st.markdown('<div class="section-header">📋 Detailed Data Tables</div>', unsafe_allow_html=True)

    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📚 Courses Overview", "📝 Applications Data", "📊 Summary Statistics"])

    with tab1:
        st.subheader("Available Courses")
        if 'training_date' in courses_df.columns:
            courses_display = courses_df[['title', 'description', 'featured', 'students_count', 'duration', 'training_date']].copy()
            courses_display['training_date'] = pd.to_datetime(courses_display['training_date']).dt.strftime('%Y-%m-%d')
        else:
            courses_display = courses_df[['title', 'description', 'featured', 'students_count', 'duration']].copy()
        
        st.dataframe(courses_display, use_container_width=True, height=400)

    with tab2:
        st.subheader("Course Applications")
        # Display applications with better formatting
        apps_display = apps_df.copy()
        if 'created_at' in apps_display.columns:
            apps_display['created_at'] = pd.to_datetime(apps_display['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        st.dataframe(apps_display, use_container_width=True, height=400)

    with tab3:
        st.subheader("Summary Statistics")
        
        # Create summary statistics
        summary_stats = pd.DataFrame({
            'Metric': [
                'Total Courses',
                'Total Applications', 
                'Unique Applicants',
                'Average Applications per Course',
                'Most Popular Course',
                'Course with Highest Capacity'
            ],
            'Value': [
                len(courses_df),
                len(apps_df),
                apps_df['email'].nunique(),
                round(len(apps_df) / len(courses_df), 2) if len(courses_df) > 0 else 0,
                app_count.loc[app_count['num_applicants'].idxmax(), 'course_name'] if not app_count.empty else 'N/A',
                courses_df.loc[courses_df['students_count'].idxmax(), 'title'] if 'students_count' in courses_df.columns else 'N/A'
            ]
        })
        
        st.dataframe(summary_stats, use_container_width=True, hide_index=True)
        
        # Course-wise breakdown
        st.subheader("Course-wise Application Breakdown")
        if not app_count.empty:
            course_breakdown = app_count.merge(
                courses_df[['title', 'students_count']], 
                left_on='course_name', 
                right_on='title', 
                how='left'
            )
            if 'students_count' in course_breakdown.columns:
                course_breakdown['utilization_rate'] = (course_breakdown['num_applicants'] / course_breakdown['students_count'] * 100).round(1)
                course_breakdown = course_breakdown[['course_name', 'num_applicants', 'students_count', 'utilization_rate']]
                course_breakdown.columns = ['Course', 'Applications', 'Capacity', 'Utilization %']
            else:
                course_breakdown = course_breakdown[['course_name', 'num_applicants']]
                course_breakdown.columns = ['Course', 'Applications']
            
            st.dataframe(course_breakdown, use_container_width=True, hide_index=True)
    # -------------------------
    # 🔹 Footer
    # -------------------------
    st.markdown("---")
    st.markdown("📊 **Dashboard powered by Streamlit & Plotly** | Data updated in real-time from Supabase")
