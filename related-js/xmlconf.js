/*
 * Read an XML file as a simple JS object.
 * Example use:
 * var config = new Configuration({path: "config.xml"});
 */


/***
 *	This file is loaded AFTER <body>, hence should contain code for interactivity
 *  and user-interaction.
 *	
 *  Code essential for buiding the <body> and the page frame (navbar or <footer>)
 *  should go inside frame.js.
 *  
 *  @requires:	preload.js - Meta,
 *  @requires:  postload.js - CookiesInterace() 
 *  @requires:  underscores.js - _,
 *  @requires:  typecast.js - type()
 *  	
 */

function XMLConfiguration(settings){
	/***
	 * Create object holdings name-->value pairs drawn from 
	 * an XML configuration file.
	 * 
	 * Example:
	 * var config = new Configuration({path: "config.xml"});
	 */

	//Private property
	var root = this;
	Meta.required(settings,['path']);
	_(settings).defaults({
	})
	

	//---------------------------------
	//		Private Methods
	//---------------------------------
	function setattr(value,name){
		root[name] = value;
	}
	var response = $.ajax({
		type:"GET",
		url:settings.path,
		dataType:"xml"
	});	
	
	//---------------------------------
	//		Create Public Properties
	//---------------------------------
	response.done(function(xml){
		var xml_obj = XML.toObj(xml);
		//Apply attributes from the xml object to 'this'
		_(xml_obj).each(function(value,name){
			root[name] = value;
		})
	});
}


/*	XML adapted from xml2json() by Stefan Goessner:
This work is licensed under Creative Commons GNU LGPL License.

License: http://creativecommons.org/licenses/LGPL/2.1/
Version: 0.9
Author:  Stefan Goessner/2006
Web:     http://goessner.net/ 
*/
var XML = {
	toObj: function(xml) {
	  var o = {};
      if (xml.nodeType==1) {   // element node ..
         if (xml.attributes.length)   // element with attributes  ..
            for (var i=0; i<xml.attributes.length; i++)
               o["@"+xml.attributes[i].nodeName] = (xml.attributes[i].nodeValue||"").toString();
         if (xml.firstChild) { // element has child nodes ..
            var textChild=0, cdataChild=0, hasElementChild=false;
            for (var n=xml.firstChild; n; n=n.nextSibling) {
               if (n.nodeType==1) hasElementChild = true;
               else if (n.nodeType==3 && n.nodeValue.match(/[^ \f\n\r\t\v]/)) textChild++; // non-whitespace text
               else if (n.nodeType==4) cdataChild++; // cdata section node
            }
            if (hasElementChild) {
               if (textChild < 2 && cdataChild < 2) { // structured element with evtl. a single text or/and cdata node ..
                  XML.removeWhite(xml);
                  for (var n=xml.firstChild; n; n=n.nextSibling) {
                     if (n.nodeType == 3)  // text node
                        o["#text"] = XML.escape(n.nodeValue);
                     else if (n.nodeType == 4)  // cdata node
                        o["#cdata"] = XML.escape(n.nodeValue);
                     else if (o[n.nodeName]) {  // multiple occurence of element ..
                        if (o[n.nodeName] instanceof Array)
                           o[n.nodeName][o[n.nodeName].length] = XML.toObj(n);
                        else
                           o[n.nodeName] = [o[n.nodeName], XML.toObj(n)];
                     }
                     else  // first occurence of element..
                        o[n.nodeName] = XML.toObj(n);
                  }
               }
               else { // mixed content
                  if (!xml.attributes.length)
                     o = XML.escape(XML.innerXml(xml));
                  else
                     o["#text"] = XML.escape(XML.innerXml(xml));
               }
            }
            else if (textChild) { // pure text
               if (!xml.attributes.length)
                  o = XML.escape(XML.innerXml(xml));
               else
                  o["#text"] = XML.escape(XML.innerXml(xml));
            }
            else if (cdataChild) { // cdata
               if (cdataChild > 1)
                  o = XML.escape(XML.innerXml(xml));
               else
                  for (var n=xml.firstChild; n; n=n.nextSibling)
                     o["#cdata"] = XML.escape(n.nodeValue);
            }
         }
         if (!xml.attributes.length && !xml.firstChild) o = null;
      }
      else if (xml.nodeType==9) { // document.node
         o = XML.toObj(xml.documentElement);
      }
      else
         alert("unhandled node type: " + xml.nodeType);
      return o;
   },
   toJson: function(o, name, ind) {
      var json = name ? ("\""+name+"\"") : "";
      if (o instanceof Array) {
         for (var i=0,n=o.length; i<n; i++)
            o[i] = XML.toJson(o[i], "", ind+"\t");
         json += (name?":[":"[") + (o.length > 1 ? ("\n"+ind+"\t"+o.join(",\n"+ind+"\t")+"\n"+ind) : o.join("")) + "]";
      }
      else if (o == null)
         json += (name&&":") + "null";
      else if (typeof(o) == "object") {
         var arr = [];
         for (var m in o)
            arr[arr.length] = XML.toJson(o[m], m, ind+"\t");
         json += (name?":{":"{") + (arr.length > 1 ? ("\n"+ind+"\t"+arr.join(",\n"+ind+"\t")+"\n"+ind) : arr.join("")) + "}";
      }
      else if (typeof(o) == "string")
         json += (name&&":") + "\"" + o.toString() + "\"";
      else
         json += (name&&":") + o.toString();
      return json;
   },
   innerXml: function(node) {
      var s = ""
      if ("innerHTML" in node)
         s = node.innerHTML;
      else {
         var asXml = function(n) {
            var s = "";
            if (n.nodeType == 1) {
               s += "<" + n.nodeName;
               for (var i=0; i<n.attributes.length;i++)
                  s += " " + n.attributes[i].nodeName + "=\"" + (n.attributes[i].nodeValue||"").toString() + "\"";
               if (n.firstChild) {
                  s += ">";
                  for (var c=n.firstChild; c; c=c.nextSibling)
                     s += asXml(c);
                  s += "</"+n.nodeName+">";
               }
               else
                  s += "/>";
            }
            else if (n.nodeType == 3)
               s += n.nodeValue;
            else if (n.nodeType == 4)
               s += "<![CDATA[" + n.nodeValue + "]]>";
            return s;
         };
         for (var c=node.firstChild; c; c=c.nextSibling)
            s += asXml(c);
      }
      return s;
   },
   escape: function(txt) {
      return txt.replace(/[\\]/g, "\\\\")
                .replace(/[\"]/g, '\\"')
                .replace(/[\n]/g, '\\n')
                .replace(/[\r]/g, '\\r');
   },
   removeWhite: function(e) {
      e.normalize();
      for (var n = e.firstChild; n; ) {
         if (n.nodeType == 3) {  // text node
            if (!n.nodeValue.match(/[^ \f\n\r\t\v]/)) { // pure whitespace text node
               var nxt = n.nextSibling;
               e.removeChild(n);
               n = nxt;
            }
            else
               n = n.nextSibling;
         }
         else if (n.nodeType == 1) {  // element node
            XML.removeWhite(n);
            n = n.nextSibling;
         }
         else                      // any other node
            n = n.nextSibling;
      }
      return e;
   }
};






