# SunMoon
This plugin is based on [pyephem](https://rhodesmill.org/pyephem/index.html), an astronomy library for Python.

## Prerequisites
Install [ephem](https://rhodesmill.org/pyephem/index.html) in a directory used by the Domoticz Python plugins, eg:
```
sudo pip3 install ephem
```
## Parameters
None

Default location specified in Domoticz is used.

## Devices
The following devices are displayed:

| Name                      | Description
| :---                      | :---
| **Sunrise**               | Today sunrise time today
| **Sunrise civil**         | Today sunrise civil time today
| **Sunrise nautical**      | Today sunrise nautical time today
| **Sunrise astronomical**  | Today sunrise astronomical time today
| **Sunset**                | Today sunset time today
| **Sunset civil**          | Today sunset civil time today
| **Sunset nautical**       | Today sunset nautical time today
| **Sunset astronomical**   | Today sunset astronomical time today
| **Sun azimuth**           | The horizontal direction of the sun in the sky
| **Sun altitude**          | The angle between the sun and the horizon
| **Sun distance**          | Distance to the sun in km
| **Sun transit**           | Today's time sun at highest point
| **Daylength**             | Daylength in minutes
| **Daylength**             | Daylength in hours:minutes
| **Moonrise**              | Moonrise time
| **Moonset**               | Moonset time
| **Moon azimuth**          | The horizontal direction of the moon in the sky
| **Moon altitude**         | The angle between the moon and the horizon
| **Moon distance**         | Distance to the moon in km
| **Moon phase** (*)        | Name of moonphase  "New moon", "Waxing crescent", "First quarter",    "Waxing gibbous", "Full moon", "Waning gibbous", "Last quarter", or "Waning crescent"
| **Next new moon**         | Date time of the next new moon
| **Next first quarter**    | Date time of the next first quarter
| **Next full moon**        | Date time of the next full moon
| **Next last quarter**     | Date time of the next last quarter
| **Moon illumination** (*) | Moon phase in % of surface illuminated

(*) The devices **Moon phase** and **Moon illumination** also display the moonphase with an icon. The following icons will be displayed:

| Icon | Description |
| :--- | :---        |
| ![New moon](https://github.com/Xorfor/Domoticz-SunMoon-Plugin/blob/master/images/xfr_sunmoon_phase048_On.png) | New moon |
| ![Waxing crescent](https://github.com/Xorfor/Domoticz-SunMoon-Plugin/blob/master/images/xfr_sunmoon_phase148_On.png) | Waxing crescent |
| ![First quarter](https://github.com/Xorfor/Domoticz-SunMoon-Plugin/blob/master/images/xfr_sunmoon_phase248_On.png) | First quarter |
| ![Waxing gibbous](https://github.com/Xorfor/Domoticz-SunMoon-Plugin/blob/master/images/xfr_sunmoon_phase348_On.png) | Waxing gibbous |
| ![Full moon](https://github.com/Xorfor/Domoticz-SunMoon-Plugin/blob/master/images/xfr_sunmoon_phase448_On.png) | Full moon |
| ![Waning gibbous](https://github.com/Xorfor/Domoticz-SunMoon-Plugin/blob/master/images/xfr_sunmoon_phase548_On.png) | Waning gibbous |
| ![Last quarter](https://github.com/Xorfor/Domoticz-SunMoon-Plugin/blob/master/images/xfr_sunmoon_phase648_On.png) | Last quarter |
| ![Waning crescent](https://github.com/Xorfor/Domoticz-SunMoon-Plugin/blob/master/images/xfr_sunmoon_phase748_On.png) | Waning crescent |


![devices](https://github.com/Xorfor/Domoticz-SunMoon-Plugin/blob/master/images/devices.jpg)
