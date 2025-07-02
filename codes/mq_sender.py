import sysv_ipc

key = 1234 
mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREAT)
message = "Hello from sender!(Hareesh)"
mq.send(message.encode(), type=1)
print("Message sent to the queue.")


