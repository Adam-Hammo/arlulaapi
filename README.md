# **Arlula API Python Package**

## Installation
`pip install arlulaapi`
## Initiation
Instantiate an ArlulaSession object using your API credentials as below. This will validate your credentials and store them for the remainder of the session.

```python
import arlulaapi
arlula_session = arlulaapi.ArlulaSession(key, secret)
```
## API Endpoints
This package contains methods for each of the supported API endpoints. Each method returns a JSON object as prescribed in the API documentation. An example of each method is below:
```python
search_result = arlula_session.search(
    start="2014-01-01",
    res="vlow",
    lat=40.84,
    long=60.15
)

order = arlula_session.order(
    id=orderId,
    eula="",
    seats=1,
    webhooks=[...],
    emails=[...]
)

## Downloads the resource to the specified filepath
arlula_session.get_resource(
    id=resourceId,
    filepath="downloads/thumbnail.jpg"
)

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
        "lat":-30,
        "long":-30
    }
]
search_result=arlula_session.gsearch(group_search)
```
**Order download**
The Arlula API also provides the option to download an entire order's resources into a specified folder, as below. You may also pass an optional suppress parameter to remove all console output.
```python
arlula_session.get_order_resources(
    id=orderId,
    folder="downloads/ordersample",
    suppress=True
)