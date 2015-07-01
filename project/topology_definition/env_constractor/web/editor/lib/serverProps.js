"use strict";

/*
Copyright [2015] [wangbin]
*/

/**
 * 
 * 
 * 
 * 
 * 
 * 
 */
function ServerProps(){
    /**management ip of switch*/
    this.ip = null;

    this.name = null;

    this.userName = null;

    this.passwd = null;

    //array of interface
    this.ifs = [{ifName:'', ip:'', mask:''}];

    //array of static route info
    this.staticRoute = [{destIp:'', nextIp:'', iface:'', mask:''}];
}



/**Loads a style from a JSONObject
 **/
ServerProps.load = function(o){
    
};

ServerProps.prototype={
    
    constructor : ServerProps,

    check:function(){
        if(!PropsHandler['iup'](this.ip, this.userName, this)){
            return false;
        }
        for(var l2if in this.ifs){
            for(var attr in l2if){
                if(typeof PropsHandler[attr] === 'function' &&
                   !PropsHandler[attr](l2if[attr])){
                    return false;
                }
            }
        }
        for(var sr in this.staticRoute){
            for(var attr in sr){
                if(typeof PropsHandler[attr] === 'function' &&
                   !PropsHandler[attr](sr[attr])){
                    return false;
                }
            }
        }
        return true;
    }

};


