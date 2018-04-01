var instance = {
        "arrival": 'KUL',
        "distance": 16700,
        "booking_date": "01/07/18",
        "city_status_destination": 3,
        "direct": 0,
        "continent_source": 'NA',
        "departure": 'MIA',
        "stops": 2,
        "city_status_source": 3,
        "country_source": 'US',
        "season": 0,
        "continent_destination": 'AS',
        "country_destination": 'MY',
        "airline": 'Air Canada Rouge',
        "nb_flights_offered": 24,
        "international": 1,
        "travel_date": '01/08/18',
        "month_of_travel": 1,
        "days_until_departure": 1
      }

    var returnButton = document.getElementById("Return");
    var oneWayButton = document.getElementById("OneWay");
    var devButton = document.getElementById("Developer");

    returnButton.onclick = function() {
      $('#returnDate').show();
      $("#devDate").addClass('hidden');

    } 

    oneWayButton.onclick = function() {
      $('#returnDate').hide();
      $("#devDate").addClass('hidden');

    } 

    devButton.onclick = function() {
      $('#returnDate').show();
      $("#devDate").removeClass('hidden');
    } 

    

    Date.prototype.addDays = function(days) {
       var dat = new Date(this.valueOf())
       dat.setDate(dat.getDate() + days);
       return dat;
    }

   function getDates(startDate, stopDate) {
      var dateArray = new Array();
      var currentDate = startDate;
      while (currentDate <= stopDate) {
        dateArray.push(currentDate)
        currentDate = currentDate.addDays(1);
      }
      return dateArray;
    }
      
      function callbackFunc(response) {
  	    // do something with the response

  	    console.log("response received")
  	    console.log(response);


        console.log(response.Price_To[0].predictions[0]);

        var dateArray = getDates(new Date(), (new Date(document.getElementById("dateTo").value)));
        var sexyDateArray = new Array();
        var count = 0;
        for (i = 0; i < dateArray.length; i++ ) {
            var month = dateArray[i].getUTCMonth() + 1; //months from 1-12
            var day = dateArray[i].getUTCDate();
            var year = dateArray[i].getUTCFullYear();

            newdate = year + "/" + month + "/" + day;
            sexyDateArray.push(newdate);
        }

        var datasetTo = new Array();
        var datasetFrom = new Array();

        for(j = 0; j < sexyDateArray.length; j++){
          datasetTo.push(response.Price_To[j].predictions[0]);
        }

        for(k=0; k<response.Price_From.length; k++){
          datasetFrom.push(response.Price_From[k].predictions[0]);
        }
          

        var MONTHS = sexyDateArray;
        var config = {
          type: 'line',
          data: {
            labels: MONTHS,
            datasets: [{
              label: 'Price From: ' + document.getElementById("flyingFrom").value,
              backgroundColor: window.chartColors.red,
              borderColor: window.chartColors.red,
              data: datasetTo,
              fill: false,
            }, {
              label: 'Price From: ' + document.getElementById("flyingTo").value,
              fill: false,
              backgroundColor: window.chartColors.blue,
              borderColor: window.chartColors.blue,
              data: datasetFrom,
            }]
          },
          options: {
            responsive: true,
            title: {
              display: true,
              text: 'Graphical Representation of Predicted Prices'
            },
            tooltips: {
              mode: 'index',
              intersect: false,
            },
            hover: {
              mode: 'nearest',
              intersect: true
            },
            scales: {
              xAxes: [{
                display: true,
                scaleLabel: {
                  display: true,
                  labelString: 'Dates'
                }
              }],
              yAxes: [{
                display: true,
                scaleLabel: {
                  display: true,
                  labelString: 'Value'
                }
              }]
            }
          }
        };

          var ctx = document.getElementById('myChart').getContext('2d');
          window.myLine = new Chart(ctx, config);
      
  
	  }
	  

      var button = document.getElementById("search");


      button.onclick = function(){
        var flyingFrom = document.getElementById('flyingFrom').value;
        var dateFrom = document.getElementById('dateFrom').value;
        var flyingTo = document.getElementById('flyingTo').value;
        var dateTo = document.getElementById('dateTo').value;

	    $.ajax({
	        type: "POST",
          url: "http://127.0.0.1:8000/index/",
	        data: { 
            flyingFrom: flyingFrom,
            flyingTo: flyingTo,
            dateFrom: dateFrom,
            dateTo: dateTo,
            csrfmiddlewaretoken: '{{ csrf_token }}',
          },
	        success: callbackFunc
	    });
		
};
