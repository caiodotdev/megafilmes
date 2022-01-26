# TV BRAZIL M3u8 Free
This project is a Django application made with Python 3.8 or higher, and it has the purpose of assembling M3u8 lists for IPTV transmission.

In this application you have: Movies, Series and Closed TV Channels.

![Channels Interface](https://i.imgur.com/tYMwVxs.png)

![List IPTV m3u8](https://i.imgur.com/YIxP9fZ.png)

## Requirements
### -- To install this project, you need to have Python (>= 3.6) installed on your machine, GIT, Google Chrome and  and the Anaconda tool.

### Step 1: Anaconda Tool
#### Download and Install Anaconda
1. Go to the [Anaconda Website](https://www.anaconda.com/download/#windows) and choose a Python 3.x graphical installer (A) or a Python 2.x graphical installer (B). If you aren't sure which Python version you want to install, choose Python 3. Do not choose both.
2. Locate your download and double click it.
3. Install Anaconda
4. This is an important part of the installation process. The recommended approach is to not check the box to add Anaconda to your path. This means you will have to use Anaconda Navigator or the Anaconda Command Prompt (located in the Start Menu under "Anaconda") when you wish to use Anaconda (you can always add Anaconda to your PATH later if you don't check the box). If you want to be able to use Anaconda in your command prompt (or git bash, [cmder](http://cmder.net/), powershell etc), please use the alternative approach and check the box.

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
To use the tool run python command.

1) On terminal and run:
```bash
python manage.py runserver <your_local_ip>:80
```
2) Open other terminal, into project root, with your created enviroment and run:
```bash
python manage.py runcrons
```

