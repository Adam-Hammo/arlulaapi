# **Arlula API Python Package**

## Prerequisites
This package requires an active Arlula account and access to the API credentials. If you don't have an account, you can create one at [api.arlula.com/signup](https://api.arlula.com/signup).

## Installation
```bash
pip install arlulaapi
```
## Initiation
Instantiate an ArlulaSession object using your API credentials as below. This will validate your credentials and store them for the remainder of the session.
```python
import arlulaapi

"""using the `with` keyword (recommended)"""
with arlulaapi.ArlulaSession(key, secret) as arlula_session :
    # Call required methods

"""explicitly defining the session"""
arlula_session = arlulaapi.ArlulaSession(key, secret)
# Call required methods
# close() removes your key and secret from the session, if desired
arlula_session.close()
```

## Utilities
A maximum cloud filter can be set on search results. If unset, it defaults to 100%.
```python
# Only return images with <40% cloud
arlula_session.set_max_cloud(40)
```

## API Endpoints
This package contains methods for each of the supported API endpoints. Each method returns an object as prescribed in the Arlula API documentation. The available parameters and an example of each method is below:
### Search
```python
# Available parameters:
search_result = arlula_session.search(
    start="string",
    end="string"
    res="string",
    lat=float,
    long=float,
    north=float,
    south=float,
    east=float,
    west=float
)

search_result = arlula_session.search(
    start="2014-01-01",
    res="vlow",
    lat=40.84,
    long=60.15
)
```
### Order
```python
order = arlula_session.order(
    id=orderId,
    eula="",
    trim=False,
    seats=1,
    webhooks=[...],
    emails=[...]
)
```
### Get resource
```python
## Downloads the resource to the specified filepath
# Optional suppress parameter controls console output
arlula_session.get_resource(
    id=resourceId,
    filepath="downloads/thumbnail.jpg",
    # optional
    suppress="false"
)
```
### Get order(s)
```python
order = arlula_session.get_order(
    id="orderId"
)

orders = arlula_session.list_orders()
```
## Other methods _(experimental)_
As well as supporting all of the Arlula API endpoints, this package provides other mechanisms of utilising the API.

**Group search**

The ArlulaSession `gsearch` method allows you to perform multiple searches at once, and have the results collated into a large search result object. To use the group search method, pass a list of _GroupSearch_ objects, as below. The parameters for each search must pass the same requirements as the `search` method.
```python
group_search = [
    {
        "start":"2014-01-01",
        "res":"vlow",
        "lat":40.84,
        "long":60.15
    },
    {
        "start":"2014-01-01",
        "end":"2014-02-01",
        "res":"vlow",
        "lat":30,
        "long":30   
    },
    {
        "start":"2015-01-03",
        "end":"2015-03-03",
        "res":"vlow",
        "south":-29.5,
        "north":30.5,
        "east":30.5,
        "west":-29.5
    }
]
search_result=arlula_session.gsearch(group_search) # A list of search result objects
```
**Order download**

The Arlula API also provides the option to download an entire order's resources into a specified folder, as below. You may also pass an optional `suppress` parameter to remove all console output.
```python
arlula_session.get_order_resources(
    id=orderId,
    folder="downloads/ordersample",
    suppress=True
)
```
**Search by postcode**

The ArlulaSession `search_postcode` method utilises the [pgeocode](https://pypi.org/project/pgeocode/) API to search by postcode. The method requires a country's [two-letter ISO code](https://www.iban.com/country-codes), and can take either a single postcode or a list of postcodes. The returned object will contain a `location` object, with `postcode`, `lat`, `long` and `name`, and a `data` object, which contains either the search result or the gsearch result (depending on if more than 1 postcode is passed into the function).
An optional `boxsize` parameter may be passed in to create a bounding box around each location - this box is a square, with each edge `boxsize` kms from the postcode's centroid.
```python
# Searches a 10x10km square centred on Paris
res = arlula_session.search_postcode(
    start="2019-01-01",
    res="vlow",
    country="fr",
    postcode="75013",
    boxsize=5
)
print(res.location.name) # prints "Paris"
search_result = res.data

# Searches each of Australia's capital cities
res = arlula_session.search_postcode(
    start="2019-01-01",
    end="2019-03-01",
    res="med",
    country="au",
    postcode=["2000", "2600", "3000", "4000", "5000", "6000", "7000", "0800"],
)
print(res[2].location.name) # prints "Melbourne"
search_result = res[2].data # Melbourne search result
```
