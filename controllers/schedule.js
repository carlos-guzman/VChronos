exports.index = function(req, res) {
  res.render('schedule', {
    title: 'My Schedule'
  });
};