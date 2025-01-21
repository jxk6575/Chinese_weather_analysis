import os
import pandas as pd
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComfortCitiesProcessor:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.database_dir = self.base_dir / 'database'
        self.monthly_data_path = self.database_dir / 'monthly_data.csv'
        self.output_path = self.database_dir / 'comfort_cities.json'

    def process_comfort_cities(self):
        try:
            monthly_data = pd.read_csv(self.monthly_data_path)
            logger.info(f"Loaded monthly data with shape: {monthly_data.shape}")

            comfort_cities = {}
            
            for month in range(1, 13):
                if month == 12:
                    month_str = "2023-12"
                else:
                    month_str = f"2024-{month:02d}"
                
                month_data = monthly_data[monthly_data['年月'] == month_str]
                
                comfort_cities_data = month_data[month_data['舒适天数'] > 1].apply(
                    lambda row: {
                        'name': row['城市'],
                        'value': [float(row['经度']), float(row['纬度'])],
                        'comfort_days': float(row['舒适天数'])
                    }, axis=1
                ).tolist()
                
                comfort_cities[str(month)] = comfort_cities_data
                logger.info(f"Month {month}: Found {len(comfort_cities_data)} comfortable cities")

            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(comfort_cities, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Comfort cities data saved to {self.output_path}")
            
            return comfort_cities

        except Exception as e:
            logger.error(f"Error processing comfort cities: {e}")
            return None

if __name__ == "__main__":
    processor = ComfortCitiesProcessor()
    processor.process_comfort_cities() 