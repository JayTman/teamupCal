import urllib
from teamupNew import *
from editRide import editRide, updateRideChanges, saveRideChanges
from newYear import  resetNewYear, newYear
from rideReport2 import genReport
from updateRideStatus import updateRideStatus
from urllib.parse import unquote, quote_plus
import time
import json
import os
from teamupNew import email
from overrides import *
import re

def msgBroker(environ, start_response):

    start_response('200 OK', [('Content-Type', 'text/html')])##
    path=environ['PATH_INFO']
    if 'JAY' not in environ:
        rawArgs=environ['QUERY_STRING']
        args=urllib.parse.parse_qsl(rawArgs)
    else:
        args=environ['JAY']

    if path[-1] == "/":
        path = path[:-1] 

    msgID=None
    msg="None"
    path = path[1:]
    print("EVENT path:", path, "args:", rawArgs, "parsed args:", args)
    for arg in args:
        if arg[0] == 'msgID':
            msgID=arg[1].replace(' ', '')
        elif arg[0] == 'cal':
            cal=arg[1].replace(' ', '')
            print("cal: ", cal)
            cal = re.sub('\W','', cal)
            print("cal: ", cal)
        elif arg[0] == 'rideID':
            id=arg[1].replace(' ', '')
        elif arg[0] == 'id':
            id=arg[1].replace(' ', '')
        elif arg[0] == 'title':
            title=arg[1]
        elif arg[0] == 'location':
            location=arg[1]
        elif arg[0] == 'rideLeader':
            rideLeader=arg[1]
        elif arg[0] == 'who':
            rideLeader=arg[1]
        elif arg[0] == 'emailAddr':
            emailAddr=unquote(arg[1])
        elif arg[0] == 'msg':
            msg=arg[1]
        elif arg[0] == 'notes':
            notes=arg[1]
    #    elif arg[0] == 'nextYear':
     #       nextYear=arg[1]
        elif arg[0] == 'mode':
            mode=arg[1]
        elif arg[0] == 'start_dt':
            start_dt=arg[1]
        elif arg[0] == 'nextYear':
            nextYear=arg[1]
        else:
            function='invalid argument'

    #cal=args2[1][1]
    #rideID=args2[2][1]
    #leader= args2[3][1]

    test=False
    print("path ", path, "msgiD ", msgID)
    if path == 'msgBroker':
        function=msgID
    else:
        function=path
    print(" TIME 0 ", time.time(), "function ", function)
        #add calendar
    if function  in('pending', 'changes', 'confirm'):
        print(" TIME 1 ", time.time())
        response = updateRideStatus( function, cal, id, rideLeader)
        emailAddr = False
        print(" TIME 2 ", time.time())
        if function == 'changes':
            response = editRide(cal, id)
        else:
            url="/year?&cal=" + cal + "&rideLeader=" + rideLeader
            response = "<script> window.location.href='" + url +"';  </script>"
            #response = genReport('year', cal, rideLeader, emailAddr, test)
        print(" TIME 3 http: ", time.time())
    elif function  == 'editRide':
        response = editRide(cal, id, mode, msg)
    elif function  == 'summaryMail':
        print(" TIME 4 ", time.time())
        # otherwise make a list of ride leaders by looping through
        # all the rides.
        if rideLeader == "all":
            leaderList = list()
            today = dt.date.today()
            startDate = dt.date(today.year, 1, 1)
            endDate = dt.date(today.year, 12, 31)
            rides = getEvents(cal, startDate, endDate)
            rides.sort(key=lambda rides: rides['who'])
            for ride in rides:
                if ride['who'] == "":
                    continue
                if ride['who'].find("/") > -1:
                    ride['who'] = ride['who'].split("/")[1]
                if ride['who'].find("&") > -1:
                    ride['who'] = ride['who'].split("&")[1]
                if ride['who'] in leaderList:
                    continue
                if ride['who'] == "":
                    continue
                leaderList.append(ride['who'])
                #Now send out a summary of rides
                # to every ride leader.
            for i in range (len(leaderList)):
                emailAddr = addressBook(leaderList[i])
                genReport('summaryMail', cal, leaderList[i],emailAddr , test)
                i += 1
        else:
            emailAddr=addressBook(rideLeader)
            response = genReport('summaryMail', cal, rideLeader, emailAddr, test)
        url = " /newYear?cal=" + cal 
        response = "<script> window.location.href='" + url +"';  </script>"
            # response = newYear( cal)
    elif function == "testme":
        response = 'Request method: %s' % environ['REQUEST_METHOD']
        for x in environ:
            response += "<b>" + str(x) + ":</b> "
            response += str(environ[x])  + "<br>"
    elif function == "login":
        file = webDir + "/login/login.php"
        with open(file, 'r') as reader:
            response=reader.read()
    elif function == "emailRideLeader":
        print(msg)
        print(response)
        response = genReport('year', cal, rideLeader, emailAddr, test)
        print(" TIME 5 ", time.time())
    elif function == "newYear":
        response = newYear( cal)
        print(" TIME 5 ", time.time())
    elif function in ("lockPending", "unlockPending"):
        file = open(resetLockFile, "w")
        file.write("01/01/" + nextYear)
        file.close()
        response = newYear( cal)
    elif function == "resetNewYear":
        resetNewYear(cal, nextYear, msg)
        url = "/newYear?cal=" + cal 
        #response = newYear( cal)
        response = "<script> window.location.href='" + url + " ';  </script>"
        #response = newYear( cal)
#        response = "<script> window.location.href='" + url +"';  </script>"
#        response = "<script> \"loadDoc(" + url + ", myfurnction1()\";  </script>"
    elif function  == 'saveRideChanges':
        print("cal", cal, "id", id)
        saveRideChanges(cal, args, id)
        response = newYear( cal)
        response = "<script> window.location.href='/newYear?cal=" + cal  + "';  </script>"

    elif function  == 'updateRideChanges':
        response = updateRideChanges(cal, args, id)
        emailAddr = False
        url = " year?cal=" + cal 
        url += "&rideLeader=" + quote_plus(rideLeader) 
        response = "<script> window.location.href='" + url +"';  </script>"
        # response = genReport('year', cal, rideLeader, emailAddr, test)

    elif function  == 'ISCfile':
        response = updateRideChanges(cal, args, id)
        emailAddr = False
        url = " year?cal=" + cal 
        url += "&rideLeader=" + quote_plus(rideLeader) 
        response = "<script> window.location.href='" + url +"';  </script>"
        # response = genReport('year', cal, rideLeader, emailAddr, test)

    elif function == 'year':
        emailAddr = False
        #add calendar
        print("AT YEAR")
        print(" TIME 6 ", time.time())
        response = genReport(function, cal, rideLeader, emailAddr, test)
        print(" TIME 7 ", time.time())
    elif function == 'yearMail':
        #add calendar
        response = genReport(function, cal, rideLeader, emailAddr, test)
    elif function == "rideReport":
        function = year
        emailAddr = None
        response = genReport(function, cal, rideLeader, emailAddr, test)
    elif function == "text":
        print("args are: ", args)
        response = "<h2> text args=" + str(args)  +  "</h2>"
    elif function == "":
        file = webDir + "/matrix.php"
        with open(file, 'r') as reader:
            response=reader.read()
    else:
        response = """
   <br /> <br /><h1><em></em><strong>Sorry<a href="https://ebcrides.org/browser/upload/oops.jpg" target="_blank" rel="noopener"><img src="https://ebcrides.org/browser/upload/oops.jpg" style="float: left;" /></a>, Something's gone wrong.</strong></h1>
   <p><strong></strong></p>
        """        
        response +="<h4> The action causing the problem is: " + str(function) + "<br /> The parameters are: " + str(args)

    print(" TIME 8 ", time.time())
    ajax = """
            <script>
            function setConfirm(url, index) {
                var xhttp;
                var name = "card" + index;
                var x = document.getElementById(name);
                //alert(url);
                x.style.background = '#33DD00';
                name = "btn" + index;
                var x = document.getElementById(name);
                x.classList.toggle('confirmLabel');
                x.innerHTML = 'This Ride Has Been Confirmed';
                xhttp=new XMLHttpRequest();
                xhttp.open("GET", url, true);
                xhttp.send();
             }
            </script>
         <script>
            function loadDoc(url, cFunction) {
                var xhttp;

                xhttp=new XMLHttpRequest();
               alert(url)
                      cFunction(this, index);

                 xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                    }
                 };
              xhttp.open("GET", url, true);
              alert("three")
                xhttp.send();
                 }
             function myFunction1(xhttp) {
                }

      </script>
    """
    response +=  ajax
    if response:
        return [response.encode()]
    else:
        return("")

    return [response.encode()]

"""
    case "leaderlesReport": // generate a report of leaderless rides
        $pgm = "ridesWithoutLeaders.py -y 2019";
        break;

    case "addLeader":  // set a ride to a new ride leader
        $who=$_GET['who'];
        $pgm="updateRideLeader.py" . " ". $cal. " " . $id . "  '" . $who . "'";
        break;
    """



