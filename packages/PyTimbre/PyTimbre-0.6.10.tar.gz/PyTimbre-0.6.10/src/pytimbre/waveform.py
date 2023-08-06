import math
import sys

import numpy as np
from datetime import datetime, timedelta
from enum import Enum
from scipy.signal.windows import hamming, tukey
import scipy.signal
import statsmodels.api as sm
import colorednoise as cn
import warnings
from typing import Dict, Tuple
import numpy.typing as npt
from .yin import yin


class WindowingMethods(Enum):
    """
    The available windowing methods for the waveform
    """

    hanning = 1
    hamming = 2
    tukey = 3
    rectangular = 4


class TrimmingMethods(Enum):
    """
    Trimming can be accomplished with either the samples or times. This enumeration defines whether to use the time to
    calculate the sample or just provide the samples.
    """

    samples = 1
    times_absolute = 2
    times_relative = 3


class ScalingMethods(Enum):
    """
    In scaling the waveform we can apply the level changes in either decibels or linear values. This will determine how
    the interface scales the signal when manipulating the sample magnitudes.
    """

    linear = 1
    logarithmic = 2


class WeightingFunctions(Enum):
    """
    This class provides the options on how to weight the calculation of the overall level values
    """

    unweighted = 0
    a_weighted = 1
    c_weighted = 2


class CorrelationModes(Enum):
    """
    This class defines the various modes for the cross-correlation function.
    """

    valid = 0
    full = 1
    same = 2


class NoiseColor(Enum):
    white = 0
    pink = 1
    brown = 2


class LeqDurationMode(Enum):
    """
    The available types of time scaling for conversion of a signal to equivalent levels
    """

    steady_state = 0
    transient = 1


class Waveform:
    """
    This is a generic base class that contains the start time, samples and sample rate for a waveform.  Some limited
    operations exist within this class for manipulation of the base data within the class.

    #   TODO: Add function to overload the __add__ operator so that two waveforms can be combined appropriately
    #   TODO: Add convolution function
    #   TODO: Connect the WaveFile Start time to the Waveform start time
    #   TODO: Add function for SEL calculation
    #   TODO: Add filter array function
    Remarks
    2022-05-11 - FSM - added the function to determine whether the waveform is a calibration signal or not.
    """

    def __init__(self, pressures, sample_rate, start_time, remove_dc_offset: bool = True):
        """
        Default constructor
        :param pressures: float, array-like - the list of pressure values
        :param sample_rate: float - the number of samples per second
        :param start_time: float or datetime - the time of the first sample
        :param remove_dc_offset: bool, default = True - remove a DC offset from the samples
        """

        self._samples = pressures
        if remove_dc_offset:
            self._samples -= np.mean(self._samples)
        self.fs = sample_rate
        self.time0 = start_time
        self._forward_coefficients = None
        self._reverse_coefficients = None

        self._coefficient_count = 12
        self._hop_size_seconds = 0.0029
        self._window_size_seconds = 0.0232
        self._cutoff_frequency = 5
        self._centroid_threshold = 0.15
        self._effective_duration_threshold = 0.4

        self._signal_envelope = None
        self._normal_signal_envelope = None
        self._log_attack = None
        self._increase = None
        self._decrease = None
        self._Addresses = None
        self._amplitude_modulation = None
        self._frequency_modulation = None
        self._auto_correlation_coefficients = None
        self._zero_cross_rate = None
        self._temporal_centroid = None
        self._effective_duration = None
        self._temporal_feature_times = None

    # ---------------------- Collection of properties - this is both getters and setters -------------------------------

    @property
    def duration(self):
        """
        Determine the duration of the waveform by examining the number of samples and the sample rate
        :return: float - the total number of seconds within the waveform
        """
        return float(len(self._samples)) / self.fs

    @property
    def end_time(self):
        """
        Determine the end time - if the start time was a datetime, then this returns a datetime.  Otherwise a floating
        point value is returned
        :return: float or datetime - the end of the file
        """
        if isinstance(self.time0, datetime):
            return self.time0 + timedelta(seconds=self.duration)
        else:
            return self.time0 + self.duration

    @property
    def samples(self):
        """
        The actual pressure waveform
        :return: float, array-like - the collection of waveform data
        """
        return self._samples

    @samples.setter
    def samples(self, array):
        self._samples = array

    @property
    def sample_rate(self):
        """
        The number of samples per second to define the waveform.
        :return: float - the number of samples per second
        """
        return self.fs

    @sample_rate.setter
    def sample_rate(self, value):
        self.fs = value

    @property
    def start_time(self):
        """
        The time of the first sample
        :return: float or datetime - the time of the first sample
        """

        return self.time0

    @start_time.setter
    def start_time(self, value):
        self.time0 = value

    @property
    def forward_coefficients(self):
        return self._forward_coefficients

    @property
    def reverse_coefficients(self):
        return self._reverse_coefficients

    @property
    def times(self):
        """
        This determines the time past midnight for the start of the audio and returns a series of times for each sample
        :return: float, array-like - the sample times for each element of the samples array
        """

        if isinstance(self.start_time, datetime):
            t0 = (60 * (60 * self.start_time.hour + self.start_time.minute) + self.start_time.second +
                  self.start_time.microsecond * 1e-6)
        else:
            t0 = self.start_time

        return np.arange(0, len(self.samples)) / self.sample_rate + t0

    @property
    def effective_duration_threshold(self):
        return self._effective_duration_threshold

    @property
    def centroid_threshold(self):
        return self._centroid_threshold

    @property
    def cutoff_frequency(self):
        return self._cutoff_frequency

    @cutoff_frequency.setter
    def cutoff_frequency(self, value):
        self._cutoff_frequency = value

    @property
    def window_size_seconds(self):
        return self._window_size_seconds

    @window_size_seconds.setter
    def window_size_seconds(self, value):
        self._window_size_seconds = value

    @property
    def hop_size_seconds(self):
        return self._hop_size_seconds

    @hop_size_seconds.setter
    def hop_size_seconds(self, value):
        self._hop_size_seconds = value

    @property
    def window_size_samples(self):
        return int(np.round(self.window_size_seconds * self.sample_rate))

    @property
    def hop_size_samples(self):
        return int(round(self.hop_size_seconds * self.sample_rate))

    @property
    def coefficient_count(self):
        """
        The number of coefficients to generate for the available data
        """

        return self._coefficient_count

    @coefficient_count.setter
    def coefficient_count(self, value):
        """
        Set the number of coefficients for the analysis
        """

        self._coefficient_count = value

    @property
    def attack(self):
        if self._Addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._Addresses = self.calculate_log_attack()

        return self._Addresses[0]

    @property
    def decrease(self):
        if self._Addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._Addresses = self.calculate_log_attack()

        return self._Addresses[1]

    @property
    def release(self):
        if self._Addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._Addresses = self.calculate_log_attack()

        return self._Addresses[4]

    @property
    def log_attack(self):
        """
        The log-attack-time is simply defined as LAT = log_10(t[-1]-t[0])
        """
        if self._Addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._Addresses = self.calculate_log_attack()

        return self._log_attack

    @property
    def attack_slope(self):
        """
        The attack slope is defined as the average temporal slope of the energy during the attack segment. We compute
        the local slopes of the energy corresponding to each effort w_i. We then compute a weighted average of the
        slopes. The weights are chosen in order to emphasize slope values in the middle of the attack (the weights are
        the values of a Gaussian function centered around the threshold = 50% and with a standard-deviation of 0.5).
        """
        if self._Addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._Addresses = self.calculate_log_attack()

        return self._increase

    @property
    def decrease_slope(self):
        """
        The temporal decrease is a measure of the rate of decrease of the signal energy. It distinguishes non-sustained
        (e.g. percussive, pizzicato) sounds from sustained sounds. Its calculation is based on a decreasing exponential
        model of the energy envelope starting from it maximum.
        """
        if self._Addresses is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._Addresses = self.calculate_log_attack()

        return self._decrease

    @property
    def temporal_centroid(self):
        """
        The temporal centroid is the center of gravity of the energy envelope. It distinguishes percussive from
        sustained sounds. It has been proven to be a perceptually important descriptor (Peeters et al., 2000).
        """
        if self._temporal_centroid is None:
            self._calculate_signal_envelope()
            self._temporal_centroid = self.calculate_temporal_centroid()

        return self._temporal_centroid

    @property
    def effective_duration(self):
        """
        The effective duration is a measure intended to reflect the perceived duration of the signal. It distinguishes
        percussive sounds from sustained sounds but depends on the event duration. It is approximated by the time the
        energy envelop is above a given threshold. After many empirical tests, we have set this threshold to 40%
        """
        if self._effective_duration is None:
            self._calculate_signal_envelope()
            self._effective_duration = self.calculate_effective_duration()

        return self._effective_duration

    @property
    def amplitude_modulation(self):
        if self._amplitude_modulation is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._Addresses = self.calculate_log_attack()
            self._frequency_modulation, self._amplitude_modulation = self.calculate_modulation()
        return self._amplitude_modulation

    @property
    def frequency_modulation(self):
        if self._frequency_modulation is None:
            self._calculate_signal_envelope()
            self._log_attack, self._increase, self._decrease, self._Addresses = self.calculate_log_attack()
            self._frequency_modulation, self._amplitude_modulation = self.calculate_modulation()
        return self._frequency_modulation

    @property
    def auto_correlation(self):
        if self._auto_correlation_coefficients is None:
            self._temporal_feature_times, self._auto_correlation_coefficients, self._zero_cross_rate = \
                self.instantaneous_temporal_features()
        return self._auto_correlation_coefficients

    @property
    def zero_crossing_rate(self):
        if self._zero_cross_rate is None:
            self._temporal_feature_times, self._auto_correlation_coefficients, self._zero_cross_rate = \
                self.instantaneous_temporal_features()
        return self._zero_cross_rate

    @property
    def temporal_feature_times(self):
        if self._temporal_feature_times is None:
            self._temporal_feature_times, self._auto_correlation_coefficients, self._zero_cross_rate = \
                self.instantaneous_temporal_features()
        return self._temporal_feature_times

    @property
    def signal_envelope(self):
        if self._signal_envelope is None:
            self._calculate_signal_envelope()

        return self._signal_envelope

    @property
    def normal_signal_envelope(self):
        if self._normal_signal_envelope is None:
            self._calculate_signal_envelope()

        return self._normal_signal_envelope

    @property
    def loudness(self):
        from mosqito.sq_metrics import loudness_zwst_perseg
        return loudness_zwst_perseg(signal=self.samples, fs=self.sample_rate)[0]

    @property
    def roughness(self):
        from mosqito.sq_metrics import roughness_dw

        return roughness_dw(signal=self.samples, fs=self.sample_rate)[0]

    @property
    def sharpness(self):
        from mosqito.sq_metrics import sharpness_din_perseg

        return sharpness_din_perseg(signal=self.samples, fs=self.sample_rate)[0]

    @property
    def is_mono(self):
        """
        This function examines the size of the samples array within the function. If there is a second dimension then
        this function returns false. It is true otherwise.
        """
        return len(self.samples.shape) == 1

    @property
    def is_clipped(self):
        """
        This function attempts to determine whether there is clipping in the acoustic data represented in this waveform.
        """

        clipped_sections, total_clipped_samples = Waveform._detect_clipping(self.samples)

        return not ((total_clipped_samples / len(self.samples)) < 0.01)

    @property
    def fundamental_frequency(self):
        return np.median(yin(
            self.samples,
            self.sample_rate,
            F_max=10000,
            F_min=10,
            N=int(np.floor(self.sample_rate / 10)),
            H=int(np.floor(self.sample_rate / 10 / 4))
        )[0])

    # ------------------ Static functions for the calculation of filter shapes and timbre features ---------------------
    @staticmethod
    def _detect_clipping(
            samples_array: npt.NDArray, max_threshold=0.995, min_threshold=0.995
    ) -> Tuple[Dict[str, int], int]:
        """
        Somewhat informed from https://www.sciencedirect.com/science/article/pii/S0167639321000832
        but without the sample-by-sample tagging. Intended to catch cases where clipped values have
        been normalized away.

        Returns the tagged clipped samples and the total number of clipped samples

        2023-04-06 - FSM - This function was extracted from the clipdetect project to minimize the dependency
        requirements of PyTimbre
        """
        if len(samples_array.shape) != 1:
            raise ValueError(
                "You must pass just the samples without any channel information"
            )
        max_sample = samples_array.max()
        min_sample = samples_array.min()
        max_threshold *= max_sample
        min_threshold *= min_sample
        clipping_sections = []
        total_clipped_samples = 0
        clip_end = 0
        for i, sample in enumerate(samples_array):
            if i > clip_end and sample in [max_sample, min_sample]:
                clipping_count = 0
                for new_sample in samples_array[i:]:
                    if new_sample >= max_threshold or new_sample <= min_threshold:
                        clipping_count += 1
                    else:
                        clipping_sections.append({"start": i, "end": i + clipping_count})
                        total_clipped_samples += clipping_count
                        clip_end = i + clipping_count
                        break
        return clipping_sections, total_clipped_samples

    @staticmethod
    def AC_Filter_Design(fs):
        """
        AC_Filter_Design.py

        Created on Mon Oct 18 19:27:36 2021

        @author: Conner Campbell, Ball Aerospace

        Description
        ----------
        Coeff_A, Coeff_C = AC_Filter_Design(fs)

        returns Ba, Aa, and Bc, Ac which are arrays of IRIR filter
        coefficients for A and C-weighting.  fs is the sampling
        rate in Hz.

        This progam is a recreation of adsgn and cdsgn
        by Christophe Couvreur, see	Matlab FEX ID 69.


        Parameters
        ----------
        fs : double
            sampling rate in Hz

        Returns
        -------

        Coeff_A: list
            List of two numpy arrays, feedforward and feedback filter
            coeffecients for A-weighting filter. Form of lits is [Ba,Aa]

        Coeff_c: list
            List of two numpy arrays, feedforward and feedback filter
            coeffecients for C-weighting filter. Form of lits is [Bc,Ac]

        Code Dependencies
        -------
        This program requires the following python packages:
        scipy.signal, numpy

        References
        -------
        IEC/CD 1672: Electroacoustics-Sound Level Meters, Nov. 1996.

        ANSI S1.4: Specifications for Sound Level Meters, 1983.

        ACdsgn.m: Christophe Couvreur, Faculte Polytechnique de Mons (Belgium)
        couvreur@thor.fpms.ac.be
        """

        # Define filter poles for A/C weight IIR filter according to IEC/CD 1672

        f1 = 20.598997
        f2 = 107.65265
        f3 = 737.86223
        f4 = 12194.217
        A1000 = 1.9997
        C1000 = 0.0619
        pi = np.pi

        # Calculate denominator and numerator of filter tranfser functions

        coef1 = (2 * pi * f4) ** 2 * (10 ** (C1000 / 20))
        coef2 = (2 * pi * f4) ** 2 * (10 ** (A1000 / 20))

        Num1 = np.array([coef1, 0.0])
        Den1 = np.array([1, 4 * pi * f4, (2 * pi * f4) ** 2])

        Num2 = np.array([1, 0.0])
        Den2 = np.array([1, 4 * pi * f1, (2 * pi * f1) ** 2])

        Num3 = np.array([coef2 / coef1, 0.0, 0.0])
        Den3 = scipy.signal.convolve(np.array([1, 2 * pi * f2]).T, (np.array([1, 2 * pi * f3])))

        # Use scipy.signal.bilinear function to get numerator and denominator of
        # the transformed digital filter transfer functions.

        B1, A1 = scipy.signal.bilinear(Num1, Den1, fs)
        B2, A2 = scipy.signal.bilinear(Num2, Den2, fs)
        B3, A3 = scipy.signal.bilinear(Num3, Den3, fs)

        Ac = scipy.signal.convolve(A1, A2)
        Aa = scipy.signal.convolve(Ac, A3)

        Bc = scipy.signal.convolve(B1, B2)
        Ba = scipy.signal.convolve(Bc, B3)

        Coeff_A = [Ba, Aa]
        Coeff_C = [Bc, Ac]
        return Coeff_A, Coeff_C

    @staticmethod
    def detect_local_extrema(input_v, lag_n):
        """
        This will detect the local maxima of the vector on the interval [n-lag_n:n+lag_n]

        Parameters
        ----------
        input_v : double array-like
            This is the input vector that we are examining to determine the local maxima
        lag_n : double, integer
            This is the number of samples that we are examining within the input_v to determine the local maximum

        Returns
        -------
        pos_max_v : double, array-like
            The locations of the local maxima
        """

        do_affiche = 0
        lag2_n = 4
        seuil = 0

        L_n = len(input_v)

        pos_cand_v = np.where(np.diff(np.sign(np.diff(input_v))) < 0)[0]
        pos_cand_v += 1

        pos_max_v = np.zeros((len(pos_cand_v),))

        for i in range(len(pos_cand_v)):
            pos = pos_cand_v[i]

            if (pos > lag_n) & (pos <= L_n - lag_n):
                tmp = input_v[pos - lag_n:pos + lag2_n]
                position = np.argmax(tmp)

                position = position + pos - lag_n - 1

                if (pos - lag2_n > 0) & (pos + lag2_n < L_n + 1):
                    tmp2 = input_v[pos - lag2_n:pos + lag2_n]

                    if (position == pos) & (input_v[position] > seuil * np.mean(tmp2)):
                        pos_max_v[i] = pos

        return pos_max_v

    @staticmethod
    def next_pow2(x: int):
        n = np.log2(x)
        return 2 ** (np.floor(n) + 1)

    @staticmethod
    def gps_audio_signal_converter(filename: str):
        """
        This function will convert the data from an audio file that captured the GPS signal and converted it to an
        audio channel.

        This function is adapted from the Python code delivered as part of the ESCAPE 2018 dataset (gps_wav.py)

        Parameters
        ----------
        filename: str - the full path to the audio file
        """
        import wave
        import struct
        import scipy.signal
        import re

        #   Initialize some parsing variables
        start_search = 2
        win = 1000
        thrE = 1000
        thr = 2500
        gap = 99

        #   Load the wave data
        wave_object = wave.open(filename, 'rb')
        channel_count = wave_object.getnchannels()
        bit_count = wave_object.getsampwidth()
        sample_rate = wave_object.getframerate()
        frame_count = wave_object.getnframes()
        temp_data = wave_object.readframes(frame_count)
        data = struct.unpack("<" + str(frame_count) + "h", temp_data)

        #   Filter the data with a high-pass filter to remove any DC offsets
        data = scipy.signal.lfilter([1.0, -1.0], 1.0, data)

        #   Find first complete GPS data burst
        energy = []
        filtered_data = []
        for i in range(0, start_search * sample_rate, win):
            energy = np.sum(np.square(data[i:i + win])) / win
            if energy < thrE:
                offset = i + win
                filtered_data.extend(data[offset:frame_count])
                frame_count = len(filtered_data)
                break

        # Detect pulse state transitions in audio signal
        state = True
        detect = []
        ind = []
        indPlus = []
        for i in range(1, np.min([250000, frame_count])):
            if (filtered_data[i] >= filtered_data[i + 1]) & (filtered_data[i] > filtered_data[i - 1]):
                if filtered_data[i] > thr:
                    detect.append(state)
                    state = not state
                    ind.append(i)
                    indPlus.append(i)
            elif (filtered_data[i] <= filtered_data[i + 1]) & (filtered_data[i] < filtered_data[i - 1]):
                if filtered_data[i] < -thr:
                    detect.append(state)
                    state = not state
                    ind.append(i)

        # Extract bit sequence and corresponding sample indices
        bits = []
        index = []
        index.append(ind[0])
        for i in range(len(ind) - 1):
            if (ind[i + 1] - ind[i]) > gap:
                bits.append(1)
                index.append(ind[i + 1])
                # print(ind[i+1])
                continue
            if detect[i]:
                bits.extend(np.zeros(int(round((ind[i + 1] - ind[i]) / 10.0)), dtype=int))
            else:
                bits.extend(np.ones(int(round((ind[i + 1] - ind[i]) / 10.0)), dtype=int))

        #   Extract NMEA 0183 sentences from bit sequence and write to file
        s = ''
        sent = ''
        cnt = 0
        for i in range(int(len(bits) / 10)):
            word = s.join(map(str, bits[cnt:cnt + 10]))
            cnt = cnt + 10
            if bool(int(word[0])) or bool(int(word[8])) or not (bool(int(word[9]))):
                # continue
                wordE = []
                for k in range(10):
                    wordE.append(str(int(not (bool(int(word[k]))))))
                word = s.join(wordE)
            sent = sent + chr(int('0b' + word[8:0:-1], 2))

        elements = sent.split('\r\n')

        for i in range(len(elements)):
            if elements[i].split(',')[0] == "$GPRMC":
                first_rmc = elements[i]
                break

        # Find start of 1st complete GPS data bursts
        indBurst = indPlus[0] + offset
        elements = first_rmc.split(',')
        hour = int(elements[1][:2])
        minute = int(elements[1][2:4])
        start_time = (60 * (60 * int(elements[1][:2]) + int(elements[1][2:4])) + float(elements[1][4:]) - indBurst /
                      sample_rate)
        date = datetime(int(elements[9][4:]) + 2000, int(elements[9][2:4]), int(elements[9][:2])) + \
               timedelta(seconds=start_time)

        return date

    @staticmethod
    def generate_tone(frequency: float = 100, sample_rate: float = 48000, duration: float = 1.0,
                      amplitude_db: float = 94):
        """
        This function generates a sine wave tone function with the specific frequency and duration specified in the
        argument list.

        Parameters
        ----------
        frequency: float, default: 100 - the linear frequency of the waveform
        sample_rate: float, default: 48000 - the number of samples per second
        duration: float, default: 1.0 - the total number of seconds in the waveform
        amplitude_db: float, default:94, this is the RMS amplitude of the waveform

        Returns
        -------
        A waveform this the generated data.
        """

        amplitude_rms = 10 ** (amplitude_db / 20) * 2e-5
        x = np.arange(0, duration, 1 / sample_rate)
        y = amplitude_rms * np.sqrt(2) * np.sin(2 * np.pi * frequency * x)

        return Waveform(y, sample_rate, 0)

    @staticmethod
    def generate_noise(sample_rate: float = 48000, duration: float = 1.0, amplitude_db: float = 94,
                       noise_color=NoiseColor.pink):
        samples = cn.powerlaw_psd_gaussian(noise_color.value, int(np.floor(duration * sample_rate)))

        wfm = Waveform(samples, sample_rate, 0)
        scaling = amplitude_db - wfm.overall_level()
        wfm.scale_signal(scaling, True, ScalingMethods.logarithmic)

        return wfm

    @staticmethod
    def irig_converter(signal):
        """
        Compute the time of the signal using the IRIG-B format as reference.

        Parameters
        ----------
        signal : double, array-like

        Returns
        -------
        datetime object for the start of the sample
        """

        irig = signal * 30.0 / np.max(signal)
        si = np.sign(irig - np.mean(irig))

        dsi = np.diff(si)

        rise = np.where(dsi == 2)[0]
        fall = np.where(dsi == -2)[0]

        if np.min(fall) < np.min(rise):
            fall = fall[1:]

        if np.max(rise) > np.max(fall):
            rise = rise[:-1]

        rf = np.stack([rise, fall]).transpose()

        index = np.round(np.mean(rf, axis=1, dtype='int'))
        top = irig[index]
        top2 = (top > 20) * 30 + (top < 20) * 10 - 10

        p0pr = np.array([30, 30, 30, 30, 30, 30, 30, 30, 10, 10, 30, 30, 30, 30, 30, 30, 30, 30]) - 10

        #   Locate this sequence in the top2 array

        pr = list()
        for i in range(len(top2) - len(p0pr)):
            located = True
            for j in range(len(p0pr)):
                if top2[i + j] != p0pr[j]:
                    located = False
                    break
            if located:
                pr.append(i + 10)

        prrise = rise[pr]
        sps = np.mean(np.diff(prrise))

        carr = np.mean(np.diff(pr))

        seconds = np.zeros((len(pr) - 1,))
        minutes = np.zeros((len(pr) - 1,))
        hours = np.zeros((len(pr) - 1,))
        day_of_year = np.zeros((len(pr) - 1,))
        dt = np.zeros((len(pr) - 1,))

        for j in range(len(pr) - 1):

            start_index = int(pr[j] + 0.01 * carr)
            stop_index = int(pr[j] + 0.01 * 2 * carr)

            values = np.array([1, 2, 4, 8, 0, 10, 20, 40])
            mask = np.zeros((len(values),))

            for i in range(len(mask)):
                if np.sum(top2[start_index:stop_index]) > 70:
                    mask[i] = 1

                start_index += 10
                stop_index += 10

            seconds[j] = np.sum(values * mask)

            start_index = int(pr[j] + 0.01 * carr * 10)
            stop_index = int(pr[j] + 0.01 * 11 * carr)

            values = np.array([1, 2, 4, 8, 0, 10, 20, 40])
            mask = np.zeros((len(values),))

            for i in range(len(mask)):
                if np.sum(top2[start_index:stop_index]) > 70:
                    mask[i] = 1

                start_index += 10
                stop_index += 10

            minutes[j] = np.sum(values * mask)

            start_index = int(pr[j] + 0.01 * carr * 20)
            stop_index = int(pr[j] + 0.01 * 21 * carr)

            values = np.array([1, 2, 4, 8, 0, 10, 20])
            mask = np.zeros((len(values),))

            for i in range(len(mask)):
                if np.sum(top2[start_index:stop_index]) > 70:
                    mask[i] = 1

                start_index += 10
                stop_index += 10

            hours[j] = np.sum(values * mask)

            start_index = int(pr[j] + 0.01 * carr * 30)
            stop_index = int(pr[j] + 0.01 * 31 * carr)

            values = np.array([1, 2, 4, 8, 0, 10, 20, 40, 80, 0, 100, 200])
            mask = np.zeros((len(values),))

            for i in range(len(mask)):
                if np.sum(top2[start_index:stop_index]) > 70:
                    mask[i] = 1

                start_index += 10
                stop_index += 10

            day_of_year[j] = np.sum(values * mask)

            #   Determine the linear adjustment for the zero cross over not occurring right on the sample

            dt[j] = (np.interp(0, [irig[prrise[j]], irig[prrise[j] + 1]], [prrise[j], prrise[j] + 1]) - prrise[j]) / sps

        #   Compute the time past midnight

        times = 60 * (60 * hours + minutes) + seconds - dt

        day_of_year = np.mean(day_of_year)

        index = np.arange(0, len(irig))
        timevector = times[0] + (index - prrise[0]) / sps

        return times[0] - prrise[0] / sps, day_of_year

    @staticmethod
    def irig_converter_for_arc(data, fs):
        """
        The timecode generators present at the Aeroacoustic Research Complex (ARC) produce the signal that defines the IRIG-
        B timecode differently. The previous methods do not return the correct information for the ARC data.


        """
        #   Find the index of the first minimum - which is assumed to occur within the first second of the waveform

        index = np.where(data[:fs] == np.min(data[:fs]))[0][0]

        #   The IRIG-B waveform is an amplitude modulated 1 kHz sine wave.  So we need to know the number of samples
        #   for a single period of the waveform

        frequency = 1000
        period = 1 / frequency
        period_samples = period * fs

        #   Now we can get the first set of signals and determine the amplitude for the minima

        amplitudes = np.zeros((3000,))

        for i in range(3000):
            amplitudes[i] = data[int(index + i * period_samples)]

            if index + (i + 1) * period_samples >= len(data):
                break

        maximum_index = i

        #   Scale by the smallest value in this array

        amplitudes /= np.min(amplitudes)

        #   Convert this to a binary array that will be used for the determination of the bit-wise elements of the
        #   signal

        binary_array = np.zeros((maximum_index,))

        for i in range(maximum_index):
            if amplitudes[i] >= 0.8:
                binary_array[i] = 1

        #   Now the start of a signal must be with a signal that is 8, so we need to locate the first 8 within the
        #   summation of the binary signal.

        first_eight = -1
        for i in range(3000):
            elements = binary_array[i:i + 10]

            if np.sum(elements) == 8 and binary_array[i] == 1 and binary_array[i + 9] == 0:
                first_eight = i
                break

        if first_eight < 0:
            return None, None

        #   Now that we have determined the location of the first 8, we can begin to sum the binary array in
        #   sections of 10 elements at a time

        summed_array = np.zeros((250,))

        for i in range(250):
            idx = first_eight + i * 10
            summed_array[i] = np.sum(binary_array[idx:idx + 10])

        #   Now we must find the first double-8 as this marks the beginning of the time code definition

        first_double_eight = -1
        for i in range(250):
            if summed_array[i] == 8 and summed_array[i + 1] == 8:
                first_double_eight = i + 1
                break

        if first_double_eight < 0:
            return None, None

        #   Now from this we need to extract the various parts of the time code

        timecode_elements = summed_array[first_double_eight:first_double_eight + 100]

        #   Get the hours

        hour_elements = timecode_elements[20:30]
        hour_elements[np.where(hour_elements < 5)[0]] = 0
        hour_elements[np.where(hour_elements >= 5)[0]] = 1

        weights = np.array([1, 2, 4, 8, 0, 10, 20, 0, 0, 0])

        hour = np.sum(hour_elements * weights)

        #   Get the minutes

        minute_elements = timecode_elements[10:20]
        minute_elements[np.where(minute_elements < 5)[0]] = 0
        minute_elements[np.where(minute_elements == 5)[0]] = 1
        weights = np.array([1, 2, 4, 8, 0, 10, 20, 40, 0, 0])

        minutes = np.sum(minute_elements * weights)

        #   Next the seconds

        seconds_elements = timecode_elements[:10]
        seconds_elements[np.where(seconds_elements < 5)[0]] = 0
        seconds_elements[np.where(seconds_elements == 5)[0]] = 1
        weights = np.array([0, 1, 2, 4, 8, 0, 10, 20, 40, 0])

        seconds = np.sum(seconds_elements * weights)

        #   And finally we get the julian date of the time code

        date_elements = timecode_elements[30:42]
        date_elements[np.where(date_elements != 5)[0]] = 0
        date_elements[np.where(date_elements == 5)[0]] = 1
        weights = np.array([1, 2, 4, 8, 0, 10, 20, 40, 80, 0, 100, 200])

        julian_date = np.sum(weights * date_elements)

        #   Now we know that the time code was not at the very beginning of the signal, so let's go ahead and
        #   determine the time offset to the beginning of the file.

        tpm = 60 * (60 * hour + minutes) + seconds

        file_start_adjustment = (((first_double_eight + 1) * 10 + first_eight) * (fs / 1000) + index) / fs

        tpm -= file_start_adjustment

        return tpm, julian_date

    # ---------------------------- Protected functions for feature calculation -----------------------------------------

    def _calculate_signal_envelope(self):
        #   Calculate the energy envelope of the signal that is required for many of the features

        analytic_signal = scipy.signal.hilbert(self.samples)
        amplitude_modulation = np.abs(analytic_signal)
        normalized_freq = self.cutoff_frequency / (self.sample_rate / 2)
        sos = scipy.signal.butter(3, normalized_freq, btype='low', analog=False, output='sos')
        self._signal_envelope = scipy.signal.sosfilt(sos, amplitude_modulation)

        #   Normalize the envelope

        self._normal_signal_envelope = self.signal_envelope / np.max(self.signal_envelope)

    def _trim_by_samples(self, s0: int = None, s1: int = None):
        """
        This function will trim the waveform and return a subset of the current waveform based on sample indices within
        the 'samples' property within this class.

        Parameters
        __________
        :param s0: int - the start sample of the trimming. If s0 is None, then interface will use the first sample
        :param s1: int - the stop sample of the trimming. If s1 is None, then the interface uses the last sample

        Returns
        _______
        :returns: Waveform - a subset of the waveform samples
        """

        #   Handle the start/stop samples may be passed as None arguments

        if s0 is None:
            s0 = 0

        if s1 is None:
            s1 = self._samples.shape[0]

        #   Determine the new start time of the waveform

        if isinstance(self.start_time, datetime):
            t0 = self.start_time + timedelta(seconds=s0 / self.sample_rate)
        else:
            t0 = self.start_time + s0 / self.sample_rate

        #   Create the waveform based on the new time, and the subset of the samples

        return Waveform(self.samples[np.arange(s0, s1)].copy(), self.sample_rate, t0, remove_dc_offset=False)

    def _scale_waveform(self, scale_factor: float = 1.0, inplace: bool = False):
        """
        This function applies a scaling factor to the waveform's sample in a linear scale factor.

        Parameters
        __________
        :param scale_factor: float - the linear unit scale factor to change the amplitude of the sample values
        :param inplace: boolean - Whether to modify the samples within the current object, or return a new object

        Returns
        _______
        :returns: If inplace == True a new Waveform object with the sample magnitudes scaled, None otherwise
        """

        if inplace:
            self._samples *= scale_factor

            return None
        else:
            return Waveform(self._samples * scale_factor, self.sample_rate, self.start_time)

    # -------------------- Public functions for operations on the samples within the Waveform --------------------------

    def determine_calibration_scale_factor(self, level: float = 114, frequency: float = 1000):
        """
        This function will take the information within the current Waveform and determine the scaling factor that can be
        applied to this, or any other file, to ensure that the acoustic reference is obtained.

        Parameters
        ----------
        :param level: float
            default = 114 dB, this is the acoustic level at the specified frequency that we expect the calibration tone
            to generate
        :param frequency: float
            default = 1000 Hz, this is the acoustic frequency of the calibration device
        """

        from .spectral.fractional_octave_band import FractionalOctaveBandTools as fob

        #   ensure that the calibration frequency is actually located within the Waveform.
        calibration, detected_frequency = self.is_calibration()
        if not calibration or abs(detected_frequency - frequency) > 25:
            raise ValueError("The Waveform passed to the function does not contain a calibration tone or the tone is "
                             "not at the expected frequency, based on the arguments of the function.")

        #   Now we need to calculate the scale factor required to adjust the level of the calibration Waveform to the
        #   desired magnitude.
        filtered_wfm = self.apply_bandpass(fob.lower_frequency(3, fob.nearest_band(3, frequency)),
                                           fob.upper_frequency(3, fob.nearest_band(3, frequency)))

        #   Now assuming that the data within the samples array is a pressure
        rms_level = 20 * np.log10(np.std(filtered_wfm.samples) / 20e-6)

        sens = level - rms_level
        sens /= 20
        sens *= -1
        sens = 10.0 ** sens

        return sens

    def apply_calibration(self, wfm, level: float = 114, frequency: float = 1000, inplace: bool = False):
        """
        This function assumes that the current Waveform, and the item provided as the first argument, possess the
        same parameters for the acquisition system. This assumes that the Waveform (wfm) is a calibration data that
        is collected with the same level and frequency passed to the function. This will scale the current samples to
        the same amplitude based on the data within the wfm.

        Parameters
        ----------
        wfm - The Waveform that possesses a calibration signal that can be analyzed to determine the scaling factor
        level: float, default = 114 - the expected acoustic level for the calibration signal in wfm
        frequency: float, default = 1000 - the frequency of the calibration signal in wfm
        inplace: bool, default = False - whether the manipulation is applied to the current Waveform,
            or a new Waveform object is returned to the user.
        """

        if not isinstance(wfm, Waveform):
            raise ValueError("The wfm is expected to be a Waveform object")

        sens = wfm.determine_calibration_scale_factor(level, frequency)

        #   Now scale the calibration signal and determine whether the overall level is close to the expected level
        scaled_calibration_wfm = wfm.scale_signal(1 / sens)

        if abs(np.any(scaled_calibration_wfm.overall_level() - level)) > 2:
            raise ValueError("The method did not appropriately scale the calibration signal")

        return self.scale_signal(1 / sens, inplace=inplace)

    def scale_signal(self, factor: float = 1.0, inplace: bool = False,
                     scale_type: ScalingMethods = ScalingMethods.linear):
        """
        This method will call the sub-function to scale the values of the waveform in linear fashion. If the scale
        factor is provided in logarithmic form, it will be converted to a linear value and sent to the sub-function.

        Parameters
        ----------
        :param factor: float - the scale factor that needs to be passed to the scaling sub-function, which will be
            multiplied by the unscaled signal (e.g. 1 divided by the sensitivity of a microphone in V/Pa)
        :param inplace: bool - whether to manipulate the data within the current class, or return a new instance
        :param scale_type: scaling_method - how to apply the scaling to the signal

        Returns
        -------

        :returns: output of sub-function
        """

        scale_factor = factor

        if scale_type == ScalingMethods.logarithmic:
            scale_factor = 10 ** (scale_factor / 20)

        return self._scale_waveform(scale_factor, inplace)

    def trim(self, s0: float = 0.0, s1: float = None, method: TrimmingMethods = TrimmingMethods.samples):
        """
        This function will remove the samples before s0 and after s1 and adjust the start time
        :param s0: float - the sample index or time of the new beginning of the waveform
        :param s1: float - the sample index or time of the end of the new waveform
        :param method: trimming_methods - the method to trim the waveform
        :return: generic_time_waveform object
        """

        #   Determine whether to use the time or sample methods

        if method == TrimmingMethods.samples:
            return self._trim_by_samples(int(s0), int(s1))
        elif method == TrimmingMethods.times_absolute:
            t0 = s0
            t1 = s1

            if isinstance(self.start_time, datetime):
                start_seconds = 60 * (60 * self.start_time.hour + self.start_time.minute) + self.start_time.second + \
                                self.start_time.microsecond / 1e6
            else:
                start_seconds = self.start_time

            s0 = (t0 - start_seconds) * self.sample_rate
            ds = (t1 - t0) * self.sample_rate
            s1 = s0 + ds

            return self._trim_by_samples(int(s0), int(s1))

        elif method == TrimmingMethods.times_relative:
            t0 = s0
            t1 = s1

            s0 = t0 * self.sample_rate
            s1 = t1 * self.sample_rate

            return self._trim_by_samples(int(s0), int(s1))

    def apply_window(self, window: WindowingMethods = WindowingMethods.hanning, windowing_parameter=None):
        """
        This will apply a window with the specific method that is supplied by the window argument and returns a
        generic_time_waveform with the window applied

        :param window:windowing_methods - the enumeration that identifies what type of window to apply to the waveform
        :param windowing_parameter: int or float - an additional parameter that is required for the window
        :returns: generic_time_waveform - the waveform with the window applied
        """

        W = []

        if window == WindowingMethods.tukey:
            W = tukey(len(self.samples), windowing_parameter)

        elif window == WindowingMethods.rectangular:
            W = tukey(len(self.samples), 0)

        elif window == WindowingMethods.hanning:
            W = tukey(len(self.samples), 1)

        elif window == WindowingMethods.hamming:
            W = hamming(len(self.samples))

        return Waveform(self.samples * W, self.fs, self.start_time)

    def apply_iir_filter(self, b, a):
        """
        This function will be able to apply a filter to the samples within the file and return a new
        generic_time_waveform object

        :param b: double, array-like - the forward coefficients of the filter definition
        :param a: double, array-like - the reverse coefficients of the filter definition
        """

        self._forward_coefficients = b
        self._reverse_coefficients = a
        return Waveform(scipy.signal.lfilter(b, a, self.samples), self.sample_rate, self.start_time)

    def apply_a_weight(self):
        """
        This function specifically applies the a-weighting filter to the acoustic data, and returns a new waveform with
        the filter applied.

        :returns: generic_time_waveform - the filtered waveform
        """
        a, c = Waveform.AC_Filter_Design(self.sample_rate)

        return self.apply_iir_filter(a[0], a[1])

    def apply_c_weight(self):
        """
        This function specifically applies the a-weighting filter to the acoustic data, and returns a new waveform with
        the filter applied.

        :returns: generic_time_waveform - the filtered waveform
        """
        a, c = Waveform.AC_Filter_Design(self.sample_rate)

        return self.apply_iir_filter(c[0], c[1])

    def apply_lowpass(self, cutoff: float, order: int = 4):
        """
        This function applies a Butterworth filter to the samples within this class.

        :param cutoff: double - the true frequency in Hz
        :param order: double (default: 4) - the order of the filter that will be created and applied

        :returns: generic_time_waveform - the filtered waveform
        """

        #   Determine the nyquist frequency

        nyquist = self.sample_rate / 2.0

        #   Determine the normalized frequency

        normalized_cutoff = cutoff / nyquist

        #   Design the filter

        b, a = scipy.signal.butter(order, normalized_cutoff, btype='low', analog=False, output='ba')

        #   Filter the data and return the new waveform object

        return self.apply_iir_filter(b, a)

    def apply_highpass(self, cutoff: float, order: int = 4):
        """
        This function applies a Butterworth filter to the samples within this class.

        :param cutoff: double - the true frequency in Hz
        :param order: double (default: 4) - the order of the filter that will be created and applied

        :returns: Waveform - the filtered waveform
        """

        #   Determine the nyquist frequency

        nyquist = self.sample_rate / 2.0

        #   Determine the normalized frequency

        normalized_cutoff = cutoff / nyquist

        #   Design the filter

        b, a = scipy.signal.butter(order, normalized_cutoff, btype='high', analog=False, output='ba')

        #   Filter the data and return the new waveform object

        return self.apply_iir_filter(b, a)

    def apply_bandpass(self, low_cutoff: float, high_cutoff: float, order: int = 3):
        """
        This function determines the bandpass Butterworth filter coefficients and sends them and the current waveform
        into the function that will filter the data with an IIR filter coefficient set

        Parameters
        ----------
        low_cutoff: float - the regular frequency cutoff for the low edge of the band pass filter (Units: Hz)
        high_cutoff: float - the regular frequency cutoff for the upper edge of the band pass filter (Units: Hz)
        order: int - default: 3, the order of the filter
        """

        #   Determine the nyquist frequency for the upper and lower edges of the band
        nyquist = self.sample_rate / 2.0
        upper = high_cutoff / nyquist
        lower = low_cutoff / nyquist

        #   Design the filter
        b, a = scipy.signal.butter(order, [lower, upper], btype='bandpass', analog=False, output='ba')

        #   send this waveform and the coefficients into the filtering algorithm and return the filtered waveform
        return self.apply_iir_filter(b, a)

    def resample(self, new_sample_rate: int):
        """
        This function resamples the waveform and returns a new object with the correct sample rate and sample count.
        This function employs the resample function within scipy.signal to conduct the resampling.

        Parameters
        ----------
        new_sample_rate: int - the new sample rate that we want to create a signal for

        Returns
        -------
        Waveform - the new waveform object that contains the resampled data with the new sample rate.
        """

        #   Determine the ratio of the current sample rate to the new sample rate

        sr_ratio = new_sample_rate / self.sample_rate

        return Waveform(scipy.signal.resample(self.samples, int(np.floor(len(self.samples) * sr_ratio))),
                        new_sample_rate, self.start_time)

    def apply_tob_equalizer_filter(self, frequencies: np.ndarray, sound_pressure_levels: np.ndarray):
        from .spectral.fractional_octave_band import FractionalOctaveBandTools as fob
        import warnings

        """
        Pass the waveform through a series of filters adjusting the amplitude by the adjusted value of the arrays.

        Parameters
        ----------
        frequencies: np.ndarray - the collection of frequencies to generate filters
        sound_pressure_levels: np.ndarray - the collection of sound pressure levels to adjust the amplitude

        Returns
        -------
        Waveform - the summation of the n Waveforms that are generated by each of the filters.
        """
        #   Adjust the sound pressure level array by the average
        magnitude = sound_pressure_levels - np.mean(sound_pressure_levels)

        #   Determine the center frequency of the highest octave containing the upper frequency
        full_band = int(np.floor(fob.nearest_band(1, frequencies[-1])))

        #   Now determine the upper edge of this full octave band
        f_hi = fob.upper_frequency(1, full_band)
        f_lo = fob.lower_frequency(1, full_band)

        #   With this information we can determine the band number of the highest one-third-octave band in this full
        #   octave band. This is used to determine the filter collection.
        b_coefficients = list()
        a_coefficients = list()

        f_band = int(np.floor(fob.nearest_band(3, f_hi)))

        #   Create the collection of samples that we will add the output of the filter to create the final object
        samples = np.zeros((len(self.samples),))

        #   Now loop through the bands until we exit this full octave band
        while fob.lower_frequency(3, f_band) >= f_lo * 0.9:
            #   Define the window for the bandpass filter
            upper = fob.upper_frequency(3, f_band)
            lower = fob.lower_frequency(3, f_band)
            window = np.array([lower, upper]) / self.sample_rate / 2.0

            #   Create the filter coefficients for this frequency band and add it to the list for each coefficient set
            b, a = scipy.signal.butter(
                3,
                window,
                btype='bandpass',
                analog=False,
                output='ba'
            )

            b_coefficients.append(b)
            a_coefficients.append(a)

            #   Decrement the band number to move to the next band down.
            f_band -= 1

            #   With that we now need to determine the limits of the band calculations
            #   Determine the octave bands that will need to be calculated to cover the desired frequency range.
            low_band = int(np.floor(fob.nearest_band(1, frequencies[0])))
            hi_band = int(np.floor(fob.nearest_band(1, frequencies[-1])))

            #   Get the index of the band at the top of the full octave filter
            fob_band_index = int(np.floor(fob.nearest_band(3, fob.upper_frequency(1, hi_band))))

            #   Make a copy of the waveform that can be decimated
            wfm = Waveform(pressures=self.samples.copy(),
                           sample_rate=self.sample_rate,
                           start_time=self.start_time)

            #   Loop through the frequencies
            for band_index in range(hi_band, low_band - 1, -1):
                #   Loop through the filter definitions
                for filter_index in range(len(b_coefficients)):
                    filtered_waveform = wfm.apply_iir_filter(b_coefficients[filter_index], a_coefficients[filter_index])

                    band_index -= 1

                    #   Up sample the waveform
                    while filtered_waveform.sample_rate < self.sample_rate:
                        filtered_waveform = filtered_waveform.resample(filtered_waveform.sample_rate * 2)

                    #   Apply the amplification factor to the data
                    filtered_waveform.scale_signal(magnitude[band_index], scale_type=ScalingMethods.logarithmic)

                    #   Add the contents of the waveform to the sample list
                    if (fob.center_frequency(3, band_index) <= frequencies[-1]) and \
                            (fob.center_frequency(3, band_index) >= frequencies[0]):
                        samples += filtered_waveform.samples[:len(samples)]

                    #   Decimate the waveform, halving the sample rate and making the filter definitions move down a
                    #   full octave
                    if len(wfm.samples) / 2 < 3 * len(b_coefficients):
                        warnings.warn(
                            "The number of points within the Waveform are insufficient to calculate digital filters "
                            "lower than these frequencies")

                        break

                    wfm = Waveform(pressures=scipy.signal.decimate(wfm.samples, 2),
                                   sample_rate=wfm.sample_rate,
                                   start_time=wfm.start_time)

        return Waveform(pressures=samples, sample_rate=self.sample_rate, start_time=self.start_time)

    def is_calibration(self):
        """
        This function examines the samples and determines whether the single contains a single pure tone.  If it does
        the function returns the approximate frequency of the tone.  This will examine every channel and determine
        whether each channel is a calibration tone

        :returns: bool - flag determining whether the signal was pure tone
                  float - the approximate frequency of the pure tone
        """

        calibration = None
        freq = None

        #   Loop through the channels

        #   To remove high frequency transients, we pass the signal through a 2 kHz low pass filter

        wfm = Waveform(self.samples, self.sample_rate, self.start_time)
        wfm.apply_lowpass(2000)

        peaks = scipy.signal.find_peaks(wfm.samples, height=0.8 * np.max(self.samples))[0]

        if len(peaks) >= 2:
            calibration = False
            freq = -1

            #   Determine the distance between any two adjacent peaks

            distance_sample = np.diff(peaks)

            #   Determine the distance between the samples in time

            distance_time = distance_sample / self.sample_rate

            #   Determine the frequencies

            frequencies = 1 / distance_time

            freq = np.mean(frequencies)

            calibration = (abs(freq - 1000) < 0.1 * 1000) or \
                          (abs(freq - 250) < 0.1 * 250)

        return calibration, freq

    def get_features(self, include_sq_metrics: bool = True):
        """
        This function calculates the various features within the global time analysis and stores the results in the
        class object.  At the end, a dictionary of the values is available and returned to the calling function.

        Returns
        -------
        features : dict()
            The dictionary containing the various values calculated within this method.
        """

        #   Create the dictionary that will hold the data for return to the user

        features = {'attack': self.attack,
                    'decrease': self.decrease,
                    'release': self.release,
                    'log_attack': self.log_attack,
                    'attack slope': self.attack_slope,
                    'decrease slope': self.decrease_slope,
                    'temporal centroid': self.temporal_centroid,
                    'effective duration': self.effective_duration,
                    'amplitude modulation': self.amplitude_modulation,
                    'frequency modulation': self.frequency_modulation,
                    'auto-correlation': self.auto_correlation,
                    'zero crossing rate': self.zero_crossing_rate}

        if include_sq_metrics:
            features['loudness'] = self.loudness
            features['roughness'] = self.roughness
            features['sharpness'] = self.sharpness

        return features

    def calculate_temporal_centroid(self):

        env_max_idx = np.argmax(self.signal_envelope)
        over_threshold_idcs = np.where(self.normal_signal_envelope > self.centroid_threshold)[0]

        over_threshold_start_idx = over_threshold_idcs[0]
        if over_threshold_start_idx == env_max_idx:
            over_threshold_start_idx = over_threshold_start_idx - 1

        over_threshold_end_idx = over_threshold_idcs[-1]

        over_threshold_TEE = self.signal_envelope[over_threshold_start_idx - 1:over_threshold_end_idx - 1]
        over_threshold_support = [*range(len(over_threshold_TEE))]
        over_threshold_mean = np.divide(np.sum(np.multiply(over_threshold_support, over_threshold_TEE)),
                                        np.sum(over_threshold_TEE))

        temporal_threshold = ((over_threshold_start_idx + 1 + over_threshold_mean) / self.sample_rate)

        return temporal_threshold

    def calculate_effective_duration(self):

        env_max_idx = np.argmax(self.signal_envelope)
        over_threshold_idcs = np.where(self.normal_signal_envelope > self.effective_duration_threshold)[0]

        over_threshold_start_idx = over_threshold_idcs[0]
        if over_threshold_start_idx == env_max_idx:
            over_threshold_start_idx = over_threshold_start_idx - 1

        over_threshold_end_idx = over_threshold_idcs[-1]

        return (over_threshold_end_idx - over_threshold_start_idx + 1) / self.sample_rate

    # def rms_envelope(self):
    #
    #     win_size = int(round(self._window_size_seconds * self.sample_rate))
    #     hop_size = int(round(self._hop_size_seconds * self.sample_rate))
    #     t_support = [*range(0, int(round(hop_size * np.floor((len(self.samples) - win_size) / hop_size))), hop_size)]
    #     value = []
    #     for i in range(len(t_support)):
    #         a = self.samples[np.subtract(np.add(t_support[i], [*range(1, win_size + 1)]), 1).astype(int)]
    #         value.append(np.sqrt(np.mean(np.power(a, 2))))
    #     t_support = np.divide(np.add(t_support, np.ceil(np.divide(win_size, 2))), self.sample_rate)
    #     return value

    def instantaneous_temporal_features(self):
        """
        This function will calculate the instantaneous features within the temporal analysis.  This includes the
        auto-correlation and the zero crossing rate.
        """
        count = 0
        temporal_feature_times = np.zeros(
            (int(np.floor((len(self.samples) - self.window_size_samples) / self.hop_size_samples) + 1),))

        auto_coefficients = np.zeros((len(temporal_feature_times), self.coefficient_count))
        zero_crossing_rate = np.zeros((len(temporal_feature_times),))

        #   Loop through the frames

        for n in range(0, len(temporal_feature_times)):
            #   Get the frame

            frame_length = self.window_size_samples
            start = n * self.hop_size_samples
            frame_index = np.arange(start, frame_length + start)
            f_Frm_v = self.samples[frame_index] * np.hamming(self.window_size_samples)
            temporal_feature_times[n] = n * self.hop_size_seconds

            count += 1

            #   Calculate the auto correlation coefficients

            auto_coefficients[n, :] = sm.tsa.acf(f_Frm_v, nlags=self.coefficient_count, fft=False)[1:]

            #   Now the zero crossing rate

            i_Sign_v = np.sign(f_Frm_v - np.mean(f_Frm_v))
            i_Zcr_v = np.where(np.diff(i_Sign_v))[0]
            i_Num_Zcr = len(i_Zcr_v)
            zero_crossing_rate[n] = i_Num_Zcr / (len(f_Frm_v) / self.sample_rate)

        return temporal_feature_times, auto_coefficients, zero_crossing_rate

    def calculate_modulation(self):
        """
        Calculate the frequency/amplitude modulations of the signal.  This can be accomplished with either a Fourier or
        Hilbert method.

        Returns
        -------

        frequency_modulation : double
            A metric measuring the frequency modulation of the signal
        amplitude_modulation : double
            A metric measuring the amplitude modulation of the signal
        """

        sample_times = np.arange(len(self.signal_envelope) - 1) / self.sample_rate

        sustain_start_time = self._Addresses[1]
        sustain_end_time = self._Addresses[4]

        is_sustained = False

        if (sustain_end_time - sustain_start_time) > 0.02:
            pos_v = np.where((sustain_start_time <= sample_times) & (sample_times <= sustain_end_time))[0]
            if len(pos_v) > 0:
                is_sustained = True

        if not is_sustained:
            amplitude_modulation = 0
            frequency_modulation = 0
        else:
            envelop_v = self.signal_envelope[pos_v]
            temps_sec_v = sample_times[pos_v]
            M = np.mean(envelop_v)

            #   Taking the envelope

            mon_poly = np.polyfit(temps_sec_v, np.log(envelop_v), 1)
            hat_envelope_v = np.exp(np.polyval(mon_poly, temps_sec_v))
            signal_v = envelop_v - hat_envelope_v

            sa_v = scipy.signal.hilbert(signal_v)
            sa_amplitude_v = abs(signal_v)
            sa_phase_v = np.unwrap(np.angle(sa_v))
            sa_instantaneous_frequency = (1 / 2 / np.pi) * sa_phase_v / (len(temps_sec_v) / self.sample_rate)

            amplitude_modulation = np.median(sa_amplitude_v)
            frequency_modulation = np.median(sa_instantaneous_frequency)

        return frequency_modulation, amplitude_modulation

    def calculate_log_attack(self):
        """
        This calculates the various global attributes.

        In some cases the calculation of the attack did not return an array, so the error is trapped for when a
        single values is returned rather than an array.

        20230318 - FSM - According to the paper on the Timbre Toolbox, the thresholds were to be estimated on the
        maximum value of the energy envelope, not the values at the start and end of the attack. This was addressed
        in the determination of the value of the threshold.

        Returns
        -------
        attack_start : TYPE
            DESCRIPTION.
        log_attack_time : TYPE
            DESCRIPTION.
        attack_slope : TYPE
            DESCRIPTION.
        attack_end : TYPE
            DESCRIPTION.
        release : TYPE
            DESCRIPTION.
        release_slope : TYPE
            DESCRIPTION.

        """

        #   Define some specific constants for this calculation
        method = 3
        noise_threshold = 0.15
        decrease_threshold = 0.4
        percent_step = 0.1

        #   Detection of the start (start_attack_position) and stop (end_attack_position) of the attack
        position_value = np.where(self.normal_signal_envelope > noise_threshold)[0]

        #   Determine the start and stop positions based on selected method
        #   Methods 1 and 2 are using fixed thresholds to estimate the end position. According to Peeters,
        #   these are found insufficiently robust with real signals. As such he proposed a "weakest-effort method" in
        #   2004 to estimate the indices for the start and stop of the attack.
        if method == 1:  # Equivalent to a value of 80%
            start_attack_position = position_value[0]
            end_attack_position = position_value[int(np.floor(0.8 / percent_step))]
        elif method == 2:  # Equivalent to a value of 100%
            start_attack_position = position_value[0]
            end_attack_position = position_value[int(np.floor(1.0 / percent_step))]
        elif method == 3:
            #   Calculate the position for each threshold
            percent_value_value = np.arange(percent_step, 1 + percent_step, percent_step)
            percent_value_position = np.zeros(percent_value_value.shape)

            for p in range(len(percent_value_value)):
                percent_value_position[p] = np.where(self.normal_signal_envelope >= percent_value_value[p])[0][0]

            #   Define parameters for the calculation of the search for the start and stop of the attack
            #
            #   The terminations for the mean calculation
            m1 = int(round(0.3 / percent_step)) - 1
            m2 = int(round(0.6 / percent_step))

            #   define the multiplicative factor for the effort
            multiplier = 3

            #   Terminations for the start attack correction
            s1att = int(round(0.1 / percent_step)) - 1
            s2att = int(round(0.3 / percent_step))

            #   Terminations for the end attack correction
            e1att = int(round(0.5 / percent_step)) - 1
            e2att = int(round(0.9 / percent_step))

            #   Calculate the effort as the effective difference in adjacent position values
            percent_position_value = np.diff(percent_value_position)

            #   Determine the average effort
            M = np.mean(percent_position_value[m1:m2])

            #   Start the start attack calculation
            #   we start just after the effort to be made (temporal gap between percent) is too large
            position2_value = np.where(percent_position_value[s1att:s2att] > multiplier * M)[0]

            if len(position2_value) > 0:
                index = int(np.floor(position2_value[-1] + s1att))
            else:
                index = int(np.floor(s1att))

            start_attack_position = percent_value_position[index]

            #   refinement: we are looking for the local minimum
            delta = int(np.round(0.25 * (percent_value_position[index + 1] - percent_value_position[index]))) - 1
            n = int(np.floor(percent_value_position[index]))

            if n - delta >= 0:
                min_position = np.argmin(self.normal_signal_envelope[n - delta:n + delta])
                start_attack_position = min_position + n - delta - 1

            #   Start the end attack calculation
            #   we STOP JUST BEFORE the effort to be made (temporal gap between percent) is too large
            position2_value = np.where(percent_position_value[e1att:e2att] > multiplier * M)[0]

            if len(position2_value) > 0:
                index = int(np.floor(position2_value[0] + e1att))
            else:
                index = int(np.floor(e1att))

            end_attack_position = percent_value_position[index]

            #   refinement: we are looking for the local minimum
            delta = int(np.round(0.25 * (percent_value_position[index] - percent_value_position[index - 1])))
            n = int(np.floor(percent_value_position[index]))

            if n - delta >= 0:
                min_position = np.argmax(self.normal_signal_envelope[n - delta:n + delta + 1])
                end_attack_position = min_position + n - delta

        #   Calculate the Log-attack time
        if start_attack_position == end_attack_position:
            start_attack_position -= 1

        rise_time_n = end_attack_position - start_attack_position
        log_attack_time = np.log10(rise_time_n / self.sample_rate)

        #   Calculate the temporal growth - New 13 Jan 2003
        #   weighted average (Gaussian centered on percent=50%) slopes between start_attack_position and
        #   end_attack_position
        start_attack_position = int(np.round(start_attack_position))
        end_attack_position = int(np.round(end_attack_position))
        start_attack_value = self.normal_signal_envelope[start_attack_position]
        end_attack_value = self.normal_signal_envelope[end_attack_position]

        #   Now that we have determined where the attack occurs, we must define a set of thresholds as a proportion
        #   of the maximum pf the energy envelop. To ensure that the value is within the attack range, we seek for
        #   the maximum within this region.
        threshold_value = np.arange(0.1, 1.1, 0.1)
        threshold_value *= np.max(self.normal_signal_envelope[start_attack_position:end_attack_position])
        threshold_position_seconds = np.zeros(np.size(threshold_value))
        for i in range(len(threshold_value)):
            #   Find the index within the envelope where the value is greater than the selected threshold value
            idx = np.where(self.normal_signal_envelope[start_attack_position:end_attack_position] >=
                           threshold_value[i])[0]

            if len(idx) > 0:
                threshold_position_seconds[i] = idx[0] / self.sample_rate

        slopes = np.divide(np.diff(threshold_value), np.diff(threshold_position_seconds) + sys.float_info.epsilon)

        #   Calculate the increase
        thresholds = (threshold_value[:-1] + threshold_value[1:]) / 2
        weights = np.exp(-(thresholds - 0.5) ** 2 / (0.5 ** 2))
        increase = np.sum(np.dot(slopes, weights)) / np.sum(weights)

        #   Calculate the time decay

        envelope_max_index = np.where(self.normal_signal_envelope == np.max(self.normal_signal_envelope))[0]
        envelope_max_index = int(np.round(0.5 * (envelope_max_index + end_attack_position)))

        stop_position = np.where(self.normal_signal_envelope > decrease_threshold)[0][-1]

        if envelope_max_index == stop_position:
            if stop_position < len(self.normal_signal_envelope):
                stop_position += 1
            elif envelope_max_index > 1:
                envelope_max_index -= 1

        #   Calculate the decrease

        X = np.arange(envelope_max_index, stop_position) / self.sample_rate
        X_index = np.arange(envelope_max_index, stop_position)
        Y = np.log(self.normal_signal_envelope[X_index])
        polynomial_fit = np.polyfit(X, Y, 1)
        decrease = polynomial_fit[0]

        #   Create the list of addresses that we are interested in storing for later consumption

        addresses = np.array([start_attack_position, envelope_max_index, 0, 0, stop_position]) / self.sample_rate

        return log_attack_time, increase, decrease, addresses

    def equivalent_level(self,
                         weighting: WeightingFunctions = WeightingFunctions.a_weighted,
                         equivalent_duration: float = 8 * 3600,
                         start_sample: int = 0,
                         stop_sample: int = None,
                         leq_mode: LeqDurationMode = None,
                         exposure_duration: float = None):
        """
        This function computes the equivalent level on the pressures within the waveform. If there is a weighting
        function specified this is applied before the pressures are summed. Additionally, the duration of the summation
        is specified (in seconds) for the new value with a default of 8 hours. Finally, if there is a cause to exclude
        portions of the data (i.e. calculating the SEL for the 10 dB down points in community noise) you can specify
        the start and stop index. If the stop index is None, then the last pressure defines the limit of the summation.

        Parameters
        ----------
        :param weighting:   WeightingFunctions
            The enumeration to determine filtering function applied to the waveform
        :param equivalent_duration :   float
            The denominator of the summation - in seconds - representing the desired length of total exposure
            time (e.g. an 8-hour duty day, or a 1-second sound exposure level)
        :param start_sample :   int
            default = 0. The start sample of the pressure summation
        :param stop_sample :   int
            default = None. The stop sample, if the value is None, then it is replaces with the last sample index
        :param leq_mode :   LeqDurationMode
            The enumeration to determine whether the input signal contains all energy
            of an exposure to the listener (transient) or the signal represents a sample of a longer-duration
            (steady_state) exposure
        :param exposure_duration :   float
            If leq_mode is steady_state, this is the actual time of noise exposure to the
            listener in seconds

        """

        if stop_sample is None:
            stop_sample = len(self.samples)

        number_of_samples = stop_sample - start_sample
        signal_duration = number_of_samples / self.sample_rate

        if weighting == WeightingFunctions.unweighted:
            s = np.sum(self.samples[start_sample:stop_sample] ** 2, axis=0)
        elif weighting == WeightingFunctions.a_weighted:
            s = np.sum(self.apply_a_weight().samples[start_sample:stop_sample] ** 2, axis=0)
        elif weighting == WeightingFunctions.c_weighted:
            s = np.sum(self.apply_c_weight().samples[start_sample:stop_sample] ** 2, axis=0)

        total_energy_in_signal = s / self.sample_rate

        if leq_mode == LeqDurationMode.transient:
            total_energy_of_exposure = total_energy_in_signal
        elif leq_mode == LeqDurationMode.steady_state:
            if exposure_duration is None:
                exposure_duration = signal_duration
            total_energy_of_exposure = total_energy_in_signal * (exposure_duration / signal_duration)
        elif leq_mode is None:
            raise ValueError("User must specify a signal duration mode of class LeqDurationMode.")

        average_energy_over_equivalent_duration = total_energy_of_exposure / equivalent_duration

        return 10.0 * np.log10(average_energy_over_equivalent_duration / 20e-6 / 20e-6)

    def overall_level(self, integration_time: float = None,
                      weighting: WeightingFunctions = WeightingFunctions.unweighted):
        """
        Integrate the levels within the waveform to generate the weighted level. This will permit different weighting
        functions to be applied before the calculation of the overall level.

        Parameters
        ----------
        integration_time: float, default: None - The amount of time that we will collect prior to determining the
            RMS level within the samples.
        weighting: weighting_function, default: unweighted - the weighting to be applied prior to determining the RMS
            value of the signal.

        Returns
        -------
        float, array-like - A collection of the overall levels, with applicable weighting, with the number being equal
            to the int(np.floor(duration / integration_time))

        Revision
        20221007 - FSM - updated the method when the start_time is a datetime rather than a floating point value
        """

        if integration_time is None:
            n = 1
            integration_time = self.duration
        else:
            n = int(np.floor(self.duration / integration_time))

        if weighting == WeightingFunctions.a_weighted:
            wfm = self.apply_a_weight()
        elif weighting == WeightingFunctions.c_weighted:
            wfm = self.apply_c_weight()
        else:
            wfm = Waveform(self.samples, self.sample_rate, self.start_time)
        level = list()

        t0 = self.start_time
        if isinstance(t0, datetime):
            t0 = 60 * (60 * t0.hour + t0.minute) + t0.second + t0.microsecond / 1e6

        for i in range(n):
            subset = wfm.trim(t0, t0 + integration_time, TrimmingMethods.times_absolute)
            level.append(np.std(subset.samples))

            t0 += integration_time

        return 20 * np.log10(np.array(level) / 20e-6)

    def cross_correlation(self, b, mode=CorrelationModes.valid, lag_limit=None):
        """
        This function determines the cross correlation between the current waveform and the waveform passed to the
        function.

        Parameters
        ----------
        b: Waveform - the signal to compare to the current waveform's samples
        mode: correlation_mode - the mode of the correlation that we want to execute for the correlation methods
        lag_limit: - the limit of the correlation analysis

        Returns
        -------

        value of the maximum correlation
        sample lag of the maximum correlation

        Remarks
        2022-12-01 - FSM - Added completed enumeration usage for different correlation modes
        """

        # TODO - @Alan - we need a test for this function.

        if not isinstance(b, Waveform):
            raise ValueError("The first argument is required to be a Waveform object")

        sig = b.samples
        ref_sig = self.samples
        if len(sig) > len(ref_sig):
            sig, ref_sig = ref_sig, sig

        M = len(ref_sig)
        N = len(sig)

        if lag_limit is None:
            correlation_values = np.correlate(ref_sig, sig, mode.name)
            if mode == CorrelationModes.valid:
                lags = np.arange(0, max(M, N) - min(M, N) + 1)
            elif mode == CorrelationModes.full:
                lags = np.arange(-(N - 1), M)
            elif mode == CorrelationModes.same:
                lags = np.arange(-np.floor(N / 2), M - np.floor(N / 2))
        else:
            ref_sig_pad = np.pad(ref_sig.conj(), lag_limit, mode='constant')
            correlation_values = np.zeros(2 * lag_limit + 1)
            for i in range(0, 2 * lag_limit + 1):
                correlation_values[i] = sum(ref_sig_pad[i:len(sig) + i] * sig)
            lags = np.arange(-lag_limit, lag_limit + 1)

        return np.max(correlation_values), lags[np.argmax(correlation_values)]

    def resample(self, new_sample_rate: int):
        """
        This function resamples the waveform and returns a new object with the correct sample rate and sample count.
        This function employs the resample function within scipy.signal to conduct the resampling.

        Parameters
        ----------
        new_sample_rate: int - the new sample rate that we want to create a signal for

        Returns
        -------
        Waveform - the new waveform object that contains the resampled data with the new sample rate.
        """

        #   Determine the ratio of the current sample rate to the new sample rate

        sr_ratio = new_sample_rate / self.sample_rate

        return Waveform(scipy.signal.resample(self.samples, int(np.floor(len(self.samples) * sr_ratio))),
                        new_sample_rate, self.start_time)

    def concatenate(self, wfm):
        """
        This will create a new audio file that contains the data from the current Waveform and adds the samples from the
        new Waveform to the list and then returns a new object.

        Parameters
        ----------
        :param wfm: This is the Waveform that we want to concatenate with the current samples

        Returns
        -------
        A new waveform that contains the audio from the argument tacked onto the end of the samples from the current
        waveform.
        """

        new_samples = np.concatenate([self.samples, wfm.samples])
        return Waveform(new_samples, self.sample_rate, self.start_time)

    #   ----------------------------------------------- Operators ------------------------------------------------------

    def __add__(self, other):
        """
        This function will add the contents of one waveform to the other. This feature checks the sample rate to ensure
        that they both possess the same sample times. Also, if the data starts at different times, this function will
        create a new object that is the addition of the samples, with the new sample times.

        Parameters
        ----------
        :param other: Waveform - the new object to add to this class's data

        Returns
        -------
        :returns: - A new Waveform object that is the sum of the two
        """

        warnings.warn(
            message='waveform.add not yet tested. Use at your own risk.'
        )

        if not isinstance(other, Waveform):
            ValueError("You must provide a new Waveform object to add to this object.")

        if self.sample_rate != other.sample_rate:
            ValueError("At this time, the two waveforms must possess the same sample rate to add them together")

        s0 = int(other.start_time * other.sample_rate)
        s1 = s0 + len(other.samples)

        return Waveform(self.samples[s0:s1] + other.samples, self.sample_rate, self.start_time)

    def __sub__(self, other):
        """
        This function subtracts another Waveform object from the current object and returns the value as a new
        Waveform. If the start times, durations, or sample rates are not equal then the function returns a ValueError

        """

        if self.start_time != other.start_time or self.duration != other.duration or self.sample_rate != \
                other.sample_rate:
            raise ValueError("The meta-data of these two waveforms is inconsistent making it impossible to know how "
                             "to subtract the information in the pressures.")

        return Waveform(self.samples - other.samples, self.sample_rate, self.start_time, False)
