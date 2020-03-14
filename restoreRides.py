from teamupNew import *
import sys
from dateutil.parser import parse
import copy
from collections import defaultdict
from nested_lookup import nested_update, nested_delete, nested_lookup, get_occurrence_of_key, get_occurrence_of_value, get_all_keys

# Calendar ID's
insertRides = True
findRides = False

def deleteCustomsFields(toCal):
    params = ""
    fields = getFields(toCal)
    for field in fields:
        if field['type'].find('builtin') > -1:
            continue
        print(field['id'])
        results = queryTeamup(UPDATE_HEADERS, toCal, 'delete', 'field-definitions', params, field['id'])
        if isinstance(results, str):
            print(results)
            return(results)



def restoreRides(fileName, toCal):
    calName = ""
    if insertRides == False:
        print("Running in test mode, nothing will get altered")
    #teamupCal = calendarPicker("Pick a Calendar to restore ")

    if insertRides == False:
        print ("Testing ")

    if fileName == "":
        fileName = filePicker("Pick one: ", "*.jsn")
    if toCal == "":
        toCal = calendarPicker("Pick a calendar to restore into: ")


    with open(fileName, "r") as results:
        fileCal = json.load(results)
    toConfig = getConfig(toCal)
    fileConfigs = fileCal['configuration']
    fileSubCalendars = fileCal['subcalendars']
    fileRides = fileCal['events']
    fileRides.sort(key=lambda x: x['start_dt'])
    fileCustomDef = fileConfigs['fields']['definitions']

    start = parse(fileRides[0]['start_dt'])
    start  = dt.date(start.year, start.month, start.day)
    end = fileRides[-1]['start_dt']

    toSubCalendars = getSubCalendars(toCal)
    toConfig = getConfig(toCal)
    toEvents = getEvents(toCal, start, end)
    toEvents.sort(key=lambda x: x['start_dt'])
    count = 0
    errorCount = 0
    updateCount = 0
    errors = ""
    tmp = copy.deepcopy(fileCustomDef)
    print ("Restoring custom fields")

    createCustomFields(toCal, tmp)
    for fileEvent in fileRides:
        # print (i)
        # fileEvent = fileRides[i]

        date = fromTeamupDate(fileEvent['start_dt'])
        rideName = "Processing:" + date + " " + fileEvent['title']
        print(rideName)

        #if fileEvent['title'] == fileSeriesID:
            #print("dup title prev date " + startdt)
        #else:
            #fileSeriesID = fileEvent['title']
            #startdt = fileEvent['start_dt']
        #date = fromTeamupDate(fileEvent['start_dt'])
        if fileEvent['series_id'] == None:
            print("Warning: Event does not repeat, no series id set ")

        restoreSubCals(toSubCalendars, fileEvent)

        skip = False
        updated = False
        for existing in toEvents:
            if existing['title'] == fileEvent['title'] \
               and existing['start_dt'] == fileEvent['start_dt'] \
               and existing['who'] == fileEvent['who']:
                updated += 1
                #any changes go here
#                print("existing ", existing['custom'] , "\nnewsting ", fileEvent['custom'])
                existing['custom'] = fileEvent['custom']
                # do not remove redit
                #existing['redit'] = "all"
                #updateEvent(toCal, existing)
                #updated = True
                print("Already exists, skipping.")
                updateCount += 1
                break

            else:
                continue
#                else:
#                    print(fileEvent['title'] + " memory: " + fromTeamupDate(existing['start_dt']) +  " " + existing['title'])

                #print( str(i) + " extra definitions")
        if updated == True:
            updated = False
            continue
        params = ""
        if 'custom' in fileEvent:
            fcustom = fileEvent.pop('custom')
            newCustom = dict()
            for fieldID, valueID in fcustom.items():
                fieldName, valueName = customIDToName({fieldID: valueID}, fileCustomDef)
                toFieldID, toValueID = customNameToID({fieldName:valueName})
                if toFieldID == None or toFieldID == 'notfound':
                    continue
                newCustom.update({toFieldID:toValueID})
            fileEvent['custom'] = newCustom
        fileEvent['redit'] = "all"
        res = queryTeamup(UPDATE_HEADERS, toCal,
                         'post', 'events', params, fileEvent)
        if isinstance(res, str):
            if res.find("Er") > -1:
                errors += rideName + " " + res + "\n"
                errorCount += 1
            print(res)
        else:
            print("Inserted.")

            count += 1
    print("\n\n", errors)
    print("\nRestore Complete: Inserted " + str(count) + " Updated: " + str(updateCount) + " Errors: "  + str(errorCount))

def main(argv):
    global insertRides
    fileName = ""
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
        if opt in ("-s"):
            insertSubCals = True

    toCal = ""
    if len(args) == 1:
        fileName = args[0]
    if len(args) == 2:
        fileName = args[0]
        toCal = args[1]
    restoreRides(fileName, toCal)

if __name__ == "__main__":
    main(sys.argv[1:])


