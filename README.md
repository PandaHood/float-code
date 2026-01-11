# For competition

Show to judges that this is our float. 
```
python3 info.py
```

Output will show our team number, our team name, and our time.
```
Team Number: 1
Profile Number (1 or 2): 1
Team_number: 1, Team_name: NUWave, Time: 2025-06-01 15:12:10.187183
```

Then run:
```
screen python3 -m main.py
```

This will begin our profile to 2.5 meter target depth and write collected data in a txt file.
Run again for 2nd profile.

# Requirements to get running

https://docs.google.com/document/d/1D_I2853OfC4Va9mcNUwvv2ihBTWLX-WokWMMtqTiFkc/edit?tab=t.0 

Make sure https://github.com/bluerobotics/ms5837-python is installed
- gpiozero

Run $ pip install -r requirements.txt for python package requirements

How to run code:

$ screen python3 [python file]

$ screen python -m testing.[dir].[file] for running test package files

have dhcp client list open, when program ends and float gets back
in range, reconnect at ssh at new raspberry pi address

chmod +x run.sh to activate script

