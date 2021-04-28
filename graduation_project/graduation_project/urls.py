"""graduation_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from user import views as user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user.index),
    path('login/', user.login),
    path('index/', user.mapShow),
    path('getmonitorbyroad/', user.getMonitorByRoad),
    path('getmonitorbyarea/', user.getMonitorByArea),
    path('getmonitordata/', user.getMonitorData),
    path('monitorShow/', user.monitorShow),
    path('trafficStatics/', user.trafficStatics),
    path('districtStatics/', user.districtStatics),
    path('carSearch/', user.car_search),
    path('foreignCar/', user.foreign_car),
    path('collisionAnalysis/', user.collision_analysis),
    path('realTimeAnalysisStart/', user.real_time_analysis_start),
    path('realTimeAnalysisStop/', user.real_time_analysis_stop),
    path('realTimeAnalysis/', user.real_time_analysis),
    path('realTimeData/', user.real_time_data),
    path('trafficForecast/', user.traffic_forecast)
]
