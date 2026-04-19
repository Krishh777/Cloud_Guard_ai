"""
CloudGuard AI Dashboard
Beautiful real-time visualization of findings
"""

import os
import sys
import json
import requests
import logging
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()

logger = logging.getLogger(__name__)

# Rest of the code stays the same...

# Page configuration
st.set_page_config(
    page_title="CloudGuard AI Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e3a8a;
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .critical { color: #ef4444; font-weight: bold; }
    .high { color: #f97316; font-weight: bold; }
    .medium { color: #eab308; font-weight: bold; }
    .low { color: #22c55e; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# APIs
FOG_API = os.getenv('FOG_API_ENDPOINT', 'http://localhost:8001')
CLOUD_API = os.getenv('CLOUD_API_ENDPOINT', 'http://localhost:8000')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data(ttl=60)
def get_findings_from_cache():
    """Fetch findings from Fog Layer cache"""
    try:
        response = requests.get(f"{FOG_API}/cache/findings", timeout=5)
        if response.status_code == 200:
            return response.json()['findings']
        return []
    except Exception as e:
        st.error(f"Error fetching findings: {e}")
        return []

@st.cache_data(ttl=60)
def get_stats():
    """Fetch statistics from Fog Layer"""
    try:
        response = requests.get(f"{FOG_API}/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching stats: {e}")
        return None

def get_severity_color(severity):
    """Get color for severity badge"""
    colors = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }
    return colors.get(severity, '⚪')

def format_cost(cost):
    """Format cost to currency"""
    return f"${cost:,}" if cost else "$0"

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.markdown("# 🛡️ CloudGuard AI")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "🔍 Findings", "📈 Analytics", "⚙️ Settings"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Filters
st.sidebar.subheader("Filters")
severity_filter = st.sidebar.multiselect(
    "Severity",
    ["critical", "high", "medium", "low"],
    default=["critical", "high", "medium"],
    key="severity_filter"
)

resource_filter = st.sidebar.multiselect(
    "Resource Type",
    ["s3", "ec2", "rds", "iam", "dynamodb"],
    default=["s3", "ec2", "rds", "iam"],
    key="resource_filter"
)

st.sidebar.markdown("---")

# Refresh button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")

# API Status
col1, col2 = st.sidebar.columns(2)
with col1:
    try:
        fog_status = requests.get(f"{FOG_API}/health", timeout=2).status_code == 200
        st.metric("Fog API", "✅" if fog_status else "❌")
    except:
        st.metric("Fog API", "❌")

with col2:
    try:
        cloud_status = requests.get(f"{CLOUD_API}/health", timeout=2).status_code == 200
        st.metric("Cloud API", "✅" if cloud_status else "❌")
    except:
        st.metric("Cloud API", "❌")

# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================

if page == "📊 Overview":
    st.title("🛡️ CloudGuard AI Security Dashboard")
    st.markdown("Real-time AWS security posture and threat analysis")
    
    # Get data
    findings = get_findings_from_cache()
    stats = get_stats()
    
    if not findings:
        st.warning("⚠️ No findings detected yet. Run the scanner to get started!")
        st.info("""
            **Getting Started:**
            1. Open terminal and run: `python edge_layer/scanner.py`
            2. Check back here for results
            3. Data will appear in ~30 seconds
        """)
    else:
        # Top metrics
        st.subheader("Security Posture")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            critical_count = stats.get('critical_count', 0)
            st.metric("🔴 Critical", critical_count)
        
        with col2:
            high_count = stats.get('high_count', 0)
            st.metric("🟠 High", high_count)
        
        with col3:
            medium_count = stats.get('medium_count', 0)
            st.metric("🟡 Medium", medium_count)
        
        with col4:
            low_count = stats.get('low_count', 0)
            st.metric("🟢 Low", low_count)
        
        with col5:
            avg_risk = stats.get('average_risk_score', 0)
            st.metric("📊 Avg Risk", f"{avg_risk:.1f}/100")
        
        st.markdown("---")
        
        # Financial Impact
        st.subheader("Financial Impact")
        total_cost = stats.get('total_estimated_cost', '$0')
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Estimated Breach Cost",
                total_cost,
                delta="If no action taken",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "ROI of Fixing Issues",
                f"Up to {(stats.get('average_risk_score', 50) * 10):,.0f}",
                delta="Potential savings",
                delta_color="off"
            )
        
        st.markdown("---")
        
        # Severity Distribution Chart
        st.subheader("Finding Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            severity_data = {
                'Severity': list(stats.get('severity_breakdown', {}).keys()),
                'Count': list(stats.get('severity_breakdown', {}).values())
            }
            
            fig = px.pie(
                severity_data,
                values='Count',
                names='Severity',
                color='Severity',
                color_discrete_map={
                    'critical': '#ef4444',
                    'high': '#f97316',
                    'medium': '#eab308',
                    'low': '#22c55e'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Risk Score Distribution
            risk_scores = [f.get('risk_score', 0) for f in findings]
            
            fig = go.Figure(data=[
                go.Histogram(
                    x=risk_scores,
                    nbinsx=20,
                    marker_color='#3b82f6'
                )
            ])
            fig.update_layout(
                title="Risk Score Distribution",
                xaxis_title="Risk Score (0-100)",
                yaxis_title="Count",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Top Critical Findings
        st.subheader("🔴 Top Critical Findings")
        
        critical_findings = [f for f in findings if f.get('severity') == 'critical']
        
        if critical_findings:
            for idx, finding in enumerate(critical_findings[:5], 1):
                with st.expander(f"{idx}. {finding['finding_type']} - {finding['resource_id']}", expanded=idx==1):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Severity", "🔴 CRITICAL")
                    
                    with col2:
                        st.metric("Risk Score", f"{finding.get('risk_score', 0):.0f}/100")
                    
                    with col3:
                        st.metric("Cost Impact", format_cost(finding.get('estimated_cost', 0)))
                    
                    with col4:
                        st.metric("Priority", f"#{finding.get('priority', 0)}")
                    
                    st.markdown("**Description:**")
                    st.write(finding.get('description', 'N/A'))
                    
                    st.markdown("**Recommendation:**")
                    rec = finding.get('recommendation', {})
                    if isinstance(rec, dict):
                        st.markdown(f"**{rec.get('title', 'Fix This Issue')}**")
                        st.markdown(f"**Difficulty:** {rec.get('difficulty', 'Unknown')}")
                        st.markdown(f"**Time to Fix:** {rec.get('time_to_fix', 'Varies')}")
                        
                        st.markdown("**Steps:**")
                        for step in rec.get('steps', []):
                            st.write(step)
        else:
            st.success("✅ No critical findings! Great job!")

# ============================================================================
# PAGE 2: FINDINGS
# ============================================================================

elif page == "🔍 Findings":
    st.title("🔍 Security Findings")
    st.markdown("Detailed view of all security issues")
    
    findings = get_findings_from_cache()
    
    if not findings:
        st.info("No findings yet. Run the scanner to get started!")
    else:
        # Filter findings
        df = pd.DataFrame(findings)
        
        # Apply filters
        if severity_filter:
            df = df[df['severity'].isin(severity_filter)]
        
        if resource_filter:
            df = df[df['resource_type'].isin(resource_filter)]
        
        st.subheader(f"Found {len(df)} Issues")
        
        # Sort by severity then risk score
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        df['severity_order'] = df['severity'].map(severity_order)
        df = df.sort_values(['severity_order', 'risk_score'], ascending=[True, False])
        df = df.drop('severity_order', axis=1)
        
        # Display as table
        display_cols = ['finding_type', 'severity', 'risk_score', 'estimated_cost', 'resource_id']
        
        for idx, row in df.iterrows():
            with st.expander(
                f"{get_severity_color(row['severity'])} {row['finding_type']} | "
                f"Risk: {row['risk_score']:.0f} | Cost: {format_cost(row['estimated_cost'])}",
                expanded=False
            ):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Type", row['resource_type'].upper())
                
                with col2:
                    st.metric("Risk", f"{row['risk_score']:.0f}/100")
                
                with col3:
                    st.metric("Cost", format_cost(row['estimated_cost']))
                
                with col4:
                    st.metric("Priority", f"#{row.get('priority', 'N/A')}")
                
                st.markdown("**Description:**")
                st.write(row['description'])
                
                st.markdown("**Recommendation:**")
                rec = row.get('recommendation', {})
                if isinstance(rec, dict):
                    st.markdown(f"### {rec.get('title', 'Fix This Issue')}")
                    st.markdown(f"📊 **Difficulty:** {rec.get('difficulty', 'Unknown')}")
                    st.markdown(f"⏱️ **Time to Fix:** {rec.get('time_to_fix', 'Varies')}")
                    
                    st.markdown("**Steps to Fix:**")
                    for step in rec.get('steps', []):
                        st.write(f"• {step}")

# ============================================================================
# PAGE 3: ANALYTICS
# ============================================================================

elif page == "📈 Analytics":
    st.title("📈 Analytics & Insights")
    st.markdown("Advanced metrics and trends")
    
    findings = get_findings_from_cache()
    
    if not findings:
        st.info("No data available yet!")
    else:
        df = pd.DataFrame(findings)
        
        # Top resource types
        st.subheader("Resource Type Distribution")
        resource_counts = df['resource_type'].value_counts()
        
        fig = px.bar(
            x=resource_counts.values,
            y=resource_counts.index,
            orientation='h',
            labels={'x': 'Count', 'y': 'Resource Type'},
            color=resource_counts.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Top finding types
        st.subheader("Top Finding Types")
        finding_counts = df['finding_type'].value_counts()
        
        fig = px.bar(
            finding_counts,
            labels={'index': 'Finding Type', 'value': 'Count'},
            color=finding_counts.values,
            color_continuous_scale='Oranges'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Risk vs Cost
        st.subheader("Risk Score vs Estimated Cost")
        
        fig = px.scatter(
            df,
            x='risk_score',
            y='estimated_cost',
            color='severity',
            size='estimated_cost',
            hover_data=['finding_type', 'resource_id'],
            color_discrete_map={
                'critical': '#ef4444',
                'high': '#f97316',
                'medium': '#eab308',
                'low': '#22c55e'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Summary stats
        st.subheader("Summary Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Findings", len(df))
        
        with col2:
            avg_risk = df['risk_score'].mean()
            st.metric("Avg Risk Score", f"{avg_risk:.1f}/100")
        
        with col3:
            max_cost = df['estimated_cost'].max()
            st.metric("Highest Cost", format_cost(max_cost))
        
        with col4:
            total_cost = df['estimated_cost'].sum()
            st.metric("Total Cost", format_cost(total_cost))

# ============================================================================
# PAGE 4: SETTINGS
# ============================================================================

elif page == "⚙️ Settings":
    st.title("⚙️ Settings & Configuration")
    
    tab1, tab2, tab3 = st.tabs(["📋 Configuration", "🗑️ Cache Management", "ℹ️ About"])
    
    with tab1:
        st.subheader("Current Configuration")
        
        config = {
            "AWS Region": os.getenv('AWS_REGION'),
            "Fog API": FOG_API,
            "Cloud API": CLOUD_API,
            "DynamoDB Table": os.getenv('DYNAMODB_TABLE_NAME'),
            "RDS Host": os.getenv('DB_HOST', 'Not configured'),
        }
        
        for key, value in config.items():
            st.text_input(key, value, disabled=True)
    
    with tab2:
        st.subheader("Cache Management")
        
        if st.button("🗑️ Clear All Cached Findings", use_container_width=True):
            try:
                response = requests.delete(f"{FOG_API}/cache/clear", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Cache cleared successfully!")
                    st.cache_data.clear()
                    st.rerun()
            except Exception as e:
                st.error(f"Error clearing cache: {e}")
    
    with tab3:
        st.subheader("About CloudGuard AI")
        st.markdown("""
        **CloudGuard AI** is an intelligent AWS security scanning and analysis platform.
        
        ### Features
        - 🔍 Automated AWS security scanning
        - 🤖 ML-powered risk analysis
        - 💰 Financial impact estimation
        - 📊 Beautiful dashboards
        - 🚨 Real-time alerts
        
        ### Architecture
        - **Edge Layer:** Scans AWS account
        - **Fog Layer:** Enriches findings with risk scores
        - **Cloud Layer:** ML analysis and predictions
        - **Dashboard:** Real-time visualization
        
        ### Technology Stack
        - AWS (EC2, RDS, DynamoDB, SNS, S3)
        - Python (FastAPI, scikit-learn)
        - Streamlit (Dashboard)
        - PostgreSQL (Data storage)
        
        Made for college demo 🎓
        """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
        CloudGuard AI Dashboard | Last refreshed: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
    </div>
""", unsafe_allow_html=True)