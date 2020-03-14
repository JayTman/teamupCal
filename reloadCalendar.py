from truncateSubCalendars import *
from restoreSubCalendar import *
from restoreRides import *



def  reloadCalendars(fileName, toCal):
    truncateSubCals(toCal)
    s = input("Continue and load sub calendars? (y/n) ")
    if s != 'y':
        print("Exiting")
        exit(0)

    loadSubCals(fileName, toCal)

    s = input("Continue and load rides? (y/n) ")
    if s != 'y':
        print("Exiting")
        exit(0)


    restoreRides(fileName, toCal)


def main(argv):

    fileName = ""
    try:
        opts, args = getopt.gnu_getopt(argv, "")
    except getopt.GetoptError:
        print (argv[0], "")
        sys.exit(2)
    argCount = 0
    for opt, args in opts:
        if  arg == '':
            argCount += 1
        else:
            argCount += 2

    toCal = ""
    fileName = ""

    fileName = filePicker("Backup File for data source", "*.jsn")
    toCal = calendarPicker("Calendar to trancate and restore")
    reloadCalendars(fileName, toCal)

if __name__ == "__main__":
    main(sys.argv[1:])


