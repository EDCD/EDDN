var updateInterval      = 60000,

    monitorEndPoint     = 'http://eddn-monitor.ed-td.space:9091/',
    
    gatewayBottlePort   = 8080,
    relayBottlePort     = 9090,
    
    relays              = [
        'eddn-gateway.elite-markets.net',
        'eddn-gateway.ed-td.space'
    ]; // Must find a way to bind them to monitor
    
var stats = {
    'gateway' : {},
    'relay'   : {}
}; // Stats placeholder


secondsToDurationString = function(seconds) {
  var hours   = Math.floor(seconds / 3600);
  var minutes = Math.floor((seconds - (hours * 3600)) / 60);
  var seconds = seconds - (hours * 3600) - (minutes * 60);
  var days = 0;

  if (hours > 24) {
    days = Math.floor(hours / 24)
    hours = Math.floor((hours - days * 24) / 3600);
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


var doUpdates = function(type){
    $("select[name=" + type + "] option").each(function(){
        var currentItem = $(this).html(),
            isSelected  = $(this).is(':selected');
        
        $.ajax({
            dataType: "json",
            url: $(this).val(),
            success: function(data){
                d = new Date();
                
                stats[type][currentItem]['lastUpdate']  = d.toString("yyyy-MM-dd HH:mm:ss");
                stats[type][currentItem]['last']        = data;
                
                if(isSelected)
                    showStats(type, currentItem);
                    
                var chart = $("#" + type + " .chart[data-name='" + currentItem + "']").highcharts();
                
                shift = chart.get('inbound').data.length > 60;
                chart.get('inbound').addPoint([d.getTime(), (data['inbound'] || {})['1min'] || 0], true, shift);
                
                shift = chart.get('outbound').data.length > 60;
                chart.get('outbound').addPoint([d.getTime(), (data['outbound'] || {})['1min'] || 0], true, shift);
                
                if(type == 'gateway')
                {
                    shift = chart.get('invalid').data.length > 60;
                    chart.get('invalid').addPoint([d.getTime(), (data['invalid'] || {})['1min'] || 0], true, shift);
                }
            }
        });
    });
};

var showStats = function(type, currentItem){
    var el                  = $('#' + type),
        currentItemStats    = stats[type][currentItem]['last'];
        
    el.find(".inbound_1min").html((currentItemStats['inbound'] || {})['1min'] || 0);
    el.find(".inbound_5min").html((currentItemStats["inbound"] || {})['5min'] || 0);
    el.find(".inbound_60min").html((currentItemStats["inbound"] || {})['60min'] || 0);
    
    if(type == 'gateway')
    {
        el.find(".invalid_1min").html((currentItemStats["invalid"] || {})['1min'] || 0);
        el.find(".invalid_5min").html((currentItemStats["invalid"] || {})['5min'] || 0);
        el.find(".invalid_60min").html((currentItemStats["invalid"] || {})['60min'] || 0);
    }
    
    el.find(".outbound_1min").html((currentItemStats["outbound"] || {})['1min'] || 0);
    el.find(".outbound_5min").html((currentItemStats["outbound"] || {})['5min'] || 0);
    el.find(".outbound_60min").html((currentItemStats["outbound"] || {})['60min'] || 0);
    
    el.find(".update_timestamp").html(stats[type][currentItem]['lastUpdate']);
    el.find(".version").html(currentItemStats['version'] || 'N/A');
    
    if (currentItemStats['uptime'])
        el.find(".uptime").html(secondsToDurationString(currentItemStats['uptime']));
    else
        el.find(".uptime").html('N/A');
        
    el.find(".stat").removeClass("warning").each(function() {
        if ($(this).html() == "0")
            $(this).addClass("warning");
    });
    
    el.find(".chart").hide();
    el.find(".chart[data-name='" + currentItem + "']").show();
    $(window).trigger('resize'); // Fix wrong size in chart
};



/**
 *  Launch monitoring
 */
var start       = function(){
    Highcharts.setOptions({global: {useUTC: false}});
    
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
                
                $('#gateway .charts').append(
                                        $('<div>').addClass('chart')
                                                  .css('width', '100%')
                                                  .attr('data-name', gateway)
                                     );
                                     
                $("#gateway .chart[data-name='" + gateway + "']").highcharts({
                    chart: {
                        type: 'spline', animation: Highcharts.svg,
                        height: 200
                    },
                    title: { text: '', style: {display: 'none'} },
                    xAxis: {
                        type: 'datetime',
                        tickPixelInterval: 150
                    },
                    yAxis: {
                        title: {text: ''},
                        plotLines: [{value: 0, width: 1, color: '#808080'}],
                        min: 0
                    },
                    tooltip: { enabled: false },
                    credits: { enabled: false },
                    exporting: { enabled: false },
                    series: [
                        {id: 'inbound', data: [], name: 'Messages received'}, 
                        {id: 'outbound', data: [], name: 'Messages passed to relay'}, 
                        {id: 'invalid', data: [], name: 'Invalid messages'}
                    ]
                }).hide();
                
                stats['gateway'][gateway] = {};
            });
            
            doUpdates('gateway');
            setInterval(function(){
                doUpdates('gateway');
            }, updateInterval);
        }
    });
    
    // Grab relays
    relays = relays.sort();
    $.each(relays, function(k, relay){
        $("select[name=relay]").append($('<option>', { 
            value: 'http://' + relay + ':' + relayBottlePort + '/stats/',
            text : relay
        }));
                
        $('#relay .charts').append(
                                $('<div>').addClass('chart')
                                          .css('width', '100%')
                                          .attr('data-name', relay)
                             );
                             
        $("#relay .chart[data-name='" + relay + "']").highcharts({
            chart: {
                type: 'spline', animation: Highcharts.svg,
                height: 200,
                events: {
                    load: function(){ setTimeout(function(){$(window).trigger('resize');}, 250); }
                },
                marginRight: 10
            },
            title: { text: '', style: {display: 'none'} },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150
            },
            yAxis: {
                title: {text: ''},
                plotLines: [{value: 0, width: 1, color: '#808080'}],
                min: 0
            },
            tooltip: { enabled: false },
            credits: { enabled: false },
            exporting: { enabled: false },
            series: [
                {id: 'inbound', data: [], name: 'Messages received'}, 
                {id: 'outbound', data: [], name: 'Messages passed to subscribers'}
            ]
        }).hide();
        
        stats['relay'][relay] = {};
    });
    
    doUpdates('relay');
    setInterval(function(){
        doUpdates('relay');
    }, updateInterval);
    
    // Attach events
    $("select[name=gateway]").change(function(){
        showStats('gateway', $(this).find('option:selected').html());
    });
    $("select[name=relay]").change(function(){
        showStats('relay', $(this).find('option:selected').html());
    });    
}

$(document).ready(function(){
    start();
});