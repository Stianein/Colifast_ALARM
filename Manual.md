# Colifast ALARM Instrument Manual

**Developed by Stian Eide Ingebrigtsen for Colifast AS**

This software is intended to operate the Colifast ALARM Instrument with its components. Method files can be loaded to run different setups, and you can create files to conduct specific tasks utilizing the components in a customized manner.

## Getting Started

1. **Bottle Size Setup:**
   - Navigate to the **Bottle Size** menu and set the size of the medium bottle (typically 21 samples per bottle). 
   - This value is directly responsible for stopping the instrument when there is no medium left.
   - The medium progress bar will display the amount of medium remaining.
   - Ensure this value is correct, as the instrument will not allow a run to start if the remaining medium is set to zero.
   - Clicking the medium progress bar allows the user to register the installation of a new bottle.

   **Note:** You can order a bottle size that suits your frequency of medium bottle change. Most customers use a 21-day bottle for a 3-week change frequency. Volumes for 14 samples are also readily available. Ensure this setting is aligned with the bottle volume.

2. **Method Selection:**
   - Navigate to the **Method** section.
   - From the **Method File** drop-down menu, select the file you want the program to run.
   - Select the target bacteria group from the **Analysis** drop-down.
   - Set the frequency of samples:
     - Continuously
     - 24 hours intervals
     - 48 hours intervals
     - Custom interval (in days)

    - **Additional Options**
        
        | **Option**                    | **Explanation**                                                                                                                                                       |
        |--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
        | **Sodium Thiosulfate**         | Adds this chelator to the sample. It is used with chlorinated water sources, to "remove" chlorine, which could kill the target bacteria.                                                            |
        | **External Sample**            | Fills an external bottle with a sample for collection as a reference. Typically used when sending a sample to an accredited lab after a positive bacteria alarm. This option is mutually exclusive with the Alternate sample sources as it make use of the same channel.      |
        | **Alternate Sample Sources**   | Enables alternating between two sample sources. This option is mutually exclusive with the External sample as it make use of the same channel.                                            |
        | **Delay Before Start**         | Delays the starting point of the first sample, allowing the instrument to start at a specific time in the future.                                                     |
        | **Remote Start**               | Enables remote start/stop of the equipment by calling the modem.                                                                                                      |

## History

- In the **History** menu, you can plot historical data based on date. 
- **How to Use:**
  - Click on the date you wish to plot. Dates with sample data are highlighted in white. 
  - If multiple samples are available for a given date, the program will prompt you to select the starting time of the sample you want to plot.
  - You can plot several samples sequentially. Use the slider to select days or check the **plot samples from current run** option to display all samples from that specific run (based on the bottle size setting).

## Report

- In the **Reports** menu, you can generate reports:
  - Click the *create report* button to generate a report.
  - The report will be saved in the `C:\Colifast\Reports` folder on your local machine.


## Advanced

**Note:** We do not recommend operators to access this menu.

- The Advanced menu allows the components to be handled manually. 
- This is a feature for doing service on the equipment.
- The access is password protected, and that is simply to avoid messing with important sample runs. Some of the components are not set up to handle multithreading, and trying to access them whilest a method is running might halt the program.

#### ADU

- This page allows the user to manually turn on/off the relays of the **ADU208** relay unit. 
    - There is an *ADU Load* button for initializing and updating the ports of the ADU. 
    - There is a *Reset* button for turning all the relays off.
    - A *Status field* shows the status of the ADU (connected or not).
    - The *Test* button runs read and write calls to all the ports of the device

### Spectrometer



## Tips

- Stopping
    - The **Stop Button**  <img src="icons\square.svg" alt="stop button" style="width: 24px; height: auto; vertical-align: middle;">
  will abort the program imediately, only stalling if a component are midway through an operation. But if you wish to stop the run after the current sample has ended, right click the button and select `stop run after current sample has ended`.

---

Thank you for using the Colifast ALARM Instrument!
