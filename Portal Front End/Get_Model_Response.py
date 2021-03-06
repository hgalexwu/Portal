from oauth2client.client import GoogleCredentials
import googleapiclient.discovery

def predict_json(project, model, instances, version=None):
    """Send json data to a deployed model for prediction.

    Args:
        project (str): project where the Cloud ML Engine Model is deployed.
        model (str): model name.
        instances ([Mapping[str: Any]]): Keys should be the names of Tensors
            your deployed model expects as inputs. Values should be datatypes
            convertible to Tensors, or (potentially nested) lists of datatypes
            convertible to tensors.
        version: str, version of the model to target.
    Returns:
        Mapping[str: any]: dictionary of prediction results defined by the
            model.
    """
    # Create the ML Engine service object.
    # To authenticate set the environment variable
    # GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
    service = googleapiclient.discovery.build('ml', 'v1')
    name = 'projects/{}/models/{}'.format(project, model)

    if version is not None:
        name += '/versions/{}'.format(version)
    response = service.projects().predict(
        name=name,
        body=input
    ).execute()
    if 'error' in response:
        raise RuntimeError(response['error'])

    return response['predictions']


input = {"instances": [{"arrival": 'KUL',
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
                        "days_until_departure": 1}
                       ]}


project_name = "astute-backup-134320"
model_name = "Portal_First_Estimators_Model"
version_name = "a"

if __name__ == "__main__":
    return {"caaca":"pipi"}
  #return  predict_json(project_name, model_name, input, version_name)