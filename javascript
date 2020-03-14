    URL="'https://" + domain + "/confirm?cal=" + calendar
    URL += "&rideID=" + ride['id'] + "&rideLeader=" + quote(rideLeader)
    confirmButton = " <button type='button' onclick=\"setConfirm("
    confirmButton += URL + "', " + str(index) + ")\" "
    confirmButton += " class='button confirmButton'> Confirm</button>"
// load a page
//
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

// Set attributes on a page, ID should be unique
    html  = "  <div class='box " + cname + "' id='card" + str(index)+ "' >"

    URL="'https://" + domain + "/confirm?cal=" + calendar
    confirmButton = " <button type='button' onclick=\"setConfirm("
    confirmButton += URL + "', " + str(index) + ")\" "
    confirmButton += " class='button confirmButton'> Confirm</button>"
   
    html += confirmButton
    html += """
    function setConfirm(url, index) {
                var xhttp;
                var name = "card" + index;
                var x = document.getElementById(name);
                //alert(url);
                xhttp=new XMLHttpRequest();
                x.style.background = '#33DD00';
                xhttp.open("GET", url, true);
                xhttp.send();
             }
     """
//switch to a different url
        response = "<script> window.location.href='" + url +"';  </script>"
