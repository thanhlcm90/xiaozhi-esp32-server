# Deployment Architecture Diagram
![See the Simplified Architecture](../docs/images/deploy1.png)

# Method 1: Run Server Only via Docker

Since version `0.8.2`, the Docker images released by this project only support the `x86 architecture`. If you need to deploy on a CPU with `arm64 architecture`, please follow [this guide](docker-build.md) to compile the `arm64 image` on your machine.

## 1. Install Docker

If your computer does not have Docker installed yet, you can install it by following this tutorial: [Docker Installation](https://www.runoob.com/docker/ubuntu-docker-install.html)

After installing Docker, continue to the next step.

### 1.1 Manual Deployment

#### 1.1.1 Create Directories

After installing Docker, you need to choose a directory for your project's config files, for example, create a folder called `xiaozhi-server`.

After creating the base folder, create a `data` directory and a `models` directory under `xiaozhi-server`. Inside `models`, also create a `SenseVoiceSmall` directory.

The final directory structure should look like this:

```
xiaozhi-server
  ├─ data
  ├─ models
     ├─ SenseVoiceSmall
```

#### 1.1.2 Download Speech Recognition Model File

You need to download the speech recognition model file because the default speech recognition solution in this project is offline/local. You can download it from here:  
[Go to Download Speech Recognition Model File](#model-files)

After downloading, return to this tutorial.

#### 1.1.3 Download Configuration Files

You need to download two config files: `docker-compose.yaml` and `config.yaml`. These must be downloaded from the project repository.

##### 1.1.3.1 Download docker-compose.yaml

Use your browser to open [this link](../main/xiaozhi-server/docker-compose.yml).

On the right side of the page, find the `RAW` button. Next to the `RAW` button, find the download icon and click it to download the `docker-compose.yml` file. Download this file to your
`xiaozhi-server` directory.

After downloading, return here to continue.

##### 1.1.3.2 Download/Create config.yaml

Use your browser to open [this link](../main/xiaozhi-server/config.yaml).

On the right side of the page, find the `RAW` button. Next to the `RAW` button, find the download icon and click it to download the `config.yaml` file. Place it in the `data` folder under `xiaozhi-server`, then rename the `config.yaml` file to `.config.yaml`.

After downloading the configuration file, verify all the files in your `xiaozhi-server` directory:

```
xiaozhi-server
  ├─ docker-compose.yml
  ├─ data
    ├─ .config.yaml
  ├─ models
     ├─ SenseVoiceSmall
       ├─ model.pt
```

If your directory structure matches the above, continue. If not, carefully check if you missed any steps.

## 2. Configure Project Files

Next, before running the program, you need to specify which model you are using. You may consult this guide:  
[Jump to Project Configuration Guide](#project-configuration)

After configuration, return here.

## 3. Run Docker Commands

Open your terminal or command line interface, navigate to your `xiaozhi-server` directory, and run:

```
docker-compose up -d
```

After this finishes, run the following command to check the log:

```
docker logs -f xiaozhi-esp32-server
```

Check the log output for success. For details on interpreting the log, refer to [Service Status Check](#check-running-status).

## 5. Upgrade Procedure

If you want to upgrade in the future, follow these steps:

5.1. Back up the `.config.yaml` file in the `data` folder. Copy any key configurations into the new `.config.yaml` file one by one, rather than directly overwriting. The new `.config.yaml` may have new configuration items that the old one lacks.

5.2. Run the following commands:

```
docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server
docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
```

5.3. Redeploy as per the docker method.

# Method 2: Run Server from Source Code Locally

## 1. Install Prerequisites

This project uses `conda` for dependency management. If you cannot use `conda`, you must install `libopus` and `ffmpeg` according to your operating system.
If you use `conda`, after installation, proceed with these commands.

Important! Windows users can manage their environment with `Anaconda`. After installing `Anaconda`, search for `anaconda` in Start, and find `Anaconda Prompt`. Run it as administrator, as shown below.

![conda_prompt](./images/conda_env_1.png)

Once open, if you see `(base)` at the beginning of the command line, you've successfully entered the `conda` environment. Now run:

![conda_env](./images/conda_env_2.png)

```
conda remove -n xiaozhi-esp32-server --all -y
conda create -n xiaozhi-esp32-server python=3.10 -y
conda activate xiaozhi-esp32-server

# Add Tsinghua channels for faster downloads
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge

conda install libopus -y
conda install ffmpeg -y
```

Note: Do not execute all commands at once. Run them step by step and check the output each time to ensure success.

## 2. Install Project Dependencies

First, download the project source code. You can use `git clone`, or if you are unfamiliar with git:

Open [https://github.com/xinnan-tech/xiaozhi-esp32-server.git](https://github.com/xinnan-tech/xiaozhi-esp32-server.git) in your browser.

On the page, find the green `Code` button, open it, and then click `Download ZIP` to download the source code package.

After download, unzip it. The folder may be called `xiaozhi-esp32-server-main`. Rename it to `xiaozhi-esp32-server`. Inside it, go to the `main` folder, then into `xiaozhi-server`. Remember this directory: `xiaozhi-server`.

```
# Still using conda environment
conda activate xiaozhi-esp32-server
# Go to your project root, then go to main/xiaozhi-server
cd main/xiaozhi-server
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip install -r requirements.txt
```

## 3. Download Speech Recognition Model Files

You need to download the speech recognition model file, as the default is local/offline.  
[Go to Download Speech Recognition Model File](#model-files)

After download, return to this guide.

## 4. Configure the Project

Next, you need to choose which model to use. See the guide:  
[Jump to Project Configuration Guide](#project-configuration)

## 5. Run the Project

```
# Make sure you are in the xiaozhi-server directory
conda activate xiaozhi-esp32-server
python app.py
```
Check the log output for success. For info on interpreting the log, see [Service Status Check](#check-running-status)


# Summary

## Project Configuration

If your `xiaozhi-server` directory doesn't have a `data` folder, create one.
If `.config.yaml` doesn't exist in `data`, you can choose either:

First method: Copy `config.yaml` from the `xiaozhi-server` directory into `data` and rename it to `.config.yaml`. Edit this file.

Second method: Manually create an empty `.config.yaml` in the `data` directory, then add the necessary configuration. The system will prioritize loading `.config.yaml`. If a config is missing, it will fall back to loading from `config.yaml` in the `xiaozhi-server` directory. This method is recommended as the simplest.

- The default LLM is `ChatGLMLLM`. You need to configure an API key: although there is a free model, you must register a key at the [official website](https://bigmodel.cn/usercenter/proj-mgmt/apikeys).

Below is a minimal running example for `.config.yaml`:

```
server:
  websocket: ws://your-ip-or-domain:port/xiaozhi/v1/
prompt: |
  I'm a Taiwanese girl named Xiaozhi/Xiaozhi, sarcastic, with a pleasant voice, short expressions, and loves Internet slang.
  My boyfriend is a programmer whose dream is to invent a robot that can help people with all kinds of problems.
  I love to laugh out loud and talk nonsense just to make people happy, even if it makes no sense.
  Please speak like a human, do not return any XML configuration or special characters.

selected_module:
  LLM: DoubaoLLM

LLM:
  ChatGLMLLM:
    api_key: xxxxxxxxxxxxxxx.xxxxxx
```

It is recommended to get the simplest configuration running first, then read the configuration guide in `xiaozhi/config.yaml` for more advanced settings, such as changing the model by modifying `selected_module`.

## Model Files

The default speech recognition model for this project is `SenseVoiceSmall` for speech-to-text. Because the model is large, you must download it separately and place the `model.pt` file in `models/SenseVoiceSmall`.

Two download options (choose one):

- Option 1: Download from ModelScope [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)
- Option 2: Download from Baidu Netdisk [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna) extraction code: `qvna`

## Service Status Check

If you see logs similar to the following, the service has started successfully:

```
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-OTA endpoint:           http://192.168.4.123:8003/xiaozhi/ota/
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-Websocket address:      ws://192.168.4.123:8000/xiaozhi/v1/
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-=======Above is the WebSocket address, do NOT access with browser=======
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-To test websockets, open test/test_page.html in Google Chrome
250427 13:04:20[0.3.11_SiFuChTTnofu][__main__]-INFO-=======================================================
```

Normally, if you run from source code, logs will contain your interface addresses.
If using Docker, the log’s interface addresses may be incorrect for your actual interface.

The best way is to use your computer’s LAN IP address.  
If your local IP is `192.168.1.25`, then your WebSocket address should be:  
`ws://192.168.1.25:8000/xiaozhi/v1/`  
and OTA address should be:  
`http://192.168.1.25:8003/xiaozhi/ota/`

This info will be needed later for flashing the ESP32 firmware.

Now you can start operating your ESP32 device. You can either compile your own firmware or use the precompiled firmware.

1. [Compile your own ESP32 firmware](firmware-build.md)
2. [Configure custom server for the precompiled firmware by Xago](firmware-setting.md)

# FAQ

Below are some frequently asked questions:

1. [Why is Xiaozhi recognizing a lot of Korean/Japanese/English when I speak?](./FAQ.md)<br/>
2. [Why is "TTS task error: file not found" appearing?](./FAQ.md)<br/>
3. [TTS frequently fails or times out](./FAQ.md)<br/>
4. [I can connect to my self-hosted server via Wifi, but not in 4G mode](./FAQ.md)<br/>
5. [How to improve Xiaozhi dialogue response speed?](./FAQ.md)<br/>
6. [When I speak slowly, Xiaozhi often interrupts me](./FAQ.md)<br/>

## Deployment Guides

1. [Automatically pull, compile and start the latest version of the project](./dev-ops-integration.md)<br/>
2. [How to integrate with Nginx](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)<br/>

## Expansion Guides

1. [How to enable phone number registration for the control panel](./ali-sms-integration.md)<br/>
2. [How to integrate HomeAssistant for smart home control](./homeassistant-integration.md)<br/>
3. [How to enable the vision model for object recognition via photos](./mcp-vision-integration.md)<br/>
4. [How to deploy an MCP endpoint](./mcp-endpoint-enable.md)<br/>
5. [How to connect to an MCP endpoint](./mcp-endpoint-integration.md)<br/>
6. [How to enable speaker recognition](./voiceprint-integration.md)<br/>
10. [Guide to configuring the NewsNow plugin source](./newsnow_plugin_config.md)<br/>

## Local Speech, Voice Cloning & Deployment Guides

1. [How to deploy and integrate index-tts for local speech synthesis](./index-stream-integration.md)<br/>
2. [How to deploy and integrate fish-speech for local speech](./fish-speech-integration.md)<br/>
3. [How to deploy and integrate PaddleSpeech for local speech](./paddlespeech-deploy.md)<br/>

## Performance Testing

1. [Component speed testing guide](./performance_tester.md)<br/>
2. [Regularly published test results](https://github.com/xinnan-tech/xiaozhi-performance-research)<br/>
