"""
WFM Forecasting Calculator
Erlang C, Shrinkage, FTE Planning

Author: Hatem Shalaby
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from src.erlang_c import required_agents, service_level, occupancy, erlang_c
from src.wfm_calculations import (calculate_shrinkage, calculate_required_fte, 
                              interval_staffing_plan, forecast_volume)

# Page config
st.set_page_config(
    page_title="WFM Forecasting Calculator",
    page_icon="📞",
    layout="wide"
)

# Header
st.title("📞 WFM Forecasting Calculator")
st.markdown("**Workforce Management Planning Tool - Erlang C & Staffing Models**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Calculator Mode")
    
    mode = st.radio(
        "Select Calculation:",
        ["Quick Staffing", "Interval Planning", "Shrinkage Analysis", "FTE Planning"]
    )
    
    st.markdown("---")
    st.markdown("### 📖 WFM Formulas")
    st.markdown("""
    **Erlang C:** Probability of queueing
    
    **Service Level:** % answered in X seconds
    
    **Occupancy:** Agent utilization %
    
    **Shrinkage:** Non-productive time %
    """)

# QUICK STAFFING MODE
if mode == "Quick Staffing":
    st.subheader("🎯 Quick Staffing Calculator")
    st.markdown("Calculate required agents for a single interval")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📊 Volume Inputs**")
        call_volume = st.number_input("Calls in Interval", min_value=1, value=100, step=10)
        interval_minutes = st.number_input("Interval Length (min)", min_value=15, max_value=60, value=30, step=15)
    
    with col2:
        st.markdown("**⏱️ Timing Inputs**")
        aht_seconds = st.number_input("Average Handle Time (sec)", min_value=30, value=180, step=15)
        target_answer_time = st.number_input("Target Answer Time (sec)", min_value=5, max_value=120, value=20, step=5)
    
    with col3:
        st.markdown("**🎯 Target Metrics**")
        target_sl = st.slider("Target Service Level %", min_value=50, max_value=100, value=80, step=5)
        max_occupancy = st.slider("Max Occupancy %", min_value=70, max_value=95, value=85, step=5)
    
    if st.button("🔄 Calculate Required Agents", type="primary"):
        with st.spinner("Calculating..."):
            result = required_agents(
                call_volume=call_volume,
                aht=aht_seconds,
                interval_minutes=interval_minutes,
                target_sl=target_sl,
                target_answer_time=target_answer_time,
                max_occupancy=max_occupancy
            )
        
        st.markdown("---")
        st.subheader("📈 Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Required Agents", result['required_agents'])
        
        with col2:
            sl_delta = result['achieved_sl'] - target_sl
            st.metric("Achieved SL", f"{result['achieved_sl']}%", delta=f"{sl_delta:+.1f}%")
        
        with col3:
            occ_color = "🟢" if result['occupancy'] <= max_occupancy else "🔴"
            st.metric("Occupancy", f"{result['occupancy']}% {occ_color}")
        
        with col4:
            st.metric("Avg Speed Answer", f"{result['asa']:.1f}s")
        
        # Sensitivity Analysis
        st.markdown("---")
        st.subheader("🔍 Sensitivity Analysis")
        
        sensitivity_data = []
        for agents in range(max(1, result['required_agents'] - 5), result['required_agents'] + 6):
            sl = service_level(agents, result['traffic_intensity'], target_answer_time, aht_seconds)
            occ = occupancy(result['traffic_intensity'], agents)
            
            sensitivity_data.append({
                'Agents': agents,
                'Service Level %': round(sl, 1),
                'Occupancy %': round(occ, 1)
            })
        
        sens_df = pd.DataFrame(sensitivity_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sens_df['Agents'], y=sens_df['Service Level %'], 
                                 name='Service Level', mode='lines+markers', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=sens_df['Agents'], y=sens_df['Occupancy %'], 
                                 name='Occupancy', mode='lines+markers', line=dict(color='orange')))
        
        fig.add_hline(y=target_sl, line_dash="dash", line_color="blue", annotation_text=f"Target SL: {target_sl}%")
        fig.add_hline(y=max_occupancy, line_dash="dash", line_color="orange", annotation_text=f"Max Occ: {max_occupancy}%")
        
        fig.update_layout(
            title="Agent Count Impact on SL & Occupancy",
            xaxis_title="Number of Agents",
            yaxis_title="Percentage",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# INTERVAL PLANNING MODE
elif mode == "Interval Planning":
    st.subheader("📅 Interval Staffing Plan")
    st.markdown("Generate 30-minute interval staffing for full day")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Input Method**")
        input_method = st.radio("Choose input:", ["Manual Entry", "Upload CSV"])
        
        if input_method == "Manual Entry":
            st.markdown("**Hourly Call Volumes (0-23):**")
            hourly_volumes = []
            
            cols = st.columns(6)
            for i in range(24):
                with cols[i % 6]:
                    vol = st.number_input(f"Hour {i}", min_value=0, value=50 if 9 <= i <= 17 else 10, 
                                         key=f"hour_{i}", label_visibility="visible")
                    hourly_volumes.append(vol)
        else:
            uploaded = st.file_uploader("Upload hourly volumes CSV", type=['csv'])
            if uploaded:
                df = pd.read_csv(uploaded)
                hourly_volumes = df['volume'].tolist()[:24]
            else:
                hourly_volumes = [50] * 24
    
    with col2:
        st.markdown("**⚙️ Parameters**")
        aht = st.number_input("AHT (seconds)", value=180)
        target_sl = st.slider("Target SL %", 50, 100, 80)
        target_answer = st.number_input("Target Answer (sec)", value=20)
    
    if st.button("📊 Generate Staffing Plan"):
        with st.spinner("Building interval plan..."):
            plan_df = interval_staffing_plan(
                hourly_volumes=hourly_volumes,
                aht_seconds=aht,
                target_sl=target_sl,
                target_answer_time=target_answer
            )
        
        st.markdown("---")
        
        # Visualization
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=plan_df['interval'], y=plan_df['calls'], 
                                 name='Call Volume', yaxis='y', mode='lines', line=dict(color='blue')))
        fig.add_trace(go.Bar(x=plan_df['interval'], y=plan_df['required_agents'], 
                            name='Required Agents', yaxis='y2', marker_color='green'))
        
        fig.update_layout(
            title='Interval Staffing Requirements',
            xaxis=dict(title='Time Interval', tickangle=45),
            yaxis=dict(title='Call Volume', side='left'),
            yaxis2=dict(title='Required Agents', side='right', overlaying='y'),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.subheader("📋 Detailed Plan")
        st.dataframe(plan_df, use_container_width=True, height=400)
        
        # Export
        csv = plan_df.to_csv(index=False)
        st.download_button("📥 Download Plan", csv, "staffing_plan.csv", "text/csv")

# SHRINKAGE ANALYSIS
elif mode == "Shrinkage Analysis":
    st.subheader("📉 Shrinkage Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⏰ Non-Productive Time (minutes/day)**")
        breaks = st.number_input("Breaks", value=30)
        lunch = st.number_input("Lunch", value=30)
        meetings = st.number_input("Meetings", value=30)
        training = st.number_input("Training", value=15)
        other = st.number_input("Other (coaching, 1-on-1s)", value=15)
    
    with col2:
        st.markdown("**📊 Shift Information**")
        shift_length = st.number_input("Shift Length (minutes)", value=480, step=30)
        
        shrinkage_result = calculate_shrinkage(breaks, lunch, meetings, training, other, shift_length)
        
        st.markdown("---")
        st.metric("Total Shrinkage", f"{shrinkage_result['shrinkage_pct']}%", 
                 f"{shrinkage_result['total_shrinkage_min']} min")
        st.metric("Productive Time", f"{shrinkage_result['productive_time_min']} min")
    
    # Pie chart
    shrinkage_breakdown = {
        'Breaks': breaks,
        'Lunch': lunch,
        'Meetings': meetings,
        'Training': training,
        'Other': other,
        'Productive Time': shrinkage_result['productive_time_min']
    }
    
    fig = px.pie(
        values=list(shrinkage_breakdown.values()),
        names=list(shrinkage_breakdown.keys()),
        title='Time Allocation Breakdown'
    )
    st.plotly_chart(fig, use_container_width=True)

# FTE PLANNING
elif mode == "FTE Planning":
    st.subheader("👥 FTE Requirement Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Base Requirements**")
        base_agents = st.number_input("Base Agents (from Erlang C)", value=20, min_value=1)
        shrinkage_pct = st.slider("Shrinkage %", 0, 50, 25)
        absenteeism_pct = st.slider("Absenteeism %", 0, 20, 5)
    
    with col2:
        st.markdown("**💰 Cost Analysis (Optional)**")
        monthly_salary = st.number_input("Monthly Salary per Agent", value=5000, step=500)
        benefits_pct = st.slider("Benefits % of Salary", 0, 50, 20)
    
    if st.button("Calculate FTE Needs"):
        fte_result = calculate_required_fte(base_agents, shrinkage_pct, absenteeism_pct)
        
        st.markdown("---")
        st.subheader("📈 FTE Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Base Agents", fte_result['base_requirement'])
        
        with col2:
            st.metric("After Shrinkage", fte_result['after_shrinkage'])
        
        with col3:
            st.metric("Total FTE Needed", fte_result['total_fte'], 
                     f"+{fte_result['overhead_agents']} overhead")
        
        # Cost calculation
        if monthly_salary > 0:
            st.markdown("---")
            st.subheader("💵 Cost Impact")
            
            total_cost = fte_result['total_fte'] * monthly_salary * (1 + benefits_pct / 100)
            base_cost = base_agents * monthly_salary * (1 + benefits_pct / 100)
            overhead_cost = total_cost - base_cost
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Monthly Cost", f"${total_cost:,.0f}")
            
            with col2:
                st.metric("Annual Cost", f"${total_cost * 12:,.0f}")
            
            with col3:
                st.metric("Overhead Cost", f"${overhead_cost:,.0f}/mo")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Built by <strong>Hatem Shalaby</strong> | WFM Automation Expert</p>
    <p><a href='https://github.com/hatemismail2011shalaby'>GitHub</a> | 
    <a href='https://linkedin.com/in/hatem-shalaby-7359611a2'>LinkedIn</a></p>
</div>
""", unsafe_allow_html=True)