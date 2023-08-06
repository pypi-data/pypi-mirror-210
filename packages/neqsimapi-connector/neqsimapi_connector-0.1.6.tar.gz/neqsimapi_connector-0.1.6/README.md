# NeqSimAPI-connector
A python package to simplify calling NeqSimAPI for end-users handling authentication.  

See https://neqsimapi.app.radix.equinor.com/docs for available endpoints.

# Usage
See [https://github.com/equinor/neqsimapi-connector/blob/main/example/demo.py](/example/demo.py) for a simple demo that connects and gets data from NeqSimAPI.

A short snippet is seen below
```
from neqsimapi_connector.Connector import Connector as neqsim_api_connector

data = {"compression_factor": 10,
        "refrigerant": {
            "fluid": "propane",
            "fraction": 1,
            "unit_temperature": "C",
            "unit_pressure": "bara",
            "unit_flowrate": "kg/hr",
            "temperature": 30,
            "pressure": 15,
            "flowrate": 1000}
        }


c = neqsim_api_connector()
res = c.post("DEMO/demo-process/simulate", data=data)
print(res)
```

# Install using pip
Usage of NeqSimAPI is limited to equinor users, but the package is available on pip.  
```python -m pip neqsimapi_connector```