#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
<plugin key="xfr_sunmoon" name="SunMoon" author="Xorfor" version="1.0.0">
    <params>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import datetime
from math import degrees as deg
import sys
from enum import IntEnum, unique  # , auto

try:
    import ephem
except:
    pass


@unique
class used(IntEnum):
    """
    Constants which can be used to create the devices. Look at onStart where
    the devices are created.
        used.NO, the user has to add this device manually
        used.YES, the device will be directly available
    """

    NO = 0
    YES = 1


class images:
    PREFIX_IMAGE = "xfr_sunmoon_"
    PREFIX_PHASE = "phase"
    #
    SUN = PREFIX_IMAGE + "sun"
    SUNRISE = PREFIX_IMAGE + "sunrise"
    SUNSET = PREFIX_IMAGE + "sunset"
    MOON = PREFIX_IMAGE + "moon"
    MOONRISE = PREFIX_IMAGE + "moonrise"
    MOONSET = PREFIX_IMAGE + "moonset"
    MOONPHASE0 = MOONNEW = PREFIX_IMAGE + PREFIX_PHASE + "0"  # New moon
    MOONPHASE1 = PREFIX_IMAGE + PREFIX_PHASE + "1"  # Waxing crescent
    MOONPHASE2 = MOONFIRSTQUARTER = PREFIX_IMAGE + PREFIX_PHASE + "2"  # First quarter
    MOONPHASE3 = PREFIX_IMAGE + PREFIX_PHASE + "3"  # Waxing gibbous
    MOONPHASE4 = MOONFULL = PREFIX_IMAGE + PREFIX_PHASE + "4"  # Full moon
    MOONPHASE5 = PREFIX_IMAGE + PREFIX_PHASE + "5"  # Waning gibbous
    MOONPHASE6 = MOONLASTQUARTER = PREFIX_IMAGE + PREFIX_PHASE + "6"  # Last quarter
    MOONPHASE7 = PREFIX_IMAGE + PREFIX_PHASE + "7"  # Waning crescent
    ALL = {
        SUN,
        SUNRISE,
        SUNSET,
        MOON,
        MOONRISE,
        MOONSET,
        MOONPHASE0,
        MOONPHASE1,
        MOONPHASE2,
        MOONPHASE3,
        MOONPHASE4,
        MOONPHASE5,
        MOONPHASE6,
        MOONPHASE7,
    }


@unique
class unit(IntEnum):
    """
    Device Unit numbers

    Define here your units numbers. These can be used to update your devices.
    Be sure the these have a unique number!
    """

    SUN_RISE = 1
    SUN_RISE_CIVIL = 2
    SUN_RISE_NAUTICAL = 3
    SUN_RISE_ASTRONOMICAL = 4
    SUN_TRANSIT = 5
    SUN_SET = 6
    SUN_SET_CIVIL = 7
    SUN_SET_NAUTICAL = 8
    SUN_SET_ASTRONOMICAL = 9
    SUN_AZ = 10
    SUN_ALT = 11
    SUN_DIST = 12
    #
    DAY_LENGTH_M = 18
    DAY_LENGTH_T = 19
    #
    MOON_RISE = 20
    MOON_SET = 21
    MOON_AZ = 22
    MOON_ALT = 23
    MOON_DIST = 24
    MOON_PHASE = 25
    MOON_NEXT_NEW = 26
    MOON_NEXT_FIRST_QUARTER = 27
    MOON_NEXT_FULL = 28
    MOON_NEXT_LAST_QUARTER = 29
    MOON_ILLUMINATION = 30


class BasePlugin:

    __DEBUG_NONE = 0
    __DEBUG_ALL = 1

    __HEARTBEATS2MIN = 6
    __MINUTES = 1

    __SEC30 = datetime.timedelta(seconds=30)
    __D_FORMAT = "%Y-%m-%d"
    __T_FORMAT = "%H:%M"
    __DT_FORMAT = "{} {}".format(__D_FORMAT, __T_FORMAT)

    # Twilights, their horizons and whether to use the centre of the Sun or not
    __TWILIGHTS = [("0", False), ("-6", True), ("-12", True), ("-18", True)]

    # Device units
    __UNITS = [
        # Unit, Name, Type, Subtype, Options, Used, image
        [unit.SUN_RISE, "Sunrise", 243, 19, {}, used.YES, images.SUNRISE],
        [unit.SUN_RISE_CIVIL, "Sunrise civil", 243, 19, {}, used.YES, images.SUNRISE],
        [
            unit.SUN_RISE_NAUTICAL,
            "Sunrise nautical",
            243,
            19,
            {},
            used.YES,
            images.SUNRISE,
        ],
        [
            unit.SUN_RISE_ASTRONOMICAL,
            "Sunrise astronomical",
            243,
            19,
            {},
            used.YES,
            images.SUNRISE,
        ],
        [unit.SUN_SET, "Sunset", 243, 19, {}, used.YES, images.SUNSET],
        [unit.SUN_SET_CIVIL, "Sunset civil", 243, 19, {}, used.YES, images.SUNSET],
        [
            unit.SUN_SET_NAUTICAL,
            "Sunset nautical",
            243,
            19,
            {},
            used.YES,
            images.SUNSET,
        ],
        [
            unit.SUN_SET_ASTRONOMICAL,
            "Sunset astronomical",
            243,
            19,
            {},
            used.YES,
            images.SUNSET,
        ],
        [
            unit.SUN_ALT,
            "Sun Altitude",
            243,
            31,
            {"Custom": "0;°"},
            used.YES,
            images.SUN,
        ],
        [
            unit.SUN_AZ,
            "Sun Azimuth",
            243,
            31,
            {"Custom": "0;°"},
            used.YES,
            images.SUN,
        ],
        [
            unit.SUN_DIST,
            "Sun Distance",
            243,
            31,
            {"Custom": "0;km"},
            used.YES,
            images.SUN,
        ],
        [unit.SUN_TRANSIT, "Sun transit", 243, 19, {}, used.YES, images.SUN],
        [
            unit.DAY_LENGTH_M,
            "Day length",
            243,
            31,
            {"Custom": "0;min"},
            used.YES,
            images.SUN,
        ],
        [unit.DAY_LENGTH_T, "Daylength", 243, 19, {}, used.YES, images.SUN],
        #
        [unit.MOON_RISE, "Moon rise", 243, 19, {}, used.YES, images.MOONRISE],
        [unit.MOON_SET, "Moon set", 243, 19, {}, used.YES, images.MOONSET],
        [
            unit.MOON_AZ,
            "Moon Azimuth",
            243,
            31,
            {"Custom": "0;°"},
            used.YES,
            images.MOON,
        ],
        [
            unit.MOON_ALT,
            "Moon Altitude",
            243,
            31,
            {"Custom": "0;°"},
            used.YES,
            images.MOON,
        ],
        [
            unit.MOON_DIST,
            "Moon Distance",
            243,
            31,
            {"Custom": "0;km"},
            used.YES,
            images.MOON,
        ],
        [unit.MOON_PHASE, "Moon Phase", 243, 19, {}, used.YES, images.MOON],
        [unit.MOON_NEXT_NEW, "Next new moon", 243, 19, {}, used.YES, images.MOONNEW],
        [
            unit.MOON_NEXT_FIRST_QUARTER,
            "Next first quarter",
            243,
            19,
            {},
            used.YES,
            images.MOONFIRSTQUARTER,
        ],
        [unit.MOON_NEXT_FULL, "Next full moon", 243, 19, {}, used.YES, images.MOONFULL],
        [
            unit.MOON_NEXT_LAST_QUARTER,
            "Next last quarter",
            243,
            19,
            {},
            used.YES,
            images.MOONLASTQUARTER,
        ],
        [
            unit.MOON_ILLUMINATION,
            "Moon Illumination",
            243,
            31,
            {"Custom": "0;%"},
            used.YES,
            images.MOON,
        ],
    ]
    __MOON_PHASE_DESCRIPTIONS = [
        "New moon",
        "Waxing crescent",
        "First quarter",
        "Waxing gibbous",
        "Full moon",
        "Waning gibbous",
        "Last quarter",
        "Waning crescent",
    ]

    def __init__(self):
        self.__runAgain = 0
        if "ephem" in sys.modules:
            self.__ephem_exist = True
        else:
            self.__ephem_exist = False

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand: {}, {}, {}, {}".format(Unit, Command, Level, Hue))

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug(
            "onConnect: {}, {}, {}".format(Connection.Name, Status, Description)
        )

    def onDeviceAdded(self, Unit):
        Domoticz.Debug("onDeviceAdded: {}".format(Unit))

    def onDeviceModified(self, Unit):
        Domoticz.Debug("onDeviceModified: {}".format(Unit))

    def onDeviceRemoved(self, Unit):
        Domoticz.Debug("onDeviceRemoved: {}".format(Unit))

    def onStart(self):
        Domoticz.Debug("onStart")
        if not self.__ephem_exist:
            Domoticz.Error("Ephem not available")
            return False
        #
        # Parameters
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(self.__DEBUG_ALL)
        else:
            Domoticz.Debugging(self.__DEBUG_NONE)
        #
        # Get Domoticz location
        loc = Settings["Location"].split(";")
        self.__lat = loc[0]
        self.__lon = loc[1]
        if self.__lat is None or self.__lon is None:
            Domoticz.Error("Unable to parse coordinates")
            return False
        self.__observer = ephem.Observer()
        self.__observer.lat = self.__lat
        self.__observer.lon = self.__lon
        self.__observer.date = datetime.datetime.utcnow()
        self.__sun = ephem.Sun()
        self.__moon = ephem.Moon()
        #
        # Load images
        # Check if images are in database
        for image in images.ALL:
            if image not in Images:
                zip = "{}.zip".format(image)
                Domoticz.Image(zip).Create()
        #
        # Create devices
        for unit in self.__UNITS:
            if unit[0] not in Devices:
                Domoticz.Device(
                    Unit=unit[0],
                    Name=unit[1],
                    Type=unit[2],
                    Subtype=unit[3],
                    Options=unit[4],
                    Used=unit[5],
                    Image=Images[unit[6]].ID,
                ).Create()
        # Log config
        DumpAllToLog()

    def onStop(self):
        Domoticz.Debug("onStop")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage: {}, {}".format(Connection.Name, Data))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug(
            "onNotification: {}, {}, {}, {}, {}, {}, {}".format(
                Name, Subject, Text, Status, Priority, Sound, ImageFile
            )
        )

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect: {}".format(Connection.Name))

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat")
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            self.__runAgain = self.__HEARTBEATS2MIN * self.__MINUTES
            #
            utc_now = datetime.datetime.utcnow()
            target_date = datetime.datetime.now().date()
            #
            self.__observer.date = utc_now
            self.__sun.compute(self.__observer)
            #
            ################################################################################
            # Sun data
            ################################################################################
            #
            # -------------------------------------------------------------------------------
            # Sun altitude
            # -------------------------------------------------------------------------------
            value = round(deg(self.__sun.alt), 2)
            UpdateDevice(unit.SUN_ALT, int(value), str(value))
            #
            # -------------------------------------------------------------------------------
            # Sun azimuth
            # -------------------------------------------------------------------------------
            value = round(deg(self.__sun.az), 2)
            UpdateDevice(unit.SUN_AZ, int(value), str(value))
            #
            # -------------------------------------------------------------------------------
            # Sun distance
            # -------------------------------------------------------------------------------
            value = round(self.__sun.earth_distance * ephem.meters_per_au / 1000)
            UpdateDevice(unit.SUN_DIST, int(value), str(value))
            #
            # -------------------------------------------------------------------------------
            # Sun transit
            # -------------------------------------------------------------------------------
            value = (
                ephem.localtime(self.__observer.next_transit(self.__sun)) + self.__SEC30
            )
            UpdateDevice(
                unit.SUN_TRANSIT, 0, "{}".format(value.strftime(self.__DT_FORMAT))
            )
            #
            # -------------------------------------------------------------------------------
            # Sun rise & set today
            # -------------------------------------------------------------------------------
            self.__observer.date = target_date
            self.__sun.compute(self.__observer)
            i = 0
            for t in self.__TWILIGHTS:
                # Zero the horizon
                self.__observer.horizon = t[0]
                next_rising = (
                    ephem.localtime(
                        self.__observer.next_rising(self.__sun, use_center=t[1])
                    )
                    + self.__SEC30
                )
                UpdateDevice(
                    unit.SUN_RISE + i,
                    0,
                    "{}".format(next_rising.strftime(self.__DT_FORMAT)),
                )
                next_setting = (
                    ephem.localtime(
                        self.__observer.next_setting(self.__sun, use_center=t[1])
                    )
                    + self.__SEC30
                )
                UpdateDevice(
                    unit.SUN_SET + i,
                    0,
                    "{}".format(next_setting.strftime(self.__DT_FORMAT)),
                )
                if i == 0:
                    value = (next_setting - next_rising).total_seconds()
                    hh = divmod(value, 3600)
                    mm = divmod(hh[1], 60)
                    min = int(divmod(value, 60)[0])
                    UpdateDevice(
                        unit.DAY_LENGTH_M,
                        min,
                        "{}".format(min),
                    )
                    UpdateDevice(
                        unit.DAY_LENGTH_T,
                        0,
                        "{:02}:{:02}".format(int(hh[0]),int(mm[0])),
                    )

                i += 1
            #
            # Reset horizon for further calculations
            self.__observer.horizon = "0"
            #
            ################################################################################
            # Moon data
            ################################################################################
            #
            self.__observer.date = utc_now
            self.__moon.compute(self.__observer)
            #
            # -------------------------------------------------------------------------------
            # Moon rise
            # -------------------------------------------------------------------------------
            value = (
                ephem.localtime(self.__observer.next_rising(self.__moon)) + self.__SEC30
            )
            UpdateDevice(
                unit.MOON_RISE, 0, "{}".format(value.strftime(self.__DT_FORMAT))
            )
            #
            # -------------------------------------------------------------------------------
            # Moon set
            # -------------------------------------------------------------------------------
            value = (
                ephem.localtime(self.__observer.next_setting(self.__moon))
                + self.__SEC30
            )
            UpdateDevice(
                unit.MOON_SET, 0, "{}".format(value.strftime(self.__DT_FORMAT))
            )
            #
            # -------------------------------------------------------------------------------
            # Moon altitude
            # -------------------------------------------------------------------------------
            self.__moon.compute(self.__observer)
            #
            value = round(deg(self.__moon.alt), 2)
            UpdateDevice(unit.MOON_ALT, int(value), str(value))
            #
            # -------------------------------------------------------------------------------
            # Moon azimuth
            # -------------------------------------------------------------------------------
            value = round(deg(self.__moon.az), 2)
            UpdateDevice(unit.MOON_AZ, int(value), str(value))
            #
            # -------------------------------------------------------------------------------
            # Moon distance
            # -------------------------------------------------------------------------------
            value = round(self.__moon.earth_distance * ephem.meters_per_au / 1000)
            UpdateDevice(unit.MOON_DIST, int(value), str(value))
            #
            # -------------------------------------------------------------------------------
            # Next new moon
            # -------------------------------------------------------------------------------
            next_new = ephem.localtime(ephem.next_new_moon(utc_now))
            value = next_new + self.__SEC30
            UpdateDevice(
                unit.MOON_NEXT_NEW, 0, "{}".format(value.strftime(self.__DT_FORMAT))
            )
            #
            # -------------------------------------------------------------------------------
            # Next first quarter
            # -------------------------------------------------------------------------------
            next_first_quarter = ephem.localtime(ephem.next_first_quarter_moon(utc_now))
            value = next_first_quarter + self.__SEC30
            UpdateDevice(
                unit.MOON_NEXT_FIRST_QUARTER,
                0,
                "{}".format(value.strftime(self.__DT_FORMAT)),
            )
            #
            # -------------------------------------------------------------------------------
            # Next full moon
            # -------------------------------------------------------------------------------
            next_full = ephem.localtime(ephem.next_full_moon(utc_now))
            value = next_full + self.__SEC30
            UpdateDevice(
                unit.MOON_NEXT_FULL,
                0,
                "{}".format(value.strftime(self.__DT_FORMAT)),
            )
            #
            # -------------------------------------------------------------------------------
            # Next last quarter
            # -------------------------------------------------------------------------------
            next_last_quarter = ephem.localtime(ephem.next_last_quarter_moon(utc_now))
            value = next_last_quarter + self.__SEC30
            UpdateDevice(
                unit.MOON_NEXT_LAST_QUARTER,
                0,
                "{}".format(value.strftime(self.__DT_FORMAT)),
            )
            #
            # -------------------------------------------------------------------------------
            # Moon phase
            # -------------------------------------------------------------------------------
            next_full = next_full.date()
            next_new = next_new.date()
            next_last_quarter = next_last_quarter.date()
            next_first_quarter = next_first_quarter.date()
            previous_full = ephem.localtime(ephem.previous_full_moon(utc_now)).date()
            previous_new = ephem.localtime(ephem.previous_new_moon(utc_now)).date()
            previous_last_quarter = ephem.localtime(
                ephem.previous_last_quarter_moon(utc_now)
            ).date()
            previous_first_quarter = ephem.localtime(
                ephem.previous_first_quarter_moon(utc_now)
            ).date()
            #
            # Domoticz.Debug("target_date: {}".format(target_date))
            # Domoticz.Debug("next_full: {}".format(next_full))
            # Domoticz.Debug("next_new: {}".format(next_new))
            # Domoticz.Debug("next_last_quarter: {}".format(next_last_quarter))
            # Domoticz.Debug("next_first_quarter: {}".format(next_first_quarter))
            # Domoticz.Debug("previous_full: {}".format(previous_full))
            # Domoticz.Debug("previous_new: {}".format(previous_new))
            # Domoticz.Debug("previous_last_quarter: {}".format(previous_last_quarter))
            # Domoticz.Debug("previous_first_quarter: {}".format(previous_first_quarter))

            if target_date in (next_new, previous_new):
                phase = 0
            elif target_date in (next_first_quarter, previous_first_quarter):
                phase = 2
            elif target_date in (next_full, previous_full):
                phase = 4
            elif target_date in (next_last_quarter, previous_last_quarter):
                phase = 6
            elif (
                previous_new
                < next_first_quarter
                < next_full
                < next_last_quarter
                < next_new
            ):
                phase = 1
            elif (
                previous_first_quarter
                < next_full
                < next_last_quarter
                < next_new
                < next_first_quarter
            ):
                phase = 3
            elif (
                previous_full
                < next_last_quarter
                < next_new
                < next_first_quarter
                < next_full
            ):
                phase = 5
            elif (
                previous_last_quarter
                < next_new
                < next_first_quarter
                < next_full
                < next_last_quarter
            ):
                phase = 7
            else:
                phase = 4
            UpdateDevice(unit.MOON_PHASE, 0, self.__MOON_PHASE_DESCRIPTIONS[phase])
            UpdateDeviceImage(
                unit.MOON_PHASE, images.PREFIX_IMAGE + images.PREFIX_PHASE + str(phase)
            )
            #
            self.__moon.compute(self.__observer)
            #
            # -------------------------------------------------------------------------------
            # Moon illumination
            # -------------------------------------------------------------------------------
            value = round(deg(self.__moon.moon_phase), 2)
            UpdateDevice(unit.MOON_ILLUMINATION, int(value), str(value))
            UpdateDeviceImage(
                unit.MOON_ILLUMINATION,
                images.PREFIX_IMAGE + images.PREFIX_PHASE + str(phase),
            )
            #
        else:
            Domoticz.Debug(
                "onHeartbeat called, run again in {} heartbeats.".format(
                    self.__runAgain
                )
            )


global _plugin
_plugin = BasePlugin()


def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onDeviceAdded(Unit):
    global _plugin
    _plugin.onDeviceAdded(Unit)


def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)


def onDeviceRemoved(Unit):
    global _plugin
    _plugin.onDeviceRemoved(Unit)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


################################################################################
# Generic helper functions
################################################################################
def DumpDevicesToLog():
    # Show devices
    Domoticz.Debug("Device count.........: {}".format(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device...............: {} - {}".format(x, Devices[x]))
        Domoticz.Debug("Device Idx...........: {}".format(Devices[x].ID))
        Domoticz.Debug(
            "Device Type..........: {} / {}".format(Devices[x].Type, Devices[x].SubType)
        )
        Domoticz.Debug("Device Name..........: '{}'".format(Devices[x].Name))
        Domoticz.Debug("Device nValue........: {}".format(Devices[x].nValue))
        Domoticz.Debug("Device sValue........: '{}'".format(Devices[x].sValue))
        Domoticz.Debug("Device Options.......: '{}'".format(Devices[x].Options))
        Domoticz.Debug("Device Used..........: {}".format(Devices[x].Used))
        Domoticz.Debug("Device ID............: '{}'".format(Devices[x].DeviceID))
        Domoticz.Debug("Device LastLevel.....: {}".format(Devices[x].LastLevel))
        Domoticz.Debug("Device Image.........: {}".format(Devices[x].Image))


def DumpImagesToLog():
    # Show images
    Domoticz.Debug("Image count..........: {}".format((len(Images))))
    for x in Images:
        Domoticz.Debug("Image '{}'...: '{}'".format(x, Images[x]))


def DumpParametersToLog():
    # Show parameters
    Domoticz.Debug("Parameters count.....: {}".format(len(Parameters)))
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("Parameter '{}'...: '{}'".format(x, Parameters[x]))


def DumpSettingsToLog():
    # Show settings
    Domoticz.Debug("Settings count.......: {}".format(len(Settings)))
    for x in Settings:
        Domoticz.Debug("Setting '{}'...: '{}'".format(x, Settings[x]))


def DumpAllToLog():
    DumpDevicesToLog()
    DumpImagesToLog()
    DumpParametersToLog()
    DumpSettingsToLog()


def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Debug("HTTP Details (" + str(len(httpDict)) + "):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Debug("....'" + x + " (" + str(len(httpDict[x])) + "):")
                for y in httpDict[x]:
                    Domoticz.Debug("........'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Debug("....'" + x + "':'" + str(httpDict[x]) + "'")


def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    if Unit in Devices:
        if (
            Devices[Unit].nValue != nValue
            or Devices[Unit].sValue != sValue
            or Devices[Unit].TimedOut != TimedOut
            or AlwaysUpdate
        ):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            # Domoticz.Debug("Update {}: {} - '{}'".format(Devices[Unit].Name, nValue, sValue))


def UpdateDeviceOptions(Unit, Options={}):
    if Unit in Devices:
        if Devices[Unit].Options != Options:
            Devices[Unit].Update(
                nValue=Devices[Unit].nValue,
                sValue=Devices[Unit].sValue,
                Options=Options,
            )
            Domoticz.Debug(
                "Device Options update: {} = {}".format(Devices[Unit].Name, Options)
            )


def UpdateDeviceImage(Unit, Image):
    if Unit in Devices and Image in Images:
        if Devices[Unit].Image != Images[Image].ID:
            Devices[Unit].Update(
                nValue=Devices[Unit].nValue,
                sValue=Devices[Unit].sValue,
                Image=Images[Image].ID,
            )
            Domoticz.Debug(
                "Device Image update: {} = {}".format(
                    Devices[Unit].Name, Images[Image].ID
                )
            )
