Python package to control Awox mesh light bulbs.

API inspired by [Matthew Garrett](https://github.com/mjg59)'s python light bulb 
interfaces.

I have only one light bulb and so didn't really test the mesh features, and 
my light bulb was never associated with the official app.

Only tested with the ESMLm\_c9 model, firmware version 1.2.4

Requires :
- A recent version of Python 2 or 3 (tested with 3.6 and 2.7)
- bluepy
- pycryptodome

## Installation

From the directory containing `setup.py` : `pip install .` or
`pip install --user .` to install in the user's Python directory.

## Usage :

From reports, it may not be possible to use the Awox app at the same time as this.

### Setting the password on an unpaired light

The `setMesh` function may hang, but the light blinks when accepting the settings.

```python
import awoxmeshlight
mylight = awoxmeshlight.AwoxMeshLight ("A4:C1:38:78:11:33")
mylight.connect() # Unless specified, the default name and password are used
mylight.setMesh("new_mesh_name", "new_mesh_password","new_mesh_key")
mylight.disconnect()
```

### With the remote

*Contributed by [Pixtxa](https://github.com/Pixtxa).*

Reset the light (hold PowerOn + Fav. 1) and the remote (hold PowerOn +
ColorCycle) and connect the remote to the light again (hold PowerOn). Now hold
PowerOn and the blue button for a few seconds, so the remote switches to
Bluetooth-mode. Use BT-app (nRF-Connect or so) to get the mac and name (both
will have the same name, its "R-" followed by the last 6 digits of the remotes
mac-address). Password will be "1234".

For the remote:

```python
import awoxmeshlight
myremote = awoxmeshlight.AwoxMeshLight ("A4:C1:38:75:24:93", "R-752593", "1234") #change to your remotes data
myremote.connect()
myremote.setMesh("PixtxaLightNet", "IeY3johvoosh","4556572782865925") #better change all of them
myremote.disconnect()
```
[After setMesh(...) the program didn't work, but the data was set, so i killed the task]

For the light:
```python
import awoxmeshlight
mylight = awoxmeshlight.AwoxMeshLight ("A4:C1:38:78:62:74", "R-752593", "1234") #change to your lights data
mylight.connect()
mylight.setMesh("PixtxaLightNet", "IeY3johvoosh","4556572782865925") #same as on the remote
mylight.disconnect()
```
[After setMesh(...) the program didn't work, but the data was set, so i killed the task]

Now you can run a simple test script:

```python
import awoxmeshlight
import time
mylight = awoxmeshlight.AwoxMeshLight ("A4:C1:38:78:62:74", "PixtxaLightNet", "IeY3johvoosh")
mylight.connect()
mylight.setColor(0x00, 0xFF, 0x00) #green
mylight.setColorBrightness(0x01) #dark
time.sleep(1)
mylight.setColorBrightness(0x64) #bright
time.sleep(1)
mylight.setPreset(0) #colorchange
mylight.setSequenceFadeDuration(500)
mylight.setSequenceColorDuration(500)
time.sleep(15)
mylight.setWhite(0x00, 0x7F) #coldwhite
time.sleep(1)
mylight.setWhite(0x73, 0x63) #warmwhite
time.sleep(1)
mylight.off()
time.sleep(1)
mylight.on()
mylight.disconnect()
```

## Printing some debug info

Functions don't print anything, instead the `logging` module is used.

Example using the logger to print everything to stderr :
```python
import awoxmeshlight
import logging

logger = logging.getLogger("awoxmeshlight")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler ()
handler.setLevel(logging.DEBUG)
logger.addHandler (handler)

mylight = awoxmeshlight.AwoxMeshLight ("A4:C1:38:97:11:33", "mesh_name", "mesh_password")
mylight.connect ()
mylight.setColor (0x50, 0x76, 0x00 )
mylight.disconnect()
```

## Procedure to manually reset the light bulb (from Awox FAQ video):

Turn on and off in the following sequence :

- 3 times :
  - On during 1 sec
  - Off during 6 sec
- On 10 sec
- Off 10 sec
- On 10 sec
- Off 6 sec
- On -> Light will blink and turn red

