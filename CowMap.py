
# coding: utf-8

# In[1]:

import googlemaps, pandas, json, requests


# In[2]:

##Having something like this would be ideal. (for later)
#origin = input("Where are you starting?")
#destination = input("Where do you want to finish?")
#waypoints = input("Where would you like to pass through?")
#deviation = input("What distance from your current route is acceptable in metres?")


# In[3]:

data=pandas.read_excel('FarmData.xlsx')


# In[4]:

data["Address1"] = data["Address"]+", "+data["City"]+", "+data["State"]


# In[9]:

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


# In[18]:

data['lat'] = latt
data['lng'] = longg
data['address_formatted'] = addresss


# In[786]:

dist_main_ = []

GOOGLE_MAPS_API_URL = 'http://maps.googleapis.com/maps/api/directions/json'

params = {
    'units' : 'metric',
    'origin' : 'Brisbane, Queensland',
    'waypoints': "Beaudesert, Queensland 4285|Capella, Queensland 4723|Blackall, Queensland 4472|Roma, Queensland 4455|",
    'destination' : 'Brisbane, Queensland',
    'optimizeWaypoints' : True,
}

# Do the request and get the response data
req = requests.get(GOOGLE_MAPS_API_URL, params=params)
res = req.json()

dist_main_ = [res['routes'][0]['legs'][i]['distance']['value'] for i in range(len(res['routes'][0]['legs']))]
dist_main = sum(dist_main_)


# In[22]:

dist_dev_fin = []

for lt, lg in zip(data['lat'], data['lng']):
    if lt != None:
        GOOGLE_MAPS_API_URL = 'http://maps.googleapis.com/maps/api/directions/json'

        params = {
            'units' : 'metric',
            'origin' : 'Brisbane, Queensland',
            'waypoints': "Beaudesert, Queensland 4285|Capella, Queensland 4723|Blackall, Queensland 4472|Roma, Queensland 4455|"+str(lt)+','+str(lg),
            'destination' : 'Brisbane, Queensland',
            'optimizeWaypoints' : True,
        }

        # Do the request and get the response data
        req = requests.get(GOOGLE_MAPS_API_URL, params=params)
        res = req.json()
        dist_dev_ = []
        
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
        dist_dev_vin.append(None)
    


# In[24]:

data['deviation'] = dist_dev_fin


# In[146]:

df = pandas.DataFrame(columns = list(data.keys()))
df1 = data


# In[169]:

df = df1.drop(df1[(df1.deviation > 50000)].index)


# In[170]:

df = df.set_index('deviation')


# In[171]:

df = df.drop([None])


# In[168]:

Excel = pandas.ExcelWriter('FarmsOnRouteUnder50Km.xlsx', engine='xlsxwriter')
df.to_excel(Excel, sheet_name='Sheet1')
Excel.save()

