import os
import sys
import logging
from pathlib import Path
import time

import re
import chardet
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherDataProcessor:
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.data_dir = self.base_dir / 'data'
        self.weather_dir = self.data_dir / 'cities_weather'
        self.coord_file = self.data_dir / 'cities_coordinate.xls'
        self.database_dir = self.base_dir / 'database'
        self.city_file = self.data_dir / 'city.txt'
        self.province_file = self.data_dir / 'province.txt'

        if not self.weather_dir.exists():
            raise FileNotFoundError(f"Weather directory not found at: {self.weather_dir}")
        if not self.coord_file.exists():
            raise FileNotFoundError(f"Coordinates file not found at: {self.coord_file}")
        if not self.database_dir.exists():
            os.makedirs(self.database_dir)
        if not self.city_file.exists():
            raise FileNotFoundError(f"City file not found at: {self.city_file}")
        if not self.province_file.exists():
            raise FileNotFoundError(f"Province file not found at: {self.province_file}")
        
        logger.info(f"Initialized with data directory: {self.data_dir}")
        logger.info(f"Weather data directory: {self.weather_dir}")
        logger.info(f"Coordinates file: {self.coord_file}")
        logger.info(f"Database directory: {self.database_dir}")

    def detect_file_encoding(self, file_path):
        """Detect the encoding of a file"""
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding']

    def load_csv_with_encoding(self, file_path):
        """load CSV file"""
        encodings = ['utf-8', 'gb2312', 'gbk', 'gb18030']
        
        detected_encoding = self.detect_file_encoding(file_path)
        if detected_encoding:
            encodings.insert(0, detected_encoding)
        
        for encoding in encodings:
            try:
                return pd.read_csv(file_path, encoding=encoding)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"Error reading {file_path} with {encoding}: {e}")
                continue
        
        raise ValueError(f"Failed to read {file_path} with any encoding")

    def load_all_weather_data(self):
        """Load and combine all weather data"""
        logger.info("Loading weather data from all cities...")
        all_data = []
        id_counter = 0

        for city_dir in self.weather_dir.iterdir():
            if city_dir.is_dir():
                city_name = city_dir.name
                logger.info(f"Processing city: {city_name}")
                for csv_file in city_dir.glob('*.csv'):
                    try:
                        df = self.load_csv_with_encoding(csv_file)
                        
                        df['城市'] = city_name
                        df['id'] = range(id_counter, id_counter + len(df))
                        id_counter += len(df)
                        all_data.append(df)
                    except Exception as e:
                        logger.error(f"Error loading {csv_file}: {e}")
                        continue

        if not all_data:
            raise ValueError("No weather data files were found or loaded successfully")

        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df

    def load_coordinates(self):
        """Load city coordinates data"""
        logger.info("Loading city coordinates...")
        try:
            coords_df = pd.read_excel(self.coord_file, header=2)
            coords_df['城市（地区）'] = coords_df['城市（地区）'].str.strip()
            
            coords_df = coords_df.rename(columns={
                '城市（地区）': '城市'
            })
            
            coords_df['经度'] = pd.to_numeric(coords_df['经度'], errors='coerce')
            coords_df['纬度'] = pd.to_numeric(coords_df['纬度'], errors='coerce')
            
            coords_df = coords_df.dropna(subset=['经度', '纬度'])
            
            logger.info(f"Loaded coordinates for {len(coords_df)} cities")
            return coords_df
        except Exception as e:
            logger.error(f"Error loading coordinates file: {e}")
            raise

    def clean_temperature(self, temp_str):
        """Convert temperature string to float"""
        if pd.isna(temp_str):
            return np.nan
        return float(temp_str.replace('°', ''))

    def split_wind_info(self, wind_str):
        """Split wind information into direction and speed"""
        if pd.isna(wind_str):
            return pd.Series({'风向': np.nan, '风力': np.nan})
        
        match = re.match(r'([东南西北]+)风(\d+)级', wind_str)
        if match:
            return pd.Series({'风向': match.group(1), '风力': int(match.group(2))})
        return pd.Series({'风向': np.nan, '风力': np.nan})

    def get_comfort_level(self, temp):
        """Determine comfort level based on temperature"""
        if pd.isna(temp):
            return 'Unknown'
        if temp < 18:
            return '较冷'
        elif temp > 25:
            return '较热'
        else:
            return '舒适'

    def load_city_province_mapping(self):
        """Load and create city-province mapping"""
        logger.info("Loading city-province mapping...")
        try:
            city_df = None
            province_df = None
            
            encodings = ['utf-8', 'gb2312', 'gbk', 'gb18030']
            detected_encoding = self.detect_file_encoding(self.city_file)
            if detected_encoding:
                encodings.insert(0, detected_encoding)
                
            for encoding in encodings:
                try:
                    city_df = pd.read_csv(self.city_file, sep='\t', header=None, 
                                        names=['city_code', 'city_name', 'province_code'],
                                        encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
                
            if city_df is None:
                raise ValueError("Failed to read city.txt with any encoding")
            
            detected_encoding = self.detect_file_encoding(self.province_file)
            if detected_encoding:
                encodings.insert(0, detected_encoding)
                
            for encoding in encodings:
                try:
                    province_df = pd.read_csv(self.province_file, sep='\t', header=None,
                                            names=['province_code', 'province_name', 'extra'],
                                            encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
                
            if province_df is None:
                raise ValueError("Failed to read province.txt with any encoding")
            
            mapping_df = pd.merge(city_df, province_df[['province_code', 'province_name']], 
                                on='province_code', how='left')
            
            city_to_province = dict(zip(mapping_df['city_name'], mapping_df['province_name']))
            
            logger.info(f"Successfully loaded city-province mapping for {len(city_to_province)} cities")
            return city_to_province
            
        except Exception as e:
            logger.error(f"Error loading city-province mapping: {e}")
            raise

    def process_city_name(self, city_name):
        """Process city name to ensure consistent format"""
        if city_name.endswith('县市'):
            city_name = city_name[:-2] + '市'
        elif city_name.endswith('地区市'):
            city_name = city_name[:-3] + '市'
        return city_name

    def process_data(self):
        """Main data processing function"""
        try:
            df = self.load_all_weather_data()
            
            city_to_province = self.load_city_province_mapping()
            
            coords_df = self.load_coordinates()
            df = pd.merge(df, coords_df, on='城市', how='left')
            
            df['城市'] = df['城市'].apply(lambda x: x + '市' if not x.endswith('市') else x)
            df['城市'] = df['城市'].apply(self.process_city_name)
            df['省份'] = df['城市'].map(city_to_province)
            
            df[['日期', '星期']] = df['日期'].str.extract(r'(\d{4}-\d{2}-\d{2})\s+(.+)')
            
            df['最高温'] = df['最高温'].apply(self.clean_temperature)
            df['最低温'] = df['最低温'].apply(self.clean_temperature)
            
            wind_info = df['风力风向'].apply(self.split_wind_info)
            df = pd.concat([df, wind_info], axis=1)
            
            df['舒适度'] = df['最低温'].apply(self.get_comfort_level)
            
            missing_coords = df[df['经度'].isna()]['城市'].unique()
            if len(missing_coords) > 0:
                logger.warning(f"Cities missing coordinates: {missing_coords.tolist()}")
            
            output_df = df[[ 
                'id', '城市', '省份', '日期', '星期', '最高温', '最低温', 
                '天气', '风力', '风向', '空气质量指数',
                '经度', '纬度', '舒适度'
            ]]

            output_file_path = self.database_dir / 'daily_data.csv'
            
            try:
                os.makedirs(self.database_dir, exist_ok=True)
                os.chmod(self.database_dir, 0o777)
                
                if output_file_path.exists():
                    output_file_path.unlink()
                
                output_df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
                
            except PermissionError as pe:
                alt_output_path = self.base_dir / f'daily_temperature_data_{int(time.time())}.csv'
                logger.warning(f"Permission denied at {output_file_path}, trying alternative path: {alt_output_path}")
                output_df.to_csv(alt_output_path, index=False, encoding='utf-8-sig')
                output_file_path = alt_output_path

            logger.info(f"Data processing completed successfully. Output saved to: {output_file_path}")
            return output_df

        except Exception as e:
            logger.error(f"Error during processing: {e}")
            raise

if __name__ == "__main__":
    try:
        processor = WeatherDataProcessor()
        output_df = processor.process_data()
        logger.info("Processing completed successfully")
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        sys.exit(1) 