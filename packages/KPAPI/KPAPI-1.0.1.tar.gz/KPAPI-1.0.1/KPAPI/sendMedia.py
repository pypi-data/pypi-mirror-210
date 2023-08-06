import requests, json
def sendMedia(ACCESS_TOKEN, sender_id, type, url):
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {
            "id": sender_id
        },
        "message": {
            "attachment": {
                "type": type,
                "payload": {
                    "is_reusable": True,
                    "url": url
                }
            }
        }
    })

    requests.post("https://graph.facebook.com/v3.0/me/messages",
                            params=params,
                            headers=headers,
                            data=data)