var updateInterval      = 60000,

    monitorEndPoint     = 'https://eddn.edcd.io:9091/',
    
    //gatewayBottlePort   = 8080,
    gatewayBottlePort   = 4430,
    relayBottlePort     = 9090,
    
    gateways            = [
        'eddn.edcd.io',
        //'eddn-gateway.elite-markets.net'
    ], // Must find a way to bind them to monitor
    
    relays              = [
        'eddn.edcd.io',
        //'eddn-relay.elite-markets.net'
    ]; // Must find a way to bind them to monitor
    
var stats = {
    'gateways' : {},
    'relays'   : {}
}; // Stats placeholder

formatNumber = function(num) {
    return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,")
}

var makeSlug = function(str) {
	var slugcontent_hyphens = str.replace(/\s/g,'-');
	var finishedslug = slugcontent_hyphens.replace(/[^a-zA-Z0-9\-]/g,'');
	return finishedslug.toLowerCase();
}

var makeName =  function(str) {
    var match = /^http:\/\/schemas.elite-markets.net\/eddn\/(\w)(\w*)\/(\d+)$/.exec(str);
    
    if(match)
    {
        return match[1].toUpperCase() + match[2] + " v" + match[3];
    }
    
    var match = /^http:\/\/schemas.elite-markets.net\/eddn\/(\w)(\w*)\/(\d+)\/test$/.exec(str);
    
    if(match)
    {
        return match[1].toUpperCase() + match[2] + " v" + match[3] + " [TEST]";
    }
    
    return str;
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


var drillDownSoftware = false;
var currentDrillDown  = false;

var softwaresTotal    = {};
var softwaresVersion  = {};

var doUpdateSoftwares = function()
{
    var dToday      = new Date(),
        dYesterday  = new (function(d){ d.setDate(d.getDate()-1); return d})(new Date),
        
        yesterday   = dYesterday.getUTCFullYear() + '-' + ("0" + (dYesterday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dYesterday.getUTCDate())).slice(-2),
        today       = dToday.getUTCFullYear() + '-' + ("0" + (dToday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dToday.getUTCDate())).slice(-2);
    
    $.ajax({
        dataType: "json",
        url: monitorEndPoint + 'getSoftwares/?dateStart=' + yesterday + '&dateEnd = ' + today,
        success: function(softwares){
            $.ajax({
                dataType: "json",
                url: monitorEndPoint + 'getTotalSoftwares/',
                success: function(softwaresTotalData){
                    var chart   = $('#software .chart').highcharts(),
                        series  = chart.get('softwares');
                    
                    // Count total by software, all versions included
                    var softwareName = {};
                    $.each(softwaresTotalData, function(software, hits){
                        softwareSplit = software.split(' | ');
                        
                        if(!softwareName[softwareSplit[0]])
                            softwareName[softwareSplit[0]] = [0,0, parseInt(hits)];
                        else
                            softwareName[softwareSplit[0]][2] += parseInt(hits);
                        
                        // Might happen when nothing is received...
                        if(softwares[yesterday] == undefined)
                            softwares[yesterday] = [];
                        if(softwares[today] == undefined)
                            softwares[today] = [];
                        
                        softwareName[softwareSplit[0]][0] += parseInt(softwares[today][software] || 0);
                        softwareName[softwareSplit[0]][1] += parseInt(softwares[yesterday][software] || 0);
                            
                    });
                    
                    // Sort by total DESC
                    var tmp = new Array();
                    $.each(softwareName, function(software, hits){ tmp.push({name: software, today: hits[0], yesterday: hits[1], total: hits[2]}); });
                    tmp.sort(function(a,b) { return b.total - a.total; });
                    softwaresTotal = tmp;
                    
                    $('#software .table tbody').empty();
                    
                    // Prepare drilldowns
                    $.each(softwaresTotalData, function(software, hits){
                        softwareSplit = software.split(' | ');
                        
                        $('#software .table tbody').append(
                            newTr = $('<tr>').attr('data-type', 'drilldown').attr('data-parent', softwareSplit[0]).attr('data-name', software).on('mouseover', function(){
                                chart.get('software-' + makeSlug(software)).setState('hover');
                                chart.tooltip.refresh(chart.get('software-' + makeSlug(software)));
                            }).on('mouseout', function(){
                                chart.get('software-' + makeSlug(software)).setState('');
                                chart.tooltip.hide();
                            }).append(
                                $('<td>').addClass('square')
                            ).append(
                                $('<td>').html('<strong>' + softwareSplit[1] + '</strong>')
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
                        
                        if(!drillDownSoftware)
                            newTr.hide();
                        else
                            if(softwareSplit[0] != currentDrillDown)
                                newTr.hide();
                        
                        if(!softwaresVersion[softwareSplit[0]])
                            softwaresVersion[softwareSplit[0]] = {};
                        if(!softwaresVersion[softwareSplit[0]][software])
                            softwaresVersion[softwareSplit[0]][software] = {
                                today: (softwares[today][software] || 0), yesterday: (softwares[yesterday][software] || 0), total: hits
                            };
                    });
                    
                    // Add main softwares
                    $.each(softwaresTotal, function(key, values){
                        $('#software .table tbody').append(
                            newTr = $('<tr>').attr('data-type', 'parent').attr('data-name', values.name).on('click', function(event){
                                event.stopImmediatePropagation();
                                currentSoftware = $(this).attr('data-name');
                                
                                if(!drillDownSoftware)
                                {
                                    currentDrillDown = currentSoftware;
                                    
                                    $('#software .table thead th:eq(0)').html('<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>')
                                                                         .css('cursor','pointer')
                                                                         .on('click', function(){
                                                                             currentDrillDown = false;
                                                                             chart.showDrillUpButton();
                                                                             $('#software .table thead th:eq(0)').html('');
                                                                             $('#software .table thead th:eq(1)').html('');
                                                                             $('#software .table tbody tr[data-type=parent]').show();
                                                                             $('#software .table tbody tr[data-type=drilldown]').hide();
                                                                             drillDownSoftware = !drillDownSoftware;
                                                                             doUpdateSoftwares();
                                                                             chart.drillUp();
                                                                         });
                                    $('#software .table thead th:eq(1)').html(currentSoftware);
                                    $('#software .table tbody tr[data-type=parent]').hide();
                                    $('#software .table tbody tr[data-type=drilldown][data-parent="' + currentSoftware + '"]').show();
                                    
                                    var currentData = [];
                                    
                                    $.each(softwaresVersion[currentSoftware], function(key, value){
                                        currentData.push({
                                            id: 'software-' + makeSlug(key), 
                                            name: key, 
                                            y: parseInt(value.total)
                                        });
                                    });
                                    
                                    chart.addSeriesAsDrilldown(chart.get('software-' + makeSlug(currentSoftware)), {
                                        id: 'softwareDrilldown-' + makeSlug(currentSoftware),
                                        type: 'pie',
                                        name: currentSoftware,
                                        data: currentData
                                    });
                                    chart.redraw();
                                    
                                    if(chart.drillUpButton)
                                        chart.drillUpButton = chart.drillUpButton.destroy();
                                    
                                    $('#software .table tbody tr[data-type=drilldown][data-parent="' + currentSoftware + '"]').each(function(){
                                        $(this).find('.square').css('background', chart.get('software-' + makeSlug($(this).attr('data-name'))).color);
                                    });
                                }
                                
                                drillDownSoftware = !drillDownSoftware;
                            }).on('mouseover', function(){
                                chart.get('software-' + makeSlug(values.name)).setState('hover');
                                chart.tooltip.refresh(chart.get('software-' + makeSlug(values.name)));
                            }).on('mouseout', function(){
                                if(chart.get('software-' + makeSlug(values.name)))
                                    chart.get('software-' + makeSlug(values.name)).setState('');
                                chart.tooltip.hide();
                            }).append(
                                $('<td>').addClass('square')
                            ).append(
                                $('<td>').html('<strong>' + values.name + '</strong>').css('cursor','pointer')
                            )
                            .append(
                                $('<td>').addClass('stat today').html(formatNumber(values.today || 0))
                            )
                            .append(
                                $('<td>').addClass('stat yesterday').html(formatNumber(values.yesterday || 0))
                            )
                            .append(
                                $('<td>').addClass('stat total').html('<strong>' + formatNumber(values.total) + '</strong>')
                            )
                        );
                        
                        if(!drillDownSoftware)
                        {
                            if(!chart.get('software-' + makeSlug(values.name)))
                            {
                                series.addPoint({id: 'software-' + makeSlug(values.name), name: values.name, y: parseInt(values.total), drilldown: true}, false);
                            }
                            else
                                chart.get('software-' + makeSlug(values.name)).update(parseInt(values.total), false);
                                
                            newTr.find('.square').css('background', chart.get('software-' + makeSlug(values.name)).color);
                        }
                        
                        if(drillDownSoftware)
                            newTr.hide();
                    });
                    
                    if(drillDownSoftware)
                        $('#software .table tbody tr[data-type=drilldown][data-parent="' + currentDrillDown + '"]').each(function(){
                            $(this).find('.square').css('background', chart.get('software-' + makeSlug($(this).attr('data-name'))).color);
                        });
                    
                    chart.redraw();
                    
                    $('#software').find(".stat").removeClass("warning").each(function() {
                        if ($(this).html() == "0")
                            $(this).addClass("warning");
                    });
                    
                    $('#software').find(".update_timestamp").html(d.toString("yyyy-MM-dd HH:mm:ss"));
                }
            });
        }
    });
}


var doUpdateUploaders = function()
{
    var dToday      = new Date(),
        dYesterday  = new (function(d){ d.setDate(d.getDate()-1); return d})(new Date),
        
        yesterday   = dYesterday.getUTCFullYear() + '-' + ("0" + (dYesterday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dYesterday.getUTCDate())).slice(-2),
        today       = dToday.getUTCFullYear() + '-' + ("0" + (dToday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dToday.getUTCDate())).slice(-2);
    
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
                        if(uploader.length > 32)
                            truncateUploader = jQuery.trim(uploader).substring(0, 32)/*.split(" ").slice(0, -1).join(" ")*/ + "..."
                        else
                            truncateUploader = uploader
                        
                        // Might happen when nothing is received...  
                        if(uploaders[yesterday] == undefined)
                            uploaders[yesterday] = [];
                        if(uploaders[today] == undefined)
                            uploaders[today] = [];
                        
                        $('#uploaders .table tbody').append(
                            newTr = $('<tr>').attr('data-name', uploader).on('mouseover', function(){
                                chart.get('uploader-' + makeSlug(uploader)).setState('hover');
                                chart.tooltip.refresh(chart.get('uploader-' + makeSlug(uploader)));
                            }).on('mouseout', function(){
                                chart.get('uploader-' + makeSlug(uploader)).setState('');
                                chart.tooltip.hide();
                            }).append(
                                $('<td>').addClass('square')
                            ).append(
                                $('<td>').html('<strong>' + truncateUploader + '</strong>')
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
                            
                        newTr.find('.square').css('background', chart.get('uploader-' + makeSlug(uploader)).color);
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
    var dToday      = new Date(),
        dYesterday  = new (function(d){ d.setDate(d.getDate()-1); return d})(new Date),
        
        yesterday   = dYesterday.getUTCFullYear() + '-' + ("0" + (dYesterday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dYesterday.getUTCDate())).slice(-2),
        today       = dToday.getUTCFullYear() + '-' + ("0" + (dToday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dToday.getUTCDate())).slice(-2);
    
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
                        // Might happen when nothing is received...
                        if(schemas[yesterday] == undefined)
                            schemas[yesterday] = [];
                        if(schemas[today] == undefined)
                            schemas[today] = [];
                            
                        var slug = makeSlug(schema);
                        var name = makeName(schema);
                        
                        $('#schemas .table tbody').append(
                            newTr = $('<tr>').attr('data-name', schema).on('mouseover', function(){
                                chart.get('schema-' + slug).setState('hover');
                                chart.tooltip.refresh(chart.get('schema-' +slug));
                            }).on('mouseout', function(){
                                chart.get('schema-' + slug).setState('');
                                chart.tooltip.hide();
                            }).append(
                                $('<td>').addClass('square')
                            ).append(
                                $('<td>').html('<strong>' + name + '</strong>')
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
                        
                        if(!chart.get('schema-' + slug))
                            series.addPoint({id: 'schema-' + slug, name: name, y: parseInt(hits)}, false);
                        else
                            chart.get('schema-' + slug).update(parseInt(hits), false);
                            
                        newTr.find('.square').css('background', chart.get('schema-' + slug).color);
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
                
                if(type == 'gateways')
                {
                    shift = chart.get('invalid').data.length > 60;
                    chart.get('invalid').addPoint([d.getTime(), (data['invalid'] || {})['1min'] || 0], true, shift);
                }
                
                if(type == 'relays')
                {
                    shift = chart.get('duplicate').data.length > 60;
                    chart.get('duplicate').addPoint([d.getTime(), (data['duplicate'] || {})['1min'] || 0], true, shift);
                }
                
                shift = chart.get('outbound').data.length > 60;
                chart.get('outbound').addPoint([d.getTime(), (data['outbound'] || {})['1min'] || 0], true, shift);
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
        
        el.find(".outdated_1min").html((currentItemStats["outdated"] || {})['1min'] || 0);
        el.find(".outdated_5min").html((currentItemStats["outdated"] || {})['5min'] || 0);
        el.find(".outdated_60min").html((currentItemStats["outdated"] || {})['60min'] || 0);
    }
    
    if(type == 'relays')
    {
        el.find(".duplicate_1min").html((currentItemStats["duplicate"] || {})['1min'] || 0);
        el.find(".duplicate_5min").html((currentItemStats["duplicate"] || {})['5min'] || 0);
        el.find(".duplicate_60min").html((currentItemStats["duplicate"] || {})['60min'] || 0);
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
    //gateways = gateways.sort();
    $.each(gateways, function(k, gateway){
        gateway = gateway.replace('tcp://', '');
        gateway = gateway.replace(':8500', '');
        
        $("select[name=gateways]").append($('<option>', { 
            value: 'https://' + gateway + ':' + gatewayBottlePort + '/stats/',
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
                {id: 'invalid', data: [], name: 'Invalid messages', zIndex: 1},
                {id: 'outdated', data: [], name: 'Outdated messages', zIndex: 1},
                {id: 'outbound', data: [], name: 'Messages passed to relay', zIndex: 200}
            ]
        }).hide();
        
        stats['gateways'][gateway] = {};
    });
    
    doUpdates('gateways');
    setInterval(function(){
        doUpdates('gateways');
    }, updateInterval);
    
    // Grab relays
    //relays = relays.sort();
    $.each(relays, function(k, relay){
        $("select[name=relays]").append($('<option>', { 
            value: 'https://' + relay + ':' + relayBottlePort + '/stats/',
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
                {id: 'duplicate', data: [], name: 'Messages duplicate', zIndex: 1}, 
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
    $('#software .chart').highcharts({
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
            name: 'Softwares',
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
}

$(document).ready(function(){
    start();
});
