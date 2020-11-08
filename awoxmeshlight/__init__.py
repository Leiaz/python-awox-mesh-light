from __future__ import unicode_literals

from . import packetutils as pckt

from os import urandom
from bluepy import btle
import logging
import struct
import time

# Commands :

#: Set mesh groups.
#: Data : 3 bytes  
C_MESH_GROUP = 0xd7

#: Set the mesh id. The light will still answer to the 0 mesh id. Calling the 
#: command again replaces the previous mesh id.
#: Data : the new mesh id, 2 bytes in little endian order
C_MESH_ADDRESS = 0xe0

#:
C_MESH_RESET = 0xe3

#: On/Off command. Data : one byte 0, 1
C_POWER = 0xd0

#: Data : one byte
C_LIGHT_MODE = 0x33

#: Data : one byte 0 to 6 
C_PRESET = 0xc8

#: White temperature. one byte 0 to 0x7f
C_WHITE_TEMPERATURE = 0xf0

#: one byte 1 to 0x7f 
C_WHITE_BRIGHTNESS = 0xf1

#: 4 bytes : 0x4 red green blue
C_COLOR = 0xe2

#: one byte : 0xa to 0x64 .... 
C_COLOR_BRIGHTNESS = 0xf2 

#: Data 4 bytes : How long a color is displayed in a sequence in milliseconds as 
#:   an integer in little endian order
C_SEQUENCE_COLOR_DURATION = 0xf5 

#: Data 4 bytes : Duration of the fading between colors in a sequence, in 
#:   milliseconds, as an integer in little endian order
C_SEQUENCE_FADE_DURATION = 0xf6 

#: 7 bytes
C_TIME = 0xe4

#: 10 bytes
C_ALARMS = 0xe5


PAIR_CHAR_UUID = '00010203-0405-0607-0809-0a0b0c0d1914'
COMMAND_CHAR_UUID = '00010203-0405-0607-0809-0a0b0c0d1912'
STATUS_CHAR_UUID = '00010203-0405-0607-0809-0a0b0c0d1911'
OTA_CHAR_UUID = '00010203-0405-0607-0809-0a0b0c0d1913'


logger = logging.getLogger (__name__)

class Delegate(btle.DefaultDelegate):
    def __init__(self, light):
        self.light = light
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        char = self.light.btdevice.getCharacteristics (cHandle)[0]
        if char.uuid == STATUS_CHAR_UUID:
            logger.info ("Notification on status char.")
            message = pckt.decrypt_packet (self.light.session_key, self.light.mac, data)
        else :
            logger.info ("Receiced notification from characteristic %s", char.uuid.getCommonName ())
            message = pckt.decrypt_packet (self.light.session_key, self.light.mac, data)
            logger.info ("Received message : %s", repr (message))
            

class AwoxMeshLight:
    def __init__ (self, mac, mesh_name = "unpaired", mesh_password = "1234"):
        """
        Args :
            mac: The light's MAC address as a string in the form AA:BB:CC:DD:EE:FF
            mesh_name: The mesh name as a string.
            mesh_password: The mesh password as a string.
        """
        self.mac = mac
        self.mesh_id = 0
        self.btdevice = btle.Peripheral ()
        self.session_key = None
        self.mesh_name = mesh_name.encode ()
        self.mesh_password = mesh_password.encode ()
        
        # Light status
        self.white_brightness = None
        self.white_temp = None
        self.red = None
        self.green = None
        self.blue = None

    def connect(self, mesh_name = None, mesh_password = None):
        """
        Args :
            mesh_name: The mesh name as a string.
            mesh_password: The mesh password as a string.
        """
        if mesh_name : self.mesh_name = mesh_name.encode ()
        if mesh_password : self.mesh_password = mesh_password.encode ()

        self.btdevice.connect (self.mac)
        self.btdevice.setDelegate (Delegate (self))
        pair_char = self.btdevice.getCharacteristics (uuid = PAIR_CHAR_UUID)[0]
        self.session_random = urandom(8)
        message = pckt.make_pair_packet (self.mesh_name, self.mesh_password, self.session_random)
        pair_char.write (message)
        
        status_char = self.btdevice.getCharacteristics (uuid = STATUS_CHAR_UUID)[0]
        status_char.write (b'\x01')

        reply = bytearray (pair_char.read ())
        if reply[0] == 0xd :
            self.session_key = pckt.make_session_key (self.mesh_name, self.mesh_password, \
                self.session_random, reply[1:9])
            logger.info ("Connected.")
            return True
        else :
            if reply[0] == 0xe :
                logger.info ("Auth error : check name and password.")
            else :
                logger.info ("Unexpected pair value : %s", repr (reply))
            self.disconnect ()
            return False
        
    def connectWithRetry(self, num_tries = 1, mesh_name = None, mesh_password = None):
        """
        Args:
           num_tries: The number of attempts to connect.
           mesh_name: The mesh name as a string.
           mesh_password: The mesh password as a string.
        """
        connected = False
        attempts = 0
        while (not connected and attempts < num_tries ):
            try:
                connected = self.connect(mesh_name, mesh_password)
            except btle.BTLEDisconnectError:
                logger.info("connection_error: retrying for %s time", attempts)
            finally:
                attempts += 1

        return connected

    def setMesh (self, new_mesh_name, new_mesh_password, new_mesh_long_term_key):
        """
        Sets or changes the mesh network settings.

        Args :
            new_mesh_name: The new mesh name as a string, 16 bytes max.
            new_mesh_password: The new mesh password as a string, 16 bytes max.
            new_mesh_long_term_key: The new long term key as a string, 16 bytes max.

        Returns :
            True on success.
        """
        assert (self.session_key)
        
        pair_char = self.btdevice.getCharacteristics (uuid = PAIR_CHAR_UUID)[0]

        # FIXME : Removing the delegate as a workaround to a bluepy.btle.BTLEException
        #         similar to https://github.com/IanHarvey/bluepy/issues/182 That may be
        #         a bluepy bug or I'm using it wrong or both ...
        self.btdevice.setDelegate (None)

        message = pckt.encrypt (self.session_key, new_mesh_name.encode ())
        message.insert (0, 0x4)
        pair_char.write (message)

        message = pckt.encrypt (self.session_key, new_mesh_password.encode ())
        message.insert (0, 0x5)
        pair_char.write (message)

        message = pckt.encrypt (self.session_key, new_mesh_long_term_key.encode ())
        message.insert (0, 0x6)
        pair_char.write (message)

        time.sleep (1)
        reply = bytearray (pair_char.read ())

        self.btdevice.setDelegate (Delegate (self))

        if reply[0] == 0x7 :
            self.mesh_name = new_mesh_name.encode ()
            self.mesh_password = new_mesh_password.encode ()
            logger.info ("Mesh network settings accepted.")
            return True
        else:
            logger.info ("Mesh network settings change failed : %s", repr(reply))
            return False

    def setMeshId (self, mesh_id):
        """
        Sets the mesh id.

        Args :
            mesh_id: as a number.

        """
        data = struct.pack ("<H", mesh_id)
        self.writeCommand (C_MESH_ADDRESS, data)
        self.mesh_id = mesh_id

    def writeCommand (self, command, data, dest = None):
        """
        Args:
            command: The command, as a number.
            data: The parameters for the command, as bytes.
            dest: The destination mesh id, as a number. If None, this lightbulb's
                mesh id will be used.
        """
        assert (self.session_key)
        if dest == None: dest = self.mesh_id
        packet = pckt.make_command_packet (self.session_key, self.mac, dest, command, data)
        command_char = self.btdevice.getCharacteristics (uuid=COMMAND_CHAR_UUID)[0]
        logger.info ("Writing command %i data %s", command, repr (data))
        command_char.write (packet)

    def resetMesh (self):
        """
        Restores the default name and password. Will disconnect the device.
        """
        self.writeCommand (C_MESH_RESET, b'\x00')

    def readStatus (self):
        status_char = self.btdevice.getCharacteristics (uuid = STATUS_CHAR_UUID)[0]
        packet = status_char.read ()
        return pckt.decrypt_packet (self.session_key, self.mac, packet)

    def setColor (self, red, green, blue):
        """
        Args :
            red, green, blue: between 0 and 0xff
        """
        data = struct.pack ('BBBB', 0x04, red, green, blue)
        self.writeCommand (C_COLOR, data)

    def setColorBrightness (self, brightness):
        """
        Args :
            brightness: a value between 0xa and 0x64 ...
        """
        data = struct.pack ('B', brightness)
        self.writeCommand (C_COLOR_BRIGHTNESS, data)

    def setSequenceColorDuration (self, duration):
        """
        Args :
            duration: in milliseconds.
        """
        data = struct.pack ("<I", duration)
        self.writeCommand (C_SEQUENCE_COLOR_DURATION, data)

    def setSequenceFadeDuration (self, duration):
        """
        Args:
            duration: in milliseconds.
        """
        data = struct.pack ("<I", duration)
        self.writeCommand (C_SEQUENCE_FADE_DURATION, data)

    def setPreset (self, num):
        """
        Set a preset color sequence.

        Args :
            num: number between 0 and 6
        """
        data = struct.pack('B', num)
        self.writeCommand (C_PRESET, data)

    def setWhite (self, temp, brightness):
        """
        Args :
            temp: between 0 and 0x7f
            brightness: between 1 and 0x7f
        """
        data = struct.pack ('B', temp)
        self.writeCommand (C_WHITE_TEMPERATURE, data)
        data = struct.pack ('B', brightness)
        self.writeCommand (C_WHITE_BRIGHTNESS, data)

    def on (self):
        """ Turns the light on.
        """
        self.writeCommand (C_POWER, b'\x01')

    def off (self):
        """ Turns the light off.
        """
        self.writeCommand (C_POWER, b'\x00')

    def disconnect (self):
        logger.info ("Disconnecting.")
        self.btdevice.disconnect ()
        self.session_key = None

    def getFirmwareRevision (self):
        """
        Returns :
            The firmware version as a null terminated utf-8 string.
        """
        char = self.btdevice.getCharacteristics (uuid=btle.AssignedNumbers.firmwareRevisionString)[0]
        return char.read ()

    def getHardwareRevision (self):
        """
        Returns :
            The hardware version as a null terminated utf-8 string.
        """
        char = self.btdevice.getCharacteristics (uuid=btle.AssignedNumbers.hardwareRevisionString)[0]
        return char.read ()

    def getModelNumber (self):
        """
        Returns :
            The model as a null terminated utf-8 string.
        """
        char = self.btdevice.getCharacteristics (uuid=btle.AssignedNumbers.modelNumberString)[0]
        return char.read ()

    def sendFirmware (self, firmware_path):
        """
        Updates the light bulb's firmware. The light will blink green after receiving the new
        firmware.

        Args:
            firmware_path: The path of the firmware file.
        """
        assert (self.session_key)

        with open (firmware_path, 'rb') as firmware_file :
            firmware_data = firmware_file.read()

        if not firmware_data :
            return

        ota_char = self.btdevice.getCharacteristics (uuid=OTA_CHAR_UUID)[0]
        count = 0
        for i in range (0, len (firmware_data), 0x10):
            data = struct.pack ('<H', count) + firmware_data [i:i+0x10].ljust (0x10, b'\xff')
            crc = pckt.crc16 (data)
            packet = data + struct.pack ('<H', crc)
            logger.debug ("Writing packet %i of %i : %s", count + 1, len(firmware_data)/0x10 + 1, repr(packet))
            ota_char.write (packet)
            # FIXME : When calling write with withResponse=True bluepy hangs after a few packets.
            #         Without any delay the light blinks once without accepting the firmware.
            #         The choosen value is arbitrary.
            time.sleep (0.01)
            count += 1
        data = struct.pack ('<H', count)
        crc = pckt.crc16 (data)
        packet = data + struct.pack ('<H', crc)
        logger.debug ("Writing last packet : %s", repr(packet))
        ota_char.write (packet)
