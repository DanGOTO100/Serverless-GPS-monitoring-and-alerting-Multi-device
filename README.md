# What is this project
About creating a Serverless GPS tracking and alerting solution based on AWS API Gateway, Lambda and Amazon Connect.
Commercial geo monitoring GPS solutions are not usually cost-effective, mainly due to the need of servers running 24x7, and expensive digital maps licenses from 3rd party companies. Besides, these system work with proprietary GPS devices not compatible between them, that lock-in the users into each vendor’s devices.
Also, alert and geofencing is normally limited to static geofencing, but:  what if we want to track the distance between two moving points? For these reasons I decided to build my own solution  in the AWS platform using a serverless approach. 


# Objective
Create a non-expensive solution that helps track assets easily and smoothly.

# Design Requirements
The system must be serverless, use Open Data and multi-device, this is: it must accept GPS signal from multiple inputs like a  mobile phone GPS App, GPS 3G/4G devices, and IoT devices. Also, it must support any type format: NMEA or whatever.

**Alerting:** It must alert me if the distance between me and them is bigger than X (configurable) meters. Even if reference points are moving, we must be able to create a portable geofencing

# Overall Architecture

![alt text](https://github.com/DanGOTO100/AWS-Serverless-GPS-tracking-and-alerting/blob/master/ServerlessGPSarchitecture.png) 


# Step by Step description

In the first step of the architecture, we will ingest and decode the GPS location data coming from the GPS enabled devices. Remember that one of the main design’s premises is to be able to ingest data from as many types of devices as possible. Therefore, the project uses the approach of using HTTP to ingest GPS data into the system. This means that any device capable of posting its location data using HTTP protocol, will be compatible with this system. 
As an example: Any GPS device with GPRS/3G capabilities (most of the GPS devices in the market), IoT devices with GPS and 3G modules or even any of the multiple existing mobile Apps (Android or iOS) that are capable of using mobile’s GPS module and store and post the device’s location.  Opening doors to a multi-device approach to GPS monitoring and no more proprietary lock-in into devices.

Amazon API Gateway service will provide us with the a HTTP endpoint where the devices will publish their location to. It will be the front-door for the backend services where we will use and consume the device’s GPS information. If you are not familiar with Amazon API Gateway, please review the Amazon API Gateway documentation.
AWS Lambda is also very important for this first step. Lambda is an AWS service that will allow us to execute code without having to run servers or manage them. Running your backend with AWS Lambda allows you to execute your backend logic only when a request is coming to  Amazon API Gateway, not having servers running 24x7 that might be idle for most of the time. 

In the architecture, Amazon API Gateway will receive the HTTP requests from GPS devices containing their location data.  Amazon API Gateway will invoke AWS Lambda to deal with this data. An AWS Lambda function will execute and will extract the coordinates information from the HTTP message, decode them and will store as  longitude plus latitude degrees format into a database table, in this case an Amazon DynamoDB table.  



The database is exactly the second step of the architecture diagram in figure 1 above.
Amazon DynamoDB is a NoSQL Database that is also serverless: No need to provision and manage servers. It is a high-performance database and fully scalable.
We will use a couple of tables in the database. One table will store real-time location information of the devices, using it for real time visualization on the map. While another table will store all the positions the devices has posted to the system; allowing us to have an historic of the devices’ locations and reproduce, for example, of all locations in any given timeframe.

In the  third step we will consume the location information in real time through a digital map view. To do that, we will use a simple Web App, written in Javascript, that will be served from Amazon S3 and its capability to host static web sites. Therefore, there is no server running to serve the mapping Web application to user’s clients. It is served from Amazon S3, a storage service. The map visualization uses Mapbox GL Javascript API, which is based on the Open Data OpenStreetMap Data Set. The library is great, free and has lots of functionality that will allow us to provide cool visualization of the device’s location on a map.
The Web App can be used on any mobile device or Laptop, accessing it just by its HTTP address.

The fourth and final step is how the geofencing and alerts are defined and triggered. Basically, we are going to compute the distance between different devices’ location and send an alert call through Amazon Connect if the distance between them is bigger than a configurable given distance. This capability can be seen as the usual geofences in GPS systems, but can compute distance even if points are moving, behaving like a “portable” geofence. The specific details in further sections of the post.

Let’s not forget that  Amazon Cognito is used to authorize the Web App’s with read access to the information stored in Amazon DynamoDB, so it can display the location information on the map. Amazon Cognito, fully managed authentication service,  will provide permissions via an IAM role.  

# NMEA format Notes

GPS devices normally use the NMEA  standard and particularly the GPRMC sentences embedded into the HTTP messages to send their GPS location. 
The idea behind the NMEA format is that each piece of information sent, called a sentence, is totally self-contained and independent from other sentences. Each sentence starts with a “$” symbol and cannot be longer than 80 characters. An example of the information sent by the GPS devices using NMEA format via HTTP is below:

````
query=imei=357xxxxxxxx12&rmc=$GPRMC,002347.00,V,4032.35096,N,00554.01761,W,0.023,,210818,,,A*69,AUTO,3661,45,9,0,99.9,C0,0,0,0,M1

````

You can clearly see that we have two different parameters: The imei of the SIM inside the GPS device (GPRS or 3G) and the “rmc” which is basically the NMEA sentence. A full decoding information for each type of sequence can be seen in the following link.

In the ”rmc” parameter the device location, longitude and latitude, – are the elements 3 to 6 in the comma separated sequence.
In the example above, it would this part of the sequence: “4032.35096,N,00354.04761,W”.
A further step is required because the NMEA information has the longitude and latitude in the format  (d)ddmm.mmmm, where d=degrees and m=minutes. We need to convert it into degrees format before storing it into the database.

Tto ingest location information from these devices, you will create and API via Amazon API Gateway and will integrate it with an AWS Lambda function. See the NMEA lambda in this repository.
In this API setup, we need to specify two query parameters: “imei” and “rmc”.  The Lambda function will parse the GPRMC sequence to extract the device imei, longitude and latitude and convert them to degrees format. Once extracted and converted, the code will to store the information into Amazon DynamoDB table. 


In the case of IoT devices, the format to expect depends on the GPS module that is mounted in the device. Normally it will also be NMEA GPRMC sentences, but in other cases it can be already longitude and latitude in degrees format like with the in mobile App case.


