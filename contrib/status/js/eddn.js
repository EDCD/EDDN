secondsToDurationString = function(seconds) {
  var hours   = Math.floor(seconds / 3600);
  var minutes = Math.floor((seconds - (hours * 3600)) / 60);
  var seconds = seconds - (hours * 3600) - (minutes * 60);
  var days = 0;

  if (hours > 24) {
    days = Math.floor(hours / 24)
    hours = Math.floor((seconds - days * 24) / 3600);
  }
  
  if (hours   < 10) {hours   = "0" + hours;}
  if (minutes < 10) {minutes = "0" + minutes;}
  if (seconds < 10) {seconds = "0" + seconds;}
  
  if (days > 0) {
    return days + "d " + hours + ":" + minutes + ":" + seconds;
  }
  else {
    return hours + ":" + minutes + ":" + seconds;
  }
}

displayGatewayStats = function(stats) {
  $("#gateway_inbound_1min").html((stats["inbound"] || {})["1min"] || 0);
  $("#gateway_inbound_5min").html((stats["inbound"] || {})["5min"] || 0);
  $("#gateway_inbound_60min").html((stats["inbound"] || {})["60min"] || 0);
  
  $("#gateway_invalid_1min").html((stats["invalid"] || {})["1min"] || 0);
  $("#gateway_invalid_5min").html((stats["invalid"] || {})["5min"] || 0);
  $("#gateway_invalid_60min").html((stats["invalid"] || {})["60min"] || 0);
  
  $("#gateway_outbound_1min").html((stats["outbound"] || {})["1min"] || 0);
  $("#gateway_outbound_5min").html((stats["outbound"] || {})["5min"] || 0);
  $("#gateway_outbound_60min").html((stats["outbound"] || {})["60min"] || 0);
  d = new Date();
  $("#update_gateway_timestamp").html(d.toString("yyyy-MM-dd HH:mm:ss"));
  $("#gateway_version").html(stats['version'] || "N/A");
  if (stats['uptime']) {
    $("#gateway_uptime").html(secondsToDurationString(stats['uptime']));
  }
  formatStats();
}

displayRelayStats = function(stats) {
  $("#relay_inbound_1min").html((stats["inbound"] || {})["1min"] || 0);
  $("#relay_inbound_5min").html((stats["inbound"] || {})["5min"] || 0);
  $("#relay_inbound_60min").html((stats["inbound"] || {})["60min"] || 0);
  
  $("#relay_outbound_1min").html((stats["outbound"] || {})["1min"] || 0);
  $("#relay_outbound_5min").html((stats["outbound"] || {})["5min"] || 0);
  $("#relay_outbound_60min").html((stats["outbound"] || {})["60min"] || 0);
  d = new Date();
  $("#update_relay_timestamp").html(d.toString("yyyy-MM-dd HH:mm:ss"));
  $("#relay_version").html(stats['version'] || "N/A");
  if (stats['uptime']) {
    $("#relay_uptime").html(secondsToDurationString(stats['uptime']));
  }
  formatStats();
}

formatStats = function() {
  $(".stat").each(function() {
    if ($(this).html() == "0") {
      $(this).addClass("warning");
    }
    else {
      $(this).removeClass("warning");
    }
  });
}

doUpdate = function(url, success, failure) {
  $.ajax({
    dataType: "json",
    url: url,
    success: success,
    failure: failure
  });
}

getGatewayUrl = function() {
  return $("#gateway").val();
}

getRelayUrl = function() {
  return $("#relay").val();
}

$("#gateway").change(function() {alert(); doUpdate(getGatewayUrl(), displayGatewayStats);})
$("#relay").change(function() {doUpdate(getRelayUrl(), displayRelayStats);})

doUpdate(getGatewayUrl(), displayGatewayStats);
doUpdate(getRelayUrl(), displayRelayStats);
setInterval(function() {doUpdate(getGatewayUrl(), displayGatewayStats); doUpdate(getRelayUrl(), displayRelayStats)}, 60000);