import requests, json
def typingoff(ACCESS_TOKEN,sender_id):
    params = {"access_token": ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {
        "id": sender_id
    },
         "sender_action": "typing_off"
    })

    requests.post("https://graph.facebook.com/v3.0/me/messages", params=params, headers=headers, data=data)