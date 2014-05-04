exports.long_date = function(date) {
  return new Date(date.replace(/\//g,"-"));
}
exports.short_date = function(day, hour) {
  var days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  hour = hour.split(" ");
  hour[0] = hour[0].split(".");
  if (hour[1] == "PM") {
    hour[0][0] += parseInt(hour[0]) + 12;
  }
  hour[0][1] = parseInt(hour[0][1]);
  var d = new Date(0);
  d.setHours(d.getHours() + 24*days.indexOf(day));
  d.setHours(d.getHours() + hour[0][0], hour[0][1]);
  return d;
}
