# Pydule-TM

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)                 
[![Python 3.6](https://img.shields.io/badge/python-3.10.7-blue.svg)](https://www.python.org/downloads/release/python-3107/)   

## Functionality of Pydule

- Get Battery Percentage
- Access ChatGPT
- Get Any Website HTML
- Encrypt and Decrypt a String
- Record Screen,Internal Audio and Microphone
- Seperate String
- Insert Elements in Tuple & String
- Generate Qrcode
- Copy Text
- Language Translation
- Edit JSON Files
- Replace Letters in String
- Check Weather of any City
- Open any File
- Play Songs
- Get Hex of any Color
- Convert Text to Speech
- Convert Speech to Text
- Restart and Shutdown Your System
- Search on Browser
- +40 more Functions

## Usage

- Make sure you have Python installed in your system.
- Run Following command in the CMD.
 ```
  pip install Pydule
  ```
## Example

 ```
# test.py
import Pydule as py

# to Find the Remaining Battery Percentage
battery=py.aboutbattery('percentage')
print(battery)

# to Search 
py.search('Youtube')

# to Get Any Website HTML
html=py.GetWebHTML('URL')
print(html)

# to Create Qrcode
text,filename='Hello World','Hello.png'
py.cqrcode(text,filename)

# to get the Location of the Selected File
path=py.askfile()
print(path)

# to Get all Available Functions
py.functions() 

# to Open Calculator
py.openapp('calculator')

# to Copy Text
py.copy('Hello World')

# to play mp3
py.playmusic('PATH')

# to Access ChatGPT
from Pydule import AI
print(AI.ChatGPT('Hi There','Your API Key'))

# to Track the Location
print(py.TrackLocation('Your Phone Number')) #Example +911234567890
  ```