var mongoose = require('mongoose');
var course_dep = require('./Course');
var courseSchema = course_dep.courseSchema;
var timeRangeSchema = course_dep.timeRangeSchema;
var Course = course_dep.Course;
var combinations = require('../helpers/combinations');

var schedulerSchema = new mongoose.Schema({
  preferences: {type: [courseSchema], required: true},
  restrictions: {
    type: {
      times: [timeRangeSchema],
      allow_sucessive: Boolean,
      allow_sucessive_if_same_loc: Boolean,
      courses_by_classification: [{
        classification: String,
        total: Number
      }],
      unit_range: {
        min: {type: Number, default: 16},
        max: {type: Number, default: 18}
      }
    },
    required: true
  }
});

schedulerSchema.methods.getValidator = function () {
  return function (schedule) {
    var units = 0;
    for (var i = 0; i < schedule.length; i++) {
      var course = schedule[i]
      units += course.units;
      if (units > this.restrictions.unit_range.max) {
        return false;
      }
      for (var j = i+1; j < schedule.length; j++) {
        if (course.conflictsWith(schedule[j])) {
          return false;
        }
      }
    }
    if (units < this.restrictions.unit_range.min) {
      return false;
    }
    return true;
  };
}



schedulerSchema.methods.createSchedules = function (cb) {
  Course.find(
    { _id: { $in: this.preferences } },
    function (err, res) {
      if (err) {
        return err;
      } else {
        return combinations(res, this.getValidator());
      }
    }
  );
};


module.exports = mongoose.model('Course', courseSchema);
