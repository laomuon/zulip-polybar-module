#/usr/bin/env python3.10
import zulip
import time
from sys import stdout

client = zulip.Client(config_file = "~/zuliprc")


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
            time.sleep(1)
            continue
        if "error" in res["result"]:
            if res["result"] == "http-error":
                print("HTTP error event")
            else:
                if res.get("code") == "BAD_EVENT_QUEUE_ID":
                    queue_id = None
            time.sleep(1)
            continue

        for event in res["events"]:
            last_event_id = max(int(event["id"]), last_event_id)
            callback(event, count)

        print(count)
        stdout.flush()
        time.sleep(1)
        
def callback(event, count):
    if event["type"] == "message" and len(event["flags"]) == 0:
        count = count + 1
        return

    if event["type"] == "update_message_flags" and event["flag"] == "read":
        if event["op"] == "add":
            count = count - 1
        elif event["op"] == "remove":
            count = count + 1

if __name__ == "__main__":
    run()


