var server = require("./server");
var router = require("./router");
var requestHandlers = require("./requestHandlers");

var handle = {
	GET : {},
	POST : {}
};
handle['GET']['/'] = requestHandlers.index;
handle['GET']['.html'] = requestHandlers.html;
handle['GET']['.js'] = requestHandlers.js;
handle['GET']['.css'] = requestHandlers.css;
handle['GET']['.png'] = requestHandlers.bin;
handle['GET']['.gif'] = requestHandlers.bin;
handle['GET']['.ico'] = requestHandlers.bin;
handle['POST']['/submitJson'] = requestHandlers.submitJson;
handle['POST']['/getDevInfo'] = requestHandlers.getDevInfo;

server.run(router, handle);

