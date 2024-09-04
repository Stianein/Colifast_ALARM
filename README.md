<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GPL License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][Colifast-linkedin]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://www.colifast.no/">
    <img src="images/Colifast_50pix.png" alt="Logo" width="200" height="30">
  </a>

<h3 align="center">Software for Colifast ALARM</h3>

  <p align="center">
    For the operation of a bacterial monitor - a growth based solution to metering feacal contamination in water.
    <br>
    <br />
    <a href="https://github.com/Stianein/Colifast_ALARM/blob/main/docs/index.md"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Stianein/Colifast_ALARM/blob/main/Manual.md">View Demo</a>
    ·
    <a href="https://github.com/Stianein/Colifast_ALARM/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/Stianein/Colifast_ALARM/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

 This project is designed to operate pumps and valves, heater element, light sources and spectrophotometer, etc. for metering fecal content of water sources. The software allows the user control over the components through a python-based file with extension ``.CFAST``. There are helper functions in the background that can be utilized from these files, which is described in the documentation, as well as the basic communication with the components.


`Stianein`, `Colifast_ALARM`, `twitter_handle`, `linkedin_username`, `email_client`, `email`, `project_title`, `project_description`

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* ![Python](https://img.shields.io/badge/Python-3.11-blue.svg) [Python](https://www.python.org/) - Programming language used.
* ![Anaconda](https://img.shields.io/badge/Environment-Anaconda-blue.svg) [Anaconda](https://www.anaconda.com/) - Python distribution and package management.
* ![PyQt5](https://img.shields.io/badge/PyQt5-5.15.9-brightgreen.svg) [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) - GUI framework for creating the application interface.
* ![NumPy](https://img.shields.io/badge/NumPy-1.26.0-orange.svg) [NumPy](https://numpy.org/) - Numerical computations and array handling.
* ![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7.2-blue.svg) [Matplotlib](https://matplotlib.org/) - Plotting and data visualization.
* ![Seabreeze](https://img.shields.io/badge/Seabreeze-2.8.0-yellow.svg) [Seabreeze](https://pypi.org/project/Seabreeze/) - Interface for Ocean Optics spectrometers.
* ![PySerial](https://img.shields.io/badge/PySerial-3.5-yellowgreen.svg) [PySerial](https://pyserial.readthedocs.io/en/latest/) - Serial port communication library.
* ![Qt](https://img.shields.io/badge/Qt-5.15.8-green.svg) [Qt](https://www.qt.io/) - Cross-platform application framework.
* [Lexilla](https://github.com/ScintillaOrg/lexilla) - Library for syntax highlighting, used by QScintilla.
* ![QScintilla](https://img.shields.io/badge/QScintilla-2.14.1-blue.svg) [QScintilla](https://riverbankcomputing.com/software/qscintilla/intro) - A Qt port of the Scintilla C++ editor component.
* [APScheduler](https://apscheduler.readthedocs.io/en/latest/) - Advanced Python Scheduler for scheduling tasks.

 **Standard Libraries**:
  * [Threading](https://docs.python.org/3/library/threading.html) - Python’s standard library for creating and managing threads.
  * [Queue](https://docs.python.org/3/library/queue.html) - Standard library for thread-safe queues.
  * [Futures](https://docs.python.org/3/library/concurrent.futures.html) - Standard library for asynchronously executing callables.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

For installing the prerequisite packages and setting up an environment for running this software I suggest using Anaconda:

### Prerequisites

* Find the prerequisited packages in the environment.yml file

### Installation

Go to Anaconda's webpage to download https://www.anaconda.com/download

1. Set up an environement using the provided environment.yml file.
   ```sh
   conda env create -f environment.yml
   ```
2. Clone the repo
   ```sh
   git clone https://github.com/Stianein/Colifast_ALARM
   ```
3. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin Stianein/Colifast_ALARM
   git remote -v # confirm the changes
   ```
4. Set up the pyseabreeze drivers – by running the run_seabreeze_setup.bat file.

5. Make sure to include the dll´s in the right folders. Pump and ADU – figure out how i did this myself.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
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

For more detailed descriptions of commands for the components and inherent functions from the ``method_helper`` file, see the [docs](https://github.com/Stianein/Colifast_ALARM/blob/main/docs/index.md).



## Demo

For a demo check out the [manual](https://github.com/Stianein/Colifast_ALARM/blob/main/Manual.md)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap


See the [open issues](https://github.com/Stianein/Colifast_ALARM/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/Stianein/Colifast_ALARM/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Stianein/Colifast_ALARM" alt="contrib.rocks image" />
</a>



<!-- LICENSE -->
## License

Distributed under the GPL License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Stian Ingebrigtsen - si@colifast.no

![Colifast home page][Colifast]

Project Link: [https://github.com/Stianein/Colifast_ALARM](https://github.com/Stianein/Colifast_ALARM)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* This project started as a bachelor project for students at the University of Oslo a special thanks to Julie Knapstad, Jon Sebastian Kaupang and Are Pettersen for their contributions.
* This Readme was made using [this](https://github.com/othneildrew/Best-README-Template/blob/main/BLANK_README.md) readme template, by [othneildrew](https://github.com/othneildrew/).
* Lexilla


License for Lexilla, Scintilla, and SciTE

Copyright 1998-2021 by Neil Hodgson <neilh@scintilla.org>

All Rights Reserved

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation.

NEIL HODGSON DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS, IN NO EVENT SHALL NEIL HODGSON BE LIABLE FOR ANY
SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE
OR PERFORMANCE OF THIS SOFTWARE.


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Stianein/Colifast_ALARM.svg?style=for-the-badge
[contributors-url]: https://github.com/Stianein/Colifast_ALARM/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Stianein/Colifast_ALARM.svg?style=for-the-badge
[forks-url]: https://github.com/Stianein/Colifast_ALARM/network/members
[stars-shield]: https://img.shields.io/github/stars/Stianein/Colifast_ALARM.svg?style=for-the-badge
[stars-url]: https://github.com/Stianein/Colifast_ALARM/stargazers
[issues-shield]: https://img.shields.io/github/issues/Stianein/Colifast_ALARM.svg?style=for-the-badge
[issues-url]: https://github.com/Stianein/Colifast_ALARM/issues
[license-shield]: https://img.shields.io/github/license/Stianein/Colifast_ALARM.svg?style=for-the-badge
[license-url]: https://github.com/Stianein/Colifast_ALARM/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username

[readme-template]: https://github.com/othneildrew/Best-README-Template/blob/main/BLANK_README.md
[readme-creator]: https://github.com/othneildrew/

[Colifast]: https://www.colifast.no
[Colifast-linkedin]: https://www.linkedin.com/company/colifast


[Documentation]: link_here