# Deployment Architecture Diagram
![Reference - Full Module Installation Architecture](../docs/images/deploy2.png)

# Method 1: Full Module Deployment via Docker

Since version `0.8.2`, the official Docker images only support `x86 architecture`. If you need to deploy on a CPU with `arm64 architecture`, refer to [this tutorial](docker-build.md) to build the `arm64` image locally.

## 1. Install Docker

If you don't have Docker installed yet, you can follow this tutorial: [Install Docker](https://www.runoob.com/docker/ubuntu-docker-install.html)

There are two ways to deploy all modules with Docker: you can use the [one-click script](./Deployment_all.md#11-懒人脚本) (by [@VanillaNahida](https://github.com/VanillaNahida)), which will download all required files and configs for you, or you can opt for the [manual deployment](./Deployment_all.md#12-手动部署) to set up everything from scratch.

### 1.1 One-Click Script

For a quick setup, refer to the [video tutorial](https://www.bilibili.com/video/BV17bbvzHExd/), or follow the instructions below:

> [!NOTE]  
> Currently, only supports one-click deployment on Ubuntu server. Other operating systems may have issues and are not tested.

Use an SSH tool to connect to your server, and execute the following script as root:
```bash
sudo bash -c "$(wget -qO- https://ghfast.top/https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/main/docker-setup.sh)"
```

This script will automatically:

> 1. Install Docker
> 2. Configure Docker image sources
> 3. Download/Pull images
> 4. Download the speech recognition model
> 5. Guide you to configure the server

After finishing the simple configuration, please refer to [4. Run the Program](#4-运行程序) and [5. Restart xiaozhi-esp32-server](#5重启xiaozhi-esp32-server) and carry out the three most important configurations to start using the system.

### 1.2 Manual Deployment

#### 1.2.1 Create Directory Structure

After installing Docker, create a directory for the project, e.g., `xiaozhi-server`.

Within this directory, create a `data` folder and a `models` folder. Inside `models`, create a subfolder called `SenseVoiceSmall`.

Final directory structure should look like:

```
xiaozhi-server
  ├─ data
  ├─ models
     ├─ SenseVoiceSmall
```

#### 1.2.2 Download Speech Recognition Model

The project uses the `SenseVoiceSmall` model for speech-to-text by default. As the model is large, you need to download it separately and place the `model.pt` file in the `models/SenseVoiceSmall` directory.

- Option 1: Alibaba ModelScope [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)
- Option 2: Baidu Netdisk [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna) extraction code: `qvna`

#### 1.2.3 Download Configuration Files

You need to download two configuration files: `docker-compose_all.yaml` and `config_from_api.yaml` from the project repository.

##### 1.2.3.1 Download docker-compose_all.yaml

Open [this link](../main/xiaozhi-server/docker-compose_all.yml) in your browser.

On the right side, find the `RAW` button. Next to it, click the download icon to download `docker-compose_all.yml`. Save it in your `xiaozhi-server` directory.

Or run this command directly:

```
wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/docker-compose_all.yml
```

##### 1.2.3.2 Download config_from_api.yaml

Open [this link](../main/xiaozhi-server/config_from_api.yaml) in your browser.

Again, click the download icon next to the `RAW` button to download `config_from_api.yaml`. Save it in the `data` subfolder of your `xiaozhi-server` directory and then rename it to `.config.yaml`.

Alternatively, run:

```
wget https://raw.githubusercontent.com/xinnan-tech/xiaozhi-esp32-server/refs/heads/main/main/xiaozhi-server/config_from_api.yaml
```

After downloading the configuration files, your directory structure should be:

```
xiaozhi-server
  ├─ docker-compose_all.yml
  ├─ data
    ├─ .config.yaml
  ├─ models
     ├─ SenseVoiceSmall
       ├─ model.pt
```

If your directory structure matches the example above, you can continue. If not, please check if you missed any steps.

## 2. Backup Data

If you have previously used Zhikonsole and your keys are stored there, back up your important data first! Upgrading may overwrite your old data.

## 3. Remove Old Images and Containers

Open your terminal and navigate to your `xiaozhi-server` directory. For cleanup, execute:

```
docker compose -f docker-compose_all.yml down

docker stop xiaozhi-esp32-server
docker rm xiaozhi-esp32-server

docker stop xiaozhi-esp32-server-web
docker rm xiaozhi-esp32-server-web

docker stop xiaozhi-esp32-server-db
docker rm xiaozhi-esp32-server-db

docker stop xiaozhi-esp32-server-redis
docker rm xiaozhi-esp32-server-redis

docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest
docker rmi ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:web_latest
```

## 4. Run the Program

Start the containers:
```
docker compose -f docker-compose_all.yml up -d
```

Check web logs:
```
docker logs -f xiaozhi-esp32-server-web
```

If you see log output like:

```
2025-xx-xx 22:11:12.445 [main] INFO  c.a.d.s.b.a.DruidDataSourceAutoConfigure - Init DruidDataSource
2025-xx-xx 21:28:53.873 [main] INFO  xiaozhi.AdminApplication - Started AdminApplication in 16.057 seconds (process running for 17.941)
http://localhost:8002/xiaozhi/doc.html
```

then the management console has started successfully.

You can now access the management console at http://127.0.0.1:8002 to register the first user. The first user is the super administrator. Other users are normal users. Regular users can only bind devices and configure agents. Super admins can manage models, users, system parameters, etc.

Next, you need to do three important things:

### Task 1

After logging into the management console with the super administrator account, go to the "Parameter Management" menu and find the row with `server.secret` as the parameter code. Copy the parameter value.

`server.secret` is required to let your Server connect with the manager-api. Each new deployment of the manager module generates a new random key.

After copying the value, open the `.config.yaml` file in the `data` directory of `xiaozhi-server`. It should look like:

```
manager-api:
  url:  http://127.0.0.1:8002/xiaozhi
  secret: your_server.secret_value
```

1. Paste the copied `server.secret` into the `secret` field.

2. Since you are deploying with Docker, change the `url` to: `http://xiaozhi-esp32-server-web:8002/xiaozhi`

The expected result:
```
manager-api:
  url: http://xiaozhi-esp32-server-web:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

Save the file and move to the next task.

### Task 2

With the super administrator account on the management console, go to "Model Configuration" in the top menu, click "Large Language Model" on the left, find the first entry "Zhipu AI", click "Edit", and fill your ZhipuAI API key in the "API Key" box. Click save.

## 5. Restart xiaozhi-esp32-server

In the terminal, run:
```
docker restart xiaozhi-esp32-server
docker logs -f xiaozhi-esp32-server
```

If you see logs like:

```
25-02-23 12:01:09[core.websocket_server] - INFO - Websocket address: ws://xxx.xx.xx.xx:8000/xiaozhi/v1/
25-02-23 12:01:09[core.websocket_server] - INFO - =======The address above is for websocket protocol, do not access it with a browser=======
25-02-23 12:01:09[core.websocket_server] - INFO - To test websocket, open test/test_page.html with Chrome
25-02-23 12:01:09[core.websocket_server] - INFO - =======================================================
```

it means the server is running.

Since this is a full module deployment, you need to write two important interface URLs into your ESP32 device:

OTA interface:
```
http://your_host_lan_ip:8002/xiaozhi/ota/
```

Websocket interface:
```
ws://your_host_ip:8000/xiaozhi/v1/
```

### Task 3

With the super administrator account, go to "Parameter Management" in the management console, find the parameter code `server.websocket` and set it to your Websocket interface.

Also, find the parameter code `server.ota` and set it to your OTA interface.

You can now start working with your ESP32 device. You can [compile your own ESP32 firmware](firmware-build.md), or [set up a custom server with the pre-compiled firmware version 1.6.1 or later](firmware-setting.md).

---

# Method 2: Run All Modules from Source

## 1. Install MySQL Database

If MySQL is already installed, directly create a database named `xiaozhi_esp32_server`:

```sql
CREATE DATABASE xiaozhi_esp32_server CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

If not, use Docker to run MySQL:

```
docker run --name xiaozhi-esp32-server-db -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 -e MYSQL_DATABASE=xiaozhi_esp32_server -e MYSQL_INITDB_ARGS="--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci" -e TZ=Asia/Shanghai -d mysql:latest
```

## 2. Install Redis

If Redis is not yet installed, you can launch it with Docker:

```
docker run --name xiaozhi-esp32-server-redis -d -p 6379:6379 redis
```

## 3. Run the manager-api Program

3.1 Install JDK 21 and set JAVA_HOME

3.2 Install Maven and set M2_HOME

3.3 Use VSCode and Java plugins

3.4 Load the manager-api module in VSCode

Set the DB config in `src/main/resources/application-dev.yml`:

```
spring:
  datasource:
    username: root
    password: 123456
```

Set Redis config in the same file:
```
spring:
  data:
    redis:
      host: localhost
      port: 6379
      password:
      database: 0
```

3.5 Start the Main Program

This is a SpringBoot project. Open `Application.java` and run the `Main` method.

```
Source path:
src/main/java/xiaozhi/AdminApplication.java
```

When you see logs like below, your manager-api is successfully running:

```
2025-xx-xx 22:11:12.445 [main] INFO  c.a.d.s.b.a.DruidDataSourceAutoConfigure - Init DruidDataSource
2025-xx-xx 21:28:53.873 [main] INFO  xiaozhi.AdminApplication - Started AdminApplication in 16.057 seconds (process running for 17.941)
http://localhost:8002/xiaozhi/doc.html
```

## 4. Run the manager-web Program

4.1 Install nodejs

4.2 Use VSCode to open the manager-web module

In the terminal, go to the manager-web directory:

```
npm install
```
Then start:
```
npm run serve
```

If your manager-api is not at `http://localhost:8002`, edit the path in `main/manager-web/.env.development`.

After successful startup, open http://127.0.0.1:8001 in your browser to register the first user (super admin). Other users will be regular users; super admins can manage models, users, and parameters.

> IMPORTANT: Once registered, log in as super admin, go to "Model Configuration", click "Large Language Model" on the left, find the first entry "Zhipu AI", click "Edit", and paste your ZhipuAI API key in the "API Key" box. Save your changes.

## 5. Install Python Environment

This project uses `conda` for environment management. If you cannot use `conda`, you must install `libopus` and `ffmpeg` in your system.

Windows users: Install Anaconda. After installation, search for "Anaconda Prompt", right-click and run as administrator. See image below:

![conda_prompt](./images/conda_env_1.png)

If you see `(base)` at the command line, you're in the conda environment.

![conda_env](./images/conda_env_2.png)

Commands to run (step-by-step):

```
conda remove -n xiaozhi-esp32-server --all -y
conda create -n xiaozhi-esp32-server python=3.10 -y
conda activate xiaozhi-esp32-server

# Add Tsinghua university channels (for faster downloads in China)
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge

conda install libopus -y
conda install ffmpeg -y
```

> NOTE: Do not run all commands at once. Execute each step and verify successful output before proceeding.

## 6. Install Project Dependencies

First, download the project source code. You can use `git clone`, or simply go to `https://github.com/xinnan-tech/xiaozhi-esp32-server.git` in your browser. Click the green `Code` button, then click `Download ZIP`.

After downloading and extracting, rename the directory to `xiaozhi-esp32-server`, enter `main`, then enter `xiaozhi-server`. Remember this path.

```
# Continue in conda environment
conda activate xiaozhi-esp32-server
# Go to your project's root and then main/xiaozhi-server
cd main/xiaozhi-server
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip install -r requirements.txt
```

### 7. Download Speech Recognition Model

As above, download the `SenseVoiceSmall` model and place `model.pt` inside `models/SenseVoiceSmall`:

- Option 1: Alibaba ModelScope [SenseVoiceSmall](https://modelscope.cn/models/iic/SenseVoiceSmall/resolve/master/model.pt)
- Option 2: Baidu Netdisk [SenseVoiceSmall](https://pan.baidu.com/share/init?surl=QlgM58FHhYv1tFnUT_A8Sg&pwd=qvna) password: `qvna`

## 8. Configure Project Files

Log in to Zhikonsole as super admin and go to "Parameter Management". Find the first entry with parameter code `server.secret` and copy its value.

If your `xiaozhi-server` directory does not contain a `data` folder, create it. If there's no `.config.yaml` inside `data`, copy `config_from_api.yaml` from the project root into `data` and rename it `.config.yaml`.

Update `.config.yaml` to:

```
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: your_server.secret_value
```

Paste your copied `server.secret` value into `secret`.

Example:
```
manager-api:
  url: http://127.0.0.1:8002/xiaozhi
  secret: 12345678-xxxx-xxxx-xxxx-123456789000
```

## 9. Run the Project

```
# Make sure you are in the xiaozhi-server directory
conda activate xiaozhi-esp32-server
python app.py
```

If you see server logs like:

```
25-02-23 12:01:09[core.websocket_server] - INFO - Server is running at ws://xxx.xx.xx.xx:8000/xiaozhi/v1/
25-02-23 12:01:09[core.websocket_server] - INFO - =======The address above is for websocket protocol, do not access it with a browser=======
25-02-23 12:01:09[core.websocket_server] - INFO - To test websocket, open test/test_page.html with Chrome
25-02-23 12:01:09[core.websocket_server] - INFO - =======================================================
```

the server has started successfully.

Since this is a full module deployment, you have two interface URLs:

OTA interface:
```
http://your_lan_ip:8002/xiaozhi/ota/
```

Websocket interface:
```
ws://your_lan_ip:8000/xiaozhi/v1/
```

Make sure to input these URLs in your Zhikonsole "Parameter Management" (`server.websocket` and `server.ota`).

You can now work with your ESP32 device using either route:

1. [Compile your own ESP32 firmware](firmware-build.md)
2. [Configure pre-built firmware (v1.6.1 or later) to use your custom server](firmware-setting.md)

# FAQ

Some common questions:

1. [Why does XiaoZhi recognize a lot of Korean, Japanese, or English when I speak?](./FAQ.md)<br/>
2. [Why do I get "TTS task failed - file not found"?](./FAQ.md)<br/>
3. [TTS fails or times out frequently](./FAQ.md)<br/>
4. [WiFi can connect to my self-built server, but 4G cannot](./FAQ.md)<br/>
5. [How to improve XiaoZhi's response speed?](./FAQ.md)<br/>
6. [XiaoZhi interrupts me when I pause during speech](./FAQ.md)<br/>

## Deployment Tutorials

1. [How to automatically pull the latest code, build, and start](./dev-ops-integration.md)<br/>
2. [Nginx integration guide](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791)<br/>

## Expansion Tutorials

1. [Enable mobile phone registration for Zhikonsole](./ali-sms-integration.md)<br/>
2. [Integrate with HomeAssistant for smart home control](./homeassistant-integration.md)<br/>
3. [Enable vision model for object recognition](./mcp-vision-integration.md)<br/>
4. [Deploy MCP endpoint](./mcp-endpoint-enable.md)<br/>
5. [Integrate MCP endpoint](./mcp-endpoint-integration.md)<br/>
6. [Enable voiceprint recognition](./voiceprint-integration.md)<br/>
7. [News plugin configuration guide](./newsnow_plugin_config.md)<br/>
8. [Weather plugin usage guide](./weather-integration.md)<br/>

## Voice Cloning & Local Speech Tutorials

1. [How to integrate index-tts for local speech](./index-stream-integration.md)<br/>
2. [How to integrate fish-speech for local speech](./fish-speech-integration.md)<br/>
3. [How to integrate PaddleSpeech for local speech](./paddlespeech-deploy.md)<br/>

## Performance Testing

1. [Component speed testing guide](./performance_tester.md)<br/>
2. [Periodic public test results](https://github.com/xinnan-tech/xiaozhi-performance-research)<br/>
