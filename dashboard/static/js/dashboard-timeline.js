var DASHBOARD_TIMELINE = (function (my) {

var g_next_item_id = 0;
var g_items = new vis.DataSet();
var g_refresh_id;
var g_timeline;
var g_timeline_delay = 1000;

var generate_items = function(max) {
  var len = Math.random() * max;
  var result = [];
  for (var i = 0; i < len; i++) {
    g_items.add({id: g_next_item_id, content: "item " + g_next_item_id,
      start: new Date(new Date().getTime() + g_next_item_id*10)
    });
    g_next_item_id++;
  }
};

var setup_timeline = function() {
  var myPanel = $.jsPanel({
    container: '#container-body',
    position: 'center-top',
    position: 'center-bottom',
    position: 'center',
    content: ' \
<div id="mytimeline"></div> \
<input id="start" type="button" value="Start"> \
<input id="stop" type="button" value="Stop"> \
<input id="reset" type="button" value="Reset"> \
',
    headerTitle: 'Timeline',
    contentSize: "640 auto",
    contentSize: {width: 640, height: 240},
    contentSize: {width: 640, height: 340}
  });

  var container = document.getElementById('mytimeline');
  // Configuration for the Timeline
  // specify options
  var options = {
    start: new Date(),
    end: new Date(new Date().getTime() + 1000000),
    end: new Date(new Date().getTime() + 1000*60),
    rollingMode: true,
    editable: true,
    showCurrentTime: true,
    // timeAxis: {scale: 'minute'},
    // zoomMin: 1000*30,
    // zoomMax: 1000*60*60*24
  };

  // create a Timeline
  g_timeline = new vis.Timeline(container, g_items, null, options);
  g_timeline.zoomIn(0.1);
  // g_timeline.toggleRollingMode();

/* DBG set up panel as clickable.
  container.onclick = function (event) {
    var props = g_timeline.getEventProperties(event);
    console.log(props);
    url = 'http://localhost:8080/Unknown';
    url = 'https://www.linkedin.com/in/joe-bond-7a11652';
    name = 'unknown';
    name = '_blank';
    window.open(url, name);
  }
*/

  document.getElementById('start').onclick = function() {
    if (!g_refresh_id) {
      // g_refresh_id = setInterval(update_items, 1000, [1,2,3,4,5,6,7,8,9,10]);
      g_refresh_id = setTimeout(update_items, g_timeline_delay);
    }
  };

  document.getElementById('stop').onclick = function() {
    if (g_refresh_id) {
      clearInterval(g_refresh_id);
      g_refresh_id = null;
    }
  };

  document.getElementById('reset').onclick = function() {
    // g_timeline.destroy();
    // g_items = new vis.DataSet();
    location.reload();
  };

  // setTimeout(update_items, g_timeline_delay, [1,2,3,4,5,6,7,8,9,10]);
  // g_refresh_id = setInterval(update_items, g_timeline_delay);
  g_refresh_id = setTimeout(update_items, g_timeline_delay);
};

var update_items = function(items) {
  //DBG console.log("update_items");
  //DBG generate_items(5);
  //g_refresh_id = setTimeout(update_items, g_timeline_delay);

  var log_url = "get-face-logs";

  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      //DBG console.log(xhr.response);
      var result = xhr.response;

      //DBG alert("result.len: " + result.length);
      for (var i = 0; i < result.length; i++) {
        var fields = result[i].split(",");
        var log_name = fields[0];
        // var log_time = new Date(new Date().getTime() + g_next_item_id*10);
        var log_time = new Date(fields[1]);
        var content = log_name;
        var linkedin_url = '';
        if (fields.length > 2) {
          linkedin_url = fields[2];
          content = '<a href="' + linkedin_url + '" target="' + log_name + '">' + log_name + '</a>';
          //DBG console.log('content: ' + content);
        }
        //DBG console.log(log_time);
        g_items.add({id: g_next_item_id, content: content,
          start: log_time
        });
        g_next_item_id++;
      }

      g_refresh_id = setTimeout(update_items, g_timeline_delay);
    } else if (xhr.readystate == 4 && xhr.status != 200) {
      alert(xhr.status);
      g_refresh_id = setTimeout(update_items, g_timeline_delay);
    }
  }
  xhr.onerror = function() {
    alert(xhr.status);
    g_refresh_id = setTimeout(update_items, g_timeline_delay);
  }

  xhr.responseType = "json";
  xhr.open("GET", log_url, true);
  xhr.send();
};

setup_timeline();

}(DASHBOARD_TIMELINE || {}));
