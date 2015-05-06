var updateInterval      = 60000,

    monitorEndPoint     = 'http://eddn-monitor.ed-td.space:9091/',
    
    gatewayBottlePort   = 8080,
    relayBottlePort     = 9090,
    
    relays              = [
        'eddn-gateway.elite-markets.net',
        'eddn-gateway.ed-td.space'
    ];


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

displayStats = function(el, stats){
    el.find(".inbound_1min").html((stats["inbound"] || {})["1min"] || 0);
    el.find(".inbound_5min").html((stats["inbound"] || {})["5min"] || 0);
    el.find(".inbound_60min").html((stats["inbound"] || {})["60min"] || 0);
    
    el.find(".invalid_1min").html((stats["invalid"] || {})["1min"] || 0);
    el.find(".invalid_5min").html((stats["invalid"] || {})["5min"] || 0);
    el.find(".invalid_60min").html((stats["invalid"] || {})["60min"] || 0);
    
    el.find(".outbound_1min").html((stats["outbound"] || {})["1min"] || 0);
    el.find(".outbound_5min").html((stats["outbound"] || {})["5min"] || 0);
    el.find(".outbound_60min").html((stats["outbound"] || {})["60min"] || 0);
    
    d = new Date();
    el.find(".update_timestamp").html(d.toString("yyyy-MM-dd HH:mm:ss"));
    el.find(".version").html(stats['version'] || "N/A");
    
    if (stats['uptime'])
        el.find(".uptime").html(secondsToDurationString(stats['uptime']));
    
    formatStats();
}

displayGatewayStats = function(stats) {
    return displayStats($('#gateway'), stats)
}

displayRelayStats = function(stats) {
  return displayStats($('#relay'), stats)
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

doUpdate = function(url, success) {
  $.ajax({
    dataType: "json",
    url: url,
    success: success
  });
}

getGatewayUrl = function() {
  return $("select[name=gateway]").val();
}

getRelayUrl = function() {
  return $("select[name=relay]").val();
}



/**
 *  Launch monitoring
 */
var start       = function(){
    // Grab gateways from monitor
    $.ajax({
        dataType: "json",
        url: monitorEndPoint + 'getGateways/',
        success: function(gateways){
            gateways = gateways.sort();
            $.each(gateways, function(k, gateway){
                gateway = gateway.replace('tcp://', '');
                gateway = gateway.replace(':8500', '');
                
                $("select[name=gateway]").append($('<option>', { 
                    value: 'http://' + gateway + ':' + gatewayBottlePort + '/stats/',
                    text : gateway
                }));
            });
            doUpdate(getGatewayUrl(), displayGatewayStats);
        }
    });
    
    // Grab relays
    relays = relays.sort();
    $.each(relays, function(k, relay){
        $("select[name=relay]").append($('<option>', { 
            value: 'http://' + relay + ':' + relayBottlePort + '/stats/',
            text : relay
        }));
    });
    
    // Attach events
    $("select[name=gateway]").change(function() {doUpdate(getGatewayUrl(), displayGatewayStats);})
    $("select[name=relay]").change(function() {doUpdate(getRelayUrl(), displayRelayStats);})
    
    // Start updates interval
    setInterval(doUpdates, updateInterval);
    doUpdates();
}
var doUpdates   = function(){
    doUpdate(getGatewayUrl(), displayGatewayStats);
    doUpdate(getRelayUrl(), displayRelayStats);
}
$(document).ready(function(){
    start();
});