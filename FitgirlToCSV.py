
##################END CONFIG AREA####################

#A certain repack site, ex 'mittGirl-Resnacks.mite'
fitgirlSiteUrl = 'mittGirl-Resnacks.mite'

##################END CONFIG AREA####################

#Check Python Version
import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
    sys.exit(1)

try:
    import time
except:
	print('Missing module time, please install using "pythom -m pip install time"')
	pass

#Makes a universal cls function to clear screen. Thanks popcnt: https://stackoverflow.com/a/684344
import os
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

#Set Window Title. I stuck this under a "try" command because this would fail on Linux systems due to no ctypes/window stuffs
#Although trying to run this on Linux would likely fail since we use a headless chrome browser window to approve donos...
try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleTitleW("Fitgirl to CSV")
except:
	if os.name=='nt':
		print('Missing module ctypes, please install using "pythom -m pip install ctypes" if you care about having a fancy cmd prompt title')
	else:
		pass
	pass
try:
	from bs4 import BeautifulSoup
except ImportError:
	print('Missing module bs4, please install using "pythom -m pip install bs4"')

try:
	import csv
except ImportError:
	print('Missing module csv, please install using "pythom -m pip install csv"')

try:
	import requests
except ImportError:
	print('Missing module requests, please install using "pythom -m pip install requests"')

#Disable SSL warnings
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

#Gets how many page numbers there are on the site
def getPageNumbers():
	url = 'https://'+ fitgirlSiteUrl + '/all-my-repacks-a-z/'
	payload = {}
	headers = {}
	html_doc = (requests.request("GET", url, json=payload, headers=headers, verify=False))
	#print(response.text)
	soup = BeautifulSoup(html_doc.text, 'html.parser')
	footerFind = soup.find('ul', class_='lcp_paginator')
	totalPages = int(footerFind.find_all('li')[-2].getText())
	return totalPages


#Actually scrape the page for links/text
def getPageGameList(pageNumber):
	url = 'https://' + fitgirlSiteUrl + '/all-my-repacks-a-z/?lcp_page0=' + str(pageNumber) + '#lcp_instance_0'
	payload = {}
	headers = {}
	html_doc = (requests.request("GET", url, json=payload, headers=headers, verify=False))
	#print(response.text)
	soup = BeautifulSoup(html_doc.text, 'html.parser')
	listFindUL = soup.find('ul', class_='lcp_catlist')
	#listContents = footerFind.find_all('li')
	listOfGames = []
	for a in listFindUL.find_all('a', href=True):
		#print("URL:", a['href'], 'Text: ', a.getText())
		text = a.getText()
		
		#Strip Unicode text out by encoding bytes with ascii and "ignore" errors, then re-encode it back to text
		textEnc = text.encode("ascii", "ignore")
		textCleaned = textEnc.decode()
		listOfGames.append({'URL' : a['href'],'Name' : textCleaned, 'Page' : str(pageNumber)})
		
	#for element in listContents:
	#	href = element.find('ul', class_='lcp_catlist')
	return listOfGames
#print(soup.prettify())

#Try to open CSV for writing, error if fails
try:
	myFile = open('FitgirlToCSV_Output.csv', 'w', newline='')
except PermissionError:
	print('Could not open FitgirlToCSV_Output.csv for writing, exiting...')
	sys.exit(1)
	
if myFile.writable():
	print('Confirmed FitgirlToCSV_Output.csv is writable, continuing...')
else:
	print('Could not open FitgirlToCSV_Output.csv for writing, exiting...')
	sys.exit(1)

#get total page numbers
totalPages = getPageNumbers()

#Make actual list of games, put into a list of dicts
gameList = []
for i in range(1,totalPages):
	gameList.extend(getPageGameList(i))
	#Sleep at least *some* time between requesting pages...
	time.sleep(0.25)
#for i in range(1,totalPages)
#print(gameList)

#write list of dicts to CSV
writer = csv.DictWriter(myFile, fieldnames=['Name', 'URL', 'Page'])
writer.writeheader()
writer.writerows(gameList)
myFile.close()
