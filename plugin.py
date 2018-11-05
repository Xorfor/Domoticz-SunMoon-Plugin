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
import math
import ephem


class BasePlugin:

    __DEBUG_NONE = 0
    __DEBUG_ALL = 1

    __HEARTBEATS2MIN = 6
    __MINUTES = 1

    # Device units
    __UNIT_SUN_AZ = 1
    __UNIT_SUN_ALT = 2
    __UNIT_SUN_DIST = 3
    __UNIT_MOON_AZ = 4
    __UNIT_MOON_ALT = 5
    __UNIT_MOON_DIST = 6
    __UNIT_MOON_PHASE = 7

    __UNITS = [
        # Unit, Name, Type, Subtype, Options, Used
        [__UNIT_SUN_AZ, "Sun Azimuth", 243, 31, {"Custom": "0;°"}, 1],
        [__UNIT_SUN_ALT, "Sun Altitude", 243, 31, {"Custom": "0;°"}, 1],
        [__UNIT_SUN_DIST, "Sun Distance", 243, 31, {"Custom": "0;km"}, 1],
        [__UNIT_MOON_AZ, "Moon Azimuth", 243, 31, {"Custom": "0;°"}, 1],
        [__UNIT_MOON_ALT, "Moon Altitude", 243, 31, {"Custom": "0;°"}, 1],
        [__UNIT_MOON_DIST, "Moon Distance", 243, 31, {"Custom": "0;km"}, 1],
        [__UNIT_MOON_PHASE, "Moon Phase", 243, 31, {"Custom": "0;%"}, 1],
    ]

    def __init__(self):
        self.__runAgain = 0

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug(
            "onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onDeviceAdded(self, Unit):
        Domoticz.Debug("onDeviceAdded called for Unit " + str(Unit))

    def onDeviceModified(self, Unit):
        Domoticz.Debug("onDeviceModified called for Unit " + str(Unit))

    def onDeviceRemoved(self, Unit):
        Domoticz.Debug("onDeviceRemoved called for Unit " + str(Unit))

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(self.__DEBUG_ALL)
        else:
            Domoticz.Debugging(self.__DEBUG_NONE)

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
        self.__sun = ephem.Sun()
        self.__moon = ephem.Moon()

        # Create devices
        if len(Devices) == 0:
            # Following devices are set on used by default
            for unit in self.__UNITS:
                Domoticz.Device(Unit=unit[0],
                                Name=unit[1],
                                Type=unit[2],
                                Subtype=unit[3],
                                Options=unit[4],
                                Used=unit[5]).Create()

        # Log config
        DumpAllToLog()

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
            Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            self.__runAgain = self.__HEARTBEATS2MIN * self.__MINUTES
            self.__observer.date = datetime.datetime.utcnow()
            Domoticz.Debug("DT: {}".format(self.__observer.date))
            # Sun data
            self.__sun.compute(self.__observer)
            alt = round(math.degrees(self.__sun.alt), 2)
            az = round(math.degrees(self.__sun.az), 2)
            dist = round(self.__sun.earth_distance * ephem.meters_per_au / 1000)
            Domoticz.Debug("Sun data: {} / {}".format(alt, az))
            UpdateDevice(self.__UNIT_SUN_ALT, int(alt), str(alt))
            UpdateDevice(self.__UNIT_SUN_AZ, int(az), str(az))
            UpdateDevice(self.__UNIT_SUN_DIST, int(dist), str(dist))
            # Moon data
            self.__moon.compute(self.__observer)
            alt = round(math.degrees(self.__moon.alt), 2)
            az = round(math.degrees(self.__moon.az), 2)
            dist = round(self.__moon.earth_distance * ephem.meters_per_au / 1000)
            Domoticz.Debug("Phase: {}".format(self.__moon.moon_phase))
            phase = round(self.__moon.moon_phase * 100, 1)
            UpdateDevice(self.__UNIT_MOON_ALT, int(alt), str(alt))
            UpdateDevice(self.__UNIT_MOON_AZ, int(az), str(az))
            UpdateDevice(self.__UNIT_MOON_DIST, int(dist), str(dist))
            UpdateDevice(self.__UNIT_MOON_PHASE, int(phase), str(phase))
            # Data not able to show
            prev_sun_rise = ephem.localtime(self.__observer.previous_rising(
                ephem.Sun()))
            Domoticz.Debug("Sun prev rise: {}".format(prev_sun_rise))
            prev_sun_trans = ephem.localtime(self.__observer.previous_transit(
                ephem.Sun()))
            Domoticz.Debug("Sun prev trans: {}".format(prev_sun_trans))
            prev_sun_set = ephem.localtime(self.__observer.previous_setting(
                ephem.Sun()))
            Domoticz.Debug("Sun previous set: {}".format(prev_sun_set))
            #
            next_sun_rise = ephem.localtime(self.__observer.next_rising(
                ephem.Sun()))
            Domoticz.Debug("Sun next rise: {}".format(next_sun_rise))
            next_sun_trans = ephem.localtime(self.__observer.next_transit(
                ephem.Sun()))
            Domoticz.Debug("Sun next trans: {}".format(next_sun_trans))
            next_sun_set = ephem.localtime(self.__observer.next_setting(
                ephem.Sun()))
            Domoticz.Debug("Sun next set: {}".format(next_sun_set))
            #
            moon_rise = ephem.localtime(
                self.__observer.previous_rising(ephem.Moon()))
            Domoticz.Debug("Moon rise: {}".format(moon_rise))
            moon_set = ephem.localtime(self.__observer.next_setting(
                ephem.Moon()))
            Domoticz.Debug("Moon set: {}".format(moon_set))
        else:
            Domoticz.Debug(
                "onHeartbeat called, run again in {} heartbeats.".format(self.__runAgain))


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
    _plugin.onNotification(Name, Subject, Text, Status,
                           Priority, Sound, ImageFile)


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
            "Device Type..........: {} / {}".format(Devices[x].Type, Devices[x].SubType))
        Domoticz.Debug("Device Name..........: '{}'".format(Devices[x].Name))
        Domoticz.Debug("Device nValue........: {}".format(Devices[x].nValue))
        Domoticz.Debug("Device sValue........: '{}'".format(Devices[x].sValue))
        Domoticz.Debug(
            "Device Options.......: '{}'".format(Devices[x].Options))
        Domoticz.Debug("Device Used..........: {}".format(Devices[x].Used))
        Domoticz.Debug(
            "Device ID............: '{}'".format(Devices[x].DeviceID))
        Domoticz.Debug("Device LastLevel.....: {}".format(
            Devices[x].LastLevel))
        Domoticz.Debug("Device Image.........: {}".format(Devices[x].Image))


def DumpImagesToLog():
    # Show images
    Domoticz.Debug("Image count..........: " + str(len(Images)))
    for x in Images:
        Domoticz.Debug("Image '" + x + "...': '" + str(Images[x]) + "'")


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
                Domoticz.Debug(
                    "....'" + x + " (" + str(len(httpDict[x])) + "):")
                for y in httpDict[x]:
                    Domoticz.Debug("........'" + y + "':'" +
                                   str(httpDict[x][y]) + "'")
            else:
                Domoticz.Debug("....'" + x + "':'" + str(httpDict[x]) + "'")


def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[
                Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(
                nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            # Domoticz.Debug("Update {}: {} - '{}'".format(Devices[Unit].Name, nValue, sValue))


def UpdateDeviceOptions(Unit, Options={}):
    if Unit in Devices:
        if Devices[Unit].Options != Options:
            Devices[Unit].Update(nValue=Devices[Unit].nValue,
                                 sValue=Devices[Unit].sValue, Options=Options)
            Domoticz.Debug("Device Options update: " +
                           Devices[Unit].Name + " = " + str(Options))


def UpdateDeviceImage(Unit, Image):
    if Unit in Devices and Image in Images:
        if Devices[Unit].Image != Images[Image].ID:
            Devices[Unit].Update(nValue=Devices[Unit].nValue,
                                 sValue=Devices[Unit].sValue, Image=Images[Image].ID)
            Domoticz.Debug("Device Image update: " +
                           Devices[Unit].Name + " = " + str(Images[Image].ID))
