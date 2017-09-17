Python package to control Awox mesh light bulbs.

API inspired by [Matthew Garrett](https://github.com/mjg59)'s python light bulb 
interfaces.

I have only one light bulb and so didn't really test the mesh features, and 
my light bulb was never associated with the official app.
Only tested with the ESMLm\_c9 model, firmware version 1.2.4

Requires :
Python 3, tested with 3.6.2
bluepy
pycrypto

### Exampe usage :
```
import awoxmeshlight

mylight = awoxmeshlight.AwoxMeshLight ("A4:C1:38:97:11:33", "mesh_name", "mesh_password")
mylight.connect ()

mylight.setColor (0x50, 0x76, 0x00 )

mylight.disconnect()

```

### Procedure to manually reset the light bulb (from Awox FAQ video):

3 times {
  On 1 sec
  Off 6 sec
}
On 10 sec
Off 10 sec
On 10 sec
Off 6 sec
On -> Light will blink and turn red

