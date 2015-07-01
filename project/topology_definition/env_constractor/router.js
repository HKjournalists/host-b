exports.routeGet = function(handle, pathName, res){
	var ext = pathName.match(/(\.[^.]+|)$/)[0];
	if(ext === ''){
		ext = pathName;
	}
	if (typeof handle[ext] === 'function') {
		handle[ext](res, pathName);
 	} else {
 		console.log("No request handler found for " + pathName);
 	}
}

exports.routePost = function(handle, pathName, queryStr, res){
	if (typeof handle[pathName] === 'function') {
		handle[pathName](res, pathName, queryStr);
 	} else {
 		console.log("No request handler found for " + pathName);
 	}
}