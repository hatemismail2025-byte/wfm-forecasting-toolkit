"""
Workforce Management Calculations
Shrinkage, FTE requirements, cost modeling
"""

import pandas as pd
import numpy as np
import math

def calculate_shrinkage(breaks_min, lunch_min, meetings_min, training_min, 
                       other_min, shift_length_min):
    """
    Calculate total shrinkage percentage
    
    Shrinkage = (Non-productive time / Total paid time) × 100
    
    Args:
        All time values in minutes per day
    
    Returns:
        dict with breakdown and total shrinkage %
    """
    
    total_shrinkage_min = breaks_min + lunch_min + meetings_min + training_min + other_min
    shrinkage_pct = (total_shrinkage_min / shift_length_min) * 100
    
    return {
        'breaks': breaks_min,
        'lunch': lunch_min,
        'meetings': meetings_min,
        'training': training_min,
        'other': other_min,
        'total_shrinkage_min': total_shrinkage_min,
        'shift_length_min': shift_length_min,
        'productive_time_min': shift_length_min - total_shrinkage_min,
        'shrinkage_pct': round(shrinkage_pct, 2)
    }


def calculate_required_fte(base_agents, shrinkage_pct, absenteeism_pct=5):
    """
    Calculate total FTE needed accounting for shrinkage and absenteeism
    
    Args:
        base_agents: Base agents needed (from Erlang C)
        shrinkage_pct: Shrinkage percentage
        absenteeism_pct: Expected absenteeism rate
    
    Returns:
        dict with FTE breakdown
    """
    
    # Account for shrinkage
    agents_with_shrinkage = base_agents / (1 - shrinkage_pct / 100)
    
    # Account for absenteeism
    total_fte = agents_with_shrinkage / (1 - absenteeism_pct / 100)
    
    return {
        'base_requirement': base_agents,
        'after_shrinkage': round(agents_with_shrinkage, 2),
        'total_fte': math.ceil(total_fte),
        'shrinkage_pct': shrinkage_pct,
        'absenteeism_pct': absenteeism_pct,
        'overhead_agents': math.ceil(total_fte) - base_agents
    }


def calculate_cost_per_contact(total_agent_cost, total_contacts):
    """
    Calculate cost per contact handled
    
    Args:
        total_agent_cost: Total agent costs (salary + benefits)
        total_contacts: Total contacts handled in period
    
    Returns:
        float: Cost per contact
    """
    
    if total_contacts == 0:
        return 0
    
    return round(total_agent_cost / total_contacts, 2)


def forecast_volume(historical_data, periods_ahead=1, method='moving_average', window=4):
    """
    Simple volume forecasting using moving average or linear trend
    
    Args:
        historical_data: List or array of historical volumes
        periods_ahead: Number of periods to forecast
        method: 'moving_average' or 'linear_trend'
        window: Window size for moving average
    
    Returns:
        list: Forecasted volumes
    """
    
    data = np.array(historical_data)
    
    if method == 'moving_average':
        # Simple moving average
        if len(data) < window:
            forecast = np.mean(data)
        else:
            forecast = np.mean(data[-window:])
        
        return [round(forecast)] * periods_ahead
    
    elif method == 'linear_trend':
        # Linear regression for trend
        x = np.arange(len(data))
        y = data
        
        # Simple linear regression
        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x ** 2)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        forecasts = []
        for i in range(1, periods_ahead + 1):
            next_x = len(data) + i - 1
            forecast = slope * next_x + intercept
            forecasts.append(round(max(0, forecast)))
        
        return forecasts
    
    return [0] * periods_ahead


def interval_staffing_plan(hourly_volumes, aht_seconds, target_sl=80, 
                           target_answer_time=20, interval_minutes=30):
    """
    Create interval-by-interval staffing plan for a day
    
    Args:
        hourly_volumes: List of call volumes by hour (24 elements)
        aht_seconds: Average Handle Time
        target_sl: Target service level %
        target_answer_time: Target answer time in seconds
        interval_minutes: Interval length (default 30)
    
    Returns:
        DataFrame with staffing requirements by interval
    """
    
    from erlang_c import required_agents
    
    intervals_per_hour = 60 // interval_minutes
    
    staffing_plan = []
    
    for hour, volume in enumerate(hourly_volumes):
        # Split hourly volume into intervals
        interval_volume = volume / intervals_per_hour
        
        for interval in range(intervals_per_hour):
            interval_name = f"{hour:02d}:{interval * interval_minutes:02d}"
            
            if interval_volume > 0:
                result = required_agents(
                    call_volume=interval_volume,
                    aht=aht_seconds,
                    interval_minutes=interval_minutes,
                    target_sl=target_sl,
                    target_answer_time=target_answer_time
                )
                
                staffing_plan.append({
                    'interval': interval_name,
                    'hour': hour,
                    'calls': round(interval_volume),
                    'required_agents': result['required_agents'],
                    'achieved_sl': result['achieved_sl'],
                    'occupancy': result['occupancy'],
                    'asa': result['asa']
                })
            else:
                staffing_plan.append({
                    'interval': interval_name,
                    'hour': hour,
                    'calls': 0,
                    'required_agents': 0,
                    'achieved_sl': 100,
                    'occupancy': 0,
                    'asa': 0
                })
    
    return pd.DataFrame(staffing_plan)