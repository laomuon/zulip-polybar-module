import zulip
import time
from sys import stdout

print("!")
stdout.flush()

client = zulip.Client(config_file = "~/zuliprc")

update_time = 1

def run():
    result = client.register(
            event_types = ['message', 'update_message_flags'],
            fetch_event_types = ['message', 'update_message_flags'],
            )

    last_event_id = -1
    queue_id = result["queue_id"]
    assert queue_id is not None

    count = result["unread_msgs"]["count"]

    print(count)
    stdout.flush()
    while True:
        if queue_id is None:
            result = client.register(
                    event_types = ['message', 'update_message_flags'],
                    fetch_event_types = ['message', 'update_message_flags'],
                    )
            queue_id  = result["queue_id"]
        try:
            res = client.get_events(queue_id=queue_id, last_event_id=last_event_id)
        except Exception:
            time.sleep(update_time)
            print("!")
            stdout.flush()
            continue

        if "error" in res["result"]:
            if res.get("code") == "BAD_EVENT_QUEUE_ID":
                queue_id = None
            time.sleep(update_time)
            print("!")
            stdout.flush()
            continue

        for event in res["events"]:
            last_event_id = max(int(event["id"]), last_event_id)
            count = count + callback(event)

        print(count)
        stdout.flush()
        time.sleep(update_time)
        
def callback(event) -> int:
    if event["type"] == "message" and "read" not in event["flags"]:
        return 1

    if event["type"] == "update_message_flags" and event["flag"] == "read":
        if event["op"] == "add":
            return - len(event["messages"])
        elif event["op"] == "remove":
            return len(event["messages"]) 

    return 0

if __name__ == "__main__":
    run()


