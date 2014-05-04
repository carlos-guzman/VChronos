User = mongoose.model('User'); // Declare a new mongoose User

app.get('/search_member', function(req, res) {
   var regex = new RegExp(req.query["term"], 'i');

   //Look in course name, description, instructors and hopefully classification+number combined
   var query = User.find({course_name: regex},{ description:regex}, {instructors:regex}, {'classification': 1 }).sort({"updated_at":-1}).sort({"created_at":-1}).limit(10);
        
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
});