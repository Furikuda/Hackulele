# Hackulele

Because all things got to be smart, China gifted us with a SmartUkulele called Populele [0]

The point is to use a bloated, kind of ugly app [1] to connect to your uke over bluetooth, sending commands to blink the lights behind the frets. The app gamifies the learning process, has songbooks and stuff, but as all "smart" things go, everyone on the App's page complains about unreliable BT connection, bugs, etc.

## Closer look at the Smart inside

The Smartness is hidden in the instrument and reveals a boardy board, a lipo-y lipo, and cabley cables to connect to the blinky blink side.

<img src="./docs/pics/top.jpg" width="300">

<img src="./docs/pics/bottom.jpg" width="300">

Main chip there is a Dialog 14580 [2]. Unfortunately, according to my logic analyzer, both TX/RX (for serial) & SDIO/SCK (for JTAG) aren't active: no easy hacking for me :'(

## BLE sniffing

I use the nRF52 devKit by Nordic [4] to sniff the BLE traffic. The output is verbose, the uke sends multiple heartbeats per second... LED matrix state is set by a 19 bytes packet sent to a GATT service  (attribute handle 0x0024, UUID is 0000dc8600001000800000805f9b34fb). 24 bits per string, as so:

```
f1 GG GG GG CC CC CC EE EE EE AA AA AA 00 00 00 00 00 00
^^ Header
   ^^ ^^ ^^ State of the G string LEDs
            ^^ ^^ ^^ State of the C string LEDs
                     ^^ ^^ ^^ State of the E string LEDs
                              ^^ ^^ ^^ State of the A string LEDS
```

The `bluez.py` script [3] will let you send these packets through BlueZ.

## Inside the fret board.

Hooking up your logic analyzer on SDA/SCL you get a listing of the SPI commands sent to the IS31FL3731 chip at boot time (address 0x74):

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

No idea why there are all these 0x08, they are nowhere in the IS31 doc, trying to fix weird timing issues maybe? Or just sloppy coding? I just ignored and wote a lib, which is in the repo [3]. The annoying part was finding what LED address corresponded to where on the fretboard.

Pull SCL & SDA up with a 4.7K resistor, ground INT, and set SDB as a 'enable' pin, to connect to the LED matrix.
```
          ___      ___
    _____|   |____|   |______
   |                         |
   |    5V     GND     SCL   |
   |                         |
   |    SDB    INT     SDA   |
   |_________________________|

```

and you get full control of the LEDs PWM and super fast animation update without the painful BLE setup.

## Animations!

This project is heavily influenced by the Best Badge Ever [5]. Both the CircuitPython `main.py` and BlueZ `bluez.py` scripts use the same Animator objects. See `animations/scroll.py` for an example.

# Links

[0] https://popuband.com/products/populele-with-accessory 
[1] https://play.google.com/store/apps/details?id=com.gt.populeleinternational&hl=en&showAllReviews=true
[2] https://support.dialog-semiconductor.com/downloads/DA14580_DS_v3.1.pdf 
[3] https://github.com/Furikuda/hackulele
[4] https://www.nordicsemi.com/Software-and-Tools/Development-Kits/nRF52-DK 
[5] https://github.com/oskirby/dc26-fur-scripts
