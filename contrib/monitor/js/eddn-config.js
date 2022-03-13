/* vim: wrapmargin=0 textwidth=0 tabstop=4 softtabstop=4 expandtab shiftwidth=4
 */
var eddn_config = {
	updateInterval: 60000,

    eddn_host:          'eddn.miggy.org',
	monitorEndPoint: 'https://eddn.miggy.org/dev/monitor/',

	gatewayStats: '/dev/stats/',

    relayStats: '/dev/relay/stats/',
	relayBottlePort: 9110,

	gateways: [
    	'eddn.miggy.org'
	], //TODO: Must find a way to bind them to monitor

	relays: [
    	'eddn.miggy.org'
	] //TODO: Must find a way to bind them to monitor

};
