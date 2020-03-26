import schedule 
import pymsteams
import time
from lxml import html	
import requests
from datetime import datetime

#Time string given to scheduler to post each day (mon-sun)
time_to_post = "08:00"

#Pages for scraping BOM weather observations and latest corona virus stats
canberra_BOM_obs = r"http://www.bom.gov.au/act/observations/canberra.shtml"
australia_corona_stats = r"https://www.worldometers.info/coronavirus/country/australia/"

#Incoming Webhooks needs to be added as an app to your team and a webhook created, in the process you will get a webhook URL
webhook = r"[incoming webhook URL from MS Teams]"

#Get the current canberra temperature from BOM obs 
##### - WARNING: do not scrape the BOM too hard, it will be ok for an hour or two and then they will block your IP - ####
def getTemp():
	page = requests.get(canberra_BOM_obs)
	tree = html.fromstring(page.content)
	
	#HTML as shown in page source:   <td headers="tCANBERRA-tmp tCANBERRA-station-canberra">[temp_value]</td>
	temp = tree.xpath('//td[@headers="tCANBERRA-tmp tCANBERRA-station-canberra"]/text()')
	
	return str(temp[0])

#Get number of people who have recovered from corona virus in Australia
def getRecoveries():
	page = requests.get(australia_corona_stats)
	tree = html.fromstring(page.content)

	#HTML as shown in page source:   <span class="number-table" style="color:#8ACA2B">[recovered_value]</span>
	temp = tree.xpath('//span[@class="number-table"]/text()')
	
	return str(temp[2])

#Get morning/afternoon/evening depending on hour of the day
def get_part_of_day(hour):
    return (
        "morning" if 0 <= hour <= 11
        else
        "afternoon" if 12 <= hour <= 17
        else
        "evening" 
    )

#Function purely for sending a basic test post, only for QA, not for deployment
def testpost():
	myTeamsMessage = pymsteams.connectorcard(webhook)
	myTeamsMessage.text("Test post, please ignore")
	myTeamsMessage.send()

#Post to MS Teams tab 
def post():
	
	#creates a connector card using webhook url from MS teams
	myTeamsMessage = pymsteams.connectorcard(webhook)
	
	#get current hour and time
	now = datetime.now()
	h = now.hour
	time = now.strftime("%H:%M")
	
	#compose core of message and add text 
	text1 = "Good "+get_part_of_day(h)+" team! As of "+time+", the temperature in Canberra is "+getTemp()+"c, and "+getRecoveries()+" healthy people have recovered from Covid-19 in Australia!"
	myTeamsMessage.text(text1)
	
	#caveat to include in case things go wrong
	text2 = "-This has been an automated message, please let Mick know if things have gone awry"
	
	# Create Section 1, used for 'everything is fine' image
	Section1 = pymsteams.cardsection()
	Section1.addImage("https://i.imgur.com/B7ZtJwD.png")
	
	# Create Section 2, used for caveat
	Section2 = pymsteams.cardsection()
	Section2.text(text2)
	
	# Add sections to message
	myTeamsMessage.addSection(Section1)
	myTeamsMessage.addSection(Section2)

	# send the message.
	myTeamsMessage.send()
	print("Message sent to team")

#Create a schedule event for the same time everyday using the time_to_post defined at top of script
schedule.every().day.at(time_to_post).do(post) 

# Loop so that the scheduling task keeps on running until interupted
while True: 

	#printing '.' just so you can tell its looping in console
	print(".")
	
	# Checks whether a scheduled task is pending and runs/doesnt run 
	schedule.run_pending() 
	
	#1 second pause between loops
	time.sleep(1) 
