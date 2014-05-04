module.exports = function (set, validator) {
  var combinations = [];
  var length = set.length;
  for (var i = length - 1; i > 0; i--) {
    for (var j = 0; j < length - i; j++) {
      var base = set.slice(j,j+i);
      var add = set.slice(j+i);
      for (int k = 0; k < add.length; k++) {
        var temp = base.concat([add[k]]);
        if (validator(temp)) {
          combinations.push(temp);
        }
      }
    }
  }
  return combinations;
}