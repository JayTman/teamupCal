from teamupNew import *
from dateutil.relativedelta import relativedelta
import sys
import getopt
import datetime as dt
from dateutil.parser import parse
import string
from urllib.parse import quote_plus
from urllib.parse import quote
import textwrap
from copy import deepcopy

# HEADERS = {'Teamup-Token': APIkey}

# get the calendar in use

leaders = []
scrollPosition = 0
# Where message from ride leader is stored
dataDir = "data/"

# Add to google or iCalendar buttons
#
def calButtons(calendar,ride,  buttons):
    # get time and date into format that google likes
    p= parse(ride['start_dt'])
    tz = dt.datetime.strftime(p, '%z') 
    print("tz is", tz)
    if tz == "":
        tz = 0
    else:
        tz = int(dt.datetime.strftime(p, '%z')[:3])

    p = p - relativedelta(hours=+tz)
    sdate = dt.datetime.strftime(p,'%Y%m%dT%H%M00Z')
    p= parse(ride['end_dt'])
    p = p - relativedelta(hours=+tz)
    edate = dt.datetime.strftime(p,'%Y%m%dT%H%M00Z')
    gcal = "https://calendar.google.com/calendar/r/eventedit?sprop=website:www.teamup.com"
    gcal += "&text=" + quote_plus(str(ride['title'])) + "&dates=" + sdate + "/"
    gcal += edate
    gcal += "&location=" + quote_plus(str(ride['location'])) + "&details=" + quote(str(ride['notes']))
    gcal += "a&sf=True"

     
    googleButton = "<div style=-wrap:wrap;><a href='" + gcal + "' target='_blank' rel='noreferrer noopener external' style=margin-left:5px>"
    googleButton += "<img src='https://ebcrides.org/images/cal/google-calendar.png' alt=''></a>"

    iCalButton = "<a href='https://teamup.com/" + calendar + "/events/" + ride['id'] + ".ics' download='EBC_Ride'>"
    iCalButton += "<img src='https://ebcrides.org/images/cal/icalendar.png' alt='' style=margin-left:55px;></a>"
    buttons += "<h6 style=text-align:center>Press the button below to add this to your,</h6><br>" + googleButton + iCalButton 
    return(buttons)

index = 0
def yearButtons(calendar, ride, buttons, rideLeader):
    global index

    statusID, confirmID = customNameToID({'Status': ['Confirmed']})
    statusID, changeID = customNameToID({'Status': ['change']})
    COstatusID, coConfirmID = customNameToID({' Co Leader Status': ['Confirmed']})
    index += 1

    URL="'https://" + domain + "/confirm?cal=" + calendar
    URL += "&rideID=" + ride['id'] + "&rideLeader=" + quote(rideLeader)
    confirmButton = " <button type='button' onclick=\"setConfirm("
    confirmButton += URL + "', " + str(index) + ")\" "
    confirmButton += " class='button confirmButton'> Confirm</button>"

    changeButton = "<a href='https://" + domain + "//editRide?cal=" + calendar
    changeButton += "&rideID=" + ride['id'] + "&rideLeader=" + quote(rideLeader)

    chgPendingButton = changeButton + "&mode=REEDIT' class='button chgPendingButton'> Make more changes </a>"
    changeButton += "&mode=EDIT' + class='button changeButton'>Change Ride</a>"

    #RESPONSE = genReport('year', cal, rideLeader, emailAddr, msg)

    button2 = changeButton
    cname="card"

    if 'custom' in ride:
        print("status",  confirmID, changeID, ride['custom'][statusID])
        if confirmID  == ride['custom'][statusID]:
            cname = "card confirmCard"
        elif changeID  == ride['custom'][statusID]:
            button2 = chgPendingButton
            cname = "card chgCard"
        #     cname = "card confirmCard"
        # elif coConfirmID  in nested_lookup('statusID', custom):
        #     cname = "card confirmCard"
        # else:
        #     cname = "card "
        # for fieldID, valueID in ride['custom'].items():
        #     field, val = customIDToName({fieldID:valueID})
        #     if fuzzyCompare('status', field) == True:
        #         if fuzzyCompare('confirm', val[0]) == True:
        #             cname = "card confirmCard"
        #             break
        #         #elif fuzzyCompare('changes', val[0]) == True:
        #         #    button2 = emailRideButton

        #     else:
        #         cname = 'card'
        #     #else:
        #         #cname="card"
        #         #field, value = customNameToID({field:val}).popitem()
        #         #if field == "Co Leader Status" and value == "Confirmed" \
        #            #and cname == 'card':
        #             #cname="card halfConfirmCard"
    buttons += "  <div class='box " + cname + "' id='card" + str(index)+ "' >"
    if confirmID  == ride['custom'][statusID]:
        buttons += "<div class='confirmLabel'> This Ride Has Been Confirmed </div>"
    else:
        buttons += "<div   class='btn-group' id=btn"+ str(index) +"> "
        buttons +=  confirmButton
        buttons +=  button2 + "</div>"

    #text = textwrap.fill(text, 60)
    return(buttons)

def createHTMLHeader(htmlHeader):
    file = open("rideReport.css", "r")
    htmlHeader = file.read()
    htmlHeader += "<body>"
    return(htmlHeader)

def createRide(calendar, ride, report, rideLeader, sendEmail, mode):

    statusID, confirmID = customNameToID({'Status': ['Confirmed']})
    date = fromTeamupDate(ride['start_dt'])

    if mode == 'reminderMail':
        report = calButtons(calendar, ride, report)
    elif mode == 'year':
        # uncomment to skip confirmed rides
        #if ride['custom'][statusID] == confirmID:
        #    return(report)
        report = yearButtons(calendar, ride, report, rideLeader)
    elif mode == 'summaryMail':
        print("summary 1", ride['title'], ride['custom'][statusID])
        if ride['custom'][statusID] == confirmID:
            print("returning empty report")
            return(report)
        report += date + " " + ride['title'] + "<br />"
        return(report)


    #cal = getSubCalendars(calendar)
    report += "<h2>" + date + " " + ride['title'] + "<p id=custom>"
    if 'custom' in ride:
        coLeaderID, x = customNameToID({'Co Leader Name' : None})
        x, confirmID  = customNameToID({'Co Leader Status': ""})
        if coLeaderID in ride['custom']:
            report += "<br /> Co-leading with " + ride['who']
    report += "</h2>Start Location: " + ride['location']
    report += "<br /><br />Leader: " + ride['who'] + "<br />"


    if 'custom' in ride:
        #if distanceID in ride['custom']:
            #distance = ride['custom'][distanceID]
        #else:
            #distance = "Unknown"
        custom = list()
        statusID, confirmID = customNameToID({'Status': ['Confirmed']})
        for nameID, valueID in ride['custom'].items():
            name, val = customIDToName({nameID: valueID})
            if isinstance(val, list):
                value = ""
                for i in range(len(val)):
                    value += str(val[i]) + " "
            else:
                value = str(val)

            if nameID == statusID:
                continue
            report += name + value + "<br />"
        report += "<p> </p>"
    # t
    # Add ride description if it exists

    if ride['notes'] != None and ride['notes'] != "":
        report += "<small>" + ride['notes'] + "</small>"

    # convert from ID to Labels *
    if 'custom' in ride:
        for k, v in ride['custom'].items():
            if k.find("Status") > -1 and v.find("Confirm") == -1:
                email(report, rideLeader, ridesChair, "This upcoming ride hasn't been confirmed yet", sendEmail)

    buttons = ""
    report += calButtons(calendar,ride,  buttons)
    report += "</div></div>"
    return(report)

def genReport(mode, calendar, rideLeader, sendEmail=True, test=False):

    #
    # get the ride leaders and message from the
    # flat files

    file = open(dataDir + "rideReminder.msg", "r")
    reminderMessage = file.read()
    file.close()

    # figure out which date(s) to run
    # the report. If in Dec, run for next year.
    today = dt.date.today()
    if mode in ("year", "summaryMail", "list"):
        if today.month > 11:
            year = today.year + 1
        else:
            year = today.year
        startDate = dt.date(year, 1, 1)
        endDate = dt.date(year, 12, 31)

    #only for 1 month from today
    elif mode == "reminderMail":
        startDate = today + relativedelta(weeks=+4)
        endDate = today + relativedelta(weeks=+4, hours=+23, minutes=+59)
        #
        # if testing make sure I don't mess something up.
        if test == True:
            startDate = dt.date(2028, 3, 11)
            endDate = dt.date(2028, 3, 11)
            if sendEmail == True:
                sendEmail = "jaytwery@gmail.com"
    #if mode == 'year' and sendEmail != False:
        #mode = 'summaryMail'


    rides = getEvents(calendar, startDate, endDate)
    config = getConfig(calendar)
    cal = getSubCalendars(calendar)
    rides.sort(key=lambda rides: rides['start_dt'])


    report = ""
    count = 0
    coLeaderName, x = customNameToID({'Co Leader Name' : None})
    coLeaderStatusID, x = customNameToID({'Co Leader Status' : None})
    coLeaderPaceID, x = customNameToID({'Co Leader Pace' : None})
    for ride in rides:
        # skip rides without leaders and weekly rides
        if ride['who'] ==  "":
            continue
        if ride['rrule'].find('WEEKLY') >= 0:
            continue
        if mode == "reminderMail":
            rideLeader = ""
            report = ""
            p = parse(ride['start_dt'])
            sdate = dt.datetime.strftime(p, '%m/%d/%Y')
            p = parse(ride['end_dt'])
            edate = dt.datetime.strftime(p, '%m/%d/%Y')
            p = parse(ride['start_dt'])
            p = today + relativedelta(months=+1, minutes=+1)
            tdate = dt.datetime.strftime(startDate, '%m/%d/%Y')
            #
            # this will suppress reminders from going everyday for multi day
            # rides. It will just be sent on the first day.
            #
            if sdate != edate and sdate != tdate:
                continue

        if rideLeader == "":
            rideLeader = ride['who']
        date = dt.datetime.strftime(parse(ride['start_dt']), '%m/%d/%Y %H:%M')
        if ride['who'].lower() == rideLeader.lower():
            print("Reminder: ", date, " ", ride['title'])
            report  = createRide(calendar, ride, report, rideLeader, sendEmail, mode)
            buttons = ""
            count += 1

    #
    # No report genearted, nothing to send out.
    if len(report) == 0:
        return()
    if mode == 'reminderMail':
        HTMLHeader = ""
        HTMLHeader = createHTMLHeader(HTMLHeader)
        date = dt.datetime.strftime(parse(ride['start_dt']), '%m/%d/%Y')

        reportHeader= "<div display=flex style='margin:10px; justify-items:center'>"
        reportHeader += "<strong>h2>Hello " + rideLeader + ", <br /></h2>"
        report = HTMLHeader + reportHeader + reminderMessage + report
        sendTo = ""
        sendTo = addressBook(rideLeader)
        email(report, rideLeader, sendTo, "Reminder: upcoming EBC ride on " + date, sendEmail)

    if mode == 'year':
        reportHeader = "<heading id='head'; width=100%; style='margin:10px; text-align: left;'> <h4>Hello "
        reportHeader += rideLeader.split()[0] + ",<br /> "
        #reportHeader += "<a href='https://teamup.com/" + calendar + "?query=&quot;" + rideLeader + "&quot"
        #reportHeader += "' rel = 'noreferrer noopener external' target = '_blank' >Click here if you want to see all your rides displayed in the Calendar.</a>"
        #reportHeader += "<br />Below"
        #if count == 1:
        #    reportHeader += " is "
        #else:
        #    reportHeader += " are "
        #reportHeader += "your "  + str(count)
        #reportHeader += " your unconfirmed Rides for "
        #reportHeader += dt.datetime.strftime(parse(date), '%Y') + ".<br />"

        reportHeader += "Please acknowledge that you can lead the rides below by pressing the Confirm button for each ride.<br /></h4><small>"
        reportHeader += "<h4>If you need to make change, press the Change Ride button to send a message to the Rides Chair.<br /></h4><small>"
        reportHeader += "<heading id='head';>"
        HTMLHeader = ""
        HTMLHeader = createHTMLHeader(HTMLHeader)
        report = HTMLHeader + reportHeader + report
        report += "</small></div></body></html>"
      #  print("\nHEAD: " + header + "\nTEXT: " + reportHeader  )
        if __name__ == "__main__":
            print("AT MAIN PRINTING REPORT \n", report)
        else:
            return(report)

    elif mode == 'summaryMail':

        year =  dt.datetime.strftime(parse(date), '%Y')
        file = open(newYearMsg, "r")
        msg = file.read()
        file.close()
        cmd1 = "https://" + domain + "/year"
        ridesButton = "<h2><p><a href='" + cmd1 + "?cal=" + calendar
        ridesButton += "&rideLeader=" + quote_plus(rideLeader) + "'>"
        ridesButton += ""
        ridesButton += "<img src='http://ebcrides.org/images/cal/button_review_rides.png' alt='Review Rides'></a><p>"
        reportHeader = "<html><div style='padding:10px; font-size:12px;'><h2> Hello "

        if rideLeader.find('&') == -1 and rideLeader.find('/') == -1:
            reportHeader += rideLeader.split()[0]
        else:

            reportHeader += rideLeader + "</h2>"

        reportHeader +=  ",<br /> " + msg
        reportHeader +="  <br />" + ridesButton + "<h5>"
        reportHeader += "Below are your Pending Rides for "  + year + ":<br /> <br />"
        HTMLHeader = ""
        HTMLHeader = createHTMLHeader(HTMLHeader)
        report = HTMLHeader + reportHeader + report + "</h5></div></body></html>"
        sendTo = ""
        sendTo = addressBook(rideLeader)
        print("summary mail ", sendTo, " Ride Leader ", rideLeader)
        email(report, rideLeader, sendTo, "Your EBC Scheduled Rides for "  + year, sendEmail)



def main(argv):
    month = ''
    year = 0
    sendYear = False
    mode = "reminderMail"
    calendar = ""
    rideLeader = ""
    sendEmail = False
    test = False
    try:
        opts, args = getopt.gnu_getopt(argv, "er s: t  y: c:")
    except getopt.GetoptError:
        print (argv[0], '-y)ear_mode \"RideLeader Name\" [-r)eminder_mode -s)ummary mail message -e)mail Email address override')
        sys.exit(2)
    argCount = 0
    for opt, arg in opts:
        if  arg == '':
            argCount += 1
        else:
            argCount += 2
        if opt in ("-e"):
            sendEmail = True
        elif opt in ("-r"):
            mode = "reminderMail"
        elif opt in ("-c"):
            calendar = arg
        elif opt in ("-t"):
            test = True
        elif opt in ("-s"):
            mode = "summaryMail"
            if arg != '':
                rideLeader = str(arg)
        elif opt in ("-y"):
            mode = "year"
            rideLeader = arg

    for i in range(argCount):
        argv.pop(0)

    if calendar == "":
        calendar = calendarPicker("Pick a Calender")
    # endDate = startDate
    #    startDate = dt.datetime.strftime(startDate, '%Y-%m-%d')
    #    endDate = dt.datetime.strftime(endDate, '%Y-%m-%d')
    #    startDate = toTeamupDate(startDate)
    #    endDate = toTeamupDate(endDate)

    if len(argv) == 1:
        if   sendEmail == True:
            sendEmail = argv[0]
        else:
            rideLeader = argv[0]

    if mode != "summaryMail":
        report = genReport(mode, calendar, rideLeader, sendEmail, test)
        exit(0)

    # beginning of year summary email
    # if ride leader is set, just email that ride leader
    if mode == "summaryMail":
        if isinstance(rideLeader, str) == True:
            genReport(mode, calendar, rideLeader, sendEmail, test)
            exit()
        #
        # otherwise make a list of ride leaders by looping through
        # all the rides.
        leaderList = list()
        today = dt.date.today()
        startDate = dt.date(today.year, 1, 1)
        endDate = dt.date(today.year, 12, 31)
        rides = getEvents(calendar, startDate, endDate)
        for ride in rides:
            if ride['who'] != "":
                if ride['who'] in leaderList:
                    continue
            leaderList.append(ride['who'])
        #Now send out a summary of rides
        # to every ride leader.
        for i in range (len(leaderList)):
            genReport(mode, calendar, leaderList[i], sendEmail, test)





if __name__ == "__main__":
    main(sys.argv[1:])
