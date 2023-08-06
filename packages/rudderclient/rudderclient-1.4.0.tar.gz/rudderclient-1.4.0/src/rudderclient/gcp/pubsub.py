from google.cloud import pubsub_v1


def write_message(project_id, topic_id, message_str, status, joinerId):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    # Data must be a bytestring
    message = message_str.encode("utf-8")

    future = publisher.publish(
        topic_path, message, status=str(status), joinerId=str(joinerId)
    )

    result = future.result()

    return result
