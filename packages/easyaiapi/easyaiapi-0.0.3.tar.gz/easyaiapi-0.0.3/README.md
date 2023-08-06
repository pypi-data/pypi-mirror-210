# FastAi API

```python
from fastaiapi import background_thread, WssClient, WssServer
from fastaiapi.utils import read_base64_image

TARGET_SOCKET_URL = "[ENTER TARGET WS URL]"

client = WssClient()

@client.from_video_source(TARGET_SOCKET_URL, 0)
def on_data_received(data):
    print(data)

```

