/*
 * @author Oakland J. Peters
 * @institution Laboratory of Dr. Dakshanamurthy, Lombardi Cancer Center, Georgetown Medical Center
 * @date started: ~06/27/2013
 * @requires jQuery.js v1.10
 * 
 * Pre-alpha notes on a Collections() class, which will act as an array-like iterator
 * for a collection of objects with the same prototype/attribute-structure.
 */

//Useful to include object_watch.js -- which is a polyfill, enabling object watch/unwatch in all browsers



/*
 * Update this with:
 * 
 * [] Method application support. For basic (no arguments) functions.
 *    so that myCol.myFunc()  becomes reasonable.
 *    () Thought process: functions should be associated with the Collections object, and not with the component objects.
 *    		So that statements like myCol['func']('a') may possible be reasonable.
 *    () If that property is a function for the first entry of .contents - assume it is for all
 *    () --> establish a WRAPPER, around all functions
 *    () This will require changing:
 *      [] SETTER : it needs to set this.functions[attr] = newval
 *      				this[attr] = function() { //wrapper function
 *      					nargs = [this,arguments]	//this phrasing is wrong
 *      					this.functions[attr](this
 *      				};
 *      	[] WRAPPER : fairly complicated. For now - have it assume that any arguments in are static.
 *				For now it should call this.functions[
 *		[] UPDATE : probably have to do something with it as well.      		
 *      arguments[0] : reference to this/self
 *      		
 * [] Expanded setter, allowing me to assign an array to an array
 *    so that things like myCol['name'] = ['1','2'] become sensible. (aka it will check for the type of the RHS, and deconstruct it for assignments).
 */ 

var notation;
/*
 * ---------- IMPORTANT
 * 		Try branch/version which uses underscore.js functionality, which simplifies/replicates a lot of what I want here.
 * 
 * 
 */


function Collection() {
	var args = Array.prototype.slice.call(arguments);		//Converts 'arguments' to a proper array
	this.contents = args;
	this.functions = {};
	this.wrappers = {};
	this.update();
}

Collection.prototype.get = function(attr) {	
	//For functions, call that function's wrapper (established by Collections.set()
	if (attr in this.functions){	//If attr is in the list of functions
		return this.wrappers[attr];		
		
	//For properties, iterate across all this.contents, and get property for each.
	} else {
		return $.map(this.contents,function(obj){
			if (attr in obj) {
				//if(typeof attr == "function") {
				//	console.log("I am a function.")
				//} else 
				return obj[attr];
			} else {
				return [];
			}
		});
	}
}

Collection.prototype.set = function(attr,newval) {
	if (typeof newval == "function"){
		this.functions[attr] = newval;
		var root = this;		//A reference to the Collections object.
		this.wrappers[attr] = function(){
			//EVENTUALLY, will need to implement the 'deferred attribute' vs static objects distinction here.
			//my preference: DefArg(arg) class --> _$(arg) 		VS		arg		(static)
			if (arguments.length == 0) {
				$.map(root.contents,function(obj){
					return root.functions[attr]();
				});
			} else {
				//Build set of arguments
				var args = Array.prototype.slice.call(arguments);		//Turn arguments into an actual array.
				
				//Call main loop once per content object
				$.map(root.contents,function(obj){
					//Build arguments from current content object
					var argset = [];
					$.each(args,function(ind,arg){
						//Extract .contents object's property for this argument
						console.log("typeName == "+typeName(arg));
						if(typeName(arg) == "DefArg"){	//'DefArg' is used as a flag for inputs to be drawn from .contents
							arg = arg.value;
							argset.push( obj[arg] );
						
						//Treat as a literal input 
						} else {
							argset.push( arg );
						}
						
					});
					//Now call the function with accumulated argset, and return result
					return root.functions[attr](argset);
				});
				
				
			}
		}
	} else {
	
		$.map(this.contents,function(obj){
			obj[attr] = newval;
		});
	}
	this.update(attr);
}



Collection.prototype.create = function(attr) {
	$.map(this.contents,function(obj){
		obj[attr] = []
	});
	this.update(attr);
	return this;
}

Collection.prototype.update = function() {
	var traits = {};
	//Set traits/properties to be updated.
	if (arguments.length == 0) {		//If no argument provided - look for all properties from all objects in .contents
		$.each(this.contents,function(ind,val){
			for (trait in val) {
				traits[trait] = null;
			}
		});
	} else {		//
		traits[arguments[0]] = null;
	}

	for (obj in this.contents) {
		for (attr in traits) {
			this.__defineGetter__(attr,function(){ return this.get(attr); });
			this.__defineSetter__(attr,function(newval){ this.set(attr,newval); });
		}
	}
}

function DefArg(arg) {
	//Deferred argument class. Used to denote properties of Collections.contents, in function calls.
	this.value = arg;
}
_$ = function(arg){
	var stuff = new DefArg(arg);		//pseudonym for DefArg.
	return stuff;
}

function typeName(obj) {
	var funcNameRegex = /function (.{1,})\(/;
	var results = (funcNameRegex).exec(obj.constructor.toString());
	return (results && results.length > 1) ? results[1] : "";
} 

var sayhi = function(x) {console.log('hi '+x);}
delete myCol;
var myCol = new Collection({'name':'john','job':'programmer'},{'name':'peters','hobby':'climbing'});
myCol.set('func',sayhi);
myCol.func(_$('name'));	//Treats 'name' at a property
myCol.func();
myCol.func('name');


myCol.get('name')
myCol.name		//or myCol['name']
myCol.set('func',sayhi)		//or myCol.create('func'); myCol['func'] = sayhi;
myCol.sayhi('in argument')