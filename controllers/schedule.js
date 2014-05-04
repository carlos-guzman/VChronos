/**
 * GET /schedules
 * Schedule.
 */

exports.create = function(req, res) {
  res.render('schedule/create', {
    title: 'Create My Schedule'
  });
};

exports.interact = function(req, res) {
  res.render('schedule', {
    title: 'View/Edit My Schedules'
  });
};