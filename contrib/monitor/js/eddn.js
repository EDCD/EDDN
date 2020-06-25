/* vim: wrapmargin=0 textwidth=0 tabstop=4 softtabstop=4 expandtab shiftwidth=4
 */
var updateInterval      = 60000,

    monitorEndPoint     = 'https://eddn.edcd.io:9091/',

    //gatewayBottlePort   = 8080,
    gatewayBottlePort   = 4430,
    relayBottlePort     = 9090,

    gateways            = [
        'eddn.edcd.io'
    ], //TODO: Must find a way to bind them to monitor

    relays              = [
        'eddn.edcd.io'
    ]; //TODO: Must find a way to bind them to monitor

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
	var match = /^https:\/\/eddn.edcd.io\/schemas\/(\w)(\w*)\/(\d+)$/.exec(str);
	if(match)
	{
		return match[1].toUpperCase() + match[2] + " v" + match[3];
	}

	var match = /^https:\/\/eddn.edcd.io\/schemas\/(\w)(\w*)\/(\d+)\/test$/.exec(str);
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

var softwaresSort     = { field: 'today', order: 'desc' }; // Very first load sort order
var softwaresData     = new Array();     // The last data we got from API
var softwaresViewData = new Array(); // The data for the current view
var softwaresVersion  = {};

var softwaresJsGridDataController = function () {
    console.log('softwares -> jsGrid.controller.loadData() returning %o', softwaresViewData);
    return softwaresViewData;
};

/*
 * Create a new jsGrid and HighChart for Softwares
 */
var softwaresNewJsGrid = function () {
    var chart  = $('#software .chart').highcharts(),
        series = chart.get('softwares');
    var newJsGrid;
    if (currentDrillDown) {
        newJsGrid = $("#table-softwares").jsGrid({
            width: "100%",
    
            filtering: false,
            inserting: false,
            editing: false,
            sorting: true,
    
            controller: {
                loadData: softwaresJsGridDataController,
            },
    
            fields: [
                {
                    title: "",
                    width: "30px",
                    sorting: false,
                    readOnly: true,
                },
                {
                    title: currentDrillDown,
                    width: "50%",
                    name: "name",
                    type: "text",
                    align: "left",
                    readOnly: true,
                },
                {
                    title: "Today hits",
                    name: "today",
                    type: "number",
                    align: "right",
                    readOnly: true,
                    css: "stat today",
                    itemTemplate: formatNumberJsGrid,
                },
                {
                    title: "Yesterday hits",
                    name: "yesterday",
                    type: "number",
                    align: "right",
                    readOnly: true,
                    css: "stat yesterday",
                    itemTemplate: formatNumberJsGrid,
                },
                {
                    title: "Total hits",
                    name: "total",
                    type: "number",
                    align: "right",
                    readOnly: true,
                    css: "stat total",
                    itemTemplate: formatNumberJsGrid,
                },
            ],
    
            rowRenderer: function(item) {
                softwareSplit = item.name.split(' | ');
                return $('<tr>').attr('data-type', 'parent').attr('data-name', item.name).on('mouseover', function(){
                    chart.get('software-' + makeSlug(item.name)).setState('hover');
                    chart.tooltip.refresh(chart.get('software-' + makeSlug(item.name)));
                }).on('mouseout', function(){
                    if(chart.get('software-' + makeSlug(item.name)))
                        chart.get('software-' + makeSlug(item.name)).setState('');
                    chart.tooltip.hide();
                }).append(
                    $('<td>').addClass('square').attr('data-name', item.name).css('width', '30px').css('padding', '8px')
                ).append(
                    $('<td>').html('<strong>' + item.name + '</strong>').css('cursor','pointer').css('width', '50%')
                )
                .append(
                    $('<td>').addClass(item.today ? 'stat today' : 'warning').html(formatNumber(item.today || 0))
                )
                .append(
                    $('<td>').addClass(item.yesterday ? 'stat yesterday' : 'warning').html(formatNumber(item.yesterday || 0))
                )
                .append(
                    $('<td>').addClass('stat total').html('<strong>' + formatNumber(item.total) + '</strong>')
                );
            },
    
            onRefreshed: function(grid) {
                // Gets fired when sort is changed
                //console.log('softwares.onRefreshed(): %o', grid);
                if (grid && grid.grid && grid.grid._sortField) {
                    //console.log(' grid sort is: %o, %o', grid.grid._sortField.name, grid.grid._sortOrder);
                    //console.log(' saved sort is: %o', softwaresSort);
                    if (softwaresSort.field != grid.grid._sortField.name) {
                        softwaresSort.field = grid.grid._sortField.name;
                        $("#table-softwares").jsGrid("sort", softwaresSort);
                        return;
                    } else {
                        softwaresSort.order = grid.grid._sortOrder;
                    }
                    $.each(softwaresViewData, function(key, values) {

                        if(!chart.get('software-' + makeSlug(values.name)))
                        {
                            //console.log('Adding data point sort is: %o', softwaresSort.field);
                            // Populates the data into the overall Software pie chart as per current sort column
                            series.addPoint({id: 'software-' + makeSlug(values.name), name: values.name, y: parseInt(values[grid.grid._sortField.name]), drilldown: true}, false);
                        } else {
                            // Populates the data into the overall Software pie chart as per current sort column
                            chart.get('software-' + makeSlug(values.name)).update(parseInt(values[grid.grid._sortField.name]), false);
                        }
                        $(".square[data-name='" + this.name + "']").css('background', chart.get('software-' + makeSlug(values.name)).color);
                    });
                }
                chart.redraw();
            },
        });

        $("#table-softwares table .jsgrid-header-row th:eq(0)").html('<span class="glyphicon glyphicon-remove"></span>')
        .css('cursor','pointer')
        .on('click', function(event) {
            //console.log('softwares: click! %o', event);
            currentDrillDown = false;
            /*
             * No longer drilling down, so need to reset the data
             */
            softwaresViewData = new Array();
            softwaresData.forEach(function(software, s) {
                softwareSplit = software.name.split(' | ');
                name = softwareSplit[0];
                var sw = softwaresViewData.find(o => o.name === name);
                if(!sw) {
                    softwaresViewData.push({ 'name': name, 'today': software.today, 'yesterday': software.yesterday, 'total': software.total});
                    sw = softwaresViewData.find(o => o.name === name);
                } else {
                    sw['today'] += software.today;
                    sw['yesterday'] += software.yesterday;
                    sw['total'] += software.total;
                }
            });
            softwaresNewJsGrid();
        });

    } else {
        // Not drilling down
        newJsGrid = $("#table-softwares").jsGrid({
            width: "100%",
        
            filtering: false,
            inserting: false,
            editing: false,
            sorting: true,
            autoload: false,
        
            controller: {
                loadData: softwaresJsGridDataController
            },
        
            fields: [
                {
                    title: "",
                    width: "30px",
                    sorting: false,
                    readOnly: true,
                },
                {
                    title: "Software name",
                    width: "50%",
                    name: "name",
                    type: "text",
                    align: "left",
                    readOnly: true,
                },
                {
                    title: "Today hits",
                    name: "today",
                    type: "number",
                    align: "right",
                    readOnly: true,
                    css: "stat today",
                    itemTemplate: formatNumberJsGrid,
                },
                {
                    title: "Yesterday hits",
                    name: "yesterday",
                    type: "number",
                    align: "right",
                    readOnly: true,
                    css: "stat yesterday",
                    itemTemplate: formatNumberJsGrid,
                },
                {
                    title: "Total hits",
                    name: "total",
                    type: "number",
                    align: "right",
                    readOnly: true,
                    css: "stat total",
                    itemTemplate: formatNumberJsGrid,
                },
            ],
    
            rowRenderer: function(item) {
                return $('<tr>').attr('data-type', 'parent').attr('data-name', item.name).on('click', function(event){
                    //console.log('softwares: click! %o', event);
                    currentDrillDown = item.name;
    
                    /*
                     * The data we need for this drilldown
                     */
                    softwaresViewData = new Array();
                    softwaresData.forEach(function(software, s) {
                        softwareSplit = software.name.split(' | ');
                        var name = "";
                        if (currentDrillDown == softwareSplit[0]) {
                            name = softwareSplit[1];
                        } else {
                            return true;
                        }
                        var sw = softwaresViewData.find(o => o.name === name);
                        if(!sw) {
                            softwaresViewData.push({ 'name': name, 'today': software.today, 'yesterday': software.yesterday, 'total': software.total});
                            sw = softwaresViewData.find(o => o.name === name);
                        } else {
                            sw['today'] += software.today;
                            sw['yesterday'] += software.yesterday;
                            sw['total'] += software.total;
                        }
                    });
                    softwaresNewJsGrid();
                }).on('mouseover', function(){
                    chart.get('software-' + makeSlug(item.name)).setState('hover');
                    chart.tooltip.refresh(chart.get('software-' + makeSlug(item.name)));
                }).on('mouseout', function(){
                    if(chart.get('software-' + makeSlug(item.name)))
                        chart.get('software-' + makeSlug(item.name)).setState('');
                    chart.tooltip.hide();
                }).append(
                    $('<td>').addClass('square').attr('data-name', item.name).css('width', '30px').css('padding', '8px')
                ).append(
                    $('<td>').html('<strong>' + item.name + '</strong>').css('cursor','pointer').css('width', '50%')
                )
                .append(
                    $('<td>').addClass(item.today ? 'stat today' : 'warning').html(formatNumber(item.today || 0))
                )
                .append(
                    $('<td>').addClass(item.yesterday ? 'stat yesterday' : 'warning').html(formatNumber(item.yesterday || 0))
                )
                .append(
                    $('<td>').addClass('stat total').html('<strong>' + formatNumber(item.total) + '</strong>')
                );
            },
        
            onRefreshed: function(grid) {
                // Gets fired when sort is changed
                //console.log('softwares.onRefreshed(): %o', grid);
                if (grid && grid.grid && grid.grid._sortField) {
                    //console.log(' grid sort is: %o, %o', grid.grid._sortField.name, grid.grid._sortOrder);
                    //console.log(' saved sort is: %o', softwaresSort);
                    if (softwaresSort.field != grid.grid._sortField.name) {
                        softwaresSort.field = grid.grid._sortField.name;
                        $("#table-softwares").jsGrid("sort", softwaresSort);
                        return;
                    } else {
                        softwaresSort.order = grid.grid._sortOrder;
                    }
                    $.each(softwaresViewData, function(key, values) {

                        if(!chart.get('software-' + makeSlug(values.name)))
                        {
                            //console.log('Adding data point sort is: %o', softwaresSort.field);
                            // Populates the data into the overall Software pie chart as per current sort column
                            series.addPoint({id: 'software-' + makeSlug(values.name), name: values.name, y: parseInt(values[grid.grid._sortField.name]), drilldown: true}, false);
                        } else {
                            // Populates the data into the overall Software pie chart as per current sort column
                            chart.get('software-' + makeSlug(values.name)).update(parseInt(values[grid.grid._sortField.name]), false);
                        }
                        $(".square[data-name='" + this.name + "']").css('background', chart.get('software-' + makeSlug(values.name)).color);
                    });
                }
                chart.redraw();
            },
        });
    }
    
    // Because we're using a controller for data we need to trigger it
    $("#table-softwares").jsGrid("loadData");
    // Re-apply the last stored sor
    $("#table-softwares").jsGrid("sort", softwaresSort);

    // Populate the chart with the data
    series.remove(false);
    series = chart.addSeries({
        id: 'softwares',
        name: 'Softwares',
        type: 'pie',
        data: []
    });
    $.each(softwaresViewData, function(key, values) {
        field = $("#table-softwares").jsGrid("getSorting").field;
        if(!chart.get('software-' + makeSlug(values.name)))
        {
            //console.log('Adding data point sort is: %o', softwaresSort.field);
            // Populates the data into the overall Software pie chart as per current sort column
            series.addPoint({id: 'software-' + makeSlug(values.name), name: values.name, y: parseInt(values[field]), drilldown: true}, false);
        } else {
            // Populates the data into the overall Software pie chart as per current sort column
            chart.get('software-' + makeSlug(values.name)).update(parseInt(values[field]), false);
        }
        $(".square[data-name='" + this.name + "']").css('background', chart.get('software-' + makeSlug(values.name)).color);
    });
    
    chart.redraw();

    $('#software').find(".stat").removeClass("warning").each(function() {
        if ($(this).html() == "0")
            $(this).addClass("warning");
    });

    return newJsGrid;
}

var doUpdateSoftwares = function()
{
    var dToday      = new Date(),
        dYesterday  = new (function(d){ d.setDate(d.getDate()-1); return d})(new Date),

        yesterday   = dYesterday.getUTCFullYear() + '-' + ("0" + (dYesterday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dYesterday.getUTCDate())).slice(-2),
        today       = dToday.getUTCFullYear() + '-' + ("0" + (dToday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dToday.getUTCDate())).slice(-2);

    /*
     * Gathering the data per a "<softwareName> | <softwareVersion>" tuple takes two calls.
     *
     *  1) First a /getSoftwares/?dateStart=<yesterday>&dateEnd=<today>
     *
     *      This returns an object with two top level keys, one for each date.  The value
     *      for each is another object with "<softwareName> | <softwareVersion>" as each key,
     *      and the value as the count for that tuple.
     *
     *  2) Then the lifetime totals for each "<softwareName> | <softwareVersion>" tuple, from
     *     /getTotalSoftwares/
     *
     *      This returns an object with "<softwareName> | <softwareVersion>" tuples as keys,
     *      the values being the lifetime totals for each tuple.
     *
     *  The calls are nested here, so only the inner .ajax() has access to the totality of data.
     */
    $.ajax({
        dataType: "json",
        url: monitorEndPoint + 'getSoftwares/?dateStart=' + yesterday + '&dateEnd = ' + today,
        success: function(softwaresTodayYesterday){
            $.ajax({
                dataType: "json",
                url: monitorEndPoint + 'getTotalSoftwares/',
                success: function(softwaresTotals){
                    // Might happen when nothing is received...
                    if(softwaresTodayYesterday[yesterday] == undefined)
                        softwaresTodayYesterday[yesterday] = [];
                    if(softwaresTodayYesterday[today] == undefined)
                        softwaresTodayYesterday[today] = [];

                    /*
                     * Prepare 'softwaresData' dictionary:
                     *
                     * 	key: software name, including the version
                     * 	value: dictionary with counts for: today, yesterday, total (all time)
                     */
                    softwaresData = new Array();
                    $.each(softwaresTotals, function(softwareName, total){
                        var sw = { 'name': softwareName, 'today': 0, 'yesterday': 0, 'total': parseInt(total)};

                        sw['today'] += parseInt(softwaresTodayYesterday[today][softwareName] || 0);
                        sw['yesterday'] += parseInt(softwaresTodayYesterday[yesterday][softwareName] || 0);

                        softwaresData.push(sw);
                    });

                    /*
                     * Now the data we need for the current view (overall data or a drilldown of a software)
                     */
                    softwaresViewData = new Array();
                    softwaresData.forEach(function(software, s) {
                        softwareSplit = software.name.split(' | ');
                        var name = "";
                        if (currentDrillDown) {
                            if (currentDrillDown == softwareSplit[0]) {
                                name = softwareSplit[1];
                            } else {
                                return true;
                            }
                        } else {
                            name = softwareSplit[0];
                        }
                        var sw = softwaresViewData.find(o => o.name === name);
                        if(!sw) {
                            softwaresViewData.push({ 'name': name, 'today': software.today, 'yesterday': software.yesterday, 'total': software.total});
                            sw = softwaresViewData.find(o => o.name === name);
                        } else {
                            sw['today'] += software.today;
                            sw['yesterday'] += software.yesterday;
                            sw['total'] += software.total;
                        }
                    });

                    // Ensure we have the jsGrid added
                    if (! $("#table-softwares").length ) {
                        // Append a new DIV for this jsGrid to the "#software #tables" div
                        $('#software #tables').append(
                            $('<div/>').addClass('jsGridTable').attr('id', 'table-softwares')
                        );
                    } else {
                        // Store the last selected sort so we can apply it to the new version
                        softwaresSort = $("#table-softwares").jsGrid("getSorting");
                    }

                    newJsGrid = softwaresNewJsGrid();

                    $('#software').find(".update_timestamp").html(d.toString("yyyy-MM-dd HH:mm:ss"));
                }
            });
        }
    });
}


var schemasSort = { field: 'today', order: 'desc' }; // Very first load sort order
var schemasData    = new Array();

var doUpdateSchemas = function()
{
    var dToday      = new Date(),
        dYesterday  = new (function(d){ d.setDate(d.getDate()-1); return d})(new Date),

        yesterday   = dYesterday.getUTCFullYear() + '-' + ("0" + (dYesterday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dYesterday.getUTCDate())).slice(-2),
        today       = dToday.getUTCFullYear() + '-' + ("0" + (dToday.getUTCMonth() +　1)).slice(-2) + '-' + ("0" + (dToday.getUTCDate())).slice(-2);

    $.ajax({
        dataType: "json",
        url: monitorEndPoint + 'getSchemas/?dateStart=' + yesterday + '&dateEnd = ' + today,
        success: function(schemasTodayYesterday){
            // Might happen when nothing is received...
            if(schemasTodayYesterday[yesterday] == undefined)
                schemaTodayYesterday[yesterday] = [];
            if(schemasTodayYesterday[today] == undefined)
                schemasTodayYesterday[today] = [];

            $.ajax({
                dataType: "json",
                url: monitorEndPoint + 'getTotalSchemas/',
                success: function(schemasTotals){
                    var chart   = $('#schemas .chart').highcharts(),
                        series  = chart.get('schemas');

                    /*
                     * Prepare 'schemasData' dictionary
                     */
                    schemasData = new Array();
                    $.each(schemasTotals, function(schema, total) {
                        schemaName = schema.replace('http://schemas.elite-markets.net/eddn/', 'https://eddn.edcd.io/schemas/');
                        // Due to the schema renames and us merging them there could be more than one
                        // row of data input per schema
                        var sch = schemasData.find(o => o.name === schemaName);
                        if (!sch) {
                            schemasData.push({ 'name': schemaName, 'today': 0, 'yesterday': 0, 'total': parseInt(total)});
                            sch = schemasData.find(o => o.name === schemaName);
                        } else {
                            sch['total'] += parseInt(total);
                        }
                    });

                    // Today
                    $.each(schemasTodayYesterday[today], function(schema, hits) {
                        schemaName = schema.replace('http://schemas.elite-markets.net/eddn/', 'https://eddn.edcd.io/schemas/');
                        var sch = schemasData.find(o => o.name === schemaName);
                        sch['today'] += parseInt(hits);
                    });
                    // Yesterday
                    $.each(schemasTodayYesterday[yesterday], function(schema, hits) {
                        schemaName = schema.replace('http://schemas.elite-markets.net/eddn/', 'https://eddn.edcd.io/schemas/');
                        var sch = schemasData.find(o => o.name === schemaName);
                        sch['yesterday'] += parseInt(hits);
                    });

                    // Ensure we have the jsGrid added
                    if (! $("#table-schemas").length ) {
                        // Append a new DIV for this jsGrid to the "#schemas #tables" div
                        $('#schemas #tables').append(
                            $('<div/>').addClass('jsGridTable').attr('id', 'table-schemas')
                        );
                    } else {
                        // Store the last selected sort so we can apply it to the new version
                        schemasSort = $("#table-schemas").jsGrid("getSorting");
                    }

                    newJsGrid = $("#table-schemas").jsGrid({
                        width: "100%",

                        filtering: false,
                        inserting: false,
                        editing: false,
                        sorting: true,
                        autoload: false,

                        data: schemasData,

                        fields: [
                            {
                                title: "",
                                width: "30px",
                                name: "chartslug",
                                sorting: false,
                                readOnly: true,
                            },
                            {
                                title: "Schema",
                                width: "50%",
                                name: "name",
                                type: "text",
                                align: "left",
                                readOnly: true,
                            },
                            {
                                title: "Today hits",
                                name: "today",
                                type: "number",
                                align: "right",
                                readOnly: true,
                                css: "stat today",
                                itemTemplate: formatNumberJsGrid,
                            },
                            {
                                title: "Yesterday hits",
                                name: "yesterday",
                                type: "number",
                                align: "right",
                                readOnly: true,
                                css: "stat yesterday",
                                itemTemplate: formatNumberJsGrid,
                            },
                            {
                                title: "Total hits",
                                name: "total",
                                type: "number",
                                align: "right",
                                readOnly: true,
                                css: "stat total",
                                itemTemplate: formatNumberJsGrid,
                            },
                        ],

                        rowRenderer: function(item) {
                            return $('<tr>').attr('data-type', 'parent').attr('data-name', item.name).on('mouseover', function(){
                                chart.get('schema-' + makeSlug(item.name)).setState('hover');
                                chart.tooltip.refresh(chart.get('schema-' + makeSlug(item.name)));
                            }).on('mouseout', function(){
                                if(chart.get('schema-' + makeSlug(item.name)))
                                    chart.get('schema-' + makeSlug(item.name)).setState('');
                                chart.tooltip.hide();
                            }).append(
                                $('<td>').addClass('square').attr('data-name', item.name).css('width', '30px').css('padding', '8px')
                            ).append(
                                $('<td>').html('<strong>' + makeName(item.name) + '</strong>').css('cursor','pointer').css('width', '50%')
                            )
                            .append(
                                $('<td>').addClass(item.today ? 'stat today' : 'warning').html(formatNumber(item.today || 0))
                            )
                            .append(
                                $('<td>').addClass(item.yesterday ? 'stat yesterday' : 'warning').html(formatNumber(item.yesterday || 0))
                            )
                            .append(
                                $('<td>').addClass('stat total').html('<strong>' + formatNumber(item.total) + '</strong>')
                            );
                        },

                        onRefreshed: function(grid) {
                            // Gets fired when sort is changed
                            //console.log('softwares.onRefreshed(): %o', grid);
                            if (grid && grid.grid && grid.grid._sortField) {
                                //console.log(' grid sort is: %o, %o', grid.grid._sortField.name, grid.grid._sortOrder);
                                //console.log(' saved sort is: %o', schemasSort);
                                if (schemasSort.field != grid.grid._sortField.name) {
                                    schemasSort.field = grid.grid._sortField.name;
                                    $("#table-schemas").jsGrid("sort", schemasSort);
                                    return;
                                } else {
                                    schemasSort.order = grid.grid._sortOrder;
                                }
                                $.each(schemasData, function(key, values) {
                                    if(!chart.get('schema-' + makeSlug(values.name)))
                                    {
                                        //console.log('Adding data point sort is: %o', schemasSort.field);
                                        // Populates the data into the overall Software pie chart as per current sort column
                                        series.addPoint({id: 'schema-' + makeSlug(values.name), name: values.name, y: parseInt(values[grid.grid._sortField.name]), drilldown: true}, false);
                                    } else {
                                        // Populates the data into the overall Software pie chart as per current sort column
                                        chart.get('schema-' + makeSlug(values.name)).update(parseInt(values[grid.grid._sortField.name]), false);
                                    }
                                    $(".square[data-name='" + this.name + "']").css('background', chart.get('schema-' + makeSlug(values.name)).color);
                                });
                            }
                            chart.redraw();
                        },
                    });

                    // Re-apply the last stored sort
                    $("#table-schemas").jsGrid("sort", schemasSort);

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

/*
 * JS Grid related functions
 */

/*
 * Nicely format a number for jsGrid
 */
formatNumberJsGrid = function(value, item) {
    return value.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,");
}

$(document).ready(function(){
    start();
});
