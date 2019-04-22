
import boto3
import json
from math import sin, cos, sqrt, atan2, radians
R = 6373.0

# maximum distance of separation between deviced when user will be warned in the warning variable
#in meters (not km)

warning = 15

print('Loading function')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url=“—“your dynamoDB endpoint table—“)
client = boto3.client('connect')


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
    print(“Event: ", event)
    
    lati = event['queryStringParameters']['lati']
    longi = event['queryStringParameters']['longi']
    time = event['queryStringParameters']['time']
    deviceid = event['queryStringParameters']['serial']
    
    
    #Update table with historic position
    table = dynamodb.Table(‘—your historic GPS table—‘)
    response = table.put_item(
        Item={
            'deviceid': deviceid,
            'time': time,
            'latitude': lati,    
            'longitude': longi }
        )
    
    #Update table with real time position
    table = dynamodb.Table(‘— your realtime GPS table—‘)
    response = table.put_item(
        Item={
            'deviceid': deviceid,
            'latitude': lati,    
            'longitude': longi }
        )        


    #Check distance with its pair device
    #As mentioned, for multi device, this should be extracted from a higher level-
    #DynamoDB table, containing the specific pair of each device
    
    #get info from pair from the real time table
    
    table = dynamodb.Table('— your realtime GPS table—')
    deviceidp = “—your device id—“
    try:
        response = table.get_item(
            Key={
                'deviceid': deviceidp,
            }
        )
    except ClientError as e:
        print(e.response['Error']['Error quering the pair device'])
    else:
        item = response['Item']
        plati = item['latitude']
        plongi = item['longitude']
   
    #now let's calculate distance between them
    #using Haversine formula, implementation found in: https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
    
    lat1 = radians(abs(float(lati)))
    lon1 = radians(abs(float(longi)))
    lat2 = radians(abs(float(plati)))
    lon2 = radians(abs(float(plongi)))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = (R * c)*1000
    
    print("-------------------------------------------------------------")
    print("Distance between devices in meters:", distance)
    print("-------------------------------------------------------------")
    
    #Let's check if the distance between pairing devices exceed the allowed
    #if so, let's call via Amazon Connect
    #We know the warning phone from the Higher DynamoDB table where
    #the relationship between devices and warning numbers is stated
    #for this PoC,  I will assume warning number is this : “—sample phone number—“
    
    if distance > warning:
        print("")
        print("-------------------------------------------------------------")
        print("***** Distance >", warning, " WE SHOULD WARN THE USER")
        print("-------------------------------------------------------------")
        print("")
        response = client.start_outbound_voice_contact(
            DestinationPhoneNumber=‘—destination phone number—‘,
            ContactFlowId=‘—contact flow id—’,
            InstanceId=‘—instance id —‘,
            SourcePhoneNumber=‘— source phone number—‘,
        )
    
    
    #Final considerations:
    print("-------------------------------------")
    print("*****Lambda execution succeeded:****")
    print("-------------------------------------")
    message = '{"deviceid": "GPSIngestLambda", "text": "Coordinates inserted"}'
    #message = '{"deviceid": '+ deviceid + ' , "text": "Coordinates inserted"}'
    
    #Let's get out chaval!
    return respond(None,json.loads(message))
