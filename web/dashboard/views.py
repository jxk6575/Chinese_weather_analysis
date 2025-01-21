from django.shortcuts import render
from visualize.visualizer import WeatherVisualizer

def dashboard_view(request):
    visualizer = WeatherVisualizer()
    return visualizer.render_dashboard(request)
