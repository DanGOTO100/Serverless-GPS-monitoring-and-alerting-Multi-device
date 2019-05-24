# What is this project
About creating a Serverless GPS tracking and alerting solution based on AWS API Gateway, Lambda and Amazon Connect.

# Objective
Create a non-expensive solution that helps track assets easily and smoothly.

# Design Requirements
The system must be serverless, use Open Data and multi-device, this is: it must accept GPS signal from multiple inputs like a  mobile phone GPS App, GPS 3G/4G devices, and IoT devices. Also, it must support any type format: NMEA or whatever.

**Alerting:** It must alert me if the distance between me and them is bigger than X (configurable) meters. Even if reference points are moving, we must be able to create a portable geofencing

# Overall Architecture

![alt text](https://github.com/DanGOTO100/IoTAlarmsystem/blob/master/serverlessGPSarchitecture.png) 

