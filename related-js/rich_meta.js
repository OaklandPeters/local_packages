/*	=================================================================
 * 			Meta - general utility functions
 *  =================================================================
 */
(function(Meta,undefined){
	/***
	 * Sugar; for confirming libraries loaded, and object inspection.
	 * Redundant with most standard libraries (underscore.js), but importantly 
	 * 	does not require them to be loaded.
	 */

	
	//==============================
	//		Core
	//==============================
	
	Meta.required = function(obj,properties,options){
		//
		//Sugar; dual-use.
		//(1) confirm library loaded, by inspecting window object.
		// 		Meta.required(window,'jQuery')
		//(2) validate required object-attributes of function arguments.
		//		Meta.required(arg_no_1,['user','url','settings'])
		//
		options = options || {};
		properties = Meta.ensureArray(properties);
		var blocking = options['blocking']!==false ? true:false;
		
		if (!Meta.has(obj,properties)){
			var message = "Object must have all properties: "+properties.join(', ');
			if ('message' in options) { message+= options['message'];}
			
			if (blocking){
				throw message;
			} else {
				console.error(message+" Attempting to proceeed...");
			}
		}
	}
	Meta.any = function(arr) {
		return arr.reduce(function(A,B){ return A | B; }) == true;
	}
	Meta.all = function(arr) {
		return arr.reduce(function(A,B){ return A & B; }) == true;
	}
	Meta.contains = function(arr,obj){
		var _is = function(elm){ return elm === obj };
		return Meta.any(arr.map(_is));
	}
	Meta.has = function(obj,properties){
		//
		//Sugar. Predicate confirming that obj has all properties.
		//
		var _has = function(prop){ return prop in obj };
		window.debug.properties = properties;
		properties = (typeof properties == 'string') ? Meta.ensureArray(properties) : properties;
		return Meta.all(properties.map(_has));
	}
	
	//==============================
	//		Needed for Core
	//==============================
	Meta.isArray = function(obj){
		return Object.prototype.toString.call(obj) === '[object Array]';
	}
	Meta.ensureArray = function(obj){
		if(Meta.isArray(obj))	{	return obj; }
		return [obj];
	}

	//============================================================
	//		Less Important - Type Checks and Assertions
	//============================================================
	Meta.assert = function(assertion,message){
		message = message || "Assertion error.";
		if (!assertion){
			throw message;
		}
	}
	Meta.Assertion = function(assertion,message,formatobj){
		message   = message   || "Assertion error.";
		formatobj = formatobj || {};
		if (!assertion){
			throw Meta.error(message,formatobj)
		}
	}
	Meta.assertKlass = function(obj,klasses,message){
		klasses = Meta.ensureArray(klasses);
		message = message || "Invalid object. Should be one of: '"+String(klasses)+"'";
		Meta.assert(Meta.isKlass(obj,klasses),message);
	}
	
	Meta.isKlass = function(obj,klasses){
		klasses = Meta.ensureArray(klasses);
		return Meta.contains(klasses,typeof obj);
	}
	Meta.assertEnum = function(obj,arr,message){
		message = message || "Invalid object. Must be one of: '"+String(arr)+"'";
		Meta.assert(Meta.contains(arr,obj),message);
	}
	Meta.isInstance = function(obj,func){
		return obj instanceof func;
	}
	Meta.isJQuery = function(obj){
		Meta.required(window,'jQuery');
		return obj instanceof jQuery;
	}
	Meta.ensureJQuery = function(obj){
		if (Meta.isJQuery(obj)){ return obj}
		else if (Meta.isKlass(obj,'string')) {
			return jQuery(obj)
		} else {
			throw "Cannot convert object of type '"+typeof obj+"' to jQuery."
		}
	}
	
	//============================================================
	//		Probably excessive
	//============================================================
//	Meta.isUndefined = function(obj){
//		//Comparitor for 'obj==undefined'. Corrects Javascript problems,
//		//by ensuring that undefined actually means undefined in this context
//		// (because of the way undefined is passed into Meta).
//		return obj === undefined;
//	}
	Meta.defaults = function defaults(subject,defaults) {
		if (subject===undefined){	return defaults	}
		else if (typeof subject == "object") {
			for (var prop in defaults) {
				if (subject[prop] === undefined){
					subject[prop] = defaults[prop];
				}
			}
			return subject
		} else {
			return subject
		}
	}
	Meta.__typesmsg = function(word,arr){
		return "{0} property. Should be one of type(s): {1}."
			.replace('{0}',word)
			.replace('{1}',String(arr));
	}
	Meta.validateKlass = function validateKlass(subject,types,message){
		//
		//	Sugar for validating types of fields of an object.
		//	types - object, whose property names are checked in 'subject'
		//		and whose values are inputs to assertKlass
		//
		Meta.assertKlass(subject,'object');
		Meta.assertKlass(types,'object');
		for (var prop in types) {
			Meta.assert(prop in subject,
				message || Meta.__typesmsg('Missing',types[prop])
			);
			Meta.assertKlass(subject[prop],types[prop],
				message || Meta.__typesmsg("Invalid",types[prop])
			);
		}
	}
	Meta.parameters = function parameters(url){
		//
		//	Make URL parameters object from url string.
		//	If no url provided - gets current url.
		//
		if (url == undefined){
			url = window.location.href;
		}
		var urlParams;
		
	    var match,
	        pl     = /\+/g,  // Regex for replacing addition symbol with a space
	        search = /([^&=]+)=?([^&]*)/g,
	        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
	        query  = window.location.search.substring(1);

	    urlParams = {};
	    while (match = search.exec(query))
	       urlParams[decode(match[1])] = decode(match[2]);
	    return urlParams;
	}
	Meta.format = function format(fstring,simpleobj){
		//
		//Correct:
		//    Meta.format("{0} and {1} or {2}",{0:'a',1:'b',2:'c'})
		//--> "a and b or c"
		//Incorrect:
		//    Meta.format("{0} and {1} or {2}",'a','b','c')
		//--> "a and {1} or {2}"
		if (typeof simpleobj != 'object'){
			simpleobj = {0: simpleobj};
		}
		for (key in simpleobj){
			fstring = fstring.replace('{'+key+'}',String(simpleobj[key]))
		}
		return fstring;
	}
	Meta.error = function error(fstring,simpleobj){
		msg = Meta.format(fstring,simpleobj);
		try {
			console.error(msg);
		} catch (err) {
		}
		return new Error(msg);
	}
}(window.Meta=window.Meta || {}));



//		Format, using Underscore:
//			... does not support integer indexing
/*
//	Change template notation, to look like Handlebars ({})
_.templateSettings = {
	interpolate: /\{\{(.+?)\}\}/g
};
_.template("{{name}} said hi",{name:'greg'})
//
*/
