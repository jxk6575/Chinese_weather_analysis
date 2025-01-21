import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

class WeatherAnalyzer:
    def __init__(self, city_name):
        self.base_dir = Path(__file__).parent.parent
        self.data_path = self.base_dir / 'database' / 'daily_data.csv'
        self.city_name = city_name
        
        self.colors = {
            'primary': '#1890ff',
            'secondary': '#40a9ff',
            'success': '#52c41a',
            'warning': '#faad14',
            'danger': '#f5222d',
            'background': '#001529',
            'text': '#ffffff'
        }
        
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.style.use('dark_background')
        
    def load_data(self):
        """加载并预处理数据"""
        try:
            df = pd.read_csv(self.data_path)
            self.weather_data = df[df['城市'] == self.city_name].copy()
            if self.weather_data.empty:
                raise ValueError(f"未找到{self.city_name}的天气数据")
            
            self.weather_data['日期'] = pd.to_datetime(self.weather_data['日期'])
            self.weather_data['平均温度'] = (self.weather_data['最高温'] + self.weather_data['最低温']) / 2
            self.weather_data['空气质量指数'] = self.weather_data['空气质量指数'].str.extract('(\d+)').astype(float)
            
            comfort_map = {
                '较冷': 2,
                '舒适': 5,
                '较热': 3
            }
            self.weather_data['舒适度'] = self.weather_data['舒适度'].map(comfort_map)
            
            print(f"成功加载{self.city_name}的天气数据，共{len(self.weather_data)}条记录")
        except Exception as e:
            print(f"数据加载失败: {e}")
            raise
        
    def create_analysis(self):
        """生成所有分析图表"""
        self.load_data()
        
        fig = plt.figure(figsize=(20, 20))
        fig.suptitle(f'{self.city_name}天气数据综合分析', fontsize=16, color=self.colors['text'])
        
        # 1. 温度变化趋势
        ax1 = plt.subplot(321)
        self.plot_temperature_trends(ax1)
        
        # 2. 舒适度日历图
        ax2 = plt.subplot(322)
        self.plot_comfort_calendar(ax2)
        
        # 3. 风向玫瑰图
        ax3 = plt.subplot(323, projection='polar')
        self.plot_wind_rose(ax3)
        
        # 4. 月度舒适天数统计
        ax4 = plt.subplot(324)
        self.plot_monthly_stats(ax4)
        
        # 5. 温度分布
        ax5 = plt.subplot(325)
        self.plot_temperature_distribution(ax5)
        
        # 6. 空气质量时间序列
        ax6 = plt.subplot(326)
        self.plot_aqi_timeline(ax6)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        output_path = self.base_dir / 'analysis' / f'{self.city_name}_weather_analysis.png'
        plt.savefig(output_path, bbox_inches='tight', facecolor=self.colors['background'])
        print(f"分析图表已保存至: {output_path}")
        plt.close()
        
    def plot_temperature_trends(self, ax):
        """温度变化趋势"""
        ax.plot(self.weather_data['日期'], self.weather_data['最高温'], 
                color=self.colors['danger'], label='最高温')
        ax.plot(self.weather_data['日期'], self.weather_data['最低温'], 
                color=self.colors['primary'], label='最低温')
        ax.fill_between(self.weather_data['日期'], 
                       self.weather_data['最高温'], 
                       self.weather_data['最低温'], 
                       alpha=0.2, color=self.colors['secondary'])
        
        comfort_days = self.weather_data[self.weather_data['舒适度'] == 5]
        if not comfort_days.empty:
            ax.fill_between(comfort_days['日期'],
                           comfort_days['最高温'],
                           comfort_days['最低温'],
                           color=self.colors['success'],
                           alpha=0.3,
                           label='舒适区间')
            
            ax.scatter(comfort_days['日期'], 
                      [ax.get_ylim()[0]] * len(comfort_days),
                      color=self.colors['success'],
                      marker='|',
                      s=100,
                      zorder=3)
        
        ax.set_title('全年温度变化趋势', color=self.colors['text'])
        ax.set_xlabel('日期', color=self.colors['text'])
        ax.set_ylabel('温度 (°C)', color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])
        
        ax.legend(facecolor=self.colors['background'], 
                 labelcolor=self.colors['text'],
                 loc='upper right')
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['text'])
        
    def plot_comfort_calendar(self, ax):
        """舒适度日历热力图"""
        calendar_data = self.weather_data.set_index('日期')['舒适度'].to_frame()
        
        comfort_pivot = calendar_data.pivot_table(
            index=calendar_data.index.month,
            columns=calendar_data.index.day,
            values='舒适度'
        )
        
        colors = {
            2: self.colors['primary'],   # 较冷 - 蓝色
            5: self.colors['success'],   # 舒适 - 绿色
            3: self.colors['warning']    # 较热 - 橙色
        }
        
        cmap = plt.matplotlib.colors.ListedColormap([colors[2], colors[3], colors[5]])
        
        heatmap = sns.heatmap(comfort_pivot, 
                             ax=ax,
                             cmap=cmap,
                             cbar_kws={'label': '舒适度'})
        
        colorbar = heatmap.collections[0].colorbar
        colorbar.set_ticks([0.33, 1, 1.67])
        colorbar.set_ticklabels(['较冷', '较热', '舒适'])
        
        ax.set_title('全年舒适度日历', color=self.colors['text'])
        ax.set_xlabel('日', color=self.colors['text'])
        ax.set_ylabel('月', color=self.colors['text'])
        
        ax.tick_params(colors=self.colors['text'])
        colorbar.ax.tick_params(colors=self.colors['text'])
        colorbar.ax.yaxis.label.set_color(self.colors['text'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['text'])
        
    def plot_wind_rose(self, ax):
        """风向玫瑰图"""
        wind_counts = self.weather_data['风向'].value_counts()
        angles = np.linspace(0, 2*np.pi, len(wind_counts), endpoint=False)
        
        ax.bar(angles, wind_counts.values, width=0.35,
               color=self.colors['primary'], alpha=0.5)
        ax.set_xticks(angles)
        ax.set_xticklabels(wind_counts.index, color=self.colors['text'])
        ax.set_title('风向频率分布', color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])
        for spine in ax.spines.values():
            spine.set_color(self.colors['text'])
        
    def plot_monthly_stats(self, ax):
        """月度舒适天数统计"""
        comfort_mask = (self.weather_data['舒适度'] == 5)
        
        monthly_comfort = self.weather_data[comfort_mask].groupby(
            self.weather_data[comfort_mask]['日期'].dt.strftime('%Y-%m')
        ).size()
        
        ax.bar(range(len(monthly_comfort)), monthly_comfort.values, 
               color=self.colors['primary'], width=0.4)
        
        ax.set_xticks(range(len(monthly_comfort)))
        ax.set_xticklabels(monthly_comfort.index, rotation=45, color=self.colors['text'])
        
        for i, v in enumerate(monthly_comfort.values):
            ax.text(i, v + 0.5, str(v), 
                    ha='center', va='bottom', 
                    color=self.colors['text'])
        
        ax.set_title('月度舒适天数统计', color=self.colors['text'])
        ax.set_xlabel('月份', color=self.colors['text'])
        ax.set_ylabel('舒适天数', color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['text'])
        
    def plot_temperature_distribution(self, ax):
        """温度分布"""
        sns.kdeplot(data=self.weather_data, x='最高温', ax=ax, 
                   color=self.colors['danger'], label='最高温',
                   fill=True, alpha=0.3)
        sns.kdeplot(data=self.weather_data, x='最低温', ax=ax, 
                   color=self.colors['primary'], label='最低温',
                   fill=True, alpha=0.3)
        
        ax.axvline(self.weather_data['最高温'].mean(), 
                   color=self.colors['danger'], linestyle='--', alpha=0.8,
                   label=f'平均最高温: {self.weather_data["最高温"].mean():.1f}°C')
        ax.axvline(self.weather_data['最低温'].mean(), 
                   color=self.colors['primary'], linestyle='--', alpha=0.8,
                   label=f'平均最低温: {self.weather_data["最低温"].mean():.1f}°C')
        
        ax.set_title('温度分布密度', color=self.colors['text'])
        ax.set_xlabel('温度 (°C)', color=self.colors['text'])
        ax.set_ylabel('密度', color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])
        
        ax.legend(facecolor=self.colors['background'], 
                 labelcolor=self.colors['text'],
                 loc='upper right')
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['text'])
        
    def plot_aqi_timeline(self, ax):
        """空气质量时间序列"""
        ax.plot(self.weather_data['日期'], self.weather_data['空气质量指数'], 
                color=self.colors['warning'])
        ax.set_title('空气质量指数变化')

if __name__ == "__main__":
    city_name = input("请输入城市名称（例如：北京市、上海市、广州市）：")
    try:
        analyzer = WeatherAnalyzer(city_name)
        analyzer.create_analysis()
    except Exception as e:
        print(f"分析失败: {e}") 