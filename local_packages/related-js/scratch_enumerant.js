

function Case(options) {
	//options = _(options).defaults({name:undefined,values:undefined,returns:undefined});
	var name = options.name;
	var values = options.values;
	var returns = options.returns;
	
	//Validate
	if(type.undef(values)) throw "Missing input 'values'.";
	if(type.undef(returns)) throw "Missing input 'returns'.";
	values = type.arr.to(values);	//ensure values are an array
	if(type.undef(options.name)) {	//If 'name' missing ==> infer from .implicit functions
		name = Case.find_implicit(values);
	}
	if (!type.str(name))	throw "Case name must be a string";

	//Build Case instance
	if(Case[name]) {
		return Case[name](values,returns);
	} else {
		throw "Unrecognized Case type name '{0}'.".format(name);
	}
}
Case._names = [];
Case._implicits = [];



//=====================   Core Functions
Case.extend = function(template) {
	//template = {name:,build:,implicit:,}
	Case[template.name] = template.build;
	_.extend(Case[template.name],template);
	
	if(_(template).has('implicit')) {
		Case._implicits.push(template.name);
	}
	Case._names.push(template.name);
}
Case.find_implicit = function(values) {
	//Implicitly determine the Case of an array of values
	var name = _(Case._implicits).chain()
		.filter(function(case_name){	//name of Cases with an implicit function
			return Case[case_name].implicit(values);
		}).first()	//Take the first case whose .implicit matches all input values.
		.value();
	if(type.undef(name)) { name = 'basic';}

	console.log("Implicitly concluded that '{0}' is type name '{1}'".format(values,name));
	return name
}
Case.parse = function() {
	/** Each input argument should define one case, and should be one of:
	 * 	(1) A Case object
	 *  (2) An array:
	 *  (2.1) Of length 1 --> defaults case
	 *  (2.2) Of length 2 --> implicitly determined case type
	 *  (2.3) Of length 3 --> explicitly defined case type
	 */
	var caseArray = Array.prototype.slice.call(arguments);

	return _(caseArray).map(Case.parseCase);
}
Case.parseCase = function parseCase(caseArgs) {
	//caseArgs should be one of:
	//(1): A Case Object
	var case_attributes = ['name','values','returns','is'];//attributes used for duck-typing Case objects
	if (type.obj(caseArgs)) {
		var isCase = _(case_attributes).all(function(attr){
			return _(caseArgs).has(attr);
		});
		if (isCase) {
			return caseArgs;
		}
	}
	//(2): An array of case data
	if (type.arr(caseArgs)){
		switch(caseArgs.length) {
		case 1:	//(2.1) Array length 1 --> defaults case (returns)
			return Case({name:'default',values:null,returns:caseArgs[0]});
		case 2: //(2.2) Array length 2 --> implicitly determined Case name (values,returns)
			return Case({values:caseArgs[0],returns:caseArgs[1]});	//name will be implicitly determined by Case() function
		case 3: //(2.3) Array length 3 --> explicitly defined Case name (name,values,returns)
			return Case({name:caseArgs[0],values:caseArgs[1],returns:caseArgs[2]});
		default: 
			throw "Invalid length for case array ('{0}') - should be 0,1, or 2.".format(caseArgs.length);
		}
	}
	var msg = "Input case must be either a Case() object (having fields: {0}), or an array specifying Case data. Instead received: {1}".format(case_attributes,caseArgs); 
	throw msg;
}

//=====================  Case Varieties
Case.extend({
	name:'basic',
	build: function(values,returns) {
		return {
			name: 'basic',
			values:values,
			returns:returns,
			is: function(obj) {
				return _(this.values).contains(obj);
			}
		};
	}
});
Case.extend({
	name: 'default',
	build: function(values,returns) {
		return {
			name: 'default',
			values: null,
			returns: returns,
			is: function(obj) {
				return true;
			}
		};
	}
})
Case.extend({
	name:'types',
	build: function(values,returns) {
		return {
			name: 'types',
			values: values,
			returns: returns,
			is: function(obj) {
				return _(this.values).chain()
					.map(function(type_func){	//If any of the input type functions are true for the input obj 
						try {
							return type_func(obj); 
						} catch(err) {
							return false;
						}
					}).any()
					.value();
			}
		};
	},
	implicit: function(instanceVals) {
		
		instanceVals = type.arr.to(instanceVals);
		return _(instanceVals).all(function(val){	//If all instanceVals are subtypes of 'type'
			return _.contains(_.values(type),val);
		});
	}
});





function example_cases_1() {
	window.enumerant = {};
	//var caseArray = [[0,70],[1,50],[2,30],[[3,4],25],[[type.int],1000],[20]];
	var caseArray = [[0,70],Case({name:'basic',values:1,returns:50}),[2,30],[[3,4],25],[[type.int],1000],[20]];
	var inputArray = [0,1,2,3,4,5,6,7,6,5,4,3,'a'];
	window.enumerant['caseArray'] = caseArray;
	window.enumerant['inputArray'] = inputArray;
	
	var caseObjs = Case.parse.apply(null,caseArray);
	window.enumerant['caseObjs'] = caseObjs;
	
	var resultsCases = _(inputArray).map(function(inElm){
		for (var i=0; i<caseObjs.length;i++) {
			if (caseObjs[i].is(inElm)) {
				return caseObjs[i];
			}
		}
	});
	window.enumerant['resultsCases'] = resultsCases;
	window.enumerant['resultsArray'] = _(resultsCases).pluck('returns');
	
	var displayOutput = _(inputArray).map(function(inputElm,i){
		var outline = ['#'+String(i),inputArray[i],resultsCases[i].name,resultsCases[i].returns];
		console.log(outline);
		return outline;
	});
	window.enumerant['displayOutput']=displayOutput;
}
example_cases_1()
//$.getScript('/python/local_packages/in_development/scratch_enumerant.js')
//Case({values:window.enumerant.caseArray[0][0],returns:window.enumerant.caseArray[0][1]})
//Case({name:'default',values:null,returns:window.enumerant.caseArray[0]})
var mycase = Case({values:window.enumerant.caseArray[0][0],returns:window.enumerant.caseArray[0][1]});




//=======================================================
//    ENUMERANT
//=======================================================

//Enumerant(caseArray).switch(inputArray)
//_(inputArray).Enumerate(caseArray)
//_.Enumerate(inputArray,caseArray)
function Enumerant() {
	var caseArray = Array.prototype.slice.call(arguments);	
	var cases = Case.parse.apply(null,caseArray);
	
	this.defaultCase = _(cases).chain()	//Find defaultCases
		.filter(function(caseObj){
			return caseObj.name == 'default';
		}).last()
		.value();
	this.cases = _(cases).filter(function(caseObj){
		return caseObj.name != 'default';
	});
}
Enumerant.prototype.results = function() {
	return _(this.resultsCases).pluck('returns');
}
Enumerant.prototype.switch = function() {
	//Evaluate this.cases for each elm in this.inputArray
	var self = this;	//self: this Enumerant()
	self.inputArray = Array.prototype.slice.call(arguments);
	
	
	self.resultsCases = _(self.inputArray).map(function(inElm){
		//Check non-default cases
		for (var i=0; i<self.cases.length;i++) {
			if (self.cases[i].is(inElm)) {
				return self.cases[i];
			}
		}
		//Check default Case - if one present
		if (type.def(self.defaultCase)) {
			if (self.defaultCase.is(inElm)) {
				return self.defaultCase;
			}
		} else {
			//Use 'built-in' default case -- throw exception
			var all_values = _(self.cases).pluck('values');
			var msg = "Invalid input to Enumerant.switch(): '{0}'. Instead should be one of:\n{1}".format(inElm,all_values)
			throw msg
		}
	});
	return self.results();
}
Enumerant.prototype.Case = function() {
	//Accepts a single Case
	var self = this;
	var caseArgs = Array.prototype.slice.call(arguments);
	var newCase = Case.parseCase.apply(null,caseArgs);
	window.newCase = newCase;
	self.cases.push(newCase);

	return this;
}


/*
var myenum = new Enumerant([0,70],Case({name:'basic',values:1,returns:50}),[2,30],[[3,4],25],[[type.int],1000],[20])
myenum.switch(1,2,3,4)
myenum.Case({values:window.enumerant.caseArray[0][0],returns:window.enumerant.caseArray[0][1]})
*/
var myenum = new Enumerant([0,70],Case({name:'basic',values:1,returns:50}),[2,30],[[3,4],25],[[type.int],1000],[20])
myenum.switch(1,2,3,4)
//myenum.Case([[type.str],"Its a string"])





function Enumerate(inputArray,caseArray) {
	var caseArray = Array.prototype.slice.call(arguments);	
	var cases = Case.parse.apply(null,caseArray);
	
	this.defaultCase = _(cases).chain()	//Find defaultCases
		.filter(function(caseObj){
			return caseObj.name == 'default';
		}).last()
		.value();
	this.cases = _(cases).filter(function(caseObj){
		return caseObj.name != 'default';
	});
}

//_(inputArray).Enumerate(caseArray)
//_.Enumerate(inputArray,caseArray)
//---- Harder/Challenging
//_(inputArray).Enumerate(caseArray).Case(...).Case(...).value()
_.mixin({
	enumerate: function() {
		var args = Array.prototype.slice.call(arguments);
		var inputArray = args[0];		//First element
		var caseArray = args.slice(1);	//Everything else
				
		var enumer = new Enumerant(caseArray);
		return self
	}
});