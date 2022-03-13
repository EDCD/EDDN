/* vim: wrapmargin=0 textwidth=0 tabstop=4 softtabstop=4 expandtab shiftwidth=4
 */
var eddn_config = {
	updateInterval: 60000,

    eddn_host:          'eddn.edcd.io',
	monitorEndPoint:    'https://eddn.edcd.io/monitor/',

	gatewayStats:       '/stats/',

    relayStats:         '/relay/stats/',

	gateways: [
    	'eddn.edcd.io'
	], //TODO: Must find a way to bind them to monitor

	relays: [
    	'eddn.edcd.io'
	] //TODO: Must find a way to bind them to monitor

};
/* Hard-coded, because even under dev we just use the live URL.  It's
 * really just for picking out things from the schema URLs, i.e. not used
 * to direct the browser anywhere.
 */
eddn_config['schemasURL'] = 'https://eddn.edcd.io/schemas/';
/* If you are actually using different URLs for the actual schemas you could
 * use the following to make it programmatical.
 */
// eddn_config['schemasURL'] = 'https://' + eddn_config.eddn_host + '/dev/schemas/';

