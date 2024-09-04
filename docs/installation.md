# Installation

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


The actual build of this equipment is not covered here, and also out of scope for this project. The growth medium used by the equipment is also patented and not freely availible. 