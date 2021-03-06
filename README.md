# Portal

## Problem Statement
Currently, in order to book a flight online, a customer would go directly into an airline website to search for the flights with their desired date and destination. If they are not satisfied with the result, they would simply switch over to another airline website to seek a better deal. Some clients would repeat such search using a different date and time for the flight in order to find the best prices since the flight fare fluctuates according to the date and time. This process ends up being very time-consuming and inefficient. Our project proposes a solution to this issue.
## Solution
Portal is a web based application which offers the most competitive flight fares combination to customers. The combination encapsulates where, when, and how to purchase such ticket for the trip.  
  
At the core of our application shall be a custom designed machine learning model. We shall research and design our own architecture for multiple models that attempt to solve this problem such that we can come up with the optimal one which the web based app shall use as the final solution.  
  
The models will therefore require at their base a large data set that can be used to train them, this will require a solid backend and a few web scraping scripts to be created additionally. Specifically, new data will be polled and pushed to the data set, further training the models every day. Furthermore, the model will be coded from scratch using the flexible and low level library Tensor Flow which will allow for high flexibility and control.  
  
The models themselves will be decided on and fine-tuned during the project depending on their performance measures; minimal spending by the user on a flight, minimal transfers and minimal time spent in the air. This means changing things from the possible inputs such as the time till trip to the overall architecture of the model.  
  
As for the web application itself, it shall have a UI containing multiple search criteria and preferences while also displaying a list of flight suggestions along with their performance measures. Also, it must be connected to the machine learning models and will be communicating with it through REST calls, but must also display the reasoning and the process behind the machine learning algorithm coming to such conclusion.
