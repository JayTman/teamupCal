from teamupNew import *
import datetime as dt
from dateutil.parser import parse
#from urllib.parse import quote
import os
#colheading <background:gold; color:green}

def resetNewYear(calendar, nextYear, msg = ""):
    today = dt.date.today()
    month = today.month
    day = today.day

    lastYear = int(nextYear) - 1
    print("YEARS" , lastYear,"  ",  nextYear)
        #  if repeat is yearly disconnect from pattern
    # disconnect perevious year
    startDate = dt.date(lastYear, 1, 1)
    endDate = dt.date(lastYear, 12, 31)
    events = getEvents(calendar, startDate, endDate)
    for event in events:
        if event['rrule'].find('YEAR') > -1:
            print("ungrouping: ", event['start_dt'], " " , event['title'])
            if msg == 'undo':
                event['reddit'] = "all"
            else:
                event['reddit'] = "single"

            results = updateEvent(calendar, event)
            if isinstance(results , str):
                print(results)


    statusID, valueID = customNameToID({'status': ['choices']})
    statusID, confirmID = customNameToID({'Status': ['Confirmed'][0]})
    statusID, changeID = customNameToID({'Status: ': ['change'][0]})
    statusID, pendID = customNameToID({'Status: ': ['pend'][0]})
    print(confirmID, " ", changeID, " ", pendID)
    startDate = dt.date(int(nextYear), 1, 1)
    endDate = dt.date(int(nextYear), 12, 31)
    events = getEvents(calendar, startDate, endDate)

    print("updating status", startDate, " ", endDate)
    for event in events:
        if event['rrule'].find('YEAR') == -1:
            continue
#        if event['who'] == "":
#            continue
#        if event['rrule'].find('WEEK') > -1:
#            continue
#        if event['rrule'] == None:
#            continue
        if 'custom' in event:
            if statusID in event['custom']:
                if event['custom'][statusID][0] !=  changeID and \
                   event['custom'][statusID][0] !=  confirmID: # and \
                   #event['custom'][statusID][0] !=  pendID:
                    continue
                event['custom'][statusID].clear()
                print("changing status" , event['who'], event['title'] )
                event['custom'][statusID].append(pendID)
                    # event['remote_id'] =  pendID
                event['redit'] = "all"
                results = updateEvent(calendar, event)
                print("updating ", event['start_dt'], " " , event['title'], "to", event['custom'][statusID])
                if isinstance(results , str):
                    print(results)


def newYear(calendar):
    if calendar == "":
        calendar = calendarPicker("New Year:")

    file = open("editRide.css", "r")
    htmlHeader = file.read()
    file.close()
    lastReset="1/1/1901"
    # fp = resetLockFile
    # if os.path.exists(fp):
    #     file = open(resetLockFile, "r")
    #     lastReset = file.read()
    #     file.close()
    # else:
    #     file = open(resetLockFile, "w")
    #     file.write(lastReset)
    #     file.close()
    # current year if in Jan or Feb


    today = dt.date.today()
    year = today.year
    month = today.month
    day = today.day
    if today.month < 6:
        lastYear = year - 1
        nextYear = year
    else:
        lastYear = year
        nextYear = year + 1


    startDate = dt.date(nextYear, 1, 1)
    endDate = dt.date(nextYear, 12, 31)
    events = getEvents(calendar, startDate, endDate)
    events.sort(key=lambda x: x['start_dt'])
    statusID, valueID = customNameToID({'status': ['choices']})
    statusName, statusValues= customIDToName({statusID: ["choices"]})
    statusID, confirmID = customNameToID({'status': ['confirm'][0]})
    statusID, changeID = customNameToID({'status': ['change'][0]})
    statusID, pendID = customNameToID({'status' : ['pend'][0]})
    names = {}
    events.sort(key=lambda events: events['who'])
    pcount = 0
    print(startDate, endDate)
    errorList = list()
    for event in events:
        if event['rrule'].find('YEAR') == -1:
            continue
#        if event['who'] == "":
#            continue
#        if 'custom' not in event:
#            continue
#        if event['rrule'].find('WEEK') > -1:
#            continue
        if statusID not in event['custom']:
            msg = "No Custom Field found for " + fromTeamupDate(event['start_dt']) + " " + event['title']
            errorList.append(msg)
            continue
        status = event['custom'][statusID][0]
        if event['who'] not in names.keys():
            names.update({event['who']: { confirmID:0, changeID :0, pendID: 0}})
        if status in (confirmID, changeID, pendID):
            names[event['who']][status] +=1
            if status == pendID:
               pcount += 1
    rideLeader=""
    page = htmlHeader


    page += "  <body>  <div id='head' class='container-fluid' style='border:2px solid yellow'>  "
    page += " <div class='row'><div class=col> <br /></div></div>"
    page += " <div class='row'><div class=col-3>"
    page += " <form action='/calendar/mainMenu.php'>"
    page += "              <button class='button'"
    page += "                    type='submit'"
    page += "                    >Back to Main Menu</button> </form> </div><div class=col-9> </div></div>"
    page += "<div class='row'><div class=col style='text-align:center;'><HR></hr></div></div>"
    page += "<div class=row> <div class=col-5></div><h1>" + str(nextYear) + " New Year Reset<h1></div><div class=col-7></div>"


    page += "<div class=row><div class='col-6'>"
    page += """<label>When you reset the calender, it does two things. First
     all of the rides for last year will be disconnected from their repeating pattern, so changes made to future rides will no longer affect last years rides. Secondly, status for all rides for the new year will be set to Pending. 
    
     """
    page += "</div>"

    page += "<div class='col-2'>"
######
#    if month > 3:
######
    page += " <input type='hidden'    name='cal' value='"
    page += calendar + "'  >  <input type='hidden'   name='nextYear' value="
    page += str(nextYear) + ">"
    if month > 2  or [pendID] in nested_lookup(statusID, events):
        disabled = "type= 'submit' disabled    style=' background-color: darkgrey; padding:15px;'>  LOCKED <br>  "
    else:
        disabled = "type = 'button' class='btn-3d red '   style='background-color: #aa0000; padding:15px;' > "

    url="'/resetNewYear?cal=" + calendar + "&nextYear=" + str(nextYear) + "'"
    url2="'/newYear?cal=" + calendar + "'"
    page +=  " <button  id='wait' onclick=\"setWait("
    page +=  url  + "," + url2 + ", 'wait' )\";" + disabled + " "
    page += " Reset Rides for "
    page += str(nextYear)+ " </button>    </div>"
    page += " <div class=col-4>"



    print("pcount", pcount, "month", month )
    if month < 3  and pcount > 1 and pcount < 100:
        page += "<p style='background-color: darkred; color:white;padding:10px;'>"
        page += "The reset button only works if there are no Pending or Changes Pending rides for the new year. "
        page += "There are stil rides  with the status set to Pending or Changes Pending. You need to change these to Confirmed before the reset button will become activated."
        page += "  Click on the names"
        page += " below and search the Calendar for Pending and Changes Pending."
        page += " Change the status on those to Confirmed, and then refresh this page to continue."
        page += "When there are no Pending or Changes Pending rides in the new year, the reset button will become activated. Click it to change all rides in the new year from Confirmed to Pending. Then send email confirmation requests.</p>"
    else:
        page += "Note that the weekly rides are managed manually by the Rides Chair."
#        page += "Next it will set the status to \"Pending\" for all the rides in "  + str(nextYear)
#        page += ", allowing the ride leaders to confirm their rides for "
#        page += " the coming year. <br> After this has finished you should send out"
#        page += " the request for ride confirmations below. "
    page += "</div>"
    print(errorList)

#    url="'/resetNewYear?cal=" + calendar + "&nextYear=" + str(nextYear) + "&msg=confirm'"
#    url2="'/newYear?cal=" + calendar + "'"
#    page +=  "<div class=col-1 ><button   onclick=\"setWait("
#    page +=  url  + "," + url2 + ",'wait' )\";"
#    page +=  "> Set  All Confirmed</button></div>"

###    page += "<input type='hidden' name='msg'   value='undo'"

#    page += "                </form>"

    page += """

<script>
function Waitand(wait) {
var x = document.getElementById(wait);
x.innerHTML= "<b>Please Wait...</b>";
x.type = "'submit' disabled";
x.style.color = 'white';
x.style.background ='darkred';
x.style.padding ='30px';
}
</script>
<script>
function setWait(url, url2, wait) {
    var xhttp;
    var x = document.getElementById(wait);
    x.innerHTML= "<b>Please Wait...</b>";
    x.type = "'submit' disabled";
    x.style.color = 'white';
    x.style.background ='darkred';
    x.style.padding ='30px';
    xhttp=new XMLHttpRequest();
    xhttp.open("GET", url, true);
    xhttp.send();
    xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        window.location.href= url;
                        xhttp.open("GET", url2, true);
                        xhttp.send();
                    }
                 };
}
</script>

    """
    page += "</div><div class='row'><div class=col style='text-align:center;'><HR></hr></div>"
    page += "</div><div class='row'><div class=col style='text-align:center;'> "
    page += "<h1>Ride Leader Confirmation Requests</h1></div></div><div class=row>"
    page += "<div class='col-2'>"
    page += "            <form action='/summaryMail'>"
    page += "<input type='hidden' name='cal'   value='"
    page += calendar + "'/> "
    page += "              <button class='btn-3d yellow'"
    page += "                    type='submit'"

    page += "                    name='rideLeader'"
    page += "                    value='all'>Send to all Ride Leaders</button>"
    page += "            </form></div>"


    page += "          <div class='col-4'>"
    page += "<label>After you've reset the Calender you should send Confirmation Request emails to all ride leaders. Send these as often as you like; it will send only to Ride Leaders who still have Pending rides in the new year.  </label>"
    page += "</div><div class=col-1></div><div class='col-4'>Send a Confirmation Reminder to just one Ride Leader by entering their name (must match the Ride Leader Table) and press Send."
    page += "         <form action='/summaryMail'>"
    page += " <input type='text'  id='rideLeader' name='rideLeader' "
    page += "type='text' /> "
    page += "<input type='hidden' "
    page += "              name='cal' "
    page += "              value='"
    page += calendar + "'/> "
    page += "      </div><div class=col-1> <button class='btn-3d yellow'  type='submit' style='height:50px; margin-top:18' "
    page += "'> Send</button> "
    page += "      </form> </div>"


    page += "</div><div class='row'><div class=col style='text-align:center;'><HR></div></div></HR><div class=row>"
    page += " </div><div class='row'>"

    page += ""
    page += "              <div class='col-1 '></div>"
    page += ""
    page += "              <div class='col-2 colheading2'>"
    page += "              </div>"
    page += ""
    page += "              <div class='col-1 colheading2'"
    page += "                   style='border-bottom:None;'>"
    page += "                "
    page += "              </div>"
    page += ""
    page += "              <div class='col-1 colheading2'"
    page += "                   style='border-bottom:None;'>"
    page += "               "
    page += "              Changes</div>"
    page += ""
    page += "              <div class='col-1 colheading2'"
    page += "                   style='border-bottom:None;'>"
    page += "                "
    page += "              </div>"
    page += ""
    page += "              <div class='col-1 '></div>"
    page += ""
    page += "              </div><div class='row'>"
    page += ""
    page += "              <div class='col-1 '></div>"
    page += ""
    page += "              <div class='col-2 colheading2'>"
    page += str(nextYear) + " Ride"
    page += "                Leader"
    page += "              </div>"
    page += ""
    page += "              <div class='col-1 colheading2'"
    page += "                   style='border-bottom:None;'>"
    page += "                Confirmed"
    page += "              </div>"
    page += ""
    page += "              <div class='col-1 colheading2'"
    page += "                   style='border-bottom:None;'>"
    page += "                Pending"
    page += "              </div>"
    page += ""
    page += "              <div class='col-1 colheading2'"
    page += "                   style='border-bottom:None;'>"
    page += "                Pending"
    page += "              </div>"
    page += ""
    page += "              <div class='col-1 '></div>"
    page += "                </div><div class='row'>"
    for rideLeader, statusList  in names.items():
        if statusList[pendID] == 0 and statusList[changeID] == 0:
            continue
        page += "              <div class='col-1 '> </div>"
        page +=  " <div class='col-2 namecol'>"
        page += "<a href='https://teamup.com/" + calendar + "?query=&quot;" + rideLeader + "&quot"
        page += "' rel = 'noreferrer noopener external' target = '_blank' >" + rideLeader + "</a>"
        page +=  "</div>"

        for key, value, in statusList.items():
            page +=  " <div class='col-1 tbl-body'> " + str(value) + "</div>"
        page += "              <div class='col-1 '> </div>"
        page +=  "   </div><div class='row'>"
    page += "</div><div class='row'><div class=col style='text-align:center;'><br/> </div></HR><div class=row>"
    page += "</div>"
    page += "</body>"
    page += "</html>"
    page += ""




    if __name__ == "__main__":
        print(page)
    else:
        return(page)

def main(argv):

    calendar = ""
    try:
        opts, args = getopt.gnu_getopt(argv, "")
    except getopt.GetoptError:
        print (argv[0], ' [calendar]')
        sys.exit(2)
    argCount = 0
    for opt, arg in opts:
        if  arg == '':
            argCount += 1
        else:
            argCount += 2
    if len(argv) > 0:
        calendar = argv[0]

    if calendar == "":
        calendar = calendarPicker("new year")
    newYear(calendar)

if __name__ == "__main__":
    main(sys.argv[1:])


