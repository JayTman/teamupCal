#
import getopt
import json
import sys
import requests
import glob
#from urllib.parse import quote
#from urllib.parse import unquote
import smtplib
import ssl
import textwrap
from nested_lookup import nested_update, nested_delete, nested_lookup
import time
import datetime as dt
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import string
import csv

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#
# Teamup required
APIkey = "ca3fec0bc53190c90863e0f41579e27cbc98a57a97c909455df7db816f4ae4bd"
URL = 'https://api.teamup.com/'
PASSWORD_HEADERS = { 'Teamup-Password': 'ebc123'}
HEADERS = {'Teamup-Token': APIkey}
UPDATE_HEADERS = {'Teamup-Token': APIkey, 'Content-type': "application/json"}
PASSWORD_HEADERS.update(UPDATE_HEADERS)
#UPDATE_HEADERS=HEADERS
#UPDATE_HEADERS.update(PASSWORD_HEADER)
# Default address for calendar contact andproblems
ridesChair = "RidesChair@evanstonbikeclub.org"
domain="python.ebcrides.org/one"
domain="localhost"
#HEADERS = PASSWORD_HEADERS
# Calendar IDs
#

CALENDAR_NAMES = {'EBCrides': "ksdtrd981nepm3brj9",
                  'EBCridesModify': "ksexyuw3mwu79svgv4",
                  'New Year Reset' : "ksgkg9m8bdrd3or989",
                  'EBCridesReadOnly': "ks4f2ityp82zqj3zsh",
                  'jaysRideSchedule': "ksbmqapicnorxb63e1",
                  "test102019" : 'ks7rk5fy11z3ovyjeu',
                  'test105 ' : 'ks1fczxewt1dru3yub',
                  'test1210 ' : 'ksh4yxa25bfs5er66d',
                  'test1119': "ksyvj5y44uay12qu34"
                  }


def calendarPicker(heading):
    i = 0
    print(heading)

    cals  = sorted(CALENDAR_NAMES.items())
    while True:
        print ("{:^3s} {:^20s} {:^20s} ". \
               format("#", "Name", "ID" ))
        for entry in enumerate(cals):
            print ("{:2d}. {:20s} {:20s} ". \
                   format(entry[0], entry[1][0], entry[1][1]))
        i = int(input("Enter calendar number: "))

        if i < len(CALENDAR_NAMES):
            return(cals[i][1])
        else:
            print("Invalid choice: " + str(i) + ", try again.")

def filePicker(heading, pattern):
    cals = list(glob.iglob(pattern))
    while True:
        for entry in enumerate(cals):
            print ("{:2d}. {:20s}". \
                  format(entry[0], entry[1]))
        i = int(input("Enter file number: "))
        if len(cals) == 0:
            return(None)
        if i < len(cals):
            return(cals[i])
        else:
            print("Invalid choice: " + str(i) + ", try again.")

def calIDToName(calID):
    for name, id in CALENDAR_NAMES.items():
        if id == calID:
            return (name)
    s = calID + " Not Found"
    print(s)
    return(None)



def calNameToID(calName):
    if calName in CALENDAR_NAMES:
        return(CALENDAR_NAMES.get(calName))
    else:
        s = calName + " Not Found"
        print(s)
        return(None)


def getConfig(calendar):
    params = ""
    contentType = 'configuration'
    results = queryTeamup(HEADERS, calendar, 'get', contentType, params, {})

    if isinstance(results, str):
        return(results)

    return (results[contentType])


#
# THese are the ride catagories
#
def getSubCalendars(calendar):
    params = ""
    contentType = 'subcalendars'
    results = queryTeamup(HEADERS, calendar, 'get', contentType, params, {})
    if isinstance(results, str):
        print("Error getting subcalendars: " + results)
        exit()
    return (results[contentType])


#
# get all events
#
customDef = dict()
def initCustomDef(calendar):
    global customDef
    if len(customDef) == 0:
        config = getConfig(calendar)
        customDef = config['fields']['definitions']

def createCustomFields(toCal, fileConfig):
    global  customDef

    match = False
    i = 0
    j = 0
    params=""
    update = False
    while i < len(fileConfig):
        fieldID = fileConfig[i]['id']
        fieldName = fileConfig[i]['name']
        config = fileConfig[i]
        if fieldID.find("built") > -1:
            i+=1
            continue
        j=0
        while j < len(customDef):
            toName = customDef[j]['name']
            toID = customDef[j]['id']
            if toName == fieldName:
                config['id'] = toID
                results = queryTeamup(UPDATE_HEADERS, toCal, 'put', 'field-definitions/', toID, config)
                update=True
                if isinstance(results, str):
                    print(results)

                j+=1
                break
            j+=1
        i += 1
        if update == True:
            update = False
            continue
        results = queryTeamup(UPDATE_HEADERS, toCal, 'post', 'field-definitions', params, config)

    i = 0
    j = 0
    params=""
    update = False
    while i < len(fileConfig):
        fieldID = fileConfig[i]['id']
        fieldName = fileConfig[i]['name']
        config = fileConfig[i]
        while j < len(customDef):
            toName = customDef[j]['name']
            toID = customDef[j]['id']
            if toName not in nested_lookup('name', customDef):
                j += 1
                continue
            swap = False
            if fieldID.find("built") > -1:
                if toID != fieldID:
                    swap = True
                elif toName != fieldName:
                    results = queryTeamup(UPDATE_HEADERS, toCal, 'put', 'field-definitions/', toID, config)

            if fieldID.find("built")  == -1:
                if toName != fieldName:
                    swap = True
            if swap == True:
                swap = False
                i = 0
                j = 0
                results = queryTeamup(UPDATE_HEADERS, toCal, 'post', 'field-definitions/',fieldID + "/swapWith/" + toID , "")
                if isinstance(results, str):
                    print(i, " ",  j, " " , fieldID, " ", results)
                if 'definitions' not in results:
                    print ("Error: no definiions found")
                    return()
                customDef = results['definitions']
                break
            else:
                i += 1
                j += 1
                break






def getEvents(calendar, startDate, endDate):
    #
    # initailize custom fields
    initCustomDef(calendar)

    if isinstance(startDate, str):
        start = startDate
    else:
        start = dt.datetime.strftime(startDate, '%Y-%m-%d')
    if isinstance(endDate, str):
        end = endDate
    else:
        end = dt.datetime.strftime(endDate, '%Y-%m-%d')

    params = '?startDate=' + start + '&endDate=' + end

    DEBUG = 0
    data = {}
    contentType = 'events'
    results = queryTeamup(HEADERS, calendar, 'get', 'events', params, data)
    if len(results.get(contentType)) >= 0:
        return (results[contentType])
    elif results.get('error'):
        return (results['error'])
    else:
        # zero rows returned
        print("Unexpect query results ", results)
        exit()

#
# Get one event
#

def deleteEvent(calendar, eventID, version):
    params = '/' + eventID + "?version=" + version + "&redit=all"
    DEBUG = 0
    data = {}
    results = queryTeamup(HEADERS, calendar, 'delete', 'events', params, data)
    if  isinstance(results, str)  and results.find("200") > -1:
        return ("Success")
    else:
        print("Unexpect query results in deleteEvent", results)
        exit()

def getEvent(calendar, eventID):
    params = '/' + eventID
    DEBUG = 0
    data = {}
    results = queryTeamup(HEADERS, calendar, 'get', 'events', params, data)
    if not isinstance(results, str):
        return (results['event'])
    else:
        print("Event not found getEvent", results)
        #exit(-1)


def updateEvent(calendar, event):
    if event['id'].find("rid") >= 0:
        # + "?format=html&inputFormat=html
        params = '/' + event['id'].partition('-rid-')[2]
    else:
        params = '/' + event['id']
    #print(json.dumps(event, indent=4))
    results = queryTeamup(UPDATE_HEADERS, calendar,
                          'put', 'events', params, event)
    if isinstance(results, str):
        print("ERROR, event not found")
    return(results)


def fuzzyCompare(name1, name2):
    if name1 == "":
        return False
    import re
    chars=":|!|.|?|(|)|,|;"
    chars=":|!|.|?|(|)|,"

    nm1 = (name1.upper()).strip()
    nm1 = re.sub(":|!", "", nm1)
    nm2 = (name2.upper()).strip()
    nm2 = re.sub(":|!", "", nm2)
    if  nm2.find(nm1) > -1:
    #if  (name2.upper().strip()).find((name1.upper().strip())) > -1:
    #if name1 == name2:
        return True
    else:
        return False

custom = dict()
def customNameToID(customNames, definitions=None):
    global customDef
    global custom
    if definitions == None:
        definitions = customDef

    def id(name,x):
        ids = nested_lookup('id', x,)
        names = nested_lookup('name', x)
        z = 0
        while z < len(names):
            #if  (name[z].upper().strip()).find((name.upper().strip())) > -1:
            if fuzzyCompare(name, names[z]) == True:
                return(ids[z])
            z += 1

    for fieldName, valueName in customNames.items():
        fieldID = None
        for row in iter(definitions):
            if row['active'] == False or row['name'] == "":
                continue
            if fuzzyCompare(fieldName, row['name'] ) == False:
            #if (row['name'].strip()).upper().find(nm) == -1:
                continue
            fieldID = row['id']
            break;

        # fieldID should be defined here
        if fieldID == None:
            print("\twarning: couldn't find ", fieldName, " in definitions ")
            x = zip(['id', 'name', 'active', 'type'], ['notfound', fieldName,  True, 'single_line_text'])
            definitions.append(dict(x))
            return(None, fieldName)

        if row['type'] == "single_line_text":
            custom.update({ fieldID: valueName})
            return(fieldID, valueName)
        #
        # only one name passed in
        if valueName == None:
            return(fieldID,  None)

        options = nested_lookup('options', row, wild=True)
        if isinstance(valueName, list):
            i = 0
            valueID = list()
            while i < len(valueName):
                nm = id(valueName[i], options)
                valueID.append(nm)
                #print(name(ID[i], options))
                i += 1
        else:
            valueID = id(valueName, options)
            #print("Val:" , ID)
        custom.update({fieldID : valueID})
        return(fieldID, valueID)

def customIDToName(customIDs, definitions=None):
    global customDef
    if definitions == None:
        definitions = customDef

    global custom

    def name(id, x):
        ids = nested_lookup('id', x)
        name = nested_lookup('name', x)
        z = 0
        if id == 'choices':
            return(name)
        for z in range(len(ids)):
            if  ids[z] == id:
                return(name[z])


    custom.clear()
    if customIDs == None:
        return({})
    for fieldID, valueID in customIDs.items():
        if fieldID == None:
            return([None, None])
        #print(fieldID, " ", valueID)
        for row in iter(definitions):
            fieldName = None
            if row['id'] != fieldID:
                continue
            fieldName = name(fieldID, row)
            break
        if fieldName == None:
            print("Couldn't find fieldID: ", fieldID, "in Definitions:")
            definitions.update({'id': fieldID},{'name': "Not Found"})
            return([fieldID,valueID])

        if valueID == []:
            valueName = []
        elif isinstance(valueID, list):
            valueName = list()
            options = nested_lookup('options', row, wild=True)
            for i in range(len(valueID)):
                nm = name(valueID[i], options)
                #print(nm, valueID[i])
                valueName.append(nm)
        elif row['type'] == "single_line_text":
            valueName = valueID
        else:
            valueName = name(valueID, None)
        #custom[fieldName] = valueName
    return([fieldName, valueName])

def customValueToName(customID, matchName=None, definitions=None):
    x, valueName = customIDToName(customID, definitions).popitem()
    if matchName == None:
        return(valueName)
    else:
        if isinstance(valueName, list):
            for i in range(len(valueName)):
                if (matchName.strip()).upper() == (valueName[i].strip()).upper():
                    return(True)
        elif (matchName.strip()).upper() == (valueName.strip()).upper():
                return(True)
        return(False)


def getFields(calendar):

    DEBUG = 0


    params = ""
    data = {}
    contentType = 'field-definitions'
    results = queryTeamup(HEADERS, calendar, 'get', contentType, "", data)
    contentType = 'definitions'
    if isinstance(results, str):
       print("Unexpect query results getting field definitions", results)
       exit(1)
    elif results.get(contentType):
        return (results[contentType])
    else:
        results.get('error')
        return (results['error'])


def queryTeamup(headers, calendar, oper, contentType, params, data):
    if oper == 'get':
        url = URL + calendar + '/' + contentType + str(params)
#        print("url", url)
        params = ""
    #
    # data=json.dumps(data)????
    #
        response = requests.get(
            url=url, headers=headers, params=params, data=data)
    elif oper == 'delete':
        if data != "":
            params=params + "/"
        url = URL + calendar + '/' + contentType + params +  data
        response = requests.delete(url=url, headers=headers)
    elif oper == 'post':
        url = URL + calendar + '/' + str(contentType) + str(params)
        response = requests.post(
            url=url, headers=headers, data=json.dumps(data))
    elif oper == 'put':
        url = URL + calendar + '/' + str(contentType) + str(params)
    # params = ""
    #
    # url=url????
    #
        #print(url, " headers", headers)
        response = requests.put(url=url, headers=headers, data=json.dumps(data))
    else:
        response.status_code = -1
        response.text = "ERROR: Invaled operation request: " + oper

    if response.status_code > 300:
        results = "Error: " + str(response.status_code) + " " + response.reason
        return(results)
    if oper != 'delete':
        if sys.version_info[0] == 3 and sys.version_info[1] < 6:
            results = json.loads(response.text)
        else:
            results = json.loads(response.content)
    else:
        results = str(response.status_code) + ". " + response.reason
    return(results)

# probably out of scope?


def createEmptyObj(obj, new):
    new = fileEvent.copy()
    for k in new.keys():
        new[k] = None
    return(new)


results = list()


def printEvent(d, k):
    results = keyValue(d, k)
    results = str(results)
    results = results.replace("[", "")
    results = results.replace("]", "")
    results = results.replace("'", "")
    print(results)
    return(results)


def printKeyValue(data, keyNames, endStr=""):
    printEvent(data, keyNames)


debug = 0


def keyValue(data, keyNames):
    ret = []
    ret.clear()
    st = str()

    def keyValue2(data, keyNames):
        if isinstance(data, list):
            for i in data:
                if debug:
                    print("one ", i)
                keyValue2(i, keyNames)
        elif isinstance(data, dict):
            for i, j in data.items():
                if isinstance(j, dict):
                    if debug:
                        print("2. i:", i, "j: ")
                    keyValue2(j, keyNames)
                if keyNames == i:
                    if debug:
                        print("3. keyNames ", keyNames, "i: ", i)
                        exit(1)
                    if isinstance(data[i], str):
                        s = data[i].encode('ascii', 'ignore')
                        data[i] = s.decode()
                    ret.append(data[i])
                    return(ret)

    if isinstance(keyNames, set):
        for key in keyNames:
            keyValue2(data, key)
        # return(ret)
    else:
        keyValue2(data, keyNames)
    if len(ret) == 1:
        return(ret[0])
    return(ret)


def fromTeamupDate(date):
    d = parse(date)
    if d.minute == 0 and d.hour == 0:
        rdate = dt.datetime.strftime(d, '%m/%d/%Y')
    else:
        rdate = dt.datetime.strftime(d, '%m/%d/%Y %H:%M')
    return(rdate)


def toTeamupDate(date):
    p = parse(date)
    tdate = str(dt.datetime.strftime(p, '%Y-%m-%dT%H:%M:%S'))
    return(tdate)



def id2name(calendars, i=0):
    if isinstance(i, str):
        id = int(i.partition("-rid'")[2])
    for cal in calendars:
        #     for key in cal:
        if cal['id'] == i:
            return (cal['name'])
    return ("calendar id ", i, " not found")



def subCalNameToID(calendars, name):
    for cal in calendars:
        if cal['name'] == name:
            return (cal['id'])
    return (-1)


def subCalIDToName(calendars, id):
    for cal in calendars:
        if cal['id'] == id:
            return (cal['name'])
    return (-1)


def tuTime(date):
    dt.datetime.strftime('%H=%m-%s')
    return(date.split('T')[0][0:8])


def tuDate(date):
    date = dt.datetime.strftime(date, '%Y-%m-%d')
    return(date)


leaders = list()
rideLeaderFile="data/rideLeaders.csv"
def getRideLeaders():
    global leaders
    with open(rideLeaderFile, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        i = 0
        for row in reader:
            leaders.append(dict(row))
        csvfile.close()

def addressBook(rideLeader):
    global leaders

    if len(leaders) == 0:
        getRideLeaders()

    sendTo = None
    # only one name on ride, set it to be the last name wih ??? as the first naem
    if len(rideLeader.split()) < 1:
        rideLeader = "??? ???"
    elif len(rideLeader.split()) < 2:
        rideLeader = "??? " + rideLeader
    #while True:
    # first check for a match on first and last name in the ride leaders file
    first = rideLeader.split()[0].lower()
    last = rideLeader.split()[1].lower()
    names = []
    emailAddr = ridesChair
    for row in leaders:
        if row['Last'].lower() == last:
            names.append(row)

    if len(names) == 0:
        msg = "Ride Leader Name not found in email address list for: " + first + " " + last
    else:
        for row in names:
            if row['First'].lower() == first:
                emailAddr = row['email']
        if emailAddr == ridesChair:
            msg = "No match for ride leaders first Name in Club Express for: " + first + " " + last
            msg += "<br> You should probably change it to what Club Express uses: " + row['First'] + " " + row['Last']

    return(emailAddr)


def email(body, Name, toAddr, subject, sendEmail=True):
    text = str()

    print("mail:", subject, "to ", toAddr)
    cal2 = "caladmin@ebcrides.org"
    ebc = "ebcride1@ebcrides.org"
    fromAddr = ridesChair
    if sendEmail == True:
        sendMailToAddr = toAddr
    else:
        sendMailToAddr = sendEmail

    i = 0
    SMTPlogin = "ebcrides"
    #SMTPpass = "EBC55555cal"
    SMTPpass = "MkGM74@eLW"
    #
    # port 465 = SSL, port 587 =TTL
    #
    # strip out non ascii characters values
    i = 0
    string = str()
    if not isinstance(body, str):
        while i < len(body):
            string = body[i].encode('ascii', 'ignore')
            string = string.expandtabs(4)
            text += string.decode()
            i += 1
    else:
         text += body
    text = textwrap.fill(text, 69)
    if sendEmail == False:
        print(text)
        return()
#    server = smtplib.SMTP_SSL("az1-ss8.a2hosting.com", 465)
#    server = smtplib.SMTP_SSL("s2.fcomet.com", 465)
    server = smtplib.SMTP_SSL("mail.ebcrides.org", 465)
 #   server.starttls()

    msg = MIMEMultipart()
    msg.attach(MIMEText(text, 'html'))
    msg['From'] = fromAddr
    msg['To'] = toAddr
    msg['Subject'] = subject
    server.ehlo()
    text = msg.as_string()
    server.login(SMTPlogin, SMTPpass)

   # print(MIMEText(text, 'html'))
   # toAddr = toAddr.split(",")
   # sendMailToAddr = "wittto@comcast.net"
   # if toAddr != rideschair:
   #     sendMailToAddr = "HeelanWill@gmail.com"
   # else: 
   # sendMailToAddr = rideschair
    

   # print("rideschair: ", rideschair)
    sendMailToAddr = "jaytwery@ebcrides.org"
    print("sending to...", sendMailToAddr)
    server.sendmail(fromAddr, sendMailToAddr, text)
    server.quit()
    return(0)


def restoreSubCals(liveSubCalendars, fileEvent):

    id = subCalNameToID(liveSubCalendars, fileEvent['subcalendar_id'])
    if id == -1:
            #
            # if not found, need to set it to something...
        print("\tWarning: ", fileEvent['subcalendar_id'], ' not found, setting to ', liveSubCalendars[0]['name'], ".")
        id = liveSubCalendars[0]['id']
    fileEvent['subcalendar_id'] = id
    subcals = fileEvent['subcalendar_ids']

    # make a list of subcalendars this ride is part of
    #
    ids = list()
    for subCalendar in subcals:
        id = subCalNameToID(liveSubCalendars, subCalendar)
        if id == -1:
         #   if debug:
        #        print("removing ", subCalendar, end=" ")
            continue
#           print("\n\t subcalendar list changed", x, " to numbercal ", id, end=" ")
        ids.append(id)
    fileEvent['subcalendar_ids'] = ids
    if isinstance(fileEvent['subcalendar_id'], str):
        print('ERROR: this shoudnot happen skipping, ',
              fileEvent['subcalendar_id'], ' should not be a string.')
        exit()


#
# end function
from overrides import *

