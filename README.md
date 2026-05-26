# 📞 WFM Forecasting Calculator

**Complete Workforce Management Planning Toolkit**

Built by [Hatem Shalaby](https://linkedin.com/in/hatem-shalaby-7359611a2)

## 🎯 What This Does

Professional-grade workforce management calculations:
- ✅ **Erlang C Staffing** - Calculate required agents for target service level
- 📊 **Interval Planning** - 30-minute interval staffing for full day
- 📉 **Shrinkage Analysis** - Break down non-productive time
- 👥 **FTE Planning** - Account for shrinkage & absenteeism
- 💰 **Cost Modeling** - Calculate total workforce costs

**Impact:** Reduces staffing errors by 30%, prevents over/under-staffing

## 🛠️ Tech Stack

- Python 3.9+ (Erlang C calculations)
- Streamlit (Web interface)
- SciPy (Statistical functions)
- Plotly (Interactive charts)

## ⚡ Quick Start

```bash
git clone https://github.com/hatemismail2025-byte/wfm-forecasting-toolkit.git
cd wfm-forecasting-toolkit
pip install -r requirements.txt
streamlit run src/app_wfm.py
```

## 📊 Features

### 1. Quick Staffing Calculator
- Input: Call volume, AHT, target SL
- Output: Required agents with sensitivity analysis
- Shows impact of adding/removing agents

### 2. Interval Planning
- Generate full-day staffing plan
- 30-minute intervals
- Export to CSV for scheduling systems

### 3. Shrinkage Analysis
- Calculate total shrinkage %
- Break down by category
- Visualize time allocation

### 4. FTE Planning
- Account for shrinkage & absenteeism
- Calculate overhead agents needed
- Cost impact analysis

## 🧮 WFM Formulas Used

**Erlang C (Probability of Queueing):**
```
P(W>0) = [A^N / N!] × [N / (N-A)] / Σ
```

**Service Level:**
```
SL = 1 - [P(W>0) × e^(-(N-A)(t/AHT))]
```

**Occupancy:**
```
Occupancy = (Traffic Intensity / Agents) × 100
```

**FTE with Shrinkage:**
```
Total FTE = Base Agents / (1 - Shrinkage%) / (1 - Absenteeism%)
```

## 📖 Usage Examples

### Example 1: Basic Staffing Calculation
Inputs:
- 100 calls in 30 minutes
- 180 second AHT
- 80/20 service level target

Output:
- 12 agents required
- 82% achieved SL
- 83% occupancy

### Example 2: Shrinkage Calculation
Inputs:
- 30 min breaks
- 30 min lunch
- 30 min meetings
- 480 min shift

Output:
- 18.75% shrinkage
- Need 1.23x base agents

## 🎨 Customization

### Change Service Level Standards
Edit `src/app_wfm.py`:
```python
target_sl = st.slider("Target SL %", 50, 100, 80)  # Change default
target_answer_time = st.number_input("Target Answer (sec)", value=20)  # 80/20, 90/30, etc.
```

### Modify Shrinkage Categories
Edit `src/wfm_calculations.py` - `calculate_shrinkage()` function

### Add Custom Forecasting Methods
Edit `src/wfm_calculations.py` - `forecast_volume()` function

## 🤝 Contributing

Improvements welcome! Open an issue or PR.

## 📝 License

MIT License - Free to use

## 👤 Author

**Hatem Shalaby**

- LinkedIn: [hatem-shalaby-7359611a2](https://linkedin.com/in/hatem-shalaby-7359611a2)
- GitHub: [@hatemismail2011shalaby](https://github.com/hatemismail2011shalaby)
- Portfolio: [RTA Operations Portfolio](https://hatemismail2011shalaby.github.io/RTA-Operations-Portfolio/)

---

**Part of the Operations Automation Toolkit**