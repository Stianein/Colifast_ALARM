<style>
body {
    font-family: 'Calibri', sans-serif;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}
th, td {
    padding: 8px;
    text-align: left;
    border: 1px solid #ddd;
}
th {
    background-color: #f4f4f4;
}
.enlargeable {
  cursor: pointer;
  transition: transform 0.3s ease;
  position: relative;
  float: right;
    margin-left: 15px; 
    margin-right: 15px; 
    margin-bottom: 15px;
    margin-top: 15px;
}

.enlargeable:hover {
  transform: scale(2.5); /* Adjust the scale as needed */
  transform-origin: right;
  z-index: 100;
}

</style>

<!-- TABLE OF CONTENTS -->
<h1 id="table-of-contents">Table of Contents</h1>

- [Introduction](#usage)
- [Components](#components)
  - [ADU](#adu)
  - [Spectrometer](#spectrometer)
  - [Syringe Pump](#syringe-pump)
  - [Multiposition valve](#multiposition-valve)
- [Helper functions](#helper-functions)

# Usage

For communicating with the components of the Colifast ALARM system commands described herein can be used.

The ``method_helper.py`` file is importing the components with their propper naming as can be seen below, an so when including the line ``from method_helper import *`` to the top of your custom method file, the commands mentioned here will work in your set up.

```python
# Own imports
from components.adu.adu import adu
import components.xlp as xlp
import components.sfm as sfm
import components.mpv as mpv
```

<h1 id="components">Components</h1>

<h2 id="adu">ADU</h2>

[Back to ToC](#table-of-contents)

<img src="..\images\ADU_adv.png" alt="ADU_advanced" class="enlargeable" width="250" style="float: right; margin-left: 15px; margin-right: 15px; margin-bottom: 15px;">

<br>
<br>

This component allows the user to manually turn on/off the relays of the **ADU208** relay unit. The relay box is implemented as a class called ``ADUCommunication`` found under ``components > adu > adu.py``. It is a singleton class for limiting access to the adu device to a single entry point, and handles queing of requests to the component from different threads of the system.

There are four main functions that are meant to be called from outside this class:
<table>
    <tr>
        <th>Function</th>
        <th>Use</th>
        <th>Args</th>
    </tr>
    <tr>
        <td>on</td>
        <td>adu.on(relay)</td>
        <td>where relay is an integer 0-7.</td>
    </tr>
    <tr>
        <td>off</td>
        <td>adu.off(relay)</td>
        <td>where relay is an integer 0-7.</td>
    </tr>
    <tr>
        <td>read</td>
        <td>adu.read("RPA0")</td>
        <td>"RP" + channel, channels: K0-K7/(relays) or A0-A2(readable)</td>
    </tr>
    <tr>
        <td>write</td>
        <td>adu.write("SK0")</td>
        <td>"R" or "S + channel, channels: K0-K7</td>
    </tr>
</table>

- In adition there is an ``adu.reset()`` function to zero all the relays which could also be accessed through the ``adu.write("MK0")``.
- And there is an adu.close() function to shut down the device connection. 

**Note:** The write function is somewhat superfluous as it would be used to control the relays that are already implemented in the on/off functions.

<br>
<br>

<h2 id="spectrometer">Spectrometer</h2>

[Back to ToC](#table-of-contents)


This component allow the user to read spectrum or maybe more relevant the intensity of a specified wavelength. There are some functions in the ``components > sfm.py`` which can be called, but the intention is for many of them to access them through the GUI rather than calling them from the code. The component can be initialized using serial number as an option but also just let the system fetch the first availible spectrometer.

```python
sfm.initialize(serial_number=None)
```
The integration time (milliseconds) is set in the initialization function and the value is set from the GUI, or could be set programatically with the ``settings.storeIntegrationTime(time)`` before initializing the component.

The sfm.py file has a **sfm_read** function to get time stamp and the data red, but I recommend using the wrapper function found in the ``method_helper.py`` file that also enable the storing of data inside the database of the program.

```python
sfm.sfm_read(wavelength, store_data=True, nm_bandwidth = 1, readings_to_average_over=None, series_id=1)
```

<table>
  <thead>
    <tr>
      <th>Argument</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>wavelength</strong></td>
      <td>Specify the wavelength (int), in nanometer, you want to check, e.g.turbidity standard 860 nm (remember to keep it within the bounds of the spectrometer's specifications).</td>
    </tr>
    <tr>
      <td><strong>store_data</strong></td>
      <td>Bool to choose whether to store the data in the database or not.</td>
    </tr>
    <tr>
      <td><strong>nm_bandwidth</strong></td>
      <td>The nanometer bandwidth the spectrometer should include in the data collection, default is &plus;/&minus; 0.5 nm (1) on each side of the specified wavelength.</td>
    </tr>
    <tr>
      <td><strong>readings_to_average_over</strong></td>
      <td>Multiple reads could be collected to get an average, to rule out spurious results.</td>
    </tr>
    <tr>
      <td><strong>series_id</strong></td>
      <td>A series ID (int) can be set to distinguish between series of measurements of the same wavelength should it be necessary to distinguish them from each other in the database later on.</td>
    </tr>
  </tbody>
</table>


  <!-- <img src="..\images\calibration.png" alt="spectrometer" class="enlargeable" width="100"> -->
   



<h2 id="syringe-pump">Syringe Pump</h2>

[Back to ToC](#table-of-contents)

<!-- <img src="..\images\liquid_handling.png" alt="spectrometer" class="enlargeable" width="350"> -->

The **XLP6000 syringe pump** is initialized with the COM port set in the GUI, but a port can also be specified as an argument.

```python
xlp.initialize(COMport)
```
Here are a table of other functions that control the syringe pump:

<table>
  <thead>
    <tr>
      <th>Function</th>
      <th>Argument Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>aspirate(volume)</strong></td>
      <td>Asks the pump to aspirate a specified volume. <br> <strong>volume</strong>: The amount of liquid to aspirate, in milliliters.</td>
    </tr>
    <tr>
      <td><strong>fill()</strong></td>
      <td>Fills the syringe to its maximum capacity.</td>
    </tr>
    <tr>
      <td><strong>dispense(volume)</strong></td>
      <td>Dispenses a specified volume of liquid from the syringe. <br> <strong>volume</strong>: The amount of liquid to dispense, in milliliters.</td>
    </tr>
    <tr>
      <td><strong>empty()</strong></td>
      <td>Empties the syringe completely.</td>
    </tr>
    <tr>
      <td><strong>valve_out()</strong></td>
      <td>Switches the valve head to the out position.</td>
    </tr>
    <tr>
      <td><strong>valve_in()</strong></td>
      <td>Switches the valve head to the in position.</td>
    </tr>
    <tr>
      <td><strong>flowrate(rate)</strong></td>
      <td>Sets the flow rate of the pump. <br> <strong>rate</strong>: The flow rate in microliters per second.</td>
    </tr>
    <tr>
      <td><strong>delay_until_done()</strong></td>
      <td>Delays the operation until the pump has completed its current action.</td>
    </tr>
  </tbody>
</table>

In adition there are these query functions to check the valve and plunger position.

<table>
  <thead>
    <tr>
      <th>Function</th>
      <th>Argument Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>valve_position()</strong></td>
      <td>Queries and returns the current valve position. The returned value is 'o' for out (to the MPV) or 'i' for in (to the incubator chamber).</td>
    </tr>
    <tr>
      <td><strong>pump_position()</strong></td>
      <td>Returns the current volume position of the syringe plunger based on the pump size.</td>
    </tr>
  </tbody>
</table>


**Note:** COM ports are external connections to computers, that once connected, works almost as integrel parts of the computer. They are therefor often very stable once set up, but if there is some error to the connection they will not propperly reset before the system has undergone a rebooting. That is why we often recommend a reboot when the system has trouble connecting to the syringe pump.



<h2 id="multiposition-valve">Multiposition Valve (MPV)</h2>

[Back to ToC](#table-of-contents)

The multiposition valve is initialized with the COM port set in the GUI, but a port can also be specified as an argument.

```python
mpv.initialize(COMport)
```

There is only one function for this component as it is simply used to switch the port connected to the syringe pump. 

```python
mpv.liquid(channel)
```

The argument, *channel*, ensures the valve shifts to that channel, and the syringe will thus aspirate/dispense liquid from there, given that the syringe valve is turned in the out direction towards the MPV. It is here important to know which connections are not to be dispensed large volumes to (eg. medium) and which are not to be asprated from (eg. waste). Find our standard setup in the table, the argument can be index or value in the following list: ["waste", "na_thisul", "sample2", "acid", "sample1", "media"]

<br>
    <table>
    <tr>
        <th>Channel</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>1</td>
        <td>Waste</td>
    </tr>
    <tr>
        <td>2</td>
        <td>Sample Out/External Sample</td>
    </tr>
    <tr>
        <td>3</td>
        <td>Reagent B (Sodium Thiosulfate)</td>
    </tr>
    <tr>
        <td>4</td>
        <td>Acid</td>
    </tr>
    <tr>
        <td>5</td>
        <td>Sample</td>
    </tr>
    <tr>
        <td>6</td>
        <td>Medium</td>
    </tr>
    </table>


<h2 id="helper-functions">Helper functions</h2>

[Back to ToC](#table-of-contents)

In addition to these functions for component control, there are some hidden functions in the ``method_helper.py`` file for enabling a cleaner method file.

- LogOn() which tries to log on all the components of the system.
- delay(seconds) a delay function to halt further operation untill the right time.
- error(message) a function for aborting the method when in error, with the provided **error message**.
- warning_message(message) a function for halting  the method until the user checks out the message provided as an argument.