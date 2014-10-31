window.debug.erroring = false;


//TODO create LogicalABC with the classmethods
//	And make LogicalExpression inherit from it

function LogicalExpression(func, a, b) {
	var root = this;
	this.name = func.name;
	this.func = func;
	this.A = a;
	this.B = b;

	
	

	//===============================================
	//	Type detection
	//===============================================
	this._isLogical = function _isLogical(X){
		if (typeof X === 'object'){
			if (X instanceof LogicalExpression){
				return true;
			}
		}
		return false;
	}
	this._arity = function _arity(){
		//receives arguments of indefinite length
		var arity = 0;
		for (var i = 0; i<arguments.length; i++){
			if (typeof arguments[i] !== 'undefined'){
				arity++;
			}
		}
		return arity;
	};
	this.arity = function arity(){
		return root._arity(root.A,root.B);
	}
	//=================================================================
	//	Map predicate function onto each atom, recursive
	//=================================================================
	//classmethod
	this._mapLogical = function _mapLogical(X, predicate){
		Meta.assertKlass(predicate,'function');
		if (root._isLogical(X)){
			return X.map(predicate);
		} else {
			return predicate(X);
		}
	};
	this.map = function map(predicate){
		Meta.assertKlass(predicate,'function');
		return new LogicalExpression(
			root.func,
			root._mapLogical(root.A,predicate),
			root._mapLogical(root.B,predicate)
		);
//		root.A = root._mapLogical(root.A,predicate);
//		root.B = root._mapLogical(root.B,predicate);
	};
	
	//=================================================================
	//	Process function on A & B, recursive
	//=================================================================
	//classmethod
	this._callLogical = function(X){
		if (root._isLogical(X)){
			return X.call(X);
		} else {
			return X;
		}
	};
	this.call = function(){
		//Execute root.func(A,B)
		//But first, recurse into A & B if necessary
		return root.func(root._callLogical(root.A),root._callLogical(root.B));
	}
	
	//=================================================================
	//	Apply predicate, and process expression
	//=================================================================
	this.collapse = function collapse(predicate){
		//predicate = predicate || Boolean;
		//var mapped = root.map(predicate);
		//return root.func(this.A,this.B);
		return root.map(predicate).call()
	};
	
	
	//=================================================================
	this._printLogical = function _printLogical(X){
		if (root._isLogical(X)){
			return X.string();
		} else {
			return String(X);
		}
	};
	this.string = function string(){
		var arg;
		var arity = root._arity(root.A,root.B);
		if (arity === 2){
			return "(" + [
	  			root._printLogical(root.A),root.name,root._printLogical(root.B)
	  		].join(" ") + ")";
		} else if (arity === 1){
			if (typeof root.A !== undefined){
				arg = root.A;
			} else {
				arg = root.B;
			}
			return root.name + " " + root._printLogical(arg);
		} else if (arity === 0) {
			return root.name;
		}
	};
	
	this._repr = function _repr(X){
		if (root._isLogical(X)) {
			return X.repr()
		} else {
			return X;
		}
	}
	this.repr = function repr(){
		return {
			name:		root.name,
			func:		root.func,
			A:			root._repr(root.A),
			B:			root._repr(root.B)
		};
	}
}
// -- end LogicalExpression 

function OR(A,B){
	return new LogicalExpression(
		function or(A,B){return (A || B); },
		A,
		B
	);
}
function AND(A,B){
	return new LogicalExpression(
		function and(A,B){return (A && B); },
		A,
		B
	);
}
function NOT(A){
	return new LogicalExpression(
		function not(A){ return (!A); },
		A
	);
}

//console.log(OR(AND(true,NOT(true)),AND(true)).collapse(Boolean));
var expr = OR(AND(true,NOT(true)),NOT(false));
console.log(expr.string());
console.log(expr.collapse(Boolean));


var logi = AND(true,NOT(false));

var mapString = function mapString(obj){
	if (typeof obj === 'string'){
		return 'instanceof('+obj+')';
	} else {
		return obj;
	}
}