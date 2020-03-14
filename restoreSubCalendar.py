from teamupNew import *
import sys
from dateutil.parser import parse
from collections import defaultdict



def loadSubCals(fromName, toCal):
    # params='?startDate=2018-ame01-01&endDate=2018-12-31'
    calName = ""
    insertSubCals = True
    if insertSubCals == False:
        print("Running in test mode, nothing will get altered")
    if fromName == "":
        fromName = filePicker("Pick one: ", "*.jsn")
    if toCal== "":
        toCal = calendarPicker("Pick a calendar to restore into: ")

    if insertSubCals == False:
        print ("Testing ")
    else:
        print ("Restoring ")

    with open(fromName, "r") as results:
        calData = json.load(results)

    fileConfig = calData['configuration']
    fromSubCalendars = calData['subcalendars']
#    fromFields = calData['fields']
    rides = calData['events']
    keynames = {'title', 'id', 'color', 'overlap', 'id'}
    toCalName = calIDToName(toCal)

    #print("Restoring Sub Calendars from file:" + fromName + " into calendar:" + toCalName, end=" ")
    #s = input("Are you sure (y/n) ")
    #if s != 'y':
    #    print("Exiting")
    #    exit()

    for subCal in fromSubCalendars:
        #print("Read subcalendar: ", keyValue(subCal, 'name'))
        # type = 'subcalendars'
        # for x in calendarsToLoad:
        print("Creating :", subCal['name'])
        if debug:
            print("subCal list: ", x, " ", subCal['name'])
        # if x == subCal['name']:
        del subCal['creation_dt']
        #del subCal['id']
        params = ""
        if insertSubCals == True:
            res = queryTeamup(HEADERS, toCal, 'post',
                              'subcalendars', params, subCal)
            if isinstance(res, str):
                print("Results: ", res)
                continue
            if res.get('subcalendars'):
                results = res['subcalendars']
                print(subcal['name'] + " Inserted.")
            elif res.get('error'):
                print("Error inserting Sub Clalendar: ", res['error'])


def main(argv):
    global insertRides
    global insertSubCals
    global iter
    insertSubCals = False


    try:
        opts, args = getopt.gnu_getopt(argv, "s")
    except getopt.GetoptError:
        print (argv[0], '-y)ear_mode \"RideLeader Name\" [-r)eminder_mode -s)ummary mail message -e)mail Email address override')
        sys.exit(2)
    argCount = 0
    for opt, arg in opts:
        if  arg == '':
            argCount += 1
        else:
            argCount += 2


    fromName = ""
    toCal = ""
    if len(args) > 0:
        fromName = args[0]
    restoreSubCal(fromName, toCal)



if __name__ == "__main__":
    main(sys.argv[1:])


