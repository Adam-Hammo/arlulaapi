import grequests
import base64
import requests
import json
import sys
import warnings
import os
import math
import pgeocode
# warnings.filterwarnings("ignore")

name = "arlulaapi"

# Object generator that converts returned JSON into a Python object
class ArlulaObj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [ArlulaObj(x) if isinstance(
                    x, dict) else x for x in b])
            else:
                setattr(self, a, ArlulaObj(b) if isinstance(b, dict) else b)

    def __repr__(self):
        return str(['{}: {}'.format(attr, value) for attr, value in self.__dict__.items()])[1:-1].replace('\'', '')

# Exception when group searching
def gsearch_exception(r, e):
    return("request failed")

# Custom Exception Class
class ArlulaSessionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

# Custom Warning Class
class ArlulaSessionWarning(Warning):
    pass

# The ArlulaSession code
# At some point, this should be separated into a diff file
class ArlulaSession:

    def __init__(self, key, secret):
        # Encode the key and secret
        def atob(x): return x.encode('utf-8')
        self.token = base64.b64encode(atob(
            key + ':' + secret)).decode('utf-8')
        self.header = {
            'Authorization': "Basic "+self.token,
        }
        self.baseURL = "https://api.arlula.com"
        self.max_cloud = 100
        # Supplier max bounds on cloud values
        self.max_cloud_vals = {"landsat": 100, "SIIS": 100, "maxar": 100}
        self.validate_creds()

    # Enables use of `with` keyword
    def __enter__(self):
        return self

    # Enables use of `with` keyword
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    # Removes sensitive information
    def close(self):
        self.token = None
        self.header = None

    def set_max_cloud(self, val):
        if (val<0 or val > 100) :
            raise ArlulaSessionError("Max cloud value must be between 0 and 100")
        self.max_cloud = val

    def get_max_cloud(self):
        return self.max_cloud

    def filter(self, r):
        if r['supplier']=="" :
            return False
        return r['cloud']/self.max_cloud_vals.get(r["supplier"])*100<=self.max_cloud

    def validate_creds(self):
        url = self.baseURL+"/api/test"

        headers = self.header

        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)

    def search(self,
               start=None,
               end=None,
               res=None,
               lat=None,
               long=None,
               north=None,
               south=None,
               east=None,
               west=None):
        url = self.baseURL+"/api/search"

        querystring = {"start": start, "end": end,
                       "res": res, "lat": lat, "long": long,
                       "north": north, "south": south, "east": east, "west": west}

        querystring = {k: v for k, v in querystring.items()
                       if v is not None or v == 0}

        headers = self.header
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return [ArlulaObj(x) for x in json.loads(response.text) if self.filter(x)]

    def gsearch(self,
                params):
        searches = []
        for p in params:
            url = self.baseURL+"/api/search"

            querystring = {"start": p.get('start'), "end": p.get('end'), "res": p.get('res'),
                           "lat": p.get('lat'), "long": p.get('long'), "north": p.get('north'),
                           "south": p.get('south'), "east": p.get('east'), "west": p.get('west')}

            querystring = {k: v for k, v in querystring.items()
                           if v is not None or v == 0}

            headers = self.header

            searches.append(grequests.get(
                url, headers=headers, params=querystring))

        response = grequests.map(searches, exception_handler=gsearch_exception)
        result = []
        for r in response:
            result.append([ArlulaObj(x) for x in json.loads(r.text) if self.filter(x)])
        return result

    def get_order(self,
                  id=""):

        url = self.baseURL+"/api/order/get"

        querystring = {"id": id}

        headers = self.header

        response = requests.request(
            "GET", url, headers=headers, params=querystring)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return ArlulaObj(json.loads(response.text))

    def list_orders(self):

        url = self.baseURL+"/api/order/list"

        headers = self.header

        response = requests.request(
            "GET", url, headers=headers)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return [ArlulaObj(json.loads(str(r).replace("\'", "\"")))
                    for r in eval(response.text, {'__builtins__': None}, {})]

    def order(self,
              id=None,
              eula=None,
              trim=False,
              seats=None,
              webhooks=[],
              emails=[]):

        url = self.baseURL+"/api/order/new"

        headers = self.header

        payload = json.dumps({
            "id": id,
            "eula": eula,
            "trim": trim,
            "seats": seats,
            "webhooks": webhooks,
            "emails": emails
        })

        response = requests.request("POST", url, data=payload, headers=headers)

        if response.status_code != 200:
            raise ArlulaSessionError(response.text)
        else:
            return ArlulaObj(json.loads(response.text))

    def get_resource(self,
                     id="",
                     filepath="",
                     suppress=False):
        if filepath == "":
            raise ArlulaSessionError(
                "You must specify a filepath for the download")
        with open(filepath, 'wb') as f:
            url = self.baseURL + "/api/order/resource/get"
            querystring = {"id": id}

            headers = self.header
            response = requests.request(
                "GET", url, headers=headers, params=querystring,  stream=True)
            total = response.headers.get('content-length')

            if response.status_code != 200:
                raise ArlulaSessionError(response.text)

            if total is None:
                f.write(response.content)
            else:
                downloaded = 0
                total = int(total)
                for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50*downloaded/total)
                    if not suppress:
                        sys.stdout.write('\r[{}{}]{:.2%}'.format(
                            '█' * done, '.' * (50-done), downloaded/total))
                        sys.stdout.flush()
        if not suppress:
            sys.stdout.write('\n')
            sys.stdout.write('download complete\n')

    def get_order_resources(self,
                            id="",
                            folder="",
                            suppress=False):
        if not os.path.exists(folder):
            os.makedirs(folder)
        res = self.get_order(id=id)
        counter = 1
        total = len(res.resources)
        for r in res.resources:
            url = self.baseURL + "/api/order/resource/get"
            querystring = {"id": id}

            headers = self.header

            if not suppress:
                print("File {} of {}".format(counter, total))
            try:
                self.get_resource(id=r.id, filepath=folder +
                                  "/"+r.name, suppress=suppress)
            except Exception as e:
                print("Error retrieving file {}, id={}, filename={}".format(
                    counter, r.id, r.name))
                print(e)
            counter += 1
        if not suppress:
            print("All files downloaded")

    def parse_postcode(self, res):
        if math.isnan(res.latitude):
            raise ArlulaSessionError(
                "Could not find postcode {}".format(res.postal_code))
        if res.accuracy >= 5:
            warnings.warn(
                "Postcode {} lat/long could be inaccurate".format(res.postal_code), ArlulaSessionWarning)
        return {'postcode': res.postal_code, 'lat': res.latitude, 'long': res.longitude, 'name': res.place_name}

    def search_postcode(self,
                        start=None,
                        end=None,
                        res=None,
                        country=None,
                        postcode=None,
                        boxsize=None):
        dist_to_deg_lat = 110.574
        dist_to_deg_long_factor = 111.32
        try:
            nomi = pgeocode.Nominatim(country)
        except ValueError:
            raise ArlulaSessionError("Invalid country code {}".format(country))
        if isinstance(postcode, str) or isinstance(postcode, int):
            postcode = [postcode]
        data = nomi.query_postal_code(postcode)
        params = []
        pcs = [self.parse_postcode(d[1]) for d in data.iterrows()]
        if boxsize is None:
            params = [{'start': start, 'end': end, 'res': res,
                       'lat': pc['lat'], 'long': pc['long']} for pc in pcs]
        else:
            params = [{'start': start, 'end': end, 'res': res,
                       'south': pc['lat']-boxsize/dist_to_deg_lat,
                       'north': pc['lat']+boxsize/dist_to_deg_lat,
                       'west': pc['long']-boxsize/(math.cos(math.radians(pc['lat']))*dist_to_deg_long_factor),
                       'east': pc['long']+boxsize/(math.cos(math.radians(pc['lat']))*dist_to_deg_long_factor)} for pc in pcs]
        search_res = self.gsearch(params=params)
        if len(pcs) == 1:
            return ArlulaObj({'location': pcs[0], 'data': search_res[0]})
        return [ArlulaObj({'location': pcs[i], 'data': search_res[i]}) for i in range(0, len(pcs))]
