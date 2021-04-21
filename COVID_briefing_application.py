"""Main method for COVID-19 application.
The user can create and delete alarms, which can give reports
on top news headlines, weather and COVID-19 infection rate.

ECM1400, Programming, CA3
"""

import datetime
import time
import sched
import json
import logging
import requests
import pyttsx3
from uk_covid19 import Cov19API
from flask import Markup
from flask import render_template
from flask import Flask
from flask import request

app = Flask(__name__)
alarm_schedule = sched.scheduler(time.time, time.sleep)

def reset_persistent_data():
    """Resets config file to first-startup state

    No Arguments
    """
    try:
        with open("config.json", "r") as f:
            config_file = json.load(f)

        config_file["persistent-data"]["ID-value"] = 0
        config_file["persistent-data"]["notifications"] = []
        config_file["persistent-data"]["undismissed_alarms"] = []
        config_file["persistent-data"]["upcoming_alarms"] = []

        with open("config.json", "w") as f:
            json.dump(config_file, f, indent=4, sort_keys=True)
        logging.info("Config file has been reset.")
    except Exception as raised_exception:
        logging.exception("Error in reset_config : "+str(raised_exception))


#Opening config file
with open("config.json", "r") as f:
    config_file = json.load(f)
keys = config_file["API-keys"]
settings = config_file["settings"]
persistent_data = config_file["persistent-data"]

#logging can be in info mode for cleaner data
FORMAT = "%(levelname)s: %(asctime)s %(message)s"

if settings["debug-mode"] == "True":
    logging.basicConfig(filename="program_log.log", format=FORMAT, level=logging.DEBUG)
else:
    logging.basicConfig(filename="program_log.log", format=FORMAT, level=logging.INFO)

logging.info("App has been initialized!")

#Formats minutes for welcome notification
if len(str(settings["daily-notification-min"])) == 1:
    FORMATTED_MINS = "0"+str(settings["daily-notification-min"])
else:
    FORMATTED_MINS = str(settings["daily-notification-min"])
welcome_message = {"title" : "Welcome to the COVID-19 Briefing and Alarm application!",
"content" : Markup("Your location is set to : "+settings["covid19-region"]+"<br>"+
                    "Daily infection rate notifications set to appear at "+
                    str(settings["daily-notification-hour"])+":"+
                    FORMATTED_MINS)}

notifications = config_file["persistent-data"]["notifications"]

#If welcome notification hasn't been displayed, display it!
if not welcome_message in notifications:
    notifications.append(welcome_message)
    config_file["persistent-data"]["notifications"] = notifications

    with open("config.json", "w") as f:
        json.dump(config_file, f, indent=4, sort_keys=True)

#once  upcoming alarm time appears, data is fetched
upcoming_alarms = config_file["persistent-data"]["upcoming_alarms"]
undismissed_alarms = config_file["persistent-data"]["undismissed_alarms"]


def get_day_news(date : time) -> str:
    """Returns formatted news string with headlines from the given date

    Keyword Arguments:
    date -- Date for which news articles are fetched
    """

    current_time = time.localtime()

    #checks if current day is day being fetched
    if (current_time.tm_year == date.tm_year and
        current_time.tm_mon == date.tm_mon and
        current_time.tm_mday == date.tm_mday):

        try:
            base_url = 'http://newsapi.org/v2/top-headlines'
            location = "?country=" + settings["news-country"]
            api_key = "&apiKey="+keys["news"]

            final_url = base_url + location + api_key

            response = requests.get(final_url).json()

            articles = response["articles"]
            formatted_text = "<b>Top news headlines :</b><br>"

            #Gets top 3 results
            for i in range(3):
                formatted_text = formatted_text + articles[i]["title"] + "<br>"

            logging.info("Fetched day news for alarm ring.")
            return formatted_text

        except Exception as raised_exception:
            logging.exception("Failed to retrieve news data for given day : "+str(raised_exception))
            return "Error in retrieving data. Please check log for more information."

    logging.warning("Attempt to access historical data detected. Returning Unsupported.")
    return "Historical news data not supported!"

def get_day_weather(date : time) -> str:
    """Returns formatted string with current date's weather
    Will return "historical weather not supported" if date
    doesn't match current date (openweathermap doesn't support historical data)

    Keyword Arguments:
    date -- Date for which weather is fetched
    """

    current_time = time.localtime()

    #checking if it's current day
    try:
        if (current_time.tm_year == date.tm_year and
            current_time.tm_mon == date.tm_mon and
            current_time.tm_mday == date.tm_mday):

            base_url = "http://api.openweathermap.org/data/2.5/weather"
            city = "?q=" + settings["weather-city"]
            api_key = "&appid="+keys["weather"]

            final_url = base_url + city + api_key

            response = requests.get(final_url).json()


            start = "<b>Weather :</b><br>Weather in " + response["name"] + " is "
            description = response["weather"][0]["description"]
            temp = response["main"]["temp"] - 273.15 #converting temp from K to celsius
            formatted_temp = str(round(temp,1))

            weather_text = start + description + ", " + formatted_temp + "ºC"

            logging.info("Fetched day weather for alarm ring.")
            return weather_text

    except Exception as raised_exception:
        logging.exception("Failed to retrieve weather data for given day : "+str(raised_exception))
        return "Error in retrieving data. Please check log for more information."

    logging.warning("Attempt to access historical data detected. Returning Unsupported.")
    return "Historical weather not supported!"


#Certain areas are messed up;
#Exeter : works fine
#England : Works fine
#Kent : Works fine
#Scotland : Works fine
#Birmingham : works fine (array size 2 but identical data)
#Manchester : works fine (same as birmingham)
#London : gives array of length 2 with data in second (works with -1 access)
#Bristol : straight up 0 data
#Glasgow : straight up 0 data
#Edinburgh : straight up 0 data
def get_day_infection_rate(date : time) -> str:
    """Returns formatted string with selected date's
    COVID-19 infection rate compared to the previous week's

    Keyword Arguments:
    date -- Date for which Infection rate is fetched
    """

    formatted_text = ""

    try:
        datetime_date = time_to_datetime(date)

        date_format = "%Y-%m-%d"

        current_date = (datetime_date - datetime.timedelta(days = 1)).strftime(date_format)
        prev_date = (datetime_date - datetime.timedelta(days = 2)).strftime(date_format)


        data_structure = {
            "date" : "date",
            "newCasesByPublishDate" : "newCasesByPublishDate"
        }

        data_filter_current = ["areaName="+settings["covid19-region"],"date="+current_date]
        data_filter_prev = ["areaName="+settings["covid19-region"],"date="+prev_date]

        api_response_current = Cov19API(
                        filters = data_filter_current,
                        structure = data_structure)

        api_response_prev = Cov19API(
                        filters = data_filter_prev,
                        structure = data_structure)

        current_json = api_response_current.get_json()
        prev_json = api_response_prev.get_json()

    except Exception as raised_exception:
        logging.exception("Error in API Access : "+str(raised_exception))
        formatted_text = "Error accessing API. Check log for more details."


    #IF there's data display it, otherwise display discompatibility
    if current_json["data"]:

        try:
            #using negative list values increases compatibility for edge cases
            change_in_rate = (current_json["data"][-1]["newCasesByPublishDate"] -
                                prev_json["data"][-1]["newCasesByPublishDate"])

            date_format = "%d-%m-%Y"
            formatted_date = (datetime_date - datetime.timedelta(days = 1)).strftime(date_format)

            formatted_text = ("Daily COVID-19 case increase in " +
                                settings["covid19-region"] +
                                " was " +
                                str(current_json["data"][-1]["newCasesByPublishDate"]) +
                                " on " + formatted_date + ",")

            if change_in_rate < 0:
                formatted_text = (formatted_text + " down " +
                                    str(abs(change_in_rate)) +
                                    " from the previous day.")
            else:
                formatted_text = (formatted_text + " up " +
                                    str(abs(change_in_rate)) +
                                    " from the previous day.")
            logging.info("Fetched COVID-19 data for "+formatted_date)
        except Exception as raised_exception:
            logging.exception("Error in COVID-19 data access : "+str(raised_exception))
            formatted_text = "Error accessing data. Check log for more details."

    elif formatted_text == "":
        logging.error("Failed to fetch COVID-19 infection data. Date/Area unsupported by API.")
        formatted_text = ("COVID-19 infection data for " + settings["covid19-region"]  +
                            " unavailable through PHE database for given date")

    return formatted_text


#works with IDs
def del_notif(notif_to_delete : str):
    """Dismisses selected notification

    Keyword Arguments:
    notif_to_delete -- Notification to be dismissed
    """

    for notif in notifications:
        if notif["title"] == notif_to_delete:
            notif_index = notifications.index(notif)
            notifications.pop(notif_index)

            config_file["persistent-data"]["notifications"] = notifications

            with open("config.json", "w") as f:
                json.dump(config_file, f, indent=4, sort_keys=True)

            logging.info("Deleted notification " + notif["title"])
            break

def del_alarm(alarm_to_delete : str):
    """Dismisses selected alarm

    Keyword Arguments:
    alarm_to_delete -- Alarm to be dismissed
    """

    for alarm in undismissed_alarms:
        if alarm["title"] == alarm_to_delete:
            alarm_index = undismissed_alarms.index(alarm)
            undismissed_alarms.pop(alarm_index)

            config_file["persistent-data"]["undismissed_alarms"] = undismissed_alarms

            with open("config.json", "w") as f:
                json.dump(config_file, f, indent=4, sort_keys=True)

            logging.info("Deleted alarm " + alarm["title"])
            break
    for alarm in upcoming_alarms:
        if alarm["title"] == alarm_to_delete:
            alarm_index = upcoming_alarms.index(alarm)
            upcoming_alarms.pop(alarm_index)

            config_file["persistent-data"]["upcoming_alarms"] = upcoming_alarms

            with open("config.json", "w") as f:
                json.dump(config_file, f, indent=4, sort_keys=True)

            logging.info("Deleted alarm " + alarm["title"])
            break



#this works
def set_alarm():
    """Creates alarm according to the data found in the address bar.

    No arguments
    """

    try:
        alarm_time = request.args.get('alarm')
        alarm_id = str(config_file["persistent-data"]["ID-value"])
        alarm_name = request.args.get("two") + " (ID : " + alarm_id + ")"

        new_alarm = {"title" : alarm_name, "content" : "", "time" : alarm_time}

        
        date_content = time.strftime("%H:%M %A, %d %B %Y", string_to_time(alarm_time))
        date_content = "Upcoming: <b>" + date_content + "</b>"

        new_alarm["content"] = date_content + "<br>Alarm will notify of COVID-19 infection rate"

        if request.args.get("weather") and request.args.get("news"):
            new_alarm["content"] = new_alarm["content"] + ", weather and news"
        elif request.args.get("news"):
            new_alarm["content"] = new_alarm["content"] + "  news"
        elif request.args.get("weather"):
            new_alarm["content"] = new_alarm["content"] + " and weather"

        #seems to work
        current_time = datetime.datetime.now()
        alarm_time_comparison = time_to_datetime(string_to_time(alarm_time))

        alarm_already_added = False

        #This loop avoids errors where alarms are added twice
        for alarm in undismissed_alarms:
            if alarm["title"] == alarm_name:
                alarm_already_added = True
                break

        if current_time < alarm_time_comparison and alarm_already_added is False:
            upcoming_alarms.append(new_alarm)

            config_file["persistent-data"]["ID-value"] += 1
            config_file["persistent-data"]["upcoming_alarms"] = upcoming_alarms

            with open("config.json", "w") as f:
                json.dump(config_file, f, indent=4, sort_keys=True)
            logging.info("Alarm added, "+alarm_time+", title "+new_alarm["title"])


        elif alarm_already_added is False:
            upcoming_alarms.append(new_alarm)

            config_file["persistent-data"]["ID-value"] += 1

            with open("config.json", "w") as f:
                json.dump(config_file, f, indent=4, sort_keys=True)

            logging.info("Alarm added, "+alarm_time+", title "+new_alarm["title"]+ ". Ringing immediately")
            alarm_ring(new_alarm["title"])  #immediately rings it
    except Exception as raised_exception:
        logging.exception("Error in adding alarm: "+str(Exception))

def alarm_ring(title : str):
    """Moves upcoming alarms to undismissed alarms, runs tts
    notification, and fetches content required for alarm body

    Keyword Arguments:
    title -- Title of alarm to ring
    """

    tts_engine = pyttsx3.init()

    for checked_alarm in upcoming_alarms:
        if checked_alarm["title"] == title:
            alarm = checked_alarm
            alarm_index = upcoming_alarms.index(checked_alarm)
            upcoming_alarms.pop(alarm_index)

            try:
                tts_engine.say(alarm["title"])
                tts_engine.runAndWait()
            except RuntimeError:
                logging.error("TTS Engine overloaded. Moving on.")
            except Exception as raised_exception:
                logging.exception("Error in TTS engine :"+str(raised_exception))


            try:
                weather_content = ""
                news_content = ""
                infection_content = ""

                alarm_date = string_to_time(alarm["time"])
                date_content = time.strftime("%H:%M %A, %d %B %Y", alarm_date)
                date_content = "<b>" + date_content + "</b>"

                #checks if content contains weather/news and fetches necessary data
                if "weather" in alarm["content"]:
                    weather_content = get_day_weather(alarm_date)
                if "news" in alarm["content"]:
                    news_content = get_day_news(alarm_date)

                infection_content = get_day_infection_rate(alarm_date)

                content = [date_content, infection_content, weather_content, news_content]

                alarm["content"] = ""
                #Markup makes flask not ignore newlines
                for item in content:
                    if item:
                        alarm["content"] = alarm["content"] + item + "<br>"

                alarm["content"] = Markup(alarm["content"])

                undismissed_alarms.append(alarm)

                config_file["persistent-data"]["undismissed_alarms"] = undismissed_alarms

                with open("config.json", "w") as f:
                    json.dump(config_file, f, indent=4, sort_keys=True)

                logging.info("Alarm rang " + alarm["title"])
            except Exception as raised_exception:
                logging.exception("Error in Alarm ring :"+str(raised_exception))

            break

def notification_ring(date : time):
    """Rings COVID-19 notification according to given
    date.

    Keyword Arguments:
    date -- Date for COVID-19 Infection Rates
    """
    try:
        date_content = time.strftime("%A, %d %B %Y", date)

        infection_content = get_day_infection_rate(date)

        notif = {"title":"COVID-19 Update "+date_content,"content":infection_content}


        #this fragment checks if the notification has already been displayed
        notif_displayed = False
        for notif_checked in notifications:
            if notif_checked["title"] == "COVID-19 Update "+date_content:
                notif_displayed = True
                break

        if not notif_displayed:
            notifications.append(notif)

            config_file["persistent-data"]["notifications"] = notifications

            with open("config.json", "w") as f:
                json.dump(config_file, f, indent=4, sort_keys=True)
            logging.info("Notification sent")

    except Exception as raised_exception:
        logging.exception("Error in notification ring : "+str(raised_exception))

def refresh_upcoming_alarms():
    """Refreshes delay for alarms that are upcoming

    No arguments
    """

    try:
        comp_time = datetime.datetime.now()
        current_time = time.localtime()

        #basically calculates how long until it's time for the alarms to ring
        #the list is looked through reversed to avoid errors when popping in
        #alarm_ring
        for alarm in reversed(upcoming_alarms):
            alarm_time = string_to_time(alarm["time"])

            alarm_time_comparison = time_to_datetime(alarm_time)

            if comp_time < alarm_time_comparison:
                #using abs helps with compatibility
                hour_seconds = abs(alarm_time.tm_hour - current_time.tm_hour) * 3600
                minute_seconds = abs(alarm_time.tm_min - current_time.tm_min) * 60
                delay = hour_seconds + minute_seconds

                alarm_schedule.enter(int(delay), 1, alarm_ring, (alarm["title"],))
            else:
                alarm_ring(alarm["title"])

        #if it is the daily notif time it's displayed
        if(current_time.tm_hour == settings["daily-notification-hour"] and
            current_time.tm_min == settings["daily-notification-min"]):
            notification_ring(time.localtime())

        logging.info("Alarms refreshed.")

    except Exception as raised_exception:
        logging.exception("Error in alarm refresh :"+str(raised_exception))


def string_to_time(time_string : str) -> time: #E.G 1231-02-20T21:03
    """Converts string to time object according to time format "%Y-%m-%dT%H:%M"

    Keyword Arguments:
    time_string -- String to be converted to time object
    """

    try:
        time_format = "%Y-%m-%dT%H:%M"
        return_time = time.strptime(time_string, time_format)
    except Exception as raised_exception:
        logging.exception("Error in string to time conversion :"+str(Exception))

    return return_time

def time_to_datetime(given_time : time) -> datetime:    #datetime objects facilitate comparisons
    """Converts time object to datetime object (which facilitate comparisons)

    Keyword Arguments:
    given_time -- time object to be converted to datetime object
    """

    try:
        minute = given_time.tm_min
        hour = given_time.tm_hour
        day = given_time.tm_mday
        month = given_time.tm_mon
        year = given_time.tm_year

        new_datetime = datetime.datetime(year = year,
                                        month = month,
                                        day = day,
                                        hour = hour,
                                        minute = minute)
    except Exception as raised_exception:
        logging.exception("Exception in day conversion : "+str(raised_exception))

    return new_datetime


def test_news_api():
    """Tests news api servers
    """

    base_url = 'http://newsapi.org/v2/top-headlines'
    location = "?country=" + settings["news-country"]
    api_key = "&apiKey="+keys["news"]

    final_url = base_url + location + api_key

    response = requests.get(final_url).json()

    assert response["status"] == "ok"

def test_weather_api():
    """Tests weather api servers
    """

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    city = "?q=" + settings["weather-city"]
    api_key = "&appid="+keys["weather"]

    final_url = base_url + city + api_key

    response = requests.get(final_url).json()

    assert response["cod"] == 200

def test_covid_api():
    """Tests COVID-19 api servers
    """

    date = time.localtime()
    datetime_date = time_to_datetime(date)

    date_format = "%Y-%m-%d"

    current_date = (datetime_date - datetime.timedelta(days = 1)).strftime(date_format)

    data_structure = {
        "date" : "date",
        "newCasesByPublishDate" : "newCasesByPublishDate"
    }

    data_filter_current = ["areaName="+settings["covid19-region"],"date="+current_date]

    response = Cov19API(filters = data_filter_current, structure = data_structure)

    assert response.get_json


@app.route("/index")
def index():
    """Method that runs whenever site refreshes

    No Arguments
    """
    alarm_schedule.run(blocking=False)

    if request.args.get("alarm_item"):
        del_alarm(request.args.get("alarm_item"))
    if request.args.get("notif"):
        del_notif(request.args.get("notif"))
    if request.args.get("alarm"):   #code stil unfinalized
        set_alarm()

    #for nice formatting
    for notif in notifications:
        notif["content"] = Markup(notif["content"])

    refresh_upcoming_alarms()

    #Joining all alarms for final display
    all_alarms = []
    all_alarms.extend(undismissed_alarms)
    all_alarms.extend(upcoming_alarms)
    for alarm in all_alarms:
        alarm["content"] = Markup(alarm["content"])

    return render_template("template.html",
                            title= "COVID-19 Briefing Application",
                            notifications = notifications,
                            alarms = all_alarms,
                            image = "icon.png")


if __name__ == '__main__':
    app.run()
