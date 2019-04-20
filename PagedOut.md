# Hackulele

(more info on this on the Github page)

Because all things got to be smart, China gifted us with a Smart-Ukulele called Populele.

The point is to use a bloated, kind of ugly app to connect to your uke over bluetooth, sending commands to blink the lights behind the frets. The app gamifies the learning process, has songbooks and stuff, but as all "smart" things go, everyone on the App's page complains about unreliable BT connection, bugs, etc.

## Closer look at The Smart

The "Smart" part is easy to pull off from inside the instrument and reveals a boardy board, a lipo-y lipo, and cabley cables to connect to the blinky blink side.

<img src="./docs/pics/top.jpg" width="300">

<img src="./docs/pics/bottom.jpg" width="300">

Main chip there is a Dialog 14580. Unfortunately, according to my logic analyzer, both TX/RX (for serial) & SDIO/SCK (for JTAG) aren't active: no easy hacking for me :'( I couldn't get any intel on the tiny thing on the side that's marked '5F2 A71 TOG'.

## BLE sniffing

I use the nRF52 devKit by Nordic to sniff the BLE traffic. The output is verbose, the uke sends multiple heartbeats per second, for some reason, probably to drain the battery faster.

The Uke's LED matrix state is set by a 19 bytes packet sent to a GATT service  (attribute handle 0x0024, UUID is 0000dc8600001000800000805f9b34fb). 3 bytes per string (G, C, E and A) are sent to set 18 LEDs (only the 18 MSB are used) as so:

```
f1 AA AA AA EE EE EE CC CC CC GG GG GG 00 00 00 00 00 00
```

The `bluez.py` script will let you send these packets through BlueZ.

## Inside the fret board.

Hooking up your logic analyzer on SDA/SCL you get a listing of the i2c commands sent to the IS31FL3731 chip at boot time (address 0x74):

```
74 08
74 08
74 FD 0B
74 08
74 0A 00
74 08
74 FD 00
74 08
74 00 FF
74 08
74 02 FF
74 08
74 04 FF
74 08
74 06 FF
74 08
74 08 FF
*snip*
```

No idea why the chip sends all these 0x08 commands, as they are nowhere in the IS31 doc, trying to fix weird timing issues maybe? Or just sloppy coding? I just ignored and wote a CircuitPython lib to talk to the LED matrix (`main.py`). The annoying part was finding what LED address corresponded to where on the fretboard.

To connect to the LED matrix, pull SCL & SDA up with a 4.7K resistor, ground INT, and set SDB as a 'enable' pin. The 5V VCC will need more than 50mA, so don't use an arduino GPIO.
```
female/uke side
       ___      ___
 _____|   |____|   |______
|                         |
|    5V     GND     SCL   |
|                         |
|    SDB    INT     SDA   |
|_________________________|

```

You now get full control of the LEDs PWM and super fast animation update without the painful BLE setup.

## Animations!

The library on the repo uses separate 'Animator' objects to update the internal LED state. It is heavily influenced by the Best Badge Ever (2018 DCFurs badge).

Both the CircuitPython `main.py` and BlueZ `bluez.py` scripts use the same Animator objects. See `animations/scroll.py` for an example.

## More info

Link to repo with more info, resources and docs: https://github.com/Furikuda/hackulele

You'll learn about the infamous "Page Night" (that comes after the eighth Page, and has the 0x0B identifier), and some ideas for more research.
