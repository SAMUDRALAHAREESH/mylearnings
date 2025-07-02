import can
import time
import signal

running = True

def signal_handler(sig, frame):
    global running
    print("\nStopping CAN transmission")
    running = False

signal.signal(signal.SIGINT, signal_handler)

def setup_can_interface(channel='vcan0'):
    return can.Bus(interface='socketcan', channel=channel, receive_own_messages=True)

def send_can_message(bus, arbitration_id=0x123, data=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88]):
    msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
    try:
        bus.send(msg)
        print(f"Sent:{msg}")
    except can.CanError as e:
        print(f"Failed to send message: {e}")



if __name__ == "__main__":
    bus = setup_can_interface()

    try:
        while running:
            send_can_message(bus)
            time.sleep(0.01)
        
    finally:
        bus.shutdown()
        print("CAN interface shut down.")
        