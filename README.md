# TV BRAZIL M3u8 Free
This project is a Django application made with Python 3.8 or higher, and it has the purpose of assembling M3u8 lists for IPTV transmission.

In this application you have: Movies, Series and Closed TV Channels.

![Channels Interface](https://i.imgur.com/tYMwVxs.png)

![List IPTV m3u8](https://i.imgur.com/YIxP9fZ.png)

For any devices, install your preferred:
[https://github.com/iptv-org/awesome-iptv](https://github.com/iptv-org/awesome-iptv)

## Requirements
### -- To install this project, you need to have Python (>= 3.6) installed on your machine, GIT, Google Chrome and  and the Anaconda tool.

### Step 1: Anaconda Tool
#### Download and Install Anaconda
1. Go to the [Anaconda Website](https://www.anaconda.com/download/#windows) and choose a Python 3.x graphical installer (A) or a Python 2.x graphical installer (B). If you aren't sure which Python version you want to install, choose Python 3. Do not choose both.
2. Locate your download and double click it.
3. Install Anaconda
4. This is an important part of the installation process. Please check the box to add into PATH.

### Step 2: Clone and Install
Clone the project:
```bash
git clone https://github.com/caiomarinhodev/megafilmes.git
```
then go into the project root and run:
```bash
pip install -r requirements.txt
```
to be able to install the project dependencies.

### Step 3: Configurations
In your terminal run:
```bash
python manage.py makemigrations
```
and
```bash
python manage.py migrate
```
and create an admin user for login into platform.
```bash
python manage.py createsuperuser
```

### Step 4: How to use
To use the tool you need discover your IP local.
P.S.: to find your local IP, open another terminal and run code below, and see your Local IPV4.
```bash
ipconfig
```


1) On terminal and run:
```bash
python manage.py runserver <your_local_ip>:80
```



2) Open other terminal, into project root, with your created enviroment and run:
```bash
python manage.py runcrons
```

After having the server running and the update CRON, to access the list, access your preferred browser (we recommend Chrome, as our application uses chromedriver to get the links from a reliable source.):
http://<your_local_ip>/lista.m3u8

or

http://<your_local_ip>/lista2.m3u8

CRON will update the channel list (there are 105 closed TV channels), and this process takes around 25 minutes. CRON runs the update process every 4 hours, because channels have an expiration time of 8 hours.

To solve this problem I created a CRON that runs every 4 hours and updates all 105 channels. Remember to always run the server ("runserver") to access the m3u8 list and run CRON ("runcrons") with the server on. Both must be running on different terminals.

any problem? send mail to me: caiomarinho8@gmail.com


## This project is to be used for Study purposes. Remember Piracy is Crime!
