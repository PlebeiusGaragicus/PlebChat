# How to deploy this for yourself

I recommend a dedicated Debian vitrual machine.

## change `root` prompt
```sh
echo 'export PS1="\n\[\e[1;35m\](\[\e[1;31m\]\u\[\e[1;35m\]@\[\e[1;34m\]\h\[\e[1;35m\]) [\w]\n\[\e[1;36m\]\$ \[\e[0m\]"' >> ~/.bashrc
source .bashrc
```

## `apt-update` and install prerequesties

```sh
apt-get update
apt-get upgrade -y

apt-get install -y git curl python3-venv python3-pip redis-server pkg-config

# pkg-config required for python sepsecp256k1 library, and therefore bolt11 library
```

## configure time zone
```sh
dpkg-reconfigure tzdata
```

## Configure Redis database
```sh
# ensure it's working
systemctl status redis-server
redis-cli ping

# TODO - configure it!
# nano /etc/redis/redis.conf
# systemctl restart redis-server

# enable
systemctl enable redis-server

```





## Create a non-`root` user

```sh
adduser satoshi
usermod -aG sudo satoshi
```

Then, log out of `root` and log in as this user

```sh
# signal that we are non-root
echo 'export PS1="\n\[\e[1;35m\](\[\e[1;31m\]\u\[\e[1;35m\]@\[\e[1;34m\]\h\[\e[1;35m\]) [\w] \[\e[33;3m\]\A\[\e[0m\] \[\e[1;36m\]\$ \[\e[0m\]\n"' >> ~/.bashrc

source .bashrc
```

## clone the repo

```sh
git clone https://github.com/PlebeiusGaragicus/PlebChat.git
cd PlebChat
```

## configure the Python virtual environment

note: use 3.10 on MacOS for development, but Debian 12 comes with 3.11, which probably works
```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## create user accounts for the application

```sh
bash generate_auth_yaml.sh
```

## create the `.env` file with API keys

```sh
cat << EOF > .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT="PlebChat development"
LANGCHAIN_API_KEY=

TAVILY_API_KEY=
OPENAI_API_KEY=
MISTRAL_API_KEY=
GEMINI_API_KEY=
EOF

nano .env
```

Copy and paste in any API keys you have.

## setup a `systemd` service to launch the application

Note: This will need `root` access.  Log in as `root` for these next steps.


```sh
cat << EOF > /etc/systemd/system/plebchat.service
[Unit]
Description=PlebChat Service
After=network.target

[Service]
User=satoshi
WorkingDirectory=/home/satoshi/PlebChat
ExecStart=/bin/bash -c "/home/satoshi/PlebChat/production"
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

nano /etc/systemd/system/plebchat.service
```

Also, replace `satoshi` with the non-root Linux username that you created earlier.

## start the service and monitor for errors

```sh
systemctl start plebchat
systemctl status plebchat

# works..?  If so:
systemctl enable plebchat

# watch it run via:
journalctl -u plebchat -f # hitting 'q' will exit
```

## Visit the application

Open a browser and go to the IP address of the server at port 8501. To determine the ip address, run the `ip addr` command.

For example, if your ip address is `192.169.10.200`, then put `192.169.10.200:8501` in your browser and it should work.

If you're running this locally instead of on a dedicated server then visit [localhost:8501](http://localhost:8501)
