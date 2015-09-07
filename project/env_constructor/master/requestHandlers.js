var fs = require('fs');
var exec = require("child_process").exec;
var basePath = './web/editor';

exports.index = function(res, pathName){
    var file = basePath + '/light-editor.html';
    fs.readFile(file, 'utf-8', function(err, data){
        if (err) {
            console.error(err);
        } else {
            res.writeHead(200, {"Content-Type": "text/html"});
            res.write(data);
            res.end();
        }       
    });
}

//请求html页面
exports.html = function(res, pathName){
	fs.readFile(basePath + pathName, 'utf-8', function(err, data){
		if (err) {
 			console.error(err);
 		} else {
 			res.writeHead(200, {"Content-Type": "text/html"});
    		res.write(data);
    		res.end();
 		}		
	});
}

//请求js脚本文件
exports.js = function(res, pathName){
	fs.readFile(basePath + pathName, 'utf-8', function(err, data){
        if (err) {
            console.error(err);
        } else {
            res.writeHead(200, {"Content-Type": "application/javascript"});
            res.write(data);
            res.end();
        }
    });
} 

//请求css文件
exports.css = function(res, pathName){
    fs.readFile(basePath + pathName, 'utf-8', function(err, data){
        if (err) {
            console.error(err);
        } else {
            res.writeHead(200, {"Content-Type": "text/css"});
            res.write(data);
            res.end();
        }
    });
} 

//请求二进制文件，如gif、png、ico等等
exports.bin = function(res, pathname){
    fs.readFile('./web/editor' + pathname, function(err, data){
        if (err) {
            console.error(err);
        } else {
            res.writeHead(200, {"Content-Type": "text/plain"});
            res.write(data);
            res.end();
        }
    });
}

//提交json字符串设置设备属性
exports.submitJson = function(res, pathname, queryStr){
    var data = queryStr['data'];
    console.log('Post data reviced:\n%s\n\n', data);
    //j = JSON.parse(data);
    //console.log(j);
    exec('cd scripts && python main.py --set -d \'' + data + '\'', function (error, stdout, stderr) {
        console.log('Stdout from python script:\n%s\n\n', stdout);
        if(error){
            console.log('Stderr from python script:\n%s\n\n', error);
        }
        ret = stdout;
        //console.log('ret: ' + ret);
        res.writeHead(200, {'Content-Type': 'application/x-www-form-urlencoded'});
        res.write(ret);
        res.end();
    });

}

//获取设备信息
exports.getDevInfo = function(res, pathname, queryStr){
    var data = queryStr['data'];    //接收到的JSON是字符串形式
    console.log('reviced data from client:\n%s\n\n', data);
    j = JSON.parse(data);  //由JSON字符串转换为JSON对象
    //console.log(j);
    cmd = 'cd scripts && python main.py --get-' + 
           j['dev'] + ' --' + j['qtype'] + ' -d \'' + data + '\'';
    exec(cmd, function (error, stdout, stderr) {
        console.log('Stdout from python script:\n%s\n\n', stdout);
        if(error){
            console.log('Stderr from python script:\n%s\n\n', error);
        }
        //json = eval('(' + stdout.trim() + ')');
        //ret = JSON.stringify(stdout.trim());
        ret = stdout;
        //console.log('ret: ' + ret);
        res.writeHead(200, {'Content-Type': 'application/x-www-form-urlencoded'});
        res.write(ret);
        res.end();
    });
}

//获取设备联通性
exports.getConnectivity = function(res, pathname, queryStr){
    var data = queryStr['data'];    //接收到的JSON是字符串形式
    console.log('reviced data from client:\n%s\n\n', data);
    j = JSON.parse(data);  //由JSON字符串转换为JSON对象
    //console.log(j);
    cmd = 'cd scripts && python main.py --get-conn -d \'' + data + '\'';
    exec(cmd, function (error, stdout, stderr) {
        console.log('Stdout from python script:\n%s\n\n', stdout);
        if(error){
            console.log('Stderr from python script:\n%s\n\n', error);
        }
        //json = eval('(' + stdout.trim() + ')');
        //ret = JSON.stringify(stdout.trim());
        ret = stdout;
        //console.log('ret: ' + ret);
        res.writeHead(200, {'Content-Type': 'application/x-www-form-urlencoded'});
        res.write(ret);
        res.end();
    });
}

//获取设备邻居
exports.getNbrs = function(res, pathname, queryStr){
    var data = queryStr['data'];    //接收到的JSON是字符串形式
    console.log('reviced data from client:\n%s\n\n', data);
    j = JSON.parse(data);  //由JSON字符串转换为JSON对象
    //console.log(j);
    cmd = 'cd scripts && python main.py --get-nbrs -d \'' + data + '\'';
    exec(cmd, function (error, stdout, stderr) {
        console.log('Stdout from python script:\n%s\n\n', stdout);
        if(error){
            console.log('Stderr from python script:\n%s\n\n', error);
        }
        //json = eval('(' + stdout.trim() + ')');
        //ret = JSON.stringify(stdout.trim());
        ret = stdout;
        //console.log('ret: ' + ret);
        res.writeHead(200, {'Content-Type': 'application/x-www-form-urlencoded'});
        res.write(ret);
        res.end();
    });
}