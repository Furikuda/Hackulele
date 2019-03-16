# Hackulele

I was bored abroad and missed my ukulele to just occupy my hands. Turned out some other dude was selling one of his [Populele](https://popuband.com/products/populele-with-accessory) for pretty cheap, so I bought it to have a travel uke, and also because OMG BLINKING LIGHTS. 

## Unboxing

Haha. No.

## Playing

You can make pleasant noises with it. Just train for a couple years or more.

## App

The point of the whole thing is you're supposed to use bloated ugly and slow ass app to connect to your uke over bluetooth, so it can send it commands to light the blinky lights.

After you go through the unskippable "tutorial" that will drive everybody crazy, it can shows you chords, you can 'draw', and other things.

It tries to gamify the learning process, has songbooks and stuff. 

As all "SMART" things go, everybody on the [app's page](https://play.google.com/store/apps/details?id=com.gt.populeleinternational&hl=en&showAllReviews=true) complains about shitty bluetooth connection, bugs, etc. The whole thing is just absolutely frustrating to use and barely works as expected. Also probably comes with free remote management of your Android device ¯\\\_(?)\_/¯

# Hacking

Okay here are the fun parts. The SMARTness of the thing is hidden in the easily unscrewable brown plastic part on the side of the instruments. Reveals a boardy board, a lipo-y lipo, and cabley cables to connect to the blinky blink side.

Top of the board:
<img src="./docs/pics/top.jpg" width="500">

Bottom of the board:
<img src="./docs/pics/bottom.jpg" width="500">

Connector to the LED matrix:
<img src="./docs/pics/jst.jpg" width="500">

My hackey senses are tingling at the sight of the RX/TX as well as SDIO/SCK pads there.... But well, we'll see.

Main chip is a [Dialog 14580](./docs/DA14580_DS_v3.1.pdf) which looks pretty nice. The tiny thing on the side maybe be a flash but I didn't look into it.

## The promise of UART & JTAG

RX/TX means serial UART, let's connect my usual USB to RS232 thing to there and hope this will talk to me. NOPE.

SDIO/SCK are definitely connected to the corresponding JTAG pins on the Dialog chip (P1_4/SWCLK & P1_5/SW_DIO) but again, no luck trying to talk to it.

Unfortunately, try as I might, my logic analyzer shows absolutely nothing on the UART & JTAG ports. the Dialog chip allows to programmatically disable those so I guess there is no fun for me there.

## OTA

A cool feature of the Dialog chip is they offer to flash a new version of the Firmware Over The Air via bluetooth. The manufacturer only published one [new firmware](./docs/BleUKNoShowBat_XD_1988.img) that basically makes the lights blink even without bluetooth.

You can push the new firmware via Dialog owns app.

I couldn't find any previous research on the firmware format, so there is no way I can dump that in IDA.

## Next avenue: BLE sniffing

I have been unable to make [BTLEJack](https://github.com/virtualabs/btlejack) work, and haven't try to sniff the BLE traffic to write my own client to the board

## Conclusion

Fuck that board.

# My own

## Who are you Mr Chip 

Since I basically connected my logic analyzer on every fucking pad available there to see which one was doing anything, I quickly found that SDA/SCL are for the i2c bus.

The others are either pulled high or low while operating, so I don't bother about those much, and connect them accordingly to GND or VCC from an arduino.

Using [PulseView](https://sigrok.org/wiki/PulseView) to decode the i2c protocol I get a trace that shows expected blobs of writing an i2c address (0x74) for the Populele and one or two more byte.

Unfortunately the LED driver chip is buried somewhere in the instrument, so I just save the i2c startup/operation sequence into a file and try to make sense out of it.

Knowing the i2c address can help figure out what chip you're talking to. Using the nice [i2c addresses list](https://learn.adafruit.com/i2c-addresses/the-list) provided by Adafruit, you end up with either a HT16K33 or IS31FL3731.

## The I2C trace

This is the raw i2c data sent to the LED matrix chip. Every line start with 0x74 as this is the i2c address.

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
74 08
74 0A FF
74 08
74 0C FF
74 08
74 0E FF
74 08
74 10 00
74 08
74 01 00
74 08
74 03 00
74 08
74 05 00
74 08
74 07 00
74 08
74 09 00
74 08
74 0B 00
74 08
74 0D FF
74 08
74 0F 00
74 08
74 11 00
74 08
74 FD 0B
74 08
74 00 00
74 08
74 01 00
74 08
74 02 01
74 08
74 03 02
74 08
74 05 01
74 08
74 06 00
74 08
74 08 00
74 08
74 09 00
74 08
74 0A 01
74 08
74 FD 0B
74 08
74 0A 00
74 08
74 FD 0B
74 08
74 0A 01
74 08
74 FD 00
74 08
74 08
74 90 55
74 08
74 08
74 91 55
74 08
74 08
74 92 55
74 08
74 08
74 93 55
```

Upon boot, the populele will blink a row of LEDS, which I guessed are the last part here.

Something feels funny already, they send these `0x74 0x08` commands all the time, once or twice. Nowhere in the [specification](docs/IS31FL3731.pdf) or even the [Application Notes](docs/IS31FL3731 Application Note Rev.C.pdf) does the manufacturer talks about these, so *shrug*.

You grab some piece of code for arduino or any or your favorite microcontroler, you send this code, and get your blink. Yeah!

## WTF is this all about?

I have no idea what's going on in the mind of the people who wrote the code to talk to the chip, but there is a lot of redundancy. Here is the code, doing the same thing, without all the useless crap:

```
74 FD 0B # Open 'Page Nine' or Settings page
74 0A 00 # Set shutdown = true
74 FD 00 # Open Page 1
74 00 FF # Select all LEDs in matrix A as being used
74 02 FF
74 04 FF
74 06 FF
74 08 FF
74 0A FF
74 0C FF
74 0E FF
74 10 00 # Except CA9
74 01 00 # Select all LEDs in matrix B as being unused
74 03 00
74 05 00
74 07 00
74 09 00
74 0B 00
74 0D FF # Except CB7
74 0F 00
74 11 00
74 FD 0B
74 00 00 # Set pictre mode
74 FD 0B
74 0A 01 # Undo shutdown
74 FD 00 # Select page 1
74 90 55 # Light up LED from 0x90 to 0x93
74 91 55
74 92 55
74 93 55
```

That's 30 instructions instead of 85....

Looking at the datasheet is kind of hilarious too.

The chip can store the state of LEDs in 8 pages, and the ninth page, being for whatever reason at address 0x0B, is called a bit strangely sometimes.

<img src="./docs/pics/lolsheet1.jpg" width="500">

Some other typos.

<img src="./docs/pics/lolsheet2.jpg" width="500">
