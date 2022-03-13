/* vim: wrapmargin=0 textwidth=0 tabstop=4 softtabstop=4 expandtab shiftwidth=4
 */
var eddn_config = {
	updateInterval: 60000,

    eddn_host:          'eddn.edcd.io',
	monitorEndPoint: 'https://eddn.edcd.io/dev/monitor/',

	gatewayStats: '/dev/stats/',

    relayStats: '/dev/relay/stats/',
	relayBottlePort: 9110,

	gateways: [
    	'eddn.edcd.io'
	], //TODO: Must find a way to bind them to monitor

	relays: [
    	'eddn.edcd.io'
	] //TODO: Must find a way to bind them to monitor

};
