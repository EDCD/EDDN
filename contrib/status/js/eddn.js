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