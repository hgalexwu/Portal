requirejs(['googleapis'], function(googleapis) {
  var google = require('googleapis');
  var ml = google.ml('v1');

  function auth(callback) {
      google.auth.getApplicationDefault(function(err, authClient) {
          if (err) {
              return callback(err);
          }

          if (authClient.createScopedRequired && authClient.createScopedRequired()) {
              authClient = authClient.createScoped([
                  'https://www.googleapis.com/auth/cloud-platform'
              ]);
          }
          callback(null, authClient);
      });
  }
})


  auth(function(err, authClient) {
          if (err) {
              console.error(err);
          } else {
              var ml = google.ml({
                  version: 'v1',
                  auth: authClient
              });

              // Predict
              ml.projects.predict({
                  name: 'projects/astute-backup-134320/models/Portal_First_Estimators_Model/versions/a',
                  resource: {
                      instances: [instance]
                  }
              }, function(err, result) {
                  if (err) {
                      return callback(err);
                  }
                  console.log(JSON.stringify(result));
              });
            }
        });