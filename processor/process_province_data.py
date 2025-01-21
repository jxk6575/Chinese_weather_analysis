import os
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProvinceDataProcessor:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.database_dir = self.base_dir / 'database'
        self.monthly_data_path = self.database_dir / 'monthly_data.csv'
        self.province_data_path = self.database_dir / 'province_data.csv'

    def process_province_data(self):
        try:
            monthly_df = pd.read_csv(self.monthly_data_path)
            
            province_df = monthly_df.groupby(['省份', '年月']).agg({
                '城市': 'nunique',
                '舒适天数': 'mean'
            }).reset_index()

            province_df.rename(columns={'城市': '城市数量', '舒适天数': '平均舒适天数'}, inplace=True)
            province_df.insert(0, 'id', range(len(province_df)))

            province_df.to_csv(self.province_data_path, index=False, encoding='utf-8-sig')
            logger.info(f"Province data processing completed. Output saved to: {self.province_data_path}")
            return province_df

        except Exception as e:
            logger.error(f"Failed to process province data: {e}")
            return None

if __name__ == "__main__":
    processor = ProvinceDataProcessor()
    processor.process_province_data()
