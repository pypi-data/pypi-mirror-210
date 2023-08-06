import os.path

import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser
import numpy as np
import struct
from pytimbre.waveform import Waveform


class MeasurementLogFile:
    def __init__(self, filename, irig_ch=None):
        """
        This function initializes the reading of the log file and populates the various data fields from the information
        within the file that is passes through the argument list.

        :param filename: string
            the location of the file that will be read

        :param irig_ch: int or str (optional)
            the channel of the IRIG recording on the specific recorder
        """
        self.CHANNEL_INDEX_NAME = "Channel Index"
        self.DEVICE_NUMBER_NAME = 'Device Number'
        self.SENSOR_SENSITIVITY = 'Sensitivity (mv/EU)'
        self.EXTERNAL_GAIN = 'Ext. Gain (Lin.)'
        self.INPUT_VOLTAGE_RANGE = 'Input Range (+/- V)'
        self.IEPE_POWER_SOURCE = 'IEPE Source'
        self.IEPE_POWER_LEVEL = 'IEPE Value (mA)'

        self.filename = os.path.basename(filename)[:-4].split('_')[0]
        self._duration = 0

        f = open(filename, 'rt')

        fileline = f.readline()
        if 'STANDARD LOG FILE PARAMETERS' in fileline:
            self._read_standard_file(f)
        elif fileline.upper() == "AIR FORCE RESEARCH LABORATORY LOG FILE PARAMETERS\n":
            self._read_afrl_file(f)
        else:
            self._read_miscellaneous(f)
        f.close()

        self.irig_ch = irig_ch

    @property
    def channel_number(self):
        return self._channel_no

    @property
    def start_time(self):
        return self._start_time

    @property
    def sample_rate(self):
        return self.fs

    @property
    def record_duration(self):
        return self._duration

    @property
    def stop_time(self):
        return self.start_time + timedelta(seconds=self.record_duration)

    def _read_standard_file(self, f):
        fileline = " "
        while fileline != "":
            fileline = f.readline()
            if fileline.find(':') >= 0:
                command = fileline.split('.')[0]
                data = fileline.split(':')[1]

                if command == 'FILENAME':
                    self.filename = data[1:-1]
                elif command == "DATE (mm/dd/yyyy)":
                    self._start_time = parser.parse(data[1:-1])
                elif command == "START TIME":
                    data = fileline.split(':', 1)[1]
                    dt = parser.parse(data)
                    self._start_time += timedelta(seconds=60 * (60 * dt.hour + dt.minute) + dt.second +
                                                          dt.microsecond * 1e-6)
                elif command == "OFFSET FRM UTC (hrs)":
                    self.gmt_offset = float(data[1:-1])
                elif command == "TIME ZONE":
                    self.time_zone = data[1:-1]
                elif command == "FILE COMMENTS":
                    self.comments = data[1:-1]
                elif command == "NUMBER CHANNELS":
                    self._channel_no = int(data[1:-1])
                elif command == "SAMPLE RATE (Hz)":
                    self.fs = float(data[1:-1])
                # elif command == "Block Size":
                #     self.block_size = float(data[1:-1])
                elif command == "AFR SOFTWARE VERSION":
                    self.acquisition_software_version = data[1:-1]
                elif command == "CONFIGURED CHANNEL SETTINGS":
                    _ = f.readline()
                    _ = f.readline()
                    fileline = f.readline()

                    self.channel_settings = pd.DataFrame(columns=[self.CHANNEL_INDEX_NAME,
                                                                  self.DEVICE_NUMBER_NAME,
                                                                  self.SENSOR_SENSITIVITY,
                                                                  self.EXTERNAL_GAIN,
                                                                  self.INPUT_VOLTAGE_RANGE,
                                                                  self.IEPE_POWER_SOURCE,
                                                                  self.IEPE_POWER_LEVEL])

                    for i in range(self._channel_no):
                        fileline = f.readline()

                        data = fileline.split('\t')

                        row = {self.CHANNEL_INDEX_NAME: int(data[0]),
                               self.DEVICE_NUMBER_NAME: data[1],
                               self.SENSOR_SENSITIVITY: float(data[2]),
                               self.EXTERNAL_GAIN: float(data[3]),
                               self.INPUT_VOLTAGE_RANGE: float(data[5]),
                               self.IEPE_POWER_SOURCE: data[6],
                               self.IEPE_POWER_LEVEL: float(data[7])}

                        self.channel_settings = self.channel_settings.append(row, ignore_index=True)

    def _read_afrl_file(self, f):
        fileline = " "
        while fileline != "":
            fileline = f.readline()
            if fileline.find(':') >= 0:
                command = fileline.split(':')[0].upper()
                data = fileline.split(':')[1]

                if command == 'FILE NAME':
                    self.filename = data[:-1]
                elif command == "DATE":
                    self._start_time = parser.parse(data[:-1])
                elif command == "TIME":
                    data = fileline.split(':', 1)[1]
                    dt = parser.parse(data)
                    self._start_time += timedelta(seconds=60 * (60 * dt.hour + dt.minute) + dt.second +
                                                          dt.microsecond * 1e-6)
                elif command == "OFFSET FROM GMT (H)":
                    self.gmt_offset = float(data[1:-1])
                elif command == "COMMENTS":
                    self.comments = data[:-1]
                elif command == "NUMBER OF CHANNELS":
                    self._channel_no = int(data[:-1])
                elif command == "SAMPLING FREQUENCY (HZ)":
                    self.fs = float(data[:-1])
                elif command == "BLOCK SIZE":
                    self.block_size = float(data[:-1])
                # elif command == "AFR SOFTWARE VERSION":
                #     self.AFR_Version = data[1:-1]
                elif command == "ACTUAL RECORD LENGTH":
                    duration = float(data)
                    self._duration = duration
                elif command == "CONFIGURATION":
                    #   Get the column names and create the DataFrame for the configuration

                    column_names = f.readline().split(',')
                    self.channel_settings = pd.DataFrame(columns=column_names)

                    #   Loop through the file until we have read a line for each channel within the measurement

                    channels_read = 0
                    while channels_read < self._channel_no:
                        fileline = f.readline()

                        if fileline != "":
                            data = fileline.split(',')

                            row = dict()

                            for i in range(len(column_names)):
                                row[column_names[i]] = data[i]

                            self.channel_settings = self.channel_settings.append(row, ignore_index=True)

                            channels_read += 1

    def _read_miscellaneous(self, f):
        fileline = " "
        while fileline != "":
            fileline = f.readline()

            if fileline.find(':') >= 0:
                command = fileline.split(':')[0]
                data = fileline.split(':')[1]

                if command == 'File Name':
                    self.filename = data[1:-1]
                elif command == "Date":
                    self._start_time = parser.parse(data[1:-1])
                elif command == "Start Time" or command == "Time":
                    data = fileline.split('\t')[1]
                    dt = parser.parse(data)
                    self._start_time += timedelta(seconds=60 * (60 * dt.hour + dt.minute) + dt.second +
                                                          dt.microsecond * 1e-6)
                elif command == "Offset from GMT (h)":
                    self.gmt_offset = float(data[1:-1])
                elif command == "Time Zone":
                    self.time_zone = data[1:-1]
                elif command == "File Comments":
                    self.comments = data[1:-1]
                elif command == "Number of Channels":
                    self._channel_no = int(data[1:-1])
                elif command == "Sampling Frequency (Hz)":
                    self.fs = float(data[1:-1])
                elif command == "Block Size":
                    self.block_size = float(data[1:-1])
                elif command == "AFR Software Version":
                    self.acquisition_software_version = data[1:-1]
                elif command == "Configured Channel Settings":
                    _ = f.readline()
                    _ = f.readline()
                    fileline = f.readline()

                    self.channel_settings = pd.DataFrame(columns=[self.CHANNEL_INDEX_NAME, self.DEVICE_NUMBER_NAME,
                                                                  self.SENSOR_SENSITIVITY, self.EXTERNAL_GAIN,
                                                                  self.INPUT_VOLTAGE_RANGE, self.IEPE_POWER_SOURCE,
                                                                  self.IEPE_POWER_LEVEL])

                    for i in range(self._channel_no):
                        fileline = f.readline()

                        data = fileline.split('\t')

                        row = {self.CHANNEL_INDEX_NAME: int(data[0]),
                               self.DEVICE_NUMBER_NAME: data[1],
                               self.SENSOR_SENSITIVITY: float(data[2]),
                               self.EXTERNAL_GAIN: float(data[3]),
                               self.INPUT_VOLTAGE_RANGE: float(data[5]),
                               self.IEPE_POWER_SOURCE: data[6],
                               self.IEPE_POWER_LEVEL: float(data[7])}

                        self.channel_settings = self.channel_settings.append(row, ignore_index=True)


class CalibratedBinaryFile(Waveform):
    def __init__(self, log, path, run_id=None, ch_id=None, s0=None, s1=None, sync='log_start_time'):
        """
        This function loads the waveform from the legacy measurement and adjusts for the DC offset
        :param path: string
            The path to the binary audio file
        :param log: log_file
            the object that represents the collection of audio files
        :param run_id: string or integer
            the run number represented as either the full ID component or the integer
        :param ch_id: string or integer
            the channel number represented as either the full string or the integer
        :param s0: integer
            the start sample to read from the file
        :param s1: integer
            the end sample to read from the file
        :param sync: string {'log_start_time' (default), 'irig_start_time'}
            log_start_time defines the waveform start time by the documented time in the log file.
            irig_start_time defines the waveform start time via an IRIG-B signal, and requires that log.irig_ch be populated with the appropriate IRIG channel number on the recorder.
        """

        if not isinstance(log, MeasurementLogFile):
            raise ValueError("Arugment invalid")

        if run_id is not None and ch_id is not None:
            run_str = CalibratedBinaryFile.set_record_id_to_legacy_format(run_id)
            ch_str = CalibratedBinaryFile.set_channel_to_legacy_format(ch_id)
            data_path = "{}/{}_{}.bin".format(path, run_str, ch_str)
        else:
            data_path = path

        y = CalibratedBinaryFile.read_bin_file(data_path, s0, s1)

        if sync == 'log_start_time':
            t0 = log.start_time
        elif sync == 'irig_start_time':
            tpm_s = CalibratedBinaryFile.sync_to_irig(log, data_path)
            t0 = datetime(year=log.start_time.year, month=log.start_time.month, day=log.start_time.day) + timedelta(
                seconds=tpm_s)
        elif sync == 'zero':
            t0 = datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
        else:
            raise ValueError('Input sync must be "log_start_time" or "irig_start_time" or "zero".')

        if s0 is not None:
            t0 += timedelta(seconds=s0 / log.sample_rate)

        super().__init__(y, log.sample_rate, t0)

    @property
    def peak_pressure(self):
        return np.max(self.samples)

    @property
    def peak_level(self):
        return 20 * np.log10(self.peak_pressure / 20e-6)

    @property
    def peak_time(self):
        return self.times[np.argmax(self.samples)]

    @staticmethod
    def set_channel_to_legacy_format(ch_id):
        if isinstance(ch_id, str):
            if "CH" in ch_id.upper():
                ch_str = ch_id[2:]
            else:
                ch_str = ch_id
        else:
            ch_str = "{:03.0f}".format(ch_id)
        return ch_str

    @staticmethod
    def set_record_id_to_legacy_format(run_id):
        if isinstance(run_id, int):
            run_str = "ID{:03.0f}".format(run_id)
        else:
            run_str = run_id
        return run_str

    @staticmethod
    def read_bin_file(data_path, s0, s1):
        f = open(data_path, 'rb')

        #   Determine the length of the file
        f.seek(0, 2)
        byte_count = f.tell()

        #   Move to the starting sample that we desire to read from the file
        if s0 is None or s0 == 0:
            f.seek(0)
        else:
            f.seek(s0 * 4)

        #   Determine the number of samples - the data is stored as a single precision floating point value
        #   We need to determine the number that we want to read.  If the starting sample is the beginning and the
        #   ending sample is none, then we read the entire file
        N = int(byte_count / 4)

        if s0 is not None and s1 is None:
            N -= s0
        elif s0 is None and s1 is not None:
            N = s1
        elif s0 is not None and s1 is not None:
            N = s1 - s0

        #   Read the contents of the file and unpack them as a single
        y = struct.unpack('f' * N, f.read(N * 4))

        #   Close the file

        f.close()

        return y

    @staticmethod
    def sync_to_irig(log, path):
        ch_str = CalibratedBinaryFile.set_channel_to_legacy_format(log.irig_ch)
        data_path = "{}{}.bin".format(path[0:-7], ch_str)
        y = CalibratedBinaryFile.read_bin_file(data_path, s0=0, s1=int(log.sample_rate * 3))
        tpm, julian_date = Waveform.irig_converter(np.array(y))
        return tpm
