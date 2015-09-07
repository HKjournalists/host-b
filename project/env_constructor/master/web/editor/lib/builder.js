"use strict";

/*
Copyright [2014] [Diagramo]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/**
 * This object is responsable for creating and updating the properties for figures.
 * Right now the the properties for a figure are present in a specially designated
 * panel AND, for texts, a popup editor, so the functionality is split between
 * the classic (old) panel and new popeditor.
 *
 * @constructor
 * @this {Builder}
 * 
 *  Builder allows for an {Array} of {BuilderProperty}'s to be displayed in a property panel,
 *  edited values update the owner
 *  @author Zack Newsham <zack_newsham@yahoo.co.uk>
 **/
function Builder(){
    
}

/**Image base path*/
Builder.IMAGE_BASE_PATH = './assets/images/';

/**Path to fill icon image*/
Builder.IMAGE_FILL_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-fill.png' ;

/**Path to stroke icon image*/
Builder.IMAGE_STROKE_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-stroke.png' ;

/**Path to line width icon image*/
Builder.IMAGE_LINEWIDTH_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-linewidth.png' ;

/**Line (dashed) style icon image*/
Builder.IMAGE_LINESTYLE_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-linestyle.png' ;

/**Path to start style icon image*/
Builder.IMAGE_STARTSTYLE_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-startstyle.png' ;

/**Path to end style icon image*/
Builder.IMAGE_ENDSTYLE_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-endstyle.png' ;

/**Path to width icon image*/
Builder.IMAGE_WIDTH_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-h-resize.png' ;

/**Path to height icon image*/
Builder.IMAGE_HEIGHT_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-v-resize.png' ;

/**Path to URL style icon image*/
Builder.IMAGE_URL_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-url.png' ;

/**Path to text style icon image*/
Builder.IMAGE_TEXT_ICON_PATH = Builder.IMAGE_BASE_PATH + 'prop-icon-text.png' ;


/**Creates a {Builder} out of JSON parsed object
 *@param {JSONObject} o - the JSON parsed object
 *@return {Builder} a newly constructed Builder
 *@author Alex Gheorghiu <alex@scriptoid.com>
 **/
//Builder.load = function(o){
//    var newBuilder = new Builder();
//    newBuilder.properties = BuilderProperty.loadArray(o.properties);
//    newBuilder.figureId = o.figureId;
//    return newBuilder;
//}

/**
 *Creates the property panel for a shape {Figure} or {Connector}
 *@param {DOMObject} DOMObject - the div of the properties panel
 *@param {Figure} shape - the figure for which the properties will be displayed
 **/
Builder.constructPropertiesPanel = function(DOMObject, shape) {
    for(var i = 0; i < shape.properties.length; i++){
        // regExp to avoid properties of Text editor
        // && /(props\.)\.*/g.test(shape.properties[i].property) === false
        if (/(primitives\.\d+|middleText)\.(str|size|font|align|underlined|style\.fillStyle)/g.test(shape.properties[i].property) === false 
            && /(props\.)\.*/g.test(shape.properties[i].property) === false ) {
            shape.properties[i].injectInputArea(DOMObject, shape.id);
        }
    }
};

/**
 *Creates the property panel for a Text primitive of shape {Figure} and returns it
 *@param {DOMObject} textEditor - the <div> of the properties panel (declared inside editor page)
 *@param {DOMObject} textEditorTools - the <div> of the text editor's tools (declared insider editor page)
 *@param {Figure} shape - the figure - parent of Text primitive
 *@param {Number} textPrimitiveId - the id value of Text primitive child of figure for which the properties will be displayed
 *
 *@return {TextEditorPopup} - new instance of TextEditorPopup after init
 *  @author Artyom Pokatilov <artyom.pokatilov@gmail.com>
 **/
Builder.constructTextPropertiesPanel = function(textEditor, textEditorTools, shape, textPrimitiveId) {
    var textEditor = new TextEditorPopup(textEditor, textEditorTools, shape, textPrimitiveId);
    textEditor.init();

    return textEditor;
};

//wb mod
Builder.constructConfigPanel = function(configDiv, shape, coords) {
    //console.log('constructConfigPanel')
    var cfgPanel = new ConfigPopup(configDiv, shape, coords);
    cfgPanel.init();

    return cfgPanel;
};

/*wb mod
* 建立设备信息面板
*/
Builder.constructDevInfo = function(configDiv, figureId, devType, queryType) {
    var infoPanel = new devInfoPopup(configDiv, figureId, devType, queryType);
    infoPanel.init();
    return infoPanel;
};

/** wb mod
 * 建立联通性面板
 * @param {conConnDiv} - 面板的父div
 * @param {connId} - 连接线对象的id
 * @param {coords} - 双击鼠标的位置
 **/
Builder.constructConnInfo = function(conConnDiv, connId, coords) {
    var infoPanel = new connInfoPopup(conConnDiv, connId, coords);
    infoPanel.init();
    return infoPanel;
};

/** wb mod
 * 建立邻居信息面板
 * @param {conConnDiv} - 面板的父div
 * @param {figureId} - 连接线对象的id
 * @param {coords} - 鼠标位置
 **/
Builder.constructNbrsInfo = function(nbrsDiv, figureId, coords) {
    var infoPanel = new nbrsInfoPopup(nbrsDiv, figureId);
    infoPanel.init();
    return infoPanel;
};

/**
 *Creates the properties for main CanvasProps
 *@param {DOMObject} DOMObject - the div of the properties panel
 *@param {CanvasProps} canvasProps - the CanvasProps for which the properties will be displayed
 **/
Builder.constructCanvasPropertiesPanel = function(DOMObject, canvasProps){
    var div = document.createElement("div");
    var icon;

    // colorPicker plugin requires div to be already appended to the DOM
    DOMObject.appendChild(div);

    //title
    var titleDiv = document.createElement("div");
    titleDiv.className = 'label title';
    titleDiv.textContent = 'Page Setup';
    div.appendChild(titleDiv);

    //separator
    var separator = document.createElement("hr");
    div.appendChild(separator);

    //fill color
    var colorDiv = document.createElement("div");
    colorDiv.className = "line";

    var currentColor = canvasProps.getFillColor();
    var uniqueId = new Date().getTime();

    var labelDiv = document.createElement("div");
    labelDiv.className = "label";
    labelDiv.textContent = "Background";

    /* wb mod 20150604 : delete icon
    icon = new Image();
    icon.className = 'prop-icon';
    icon.src = Builder.IMAGE_FILL_ICON_PATH;
    labelDiv.appendChild(icon);
    */

    colorDiv.appendChild(labelDiv);

    var colorSelectorDiv = document.createElement("div");
    colorSelectorDiv.id = 'colorSelector' + uniqueId;
    colorSelectorDiv.className = 'color-selector';

    var colorInput = document.createElement("input");
    colorInput.type = "text";
    colorInput.id = 'colorpickerHolder' + uniqueId;
    colorInput.value = currentColor;
    colorSelectorDiv.appendChild(colorInput);

    colorDiv.appendChild(colorSelectorDiv);

    div.appendChild(colorDiv);

    var colorPicker = document.getElementById('colorpickerHolder'+uniqueId);

    //let plugin do the job
    $(colorPicker).colorPicker();

    //on change update the canvasProps
    colorPicker.onchange = function() {
        var newColor = colorPicker.value;
        //Did we change fill color?
        if(canvasProps.getFillColor() !== newColor) {
            var cmd = new CanvasChangeColorCommand(newColor);
            cmd.execute();
            History.addUndo(cmd);

            //trigger a repaint;
            draw();
        }
    };

    //width
    var divWidth = document.createElement("div");
    divWidth.className = 'label';
    divWidth.textContent = 'Width';

    icon = new Image();
    icon.className = 'prop-icon';
    icon.src = Builder.IMAGE_WIDTH_ICON_PATH;
    divWidth.appendChild(icon);

    var inputWidth = document.createElement("input");
    inputWidth.type = "text";
    inputWidth.className = "text"; //required for onkeydown
    inputWidth.value = canvasProps.getWidth();
    divWidth.appendChild(inputWidth);

    div.appendChild(divWidth);

    //height
    var divHeight = document.createElement("div");
    divHeight.className = 'label';
    divHeight.textContent = 'Height';

    icon = new Image();
    icon.className = 'prop-icon';
    icon.src = Builder.IMAGE_HEIGHT_ICON_PATH;
    divHeight.appendChild(icon);

    var inputHeight = document.createElement("input");
    inputHeight.type = "text";
    inputHeight.className = "text"; //required for onkeydown
    inputHeight.value = canvasProps.getHeight();
    divHeight.appendChild(inputHeight);

    div.appendChild(divHeight);

    //button block: Update and Fit options
    var divButton = document.createElement("div");

    //update button
    var btnUpdate = document.createElement("input");
    btnUpdate.setAttribute("type", "button");
    btnUpdate.setAttribute("value", "Update");

    btnUpdate.onclick = function(){
        //update canvas props
        
        Log.group("builder.js->constructCanvasPropertiesPanel()->Canvas update");
        //Log.info('Nr of actions in Undo system: ' + History.ACTIONS.length);

        // Did we entered number value for width?
        var widthVal = Number(inputWidth.value);
        if (isNaN(widthVal)) {
            widthVal = canvasProps.getWidth();
            inputWidth.value = widthVal;
        }

        var heightVal = Number(inputHeight.value);
        if (isNaN(heightVal)) {
            heightVal = canvasProps.getHeight();
            inputHeight.value = heightVal;
        }

        //Did we change width or height?
        if(canvasProps.getWidth() !== widthVal || canvasProps.getHeight() !== heightVal){
            var undo = new CanvasChangeSizeCommand(widthVal, heightVal);
            undo.execute();
            History.addUndo(undo);
        }
        

        //Log.info('Nr of actions in Undo system: ' + History.ACTIONS.length);
        Log.groupEnd();
        //alert(canvasProps);

        draw();
    };

    divButton.appendChild(btnUpdate);

    //fit button
    var btnFit = document.createElement("input");
    btnFit.setAttribute("type", "button");
    btnFit.setAttribute("value", "Fit");

    btnFit.onclick = function(){
        /* Algorithm
         * 1) Find border points of Figure/Container/Connector bounds
         * 2) Get new width and height of canvas from 1)
         * 3) If canvas size changed -> Use CanvasChangeSizeCommand to change canvas size
         */

        var workAreaBounds = STACK.getWorkAreaBounds();
        var newCanvasWidth = workAreaBounds[2] - workAreaBounds[0];
        var newCanvasHeight = workAreaBounds[3] - workAreaBounds[1];

        // Did canvas size changed?
        if (newCanvasWidth !== canvasProps.getWidth() || newCanvasHeight !== canvasProps.getHeight()) {
            var cmdCanvasFit = new CanvasFitCommand(
                newCanvasWidth + DIAGRAMO.CANVAS_FIT_PADDING * 2,
                newCanvasHeight + DIAGRAMO.CANVAS_FIT_PADDING * 2,
                workAreaBounds[0] - DIAGRAMO.CANVAS_FIT_PADDING,  // new (0,0) point goes this X coordinate
                workAreaBounds[1] - DIAGRAMO.CANVAS_FIT_PADDING   // new (0,0) point goes this Y coordinate
            );
            cmdCanvasFit.execute();
            History.addUndo(cmdCanvasFit);
            //  redraw canvas
            draw();
        }
    };

    divButton.appendChild(btnFit);

    div.appendChild(divButton);
}



/** The structure that will declare any visible and changable property of a shape.
 * 
 *  Note:  A {BuilderProperty} DOES NOT STORE THE VALUE OF THE PROPERTY but only
 * describe what properties of a {Style} are exposed and how the {Builder} will
 * create interface (fragments) for user in properties panel. 
 *
 * @constructor
 * @this {Builder}
 * @param {String} name - the name of the property
 * @param {String} property - the property (in dot notation) we are using in the form of 'primitives.0.style.strokeStyle'
 * @param {Object} type - could be either, 'Color', 'Boolean', 'Text' or {Array}
 * In case it's an {Array} it is of type [{Text,Value}] and is used to generate a DD menu
 */
function BuilderProperty(name, property, type){
    this.name = name;
    this.property = property;
    this.type = type;
//    Log.info('BuilderProperty(): ' + 'Propery type: ' + this.type + ' name: ' + this.name + ' property: ' + this.property);
}

/**Color property type*/
BuilderProperty.TYPE_COLOR = 'Color';

/**Text property type*/
BuilderProperty.TYPE_TEXT = 'Text';

/**SingleText property type*/
BuilderProperty.TYPE_SINGLE_TEXT = 'SingleText';

/**Text size property type*/
BuilderProperty.TYPE_TEXT_FONT_SIZE = 'TextFontSize';

/**Font family property type*/
BuilderProperty.TYPE_TEXT_FONT_FAMILY = 'TextFontFamily';

/**Text aligment property type*/
BuilderProperty.TYPE_TEXT_FONT_ALIGNMENT = 'TextFontAlignment';

/**Text underlined property type*/
BuilderProperty.TYPE_TEXT_UNDERLINED = 'TextUnderlined';

/**Boolean property type*/
BuilderProperty.TYPE_BOOLEAN = 'Boolean';

/**Line width property type*/
BuilderProperty.TYPE_LINE_WIDTH = 'LineWidth';

/**Line width property style*/
BuilderProperty.TYPE_LINE_STYLE = 'LineStyle';

/**Image Fill type*/
BuilderProperty.TYPE_IMAGE_FILL = 'ImageFill';

/**File Upload type*/
BuilderProperty.TYPE_IMAGE_UPLOAD = "ImageUpload";

/**Connector's end property type*/
BuilderProperty.TYPE_CONNECTOR_END= 'ConnectorEnd';


/**URL attached to a figure*/
BuilderProperty.TYPE_URL= 'URL';

//wb mod 
BuilderProperty.SW_IP= 'IP';
BuilderProperty.SW_NAME = 'Name';
BuilderProperty.SW_USERNAME = 'UserName';
BuilderProperty.SW_PASSWD = 'Passwd';
BuilderProperty.SW_L2IF = 'L2if';
BuilderProperty.SW_L3IF = 'L3if';
BuilderProperty.SW_STATIC_ROUTE = 'SwStaticRoute';
BuilderProperty.SVR_IP = 'IP';
BuilderProperty.SVR_NAME = 'Name';
BuilderProperty.SVR_USERNAME = 'UserName';
BuilderProperty.SVR_PASSWD = 'Passwd';
BuilderProperty.SVR_IFS = 'Ifs';
BuilderProperty.SVR_STATIC_ROUTE = 'SvrStaticRoute';
//读取交换机信息的属性
BuilderProperty.SW_INFO = 'SwichInfo' 


//BuilderProperty.IMAGE_FILL = [{Text: 'No Scaling', Value: CanvasImage.FIXED_NONE},{Text: 'Fit to Area', Value: CanvasImage.FIXED_BOTH},{Text: 'Fit to Width',Value: CanvasImage.FIXED_WIDTH},{Text: 'Fit to Height',Value: CanvasImage.FIXED_HEIGHT},{Text: ' Auto Fit',Value: CanvasImage.FIXED_AUTO}]

/**Line widths*/
BuilderProperty.LINE_WIDTHS = [
    {Text: '1px', Value: '1'},{Text: '2px',Value: '2'},{Text: '3px',Value: '3'},
    {Text: '4px',Value: '4'},{Text: '5px',Value: '5'},{Text: '6px',Value: '6'},
    {Text: '7px',Value: '7'},{Text: '8px',Value: '8'},{Text: '9px',Value: '9'},
    {Text: '10px',Value: '10'}];


/**Line styles*/
BuilderProperty.LINE_STYLES = [
    {Text: 'Continous', Value: 'continuous'},
    {Text: 'Dotted', Value: 'dotted'},
    {Text: 'Dashed',Value: 'dashed'}
];

/**Font sizes*/
BuilderProperty.FONT_SIZES = [];
for(var i=0; i<73; i++){
  BuilderProperty.FONT_SIZES.push({Text:i+'px', Value:i});
}

/**Connector ends*/
BuilderProperty.CONNECTOR_ENDS = [{Text:'Normal', Value:'Normal'},{Text:'Arrow', Value:'Arrow'},
    {Text:'Empty Triangle', Value:'Empty'},{Text:'Filled Triangle', Value:'Filled'}];

/**Display separator*/
BuilderProperty.SEPARATOR = 'SEPARATOR';

/**Css class for button checking control*/
BuilderProperty.BUTTON_CHECKER_CLASS = 'button-checker';

/**Name of attribute to define is property checked or not*/
BuilderProperty.BUTTON_CHECKED_ATTRIBUTE = 'button-checked';

/**Label for text underlined property*/
BuilderProperty.TEXT_UNDERLINED_LABEL = 'U';

/**wb mod : 给每个属性一个方便理解的名字，用于前端显示*/
BuilderProperty.SW_NAMES = {
    l2ifs : 'L2 Interface',
    port : 'Port',
    vlanId : 'Native Vlan Id',
    vtype : 'Port mode',
    vmembers: 'Vlan members',
    opPort : 'Opposite Port',
    l3ifs : 'L3 Interface',
    ifName : 'Name',
    ip : 'IP',
    mask : 'Net Mask',
    staticRoute : 'Static Route',
    destIp : 'Dest IP',
    nextIp : 'Next Hop',
    swL2 : 'Add L2 Interface',
    swL3 : 'Add L3 Interface',
    swSR : 'Add Static Route Entry',
    svIf: 'Add Interface',
    svSR : 'Add Static Route Entry',
    iface : 'Interface'
}

/**Creates a {BuilderProperty} out of JSON parsed object
 *@param {JSONObject} o - the JSON parsed object
 *@return {BuilderProperty} a newly constructed Point
 *@author Alex Gheorghiu <alex@scriptoid.com>
 **/
BuilderProperty.load = function(o){
    var prop = new BuilderProperty();
    prop.name = o.name;
    prop.property = o.property;
    prop.type = o.type;
    return prop;
}


/**Creates an array of BuilderProperties from an array of {JSONObject}s
 *@param {Array} v - the array of JSONObjects
 *@return an {Array} of {BuilderProperty}-ies
 *@author Alex Gheorghiu <alex@scriptoid.com>
 **/
BuilderProperty.loadArray = function(v){
    var newProps = [];
    for(var i=0; i< v.length; i++){
        newProps.push(BuilderProperty.load(v[i]));
    }
    return newProps;
}

/*wb mod : 创建l2ifs属性输入表单
 * 实际l3表单也使用本方法创建
 * @figureId {number} - 当前图形的编号
 * @property {object} - 当前信息属性的属性名（如'props.l2ifs'）
 * @propObjArr {object} - 设备信息属性列表（如l2ifs、l3ifs）
 * @index {number} - 需要创建的属性在propObjArr中的索引
 */
BuilderProperty.createSwL2ifsDiv = function(figureId, property, propObjArr, index, cssPrefix){
    var lineDiv = document.createElement("div");
    lineDiv.className = cssPrefix + 'line';
    for(var attr in propObjArr[index]){  
        //将属性的key转换为方便阅读的名称
        var name = BuilderProperty.SW_NAMES[attr];
        var value = propObjArr[index][attr];
        //console.log('attr=' + attr + ', name=' + name + ', value=' + value);
        //每个标签（labelDiv）和输入框（inputDiv）组成一个subLiveDiv
        var subLineDiv = document.createElement("div");
        if(attr === 'vmembers' || attr === 'mask') {
            subLineDiv.className = cssPrefix + 'lastLine';
        } else {
            subLineDiv.className = cssPrefix + 'subLine';
        }
        var labelDiv = document.createElement("div");
        labelDiv.className = cssPrefix + 'label';
        labelDiv.textContent = name + ':';
        subLineDiv.appendChild(labelDiv);
        if(attr === 'vtype') {
            var list = [{'text': 'access', 'value': '1'}, {'text': 'trunk', 'value': '2'}];
            var prop = property + '.' + index + '.' + attr;
            subLineDiv.appendChild(BuilderProperty.createSelect(figureId, prop, list, value));
        } else {
            var inputDiv = document.createElement("input");
            inputDiv.type = 'text';
            if(attr === 'vmembers' || attr === 'ip' || attr === 'destIp' ||
               attr === 'nextIp') {
                inputDiv.className = cssPrefix + 'longText';
            } else {
                inputDiv.className = cssPrefix + 'shortText'; 
            }
            inputDiv.value = value;

            inputDiv.onchange = function(figureId, property){
                //console.log('property : ' + property);
                return function(){
                    //console.log(this); //this : inputDiv
                    updateShape(figureId, property, this.value);
                }
            }(figureId, property + '.' + index + '.' + attr);
            inputDiv.onmouseout = inputDiv.onchange;
            inputDiv.onkeyup = inputDiv.onchange;
            subLineDiv.appendChild(inputDiv);
        }
        lineDiv.appendChild(subLineDiv);  
    }
    if(index === '0'){
        return lineDiv;
    }
    var delButton = document.createElement('button');
    delButton.type = 'button';
    delButton.className = 'delButton';
    delButton.textContent = 'del';
    delButton.onclick = function(delObj){
        return function(){
            for(attr in delObj){
                delObj[attr] = 'N/A';
            }
            lineDiv.className = '';
            lineDiv.style.cssText = '';
            lineDiv.innerHTML = '';
            propObjArr.splice(index, 1);
        }
    }(propObjArr[index]);
    lineDiv.appendChild(delButton);
    return lineDiv;
}

BuilderProperty.createSelect = function(figureId, property, options, selected) {
    var select = document.createElement('select');
    select.className = 'devSelect';
    for(i in options) {
        var op = new Option(options[i]['text'], options[i]['value'])
        select.options.add(op);
    }
    if(selected === 1) {
        select.selectedIndex = 1;
    }
    select.onchange = function(figureId, property){
                //console.log('property : ' + property);
                return function(){
                    //console.log(this.selectedIndex); //this : inputDiv
                    updateShape(figureId, property, this.selectedIndex);
                }
            }(figureId, property);
    return select;
}

BuilderProperty.prototype = {
    
    constructor : BuilderProperty,

    toString:function(){
        return 'Propery type: ' + this.type + ' name: ' + this.name + 
               ' property: ' + this.property;
    },

    equals : function(anotherBuilderProperty){
        return this.type == anotherBuilderProperty.type
            && this.name == anotherBuilderProperty.name
            && this.property == anotherBuilderProperty.property;
    },
    
    /**
     *Generates a HTML fragment to allow to edit its property.
     *For example if current property is a color then this method will
     *inject a color picker in the specified DOMObject
     *
     *@param {HTMLElement} DOMObject - the div of the properties panel
     *@param {Number} figureId - the id of the figure we are using
     */
    injectInputArea:function(DOMObject, figureId){
        if(this.name === BuilderProperty.SEPARATOR){
            DOMObject.appendChild(document.createElement("hr"));
            return;
        }
        else if(this.type === BuilderProperty.TYPE_COLOR){
            this.generateColorCode(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.TYPE_TEXT){
            this.generateTextCode(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.TYPE_SINGLE_TEXT){
            this.generateSingleTextCode(DOMObject,figureId);
        }
        else if(this.type === BuilderProperty.TYPE_TEXT_FONT_SIZE){            
            this.generateArrayCode(DOMObject,figureId, BuilderProperty.FONT_SIZES);
//            this.generateFontSizesCode(DOMObject,figureId);
        }
        else if(this.type === BuilderProperty.TYPE_TEXT_FONT_FAMILY){
            this.generateArrayCode(DOMObject,figureId, Text.FONTS);
        }
        else if(this.type === BuilderProperty.TYPE_TEXT_FONT_ALIGNMENT){
            this.generateArrayCode(DOMObject,figureId, Text.ALIGNMENTS);
        }
        else if(this.type === BuilderProperty.TYPE_TEXT_UNDERLINED){
            this.generateButtonCheckerCode(DOMObject,figureId);
        }
        else if(this.type === BuilderProperty.TYPE_CONNECTOR_END){
            this.generateArrayCode(DOMObject,figureId, BuilderProperty.CONNECTOR_ENDS);
        }
        else if(this.type === BuilderProperty.TYPE_LINE_WIDTH){
            this.generateArrayCode(DOMObject,figureId, BuilderProperty.LINE_WIDTHS);
        }
        else if(this.type === BuilderProperty.TYPE_LINE_STYLE){
            this.generateArrayCode(DOMObject,figureId, BuilderProperty.LINE_STYLES);
        }
        else if(this.type === BuilderProperty.TYPE_URL){
            this.generateURLCode(DOMObject, figureId);
        }
        //wb mod
        else if(this.type === BuilderProperty.SW_IP){
            this.generateSingleInput(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.SW_NAME){
            this.generateSingleInput(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.SW_USERNAME){
            this.generateSingleInput(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.SW_PASSWD){
            this.generateSingleInput(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.SW_L2IF){
            this.generateSwL2ifCode(DOMObject, figureId, 'swL2');
        }
        else if(this.type === BuilderProperty.SW_L3IF){
            this.generateSwL2ifCode(DOMObject, figureId, 'swL3');
        }
        else if(this.type === BuilderProperty.SW_STATIC_ROUTE){
            this.generateSwL2ifCode(DOMObject, figureId, 'swSR');
        }
        //读取交换机信息
        else if(this.type === BuilderProperty.SW_INFO){
            this.generateSwInfo(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.SVR_IP){
            this.generateSingleInput(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.SVR_NAME){
            this.generateSingleInput(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.SVR_USERNAME){
            this.generateSingleInput(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.SVR_PASSWD){
            this.generateSingleInput(DOMObject, figureId);
        }
        else if(this.type === BuilderProperty.SVR_IFS){
            this.generateSwL2ifCode(DOMObject, figureId, 'svIf');
        }
        else if(this.type === BuilderProperty.SVR_STATIC_ROUTE){
            this.generateSwL2ifCode(DOMObject, figureId, 'svSR');
        }
    },

    /**
     *Creates a boolean editor; usually a chechbox
     *
     *@param {HTMLElement} DOMObject - the div of the properties panel
     *@param {Number} figureId - the id of the figure we are using
     **/
    generateBooleanCode:function(DOMObject,figureId){
        var d = new Date();
        var uniqueId = d.getTime();
        var value = this.getValue(figureId);
        var div = document.createElement("div");

        var labelDiv = document.createElement("div");
        labelDiv.className = "label";
        labelDiv.textContent = this.name;

        div.appendChild(labelDiv);

        var check = document.createElement("input");
        check.type = "checkbox"
        check.className = "text"; //required for onkeydown
        check.checked = value;
        div.children[0].appendChild(check);
        check.onclick = function(figureId,property){
                            return function(){
                                updateShape(figureId, property, this.checked)
                            }
                        }(figureId, this.property);
                        
        DOMObject.appendChild(div);
    },


    /**Generate the code to edit the text.
     *The text got updated when you leave the input area
     *
     *@param {HTMLElement} DOMObject - the div of the properties panel
     *@param {Number} shapeId - the id of the {Figure} or {Connector} we are using
     **/
    generateTextCode:function(DOMObject, shapeId){
        var uniqueId = new Date().getTime();
        var value = this.getValue(shapeId);

        var div = document.createElement("div");
        div.className = "textLine";

        var labelDiv = document.createElement("div");
        labelDiv.className = "label";
        labelDiv.textContent = this.name;

        div.appendChild(labelDiv);

        var text = document.createElement("textarea");
        text.className = "text"; //required for onkeydown
        text.value = value;
        text.spellcheck = false;
        text.style.width = "100%";
        div.appendChild(document.createElement("br"));
        div.appendChild(text);

        // used to change Text property
        text.onchange = function(shapeId,property){
            return function(){
                // update shape but without adding {Command} to the {History}
                updateShape(shapeId, property, this.value, true);
            };
        }(shapeId, this.property);

        // used to create undo {Command}
        text.onblur = function(shapeId, property, previousValue){
            return function(){
                // create {Command} where previous value is
                // the initialization value of textarea
                updateShape(shapeId, property, this.value, false, previousValue);
            };
        }(shapeId, this.property, text.value);

        text.onmouseout = text.onchange;
        text.onkeyup = text.onchange;
        DOMObject.appendChild(div);
    },


    /**Generate the code to edit the text.
     *The text got updated when you leave the input area
     *
     *@param {HTMLElement} DOMObject - the div of the properties panel
     *@param {Number} figureId - the id of the figure we are using
     **/
    generateSingleTextCode:function(DOMObject,figureId){
        var uniqueId = new Date().getTime();
        var value = this.getValue(figureId);

        var div = document.createElement("div");
        div.className = "line";

        var labelDiv = document.createElement("div");
        labelDiv.className = "label";
        labelDiv.textContent = this.name;

        var icon = new Image();
        icon.className = 'prop-icon';
        icon.src = Builder.IMAGE_TEXT_ICON_PATH;
        labelDiv.appendChild(icon);

        div.appendChild(labelDiv);

        var text = document.createElement("input");
        text.type = "text";
        text.className = "text"; //required for onkeydown
        text.value = value;
        div.appendChild(text);

        text.onchange = function(figureId,property){
            return function(){
                Log.info("Builder.generateSingleTextCode() value: " + this.value);
                updateShape(figureId, property, this.value);
            }
        }(figureId, this.property);


        text.onmouseout = text.onchange;
        text.onkeyup = text.onchange;
        DOMObject.appendChild(div);
    },


    /**Generate the code to edit the URL.
     *The URL got updated when you leave the input area
     *
     *@param {HTMLElement} DOMObject - the div of the properties panel
     *@param {Number} figureId - the id of the figure we are using
     **/
    generateURLCode:function(DOMObject,figureId){
        var uniqueId = new Date().getTime();
        var value = this.getValue(figureId);

        var div = document.createElement("div");
        div.className = "line";

        var labelDiv = document.createElement("div");
        labelDiv.className = "label";
        labelDiv.textContent = this.name;

        var icon = new Image();
        icon.className = 'prop-icon';
        icon.src = Builder.IMAGE_URL_ICON_PATH;
        labelDiv.appendChild(icon);

        div.appendChild(labelDiv);

        var text = document.createElement("input");
        text.type = "text";
        text.className = "text"; //required for onkeydown
        text.value = value;
        div.appendChild(text);

        text.onchange = function(figureId,property){
            return function(){
                Log.info("Builder.generateURLCode() value: " + this.value);
                updateShape(figureId, property, this.value);
            }
        }(figureId, this.property);


        text.onmouseout = text.onchange;
        text.onkeyup = text.onchange;
        DOMObject.appendChild(div);
    },


    /**Used to generate a drop down menu
     *
     *@param {HTMLElement} DOMObject - the div of the properties panel
     *@param {Number} figureId - the id of the figure we are using
     *@param {Array} v - a vector or hashes ex: [{Text:'Normal', Value:'Normal'},{Text:'Arrow', Value:'Arrow'}]
     */
    generateArrayCode:function(DOMObject, figureId, v){
//        Log.info("Font size length: " + v.length);
        var uniqueId = new Date().getTime();
        
        var value = this.getValue(figureId);

        var div = document.createElement('div');
        div.className = 'line';

        var labelDiv = document.createElement('div');
        labelDiv.className = 'label';
        labelDiv.textContent = this.name;

        // get last name of property to define it's icon
        var propNames = this.property.split('.');
        var propLastName = propNames.pop();

        var icon;
        switch (propLastName) {
            case 'lineWidth':
                icon = new Image();
                icon.className = 'prop-icon';
                icon.src = Builder.IMAGE_LINEWIDTH_ICON_PATH;
                labelDiv.appendChild(icon);
                break;
            case 'startStyle':
                icon = new Image();
                icon.className = 'prop-icon';
                icon.src = Builder.IMAGE_STARTSTYLE_ICON_PATH;
                labelDiv.appendChild(icon);
                break;
            case 'endStyle':
                icon = new Image();
                icon.className = 'prop-icon';
                icon.src = Builder.IMAGE_ENDSTYLE_ICON_PATH;
                labelDiv.appendChild(icon);
                break;
            case 'lineStyle':
                icon = new Image();
                icon.className = 'prop-icon';
                icon.src = Builder.IMAGE_LINESTYLE_ICON_PATH;
                labelDiv.appendChild(icon);
                break;                 
        }

        div.appendChild(labelDiv);
        
        var select = document.createElement("select");
        select.style.cssText ="float: right;";
        select.id = this.property; // for DOM manipulation
        div.appendChild(select);
        
        for(var i=0; i< v.length; i++){
            var option = document.createElement("option");
            option.value = v[i].Value;
//            Log.info("\t Text : " + v[i].Text + " Value : " + v[i].Value);
            option.text = v[i].Text; //see: http://www.w3schools.com/jsref/coll_select_options.asp
            select.options.add(option); //push does not exist in the options array
            if(option.value == value){
                option.selected = true;
            }
        }

        var selProperty = this.property; //save it in a separate variable as if refered by (this) it will refert to the 'select' DOM Object
        select.onchange = function(){
            //alert('Font size triggered. Figure id : ' + figureId + ' property: ' + selProperty + ' new value' + this.options[this.selectedIndex].value);
            updateShape(figureId, selProperty, this.options[this.selectedIndex].value);
        };

        DOMObject.appendChild(div);
    },
    

    /**
     *Used to generate a color picker
     *
     *@param{HTMLElement} DOMObject - the div of the properties panel
     *@param{Number} figureId - the id of the figure we are using
     */
    generateColorCode: function(DOMObject, figureId){
        var value = this.getValue(figureId);
       
        var uniqueId = new Date().getTime();
        var div = document.createElement("div");
        div.className = "line";

        var labelDiv = document.createElement("div");
        labelDiv.className = "label";
        labelDiv.textContent = this.name;

        // get last name of property to define it's icon
        var propNames = this.property.split('.');
        var propLastName = propNames.pop();

        var icon;
        switch (propLastName) {
            case "fillStyle":
                icon = new Image();
                icon.className = 'prop-icon';
                icon.src = Builder.IMAGE_FILL_ICON_PATH;
                labelDiv.appendChild(icon);
                break;
            case "strokeStyle":
                icon = new Image();
                icon.className = 'prop-icon';
                icon.src = Builder.IMAGE_STROKE_ICON_PATH;
                labelDiv.appendChild(icon);
                break;
        }

        div.appendChild(labelDiv);

        var colorSelectorDiv = document.createElement("div");
        colorSelectorDiv.id = 'colorSelector' + uniqueId;
        colorSelectorDiv.className = 'color-selector';

        var colorInput = document.createElement("input");
        colorInput.type = "text";
        colorInput.id = 'colorpickerHolder' + uniqueId;
        colorInput.value = value;
        colorSelectorDiv.appendChild(colorInput);

        div.appendChild(colorSelectorDiv);

        DOMObject.appendChild(div);

        var colorPicker = document.getElementById('colorpickerHolder'+uniqueId);

        //let plugin do the job
        $(colorPicker).colorPicker();

        //on change update the figure
        var propExposedToAnonymous = this.property;
        colorPicker.onchange = function() {
            Log.info('generateColorCode(): figureId: ' + figureId + 'type: ' + this.type + ' name: ' + this.name + ' property: ' + this.property);
            updateShape(figureId, propExposedToAnonymous, colorPicker.value);
        };
    },


    /**Generate the code to edit the boolean property with button.
     *Result control has 2 modes: checked/unchecked.
     *The property got updated on click
     *
     *@param {HTMLElement} DOMObject - the div of the properties panel
     *@param {Number} figureId - the id of the figure we are using
     **/
    generateButtonCheckerCode:function(DOMObject,figureId){
        var value = this.getValue(figureId);

        var div = document.createElement("div");
        div.className = "line";

        var buttonChecker = document.createElement("input");
        buttonChecker.type = "button";
        buttonChecker.id = this.property; // for DOM manipulation
        buttonChecker.className = BuilderProperty.BUTTON_CHECKER_CLASS;
        buttonChecker.value = BuilderProperty.TEXT_UNDERLINED_LABEL; // for now we have button checking only for underlined text property
        // property value stores in custom attribute
        buttonChecker.setAttribute(BuilderProperty.BUTTON_CHECKED_ATTRIBUTE, value);
        div.appendChild(buttonChecker);

        buttonChecker.onclick = function(figureId,property){
            return function(){
                // property value stores in custom attribute
                var currentValue = this.getAttribute(BuilderProperty.BUTTON_CHECKED_ATTRIBUTE);
                // new value is inverse of the current one
                var newValue = currentValue == "true" ? false : true;
                // update control first
                this.setAttribute(BuilderProperty.BUTTON_CHECKED_ATTRIBUTE, newValue);
                Log.info("Builder.generateButtonCheckerCode() value: " + newValue);
                updateShape(figureId, property, newValue);
            };
        }(figureId, this.property);

        DOMObject.appendChild(div);
    },

    //wb mod 
    generateSingleInput:function(DOMObject,figureId){
        var uniqueId = new Date().getTime();
        var value = this.getValue(figureId);
        var div = document.createElement("div");
        div.className = "line";

        var labelDiv = document.createElement("div");
        labelDiv.className = "label";
        labelDiv.textContent = this.name;

        div.appendChild(labelDiv);

        var inputDiv = document.createElement("input");
        inputDiv.type = "text";
        inputDiv.className = "inputDiv"; //required for onkeydown
        inputDiv.value = value;
        div.appendChild(inputDiv);

        inputDiv.onchange = function(figureId,property){
            return function(){
                updateShape(figureId, property, this.value);
            }
        }(figureId, this.property);


        inputDiv.onmouseout = inputDiv.onchange;
        inputDiv.onkeyup = inputDiv.onchange;
        DOMObject.appendChild(div);
    },

    //wb mod : switch l2 interfece 属性表单
    generateSwL2ifCode:function(DOMObject, figureId, cssPrefix){
        var uniqueId = new Date().getTime();
        //获取图形对象中的***Props对象中的具体属性，其中l2ifs是一个数组，
        //数组元素为{port:'', vid:'', ...}形式的对象
        var propObjArr = trimArr(this.getValue(figureId));   //确保被设为'N/A'的元素都被删除
        //console.log(propObjArr);
        
        var mainDiv = document.createElement('div');
        mainDiv.className = cssPrefix + 'MainDiv';
        //标题和新增行按钮
        var titleDiv = document.createElement('div');
        titleDiv.className = 'titleDiv';
        var titleLine = document.createElement('div');
        titleLine.className = 'titleLine';
        var titleLabel = document.createElement('div');
        titleLabel.className = 'titleLabel';
        //titleLabel.textContent = BuilderProperty.SW_NAMES[this.property.split('.')[1]];
        var titleButton = document.createElement('button');
        titleButton.type = 'button';
        titleButton.className = 'titleButton';
        titleButton.textContent = BuilderProperty.SW_NAMES[cssPrefix];
        titleButton.onclick = function(figureId, property){
            return function(){
                var lastObj = propObjArr[propObjArr.length - 1];
                var tempObj = {};
                if(propObjArr.length === 1){
                    for(var attr in lastObj){
                        tempObj[attr] = '';
                    }
                    propObjArr.push(tempObj);
                    mainDiv.appendChild(BuilderProperty.createSwL2ifsDiv(figureId, property, 
                                        propObjArr, (propObjArr.length - 1), ''));
                } else {
                    //检查前一项内容是否完成输入，只需要始终检查数组最后一个元素
                    for(var attr in lastObj){
                        if (typeof PropsHandler[attr] === 'function' && 
                            !PropsHandler[attr](lastObj[attr])){
                            return;        
                        }
                        tempObj[attr] = '';
                    }
                    propObjArr.push(tempObj);
                    mainDiv.appendChild(BuilderProperty.createSwL2ifsDiv(figureId, property, 
                                        propObjArr, (propObjArr.length - 1), ''));
                }   
            }
        }(figureId, this.property);

        titleLine.appendChild(titleLabel);
        titleLine.appendChild(titleButton);
        titleDiv.appendChild(titleLine);
        mainDiv.appendChild(titleDiv);
        //查询按钮
        var titleButton = document.createElement('button');
        titleButton.type = 'button';
        titleButton.className = 'titleButton';
        titleButton.textContent = 'Get Info...';
        titleButton.onclick = function(figureId, property){
            return function(){
                var prop = STACK.figureGetById(figureId).props;
                var ip = prop.ip;
                var uname = prop.userName;
                var passwd = prop.passwd;
                if(!PropsHandler['iup'](ip, uname, passwd)){
                    return;
                }
                var devType = cssPrefix.slice(0,2)
                var queryType = cssPrefix.slice(2)
                getDevInfo(ip, uname, passwd, devType, queryType, figureId);
            }
        }(figureId, this.property);

        titleLine.appendChild(titleLabel);
        titleLine.appendChild(titleButton);
        titleDiv.appendChild(titleLine);
        mainDiv.appendChild(titleDiv);
        if(propObjArr.length > 1){
            for(var i in propObjArr) {
                //var lineDiv = document.createElement("div");
                //lineDiv.className = "swLine";
                var flag = 0;
                for(var attr in propObjArr[i]){
                    if(propObjArr[i][attr] === 'N/A'){
                        flag = 1;
                        break;
                    }
                }
                if(i !== '0' && flag === 0){
                    mainDiv.appendChild(BuilderProperty.createSwL2ifsDiv(figureId, this.property, 
                                                                         propObjArr, i, ''));
                }
            }
        }
        DOMObject.appendChild(mainDiv);
    },

    /**We use this to return a value of the property for a figure,
     *Similar to Javas Class.forname...sort of anyway
     *We need this because passing direct references to simple data types (including strings) 
     *only passes the value, not a reference to that value (call by value not by reference)
     *
     *@param{Number} figureId - the id of the shape {Figure} or {Connector} we are using, could also be the canvas (figureId = 'a')
     */
    getValue:function(figureId){
        //Is it a Figure? 
        var obj = STACK.figureGetById(figureId);
        
        //Is it a Connector ?
        if(obj == null){ //ok so it's not a Figure...so it should be a Connector
            obj = CONNECTOR_MANAGER.connectorGetById(figureId);
        }                
        
        //Is it the Canvas?
        if(obj == null){
            if(figureId == "canvas"){
                obj = canvas;
            }
        }
        
        //Is it a Container?
        if(obj == null){
            obj = STACK.containerGetById(figureId);
        }
        //Log.debug("Unsplit property: " + this.property);
        
        var propertyAccessors = this.property.split(".");
        //console.log(propertyAccessors);
        for(var i = 0; i<propertyAccessors.length-1; i++){
//            Log.info("\tBuilderProperty::getValue() : i = " + i  + ' name= ' + propertyAccessors[i]);
            obj = obj[propertyAccessors[i]];
        }
        
        //Log.info("Object type: " + obj.oType);
        
        var propName = propertyAccessors[propertyAccessors.length -1];
        //Log.info("Property name: " + propName);
        
        var propGet = "get" + Util.capitaliseFirstLetter(propName);
        
        //null is allowed, undefined is not
        if(propGet in obj){ //@see https://developer.mozilla.org/en/JavaScript/Reference/Operators/Special_Operators/in_Operator
            return obj[propGet]();
        }
        else{
            //Access the object property's
            return obj[propertyAccessors[propertyAccessors.length -1]];
        }
    },
};



/**
 * This instance is responsible for creating and updating Text Editor Popup.
 * Text Editor Popup is made out of:
 *  - editor - a <div> (inside #container <div>) that contains the text and reflects the 
 *  - tools - a <div> (inside #container <div>) that will contain all the buttons and options to format text
 *  
 * @constructor
 * @this {TextEditorPopup}
 * @param {HTMLElement} editor - the DOM object (a <div> inside editor page) to create Text Editor Popup
 * @param {HTMLElement} tools - the DOM object (a <div> inside editor page) to create Text Editor Tools 
 * @param  shape - the {Figure} or {Connector} - parent of Text primitive
 * @param {Number} textPrimitiveId - the id value of Text primitive child of shape for which the properties will be displayed
 * @author Artyom Pokatilov <artyom.pokatilov@gmail.com>
 */
function TextEditorPopup(editor, tools, shape, textPrimitiveId){
    this.editor = editor;
    this.tools = tools;
    this.shape = shape;
    this.textPrimitiveId = textPrimitiveId;

    /*We need to construct the full path to the properties of Text*/
    // beginning of property string of BuilderProperty for primitive
    var propertyPrefix;

    if (this.shapeIsAConnector()) {
        // in case of connector with primitive = middleText
        propertyPrefix = "middleText.";
    } else {
        // in case of figure with primitive.id = textPrimitiveId
        propertyPrefix = "primitives." + this.textPrimitiveId + ".";
    }

    // value of BuiderProperty::property
    this.stringPropertyName = propertyPrefix + TextEditorPopup.STRING_PROPERTY_ENDING;
    this.sizePropertyName = propertyPrefix + TextEditorPopup.SIZE_PROPERTY_ENDING;
    this.fontPropertyName = propertyPrefix + TextEditorPopup.FONT_PROPERTY_ENDING;
    this.alignPropertyName = propertyPrefix + TextEditorPopup.ALIGN_PROPERTY_ENDING;
    this.colorPropertyName = propertyPrefix + TextEditorPopup.COLOR_PROPERTY_ENDING;
    this.underlinedPropertyName = propertyPrefix + TextEditorPopup.UNDERLINED_PROPERTY_ENDING;
}

/**A set of predefined properties fragments*/
TextEditorPopup.STRING_PROPERTY_ENDING = 'str';
TextEditorPopup.SIZE_PROPERTY_ENDING = 'size';
TextEditorPopup.FONT_PROPERTY_ENDING = 'font';
TextEditorPopup.ALIGN_PROPERTY_ENDING = 'align';
TextEditorPopup.COLOR_PROPERTY_ENDING = 'style.fillStyle';
TextEditorPopup.UNDERLINED_PROPERTY_ENDING = 'underlined';


TextEditorPopup.prototype = {
    
    constructor : TextEditorPopup,
    
    /**
     *Returns true if target shape of TextEditorPopup is a Connector
     *@return {Boolean} - true shape property is a connector
     *@author Artyom Pokatilov <artyom.pokatilov@gmail.com>
     **/
    shapeIsAConnector : function (){
        return this.shape.oType === "Connector";
    },
            
      

    /**
    *Creates DOM structure and bind events
    *@author Artyom Pokatilov <artyom.pokatilov@gmail.com>
    **/
    init : function (){
       var textarea;

       // <div> for text tools contains font size, font family, alignment and color
       for(var i = 0; i < this.shape.properties.length; i++){
           var curProperty = this.shape.properties[i].property; //get property in long format ex: primitives.1.style.fillStyle
           if (curProperty != null) {
               var curValue = this.shape.properties[i].getValue(this.shape.id);
               switch (curProperty){
                   case this.stringPropertyName:
                       this.shape.properties[i].injectInputArea(this.editor, this.shape.id);
                       textarea = this.editor.getElementsByTagName('textarea')[0];

                       // remove all <br> tags from text-editor as they were added by injectInputArea method 
                       removeNodeList(this.editor.getElementsByTagName('br')); //defined in util.js

                       // set Text editor properties on initialization
                       this.setProperty(curProperty, curValue);

                       break;

                   case this.sizePropertyName:
                   case this.fontPropertyName:
                   case this.alignPropertyName:
                   case this.colorPropertyName:
                   case this.underlinedPropertyName:
                       this.shape.properties[i].injectInputArea(this.tools, this.shape.id);

                       // set Text editor properties on initialization
                       this.setProperty(curProperty, curValue);

                       break;
               }
           }
       }

       this.editor.className = 'active';
       this.tools.className = 'active';
       //this.placeAndAutoSize();

       // select all text inside textarea (like in Visio)
       setSelectionRange(textarea, 0, textarea.value.length);
   },
           
           
    /**
     * Changing property inside Text Editor
     * provides WYSIWYG functionality
     * @param {String} property - property name that is being edited (in dotted notation)
     * @param {Object} value - the value to set the property to
     * @author Artyom Pokatilov <artyom.pokatilov@gmail.com>
     **/
    setProperty : function (property, value) {
        var textarea = this.editor.getElementsByTagName('textarea')[0];
        switch(property) {

            case this.sizePropertyName:
                // set new property value to editor's textarea
                textarea.style.fontSize = value + 'px';

                // set new property value to editor's tool
                document.getElementById(property).value = value;
                break;

            case this.fontPropertyName:
                // set new property value to editor's textarea
                textarea.style.fontFamily = value;

                // set new property value to editor's tool
                document.getElementById(property).value = value.toLowerCase();
                break;

            case this.alignPropertyName:
                // set new property value to editor's textarea
                textarea.style.textAlign = value;

                // IE doesn't apply text-align property correctly to all lines of the textarea on a fly
                // that is why we just copy it's text and paste it back to refresh text rendering
                if (Browser.msie) {
                    textarea.value = textarea.value;
                }

                // set new property value to editor's tool
                document.getElementById(property).value = value;
                break;

            case this.underlinedPropertyName:
                // set new property value to editor's textarea
                textarea.style.textDecoration = value == true ? 'underline' : '';

                // set new property value to editor's tool
                document.getElementById(property).setAttribute(BuilderProperty.BUTTON_CHECKED_ATTRIBUTE, value);
                break;

            case this.colorPropertyName:
                // set new property value to editor's textarea
                textarea.style['color'] = value;

                // set new property value to editor's tool (colorPicker)
                var colorPicker = this.tools.getElementsByClassName('color_picker')[0];
                colorPicker.style['background-color'] = value; //change the color to the proper one
                colorPicker.previousSibling.value = value; //set the value to the "hidden" text field
                break;
        }

        this.placeAndAutoSize();
    },
            

    /**
     *Places and sets size to the property panel
     *@author Artyom Pokatilov <artyom.pokatilov@gmail.com>
     **/
    placeAndAutoSize : function () {
        var textarea = this.editor.getElementsByTagName('textarea')[0];

        // set edit dialog position to top left (first) bound point of Text primitive
        var textBounds;

        if (this.shapeIsAConnector()) {
            // in case of connector primitive is a middleText property
            textBounds = this.shape.middleText.getBounds();
        } else {
            // in case of connector primitive is a primitives[this.textPrimitiveId] property
            textBounds = this.shape.primitives[this.textPrimitiveId].getBounds();
        }

        // change coordinates of editing Text primitive to include padding and border of Text Editor
        var leftCoord = textBounds[0] - defaultEditorBorderWidth - defaultEditorPadding;
        var topCoord = textBounds[1] - defaultEditorBorderWidth - defaultEditorPadding;
        
        var textareaWidth = textBounds[2] - textBounds[0];
        var textareaHeight = textBounds[3] - textBounds[1];

        // Firefox includes border & padding as part of width and height,
        // so width and height should additionally include border and padding twice
        // (similar to "feather" option in Fireworks)
        if (Browser.mozilla) {
            textareaHeight += (defaultEditorPadding) * 2;
            topCoord -= (defaultEditorPadding);
            textareaWidth += (defaultEditorPadding) * 2;
            leftCoord -= (defaultEditorPadding);
        }

        // some of IE magic:
        // enough to add half of font-size to textarea's width to prevent auto-breaking to next line
        // which is wrong in our case
        // (similar to "feather" option in Fireworks)
        if (Browser.msie) {
            var fontSize = parseInt(textarea.style['font-size'], 10);
            textareaWidth += fontSize / 2;
            leftCoord -= fontSize / 4;
        }

        this.editor.style.left = leftCoord + "px";
        this.editor.style.top = topCoord + "px";


        // visibility: 'hidden' allows us to get proper size but 
        // without getting strange visual artefacts (tiggered by settings positions & other)
        this.tools.style.visibility = 'hidden';
        
        // We set it to the left upper corner to get it's objective size
        this.tools.style.left = '0px';
        this.tools.style.top = '0px';

        // Get toolbox height and width. Notice that clientHeight differs from offsetHeight.
        //@see https://developer.mozilla.org/en/docs/DOM/element.offsetHeight
        //@see http://stackoverflow.com/questions/4106538/difference-between-offsetheight-and-clientheight
        var toolboxHeight = this.tools.offsetHeight;
        var toolboxWidth = this.tools.offsetWidth;

        // define toolbox left position
        var toolboxLeft = leftCoord;
        
        // get width of work area (#container <div> from editor)
        var workAreaWidth = getWorkAreaContainer().offsetWidth;

        // If it's not enough place for toolbox at the page right side
        if (toolboxLeft + toolboxWidth >= workAreaWidth - scrollBarWidth) {
            // then shift toolbox to left before it can be placed
            toolboxLeft = workAreaWidth - toolboxWidth - scrollBarWidth;
        }

        // define toolbox top position
        var toolboxTop = topCoord - toolboxHeight;
        // If it's not enough place for toolbox at the page top
        if (toolboxTop <= 0) {
            // then place toolbox below textarea
            toolboxTop = topCoord + toolboxHeight + defaultEditorBorderWidth + defaultEditorPadding;
        }

        this.tools.style.left = toolboxLeft + "px";
        this.tools.style.top = toolboxTop + "px";
        
        // return normal visibility to toolbox
        this.tools.style.visibility = 'visible';

        textarea.style.width = textareaWidth + "px";
        textarea.style.height = textareaHeight + "px";
    },
     
    /**
    *Removes DOM structure of editor and it's tools
    *@author Artyom Pokatilov <artyom.pokatilov@gmail.com>
    **/        
    destroy : function (){
        this.editor.className = '';
        this.editor.style.cssText = '';
        this.editor.innerHTML = '';

        this.tools.className = '';
        this.tools.style.cssText = '';
        this.tools.innerHTML = '';
    },
    
    
    /**
    *Returns true if mouse clicked inside TextEditorPopup
    *@param {Event} e - mouseDown event object
    *@return {boolean} - true if clicked inside
    *@author Artyom Pokatilov <artyom.pokatilov@gmail.com>
    **/
   mouseClickedInside : function (e) {
       var target = e.target;

       // check if user fired mouse down on the part of editor, it's tools or active color picker
       // actually active color picker in that moment can be only for Text edit
       var inside = target.id === this.editor.id
           || target.parentNode.id === this.editor.id
           || target.parentNode.parentNode.id === this.editor.id

           || target.id === this.tools.id
           || target.parentNode.id === this.tools.id
           || target.parentNode.parentNode.id === this.tools.id

           || target.className === 'color_picker'

           || target.id === 'color_selector'
           || target.parentNode.id === 'color_selector'
           || target.parentNode.parentNode.id === 'color_selector';
   
       return inside;
   },

    /**
     * Checks if TextEditorPopup refers to target shape and id of Text primitive
     * @param  shape - target figure or connector to check
     * @param {Number} textPrimitiveId - the id value of a target Text primitive
     *
     *@return {Boolean} - true if refers to target objects
     *@author Artyom Pokatilov <artyom.pokatilov@gmail.com>
     **/
    refersTo : function (shape, textPrimitiveId) {
        var result = this.shape.equals(shape);

        // in case of connector textPrimitiveId will be underfined
        if (textPrimitiveId != null) {
            result &= this.textPrimitiveId === textPrimitiveId;
        }
        return result;
    },

    /**
     * Manually triggers onblur event of textarea inside TextEditor.
     * @author Artyom Pokatilov <artyom.pokatilov@gmail.com>
     **/
    blurTextArea : function () {
        var textarea = this.editor.getElementsByTagName('textarea')[0];
        textarea.onblur();
    }
   
};

/**wb mod 生成属性定义面板
 * @param {HTMLElement} configDiv - 包含属性定义面板的div元素
 * @param {Figure} or {Connector} - 属性定义面板所属的figure或connector对象
 * @param {x, y} - 点击鼠标的位置，应以确定属性定义面板的位置
 */
function ConfigPopup(configDiv, shape, coords){
    this.configDiv = configDiv;
    this.shape = shape;
    this.coords = coords;

    /*We need to construct the full path to the properties of Text*/
    // beginning of property string of BuilderProperty for primitive
    var propertyPrefix = "props.";


    // value of BuiderProperty::property
    this.namePropertyName = propertyPrefix + 'name';
    this.usrPropertyName = propertyPrefix + 'userName';
    this.passwdPropertyName = propertyPrefix + 'passwd';
    this.ipPropertyName = propertyPrefix + 'ip';
    this.l2ifPropertyName = propertyPrefix + 'l2if';
    this.l3ifPropertyName = propertyPrefix + 'l3if';
    this.staticRouteName = propertyPrefix + 'staticRoute';
}
ConfigPopup.prototype = {
    
    constructor : ConfigPopup,
    /**
    *Creates DOM structure and bind events
    *
    **/
    init : function (){
        //console.log(this.shape.properties);
        for(var i = 0; i < this.shape.properties.length; i++){
            //if(this.shape.properties[i].name === BuilderProperty.SEPARATOR)
                //continue;
            var curProperty = this.shape.properties[i].property; //get property in long format ex: props.name
            var curValue = this.shape.properties[i].getValue(this.shape.id);
            if (curProperty != null && /(props\.)\.*/g.test(curProperty) === true) {
                //console.log(this.shape.properties[i]);
                this.shape.properties[i].injectInputArea(this.configDiv, this.shape.id); 
            }
        }

        this.configDiv.className = 'active';
        //console.log(this.coords);
        this.configDiv.style.left = this.coords[0] + 'px';
        this.configDiv.style.top = this.coords[1] + 'px';
        //this.placeAndAutoSize();
    },

    mouseClickedInside : function (e) {
       var target = e.target;

       // check if user fired mouse down on the part of editor, it's tools or active color picker
       // actually active color picker in that moment can be only for Text edit
       var inside = target.id === this.configDiv.id
           || target.parentNode.id === this.configDiv.id
           || target.parentNode.parentNode.id === this.configDiv.id
   
       return inside;
   },

    destroy : function (){
        this.configDiv.className = '';
        this.configDiv.style.cssText = '';
        this.configDiv.innerHTML = '';
    }
};

/**wb mod 生成设备信息面板
 * @param {HTMLElement} configDiv - 包含面板的div元素
 * @param {figureId}  - 面板所属的figureid
 * @param {x, y} - 点击鼠标的位置，应以确定属性定义面板的位置
 */
function devInfoPopup(configDiv, figureId, devType, queryType){
    this.configDiv = configDiv;
    this.figureId = figureId;
    this.devType = devType;
    this.queryType = queryType;

}

devInfoPopup.prototype = {
    
    constructor : devInfoPopup,
    /**
    * init 
    **/
    init : function (){
        var divClass = this.devType + this.queryType + 'Info';
        if(this.devType === 'sw'){
            if(this.queryType === 'L2'){
                //this.swL2Info();
                var titles = ['Vlan ID', 'Access', 'Trunk'];
                var tdList = [{'key':'id', 'limit': null}, {'key':'access', 'limit': 4}, 
                              {'key':'trunk', 'limit': 4},];
                this.buildPanel(titles, tdList, divClass);
            } else if (this.queryType === 'L3'){
                //this.swL3Info();
                var titles = ['Name', 'Vlan', 'State', 'Address'];
                var tdList = [{'key':'vifId', 'limit': null}, {'key':'vid', 'limit': null}, 
                              {'key':'state', 'limit': null}, {'key':'addrs', 'limit': 2}];
                this.buildPanel(titles, tdList, divClass);
            } else {        //queryType === 'SR'
                //this.swSRInfo();
                var titles = ['Destination', 'Net mask', 'Next hop'];
                var tdList = [{'key':'dest', 'limit': null}, {'key':'mask', 'limit': null}, 
                              {'key':'next', 'limit': null}];
                this.buildPanel(titles, tdList, divClass);
            } 
        } else {
            if(this.queryType === 'If'){
                //this.svIfInfo();
                var titles = ['Dev', 'State', 'Mac address' ,'IP address'];
                var tdList = [{'key':'dev', 'limit': null}, {'key':'state', 'limit': null}, 
                              {'key':'mac', 'limit': null}, {'key':'addrs', 'limit': 2}];
                this.buildPanel(titles, tdList, divClass);
            }  else {        //queryType === 'SR'
                //this.svSRInfo();
                var titles = ['Destination', 'Gateway', 'Net mask', 'Metric', 'Interface'];
                var tdList = [{'key':'dest', 'limit': null}, {'key':'gw', 'limit': null}, 
                              {'key':'mask', 'limit': null}, {'key':'metric', 'limit': null},
                              {'key':'iface', 'limit': null}];
                this.buildPanel(titles, tdList, divClass);
            } 
        }  
        this.configDiv.className = 'info';
        //console.log(this.coords);
        var pos = $("#a").offset();
        var posParent = $("#a").parent().offset();
        this.configDiv.style.left = posParent.left - pos.left + 30 + 'px';
        this.configDiv.style.top = posParent.top - pos.top + 20 + 'px';
        //this.placeAndAutoSize();
    },

    /* 构建设备属性展示面板
     * @param {list} titles - 标题列表，列表中每一个元素代表信息面板table中的一个th
     * @param {list} tdList - 用于td中展示属性的列表，形式为{['key': '0', 'limit': 0], ……}
     *  其中key表示从服务器端取回的j包含设备属性的json对象中的key值，
     *  limit表示在td中一行显示的属性个数
     * @param {string} divClass - 面板div的class属性名 
     */
    buildPanel : function(titles, tdList, divClass){
        //console.log(CURRENT_DATA);
        var dragDiv = document.createElement('div');
        dragDiv.className = 'tLabel';
        //dragDiv.textContent = 'Test'
        //this.movable(dragDiv, this.configDiv, $('#a')); 
        divMovable(dragDiv, this.configDiv, $('#a'));     
        this.configDiv.appendChild(dragDiv);
        var closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'closeButton';
        closeButton.textContent = 'close';
        closeButton.onclick = function (div){
            return function(){
                div.className = '';
                div.style.cssText = '';
                div.innerHTML = '';
            }
        }(this.configDiv);
        this.configDiv.appendChild(closeButton);
        var nbrsButton = document.createElement('button');  //扫描直连设备
        nbrsButton.type = 'button';
        nbrsButton.className = 'closeButton';
        nbrsButton.textContent = 'scan nbrs';
        nbrsButton.onclick = function (div, figureId){
            return function(event){
                //console.log(event.clientX);
                var f = STACK.figureGetById(figureId);
                var data = {
                    'ip': f.props.ip, 
                    'username': f.props.userName, 
                    'password': f.props.passwd, 
                    'devType': f.devType === 'Switch' ? 'sw' : 'sv'
                }
                getNbrs(data, f.id);
            }
        }(this.configDiv, this.figureId);
        this.configDiv.appendChild(nbrsButton);
        var table = this.buildTable(titles);
        table.className = 'infotab';
        for(var index in CURRENT_DATA){
            var trDict = CURRENT_DATA[index];
            var tr = document.createElement("tr");
            for(var index in tdList){
                this.buildTd(tr, trDict, tdList[index]['key'], tdList[index]['limit']);
            }
            table.appendChild(tr);
        }
        this.configDiv.appendChild(table);
    },

    /*
    * @param {div} tr - table row的div对象
    * @param {Object} dict - 存储要展现数据的字典对象
    * @param {string || Array} key - td对象所展示的内容在dict中的key值，同时用于div的class
    * 若dict[key]是Array，则将其每一个元素放入td中
    * @param {number} limit - td中每一行的元素个数上限（即输出多少个元素时换行），可选参数
    */
    buildTd : function (tr, dict, key, limit) {
        limit = limit || 1000;
        var td = document.createElement("td");
        td.className = key;
        var content = '';
        var value = dict[key]
        if(typeof(value) !== 'object' || value.length === 1){
            content = value
        } else {    //dict[key]是Array时
            for(var i in value){  //这里i是string类型，用于计算时要转型
                content = content + value[i] + ' , ';
                if((parseInt(i) + 1) % limit === 0){
                    content += '<br />';
                }
            }
        }
        td.innerHTML = content;
        tr.appendChild(td);      
    },

    /*根据传入的列表创建table title，返回table的div对象
    * @param {list} titles - title列表
    */
    buildTable : function (titles) {
        var table = document.createElement("table");
        table.className = 'infotab';
        var title = document.createElement("tr");
        for(var i in titles){
            var td = document.createElement("td");
            td.innerHTML = titles[i];
            title.appendChild(td);
        }
        table.appendChild(title);
        return table;
    },

    /*
     * 销毁属性面板
     */
    destroy : function (){
        this.configDiv.className = '';
        this.configDiv.style.cssText = '';
        this.configDiv.innerHTML = '';
    }
};

/**wb mod 生成联通性信息面板
 * @param {HTMLElement} configDiv - 包含面板的div元素
 * @param {figureId}  - 面板所属的figureid
 * @param {x, y} - 点击鼠标的位置，应以确定属性定义面板的位置
 */
function connInfoPopup(conConnDiv, conId, coords){
    this.conConnDiv = conConnDiv;
    this.coords = coords;
    this.srcDev = CONNECTOR_MANAGER.connectorGetById(conId).srcDev;
    this.dstDev = CONNECTOR_MANAGER.connectorGetById(conId).dstDev;
}

connInfoPopup.prototype = {
    
    constructor : connInfoPopup,
    /**
    * init 
    **/
    init : function (){
        var divClass = 'connInfo';
        var titles = ["Iface(src)", "Iface(dst)", "type", "direction", "extra"];
        var tdList = [{'key':'srcInterface', 'limit': null}, 
                      {'key':'dstInterface', 'limit': null}, 
                      {'key':'cFlag', 'limit': null}, 
                      {'key':'cType', 'limit': null},
                      {'key':'extra', 'limit': null}];
        this.buildPanel(titles, tdList, divClass)
        this.conConnDiv.className = 'conn';
        this.conConnDiv.style.left = this.coords[0] + 'px';
        this.conConnDiv.style.top = this.coords[1] + 'px';
    },

    /* 构建属性展示面板
     * @param {list} titles - 标题列表，列表中每一个元素代表信息面板table中的一个th
     * @param {list} tdList - 用于td中展示属性的列表，形式为{['key': '0', 'limit': 0], ……}
     *  其中key表示从服务器端取回的包含设备属性的json对象中的key值，
     *  limit表示在td中一行显示的属性个数
     * @param {string} divClass - 面板div的class属性名 
     */
    buildPanel : function(titles, tdList, divClass) {
        //console.log(CURRENT_DATA);
        var dragDiv = document.createElement('div');
        dragDiv.className = 'tLabel';
        dragDiv.textContent = 'Connectivity: ' + this.srcDev.props.name + "(src) -> " 
                              + this.dstDev.props.name + "(dst)";
        divMovable(dragDiv, this.conConnDiv, $('#a'));     
        this.conConnDiv.appendChild(dragDiv);
        var closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'closeButton';
        closeButton.textContent = 'close';
        closeButton.onclick = function (div){
            return function(){
                div.className = '';
                div.style.cssText = '';
                div.innerHTML = '';
            }
        }(this.conConnDiv);
        this.conConnDiv.appendChild(closeButton);
        if (CURRENT_DATA['isConnect'] === 0) {
            var unconnDiv = document.createElement('div');
            unconnDiv.className = 'unConnected';
            unconnDiv.innerHTML = this.srcDev.props.name + " and " 
                                  + this.dstDev.props.name + " is unconnected!";
            this.conConnDiv.appendChild(unconnDiv);
            return 0;
        }
        var table = this.buildTable(titles);
        table.className = 'infotab';
        for(var index in CURRENT_DATA['connInfo']){
            var trDict = CURRENT_DATA['connInfo'][index];
            var tr = document.createElement("tr");
            for(var index in tdList){
                this.buildTd(tr, trDict, tdList[index]['key'], tdList[index]['limit']);
            }
            table.appendChild(tr);
        }
        this.conConnDiv.appendChild(table);
    },

    /* 创建table中的td元素，td的内容为dict[key]
    * @param {tr} - table row的div对象
    * @param {dict} - 存储要展现数据的字典对象
    * @param {key} - td对象所展示的内容在dict中的key值，同时用于div的class
    * 若dict[key]是Array，则将其每一个元素放入td中
    * @param {limit} - td中每一行的元素个数上限（即输出多少个元素时换行），可选参数
    */
    buildTd : function (tr, dict, key, limit) {
        limit = limit || 1000;
        var td = document.createElement("td");
        td.className = key;
        if(dict[key] && key === 'extra') {
            var extraButton = document.createElement('button');
            extraButton.type = 'button';
            extraButton.className = 'extraButton';
            extraButton.textContent = 'extra';
            extraButton.onclick = function (div, info){
                return function(){
                    return 0;
                }
            }(this.conConnDiv, dict[key]);
            this.conConnDiv.appendChild(extraButton);
        }
        var content = '';
        var value = dict[key]
        if(typeof(value) !== 'object' || value.length === 1){
            content = value
        } else {    //dict[key]是Array时
            for(var i in value){  //这里i是string类型，用于计算时要转型
                content = content + value[i] + ' , ';
                if((parseInt(i) + 1) % limit === 0){
                    content += '<br />';
                }
            }
        }
        td.innerHTML = content;
        tr.appendChild(td);      
    },

    /*根据传入的列表创建table title，返回table的div对象
    * @param {list} titles - title列表
    */
    buildTable : function (titles) {
        var table = document.createElement("table");
        table.className = 'infotab';
        var title = document.createElement("tr");
        for(var i in titles){
            var td = document.createElement("td");
            td.innerHTML = titles[i];
            title.appendChild(td);
        }
        table.appendChild(title);
        return table;
    },

    /*
     * 销毁属性面板
     */
    destroy : function (){
        this.conConnDiv.className = '';
        this.conConnDiv.style.cssText = '';
        this.conConnDiv.innerHTML = '';
    }
};

/**wb mod 生成设备邻居信息面板
 * @param {HTMLElement} nbrsDiv - 包含面板的div元素
 * @param {figureId}  - 面板所属的figureid
 * @param {x, y} - 点击鼠标的位置，应以确定属性定义面板的位置
 */
function nbrsInfoPopup(nbrsDiv, figureId, coords){
    this.mainDiv = nbrsDiv;
    this.figureId = figureId;
}

nbrsInfoPopup.prototype = {
    
    constructor : nbrsInfoPopup,
    /**
    * init 
    **/
    init : function (){
        var divClass ='nbrsInfo';
        var titles = ['Dev', 'Neighbors'];
        var tdList = [{'key':'dev', 'limit': null}, {'key':'nbrs', 'limit': 2}];
        this.mainDiv.className = 'info';
        this.buildPanel(titles, tdList, divClass);
        //console.log(this.coords);
        var pos = $("#a").offset();
        var posParent = $("#a").parent().offset();
        this.mainDiv.style.left = posParent.left - pos.left + 30 + 'px';
        this.mainDiv.style.top = posParent.top - pos.top + 20 + 'px';
        //this.placeAndAutoSize();
    },

    /* 构建设备属性展示面板
     * @param {list} titles - 标题列表，列表中每一个元素代表信息面板table中的一个th
     * @param {list} tdList - 用于td中展示属性的列表，形式为{['key': '0', 'limit': 0], ……}
     *  其中key表示从服务器端取回的j包含设备属性的json对象中的key值，
     *  limit表示在td中一行显示的属性个数
     * @param {string} divClass - 面板div的class属性名 
     */
    buildPanel : function(titles, tdList, divClass){
        //console.log(CURRENT_DATA);
        var dragDiv = document.createElement('div');
        dragDiv.className = 'tLabel';
        //dragDiv.textContent = 'Test'
        divMovable(dragDiv, this.mainDiv, $('#a'));     
        this.mainDiv.appendChild(dragDiv);
        var closeButton = document.createElement('button');
        closeButton.type = 'button';
        closeButton.className = 'closeButton';
        closeButton.textContent = 'close';
        closeButton.onclick = function (div){
            return function(){
                div.className = '';
                div.style.cssText = '';
                div.innerHTML = '';
            }
        }(this.mainDiv);
        this.mainDiv.appendChild(closeButton);
        var table = this.buildTable(titles);
        table.className = 'infotab';
        for(var index in CURRENT_DATA){
            var trDict = CURRENT_DATA[index];
            var tr = document.createElement("tr");
            for(var index in tdList){
                this.buildTd(tr, trDict, tdList[index]['key'], tdList[index]['limit']);
            }
            table.appendChild(tr);
        }
        this.mainDiv.appendChild(table);
    },

    /*
    * @param {div} tr - table row的div对象
    * @param {Object} dict - 存储要展现数据的字典对象
    * @param {string || Array} key - td对象所展示的内容在dict中的key值，同时用于div的class
    * 若dict[key]是Array，则将其每一个元素放入td中
    * @param {number} limit - td中每一行的元素个数上限（即输出多少个元素时换行），可选参数
    */
    buildTd : function (tr, dict, key, limit) {  //邻居属性需要特殊处理
        limit = limit || 1000;
        var td = document.createElement("td");
        td.className = key;
        var content = '';
        var value = dict[key]
        if(typeof(value) !== 'object'){
            content = value
        } else {    //dict[key]是Array时
            for(var i in value){  //这里i是string类型，用于计算时要转型
                content += '[ '
                for(var j in value[i]) {
                    content += j + ':' + value[i][j] + ' '
                }
                content += '] '
                if((parseInt(i) + 1) % limit === 0){
                    content += '<br />';
                }
            }
        }
        td.innerHTML = content;
        tr.appendChild(td);      
    },

    /*根据传入的列表创建table title，返回table的div对象
    * @param {list} titles - title列表
    */
    buildTable : function (titles) {
        var table = document.createElement("table");
        table.className = 'infotab';
        var title = document.createElement("tr");
        for(var i in titles){
            var td = document.createElement("td");
            td.innerHTML = titles[i];
            title.appendChild(td);
        }
        table.appendChild(title);
        return table;
    },

    /*
     * 销毁属性面板
     */
    destroy : function (){
        this.mainDiv.className = '';
        this.mainDiv.style.cssText = '';
        this.mainDiv.innerHTML = '';
    }
};