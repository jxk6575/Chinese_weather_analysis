# China Cities Weather Analysis System

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## Overview
A comprehensive Python-based weather data analysis system designed to process and visualize weather data from various cities across China. The system incorporates a data processing pipeline, analysis tools, and a web visualization interface, enabling users to gain deep insights into weather patterns and trends across different cities.

![image](https://github.com/user-attachments/assets/11c601cc-23d9-4514-803a-17d10fb8b925)
![image](https://github.com/user-attachments/assets/2b1898c3-4478-4e87-9dc0-a571860b4847)

## Key Features
### Data Processing Pipeline
- **Daily/Monthly/Yearly Data Processing**
  - Temperature trend analysis
  - Humidity pattern recognition
  - Wind direction statistics
  - Air quality index tracking

- **Provincial Data Analysis**
  - Regional weather patterns
  - Cross-city comparisons
  - Seasonal variations
  - Climate zone classification

- **City Comfort Assessment**
  - Temperature comfort index
  - Humidity comfort metrics
  - Air quality evaluation
  - Overall livability scoring

- **Statistical Analysis**
  - Time series analysis
  - Correlation studies
  - Trend predictions
  - Anomaly detection

### Data Visualization
- **Temperature Analysis**
  - Annual temperature trends
  - Daily temperature variations
  - Temperature distribution patterns
  - Extreme temperature tracking

- **Comfort Index Visualization**
  - Calendar heatmaps
  - Monthly comfort statistics
  - Seasonal comfort patterns
  - Comfort zone analysis

- **Wind Analysis**
  - Wind rose diagrams
  - Directional frequency analysis
  - Speed distribution charts
  - Seasonal wind patterns

- **Air Quality Monitoring**
  - AQI time series
  - Pollution level tracking
  - Air quality forecasting
  - Regional comparisons

### Web Interface
- **Interactive Dashboard**
  - Real-time data updates
  - Custom date range selection
  - City comparison tools
  - Export functionality

- **Responsive Design**
  - Mobile-friendly interface
  - Cross-platform compatibility
  - Adaptive layouts
  - Touch-enabled interactions

## Project Structure
```
Weather_Analysis/
├── analysis/                  # Analysis modules
│   └── city_weather_analysis.py
├── data/                      # Raw data storage
│   ├── cities_weather/        # City-specific weather data
│   │   └── [city_folders]/    # Individual city data
│   ├── city.txt              # City information
│   └── province.txt          # Province information
├── database/                 # Processed data storage
│   ├── comfort_cities.json   # Comfort indices
│   ├── daily_data.csv       # Daily statistics
│   ├── monthly_data.csv     # Monthly aggregates
│   └── statistics.json      # General statistics
├── processor/                # Data processing modules
│   ├── process_daily_data.py
│   ├── process_monthly_data.py
│   ├── process_yearly_data.py
│   ├── process_province_data.py
│   ├── process_comfort_cities.py
│   └── process_statistic_data.py
└── web/                      # Web application
    ├── dashboard/            # Dashboard interface
    ├── static/              # Static resources
    │   ├── css/            # Stylesheets
    │   └── js/             # JavaScript files
    ├── visualize/          # Visualization modules
    └── weather_web/        # Web configurations
```

## Installation Guide
### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Setup Steps
1. Clone the repository
```bash
git clone https://github.com/yourusername/Weather_Analysis.git
cd Weather_Analysis
```

2. Create and activate virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize database
```bash
python main.py
```

5. Start web server
```bash
python run_web.py
```

## Usage Guide
### Data Processing
```python
from main import WeatherDataPipeline

# Initialize and run the data pipeline
pipeline = WeatherDataPipeline()
pipeline.run_pipeline()
```

### City Weather Analysis
```python
from analysis.city_weather_analysis import WeatherAnalyzer

# Analyze specific city
analyzer = WeatherAnalyzer("北京")
analyzer.create_analysis()
```

### Web Interface
Access the dashboard at http://localhost:8000 after starting the web server.

## Technical Stack
- **Backend Framework**
  - Python 3.8+
  - Django 3.2+
  
- **Data Processing**
  - Pandas 1.3+
  - NumPy 1.20+
  
- **Data Visualization**
  - Matplotlib 3.4+
  - Seaborn 0.11+
  - ECharts 5.0+
  
- **Web Technologies**
  - HTML5
  - CSS3
  - JavaScript
  - Bootstrap 5

## Data Sources
- China Meteorological Administration
- Local Weather Stations
- Environmental Monitoring Centers
- Public Weather APIs

## Contributing
We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Coding Standards
- Follow PEP 8 guidelines
- Write comprehensive docstrings
- Maintain test coverage
- Keep code modular and clean

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact Information
- **Project Maintainer:** [Your Name]
- **Email:** [your.email@example.com]
- **Project Link:** [https://github.com/yourusername/Weather_Analysis](https://github.com/yourusername/Weather_Analysis)
- **Bug Reports:** [Issues Page](https://github.com/yourusername/Weather_Analysis/issues)

## Acknowledgments
- China Meteorological Administration for data access
- Open source community for tools and libraries
- All contributors and supporters of the project

## Version History
- v1.0.0 (2024-01) - Initial release
- v1.1.0 (2024-02) - Added web interface
- v1.2.0 (2024-03) - Enhanced visualization features 
