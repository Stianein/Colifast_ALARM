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
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://www.colifast.no/">
    <img src="Images/Colifast_50pix_medium.png" alt="Logo" width="200" height="35">
  </a>

<h3 align="center">Software for Colifast ALARM</h3>

  <p align="center">
    project_description
    <br />
    <a href="https://github.com/Stianein/Colifast_ALARM"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Stianein/Colifast_ALARM">View Demo</a>
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

[![Software for Colifast ALARM][product-screenshot]](https://example.com)

In this project I have developed software for the Colifast ALARM instrument. We sought to take more control of the whole of the equipement, which measures fecal indicator bacteria in water recipients, see our web page for more info on it´s usecases.

Colifast is as of 2024 a low budget company, and open source is thus a reasonable strategy for our software. But sharing the source code may have som benefits to us too, it could help us navigate customer needs, and github can be a platform to handle future priorities of development. Aside from that maybe this project could work as a starting point for people who whish to develope software to communicate with the same or similar components used in the Colifast ALARM system. 

Off course I would be more than happy to have people participate on the development, to make the equipement even better, despite it being a commercially sold equipment, should they wish to. The software can be opened fine on a windows computer without the components connected, but it has not yet been time to make modules that simulate the function of the components. 

The equipment is not cross platform, as it utilizes components that are windows only components. 

`Stianein`, `Colifast_ALARM`, `twitter_handle`, `linkedin_username`, `email_client`, `email`, `project_title`, `project_description`

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* ![Python][Python.py][Python-url]
* ![Anaconda](https://img.shields.io/badge/Environment-Anaconda-blue.svg)


* ![Python](https://img.shields.io/badge/Python-3.11-blue.svg) [Python](https://www.python.org/) - Programming language used.
* ![Anaconda](https://img.shields.io/badge/Environment-Anaconda-blue.svg) [Anaconda](https://www.anaconda.com/) - Python distribution and package management.
* ![PyQt5](https://img.shields.io/badge/PyQt5-5.15.9-brightgreen.svg) [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) - GUI framework for creating the application interface.
* ![NumPy](https://img.shields.io/badge/NumPy-1.26.0-orange.svg) [NumPy](https://numpy.org/) - Numerical computations and array handling.
* ![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7.2-blue.svg) [Matplotlib](https://matplotlib.org/) - Plotting and data visualization.
* ![Seabreeze](https://img.shields.io/badge/Seabreeze-2.8.0-yellow.svg) [Seabreeze](https://pypi.org/project/Seabreeze/) - Interface for Ocean Optics spectrometers.
* ![PySerial](https://img.shields.io/badge/PySerial-3.5-yellowgreen.svg) [PySerial](https://pyserial.readthedocs.io/en/latest/) - Serial port communication library.
* ![Qt](https://img.shields.io/badge/Qt-5.15.8-green.svg) [Qt](https://www.qt.io/) - Cross-platform application framework.
* [Lexilla](https://github.com/ScintillaOrg/lexilla) - Lexilla is the library for syntax highlighting used by QScintilla.
* ![QScintilla](https://img.shields.io/badge/QScintilla-2.14.1-blue.svg) [QScintilla](https://riverbankcomputing.com/software/qscintilla/intro) - A Qt port of the Scintilla C++ editor component.
* [APScheduler](https://apscheduler.readthedocs.io/en/latest/) - Advanced Python Scheduler for scheduling tasks.

- **Standard Libraries**:
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

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3
    - [ ] Nested Feature

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

Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com

Project Link: [https://github.com/Stianein/Colifast_ALARM](https://github.com/Stianein/Colifast_ALARM)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

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

[product-screenshot]: images/screenshot.png
[Python.py]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[PyQt]: https://img.shields.io/badge/PyQt5-5.15.8-blue
[PyQt-url]: https://riverbankcomputing.com/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 