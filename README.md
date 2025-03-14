# Solar Energy Financial Modeling Tool

![Solar System](https://img.shields.io/badge/Solar%20System-Modeling-yellow)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![South Africa](https://img.shields.io/badge/South%20Africa-Energy-green)

A Streamlit application for designing and analyzing the financial implications of installing a home solar PV and battery system in South Africa.

## 📊 Overview

This tool helps homeowners in South Africa make informed decisions about solar energy investments by providing:

- System sizing recommendations based on daily electricity consumption
- Component cost breakdown
- Financial payback analysis with adjustable parameters
- Comparison between solar investment and alternative investments

The application is specifically tailored for the South African market, taking into account local electricity rates, solar conditions, and typical system costs.

## 🌞 Features

### System Specifications
- Calculate optimal solar array size based on daily electricity usage
- Determine appropriate battery storage capacity for desired backup duration
- Recommend inverter sizing based on peak load requirements
- Generate cost estimates for all system components

### Financial Analysis
- Calculate simple payback period based on electricity savings
- Compare solar investment against alternative investment opportunities
- Factor in electricity price inflation over time
- Optional analysis for grid sell-back scenarios
- Visual representation of long-term financial implications

### Information & Assumptions
- Transparent documentation of all system sizing logic
- Clear explanation of financial assumptions
- Details on component costs and specifications
- Notes on excluded costs and considerations

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- pip

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/solar-energy-financial-modeling.git
cd solar-energy-financial-modeling
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

## 📝 Usage

1. **Input your daily electricity consumption** in the sidebar
2. **Select your desired backup duration** (in hours)
3. **Adjust average peak sun hours** based on your location in South Africa
4. Review the recommended system specifications and cost breakdown
5. Navigate to the "Financial Analysis" tab to see payback calculations
6. Modify financial assumptions as needed for your specific situation

## 🔧 Customization

You can adjust several parameters to match your specific circumstances:

- **Electricity cost per kWh**: Current Eskom or municipal rates
- **Electricity price inflation**: Annual percentage increase expectations
- **Opportunity cost of capital**: Your expected return on alternative investments
- **Grid sell-back options**: For municipalities that allow feeding back to the grid

## 💡 Background

This project was inspired by exploring the capabilities of advanced AI systems to solve practical engineering and financial problems. It began as an investigation into solar system specifications for a typical South African home, considering the unique challenges of load-shedding and rising electricity costs in the country.

The full background and development process is documented in the accompanying article ["Analysis for a Solar PV & Battery System (South Africa)"](https://interludeone.com/posts/2024-06-05-solar-payback-time/solar-payback-time-report).

## 📚 Technical Details

### Technologies Used
- **Streamlit**: For the interactive web application
- **Pandas**: For data manipulation and analysis
- **NumPy**: For numerical calculations
- **Plotly**: For interactive data visualization

### System Sizing Logic
- Battery capacity calculation: `(daily_usage * backup_days) / battery_dod`
- Solar array sizing: `daily_usage / avg_sun_hours`
- Inverter sizing: `daily_usage * 1.25 / 5`

### Financial Model
The financial model calculates two types of payback periods:
1. **Simple Payback**: Time until cumulative electricity savings cover the initial cost
2. **Investment-Adjusted Payback**: Time until savings exceed what the same money would earn in an alternative investment

## 🤝 Contributing

Contributions to improve the tool are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Eskom for providing reference electricity rates
- South African solar industry for component pricing benchmarks
- [Streamlit](https://streamlit.io/) for their excellent data app framework
