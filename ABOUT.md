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

Since I basically connected my logic analyzer on every fucking pad available there to see which one was doing anything, I quickly found that SDA/SCL are for the i2c bus.

