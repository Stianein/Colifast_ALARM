# Software for Colifast ALARM

Project Link: [Colifast ALARM repository](https://github.com/Stianein/Colifast_ALARM)

Welcome to the **Colifast ALARM software** documentation! This project is designed to operate pumps and valves, heater element, light sources, relay box, and spectrophotometer for metering fecal content of water sources. The software allows the user control over the components through a python-based file with extension ``.CFAST``. There are helper functions in the background that can be utilized from these files, which is described in this documentation, as well as the basic communication with the components.

## Table of Contents
- [Installation](installation.md)
- [Usage](usage.md)
- [Contributing](#contributing)

## Overview

In this project I have developed software for the Colifast ALARM instrument. We sought to take more control over the whole of the equipement (previously purchased software), which measures fecal indicator bacteria in water recipients, see our web page for more info on it´s usecases.

Colifast is as of 2024 a low budget company, and open source is thus a reasonable strategy for our software. Sharing the source code may have som benefits to us, it could help us navigate customer needs, and github can be a platform to handle future priorities of development. Aside from that maybe this project could work as a starting point for people who whish to develope software to communicate with the same or similar components used in the Colifast ALARM system. 

Off course I would be more than happy to have people participate on the development, to make the equipement even better, despite it being a commercially sold equipment, should they wish to. The software can be opened fine on a *Windows computer* without the components connected, but it has not yet been time to make modules that simulate the function of the components. 

The equipment is not cross platform, as it utilizes components that are **Windows** only components. 


## Quick Start
The instrument is handled through method files that can be loaded in the GUI through the *Method Selection* found under **Method**. The method files are structured in three parts:

1. VARIABLES
2. FUNCTIONS
3. CODE TO BE EXECUTED

It is basically *Python* code, but i have given the files the CFAST extension for fun. The code is loaded into the Editor part of the gui using *AST* parser, and will try to sort the code into three windows based on these three sections. The **method_helper** file runs the method file using the *exec* function, and also contains some aditional functions for streamlining the calls one can make from the method file. This however requires the import of the *method_helper* in your *method file* `from method_helper import *`

### Variables

Here we set some initial values, eg is values stored in the settings file of the system, a file that is updated through the GUI, and thus can "communicate" the selected user settings to the *method file* if collected here.

```python
turbidity_wavelength = settings.getWavelengthTurb()
fluorescent_wavelength = settings.getWavelengthFluo()
remaining_samples = settings.getRemaining()
bottle_size = settings.getBottleSize()
sample_source = settings.getSampleSource()
```


### Functions

Here you can specify complex functions in order to keep the actual code nice and clean. Example of a functioin is the ``incubator_fill`` function that allow the user to fill the incubator chamber with the a fluid of a given volume, as the function thakes those parameters as arguments. 

```python
  # Function for washing cell #
  def inkubator_fill(fluid, volume):
    global status
    global sample_source
    status.emit(f"Flushing cell with {volume} ml of {fluid}")
    mpv.liquid(fluid)
    # Washes cell with 150 mL of water
    pump_size_ml = int(int(settings.getPumpSize())/1000)
    iterator = int(volume/pump_size_ml)
    for i in range(iterator):
      xlp.flowrate(400)
      xlp.valve_out()
      xlp.fill()
      xlp.delay_until_done()
      xlp.valve_in()
      xlp.flowrate(500)
      xlp.empty()
      xlp.delay_until_done()
  ```

### Code to be executed

Here the code to be conducted is written, the user can now, with the aforementioned function in place, call the *incubator_fill* function to rinse the chamber with 150 ml of acid from channel 4, by calling ``inkubator_fill(4, 150)``. The chamber could then be emptied by starting the peristaltic pump. It is a simple on/off relay switch that is controlled through the ADU port, 0. So calling ``adu.on(0)`` will turn on the pump. A delay, and then turning it off again is waranted for a propper emptying of the chamber, before the next piece of code. 

Remember to consider the actual mechanical strain this code does to the equipement, and be sure to know the effect of the code. The syringe pump is for instance equiped with a *flowrate* function that can be set to minimize strain on channels that goes to suceptible parts. We usually use a flowrate of 400 ul/sec, that could be set with the following command, ``xlp.flowrate(400)``

For more detailed descriptions of commands for the components and inherent functions from the ``method_helper`` file, see the [docs]().

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

[Back to Top](#software-for-colifast-alarm)

### Top contributors:

<a href="https://github.com/Stianein/Colifast_ALARM/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Stianein/Colifast_ALARM" alt="contrib.rocks image" />
</a>

## License

Distributed under the GPL License. See `LICENSE.txt` for more information.
