# Hackulele

OpenSource library to talk to a [Populele](https://popuband.com/products/populele-with-accessory)'s Led matrix

![](./docs/pics/awoo.gif)

If you're interested about the story behind the project, and how this came up, I have [another doc](ABOUT.md) for you.

## BLuez to talk to the Populele right away

If you want to talk over bluetooth to your Populele, use `bluez.py`.

Pros:

 * No need for new hardware

Cons:

 * Not possible to set PWM per LED


The script requires some dependencies:

```
apt install python-pydbus python-gi
```

Make sure Bluez is up and running. I've tested that everything works with version 5.50.

Then just hack the script to your liking and run `python bluez.py`.

## Connect your own board to the Led Matrix

Pros:

 * Full LED matrix control over SPI

Cons:

 * Need to remove all the smart from the ukulele and bring your own.

The code should currently work on any board that can run Adafruit's [CircuitPython](https://circuitpython.readthedocs.io).

I use the [Feather M0 Bluefruit](https://www.adafruit.com/product/2995), for later BLE dev (maybe).
This one is nice because it has the battery charging circuit (so I can keep everyhing inside the instrument) as well as BLE for later things.

Just copy `main.py` over to your mounted board's filesystem.

### Wires & stuff

This is a bit trickier. Once you disconnected everything from your Uke, you'll be left with a JST-style connector.
When looking at it you get the following pins:


```
          ___      ___
    _____|   |____|   |______
   |                         |
   |    5V     GND     SCL   |
   |                         |
   |    SDB    INT     SDA   |
   |_________________________|

```

Connect SCL/SDA/5V/GND to the same pins on your microcontroller board (5V is the one directly connected to USB). 

Then put INT to GND, and SDB to pin D10.

Also remember SCL & SDA need to be Pull'ed UP, so connect them to 5V via a 4.7K resistor for each line.

Stuff everything back into the ukulele and you should be good to go.

### Push the code

Your CircuitPython enabled board should expose a mass storage device. Just copy `main.py` and the folder `animations` over there.

## Add your own animations

This project is heavily influenced by the [Best Badge Ever](https://github.com/oskirby/dc26-fur-scripts).

Both the CircuitPython `main.py` and BlueZ `bluez.py` scripts call whatever animation object `Draw()` method every `interval` milliseconds. Use this to refresh the `Populele` object internal state with its public methods.

See `animations/scroll.py` for an example.
