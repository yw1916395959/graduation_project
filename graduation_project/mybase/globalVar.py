import datetime

from apscheduler.schedulers.blocking import BlockingScheduler


class GlobalVar:
    real_time_car_count = None
    real_time_car_road_list = None
    real_time_speeding_data_list = None
    start_streaming_flag = True
    my_streaming_thread = None
    yesterday = None
    ssc = None
    sc = None
    monitor_df = None
    my_scheduler = None
    area_road_list = [[4, 7, 8, 9], [2, 3, 4, 5], [1, 4, 5, 6]]


def global_var_yesterday_init():
    if not get_yesterday():
        set_yesterday(datetime.datetime.now() - datetime.timedelta(days=1))


def global_var_my_scheduler_init():
    if not get_my_scheduler():
        set_my_scheduler(BlockingScheduler())


def global_var_init():
    GlobalVar.real_time_car_count = 0
    GlobalVar.real_time_car_road_list = [{'road_id': 1, 'count': 0}, {'road_id': 2, 'count': 0},
                                         {'road_id': 3, 'count': 0}, {'road_id': 4, 'count': 0},
                                         {'road_id': 5, 'count': 0}, {'road_id': 6, 'count': 0},
                                         {'road_id': 7, 'count': 0}, {'road_id': 8, 'count': 0},
                                         {'road_id': 9, 'count': 0}]
    GlobalVar.real_time_speeding_data_list = []


def set_real_time_car_count(real_time_car_count):
    GlobalVar.real_time_car_count = real_time_car_count


def get_real_time_car_count():
    return GlobalVar.real_time_car_count


def set_real_time_car_road_list(real_time_car_road_list):
    GlobalVar.real_time_car_road_list = real_time_car_road_list


def get_real_time_car_road_list():
    return GlobalVar.real_time_car_road_list


def set_real_time_speeding_data_list(real_time_speeding_data_list):
    GlobalVar.real_time_speeding_data_list = real_time_speeding_data_list


def get_real_time_speeding_data_list():
    return GlobalVar.real_time_speeding_data_list


def set_start_streaming_flag(start_streaming_flag):
    GlobalVar.start_streaming_flag = start_streaming_flag


def get_start_streaming_flag():
    return GlobalVar.start_streaming_flag


def set_my_streaming_thread(my_streaming_thread):
    GlobalVar.my_streaming_thread = my_streaming_thread


def get_my_streaming_thread():
    return GlobalVar.my_streaming_thread


def set_yesterday(yesterday):
    GlobalVar.yesterday = yesterday


def get_yesterday():
    return GlobalVar.yesterday


def set_ssc(ssc):
    GlobalVar.ssc = ssc


def get_ssc():
    return GlobalVar.ssc


def set_sc(sc):
    GlobalVar.sc = sc


def get_sc():
    return GlobalVar.sc


def set_monitor_df(monitor_df):
    GlobalVar.monitor_df = monitor_df


def get_monitor_df():
    return GlobalVar.monitor_df


def set_area_road_list(area_road_list):
    GlobalVar.area_road_list = area_road_list


def get_area_road_list():
    return GlobalVar.area_road_list


def set_my_scheduler(my_scheduler):
    GlobalVar.my_scheduler = my_scheduler


def get_my_scheduler():
    return GlobalVar.my_scheduler
