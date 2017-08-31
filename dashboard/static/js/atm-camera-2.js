var DASHBOARD_CAMERA = (function (my) {

var g_enable_camera = true;
var g_video_delay = 50;

// if "ATM button is clicked": headerT

var setup_camera = function() {
  var panel_name = 'mycamera';
  var panelHeaderTitle = 'Camera';
  var panelContent = '\
  <html> \
  <body> \
    <a href="#" id="admin-link">Display Admin</a> \
    <a href="#" id="customer-link">Display Customer</a> \
    <div id="admin-form">Admin Form \
      <form> \
        Register Customer Name: <input type=text/> \
        Register PIN: <input type=text/> \
        <input type=submit/> \
      </form> \
    </div> \
    <div id="customer-form">Customer Form \
      <form> \
        Name: <input type=text/> \
        PIN: <input type=text/> \
        <input type=submit/> \
      </form> \
    </div> \
    <script> \
    </script> \
  </body> \
  </html> \
  ';
  
  var myPanel = $.jsPanel({
    container: '#container-body',
    position: 'center-bottom',
    position: 'center-top',
    // setstatus: 'minimize',
    content: panelContent,
    headerTitle: panelHeaderTitle,
    contentSize: {width: 640, height: 750},
    contentSize: "640 auto"
  });

window.onload = function() {
  var admin_link = document.getElementById('admin-link');
  var admin_form = document.getElementById('admin-form');
  var customer_link = document.getElementById('customer-link');
  var customer_form = document.getElementById('customer-form');

  // Default init.
  admin_form.style.display = 'block';
  customer_form.style.display = 'none';

  admin_link.onclick = function() {
    customer_form.style.display = 'none';
    admin_form.style.display = 'block';
  };

  customer_link.onclick = function() {
    admin_form.style.display = 'none';
    customer_form.style.display = 'block';
  };
};


  document.getElementById('enable-camera').onchange = function() {
    g_enable_camera = document.getElementById('enable-camera').checked;
  };

  document.getElementById('register-face-form').onsubmit = function() {
    return false;
  };


  document.getElementById('register-face-submit').onclick = function() {
    // document.getElementById('register-face-form').submit();
    var name = document.getElementById('register-face-name').value;
    var organization = document.getElementById('register-face-organization').value;
    var email = document.getElementById('register-face-email').value;
    var linkedin_url = document.getElementById('register-face-linkedin-url').value;

    var http = new XMLHttpRequest();
    //var url = "/register-face";
    var url = "http://localhost:5000/register_face";
    var params = "name=" + name +
      "&organization" + organization +
      "&email=" + email +
      "&linkedin_url=" + linkedin_url;
    http.open("POST", url, true);

    //Send the proper header information along with the request
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    http.onreadystatechange = function() {//Call a function when the state changes.
      if(http.readyState == 4 && http.status == 200) {
        alert('Face registered: ' + http.responseText);
      }
    }
    http.send(params);
    return false;
  };
  ///////////////////////////////////////
  //// End Admin Portal Methods /////////
  ///////////////////////////////////////


  ///////////////////////////////////////
  //// Begin ATM Portal Methods /////////
  ///////////////////////////////////////
  document.getElementById('lookup-face-submit').onclick = function() {
    // document.getElementById('register-face-form').submit();
    var name = document.getElementById('lookup-face-name').value;
    var account = document.getElementById('lookup-face-acct').value;
    var pin = document.getElementById('lookup-face-pin').value;

    var http = new XMLHttpRequest();
    //var url = "/register-face";
    var url = "http://localhost:5000/lookup_face";
    var params = "name=" + name +
      "&account=" + account +
      "&pin=" + pin;
    http.open("POST", url, true);

    //Send the proper header information along with the request
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    http.onreadystatechange = function() {//Call a function when the state changes.
      if(http.readyState == 4 && http.status == 200) {
        alert('Face Identified as: ' + http.responseText);
      }
    }
    http.send(params);
    return false;
  };

  document.getElementById('reset-session-submit').onclick = function() {
    
    var http = new XMLHttpRequest();
    var url = "http://localhost:5000/reset_session";
    var params = "action=" + "reset";
    http.open("POST", url, true);
    //Send the proper header information along with the request
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http.onreadystatechange = function() {//Call a function when the state changes.
      if(http.readyState == 4 && http.status == 200) {
        alert('Face Identified as: ' + http.responseText);
      }
    }
    http.send(params);
    return false;
  };
  ///////////////////////////////////////
  //// End ATM Portal Methods ///////////
  ///////////////////////////////////////

  var refresh_id = setTimeout(update_frame, g_video_delay);
  // var refresh_id = setInterval(update_frame, g_video_delay);
};

var update_frame = function(items) {
  var video_frame_url = "http://localhost:5000/video_frame";
  var camera_view_id = "camera_view";
  var camera_view = document.getElementById(camera_view_id);

  if (!g_enable_camera) {
    var refresh_id = setTimeout(update_frame, g_video_delay);
    return;
  }


  // Option 3: Seems to work.
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      camera_view.src = "data:"+xhr.getResponseHeader("Content-Type")+";base64," + btoa(String.fromCharCode.apply(null, new Uint8Array(xhr.response)));
      var refresh_id = setTimeout(update_frame, g_video_delay);
      //DBG console.log("update_frame");
    } else if (xhr.readystate == 4 && xhr.status != 200) {
      alert(xhr.status);
      if (camera_view.src.indexOf("video-feed-unavailable.png") == -1) {
        camera_view.src = "images/video-feed-unavailable.png";
        var refresh_id = setTimeout(update_frame, g_video_delay);
      }
    }
  }
  xhr.onerror = function() {
    if (camera_view.src.indexOf("video-feed-unavailable.png") == -1) {
      camera_view.src = "images/video-feed-unavailable.png";
    }
    var refresh_id = setTimeout(update_frame, 3000);
  }

  xhr.responseType = "arraybuffer";
  xhr.open("GET", video_frame_url, true);
  xhr.send();
};

setup_camera();

}(DASHBOARD_CAMERA || {}));
