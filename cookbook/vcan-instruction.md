# Virtual CAN (vCAN) 

1. **Install python3-can**
   ```bash
   sudo apt install python3-can
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. **Run vCAN on the System**
   ```bash
   sudo modprobe vcan
   sudo ip link add dev vcan0 type vcan
   sudo ip link set up vcan0
   ```

4. **Start CAN Transmission**
   ```bash
   python3 virtual_can.py
   ```

5. **CAN Utilities**
   - `cangen`: Generate CAN frames
   - `candump`: Monitor CAN traffic
   - `cansend`: Send a CAN message manually