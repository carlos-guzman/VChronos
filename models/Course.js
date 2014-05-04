var mongoose = require('mongoose');

var timeRangeSchema = new mongoose.Schema({
  start: {type: Date, required: true},
  end: {type: Date, required: true},
});

timeRangeSchema.methods.conflictsWith = function (other) {
  return ((this.start < other.start) && (this.end > other.start)) ||
         ((this.start > other.start) && (this.start < other.end));
};

timeRangeSchema.methods.duration = function () {
  return this.end - this.start;
};

var courseSchema = new mongoose.Schema({
  class_name: {type: String, index: true, required: true},
  classification: {type: String, index: true, required: true},
  college: {type: String, index: true, required: true},
  component: String,
  course_name: {type: String, index: true},
  description: {type: String, default: '', index: true},
  grading: String,
  instructors: {type: [String], default: [''], index: true},
  is_open: {type: Boolean, required: true},
  loc_code: {type: String, required: true},
  location: String,
  meet_data: {type: [timeRangeSchema], required: true},
  notes: String,
  number: String,
  section: String,
  session: {type: mongoose.Schema.ObjectId, ref: 'timeRangeSchema'},
  units: Number
});

courseSchema.methods.conflictsWith = function (other) {
  if (this.session.conflictsWith(other.session)) {
    for (i = 0; i < this.meet_data.length; i++) {
      for (j = 0; j < other.meet_data.length; j++) {
        if (this.meet_data[i].conflictsWith(other.meet_data[j])){
          return true;
        }
      }
    }
  } else {
    return false;
  }
};

exports.Course = mongoose.model('Course', courseSchema);
exports.courseSchema = courseSchema;
exports.timeRangeSchema = timeRangeSchema;
