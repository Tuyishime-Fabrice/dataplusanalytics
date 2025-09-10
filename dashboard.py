import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
import os

# -------------------------
# 🔐 Secure credential handling
# -------------------------
# Get credentials from environment variables (for deployment) or use secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ppycnugwogonwcteeyff.supabase.co")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBweWNudWd3b2dvbndjdGVleWZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc5OTYyNDQsImV4cCI6MjA2MzU3MjI0NH0.UpcVkpxEqzfoNApLys_b651qu6cGlZHLWZdyfjB8Uv4")

# Try to get from Streamlit secrets if available (for deployment)
try:
    SUPABASE_URL = st.secrets.get("SUPABASE_URL", SUPABASE_URL)
    SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", SUPABASE_ANON_KEY)
except:
    pass  # If secrets aren't available, use the fallback values

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.set_page_config(page_title="Courses & Applications Dashboard", layout="wide")
st.title("🎓 Courses & Applications Analysis")

# -------------------------
# 🔹 Step 2: Fetch courses and applications
# -------------------------
courses_resp = supabase.table("courses").select("*").execute()
courses_df = pd.DataFrame(courses_resp.data)

apps_resp = supabase.table("course_applications").select("*").execute()
apps_df = pd.DataFrame(apps_resp.data)

# -------------------------
# 🔹 Step 3: Display raw tables
# -------------------------
st.subheader("Courses Overview")
st.dataframe(courses_df[['title', 'description', 'featured', 'students_count', 'duration', 'training_date']])

st.subheader("Applications Preview")
st.dataframe(apps_df)   # show full table with all columns

# -------------------------
# 🔹 Step 4: Merge applications with courses
# -------------------------
merged_df = apps_df.merge(
    courses_df[['title','students_count']], 
    left_on='course_name', 
    right_on='title', 
    how='left'
)

# -------------------------
# 🔹 Step 5: Analysis
# -------------------------
st.subheader("📊 Number of Applicants per Course")
app_count = merged_df.groupby('course_name')['email'].count().reset_index().rename(columns={'email':'num_applicants'})
fig1 = px.bar(app_count, x='course_name', y='num_applicants', title="Applicants per Course")
st.plotly_chart(fig1)

st.subheader("👥 Gender Distribution per Course")
gender_dist = merged_df.groupby(['course_name','gender']).size().reset_index(name='count')
fig2 = px.bar(gender_dist, x='course_name', y='count', color='gender', barmode='group', title="Gender Distribution")
st.plotly_chart(fig2)

st.subheader("🎓 Education Level Distribution")
edu_dist = merged_df['education_level'].value_counts().reset_index()
edu_dist.columns = ['education_level','count']
fig3 = px.pie(edu_dist, names='education_level', values='count', title="Education Levels of Applicants")
st.plotly_chart(fig3)

st.subheader("💻 Python Experience Level")
exp_dist = merged_df['python_experience_level'].value_counts().reset_index()
exp_dist.columns = ['experience_level','count']
fig4 = px.pie(exp_dist, names='experience_level', values='count', title="Python Experience Levels")
st.plotly_chart(fig4)

st.subheader("🏫 Participation Preference (Online/In-Person/Hybrid)")
pref_dist = merged_df['participation_preference'].value_counts().reset_index()
pref_dist.columns = ['preference','count']
fig5 = px.pie(pref_dist, names='preference', values='count', title="Participation Preference")
st.plotly_chart(fig5)

st.subheader("📋 Course Capacity vs Registered Applicants")
capacity_df = merged_df.groupby('course_name').agg({'email':'count','students_count':'first'}).reset_index()
capacity_df['remaining_slots'] = capacity_df['students_count'] - capacity_df['email']
fig6 = px.bar(
    capacity_df, 
    x='course_name', 
    y=['email','remaining_slots'],
    labels={'value':'Number of Students', 'course_name':'Course'},
    barmode='stack', 
    title="Course Capacity vs Registered Applicants"
)
st.plotly_chart(fig6)

# -------------------------
# 🔹 Step 6: How people heard about DataPlus
# -------------------------
if 'how_did_you_know_dataplus' in merged_df.columns:
    st.subheader("📢 How Applicants Heard About DataPlus")
    source_dist = merged_df['how_did_you_know_dataplus'].value_counts().reset_index()
    source_dist.columns = ['source','count']
    fig7 = px.bar(source_dist, x='source', y='count', 
                  title="Where Applicants Heard About DataPlus",
                  labels={'source':'Source', 'count':'Number of Applicants'})
    st.plotly_chart(fig7)
else:
    st.warning("Column 'how_did_you_know_dataplus' not found in course_applications table.")