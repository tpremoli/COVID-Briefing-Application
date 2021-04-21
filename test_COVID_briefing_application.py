import json
import COVID_briefing_application
import time
from COVID_briefing_application import get_day_news
from COVID_briefing_application import get_day_weather
from COVID_briefing_application import get_day_infection_rate
from COVID_briefing_application import string_to_time
from COVID_briefing_application import time_to_datetime
from COVID_briefing_application import del_alarm
from COVID_briefing_application import del_notif
from COVID_briefing_application import reset_persistent_data
from COVID_briefing_application import alarm_ring
from COVID_briefing_application import notification_ring
from COVID_briefing_application import refresh_upcoming_alarms
from COVID_briefing_application import test_news_api
from COVID_briefing_application import test_weather_api
from COVID_briefing_application import test_covid_api

def test_reset_persistent_data():
    """Tests reset_persistent_data method
    """
    reset_persistent_data()

    with open("config.json", "r") as f:
        config_file = json.load(f)

    assert config_file["persistent-data"]["ID-value"] == 0
    assert config_file["persistent-data"]["notifications"] == []
    assert config_file["persistent-data"]["undismissed_alarms"] == []
    assert config_file["persistent-data"]["upcoming_alarms"] == []

def test_get_day_news():
    """Tests get_day_news method
    """
    time_string = "2001-11-11T19:23"
    time_format = "%Y-%m-%dT%H:%M"
    old_date = time.strptime(time_string, time_format)
    current_date = time.localtime()

    assert (get_day_news(current_date)
            .startswith("<b>Top news headlines :</b><br>") == True)

    assert (get_day_news(old_date) == "Historical news data not supported!")

def test_get_day_weather():
    """Tests get_day_weather method
    """
    time_string = "2001-11-11T19:23"
    time_format = "%Y-%m-%dT%H:%M"
    old_date = time.strptime(time_string, time_format)
    current_date = time.localtime()

    assert (get_day_weather(current_date).startswith(
            "<b>Weather :</b><br>Weather in ") == True)

    assert (get_day_weather(old_date) == "Historical weather not supported!")

def test_get_day_infection_rate():
    """Tests get_day_infection_rate method
    """
    time_string = "2020-11-11T19:23"
    time_format = "%Y-%m-%dT%H:%M"
    old_date = time.strptime(time_string, time_format)
    current_date = time.localtime()

    assert (get_day_infection_rate(old_date) ==
    "Daily COVID-19 case increase in Exeter was 25 on 10-11-2020, down 11 from the previous day.")
    assert (get_day_infection_rate)

def test_del_notif():
    """Tests del_notif method
    """

    #WARNING: This test will clear all the alarms that have been saved
    test_notif1 = {"title":"test_notif1","content":"content"}
    test_notif2 = {"title":"test_notif2","content":"content"}
    test_notif3 = {"title":"test_notif3","content":"content"}

    COVID_briefing_application.notifications = [test_notif1,test_notif2,test_notif3]

    del_notif("test_notif2")

    assert len(COVID_briefing_application.notifications) == 2
    assert test_notif2 not in COVID_briefing_application.notifications

    reset_persistent_data()   

def test_del_alarm():
    """Tests del_alarm method
    """

    #WARNING: This test will clear all the alarms that have been saved
    test_alarm1 = {"title":"test_alarm1","content":"content"}
    test_alarm2 = {"title":"test_alarm2","content":"content"}
    test_alarm3 = {"title":"test_alarm3","content":"content"}

    COVID_briefing_application.undismissed_alarms = [test_alarm1,test_alarm2,test_alarm3]

    del_alarm("test_alarm2")

    assert len(COVID_briefing_application.undismissed_alarms) == 2
    assert test_alarm2 not in COVID_briefing_application.undismissed_alarms

    reset_persistent_data()

#set_alarm cannot be tested as it relies on requests

def test_alarm_ring():
    """Tests alarm_ring method
    """

    #WARNING: This test will clear all the alarms that have been saved
    test_alarm1 = {"title":"test_alarm1","content":"content"}
    test_alarm2 = {"title":"test_alarm2","content":"content"}
    test_alarm3 = {"title":"test_alarm3","content":"content"}

    COVID_briefing_application.upcoming_alarms = [test_alarm1,test_alarm2,test_alarm3]
    COVID_briefing_application.undismissed_alarms = []

    alarm_ring("test_alarm2")

    assert len(COVID_briefing_application.upcoming_alarms) == 2
    assert test_alarm2 not in COVID_briefing_application.upcoming_alarms

    for alarm in COVID_briefing_application.undismissed_alarms:
        assert alarm["title"] == "test_alarm2"
        assert alarm["content"] == ""

    reset_persistent_data()

def test_notification_ring():
    """Tests notification_ring method
    """

    #WARNING: This test will clear all the alarms that have been saved
    notification_time = time.localtime()

    test_notif1 = {"title":"test_notif1","content":"content"}
    test_notif2 = {"title":"test_notif2","content":"content"}
    test_notif3 = {"title":"test_notif3","content":"content"}

    COVID_briefing_application.notifications = [test_notif1,test_notif2,test_notif3]

    notification_ring(notification_time)

    assert len(COVID_briefing_application.notifications) == 4

    reset_persistent_data()

def test_refresh_upcoming_alarms():
    """Tests refresh_upcoming_alarms method
    """
    test_alarm1 = {"title":"test_alarm1","content":"content","time":"1231-02-20T21:03"}
    test_alarm2 = {"title":"test_alarm2","content":"content","time":"2500-02-20T21:03"}
    test_alarm3 = {"title":"test_alarm3","content":"content","time":"3000-02-20T21:03"}

    COVID_briefing_application.upcoming_alarms = [test_alarm1,test_alarm2,test_alarm3]
    COVID_briefing_application.undismissed_alarms = []

    refresh_upcoming_alarms()

    assert len(COVID_briefing_application.undismissed_alarms) == 1
    assert len(COVID_briefing_application.alarm_schedule.queue) == 2

    reset_persistent_data()

def test_string_to_time():
    """Tests string_to_time method
    """
    time_string = "2020-11-11T19:23"
    time_format = "%Y-%m-%dT%H:%M"
    reformatted = time.strptime(time_string, time_format)

    assert string_to_time(time_string) == reformatted

def test_time_to_datetime():
    """Tests time_to_datetime method
    """
    conversion_time = time.localtime()
    
    assert time_to_datetime(conversion_time)

def test_API_servers():
    """Tests api servers
    """
    current_date = time.localtime()

    assert (get_day_infection_rate(current_date)
            .startswith("Daily COVID-19 case increase in "))
    
    assert (get_day_weather(current_date).startswith(
            "<b>Weather :</b><br>Weather in ") == True)

    assert (get_day_news(current_date)
            .startswith("<b>Top news headlines :</b><br>") == True)

    test_news_api()
    test_weather_api()
    test_covid_api()
