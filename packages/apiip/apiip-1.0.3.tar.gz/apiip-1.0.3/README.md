# IP to Location

Find geolocation data from IP addresses (e.g. city, country, lat/long) using the apiip.net API.

apiip.net provides 5.000 free requests per month. For higher plans, check out the [website](https://apiip.net)

## Installation

You need to get your API key from here: https://apiip.net/get-started and you'll get 5.000 free requests/month

For more details, please visit: [API Documentation](https://apiip.net/documentation)

To install this package type the following (for PyPI):

```sh
pip install apiip
```

## Usage

The package needs to be configured with your account's API key, which is available in the [Apiip.net Dashboard](https://apiip.net/user/dashboard)

```python
from apiip import apiip

api_client = apiip('YOUR_API_KEY')

info = api_client.get_location()

print(info)
```

## HTTPS Encryption

By default, the SSL/TLS is turned off, if you want to enable it just pass the options parameter

#### Example

```python
from apiip import apiip

api_client = apiip('YOUR_API_KEY', {'ssl': True})

info = api_client.get_location()

print(info)
```

## Configuration

Call getLocation method with config object

```python
from apiip import apiip

api_client = apiip('YOUR_API_KEY', {'ssl': True})

info = api_client.getLocation({
    'ip': "67.250.186.196", # '67.250.186.196, 188.79.34.191, 60.138.7.24' - for bulk request
    'output': "xml",
    'fields': "city, countryName, currency.name",
    'languages': "es",
})

print(info)
```

| Option      | Type     | Description                                                                                                | Default      |
| ----------- | -------- | ---------------------------------------------------------------------------------------------------------- | ------------ |
| `ip`        | `string` | _Optional_. Get location about the specify IP or multiple IPs.                                             | Requester IP |
| `output`    | `string` | _Optional_. Specify response format, XML or JSON.                                                          | JSON         |
| `fields`    | `string` | _Optional_. Specify response fields.                                                                       | All fields   |
| `languages` | `string` | _Optional_. Specify response language.                                                                     | EN           |
| `callback`  | `string` | _Optional_. The callback function name ([JSONP Callbacks](https://www.w3schools.com/js/js_json_jsonp.asp)) | -            |

## Example complete response

```python
{
  "ip": "67.250.186.196",
  "continentCode": "NA",
  "continentName": "North America",
  "countryCode": "US",
  "countryName": "United States",
  "countryNameNative": "United States",
  "regionCode":"NY"
  "regionName":"New York"
  "cityGeoNameId": 5128581,
  "city": "New York",
  "postalCode": "10001",
  "latitude": 40.8271,
  "longitude": -73.9359,
  "capital": "Washington D.C.",
  "phoneCode": "1",
  "countryFlagEmoj": "🇺🇸",
  "countryFlagEmojUnicode": "U+1F1FA U+1F1F8",
  "isEu": False,
  "borders": [
    "CAN",
    "MEX"
  ],
  "topLevelDomains": [
    ".us"
  ],
  "languages": {
    "en": {
      "code": "en",
      "name": "English",
      "native": "English"
    }
  },
  "currency": {
    "code": "USD",
    "name": "US Dollar",
    "symbol": "$",
    "number": "840",
    "rates": {
      "EURUSD": 0.99518
    }
  },
  "timeZone": {
    "id": "America/New_York",
    "currentTime": "10/26/2021, 2:54:10 PM",
    "code": "EDT",
    "timeZoneName": "EDT",
    "utcOffset": -14400
  },
   "userAgent": {
    "isMobile": False,
    "isiPod": False,
    "isTablet": False,
    "isDesktop": True,
    "isSmartTV": False,
    "isRaspberry": False,
    "isBot": False,
    "browser": "Chrome",
    "browserVersion": "100.0.4896.127",
    "operatingSystem": "Windows 10.0",
    "platform": "Microsoft Windows",
    "source": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
  },
  "connection": {
    "asn": 12271,
    "isp": "Charter Communications Inc"
  },
  "security": {
    "isProxy": False,
    "isBogon": False,
    "isTorExitNode": False,
    "isCloud": False,
    "isHosting": False,
    "isSpamhaus": False,
    "suggestion": "allow",
    "network": "67.250.176.0/20"
  }
}

```

## More Information

- [API Documentation](https://apiip.net/documentation)
