# Automated Upgrade Method for Full-Source Deployment

This tutorial is designed to help enthusiasts who deploy the full source code of the project to automate the process of pulling source code, compiling, and launching services using scripts, thus achieving the most efficient upgrade workflow.

Our testing platform `https://2662r3426b.vicp.fun` has been using this method since it went live, with great results.

You can also refer to a detailed video tutorial on Bilibili by `Bile Labs`: [《Open-source Xiaozhi Server Automatic Update & Latest MCP Access Point Configuration Guide》](https://www.bilibili.com/video/BV15H37zHE7Q)

# Prerequisites

- Your computer/server is running a Linux operating system
- You have already completed a full manual deployment and have the project running
- You want to follow the latest features, but find manual deployments tedious and are looking for an automated update method

The second condition is essential because this tutorial assumes you already have all the necessary resources (such as JDK, Node.js, Conda environments, etc.) from completing the manual process. If not, some instructions might be unclear.

# Tutorial Results

- Solve the problem of not being able to pull the latest project source code in mainland China
- Automatically pull and build frontend code
- Automatically pull and build Java code, kill the process occupying port 8002, and restart on 8002
- Automatically pull Python code, kill the process occupying port 8000, and restart on 8000

# Step 1: Choose Your Project Directory

For example, you can follow my structure, creating a new empty directory. To avoid mistakes, you can do exactly as shown:
```
/home/system/xiaozhi
```

# Step 2: Clone the Project

Run the following commands to pull the source code. These use a mirror suitable for servers and computers in mainland China (no VPN required):

```
cd /home/system/xiaozhi
git clone https://ghproxy.net/https://github.com/xinnan-tech/xiaozhi-esp32-server.git
```

After execution, you'll see a new folder called `xiaozhi-esp32-server` in your project directory—this is the project source code.

# Step 3: Copy Essential Files

If you've completed the whole manual setup previously, you'll be familiar with the speech model file `xiaozhi-server/models/SenseVoiceSmall/model.pt` and your private config file `xiaozhi-server/data/.config.yaml`.

Now you need to copy the `model.pt` file into the new directory:
```
# Create required directories
mkdir -p /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/

cp <full-path-to-your-original .config.yaml file> /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/data/.config.yaml
cp <full-path-to-your-original model.pt file> /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/models/SenseVoiceSmall/model.pt
```

# Step 4: Create Three Auto-Compile Scripts

## 4.1 Automatically Compile the manager-web Module

In `/home/system/xiaozhi/`, create a file called `update_8001.sh` with the following content:

```
cd /home/system/xiaozhi/xiaozhi-esp32-server
git fetch --all
git reset --hard
git pull origin main

cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web
npm install
npm run build
rm -rf /home/system/xiaozhi/manager-web
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-web/dist /home/system/xiaozhi/manager-web
```

Give it execution permission:
```
chmod 777 update_8001.sh
```
Continue to the next step.

## 4.2 Automatically Compile and Run the manager-api Module

In `/home/system/xiaozhi/`, create a file called `update_8002.sh` with the following content:

```
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main

cd /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api
rm -rf target
mvn clean package -Dmaven.test.skip=true
cd /home/system/xiaozhi/

# Find the process using port 8002
PID=$(sudo netstat -tulnp | grep 8002 | awk '{print $7}' | cut -d'/' -f1)

rm -rf /home/system/xiaozhi/xiaozhi-esp32-api.jar
mv /home/system/xiaozhi/xiaozhi-esp32-server/main/manager-api/target/xiaozhi-esp32-api.jar /home/system/xiaozhi/xiaozhi-esp32-api.jar

# Check if process exists
if [ -z "$PID" ]; then
  echo "No process found occupying port 8002"
else
  echo "Process found using port 8002, PID: $PID"
  # Kill the process
  kill -9 $PID
  kill -9 $PID
  echo "Process $PID killed"
fi

nohup java -jar xiaozhi-esp32-api.jar --spring.profiles.active=dev &

tail -f nohup.out
```

Give it execution permission:
```
chmod 777 update_8002.sh
```
Proceed to the next step.

## 4.3 Automatically Compile and Run the Python Project

In `/home/system/xiaozhi/`, create a file called `update_8000.sh` with the following content:

```
cd /home/system/xiaozhi/xiaozhi-esp32-server
git pull origin main

# Find the process using port 8000
PID=$(sudo netstat -tulnp | grep 8000 | awk '{print $7}' | cut -d'/' -f1)

# Check if process exists
if [ -z "$PID" ]; then
  echo "No process found occupying port 8000"
else
  echo "Process found using port 8000, PID: $PID"
  # Kill the process
  kill -9 $PID
  kill -9 $PID
  echo "Process $PID killed"
fi
cd main/xiaozhi-server
# Initialize conda environment
source ~/.bashrc
conda activate xiaozhi-esp32-server
pip install -r requirements.txt
nohup python app.py >/dev/null &
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

Grant execution permission:
```
chmod 777 update_8000.sh
```
Continue to the next step.

# Daily Updates

Once all these scripts are set up, for daily updates all you need to do is run these commands in order to automatically update and start the services:

```
cd /home/system/xiaozhi
# Update and launch Java service
./update_8001.sh
# Update web service
./update_8002.sh
# Update and launch Python service
./update_8000.sh

# To view Java logs later, run:
tail -f nohup.out
# To view Python logs later, run:
tail -f /home/system/xiaozhi/xiaozhi-esp32-server/main/xiaozhi-server/tmp/server.log
```

# Notes

The test platform `https://2662r3426b.vicp.fun` uses nginx as a reverse proxy. You can find the detailed nginx.conf configuration [here](https://github.com/xinnan-tech/xiaozhi-esp32-server/issues/791).

## Frequently Asked Questions

### 1. Why is there no port 8001?

Answer: 8001 is only used in the development environment to run the frontend locally. For server deployment, it's not recommended to use `npm run serve` for the frontend. Instead, follow this guide to build static HTML files and use nginx to manage web access.

### 2. Do I need to manually update SQL scripts after every update?

Answer: No. The project uses **Liquibase** for automatic database version management, which will automatically execute any new SQL scripts.