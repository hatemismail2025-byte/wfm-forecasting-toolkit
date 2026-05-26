"""
Erlang C Calculation Module
Industry-standard workforce management formulas
"""

import math
from scipy.special import factorial

def erlang_c(agents, traffic_intensity):
    """
    Calculate Erlang C probability (probability of queueing)
    
    Args:
        agents: Number of available agents
        traffic_intensity: Traffic in Erlangs (arrival_rate * AHT)
    
    Returns:
        float: Probability that a call will wait in queue
    """
    
    # Handle edge cases
    if agents <= 0 or traffic_intensity <= 0:
        return 0
    
    if traffic_intensity >= agents:
        return 1.0  # System is overloaded
    
    # Erlang C formula
    numerator = (math.pow(traffic_intensity, agents) / factorial(agents)) * \
                (agents / (agents - traffic_intensity))
    
    denominator_sum = 0
    for k in range(agents):
        denominator_sum += math.pow(traffic_intensity, k) / factorial(k)
    
    denominator_sum += (math.pow(traffic_intensity, agents) / factorial(agents)) * \
                       (agents / (agents - traffic_intensity))
    
    erlang_c_value = numerator / denominator_sum
    
    return min(erlang_c_value, 1.0)


def service_level(agents, traffic_intensity, target_answer_time, aht):
    """
    Calculate service level (% of calls answered within target time)
    
    Args:
        agents: Number of agents
        traffic_intensity: Traffic in Erlangs
        target_answer_time: Target answer time in seconds (e.g., 20 for 80/20)
        aht: Average Handle Time in seconds
    
    Returns:
        float: Service level percentage (0-100)
    """
    
    pw = erlang_c(agents, traffic_intensity)
    
    if pw == 0:
        return 100.0
    
    # Service level formula
    exponential_term = math.exp(-(agents - traffic_intensity) * (target_answer_time / aht))
    sl = 1 - (pw * exponential_term)
    
    return max(0, min(100, sl * 100))


def average_speed_of_answer(agents, traffic_intensity, aht):
    """
    Calculate Average Speed of Answer (ASA)
    
    Args:
        agents: Number of agents
        traffic_intensity: Traffic in Erlangs
        aht: Average Handle Time in seconds
    
    Returns:
        float: ASA in seconds
    """
    
    pw = erlang_c(agents, traffic_intensity)
    
    if agents <= traffic_intensity:
        return float('inf')
    
    asa = (pw * aht) / (agents - traffic_intensity)
    
    return asa


def occupancy(traffic_intensity, agents):
    """
    Calculate agent occupancy percentage
    
    Args:
        traffic_intensity: Traffic in Erlangs
        agents: Number of agents
    
    Returns:
        float: Occupancy percentage (0-100)
    """
    
    if agents == 0:
        return 0
    
    occ = (traffic_intensity / agents) * 100
    
    return min(occ, 100)


def required_agents(call_volume, aht, interval_minutes, target_sl, target_answer_time, max_occupancy=85):
    """
    Calculate required number of agents to meet service level target
    
    Args:
        call_volume: Number of calls in the interval
        aht: Average Handle Time in seconds
        interval_minutes: Length of interval (typically 30)
        target_sl: Target service level % (e.g., 80 for 80/20)
        target_answer_time: Target answer time in seconds (e.g., 20)
        max_occupancy: Maximum acceptable occupancy % (default 85)
    
    Returns:
        dict with: required_agents, achieved_sl, occupancy, asa
    """
    
    # Calculate traffic intensity in Erlangs
    interval_seconds = interval_minutes * 60
    traffic_intensity = (call_volume * aht) / interval_seconds
    
    # Start with minimum agents (at least traffic intensity rounded up)
    agents = math.ceil(traffic_intensity)
    
    # Increment until we meet both SL and occupancy targets
    max_iterations = 1000
    for i in range(max_iterations):
        current_sl = service_level(agents, traffic_intensity, target_answer_time, aht)
        current_occ = occupancy(traffic_intensity, agents)
        
        if current_sl >= target_sl and current_occ <= max_occupancy:
            asa = average_speed_of_answer(agents, traffic_intensity, aht)
            
            return {
                'required_agents': agents,
                'achieved_sl': round(current_sl, 2),
                'occupancy': round(current_occ, 2),
                'asa': round(asa, 2),
                'traffic_intensity': round(traffic_intensity, 2)
            }
        
        agents += 1
    
    # If we can't meet targets, return best effort
    asa = average_speed_of_answer(agents, traffic_intensity, aht)
    return {
        'required_agents': agents,
        'achieved_sl': round(service_level(agents, traffic_intensity, target_answer_time, aht), 2),
        'occupancy': round(occupancy(traffic_intensity, agents), 2),
        'asa': round(asa, 2),
        'traffic_intensity': round(traffic_intensity, 2),
        'warning': 'Could not meet targets within reasonable agent count'
    }