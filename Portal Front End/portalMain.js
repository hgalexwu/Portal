    var returnButton = document.getElementById("Return");
    var oneWayButton = document.getElementById("OneWay");
    var devButton = document.getElementById("Developer");

    var devDateToday = false;

    returnButton.onclick = function() {
      $('#returnDate').show();
      $("#devDate").addClass('hidden');
      devDateToday = false;

    } 

    oneWayButton.onclick = function() {
      $('#returnDate').hide();
      $("#devDate").addClass('hidden');
      devDateToday = false;

    } 

    devButton.onclick = function() {
      $('#returnDate').show();
      $("#devDate").removeClass('hidden');
      devDateToday = true;
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

        var dateTo = document.getElementById("dateTo").value;
        var dateFrom = document.getElementById("dateFrom").value;
        var dateToday = document.getElementById("dateToday").value;

        if(dateTo === ""){
          var dateArray = getDates(new Date(), new Date(dateFrom));
        } else if(devDateToday){
          var dateArray = getDates(new Date(dateToday), new Date(dateTo));
        } else {
          var dateArray = getDates(new Date(), new Date(dateTo));
        }

        
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

        for(j = 0; j < response.Price_To.length; j++){
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
              data: datasetFrom,
              fill: false,
            }, {
              label: 'Price From: ' + document.getElementById("flyingTo").value,
              fill: false,
              backgroundColor: window.chartColors.blue,
              borderColor: window.chartColors.blue,
              data: datasetTo,
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
        var dateToday = document.getElementById('dateToday').value;

      //Add some if statements for the one way, return and dev type

	    $.ajax({
	        type: "POST",
          url: "http://127.0.0.1:8000/index/",
	        data: { 
            flyingFrom: flyingFrom,
            flyingTo: flyingTo,
            dateFrom: dateFrom,
            dateTo: dateTo,
            todayDate: dateToday,
            csrfmiddlewaretoken: '{{ csrf_token }}',
          },
	        success: callbackFunc
	    });
		
};
