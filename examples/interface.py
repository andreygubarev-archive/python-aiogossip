peers = []

sender = peers[0]
receiver = peers[1]
receiver.connect([sender])

message = {"metadata": {}}
response = sender.publish("request:{uuid}", message, peers=[receiver])
async for r in response:
    print(r)
