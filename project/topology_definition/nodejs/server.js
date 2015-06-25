var http = require('http');
var url = require('url');
var querystring = require('querystring');

exports.run = function(router, handle){
	http.createServer(function(req, res){
		var pathName = url.parse(req.url).pathname;
		//console.log('req.url: '+ req.url + '   pathName: ' + pathname);
		if(req.method === 'GET'){
			router.routeGet(handle['GET'], pathName, res);
		} else if(req.method === 'POST'){
			var postData = '';
			req.on('data', function(chunk){
				postData += chunk;
			});
			req.on('end', function(chunk){
				router.routePost(handle['POST'], pathName, querystring.parse(postData), res);
			});
		}
	}).listen(8765);
	console.log('server is running');
}
