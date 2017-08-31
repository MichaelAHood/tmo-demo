var DASHBOARD_CAMERA = (function (my) {

var g_enable_camera = true;
var g_video_delay = 50;

// if "ATM button is clicked": headerT

var setup_camera = function() {
  var panel_name = 'mycamera';
  var panelHeaderTitle = 'Camera';
  var panelContent = ' \
  <body> \
  \
  <a href="#" id="admin-link">Display Admin</a> \
  <a href="#" id="customer-link">Display Customer</a> \
  \
  <div class="container-fluid"> \
  <div class="row"><img id="camera_view" src="http://localhost:5000/video_frame"></img></div> \
  </div> \
  \
  <form id="admin-form" role="form" class="form-horizontal"> \
  <div class="container-fluid"> \
    <div class="panel panel-default"> \
    \
    <div class="panel-heading"> \
      <button data-toggle="collapse" data-target="#admin-body">Register Customer</button> \
      <label class="form-check-label"><input id="enable-camera" class="form-check-input" type="checkbox" checked> Enable Camera</label> \
    </div> \
    \
    <div id="admin-body" class="panel-body collapse"> \
    <div class="form-group row"> \
      <label for="admin-name" class="col-form-label col-sm-2">Register Name:</label> \
      <div class="col-sm-10"><input id="admin-name" type="text" class="form-control" id="admin-name"></div> \
    </div> \
    \
    <div class="form-group row"> \
      <label for="admin-pin" class="col-form-label col-sm-2">Register Phone Number (ex: 555-555-5555):</label> \
      <div class="col-sm-10"><input id="admin-pin" type="text" class="form-control" id="admin-pin"></div> \
    </div> \
    \
    <div class="form-group row"> \
      <div class="col-sm-12"><button id="admin-submit" type="submit" class="btn btn-default">Submit</button></div> \
    </div> \
    </div> \
    \
    </div> \
  </div> \
  </form> \
  \
  <form id="customer-form" role="form" class="form-horizontal"> \
  <div class="container-fluid"> \
    <div class="panel panel-default"> \
    \
    <div class="panel-heading"> \
      <button data-toggle="collapse" data-target="#customer-body">Verify Customer</button> \
      <label class="form-check-label"><input id="enable-camera" class="form-check-input" type="checkbox" checked> Enable Camera </label> \
    </div> \
    \
    <div id="customer-body" class="panel-body collapse"> \
    <div class="form-group row"> \
      <label for="customer-name" class="col-form-label col-sm-2">Name:</label> \
      <div class="col-sm-10"><input id="customer-name" type="text" class="form-control" id="customer-name"></div> \
    </div> \
    \
    <div class="form-group row"> \
      <label for="customer-pin" class="col-form-label col-sm-2">Phone Number (ex: 555-555-5555):</label> \
      <div class="col-sm-10"><input id="customer-pin" type="text" class="form-control" id="customer-pin"></div> \
    </div> \
    \
    <div class="form-group row"> \
      <div class="col-sm-6 text-left"><button id="customer-form-submit" type="submit" class="btn btn-default">Submit</button></div> \
      <div class="col-sm-6 text-right"><button id="reset-session-submit" type="submit" class="btn btn-default">Reset</button></div> \
    </div> \
    </div> \
    \
    </div> \
  </div> \
  </form> \
  ';
  
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

  document.getElementById('enable-camera').onchange = function() {
    g_enable_camera = document.getElementById('enable-camera').checked;
  };

  ///////////////////////////////////////
  //// Begin ATM Portal Methods /////////
  ///////////////////////////////////////

  document.getElementById('admin-form').onsubmit = function() {
    return false;
  };

  document.getElementById('admin-submit').onclick = function() {
    var adminName = document.getElementById('admin-name').value;
    var adminPin = document.getElementById('admin-pin').value;
    var http = new XMLHttpRequest();
    var url = "http://localhost:5000/register_face";
    var params = "name=" + adminName +
                 "&pin=" + adminPin;
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
  //// Begin Customer Portal Methods ////
  ///////////////////////////////////////
  
  document.getElementById('customer-form').onsubmit = function() {
    return false;
  };

  document.getElementById('customer-form-submit').onclick = function() {
    var customerName = document.getElementById('customer-name').value;
    var customerPin = document.getElementById('customer-pin').value;
    var http = new XMLHttpRequest();
    var url = "http://localhost:5000/lookup_face";
    var params = "name=" + customerName +
                 "&pin=" + customerPin;
    http.open("POST", url, true);
    //Send the proper header information along with the request
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http.onreadystatechange = function() {//Call a function when the state changes.
      if(http.readyState == 4 && http.status == 200) {
        alert(http.responseText);
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
        alert('Session Terminated. ' + http.responseText);
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
