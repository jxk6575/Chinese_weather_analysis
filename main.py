import logging
from pathlib import Path
from processor.process_daily_data import WeatherDataProcessor
from processor.process_monthly_data import MonthlyDataProcessor
from processor.process_yearly_data import YearlyDataProcessor
from processor.process_province_data import ProvinceDataProcessor
from processor.process_statistic_data import StatisticsProcessor
from processor.process_comfort_cities import ComfortCitiesProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeatherDataPipeline:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.database_dir = self.base_dir / 'database'
        
        self.database_dir.mkdir(exist_ok=True)
        
        self.daily_processor = WeatherDataProcessor()
        self.monthly_processor = MonthlyDataProcessor()
        self.yearly_processor = YearlyDataProcessor()
        self.province_processor = ProvinceDataProcessor()
        self.statistics_processor = StatisticsProcessor()
        self.comfort_processor = ComfortCitiesProcessor()

    def run_pipeline(self):
        """运行完整的数据处理流水线"""
        try:
            logger.info("Starting data processing pipeline...")

            # 1. 处理每日数据
            logger.info("Processing daily data...")
            daily_df = self.daily_processor.process_data()

            # 2. 处理月度数据
            logger.info("Processing monthly data...")
            monthly_df = self.monthly_processor.process_monthly_data()

            # 3. 处理年度数据
            logger.info("Processing yearly data...")
            yearly_df = self.yearly_processor.process_yearly_data()

            # 4. 处理省份数据
            logger.info("Processing province data...")
            province_df = self.province_processor.process_province_data()

            # 5. 处理统计数据
            logger.info("Processing statistics data...")
            self.statistics_processor.calculate_monthly_stats()

            # 6. 处理舒适城市数据
            logger.info("Processing comfort cities data...")
            comfort_cities = self.comfort_processor.process_comfort_cities()

            logger.info("Data processing pipeline completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error in data processing pipeline: {e}")
            raise

if __name__ == "__main__":
    try:
        pipeline = WeatherDataPipeline()
        pipeline.run_pipeline()
        logger.info("Pipeline execution completed successfully")
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        exit(1)
