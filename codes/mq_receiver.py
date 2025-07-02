import sysv_ipc

key = 1234  
mq = sysv_ipc.MessageQueue(key)
message, message_type = mq.receive(type=0)
print(f"Received message (type {message_type}): {message.decode()}")

