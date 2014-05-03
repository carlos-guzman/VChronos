var cheerio = require('cheerio');
var request = require('request');
 request = request.defaults({jar: true})
var	url= 'http://sis.nyu.edu/psc/csprod/EMPLOYEE/CSSS/c/NYU_SR.NYU_CLS_SRCH.GBL',
	ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2';
 
var parsePage = function(error, response, html) {
	
// 	if (error || response.statusCode != 200) {
// 		console.log(error);
// 	}
// 	else {
		
// 		$ = cheerio.load(body);
		
// 		$('.one-sala').siblings().each(function(i, elem) {
			
// 			var cinema = $(elem).find('div .col-1');
// 			var cinemaName = $(cinema).find('h5').text();
// 			var cinemaAddress = $(cinema).find('.address-cine').text();
// 			var cinemaCity = $(cinema).find('.city-cine').text(); 
// 			var cinemaPhone = $(cinema).find('.cine-tel').text(); 
 
// 			var schedule = $(elem).find('div .col-2');
// 			$(schedule).find('div .row').each(
// 				function(key,value){
// 				var filmName = $(value).find('div .cel-2 a').text();
// 				var scheduleTime = $(value).find('div .cel-2 .film-orari').text().replace('orari:','');
// 				}
// 				);
 
// })
// 	}

	if (!error && response.statusCode == 200) {
   	console.log(html);
  }
};

request(
    {
        url : url,
        headers : {
            "User-Agent" : ua
        }
    },parsePage
);








// exports.getScraping = function(req, res, next) {
//   request.get('https://sis.nyu.edu/psc/csprod/EMPLOYEE/CSSS/c/NYU_SR.NYU_CLS_SRCH.GBL', function(err, request, body) {
//     if (err) return next(err);
//     var $ = cheerio.load(body);
    
//     var links = [];
//     $(".title a[href^='http'], a[href^='https']").each(function() {
//       links.push($(this));
//     });
    
//   });
// };

