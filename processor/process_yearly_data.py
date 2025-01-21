import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YearlyDataProcessor:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.database_dir = self.base_dir / 'database'
        self.monthly_data_path = self.database_dir / 'monthly_data.csv'
        self.yearly_data_path = self.database_dir / 'yearly_data.csv'

        if not self.monthly_data_path.exists():
            raise FileNotFoundError(f"Monthly data file not found at: {self.monthly_data_path}")

    def load_monthly_data(self):
        """Load the monthly data CSV file"""
        try:
            return pd.read_csv(self.monthly_data_path)
        except Exception as e:
            logger.error(f"Error loading monthly data: {e}")
            raise

    def process_date(self, df):
        """Extract year from year-month column"""
        df['年份'] = pd.to_datetime(df['年月']).dt.year
        return df.drop('年月', axis=1)

    def calculate_yearly_wind_stats(self, group):
        """Calculate yearly wind statistics by averaging monthly stats"""
        wind_directions = ['东', '南', '西', '北', '东北', '东南', '西南', '西北']
        yearly_wind_stats = {}
        
        for direction in wind_directions:
            freq_col = f'{direction}风频率'
            speed_col = f'{direction}风均速'
            
            total_freq = group[freq_col].sum()
            if total_freq > 0:
                weighted_speed = (group[speed_col] * group[freq_col]).sum() / total_freq
            else:
                weighted_speed = 0
                
            yearly_wind_stats[freq_col] = round(group[freq_col].mean(), 2)
            yearly_wind_stats[speed_col] = round(float(weighted_speed), 2)
            
        return pd.Series(yearly_wind_stats)

    def process_yearly_data(self):
        """Main processing function for yearly data"""
        try:
            df = self.load_monthly_data()
            
            grouped = df.groupby(['城市', '省份'])
            
            yearly_data = []
            
            for (city, province), group in grouped:
                temp_stats = {
                    '年最高温': round(group['月最高温'].max(), 2),
                    '年最低温': round(group['月最低温'].min(), 2),
                    '年平均温': round(group['月平均温'].mean(), 2)
                }
                
                wind_stats = self.calculate_yearly_wind_stats(group)
                
                total_comfort_days = group['舒适天数'].sum()
                avg_aqi = group['空气质量指数'].mean()
                
                yearly_record = {
                    '城市': city,
                    '省份': province,
                    '年份': 2024,
                    '经度': group['经度'].iloc[0],
                    '纬度': group['纬度'].iloc[0],
                    '舒适天数': total_comfort_days,
                    '空气质量指数': round(float(avg_aqi), 2) if not pd.isna(avg_aqi) else None,
                    **temp_stats,
                    **wind_stats
                }
                
                yearly_data.append(yearly_record)
            
            yearly_df = pd.DataFrame(yearly_data)
            
            yearly_df.insert(0, 'id', range(len(yearly_df)))
            
            numeric_columns = yearly_df.select_dtypes(include=[np.number]).columns
            yearly_df[numeric_columns] = yearly_df[numeric_columns].round(2)
            
            yearly_df.to_csv(self.yearly_data_path, index=False, encoding='utf-8-sig', float_format='%.2f')
            
            logger.info(f"Yearly data processing completed. Output saved to: {self.yearly_data_path}")
            return yearly_df
            
        except Exception as e:
            logger.error(f"Error processing yearly data: {e}")
            raise

if __name__ == "__main__":
    try:
        processor = YearlyDataProcessor()
        yearly_df = processor.process_yearly_data()
        logger.info("Processing completed successfully")
    except Exception as e:
        logger.error(f"Error during processing: {e}")
