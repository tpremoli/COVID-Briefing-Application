<html>
<h1 id="covid19briefingapplication">
    COVID-19 Briefing Application</h1>

<h2 id="introduction">Introduction</h2>

<p>Welcome to the COVID-19 briefing application!</p>

<p>This application allows for the creation of timed alarms.<br> The user can decide to include news and weather briefings for the alarms,<br> and choose a date and time for them to ring. The application also includes<br> daily briefings on COVID-19 infection
    rates, and an ability to cancel alarms.</p>

<p>The news is acquired from <a href="https://newsapi.org/">newsapi.org</a>, and the weather is fetched from
    <a href="https://openweathermap.org/api">openweathermap.org</a>. The COVID-19 infection data is taken from <a href="https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/index.html">Public Health England.</a></p>

<p>The app maintains persistent data (Alarms won't be deleted on shutdown), and can be customized according to user specification. </p>
<br>
<h2 id="prerequisites">Prerequisites</h2>

<p>Python 3.9 and above
    <a href="https://openweathermap.org/api">openweathermap</a> API Key (placed in config.json file)
    <a href="https://newsapi.org/">newsapi</a> API Key (placed in config.json file)</p>
<br>
<h2 id="installation">Installation</h2>

<p>Requires pyttsx3, uk-covid19, Flask and requests.</p>

<p>Run the following pip commands in your command line interface to install the required packages:</p>

<pre><code>pip install pyttsx3
pip install uk-covid19
pip install Flask
pip install requests
</code></pre>

<p>Optional: pytest (for testing)</p>

<pre><code>pip install pytest
</code></pre>
<br>
<h2 id="gettingstarted">Getting started:</h2>

<ol>
    <li>
        <p>Extract the contents of this zip file into an empty folder</p>
    </li>
    <li>
        <p>Input your API keys into appropriate locations in the config.json file (Remove parenthesis, do not modify other aspects of file) and save it</p>
        <pre><code>"API-keys": {
    "news": "(newsapi API Key)",
    "weather": "(openweathermap API Key)"
},
</code></pre></li> 
    <li>
        <p>Navigate to project folder (containing <code>COVID&#95;briefing&#95;application.py</code>) in system command line</p>
    </li>
    <li>
        <p>Run the program using </p>
    </li>
    <pre><code>py COVID&#95;briefing&#95;application.py
</code></pre>
    <li>
        <p>Open host address in web browser and enjoy! (Address should be <code>http://127.0.0.1:5000/index</code>)</p>
    </li>
</ol>
<br>
<h2 id="configuration">Confguring</h2>
<p>To configure the application, enter config.json and modify the values in settings to your liking.</p>

<br>
<p>covid19-region : Location for COVID&#95;19 infection data to be fetched from. (Default: Exeter)</p>
<br>
<p>daily-notification-hour : Hour for daily notifications to be pushed, 24hr format. (Default: 14)</p>
<br>
<p>daily-notification-min : min for daily notifications to be pushed (do not justify, i.e, should be 5, not 05). (Default: 0)</p>
<br>
<p>debug-mode : Turns debug mode on in the logger (True/False). (Default: False)</p>
<br>
<p>news-country : Country for news headlines to be checked for. (Default: gb)</p>
<br>
<p>weather-city : City for weather data to be checked for. (Default: Exeter,uk)</p>

<br>
<h2 id="testing">Testing</h2>

<p><strong>WARNING:</strong> Running pytest will clear persistent data. API Keys will not be affected</p>

<ol>
    <li>Ensure that pytest has been installed</li>

    <li>Navigate to folder containing COVID&#95;briefing&#95;application.py and test&#95;COVID&#95;briefing&#95;application.py</li>

    <li>To run tests, type the following line into the console

        <pre><code>pytest
</code></pre>

</ol>
<br>
<h2 id="developerdocumentation">Developer Documentation</h2>

<h3 id="reset&#95;persistent&#95;data">reset&#95;persistent&#95;data</h3>

<p>Resets config file to first-startup state</p>

<p>No Arguments</p>

<h3 id="get&#95;day&#95;news">get&#95;day&#95;news</h3>

<p>Returns formatted news string with headlines from the given date</p>

<p>Keyword Arguments:</p>

<p>date -- Date for which news articles are fetched</p>

<h3 id="get&#95;day&#95;weather">get&#95;day&#95;weather</h3>

<p>Returns formatted string with current date's weather. Will return "historical weather not supported" if date doesn't match current date (openweathermap doesn't support historical data)</p>

<p>Keyword Arguments:</p>

<p>date -- Date for which weather is fetched</p>

<h3 id="get&#95;day&#95;infection&#95;rate">get&#95;day&#95;infection&#95;rate</h3>

<p>Returns formatted string with selected date's COVID-19 infection rate compared to the previous day's</p>

<p>Keyword Arguments:</p>

<p>date -- Date for which Infection rate is fetched</p>

<h3 id="del&#95;notif">del&#95;notif</h3>

<p>Dismisses selected notification</p>

<p>Keyword Arguments:</p>

<p>notif&#95;to&#95;delete -- Notification to be dismissed</p>

<h3 id="del&#95;alarm">del&#95;alarm</h3>

<p>Dismisses selected alarm</p>

<p>Keyword Arguments:</p>

<p>alarm&#95;to&#95;delete -- Alarm to be dismissed</p>

<h3 id="set&#95;alarm">set&#95;alarm</h3>

<p>Creates alarm according to the data found in the address bar.</p>

<p>No arguments</p>

<h3 id="alarm&#95;ring">alarm&#95;ring</h3>

<p>Moves upcoming alarms to undismissed alarms, runs tts notification, and fetches content required for alarm body</p>

<p>Keyword Arguments:</p>

<p>title -- Title of alarm to ring</p>

<h3 id="notification&#95;ring">notification&#95;ring</h3>

<p>Rings COVID-19 notification according to given date.</p>

<p>Keyword Arguments:</p>

<p>date -- Date for COVID-19 Infection Rates</p>

<h3 id="refresh&#95;upcoming&#95;alarms">refresh&#95;upcoming&#95;alarms</h3>

<p>Refreshes delay for alarms that are upcoming</p>

<p>No arguments</p>

<h3 id="string&#95;to&#95;time">string&#95;to&#95;time</h3>

<p>Converts string to time object according to time format "YYYY-MM-DD T HH:MM"</p>

<p>Keyword Arguments:</p>

<p>time&#95;string -- String to be converted to time object</p>

<h3 id="time&#95;to&#95;datetime">time&#95;to&#95;datetime</h3>

<p>Converts time object to datetime object (which facilitate comparisons)</p>

<p>Keyword Arguments:</p>

<p>given&#95;time -- time object to be converted to datetime object</p>

<h3 id="test&#95;news&#95;api">test&#95;news&#95;api</h3>

<p>Tests news api servers</p>

<h3 id="test&#95;weather&#95;api">test&#95;weather&#95;api</h3>

<p>Tests weather api servers</p>

<h3 id="test&#95;covid&#95;api">test&#95;covid&#95;api</h3>

<p>Tests COVID-19 api servers</p>

<h3 id="index">index</h3>

<p>Method that runs whenever site refreshes</p>

<p>No Arguments</p>
<br>
<h2 id="acks">Acknowlegements</h2>
<p>Special thanks to:
    <br><a href="https://newsapi.org/">newsapi.org</a> developers for their incredible news API
    <br><a href="https://openweathermap.org/api">openweathermap.org</a> developers for their great open weather API
    <br><a href="https://publichealthengland.github.io/coronavirus-dashboard-api-python-sdk/index.html">Public Health England.</a> for their useful python modules and APIs
    <br>and of course, Matt Collison, for helping me with all doubts I had when working on this project.</p>


<br>
<h2 id="license">License</h2>

<p>Author: Tomas Premoli, 2020.<br> Please look at LICENSE file for further licensing information.</p>

</html>