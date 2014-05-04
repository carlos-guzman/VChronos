exports.getInteract = function(req, res) {
  res.render('/schedule/interact', {
    title: 'My Schedule'
  });
};

exports.getCreate = function(req, res) {
  res.render('/schedule/create', {
    title: 'Create your Schedule'
  });
};




