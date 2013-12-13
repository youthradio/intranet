/***
 * roundNumber()
 *  A simple function to round a decimal to a specified
 *  number of decimal places.
 *
 *  Arguments: number to round, number of decimal places
 *  Returns: a float
 ****/
function roundNumber(number, decimals) {
    var newnumber = new Number(number+'').toFixed(parseInt(decimals));
    return parseFloat(newnumber);
};

/***
 * hashCode()
 *  A simple function to determine a quick hash of a string.
 *
 *  Returns: a 32 bit integer
 ****/
String.prototype.hashCode = function(){
    var hash = 0, i, char;
    if (this.length == 0) return hash;
    for (i = 0; i < this.length; i++) {
        char = this.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return hash;
};
