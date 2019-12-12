from collections import namedtuple
import grequests
import base64
import requests
import json
import sys
import warnings
import os
warnings.filterwarnings("ignore")

name = "arlulaapi"


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


def gsearch_exception(r, e):
    return("request failed")


class ArlulaSessionError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class ArlulaSession:

    def __init__(self, key, secret):
        def atob(x): return x.encode('utf-8')
        self.token = base64.b64encode(atob(
            key + ':' + secret)).decode('utf-8')
        self.header = {
            'Authorization': "Basic "+self.token,
        }
        self.baseURL = "https://api.arlula.com"
        self.validate_creds()

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
            return ArlulaObj(json.loads(response.text))

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
            result.append([ArlulaObj(x) for x in json.loads(r.text)])
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
              seats=None,
              webhooks=[],
              emails=[]):

        url = self.baseURL+"/api/order/new"

        headers = self.header

        payload = json.dumps({
            "id": id,
            "eula": eula,
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
