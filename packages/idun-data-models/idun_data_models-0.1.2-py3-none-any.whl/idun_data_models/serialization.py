"""
To make API requests, the dataclasses need to be serialized to JSON.
Pydantic supports more extensive JSON serialization than the basic `json` module, but dataclasses need to use the JSON encoder explicitly.
We provide a convenience method that uses the pydantic encoder:

```python
message= Message(recordingID="1", deviceID="1", deviceTimestamp=datetime.now())
requests.post(IDUN_API..., json= json_pydantic(message))
```
"""

import json
from pydantic.json import pydantic_encoder

def json_pydantic(dataclass)-> str:
    return json.dumps(dataclass, default=pydantic_encoder)