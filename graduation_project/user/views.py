import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from mybase.db import redis2Data
from mybase import globalVar
from mybase.myscheduler import my_streaming_scheduler, my_streaming_scheduler_stop
from myspark.GetData import getUser, getMoniterDataFromMysql, set2RedisData, get_car_by_id


# Create your views here.

def index(request):
    return render(request, 'index.html')


def login(request):
    if getUser(request.POST['user_name'], request.POST['user_password']):
        return mapShow(request)
    return HttpResponse("用户名或密码错误或者没有权限")


def mapShow(request):
    return render(request, 'map_show.html')


def monitorShow(request):
    return render(request, 'monitor_log.html')


def getMonitorByRoad(request):
    return render(request, 'monitor_log.html',
                  {'data': set2RedisData(
                      ('monitor_date', 'monitor_id', 'camera_id', 'car_id', 'action_time', 'car_speed', 'road_id',
                       'area_id'),
                      getMoniterDataFromMysql(road_id=request.GET['road_id']))})


def getMonitorByArea(request):
    return render(request, 'monitor_log.html',
                  {'data': set2RedisData(
                      ('monitor_date', 'monitor_id', 'camera_id', 'car_id', 'action_time', 'car_speed', 'road_id',
                       'area_id'),
                      getMoniterDataFromMysql(area_id=request.GET['area_id']))})


def getMonitorData(request):
    return render(request, 'monitor_log.html',
                  {'data': set2RedisData(
                      ('monitor_date', 'monitor_id', 'camera_id', 'car_id', 'action_time', 'car_speed', 'road_id',
                       'area_id'),
                      getMoniterDataFromMysql(from_date=request.POST['from_date'], end_date=request.POST['end_date'],
                                              area_id=request.POST['area_id'], road_id=request.POST['road_id'],
                                              car_id=request.POST['car_id'], car_speed=request.POST['car_speed'],
                                              monitor_id=request.POST['monitor_id'],
                                              camera_id=request.POST['camera_id'], limit_num=request.POST['limit_num'],
                                              page_num=request.POST['page_num']))})


def trafficStatics(request):
    return render(request, 'traffic_statistics.html',
                  {'myData': {'yesterdayAreas': json.loads(redis2Data('yesterdayAreas')),
                              'yesterdayRoads': json.loads(redis2Data('yesterdayRoads')),
                              'lastWeek': json.loads(redis2Data('lastWeek')),
                              'yesterday_speeding_car': json.loads(redis2Data('yesterday_speeding_car')),
                              'yesterdayAverageSpeed': redis2Data('yesterdayAverageSpeed')
                              }})


def districtStatics(request):
    area_id = '1'
    try:
        area_id = request.POST['area_id']
    except KeyError as ke:
        pass
    return render(request, 'district_statistics.html', {
        'myData': {
            'areaId': area_id,
            'roadDetail': json.loads(redis2Data('yesterdayRoadsByArea' + area_id)),
            'lastWeek': json.loads(redis2Data('lastWeekByArea' + area_id)),
            'speedingCar': json.loads(redis2Data('speedingRecordByArea' + area_id))
        }})


def car_search(request):
    try:
        car_id = request.GET['car_id']
        car_list = get_car_by_id(car_id)
        print(car_list)
        if len(car_list) == 1:
            try:
                return render(request, 'car_search.html', {
                    'myData': {
                        'car_list': [],
                        'car_id': car_list[0],
                        'car_road_traffic': json.loads(redis2Data('car_road_traffic' + car_list[0])),
                        'car_traffic': redis2Data('car_traffic' + car_list[0]),
                        'car_average_speed': redis2Data('car_average_speed' + car_list[0]),
                        'speeding_record_by_car': json.loads(redis2Data('speeding_record_by_car' + car_list[0]))
                    }})
            except TypeError:
                return render(request, 'car_search.html', {'myData': {'car_list': []}})
        else:
            return render(request, 'car_search.html', {'myData': {'car_list': car_list}})
    except KeyError:
        pass
    return render(request, 'car_search.html', {'myData': {'car_list': []}})


def foreign_car(request):
    return render(request, 'foreign_car.html', {'myData': {
        'last_week_foreign_car_count': redis2Data('last_week_foreign_car_count'),
        'last_week_foreign_car_area': json.loads(redis2Data('last_week_foreign_car_area')),
        'last_week_foreign_car_road': json.loads(redis2Data('last_week_foreign_car_road')),
        'last_week_foreign_car': json.loads(redis2Data('last_week_foreign_car')),
        'yesterday_foreign_car': json.loads(redis2Data('yesterday_foreign_car'))
    }})


def collision_analysis(request):
    return render(request, 'collision_analysis.html', {'myData': {
        'collision_matter_list': json.loads(redis2Data('collision_matter_list')),
        'collision_car_count': redis2Data('collision_car_count')
    }})


def real_time_analysis_start(request):
    # print(globalVar.get_start_streaming_flag())
    my_streaming_scheduler()
    # if globalVar.get_start_streaming_flag() == 0:
    #     globalVar.set_start_streaming_flag(1)

    return HttpResponse('start-ok')


def real_time_analysis_stop(request):
    my_streaming_scheduler_stop()
    return HttpResponse('stop-ok')


def real_time_analysis(request):
    # print(globalVar.get_start_streaming_flag())
    # if globalVar.get_start_streaming_flag() == 0:
    #     globalVar.set_start_streaming_flag(1)
    #     my_streaming_scheduler()
    # return render(request, 'real_time_analysis.html', {'myData': {
    #     'real_time_car_count': redis2Data('real_time_car_count'),
    #     'real_time_car_road_list': json.loads(redis2Data('real_time_car_road_list')),
    #     'real_time_speeding_data_list': json.loads(redis2Data('real_time_speeding_data_list'))
    # }})
    return render(request, 'real_time_analysis.html')


def real_time_data(request):
    my_data = {}
    my_data['real_time_car_count'] = redis2Data('real_time_car_count')
    my_data['real_time_car_road_list'] = json.loads(redis2Data('real_time_car_road_list'))
    my_data['real_time_speeding_data_list'] = json.loads(redis2Data('real_time_speeding_data_list'))
    return JsonResponse(my_data, safe=False)


def traffic_forecast(request):
    return render(request, 'traffic_forecast.html', {'myData': {
        'bayes_predict_result': json.loads(redis2Data('bayes_predict_result')),
        'machine_learning_accuracy': '{:.2%}'.format(float(redis2Data('machine_learning_accuracy')))
    }})
