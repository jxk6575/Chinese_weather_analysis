import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonthlyDataProcessor:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.database_dir = self.base_dir / 'database'
        self.daily_data_path = self.database_dir / 'daily_data.csv'
        self.monthly_data_path = self.database_dir / 'monthly_data.csv'

        if not self.daily_data_path.exists():
            raise FileNotFoundError(f"Daily data file not found at: {self.daily_data_path}")

    def load_daily_data(self):
        """Load the daily data CSV file"""
        try:
            return pd.read_csv(self.daily_data_path)
        except Exception as e:
            logger.error(f"Error loading daily data: {e}")
            raise

    def process_date(self, df):
        """Process date column to extract year and month"""
        df['年月'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m')
        return df.drop(['日期', '星期'], axis=1)

    def calculate_wind_direction_stats(self, group):
        """Calculate wind statistics for each direction"""
        wind_directions = ['东', '南', '西', '北', '东北', '东南', '西南', '西北']
        wind_stats = {}
        total_days = len(group)
        
        for direction in wind_directions:
            mask = group['风向'].str.contains(direction, na=False)
            direction_days = mask.sum()
            avg_speed = group.loc[mask, '风力'].mean()
            
            wind_stats[f'{direction}风频率'] = round(direction_days / total_days * 100, 2)
            wind_stats[f'{direction}风均速'] = round(float(avg_speed if not pd.isna(avg_speed) else 0), 2)
            
        return pd.Series(wind_stats)

    def count_comfort_days(self, comfort_series):
        """Count number of comfortable days"""
        return (comfort_series == '舒适').sum()

    def process_monthly_data(self):
        """Main processing function for monthly data"""
        try:
            df = self.load_daily_data()
            df = self.process_date(df)
            
            grouped = df.groupby(['城市', '省份', '年月'])
            
            monthly_data = []
            
            for (city, province, month), group in grouped:
                temp_stats = {
                    '月最高温': round(group['最高温'].max(), 2),
                    '月最低温': round(group['最低温'].min(), 2),
                    '月平均温': round((group['最高温'].mean() + group['最低温'].mean()) / 2, 2)
                }
                
                wind_stats = self.calculate_wind_direction_stats(group)
                
                avg_aqi = pd.to_numeric(
                    group['空气质量指数'].str.extract(r'(\d+)', expand=False), 
                    errors='coerce'
                ).mean()
                
                comfort_days = self.count_comfort_days(group['舒适度'])
                
                monthly_record = {
                    '城市': city,
                    '省份': province,
                    '年月': month,
                    '经度': round(float(group['经度'].iloc[0]), 2),
                    '纬度': round(float(group['纬度'].iloc[0]), 2),
                    '舒适天数': comfort_days,
                    '空气质量指数': round(float(avg_aqi), 2) if not pd.isna(avg_aqi) else None,
                    **temp_stats,
                    **wind_stats
                }
                
                monthly_data.append(monthly_record)
            
            monthly_df = pd.DataFrame(monthly_data)
            
            monthly_df.insert(0, 'id', range(len(monthly_df)))
            
            numeric_columns = monthly_df.select_dtypes(include=[np.number]).columns
            monthly_df[numeric_columns] = monthly_df[numeric_columns].round(2)
            
            monthly_df.to_csv(self.monthly_data_path, index=False, encoding='utf-8-sig', float_format='%.2f')
            
            logger.info(f"Monthly data processing completed. Output saved to: {self.monthly_data_path}")
            return monthly_df
            
        except Exception as e:
            logger.error(f"Error processing monthly data: {e}")
            raise

if __name__ == "__main__":
    try:
        processor = MonthlyDataProcessor()
        monthly_df = processor.process_monthly_data()
        logger.info("Processing completed successfully")
    except Exception as e:
        logger.error(f"Error during processing: {e}")
