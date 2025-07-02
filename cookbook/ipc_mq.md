# IPC

This guide briefly explains **Named Pipes (FIFO)** and **Message Queues** for inter-process communication (IPC).

## 1. MKFIFO

Named pipes enable process communication via a special file.

### 1.1 Create a Pipe
Create a pipe using `mkfifo`:

```bash
mkfifo ~/work/ipc
```

- Check with `ls -l` (look for `p` in permissions, e.g., `prw-r--r--`).

### 1.2 Write to the Pipe
Send data to the pipe:

```bash
echo "Hello from Hareesh" > ~/work/ipc
```

### 1.3 Read from the Pipe
Read the pipe's contents:

```bash
cat ~/work/ipc
```

## 2. Message Queues

Message queues allow processes to exchange messages using C system calls.

### 2.1 Key System Calls
1. `msgget(key, flags)`: Create/access a message queue, returns queue ID.
2. `msgsnd(msgid, msg_ptr, msg_size, flags)`: Send a message to the queue.
3. `msgrcv(msgid, msg_ptr, msg_size, msg_type, flags)`: Receive a message.
4. `msgctl(msgid, command, buf)`: Manage queue (e.g., delete).


### 2.2 Program Breakdown
- **Key**: `ftok` creates a unique key.
- **Queue**: `msgget` sets up the queue.
- **Fork**: Splits into sender (parent) and receiver (child).
- **Send/Receive**: `msgsnd` sends, `msgrcv` receives.
- **Cleanup**: `msgctl` deletes the queue.

## 3. Compile & Run
```
python3 mq_sender.py
python3 mq_receiver.py
```

**Output**:
```
Sent: Hello from Hareesh
Received: Hello from Hareesh
```