var updateInterval      = 60000,

    monitorEndPoint     = 'http://eddn-monitor.ed-td.space:9091/',
    
    gatewayBottlePort   = 8080,
    relayBottlePort     = 9090,
    
    gateways            = [
        'eddn-gateway.elite-markets.net',
        'eddn-gateway.ed-td.space'
    ]; // Must find a way to bind them to monitor,
    
    relays              = [
        'eddn-relay.elite-markets.net',
        'eddn-relay.ed-td.space'
    ]; // Must find a way to bind them to monitor
    
var stats = {
    'gateways' : {},
    'relays'   : {}
}; // Stats placeholder

formatNumber = function(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,")
}

makeSlug = function(str) {
	var slugcontent_hyphens = str.replace(/\s/g,'-');
	var finishedslug = slugcontent_hyphens.replace(/[^a-zA-Z0-9\-]/g,'');
	return finishedslug.toLowerCase();
}

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


var doUpdateSoftwares = function()
{
    var yesterday   = Date.parse('yesterday').toString("yyyy-MM-dd")
    var today       = Date.parse('today').toString("yyyy-MM-dd")
    
    $.ajax({
        dataType: "json",
        url: monitorEndPoint + 'getSoftwares/?dateStart=' + yesterday + '&dateEnd = ' + today,
        success: function(softwares){
            $.ajax({
                dataType: "json",
                url: monitorEndPoint + 'getTotalSoftwares/',
                success: function(softwaresTotal){
                    var chart   = $('#softwares .chart').highcharts(),
                        series  = chart.get('softwares');
                    
                    $('#softwares .table tbody').empty();
                    
                    $.each(softwaresTotal, function(software, hits){
                        $('#softwares .table tbody').append(
                            $('<tr>').attr('data-name', software).on('mouseover', function(){
                                chart.get('software-' + makeSlug(software)).setState('hover');
                                chart.tooltip.refresh(chart.get('software-' + makeSlug(software)));
                            }).on('mouseout', function(){
                                chart.get('software-' + makeSlug(software)).setState('');
                                chart.tooltip.hide();
                            }).append(
                                $('<td>').html('<strong>' + software + '</strong>')
                            )
                            .append(
                                $('<td>').addClass('stat today').html(formatNumber(softwares[today][software] || 0))
                            )
                            .append(
                                $('<td>').addClass('stat yesterday').html(formatNumber(softwares[yesterday][software] || 0))
                            )
                            .append(
                                $('<td>').addClass('stat total').html('<strong>' + formatNumber(hits) + '</strong>')
                            )
                        );
                        
                        if(!chart.get('software-' + makeSlug(software)))
                            series.addPoint({id: 'software-' + makeSlug(software), name: software, y: parseInt(hits)}, false);
                        else
                            chart.get('software-' + makeSlug(software)).update(parseInt(hits), false);
                    });
                    
                    chart.redraw();
                    
                    $('#softwares').find(".stat").removeClass("warning").each(function() {
                        if ($(this).html() == "0")
                            $(this).addClass("warning");
                    });
                    
                    $('#softwares').find(".update_timestamp").html(d.toString("yyyy-MM-dd HH:mm:ss"));
                }
            });
        }
    });
}


var doUpdateUploaders = function()
{
    var yesterday   = Date.parse('yesterday').toString("yyyy-MM-dd")
    var today       = Date.parse('today').toString("yyyy-MM-dd")
    
    $.ajax({
        dataType: "json",
        url: monitorEndPoint + 'getUploaders/?dateStart=' + yesterday + '&dateEnd = ' + today,
        success: function(uploaders){
            $.ajax({
                dataType: "json",
                url: monitorEndPoint + 'getTotalUploaders/',
                success: function(uploadersTotal){
                    var chart   = $('#uploaders .chart').highcharts(),
                        series  = chart.get('uploaders');
                    
                    $('#uploaders .table tbody').empty();
                    
                    $.each(uploadersTotal, function(uploader, hits){
                        $('#uploaders .table tbody').append(
                            $('<tr>').attr('data-name', uploader).on('mouseover', function(){
                                chart.get('uploader-' + makeSlug(uploader)).setState('hover');
                                chart.tooltip.refresh(chart.get('uploader-' + makeSlug(uploader)));
                            }).on('mouseout', function(){
                                chart.get('uploader-' + makeSlug(uploader)).setState('');
                                chart.tooltip.hide();
                            }).append(
                                $('<td>').html('<strong>' + uploader + '</strong>')
                            )
                            .append(
                                $('<td>').addClass('stat today').html(formatNumber(uploaders[today][uploader] || 0))
                            )
                            .append(
                                $('<td>').addClass('stat yesterday').html(formatNumber(uploaders[yesterday][uploader] || 0))
                            )
                            .append(
                                $('<td>').addClass('stat total').html('<strong>' + formatNumber(hits) + '</strong>')
                            )
                        );
                        
                        if(!chart.get('uploader-' + makeSlug(uploader)))
                            series.addPoint({id: 'uploader-' + makeSlug(uploader), name: uploader, y: parseInt(hits)}, false);
                        else
                            chart.get('uploader-' + makeSlug(uploader)).update(parseInt(hits), false);
                    });
                    
                    chart.redraw();
                    
                    $('#uploaders').find(".stat").removeClass("warning").each(function() {
                        if ($(this).html() == "0")
                            $(this).addClass("warning");
                    });
                    
                    $('#uploaders').find(".update_timestamp").html(d.toString("yyyy-MM-dd HH:mm:ss"));
                }
            });
        }
    });
}


var doUpdateSchemas = function()
{
    var yesterday   = Date.parse('yesterday').toString("yyyy-MM-dd")
    var today       = Date.parse('today').toString("yyyy-MM-dd")
    
    $.ajax({
        dataType: "json",
        url: monitorEndPoint + 'getSchemas/?dateStart=' + yesterday + '&dateEnd = ' + today,
        success: function(schemas){
            $.ajax({
                dataType: "json",
                url: monitorEndPoint + 'getTotalSchemas/',
                success: function(schemasTotal){
                    var chart   = $('#schemas .chart').highcharts(),
                        series  = chart.get('schemas');
                    
                    $('#schemas .table tbody').empty();
                    
                    $.each(schemasTotal, function(schema, hits){
                        $('#schemas .table tbody').append(
                            $('<tr>').attr('data-name', schema).on('mouseover', function(){
                                chart.get('schema-' + makeSlug(schema)).setState('hover');
                                chart.tooltip.refresh(chart.get('schema-' + makeSlug(schema)));
                            }).on('mouseout', function(){
                                chart.get('schema-' + makeSlug(schema)).setState('');
                                chart.tooltip.hide();
                            }).append(
                                $('<td>').html('<strong>' + schema + '</strong>')
                            )
                            .append(
                                $('<td>').addClass('stat today').html(formatNumber(schemas[today][schema] || 0))
                            )
                            .append(
                                $('<td>').addClass('stat yesterday').html(formatNumber(schemas[yesterday][schema] || 0))
                            )
                            .append(
                                $('<td>').addClass('stat total').html('<strong>' + formatNumber(hits) + '</strong>')
                            )
                        );
                        
                        if(!chart.get('schema-' + makeSlug(schema)))
                            series.addPoint({id: 'schema-' + makeSlug(schema), name: schema, y: parseInt(hits)}, false);
                        else
                            chart.get('schema-' + makeSlug(schema)).update(parseInt(hits), false);
                    });
                    
                    chart.redraw();
                    
                    $('#schemas').find(".stat").removeClass("warning").each(function() {
                        if ($(this).html() == "0")
                            $(this).addClass("warning");
                    });
                    
                    $('#schemas').find(".update_timestamp").html(d.toString("yyyy-MM-dd HH:mm:ss"));
                }
            });
        }
    });
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
                
                if(type == 'gateways')
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
    
    if(type == 'gateways')
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
    
    // Grab gateways
    gateways = gateways.sort();
    $.each(gateways, function(k, gateway){
        gateway = gateway.replace('tcp://', '');
        gateway = gateway.replace(':8500', '');
        
        $("select[name=gateways]").append($('<option>', { 
            value: 'http://' + gateway + ':' + gatewayBottlePort + '/stats/',
            text : gateway
        }));
        
        $('#gateways .charts').append(
                                $('<div>').addClass('chart')
                                          .css('width', '100%')
                                          .attr('data-name', gateway)
                             );
                             
        $("#gateways .chart[data-name='" + gateway + "']").highcharts({
            chart: {
                type: 'spline', animation: Highcharts.svg
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
                {id: 'inbound', data: [], name: 'Messages received', zIndex: 300}, 
                {id: 'outbound', data: [], name: 'Messages passed to relay', zIndex: 200}, 
                {id: 'invalid', data: [], name: 'Invalid messages', zIndex: 1}
            ]
        }).hide();
        
        stats['gateways'][gateway] = {};
    });
    
    doUpdates('gateways');
    setInterval(function(){
        doUpdates('gateways');
    }, updateInterval);
    
    // Grab relays
    relays = relays.sort();
    $.each(relays, function(k, relay){
        $("select[name=relays]").append($('<option>', { 
            value: 'http://' + relay + ':' + relayBottlePort + '/stats/',
            text : relay
        }));
                
        $('#relays .charts').append(
                                $('<div>').addClass('chart')
                                          .css('width', '100%')
                                          .attr('data-name', relay)
                             );
                             
        $("#relays .chart[data-name='" + relay + "']").highcharts({
            chart: {
                type: 'spline', animation: Highcharts.svg,
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
                {id: 'inbound', data: [], name: 'Messages received', zIndex: 300}, 
                {id: 'outbound', data: [], name: 'Messages passed to subscribers', zIndex: 200}
            ]
        }).hide();
        
        stats['relays'][relay] = {};
    });
    
    doUpdates('relays');
    setInterval(function(){
        doUpdates('relays');
    }, updateInterval);
    
    // Grab software from monitor
    $('#softwares .chart').highcharts({
        chart: {
            type: 'pie', animation: Highcharts.svg
        },
        title: { text: '', style: {display: 'none'} },
        credits: { enabled: false },
        tooltip: { headerFormat: '', pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>' },
        legend: { enabled: false },
        plotOptions: {pie: {allowPointSelect: false,dataLabels: { enabled: false }}},
        series: [{
            id: 'softwares',
            type: 'pie',
            data: []
        }]
    });
    
    doUpdateSoftwares();
    setInterval(function(){
        doUpdateSoftwares();
    }, updateInterval);
    
    // Grab uploader from monitor
    $('#uploaders .chart').highcharts({
        chart: {
            type: 'pie', animation: Highcharts.svg
        },
        title: { text: '', style: {display: 'none'} },
        credits: { enabled: false },
        tooltip: { headerFormat: '', pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>' },
        legend: { enabled: false },
        plotOptions: {pie: {allowPointSelect: false,dataLabels: { enabled: false }}},
        series: [{
            id: 'uploaders',
            type: 'pie',
            data: []
        }]
    });
    
    doUpdateUploaders();
    setInterval(function(){
        doUpdateUploaders();
    }, updateInterval);
    
    // Grab schema from monitor
    $('#schemas .chart').highcharts({
        chart: {
            type: 'pie', animation: Highcharts.svg
        },
        title: { text: '', style: {display: 'none'} },
        credits: { enabled: false },
        tooltip: { headerFormat: '', pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>' },
        legend: { enabled: false },
        plotOptions: {pie: {allowPointSelect: false,dataLabels: { enabled: false }}},
        series: [{
            id: 'schemas',
            type: 'pie',
            data: []
        }]
    });
    
    doUpdateSchemas();
    setInterval(function(){
        doUpdateSchemas();
    }, updateInterval); 
    
    // Attach events
    $("select[name=gateways]").change(function(){
        showStats('gateways', $(this).find('option:selected').html());
    });
    $("select[name=relays]").change(function(){
        showStats('relays', $(this).find('option:selected').html());
    });
    
    $('#schemas .table tbody tr').on('', function(){
        
    });
}

$(document).ready(function(){
    start();
});