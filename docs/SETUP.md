# How to deploy this for yourself

I recommend a dedicated Debian vitrual machine.

## `apt-update` and install prerequesties

```sh
apt-update
apt-upgrade -y

apt-get install -y git curl python3-venv python3-pip

```

## Create a non-`root` user

```sh
TODO
```

Then, log out of `root` and log in as this user

## clone the repo

```sh
git clone https://github.com/PlebeiusGaragicus/PlebChat.git
cd PlebChat
```

## configure the Python virtual environment

```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## create user accounts for the application

```sh
cat << EOF > auth.yaml
credentials:
  usernames:
    satoshi:
      email: satoshi@nothing.nowhere
      name: Satoshi Nakamoto
      password: $2b$12$PuMoR5TPJUbvIA9tIAG03O4MaYyQhCzGq61MtVQ7.Hi4W5isFo.3S
    another_user:
      email: hello@nothing.nowhere
      name: Another User
      password: $2b$12$E/D/AFoBnmk66ryLjTFePuND9JI8BfBMxyAinwCycM4YMgujBvOhu
cookie:
  expiry_days: 7
  key: my_streamlit_user_auth_key
  name: my_streamlit_user_auth
preauthorized:
  emails:
    - satoshi@nothing.nowhere
EOF

nano auth.yaml
```

Note: The passwords are actually "salted" hashes.  Do not put the actual password in the .yaml file.

To save an exit - use Ctrl-X, accept changes with 'y' and press 'Enter'

## How do I determine the password hash?

Good question - run a Python REPL session and enter this code:

```python
import streamlit_authenticator as stauth
print(stauth.Hasher([input("Enter password: ")]).generate()[0])
```

## create the `.env` file with API keys

```sh
cat << EOF > .env
OPENAI_API_KEY=""
ASSEMBLYAI_API_KEY=""
MISTRAL_API_KEY=""
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
ExecStart=/bin/bash -c "/home/satoshi/PlebChat/launch_production"
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
