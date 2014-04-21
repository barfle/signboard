dataplicity controlled stockticker signboard on AM03127
=======================================================

Today I built a dataplicity-enabled stock ticker with a Raspberry Pi and a signboard I picked up at Maplins for £50 or so.  

Via the dataplicity website I can control the signboard brightness, scrolling speed, and of course which stocks I want to display.  Most of the fields in the user interface are drop down boxes and control the display and speed of the ticker.  The first field is a text box where I add tickers one at a time, separated by a space.  The Raspberry Pi then collects settings from the server, retrieves the stock data from Yahoo, and renders them appropriately on the signboard.

I've made the dataplicity project public so anyone can build it, or on it, as they please :)

Pre-requisites
==============

The signboard itself is made in China and the technical programming document is hard to find, but I've included it in this repository for posterity.  I chose to connect the signboard to the Raspberry Pi via USB, and since it uses C2102 chippery to provide a serial port, it works right out of the box on the Pi and pops up as /dev/ttyUSB0.

I followed the usual dataplicity getting started guide at http://dataplicity.com/get-started/raspberry-pi/ to set up my account, the Pi, and to register a device class generating a sine wave.

Setting up the project
======================
ystockquote is a useful pip utility to query Yahoo Finance for stock information, and is really simple to use.  pyserial is needed just to communicate with the signboard over the USB-serial port.

I copied the sinewave directory in its entirety to ~/ and installed libraries like so:

  sudo pip install pyserial
  sudo pip install ystockquote

Next, I modified dataplicity.conf to define a new device class, in this case "projects.Signboard".  The Raspberry Pi example above shows how to do this to set up a camera-enabled device class, so I just modified the example to have a name better suited to what I wanted to build.  dataplicity register and presto we're ready to go.

User interface
==============
Next up was to modify the ui.xml to replace the sinewave example stuff with a textbox to specify the stocks, and dropdowns to select all the display options.  The final ui.xml is in this repository.

This is what the finished UI looks like:
![Finished signboard user interface](/images/signboard-web.jpg)

Controlling the signboard
=========================
I created a supporting library to drive the signboard, and chose to keep it out of the main dataplicity logic.  This wasn't strictly necessary but helps to keep things neat.  

The only remaining step was to stitch it all together, which I did in a couple of lines of code in signboard.py.  In short the signboard is updated each time the main dataplicity thread polls it, and also when any configuration changes server-side (typically because someone changed a device setting on the website).  I reduced the polling interval to 60 seconds in dataplicity.conf in case Yahoo gets grumpy that I'm querying their service too often.

Result!
=======
Now I have a stock ticker!  

![Finished signboard](/images/signboard-small.jpg)

I'm not sure what I'm going to do with it yet but having a stock ticker in my lounge room does make for some interesting conversations with friends. :-)

All in, it took a few hours to work my way around the signboard documentation (including finding it in the first place), and about an hour to get the dataplicity UI looking sharp.  

Have fun :-)
