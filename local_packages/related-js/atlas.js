
/*
Now, if we wanted to, instead, define getters and setters within the context
of our object prototype (and where having “private” data is less of a 
concern) we can then use an alternative object syntax for that.
*/
function Field(val){
    this.value = val;
}
 
Field.prototype = {
    get value(){
        return this._value;
    },
    set value(val){
        this._value = val;
    }
};
/*
The syntax for getters and setters is typically what scare people the most 
about the feature. But after a little bit of use, it’s easy to get over.

Here’s another example, allowing a user to access an array of usernames 
(but denying them access to the original, underlying user objects.
*/
function Site(users){
    this.__defineGetter__("users", function(){
        // JS 1.6 Array map()
        return users.map(function(user){
            return user.name;
        });
    });
}
/*
As a bonus, here’s a method that I’ve written that can help you to extend 
one object with another (a common JavaScript operation) while still taking 
into account getters and setters:
*/
// Helper method for extending one object with another
function extend(a,b) {
    for ( var i in b ) {
        var g = b.__lookupGetter__(i), s = b.__lookupSetter__(i);
       
        if ( g || s ) {
            if ( g )
                a.__defineGetter__(i, g);
            if ( s )
                a.__defineSetter__(i, s);
         } else
             a[i] = b[i];
    }
    return a;
}
/*
Additionally, in my custom extend() method you’ll notice two new methods: 
__lookupGetter__ and __lookupSetter__. 
(Return the function bound as a getter/setter to the specified property.)
These are immensely useful, once you start dealing with getters and setters.

For example, when I did my first pass at writing an extend() method, I started 
getting all sorts of errors – I was thoroughly confused. That’s when I 
realized that two things were happening with the simple statement: a[i] = b[i];

If a setter existed in object a, named i, and a getter existed in object b, 
named i, a[i]‘s value was being set not to the other setter function, but to 
the computed value from b’s getter function. The two __lookup*__ methods allow 
you to access the original functions used for the methods (thus allowing you 
to write an effective extend method, for example).

A couple things to remember:

[] You can only have one getter or setter per name, on an object. (So you can 
have both one value getter and one value setter, but not two ‘value’ getters.)
[] The only way to delete a getter or setter is to do: ‘delete object[name];’ Be 
aware, that this command is capable of deleting normal properties, getters 
and setters. (So if all you want to do is remove a setter you need to backup 
the getter and restore it afterwards.)
[] If you use __defineGetter__ or __defineSetter__ it will silently 
overwrite any previous named getter or setter – or even property – of the 
same name.
*/

/* ------ Notes: ------------
Starting in JavaScript 1.8.1, setters are no longer called when setting properties in object and array initializers.
var o = {
	a: 7, 
	get b() {return this.a + 1;}, 
	set c(x) {this.a = x / 2}
};
The o object's properties are:

o.a — a number
o.b — a getter that returns o.a plus 1
o.c — a setter that sets the value of o.a to half of the value o.c is being set to

Please note that function names of getters and setters defined in an object 
literal using "[gs]et property()" (as opposed to __define[GS]etter__ ) are 
not the names of the getters themselves, even though the 
[gs]et propertyName(){ } syntax may mislead you to think otherwise. To name a 
function in a getter or setter using the "[gs]et property()" syntax, define 
an explicitly named function programmatically using Object.defineProperty 
(or the Object.prototype.__defineGetter__ legacy fallback).

*/