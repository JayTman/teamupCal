from teamupNew import *
import datetime as dt
from urllib.parse import quote_plus
import os
import difflib
import copy
from updateRideStatus import updateRideStatus
from rideReport2 import genReport



def HTMLDiff(a, b):


    import difflib 
    import re

    #  remove HTML from description
    #
    pattern = "<mailto:"
    pattern = "<{[ \w=\"\/\.\:\-\;\@\%]}*>"
    #pattern = "^w+"
    #pattern = "[/<[^>]*>/g, ' ']"
    #pattern = "<(^>=|=''|=""[^""]*""|=[^'""])*>"
    #
    # highlight the changes
    #

    a = re.sub(pattern, "", a)
    b= re.sub(pattern, "", b)


    matcher = difflib.SequenceMatcher(None, a, b)
    def process_tag(tag, i1, i2, j1, j2):

        #print("a: ", matcher.a[i1:i2],  matcher.b[j1:j2] )
        if tag == 'replace':
            return( '<span style="font-size:14;font-weight:bold;background:yellow; color:red"  >'  + matcher.b[j1:j2] + '</span>')
#            return( '<b style="bold;background:yellow; color:red"  >'  + matcher.b[j1:j2] + '</b>')
        if tag == 'delete':
            return ('<span class=delete ><del>' + matcher.a[i1:i2] +'</del></span>')
        if tag == 'equal':
            return( '<span class=equal >' + matcher.b[j1:j2] + '</span>')
        if tag == 'insert':
            return( '<span class=equal >' + matcher.b[j1:j2] + '</span>')
#            return( '<b style="font-size:18;font-weight:bold;background:yellow; color:red"  >'  + matcher.b[j1:j2] + '</b>')
        assert false, "Unknown tag %r"%tag
    #return(a, b)
    return ''.join(process_tag(*t) for t in matcher.get_opcodes())





def saveRideChanges(cal, args, rideID):

        ride = getEvent(cal, rideID)
        print("ARGS", args)
        for arg in args:
            if arg[0] == 'cal':
                continue
            if arg[0] not in ride:
                continue
            if arg[0] == 'start_dt':
               date = toTeamupDate(arg[1])
               ride[arg[0]] = date
            elif arg[0] in ride:
               ride[arg[0]] = arg[1]
               print("update arg", arg[0],":",  ride[arg[0]])
               #if arg[0] == 'who':
                   #rideLeader = ride['who']
            ride['redit'] = 'all'
        print("Trying to update", ride)
#        updateRideStatus( 'confirm', cal, ride['id'], ride['who'])
        ret = updateEvent(cal, ride)
        print("return from update", ret)
        address=addressBook(ride['who'])
        if address != None:
            body = "Your changes for " + ride['title'] + " ride on " + fromTeamupDate(ride['start_dt'] )
            body +=  " have been updated in the calendar."
            email(body , ride['who'], address, ride['title'])
        updateRideStatus( 'confirm', cal, ride['id'], ride['who'])
        
def updateRideChanges(cal, args, rideID):
        emailAddr = False
        msg = "NONE"
        for arg in args:
            if arg[0] == 'title':
                title = arg[1]
            if arg[0] == 'msg':
                msg = arg[1]
            if arg[0] == 'id':
                rideID = arg[1]
            if arg[0] == 'who':
                rideLeader = arg[1]
            if arg[0] == 'start_dt':
                start_dt = arg[1]

        filename = rideID + ".jsn"
        dir=rideChangePath
        if not os.path.exists(dir):
            os.mkdir(dir)

        with open(dir + filename, 'w') as file:
            json.dump(args, file)
        file.close()
        updateRideStatus( 'changes', cal, rideID, rideLeader)
        print( "saving :", filename)

        ridesButton = "   <!DOCTYPE html>"
        ridesButton += " <body>"

        ridesButton += "<a href='https://" + domain + "/editRide?"
        ridesButton += "cal=" + cal
        ridesButton += "&rideID=" + rideID + "&mode=Save&msg=" + msg + "'>Button</a>"

#        ridesButton += "<img src='http://ebcrides.org/images/cal/button_get-ride-changes.png' alt=''></a>"
        message = "<br /><br />" + rideLeader + "  has changes for the   \"" + title + "\" ride on " + fromTeamupDate(start_dt) + ". <br>" 
        if len(msg) > 4:
            message += "They have sent you this message, <i> <br /><br />"
            message += str(msg) +  "</i><br />"

        message += "<br \>Press Show Changes to see the changes for this ride"
        message += "</h3><br>" + ridesButton + "</body></html"
        sendTo=rideschair
        print(message)
        email(message, rideLeader, sendTo, 'Ride change request for: ' +  title , sendTo)
        

def editRide(cal, rideID , mode, msg):
    ride = getEvent(cal, rideID)
    if isinstance(ride, str):
        print("Ride not found")
        return("Ride not found")
    print("MODE IS" , mode, "ride is", ride)
      

    print ("mode is " , mode, " " , msg)
    file = open("editRide.css", "r")
    htmlHeader = file.read()
    file.close()
    if  mode == "Save" or mode == "REEDIT":
        print ("IN save is " , mode, " " , msg)
        if 'notes' in ride:
            oldNotes= copy.copy(ride['notes'])
            print("old noestes", oldNotes)
        filename = rideID + ".jsn"
        dir=rideChangePath
        path=dir+filename
        if not os.path.exists(dir):
            os.mkdir(dir)
        if not os.path.exists(path):
            print("Eror: no ride to edit")
            return()
        with open(path, 'r') as file:
            args = json.load(file)
            file.close()
        print("args: " , args)
        for arg in args:
            if  arg[0] == 'msg':
                msg  = arg[1]
                continue
            else:
                ride[arg[0]] = arg[1]
                
            print("new:\n", arg[0],  " arg1:\n ", arg[1], "ride:\n",  ride[arg[0]])

    if mode == "Save":
        html = "<title>Ride Changes</title>" + htmlHeader + "<body>     "
        html += "<div id='card' class='textbox'><form action='/saveRideChanges'>"
        html += "<label><br><h1>  The ride leader changes are below. "

        html += " Press save to update the Calendar with these changes. <br></h1>"
        html += "<br><br>  Message from the Ride Leader:<br><br>"
        html += "<div class=report style='margin-left:5%;padding:10px; height:9%;width:40%;font-size:12'>" 
        html +=  msg  + "</div>"
        html += "<br><br><div class='btn-box' style='margin-bottom:20px'>"
        html += """
           <div class="item">
                <label for="rideLeader">Leader </label>
                <input class="text"  name="who"
        """
        value = ride['who']
        html += "value='" + value + "' type='text' /> </div>"


       # results = updateEvent(cal, ride)
    else:
        html = htmlHeader + "<body> <div id='do'  class='testbox'>"


        html += "<form action = '/updateRideChanges' id='myform' name='myform'>"
        html += "<div header><h1><br /> You can send an email message with your changes to the Rides Chair in the box below.<br/>"
        html += "You can also use the Ride Change Form to make your changes as they'll appear in the calendar. <br />"
        html += "Press Email Changes when you're done. <br /> <br /></h1></div>"
        html += "    <label style='margin-left:10%'>Message for the Rides Chair </label>"
        html += "    <textarea rows=2  name = 'msg' style='margin-bottom:20px; width:80%; margin-left:10%'>"
        html += "    </textarea>"
        html += "<input type=hidden name='who' value='" + ride['who'] + "'> "
        html += "<div id='demo2' class='btn-box' style='margin-bottom:20px'>"

    html += "<div header style='text-align:center;'><h2><b> Ride Change Form</b> <h2><br/></div>"
    html += """
         <div class="item">
            <label for="rideDate">Ride Date </label>
            <input class="text" id="RideDate" name="start_dt"
    """
    value = fromTeamupDate(ride['start_dt'])
    html += "value='" + value + "' type='datetime' '/> </div>"
    #

    # Title
    html += """
         <div class="item">
            <label for="title">Ride Title </label>
            <input type="text" id="title" name="title"
    """
    value = ride['title']
    html += "value='" + value + "' type='text' '/> </div>"
    #
    html += """
         <div class="item">
            <label for="startLocation">Start Location </label>
            <input class="text"  name="location"

    """
    value = ride['location']
    html += "value='" + value + "' type='text' '/> </div>"
    #

    #
    if mode  == "Save":
        html += " <div class='btn-group'>"
        html += "<label>Old: </label>"
        html += "<div class=report>" + oldNotes  + "</div>"
    
        html += "<label>Changes: </label>"
        text = HTMLDiff(oldNotes, ride['notes'])
        html += "<div class=report>"
        html +=  text + "</div></div>"

    html += "<label>New Description</label>"
    html += "<textarea id ='editor1' name = 'notes'>"
    if 'notes' not in ride:
        html += "No Desc. "  +"</textarea>"
    else:
        html += ride['notes'] +"</textarea>"

    html += "</div> <div class='btn-group'>"
    html += "<input type=hidden name=cal value='" + cal + "'> "
    html += "<input type=hidden name=id  value='" + ride['id'] + "'> "

    if mode  == "Save":
        html += "<button class=button3 `type='submit' "
        html += ">Save Changes</button> </form>"
    else:
        html += "<button `type='submit' "
        html += "class='button'>Send Changes to Rides Chair</button> </form>"




    html += "<form action = '/year'>"
    html += "<input type=hidden name=cal value= '" + cal + "'> "
    html += "<input type=hidden name=id  value='" + ride['id'] + "'> "
    html += "<input type=hidden name=rideLeader  value='" + ride['who'] + "'> "
    html += "<button class=button type='submit' name=cal val='"
    html += cal + "'>Cancel</button> </form></div>"

#    ajax = """
#       <script>
#       function myFunction() {
#         x = document.getElementById("myform");
##           alert(x);  
#         document.getElementById("myform").submit();
#        }
#    </script>
    html += """
           <script>
              CKEDITOR.replace('editor1',  {height: '400px', width: '100%'});
           </script>
    """
    html += "  </div>   </body>    </html>"
    if __name__ == "__main__":
        print(html)
    else:
        return(html)

def main(argv):

    cal = ""
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

    cal = argv[0]
    ride = argv[1]
    rideLeader = argv[2]
    editRide(cal, ride, rideLeader, "foo")


if __name__ == "__main__":
    main(sys.argv[1:])

