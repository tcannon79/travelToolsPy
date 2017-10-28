# coding: utf-8

import googlemaps, pandas, json, requests

GOOGLE_MAPS_API_URL = 'http://maps.googleapis.com/maps/api/directions/json'


origin = input("Where are you starting?")
destination = input("Where do you want to finish?")
waypoints = input("Where would you like to pass through?")
deviation = int(input("What distance from your current route is acceptable in metres?"))

##        params = {
##            'units' : 'metric',
##            'origin' : 'Brisbane, Queensland',
##            'waypoints': "Beaudesert, Queensland 4285|Capella, Queensland 4723|Blackall, Queensland 4472|Roma, Queensland 4455|",
##            'destination' : 'Brisbane, Queensland',
##            'optimizeWaypoints' : True,
##        }

## deviation = 50000


data=pandas.read_excel('FarmData.xlsx')
data["Address1"] = data["Address"]+", "+data["City"]+", "+data["State"]


# Look up the coordinates and addresses of desired farms
latt = []
longg = []
addresss = []

for item in data['Address1']:
    GOOGLE_MAPS_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

    params = { 
        'address': item,
        'sensor': 'false'
    }
    # Do the request and get the response data
    req = requests.get(GOOGLE_MAPS_API_URL, params=params)
    res = req.json()
    
    if (res['status'] != 'ZERO_RESULTS' and res['status'] != []):
        # Use the first result
        result = res['results'][0]
        
        latt.append(result['geometry']['location']['lat'])
        longg.append(result['geometry']['location']['lng'])
        addresss.append(result['formatted_address'])
        
    else:
        latt.append(None)
        longg.append(None)
        addresss.append(None)


data['lat'] = latt
data['lng'] = longg
data['address_formatted'] = addresss


params = {
            'units' : 'metric',
            'origin' : origin,
            'waypoints': waypoints,
            'destination' : destination,
            'optimizeWaypoints' : True,
        }


# Do the request and get the response data
req = requests.get(GOOGLE_MAPS_API_URL, params=params)
res = req.json()

dist_main_ = [res['routes'][0]['legs'][i]['distance']['value'] for i in range(len(res['routes'][0]['legs']))]
dist_main = sum(dist_main_)


# Now calculate the deviation caused by adding new points

dist_dev_fin = []

for lt, lg in zip(data['lat'], data['lng']):
    if lt != None:
        params['destination'] = params['destination']+str(lt)+','+str(lg)

        # Do the request and get the response data
        req = requests.get(GOOGLE_MAPS_API_URL, params=params)
        res = req.json()
        
        if res['routes'] != []:
            dist_dev_ = [res['routes'][0]['legs'][i]['distance']['value'] for i in range(len(res['routes'][0]['legs']))]           
            dist_dev = sum(dist_dev_)    
            
            if dist_dev != 0:
                dist_dev_fin.append(dist_dev - dist_main)
            else: 
                dist_dev_fin.append(None)
        else:
            dist_dev_fin.append(None)
    
    else:
        dist_dev_fin.append(None)
    

data['deviation'] = dist_dev_fin

# Output results to new Spreadsheet
df = pandas.DataFrame(columns = list(data.keys()))
df = df.drop(df1[(df1.deviation > deviation)].index) # Drop all farms that increase the deviation from the path above acceptable parameters
df = df.set_index('deviation')
df = df.drop([None]) # Drop malformed data points

Excel = pandas.ExcelWriter('FarmsOnRouteUnder' + str(deviation//1000) + 'Km.xlsx', engine='xlsxwriter')
df.to_excel(Excel, sheet_name='Sheet1')
Excel.save()
