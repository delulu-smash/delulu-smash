# How to Mod Switch

````{note}
All mods recommended are ones that are wifi safe (ie Nintendo won't detect when play online and brick/block switch)
````

# Pre Requisites

````{list-table}
:header-rows: 1

* - Link
  - Description
* - Modable Switch
  - Need older switch or make hardware changes to ensure modable (check if moddable via [link](https://www.youtube.com/watch?v=HRqm3SEH-Fs&t=1240s))
* - Physical RCM Jig
  - Small device that goes into joystick slot on switch that allows to mod (can buy on [amazon](https://www.amazon.com/RGEEK-Nintendo-Circuit-Archive-Simulator/dp/B07Q6YHRBM/ref=sr_1_1?crid=ASUBHUF9NP4G&dib=eyJ2IjoiMSJ9.EfGhx3NZTLDYN8azz1XQ0G4OSJP6mEe5GBx8mLu7e0E7T7ZmtxtjqCgoAYeYYlW76IXK-TYY4bzFatLadIwsLZYA69UWrBIMX9N9TEpESIk.6x3Jn7fy2BbsJsJt8BHWBzqWdz3E4dsBhQEoQD2DyRM&dib_tag=se&keywords=physical+RCM+jig&qid=1786934749&s=electronics&sprefix=physical+rcm+jig%2Celectronics%2C151&sr=1-1))
* - Micro SD
  - Where mod software and mods are stored on
````

# Download

````{list-table}
:header-rows: 1

* - Link
  - File
* - Row1_1
  - Row1_2
* - Row2_1
  - Row2_2
````

# Steps

````{list-table}
:header-rows: 1

* - Step
  - Description
* - 0
  - Ensure have [pre requisites](#pre-requisites)
* - 1
  - Plug micro SD card into computer
* - Step
  - Go to [Atmosphere (Latest Release)](https://github.com/atmosphere-nx/atmosphere/releases), download `atmosphere....zip`, move contents to micro SD card
* - Step
  - Go to [Hekate (Latest Release)](https://github.com/CTCaer/hekate/releases), download `hekate_ctcaer_...zip` move contents to micro SD card
* - Step
  - Go to [TegraRcmGUI (Latest Release)](https://github.com/eliboa/TegraRcmGUI/releases), download `TegraRcmGUI_....zip` (will be software use to install mods to switch)
* - Step
  - Go to [SD Preparation](https://switch.hacks.guide/user_guide/all/sd_preparation), click `hekate_ipl.ini` file (ie referenced as "hekate config file")
* - Step
  - Go to [Acropolis (Latest Release)](https://github.com/Raytwo/ARCropolis/releases/), download `release.zip`, move contents to micro SD card, hit "Merge" in prompt (not replace)
* - Step
  - Go to [Skyline (Latest Release)](https://github.com/skyline-dev/skyline/releases), download `skyline.zip`, move contents to micro SD card,
* - Step
  - Move contents of Step 3 into micro SD cards `atmosphere/contents/01006A800016E000` (Note: `01006A800016E000` is the smash ultimate game id)
* - Step
  - in micro SD, at root (ie outside of `atmosphere` folder), create folder `ultimate/mods`
* - Step
  - Go to [Ultimate Training Mod Pack (Latest Version)](https://github.com/jugeeya/UltimateTrainingModpack/releases#release-beta (ie release after `beta` release)), download `TrainingModpack.zip`
* - Step
  - Go to [SSBU Online Deluxe (Latest Release)](https://github.com/saad-script/ssbu-online-deluxe/releases/tag/v1.3.0), download  `ssbu-online-deluxe-....zip`
````

# Smash Ultimate Mods

````{list-table}
:header-rows: 1

* - Link
  - Description
* - [Skins](https://gamebanana.com/mods/cats/3330)
  - Cosmetic changes to skins/alts of characters (broken down by character), see [vod](https://youtu.be/HRqm3SEH-Fs?si=6UnDAirbChRJBqTh&t=873) how to add
* - Row2_1
  - Row2_2
````

# References

````{list-table} `
:header-rows: 1

* - Link
  - Description
* - [How to Mod Switch Vod 1](https://www.youtube.com/watch?v=r3FFUkzwWQI) [How to Mod Switch Vod 2](https://www.youtube.com/watch?v=HRqm3SEH-Fs&t=1240s)
  - How to make switch moddable and basics of Smash Ultimate Modding
* - [How to Update Mod Software](https://www.youtube.com/watch?v=vAULmYf5R4Y)
  - How to update existing mod software (Eg Acropolis/plugins)
* - [Full Switch Mod Guide](https://switch.hacks.guide)
  - Full community guide for modding switch in technical detail
````