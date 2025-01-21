import pandas as pd
import json
from datetime import datetime
import os
from pathlib import Path

class StatisticsProcessor:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.database_dir = self.base_dir / 'database'
        
        self.monthly_data = pd.read_csv(self.database_dir / 'monthly_data.csv')
        self.yearly_data = pd.read_csv(self.database_dir / 'yearly_data.csv')
        self.province_data = pd.read_csv(self.database_dir / 'province_data.csv')
    
    def process_monthly_top_cities(self):
        """Process monthly top cities rankings"""
        monthly_top_cities = {}
        for month in self.monthly_data['年月'].unique():
            month_data = self.monthly_data[self.monthly_data['年月'] == month]
            top_5 = month_data.nlargest(5, '舒适天数')[['城市', '省份', '舒适天数']]
            monthly_top_cities[month] = [
                {'city': row['城市'], 
                 'province': row['省份'], 
                 'comfort_days': int(row['舒适天数'])} 
                for _, row in top_5.iterrows()
            ]
        return monthly_top_cities
    
    def process_yearly_top_cities(self):
        """Process yearly top cities rankings"""
        yearly_top_10 = self.yearly_data.nlargest(10, '舒适天数')
        return [
            {'city': row['城市'], 
             'province': row['省份'], 
             'comfort_days': int(row['舒适天数'])} 
            for _, row in yearly_top_10.iterrows()
        ]
    
    def process_monthly_province_rankings(self):
        """Process monthly province rankings"""
        monthly_province_rankings = {}
        for month in self.province_data['年月'].unique():
            month_data = self.province_data[self.province_data['年月'] == month]
            top_3 = month_data.nlargest(3, '平均舒适天数')
            monthly_province_rankings[month] = [
                {'province': row['省份'], 
                 'avg_comfort_days': float(row['平均舒适天数'])} 
                for _, row in top_3.iterrows()
            ]
        return monthly_province_rankings
    
    def process_chart_data(self):
        """Process data for charts"""
        months = sorted(self.monthly_data['年月'].unique())
        monthly_comfort = []
        for month in months:
            month_data = self.monthly_data[self.monthly_data['年月'] == month]
            avg_comfort = month_data['舒适天数'].mean()
            monthly_comfort.append(round(avg_comfort, 1))
        
        provinces = self.province_data['省份'].unique()
        province_comfort = []
        for province in provinces:
            province_data = self.province_data[self.province_data['省份'] == province]
            avg_comfort = province_data['平均舒适天数'].mean()
            province_comfort.append(round(avg_comfort, 1))
            
        return {
            'months': [datetime.strptime(m, '%Y-%m').strftime('%Y年%m月') for m in months],
            'comfort_days': monthly_comfort,
            'provinces': list(provinces),
            'province_comfort_days': province_comfort
        }
    
    def calculate_monthly_stats(self):
        """Calculate and save monthly statistics"""
        monthly_top_cities = self.process_monthly_top_cities()
        monthly_province_rankings = self.process_monthly_province_rankings()

        print("Monthly Top 5 Cities:")
        for month, cities in monthly_top_cities.items():
            print(f"{month}:")
            for city in cities:
                print(f"  {city['city']} ({city['province']}): {city['comfort_days']} days")

        print("\nMonthly Top 3 Provinces:")
        for month, provinces in monthly_province_rankings.items():
            print(f"{month}:")
            for province in provinces:
                print(f"  {province['province']}: {province['avg_comfort_days']} days")

        data = {
            'monthly_top_cities': monthly_top_cities,
            'yearly_top_cities': self.process_yearly_top_cities(),
            'monthly_province_rankings': monthly_province_rankings,
            **self.process_chart_data(),
            'total_cities': len(self.yearly_data['城市'].unique()),
            'avg_comfort_days': round(self.yearly_data['舒适天数'].mean(), 1),
            'max_comfort_days': int(self.yearly_data['舒适天数'].max()),
            'temp_comfort_rate': 75,
            'humidity_comfort_rate': 70,
            'air_quality_rate': 85
        }
        
        output_path = self.database_dir / 'statistics.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return data

if __name__ == '__main__':
    processor = StatisticsProcessor()
    processor.calculate_monthly_stats()
