
import boto3
import json

print('Loading function')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="-- your endpoint —“)


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
   
   
    #get information from HTTP message
    print("EVENTO: ", event)
   
    coords = event['queryStringParameters']['rmc']
    #time = event['queryStringParameters']['time’].  Check if your device sends time info., some of them don´t
    time = "2018-9-90" .  # in case the device doesn´t send the time info.
    imei = event['queryStringParameters']['imei']

    splitquery = coords.split(",")

    #Convert NMEA GPRMC sentence to latitude an longitude in degrees before calling dynamo
    #more info here: http://home.mira.net/~gnb/gps/nmea.html#gprmc        

    lati = float(splitquery[3])
    latid = splitquery[4]
    longi = float(splitquery[5])
    longid = splitquery[6]

    latideg1 = int(lati/100)
    latideg2 = (lati - latideg1*100)/60
    latideg = (latideg1 + latideg2)

    longideg1 = int(longi/100)
    longideg2 = (longi - longideg1*100)/60
    longideg = (longideg1 + longideg2)

    if latid == "S": latideg = latideg * (-1)
    if longid == "W": longideg = longideg * (-1)

    latideg = str(latideg)
    longideg = str(longideg)

    print("NMEA data converted: ",latideg, longideg)
   
    deviceid = imei
    
    #Update table with historic position
    table = dynamodb.Table(‘-your historic GPS table -’)
    response = table.put_item(
        Item={
            'deviceid': deviceid,
            'time': time,
            'latitude': latideg,    
            'longitude': longideg }
        )
    
    #Update table with real time position
    table = dynamodb.Table(‘-your real time GPS table -')
    response = table.put_item(
        Item={
            'deviceid': deviceid,
            'latitude': latideg,    
            'longitude': longideg }
        )        

    #Final considerations:        
    message = '{"deviceid": "GPSNMEAformat", "text": "Coordinates inserted"}'
    #message = '{"deviceid": '+ deviceid + ' , "text": "Coordinates inserted"}'
    
    #Let's get out chaval!
    return respond(None,json.loads(message))
