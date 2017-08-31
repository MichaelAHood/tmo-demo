var DASHBOARD_CAMERA = (function (my) {

var g_enable_camera = true;
var g_video_delay = 50;

var setup_camera = function() {
  var panel_name = 'mycamera';

  var myPanel = $.jsPanel({
    container: '#container-body',
    position: 'center-bottom',
    position: 'center-top',
    // setstatus: 'minimize',
    content: ' \
<div class="container-fluid"> \
<div class="row"><img id="camera_view" src="http://localhost:5000/video_frame"></img></div> \
 \
</div> \
<form id="register-face-form" role="form" class="form-horizontal"> \
<div class="container-fluid"> \
  <div class="panel panel-default"> \
  <div class="panel-heading"> \
    <button data-toggle="collapse" data-target="#register-face-body">Register Face</button> \
    <label class="form-check-label"><input id="enable-camera" class="form-check-input" type="checkbox" checked> Enable Camera</label> \
  </div> \
  <div id="register-face-body" class="panel-body collapse"> \
  <div class="form-group row"> \
    <label for="Name" class="col-form-label col-sm-2">Name:</label> \
    <div class="col-sm-10"><input id="register-face-name" type="text" class="form-control" id="name"></div> \
  </div> \
  <div class="form-group row"> \
    <label for="Organization" class="col-form-label col-sm-2">Organization:</label> \
    <div class="col-sm-10"><input id="register-face-organization" type="text" class="form-control" id="organization"></div> \
  </div> \
  <div class="form-group row"> \
    <label for="email" class="col-form-label col-sm-2">Email Address:</label> \
    <div class="col-sm-10"><input id="register-face-email" type="email" class="form-control" id="email"></div> \
  </div> \
  <div class="form-group row"> \
    <label for="linkedin_url" class="col-form-label col-sm-2">LinkedIn URL:</label> \
    <div class="col-sm-10"><input id="register-face-linkedin-url" type="url" class="form-control" id="linkedin_url"></div> \
  </div> \
  <div class="form-group row"> \
    <div class="col-sm-12"><button id="register-face-submit" type="submit" class="btn btn-default">Submit</button></div> \
  </div> \
  </div> \
  </div> \
</div> \
</form> \
',
    headerTitle: 'Camera',
    contentSize: {width: 640, height: 750},
    contentSize: "640 auto"
  });

  document.getElementById('enable-camera').onchange = function() {
    g_enable_camera = document.getElementById('enable-camera').checked;
  };

  document.getElementById('register-face-form').onsubmit = function() {
    return false;
  }

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

  // Option 1: Issues with frequent requests 
  /*
  camera_view.src = "http://localhost:5000/video_frame?" + new Date().getTime();
  */

  // https://capdroid.wordpress.com/2015/03/09/html-download-image-through-ajax-and-display-it/

  // Option 2: Seems to work.
  /*
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      var blob = new Blob([xhr.response], {
          type: xhr.getResponseHeader("Content-Type")
      });
      var imgUrl = window.URL.createObjectURL(blob);
      camera_view.src = imgUrl;
    }
  }
  xhr.responseType = "arraybuffer";
  xhr.open("GET", video_frame_url, true);
  xhr.send();
  */

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
