# KPAPI

Optimize the use of Facebook API

## Install
```shell
pip install KPAPI
```

### Usage

Send message to users:
```python
import KPAPI
KPAPI.sendMessage(Access_token,sender_ID, "text")

```
Send media:
```python
import KPAPI
KPAPI.sendMedia(Access_token,sender_id, "audio/video/image",url_media)
```
Seen action:
```python
import KPAPI
KPAPI.seen(Access_token, sender_id)
```
Typing On action:
```python
import KPAPI
KPAPI.typingon(access_token,sender_id)
```
Typing Off action:
```python
import KPAPI
KPAPI.typingoff(access_token,sender_id)
```
