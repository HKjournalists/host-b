"use strict";

/*
Copyright [2015] [wangbin]
*/

/**
 * 
 * 
 * 
 */
function SwitchProps(){
    /**management ip of switch*/
    this.ip = '';

    this.name = '';

    this.userName = '';

    this.passwd = '';
    
    //array of physical interface
    this.l2ifs = [{port:'', vlanId:'', vtype:'', vmembers:''}];

    //array of l3-interface
    this.l3ifs = [{ifName:'', vlanId:'', ip:'', mask:''}];

    //array of routeInfo
    this.staticRoute = [{destIp:'', nextIp:'', mask:''}];
}



/**Loads a style from a JSONObject
 **/
SwitchProps.load = function(o){
    
};

SwitchProps.prototype={
    
    constructor : SwitchProps,

    check:function(){
        if(!PropsHandler['iup'](this.ip, this.userName, this)){
            return false;
        }
        for(var l2if in this.l2ifs){
            for(var attr in l2if){
                if(typeof PropsHandler[attr] === 'function' &&
                   !PropsHandler[attr](l2if[attr])){
                    return false;
                }
            }
        }
        for(var l3if in this.l3ifs){
            for(var attr in l3if){
                if(typeof PropsHandler[attr] === 'function' &&
                   !PropsHandler[attr](l3if[attr])){
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


