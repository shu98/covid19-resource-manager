# covid-resources
Initial version of a website to centralize Covid-19 related clinical resources developed by a team of MIT students. This repository contains code that is available to the public. Excludes pem key and app.db files. 

## Dependencies
First install Python dependencies (Flask, etc):

```pip3 install -r requirements.txt```

## Local Development
To launch the development site, in your command prompt, type:

```python app.py localhost```

## Remote Development
First restrict read/write access on the ssh pem key.

```chmod 400 modfun.pem```

Then connect to the server (on AWS)

```ssh -i modfun.pem ubuntu@ec2-18-188-217-68.us-east-2.compute.amazonaws.com```

It's preferable to keep the pem key in a lower level directory like ~/.ssh.

Once you're on the server, connect to the tmux session `server` by running `tmux attach -t server`. That's where the Flask server is running. Here's a primer on [tmux](https://www.youtube.com/watch?v=BHhA_ZKjyxo)

The Flask process is always running on the server, and Flask listens to file updates (and liveloads according), but in the event of crashes, the server can be restarted with

```python app.py 0.0.0.0```

To view your changes after performing `git pull` in the tmux session, go to `http://ec2-18-188-217-68.us-east-2.compute.amazonaws.com:8000` or `http://18.188.217.68:8000` in your preferred browser.