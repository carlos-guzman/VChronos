var secrets = require('../config/secrets');
var Course = require('../models/Course');
var date = require('../helpers/date');

exports.create = function(req, res) {

  var not_blank = ["class_name", "classification", "college", "course_name", "is_open", "loc_code"];
  for (var i = 0; i < not_blank.length; i++) {
    req.assert(not_blank[i], not_blank[i]+' cannot be blank').notEmpty();
  }
  req.assert('secret', 'Secret does not match').equals(secrets.sessionSecret);

  var errors = req.validationErrors();
  if (errors) {
    return errors;
  } else {
    for (var i = 0; i < req.body.meet_data.length; i++) {
      var data = req.body.meet_data[i];
      data.start = date.short_date(data.day, data.start);
      data.end = date.short_date(data.day, data.start);
      delete req.body.meet_data[i].day;
    }
    req.body.session = {
      start: date.long_date(req.body.session.start),
      end: date.long_date(req.body.session.end),
    }
    var course = new Course(req.body);

    Course.findOne(
      {class_name: req.body.class_name, section: req.body.section},
      function(err, existingCourse) {
        if (existingCourse) {
          return 'Course with that class_name and section already exists.';
        } else if (err) {
          return err;
        } else {
          course.save(function(err) {
            if (err) {
              return next(err);
            }
          });
          return 'Course created successfuly.';
        }
      }
    );
  }
};