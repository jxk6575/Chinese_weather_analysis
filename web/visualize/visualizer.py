from django.shortcuts import render
import json
import os
import pandas as pd

class WeatherVisualizer:
    def __init__(self):
        print("\n=== Initializing WeatherVisualizer ===")
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        print(f"Base directory: {self.base_dir}")
        self.load_data()
        
    def load_data(self):
        print("\n=== Loading Statistics Data ===")
        json_path = os.path.join(self.base_dir, 'database', 'statistics.json')
        print(f"Loading statistics from: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"Loaded statistics keys: {list(self.data.keys())}")
    
    def get_top_comfort_cities(self):
        print("\n=== Getting Top Comfort Cities ===")
        yearly_data = pd.read_csv(os.path.join(self.base_dir, 'database', 'yearly_data.csv'))
        print(f"Loaded yearly data shape: {yearly_data.shape}")
        
        top_cities = yearly_data.nlargest(10, '舒适天数')[['城市', '省份', '舒适天数']]
        result = {
            'cities': top_cities['城市'].tolist(),
            'provinces': top_cities['省份'].tolist(),
            'values': top_cities['舒适天数'].tolist()
        }
        print("Top 10 cities data:")
        for city, province, value in zip(result['cities'], result['provinces'], result['values']):
            print(f"  {city}({province}): {value}天")
        return result
        
    def get_map_data(self):
        print("\n=== Getting Map Data ===")
        monthly_data = pd.read_csv(os.path.join(self.base_dir, 'database', 'monthly_data.csv'))
        print(f"Loaded monthly data shape: {monthly_data.shape}")
        
        # 读取舒适城市数据
        with open(os.path.join(self.base_dir, 'database', 'comfort_cities.json'), 'r', encoding='utf-8') as f:
            comfort_cities = json.load(f)
        
        # 定义所有省份和直辖市列表
        all_provinces = [
            '北京市', '天津市', '河北省', '山西省', '内蒙古自治区', 
            '辽宁省', '吉林省', '黑龙江省', '上海市', '江苏省', 
            '浙江省', '安徽省', '福建省', '江西省', '山东省',
            '河南省', '湖北省', '湖南省', '广东省', '广西壮族自治区', 
            '海南省', '重庆市', '四川省', '贵州省', '云南省', 
            '西藏自治区', '陕西省', '甘肃省', '青海省', '宁夏回族自治区', 
            '新疆维吾尔自治区', '台湾省', '香港特别行政区', '澳门特别行政区', '南海诸岛'
        ]
        
        # 创建月份数据字典
        monthly_map_data = {}
        
        # 处理每个月的数据
        for month in range(1, 13):
            # 特殊处理12月数据
            if month == 12:
                month_str = "2023-12"
            else:
                month_str = f"2024-{month:02d}"
            
            # 筛选当月数据
            month_data = monthly_data[monthly_data['年月'] == month_str]
            
            # 计算每个省份的平均舒适天数
            province_means = month_data.groupby('省份')['舒适天数'].mean().round(1)
            
            # 确保所有省份都有数据
            formatted_data = []
            for province in all_provinces:
                value = province_means.get(province, 0)  # 如果没有数据则为0
                formatted_data.append({
                    'name': province,
                    'value': float(value)
                })
            
            monthly_map_data[str(month)] = formatted_data
            print(f"Month {month} data processed with {len(formatted_data)} provinces")
            
            # 打印一些示例数据进行验证
            if month in [1, 6, 12]:  # 打印1月、6月和12月的部分数据作为示例
                print(f"\nSample data for month {month}:")
                for item in formatted_data[:3]:
                    print(f"  {item['name']}: {item['value']}天")
        
        return {
            'province_data': monthly_map_data,
            'comfort_cities': comfort_cities
        }
        
    def render_dashboard(self, request):
        print("\n=== Rendering Dashboard ===")
        context = {
            'chart_data': json.dumps({
                'months': self.data.get('months', []),
                'comfort_days': self.data.get('comfort_days', []),
                'provinces': self.data.get('provinces', []),
                'province_comfort_days': self.data.get('province_comfort_days', [])
            }, ensure_ascii=False),
            'statistics': json.dumps({
                'total_cities': self.data.get('total_cities', 0),
                'avg_comfort_days': self.data.get('avg_comfort_days', 0),
                'max_comfort_days': self.data.get('max_comfort_days', 0),
                'temp_comfort_rate': self.data.get('temp_comfort_rate', 0),
                'humidity_comfort_rate': self.data.get('humidity_comfort_rate', 0),
                'air_quality_rate': self.data.get('air_quality_rate', 0)
            }, ensure_ascii=False),
            'map_data': json.dumps(self.get_map_data(), ensure_ascii=False),
            'top_comfort_cities': json.dumps(self.get_top_comfort_cities(), ensure_ascii=False),
            'months': list(range(1, 13))
        }
        print("Context data prepared with keys:", list(context.keys()))
        return render(request, 'weather/dashboard.html', context) 