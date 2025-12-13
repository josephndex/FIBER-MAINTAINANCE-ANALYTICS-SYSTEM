"""
Suggestions Page - User Feedback and Feature Requests
Allows users to suggest improvements and new features for the application
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
import sys
sys.path.insert(0, '..')

from config import THEME_COLORS
from auth import require_authentication, log_page_visit, get_current_user

# Require authentication
require_authentication()
log_page_visit("21_Suggestions.py")

# Get current user
current_user = get_current_user()
username = current_user.get('username', 'Anonymous') if current_user else 'Anonymous'

# File to store suggestions
SUGGESTIONS_FILE = "data/suggestions.json"

def load_suggestions():
    """Load suggestions from JSON file"""
    if os.path.exists(SUGGESTIONS_FILE):
        try:
            with open(SUGGESTIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_suggestions(suggestions):
    """Save suggestions to JSON file"""
    os.makedirs(os.path.dirname(SUGGESTIONS_FILE), exist_ok=True)
    with open(SUGGESTIONS_FILE, 'w') as f:
        json.dump(suggestions, f, indent=2, default=str)

def add_suggestion(category, title, description, priority, submitted_by):
    """Add a new suggestion"""
    suggestions = load_suggestions()
    new_suggestion = {
        'id': len(suggestions) + 1,
        'category': category,
        'title': title,
        'description': description,
        'priority': priority,
        'submitted_by': submitted_by,
        'submitted_at': datetime.now().isoformat(),
        'status': 'New',
        'votes': 0,
        'comments': []
    }
    suggestions.append(new_suggestion)
    save_suggestions(suggestions)
    return True

def vote_suggestion(suggestion_id):
    """Upvote a suggestion"""
    suggestions = load_suggestions()
    for s in suggestions:
        if s['id'] == suggestion_id:
            s['votes'] = s.get('votes', 0) + 1
            break
    save_suggestions(suggestions)

# Page header
st.markdown("""
<div style='
    background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
'>
    <h1 style='margin: 0;'>💡 Suggestions & Feedback</h1>
    <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>Help us improve! Share your ideas for new features and enhancements</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Submit Suggestion", "📋 View Suggestions", "📊 Suggestion Stats"])

with tab1:
    st.markdown("### Submit a New Suggestion")
    st.markdown("Have an idea to make this app better? We'd love to hear it!")
    
    with st.form("suggestion_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox(
                "Category",
                options=[
                    "🆕 New Feature",
                    "🔧 Improvement",
                    "🐛 Bug Fix",
                    "📊 New Dashboard/Chart",
                    "📱 UI/UX Enhancement",
                    "📈 New Report Type",
                    "🔔 Notifications/Alerts",
                    "📤 Data Export",
                    "🔐 Security",
                    "📚 Documentation",
                    "🎯 Other"
                ],
                help="Select the type of suggestion"
            )
        
        with col2:
            priority = st.selectbox(
                "Priority",
                options=["🟢 Low", "🟡 Medium", "🟠 High", "🔴 Critical"],
                index=1,
                help="How important is this to you?"
            )
        
        title = st.text_input(
            "Title",
            placeholder="Brief title for your suggestion...",
            help="Give your suggestion a clear, concise title"
        )
        
        description = st.text_area(
            "Description",
            placeholder="Describe your suggestion in detail...\n\n• What problem does this solve?\n• How should it work?\n• Any examples or references?",
            height=150,
            help="Provide as much detail as possible"
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"Submitting as: **{username}**")
        with col2:
            submitted = st.form_submit_button("📤 Submit", use_container_width=True, type="primary")
        
        if submitted:
            if not title.strip():
                st.error("Please provide a title for your suggestion.")
            elif not description.strip():
                st.error("Please provide a description for your suggestion.")
            else:
                if add_suggestion(category, title.strip(), description.strip(), priority, username):
                    st.success("✅ Thank you! Your suggestion has been submitted successfully.")
                    st.balloons()
                else:
                    st.error("Failed to submit suggestion. Please try again.")

    # Quick suggestion ideas
    st.markdown("---")
    st.markdown("### 💭 Need inspiration? Here are some areas to consider:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Dashboards**
        - New metrics to track
        - Different chart types
        - Custom date ranges
        - Comparison views
        """)
    
    with col2:
        st.markdown("""
        **📈 Reports**
        - New report templates
        - Scheduled reports
        - Email delivery
        - Custom branding
        """)
    
    with col3:
        st.markdown("""
        **🔔 Alerts**
        - SLA breach notifications
        - Performance alerts
        - Trend anomalies
        - Daily/Weekly summaries
        """)

with tab2:
    st.markdown("### All Suggestions")
    
    suggestions = load_suggestions()
    
    if not suggestions:
        st.info("No suggestions yet. Be the first to submit one!")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_status = st.selectbox(
                "Filter by Status",
                options=["All", "New", "Under Review", "Planned", "In Progress", "Completed", "Declined"],
                index=0
            )
        
        with col2:
            filter_category = st.selectbox(
                "Filter by Category",
                options=["All"] + list(set(s['category'] for s in suggestions)),
                index=0
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                options=["Newest First", "Most Votes", "Priority"],
                index=0
            )
        
        # Apply filters
        filtered = suggestions.copy()
        
        if filter_status != "All":
            filtered = [s for s in filtered if s.get('status') == filter_status]
        
        if filter_category != "All":
            filtered = [s for s in filtered if s.get('category') == filter_category]
        
        # Apply sorting
        if sort_by == "Newest First":
            filtered = sorted(filtered, key=lambda x: x.get('submitted_at', ''), reverse=True)
        elif sort_by == "Most Votes":
            filtered = sorted(filtered, key=lambda x: x.get('votes', 0), reverse=True)
        elif sort_by == "Priority":
            priority_order = {"🔴 Critical": 0, "🟠 High": 1, "🟡 Medium": 2, "🟢 Low": 3}
            filtered = sorted(filtered, key=lambda x: priority_order.get(x.get('priority', '🟢 Low'), 4))
        
        st.markdown(f"*Showing {len(filtered)} of {len(suggestions)} suggestions*")
        st.markdown("---")
        
        # Display suggestions
        for suggestion in filtered:
            status_colors = {
                'New': '#3b82f6',
                'Under Review': '#f59e0b',
                'Planned': '#8b5cf6',
                'In Progress': '#10b981',
                'Completed': '#22c55e',
                'Declined': '#ef4444'
            }
            
            status = suggestion.get('status', 'New')
            status_color = status_colors.get(status, '#6b7280')
            
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 1rem;
                border-left: 4px solid {status_color};
            '>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div>
                        <span style='color: #94a3b8; font-size: 0.8rem;'>{suggestion.get('category', 'Other')}</span>
                        <h4 style='margin: 0.25rem 0; color: #f1f5f9;'>{suggestion.get('title', 'Untitled')}</h4>
                    </div>
                    <div style='text-align: right;'>
                        <span style='background: {status_color}; color: white; padding: 0.25rem 0.75rem; 
                                     border-radius: 15px; font-size: 0.75rem; font-weight: 600;'>{status}</span>
                        <br>
                        <span style='color: #64748b; font-size: 0.75rem;'>{suggestion.get('priority', '🟡 Medium')}</span>
                    </div>
                </div>
                <p style='color: #94a3b8; margin: 0.75rem 0; font-size: 0.9rem;'>
                    {suggestion.get('description', '')[:200]}{'...' if len(suggestion.get('description', '')) > 200 else ''}
                </p>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;'>
                    <span style='color: #64748b; font-size: 0.8rem;'>
                        By {suggestion.get('submitted_by', 'Anonymous')} • 
                        {suggestion.get('submitted_at', '')[:10] if suggestion.get('submitted_at') else 'Unknown date'}
                    </span>
                    <span style='color: #10b981; font-size: 0.9rem;'>
                        👍 {suggestion.get('votes', 0)} votes
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Vote button
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button(f"👍 Vote", key=f"vote_{suggestion['id']}"):
                    vote_suggestion(suggestion['id'])
                    st.rerun()
            with col2:
                with st.expander("Details"):
                    st.write(f"**Full Description:**")
                    st.write(suggestion.get('description', 'No description'))

with tab3:
    st.markdown("### Suggestion Statistics")
    
    suggestions = load_suggestions()
    
    if not suggestions:
        st.info("No suggestions to analyze yet.")
    else:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Suggestions", len(suggestions))
        
        with col2:
            new_count = len([s for s in suggestions if s.get('status') == 'New'])
            st.metric("New", new_count)
        
        with col3:
            completed_count = len([s for s in suggestions if s.get('status') == 'Completed'])
            st.metric("Completed", completed_count)
        
        with col4:
            total_votes = sum(s.get('votes', 0) for s in suggestions)
            st.metric("Total Votes", total_votes)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Category distribution
            st.markdown("##### By Category")
            category_counts = {}
            for s in suggestions:
                cat = s.get('category', 'Other')
                category_counts[cat] = category_counts.get(cat, 0) + 1
            
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                st.write(f"{cat}: **{count}**")
        
        with col2:
            # Status distribution
            st.markdown("##### By Status")
            status_counts = {}
            for s in suggestions:
                status = s.get('status', 'New')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                st.write(f"{status}: **{count}**")
        
        st.markdown("---")
        
        # Top voted suggestions
        st.markdown("##### 🏆 Top Voted Suggestions")
        top_voted = sorted(suggestions, key=lambda x: x.get('votes', 0), reverse=True)[:5]
        
        for idx, s in enumerate(top_voted, 1):
            st.markdown(f"""
            **{idx}. {s.get('title', 'Untitled')}** - 👍 {s.get('votes', 0)} votes  
            *{s.get('category', 'Other')} • {s.get('status', 'New')}*
            """)
        
        # Recent submissions
        st.markdown("---")
        st.markdown("##### 🕒 Recent Submissions")
        recent = sorted(suggestions, key=lambda x: x.get('submitted_at', ''), reverse=True)[:5]
        
        for s in recent:
            submitted_at = s.get('submitted_at', '')[:10] if s.get('submitted_at') else 'Unknown'
            st.markdown(f"""
            **{s.get('title', 'Untitled')}**  
            *Submitted by {s.get('submitted_by', 'Anonymous')} on {submitted_at}*
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 1rem;'>
    <p>Your suggestions help us build a better tool for everyone! 🚀</p>
    <p style='font-size: 0.8rem;'>All suggestions are reviewed by the development team.</p>
</div>
""", unsafe_allow_html=True)
