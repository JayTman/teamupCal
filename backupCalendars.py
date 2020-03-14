#!/home/ebcrides/virtualenv/release/3.7/bin/python
from teamup import *
from icalendar import Calendar, Event
import sys
from datetime import datetime
from dateutil.rrule import rrulestr
import csv

JSONevents = list()
count = 0
ICScalendars = dict()

all = Calendar()
calendar = ""
csvTable = list()
csvHeader = list()
csvRow = list()

def initBackupEvent(event):
    ICSevent = event['id']
    if csvHeader[0] != "new":
        rideList.clear()

def addField(event, ICSevent, name, val):
    global csvHeader, csvRow, csvTable

    # Add field name as a column if its the first row in
    # the CSV file
    if csvHeader[0] == "new":
        csvHeader.append(name)
    # Add field to CSV file
    #
    csvRow.append(val)

    # rrule does magic in the ICS library
    # just gives error messages for a valid format so change the name.
    # change it back when the file gets written
    if name.find("rrule") > -1:
        name = name + "1"
    #
    # Add field to ICS file

    #
    ICSevent.add(name, val)

def addEvent(event, ICSevent):
    global csvHeader, csvRow, csvTable

    # Add event to CSV file
    if csvHeader[0] == "new":
        csvHeader = csvHeader[1:] # get rid of the new flag
        csvTable.append(csvHeader)
        
    s = str(csvRow)
    v = s.encode('ascii', 'ignore')
    csvRow = v.decode()
    csvTable.append(csvRow)
    csvRow = []

    # Add event to JSON file
    JSONevents.append(event)
    
    # Add event to ICS file
    all.add_component(ICSevent)

    """ Uncomment to ENABLE SUB CALENDAR ICS FILES
    subCalName = event['subcalendar_id']
    Found = False
    for key in ICScalendars:
        if key == subCalName:
            ICScalendars[key].add_component(ICSevent)
            Found = True
            break
    if Found == False:
        ICSCal = Calendar()
        ICS= Event()
        #            ICSevent.add('TZID', 'America/Chicago')
        ICSCal.add('VERSION', '2.0')
        ICSCal.add('PRODID', 'Evanston Bicycle Club Ride Schedule')
        ICSCal.add('METHOD', 'PUBLISH')
        ICSCal.add('X-WR-CALNAME', "'EBC Rides And Events | " + subCalName + "'")
        #ICSCal.add_component(ICSCal)
        #ICSCal.add_component(ICSevent)
        ICScalendars.update({subCalName: ICSCal})
    """  

def writeBackups(fileName, calendars, config):
    global JSONevents
    if not fileName:
        fileName = keyValue(config, 'title')

    #
    # write json backup
    #
    data = {}
    for event in JSONevents:
        for key, val in event.items():
            if isinstance(val, str):
                v = val.encode('ascii', 'ignore')
                val = v.decode()
    
    data.update({'events': JSONevents})
    data.update({'subcalendars': calendars})
    data.update({'configuration': config})

    fileName = fileName.replace(" ", "_")
    with open(fileName + ".jsn", "w") as write_file:
        json.dump(data, write_file)
    write_file.close()
    with open(fileName + ".csv", 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvTable)
        csvFile.close()
        # None makes sorting on series+id blowup, so change it for sorting
        # and then set it back.

    # just close the CSV file
    # CSVwriter.close()

    #
    # write ICS backup
    #

    allCals = open(fileName + "All.ics", 'wb')
    allCals.write(all.to_ical())
    allCals.close
    """ ENABLE SUB CALENDAR ICS FILES
    #
    # This section will produce an ICS file for each ride category (sub calendar for teamup)
    # enable this section if you want those
    #
    
    for cal in ICScalendars:
        name = cal
        name = name.replace(" ", "_")
        name = name.replace(".", "")
        #name = name.replace(">", "-")
        name = name.replace("/", "_")
        # name = name.replace("(", "")
        # name = name.replace(")", "")
        f = open(name + ".ics", "wb")
        f.write(ICScalendars[cal].to_ical())
        f.close()
    """

def main(argv):
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "jy:")
    except getopt.GetoptError:
        print (os.path.basename(sys.argv[0]), '[-y year] [calendarName]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-y"):
            if arg != "":
                startYear = int(arg)
        elif opt in ("-j"):
            print ("j")

    csvHeader.append("new")
    if len(args) > 0:
        fileName = args[0]
        calendar = calNameToID(fileName)
    else:
        calendar = calendarPicker("Pick a Calendar a to backup:")
        fileName = calIDToName(calendar)

    if calendar == None:
        print("Error: ", args[0], "Calendar name not found")
        exit(1)

    today = dt.date.today()
    startDate = dt.date(today.year - 2, 1, 1)
    endDate = dt.date(today.year + 1 , 12, 31)
    #endDate = dt.date(today.year, today.month + 2, 30)
    config = getConfig(calendar)
    calendarName = keyValue(config, 'title')
    calendars = getSubCalendars(calendar)

    events = getEvents(calendar, startDate, endDate)
    #

    events = sorted(events, key=lambda i: (i['rrule']))
    events = sorted(events, key=lambda i: (i['title']))
    for ride in events:
        if ride['series_id'] == None:
            ride['series_id'] = "unknown"
    events = sorted(events, key=lambda i: (i['series_id']))
    for event in events:
        if event['series_id'] == "unknown":
            event['series_id'] = None
    prevSeriesID = ""
    fields = getFields(calendar)
    customTranslateTable(calendar, fields, fields)
    count = 0
    for event in events:
        #
        # each instance of a repeating event will get retrieved here, but they all will have the same series_id
        # So don't save any events until the series_id changes since there all the same ride.
        #
        if event['series_id']:
            if prevSeriesID == event['series_id']:
                #print(event['series_id'] + " Skipping prev " + prevSeriesID +  " " + event['title'] + "  " + fromTeamupDate(event['start_dt']) )
                continue
        prevSeriesID = event['series_id']
        count += 1
        names = []
        if event['notes'] != None:
            # get rid of invalid chars by encoding it
            # then turn it back into a regular string
            s = event['notes'].encode('ascii', 'ignore')
            event['notes'] = s.decode()

        #
        # swap numerical subcalendar ids for the names because the id numbers could change
        # when the restore takes place
        #
        event['subcalendar_id'] = id2name(calendars, event['subcalendar_id'])
        ids = event['subcalendar_ids']
        for x in range(len(ids)):
            names.append(id2name(calendars, ids[x]))
        event['subcalendar_ids'] = names

        #JSONevents.append(event)
        #    ICSevent = getEvent(calendar, event['id'])
        #
        #backupEvent(event)
        #ICSevent = Event()
        #ICSevent = getEvent(calendar, event['id'])
        # create ICS event and add to backup
        ICSevent = Event()
        addField(event, ICSevent,  'Summary', event['title'])
        addField(event, ICSevent,  'dtstart', parse(event['start_dt']))
        addField(event, ICSevent,  'start time', (parse(event['start_dt'])).strftime("%H:%M"))
        addField(event, ICSevent,  'dtend', parse(event['end_dt']))
        addField(event, ICSevent,  'end time', (parse(event['end_dt'])).strftime("%H:%M"))
        addField(event, ICSevent,  'category', event['subcalendar_id'])
        addField(event, ICSevent,  'location', event['location'])
        addField(event, ICSevent,  'description', event['notes'])
        addField(event, ICSevent,  'categories', event['subcalendar_ids'])
        #addField(event, ICSevent,  '"series ID"', event['series_id'])
        addField(event, ICSevent,  'organizer', event['who'])
        addField(event, ICSevent,  'rrule', event['rrule'])
        
        addField(event, ICSevent, 'SEQUENCE', 0)
        addField(event, ICSevent, 'TRANSP', 'OPAQUE')
        addField(event, ICSevent, 'CLASS', 'PUBLIC')        
        addField(event, ICSevent,  'recurrence', event['rrule'])
        addField(event, ICSevent,  'x-teamup-who', event['who'])
        addField(event, ICSevent,  'allday', event['all_day'])
        addField(event, ICSevent,  'dtstamp', parse(event['creation_dt']))
        #
        # create rows for custom fields
        #
        for k, v in event['custom'].items():
            x = customIDtoName(k)
            if isinstance(v, list) and len(v) > 0:
                val = v[0]
            else:
                val = v
            addField(event, ICSevent,  x.replace(":", ""), val)
        addEvent(event, ICSevent)
    #print(" Backing Up " + event['title'] + "  " + fromTeamupDate(event['start_dt']))

    writeBackups(fileName, calendars, config)
    print("Done backing up " + str(count) + " events in calendar: " + fileName + " Teamup URL:", calendar)

if __name__ == "__main__":
    main(sys.argv[1:])

