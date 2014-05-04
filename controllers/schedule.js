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


exports.findCourse = function(req, res) {
   var regex = new RegExp(req.query["term"], 'i');

   //Find exact data about classification, number and section
   var query = User.find({course_name: regex},{ description:regex}, {instructors:regex}, {classification: regex }).sort({"updated_at":-1}).sort({"created_at":-1}).limit(10);
      
    // Execute query in a callback and return users list
  query.exec(function(err, users) {
    if (!err) {
       // Method to construct the json result set
       var result = buildResultSet(users); 
       res.send(result, {
          'Content-Type': 'application/json'
       }, 200);
    } else {
       res.send(JSON.stringify(err), {
          'Content-Type': 'application/json'
       }, 404);
    }
  });
};

