# ESP32 Firmware Compilation

## Step 1: Prepare Your OTA Address

If you are using version 0.3.12 of this project, regardless of whether you did a Simple Server Deployment or a Full Module Deployment, you will have an OTA address.

Because the OTA address configuration differs between Simple Server and Full Module deployments, please follow the method that matches your setup below:

### If You Use Simple Server Deployment

At this point, open your OTA address in a browser. For example, my OTA address is:
```
http://192.168.1.25:8003/xiaozhi/ota/
```
If you see "OTA interface is running normally, the websocket address for devices is: ws://xxx:8000/xiaozhi/v1/", that's correct.

You can use the project's built-in `test_page.html` to test if the output websocket address from the OTA page is accessible.

If you cannot access it, you need to modify the `server.websocket` entry in your `.config.yaml` file. Restart the server and test again using `test_page.html` until connectivity is confirmed.

Once successful, proceed to Step 2.

### If You Use Full Module Deployment

Now, visit your OTA address in the browser. For example, my OTA address is:
```
http://192.168.1.25:8002/xiaozhi/ota/
```

If it shows "OTA interface is running normally, websocket cluster count: X", proceed to Step 2.

If it shows "OTA interface is not running normally", it is likely you haven't set up the `Websocket` address in the Control Panel:

- 1. Log in to the Control Panel as Super Administrator
- 2. Click on "Parameter Management" in the top menu
- 3. In the list, find the `server.websocket` option and enter your Websocket address, for example:

```
ws://192.168.1.25:8000/xiaozhi/v1/
```

After configuring, refresh your OTA address in the browser to check if it's working correctly. If it's still abnormal, double-check whether the Websocket service has started and is configured properly.

## Step 2: Setup the Environment

First, configure your development environment using this tutorial: [How to Set Up ESP IDF 5.3.2 Development Environment and Build Xiaozhi on Windows](https://icnynnzcwou8.feishu.cn/wiki/JEYDwTTALi5s2zkGlFGcDiRknXf)

## Step 3: Open the Configuration File

With the environment set up, download the Xiaoge xiaozhi-esp32 project source code,

Download the [xiaozhi-esp32 project source code here](https://github.com/78/xiaozhi-esp32).

After downloading, open the `xiaozhi-esp32/main/Kconfig.projbuild` file.

## Step 4: Modify the OTA Address

Find the line with the `OTA_URL` `default` value, and change `https://api.tenclass.net/xiaozhi/ota/` to your own address. For example, if your OTA address is `http://192.168.1.25:8002/xiaozhi/ota/`, update it accordingly.

Before change:
```
config OTA_URL
    string "Default OTA URL"
    default "https://api.tenclass.net/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```
After change:
```
config OTA_URL
    string "Default OTA URL"
    default "http://192.168.1.25:8002/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```

## Step 4: Set Compilation Parameters

Configure compilation parameters:

```
# In terminal, go to the xiaozhi-esp32 root directory
cd xiaozhi-esp32
# For example, I use the esp32s3 board, so I set the target to esp32s3. If yours is a different model, replace accordingly.
idf.py set-target esp32s3
# Enter menu configuration
idf.py menuconfig
```

After entering the menuconfig, go to `Xiaozhi Assistant`, set the `BOARD_TYPE` to your board's model.
Save and exit to return to the terminal.

## Step 5: Build the Firmware

```
idf.py build
```

## Step 6: Package the Binary Firmware

```
cd scripts
python release.py
```

After running the above commands, a `merged-binary.bin` firmware file will be generated in the `build` directory under the project root. 

This `merged-binary.bin` file is what you need to flash to your hardware device.

Note: If you see a "zip" related error after the second command, you can ignore it as long as the `build` directory has a generated `merged-binary.bin` file, it won't affect your workflow—just continue.

## Step 7: Flash the Firmware

Connect the ESP32 device to your computer, and use the Chrome browser to open:

```
https://espressif.github.io/esp-launchpad/
```

See this tutorial: [Flash Tool / Web-based Firmware Flashing (no IDF environment)](https://ccnphfhqs21z.feishu.cn/wiki/Zpz4wXBtdimBrLk25WdcXzxcnNS).

Scroll to "Method 2: ESP-Launchpad Browser Web Flash", and start from "3. Burn firmware/download to development board", then follow the instructions.

After successful flashing and connecting to the network, wake Xiaozhi using the wake word and check the server console output for status messages.

## Frequently Asked Questions

Below are some frequently asked questions for your reference:

[1. Why does Xiaozhi recognize lots of Korean, Japanese, or English when I speak?](./FAQ.md)

[2. Why does "TTS task error: file not found" occur?](./FAQ.md)

[3. TTS fails frequently or times out often](./FAQ.md)

[4. The device can connect to the local server over WiFi, but not over 4G](./FAQ.md)

[5. How to improve Xiaozhi's response speed?](./FAQ.md)

[6. I'm speaking slowly, but Xiaozhi keeps interrupting](./FAQ.md)

[7. I want to use Xiaozhi to control lights, AC, remotes, etc.](./FAQ.md)
