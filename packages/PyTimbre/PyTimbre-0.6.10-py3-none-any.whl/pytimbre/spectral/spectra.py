import sys
import warnings
import datetime
import numpy as np
import scipy.fft
import scipy.signal
from .fractional_octave_band import FractionalOctaveBandTools as fob_tools
from ..waveform import Waveform
from .acoustic_weights import AcousticWeights
from scipy.signal import find_peaks


class Spectrum:
    """
    This is the base class that defines the structure of the spectrum object. It does not calculate the frequency
    spectrum from a waveform, but can be used to represent a single spectrum that was previously created.

    Remarks
    2022-12-13 - FSM - Added a function to calculate the sound quality metrics based on the frequency spectrum

    """

    def __init__(self, a: Waveform = None):
        """
        The default constructor that builds the information within the Spectrum class based on the contents of the
        object "a".

        Parameters
        ----------
        a: Waveform - the acoustic samples that define the source of the time-domain information that we are interested
        in processing
        """

        self._waveform = a
        self._frequencies = None
        self._acoustic_pressures_pascals = None
        self._time0 = None

        self._bandwidth = None
        self._f0 = None
        self._f1 = None

        if a is not None:
            self._time0 = self.waveform.start_time

            if len(a.samples.shape) > 1:
                self._waveform.samples = self._waveform.samples.reshape((-1,))

        self._fft_size = 4096
        self._window_size_seconds = 0.0232
        self._hop_size_seconds = 0.0058
        self._window_size = self._window_size_seconds * self.sample_rate
        self._hop_size = self.hop_size_seconds * self.sample_rate

        self.bin_size = self.sample_rate / self._fft_size
        self.sample_rate_x = self.sample_rate / self.hop_size
        self.sample_rate_y = self._fft_size / self.sample_rate_x
        self.window = np.hamming(self.window_size)
        self.window_overlap = self.window_size - self.hop_size

        #   Define the features

        self.centroid = None
        self._mean_center = None
        self.spread = None
        self.skewness = None
        self.kurtosis = None
        self.slope = None
        self.decrease = None
        self.roll_off = None
        self.energy = None
        self.flatness = None
        self.crest = None
        self.probability_distribution = None
        self.integration_variable = None
        self.geometric_mean = None
        self.arithmetic_mean = None
        self.pitch_threshold = 0.01
        self.partial_frequencies_indices = None
        self._fundamental_frequency = None
        self._harmonic_energy = None
        self._noise_energy = None
        self._noisiness = None
        self._tri_stimulus = None
        self._harmonic_spectral_deviation = None
        self._odd_even_ratio = None
        self._inharmonicity = None

    #   ------------------------------------------ Protected functions -------------------------------------------------

    def _calculate_spectrum(self):
        import warnings

        warnings.warn("This function does nothing. You will need to implement this function in the child class to build"
                      "the spectrum with the correct units and format.")

        raise ValueError('This method must be implemented and assigned frequencies within the calculation '
                         'of each type of spectrum class.')

    #   ------------------------------------- Class properties ---------------------------------------------------------

    @property
    def waveform(self):
        if self._waveform is None:
            warnings.warn('No Waveform object has been passed to this Spectrum object.')
        return self._waveform

    @property
    def signal(self):
        return self.waveform.samples

    @property
    def sample_rate(self):
        if self._waveform is None:
            return 48000
        else:
            return self.waveform.sample_rate

    @property
    def duration(self):
        if self._waveform is None:
            raise AttributeError("No waveform has been provided to the Spectrum object.")
        return self.waveform.duration

    @property
    def time(self):
        if self._time0 is None:
            raise AttributeError("No time object has been provided to the Spectrum object.")
        return self._time0

    @property
    def time_past_midnight(self):
        if self._time0 is None:
            raise AttributeError("No time has been provided to the Spectrum object.")

        if isinstance(self._time0, datetime.datetime):
            return 60 * (60 * self._time0.hour + self._time0.minute) + self._time0.second + \
                float(self._time0.microsecond / 1e6)
        else:
            return self._time0

    @property
    def frequencies(self):
        if self._frequencies is None:
            self._calculate_spectrum()

        return self._frequencies

    @frequencies.setter
    def frequencies(self, values):
        self._frequencies = values

    @property
    def pressures_pascals(self):
        if self._frequencies is None or self._acoustic_pressures_pascals is None:
            self._calculate_spectrum()

        return self._acoustic_pressures_pascals

    @pressures_pascals.setter
    def pressures_pascals(self, values):
        self._acoustic_pressures_pascals = values

    @property
    def pressures_decibels(self):
        return 20 * np.log10(self.pressures_pascals / 20e-6)

    @property
    def overall_level(self):
        """
        Overall sound pressure level, unweighted (i.e. flat weighted, Z-weighted).  Calculated as the energetic sum
        of the power spectrum.
        """
        return AcousticWeights.lf(self.pressures_decibels)

    @property
    def overall_a_weighted_level(self):
        """
        A-weighted overall sound pressure level.  Calculated as the energetic sum
        of the A-weighted power spectrum.
        """

        return AcousticWeights.la(self.pressures_decibels, self.frequencies)[0]

    @property
    def perceived_noise_level(self):
        spl = self.pressures_decibels
        while len(spl) < 31:
            spl = np.concatenate([[0], spl])
        return AcousticWeights.pnl(spl)

    @property
    def fractional_octave_bandwidth(self):
        return self._bandwidth

    @fractional_octave_bandwidth.setter
    def fractional_octave_bandwidth(self, value):
        self._bandwidth = value

    @property
    def start_fractional_octave_frequency(self):
        return self._f0

    @start_fractional_octave_frequency.setter
    def start_fractional_octave_frequency(self, value):
        self._f0 = value

    @property
    def stop_fractional_octave_frequency(self):
        return self._f1

    @stop_fractional_octave_frequency.setter
    def stop_fractional_octave_frequency(self, value):
        self._f1 = value

    @property
    def narrowband_frequency_count(self):
        return self._fft_size

    @narrowband_frequency_count.setter
    def narrowband_frequency_count(self, value):
        self._fft_size = value

        self.bin_size = self.sample_rate / self._fft_size
        self.sample_rate_x = self.sample_rate / self.hop_size
        self.sample_rate_y = self._fft_size / self.sample_rate_x
        self.window = np.hamming(self.window_size)
        self.window_overlap = self.window_size - self.hop_size

    @property
    def roughness(self):
        from mosqito.sq_metrics import roughness_dw_freq

        return roughness_dw_freq(spectrum=self.pressures_decibels, freqs=self.frequencies)[0]

    @property
    def loudness(self):
        from mosqito.sq_metrics import loudness_zwst_freq

        return loudness_zwst_freq(self.pressures_decibels, self.frequencies)

    @property
    def sharpness(self):
        from mosqito.sq_metrics import sharpness_din_freq

        return sharpness_din_freq(self.pressures_decibels, self.frequencies)

    @property
    def hop_size_seconds(self):
        return self._hop_size_seconds

    @hop_size_seconds.setter
    def hop_size_seconds(self, value: float):
        self._hop_size_seconds = value
        self.hop_size = int(np.floor(self.hop_size_seconds * self.sample_rate))
        self.sample_rate_x = self.sample_rate / self.hop_size
        self.window_overlap = self.window_size - self.hop_size

    @property
    def window_size(self):
        return int(np.floor(self._window_size))

    @window_size.setter
    def window_size(self, value: int):
        self._window_size = value
        self._window_size_seconds = self.window_size / self.sample_rate
        self.window = np.hamming(self.window_size)
        self.window_overlap = self.window_size - self.hop_size

    @property
    def hop_size(self):
        return int(np.floor(self._hop_size))

    @hop_size.setter
    def hop_size(self, value: int):
        self._hop_size = value
        self.hop_size_seconds = self._hop_size / self.sample_rate
        self.sample_rate_x = self.sample_rate / self._hop_size
        self.window_overlap = self.window_size - self._hop_size

    @property
    def spectral_centroid(self):
        """
        Spectral centroid represents the spectral center of gravity.
        """

        if self.centroid is None:
            if self._acoustic_pressures_pascals is None and self._frequencies is None:
                self._calculate_spectrum()

            if self.probability_distribution is None or self.integration_variable is None:
                self._calculate_normalized_distribution()

            self.centroid = np.sum(self.integration_variable * self.probability_distribution, axis=0)

        return self.centroid

    @property
    def spectral_spread(self):
        """
        Spectral spread or spectral standard-deviation represents the spread of the spectrum around its mean value.
        """
        if self.mean_center is None:
            self._calculate_mean_center()

        if self.probability_distribution is None or self.integration_variable is None:
            self._calculate_normalized_distribution()

        if self.spread is None:
            self.spread = np.sqrt(np.sum(self.mean_center ** 2 * self.probability_distribution, axis=0))

        return self.spread

    @property
    def spectral_skewness(self):
        """
        Spectral skewness gives a measure of the asymmetry of the spectrum around its mean value. A value of 0 indicates
        a symmetric distribution, a value < 0 more energy at frequencies lower than the mean value, and values > 0 more
        energy at higher frequencies.
        """
        if self.mean_center is None:
            self._calculate_mean_center()

        if self.probability_distribution is None or self.integration_variable is None:
            self._calculate_normalized_distribution()

        if self.skewness is None:
            self.skewness = np.sum(self.mean_center ** 3 * self.probability_distribution, axis=0) / \
                            self.spectral_spread ** 3

        return self.skewness

    @property
    def spectral_kurtosis(self):
        """
        Spectral kurtosis gives a measure of the flatness of the spectrum around its mean value. Values approximately 3
        indicate a normal (Gaussian) distribution, values less than 3 indicate a flatter distributions, and values
        greater than 3 indicate a peakier distribution.
        """
        if self.mean_center is None:
            self._calculate_mean_center()

        if self.probability_distribution is None or self.integration_variable is None:
            self._calculate_normalized_distribution()

        if self.kurtosis is None:
            self.kurtosis = np.sum(self.mean_center ** 4 * self.probability_distribution, axis=0) / \
                            self.spectral_spread ** 4

        return self.kurtosis

    @property
    def spectral_slope(self):
        """
        Spectral slope is computed using a linear regression over the spectral amplitude values. It should be noted that
        the spectral slope is linearly dependent on the spectral centroid.
        """
        if self._acoustic_pressures_pascals is None and self._frequencies is None:
            self._calculate_spectrum()

        if self.probability_distribution is None or self.integration_variable is None:
            self._calculate_normalized_distribution()

        if self.slope is None:
            numerator = len(self._frequencies) * (self._frequencies.transpose().dot(self.probability_distribution))
            numerator -= np.sum(self._frequencies) * np.sum(self.probability_distribution, axis=0)
            denominator = len(self._frequencies) * sum(self._frequencies ** 2) - np.sum(self._frequencies) ** 2
            self.slope = numerator / denominator

        return self.slope

    @property
    def spectral_decrease(self):
        """
        Spectral decrease was proposed by Krimphoff (1993) in relation to perceptual studies. It averages the set of
        slopes between frequency f[k] and f[1]. It therefore emphasizes the slopes of the lowest frequencies.
        """
        if self._acoustic_pressures_pascals is None and self._frequencies is None:
            self._calculate_spectrum()

        if self.probability_distribution is None or self.integration_variable is None:
            self._calculate_normalized_distribution()

        if self.decrease is None:
            numerator = self._acoustic_pressures_pascals[1:] - self._acoustic_pressures_pascals[0]
            denominator = (1 / np.arange(1, len(self._frequencies)))
            self.decrease = (denominator.dot(numerator)).transpose().reshape((-1,))
            self.decrease /= np.sum(self.probability_distribution[1:], axis=0)

        return self.decrease[0]

    @property
    def spectral_roll_off(self):
        """
        Spectral roll-off was proposed by Scheirer and Slaney (1997). It is defined as the frequency below which 95%
        of the signal energy is contained. The value is returned as the normalized frequency (i.e. you must multiply
        by the sample rate to determine the actual frequency of the roll-off.
        """
        if self._acoustic_pressures_pascals is None and self._frequencies is None:
            self._calculate_spectrum()

        if self.roll_off is None:
            threshold = 0.95
            cum_sum = np.cumsum(self._acoustic_pressures_pascals, axis=0)
            _sum = np.ones((len(self.frequencies),)) * (threshold * np.sum(self._acoustic_pressures_pascals))

            _bin = np.cumsum(1 * (cum_sum > _sum), axis=0)
            idx = np.where(_bin == 1)[0]

            self.roll_off = self.frequencies[idx][0]

        return self.roll_off

    @property
    def spectral_energy(self):
        """
        A summation of the energy within the spectrum
        """
        if self._acoustic_pressures_pascals is None and self._frequencies is None:
            self._calculate_spectrum()

        if self.energy is None:
            self.energy = np.sum(self._acoustic_pressures_pascals ** 2, axis=0)

        return self.energy

    @property
    def spectral_flatness(self):
        """
        Spectral flatness is obtained by comparing the geometrical mean and the arithmetical mean of the spectrum. The
        original formulation first splot the spectrum into various frequency bands (Johnston, 1988). However, in the
        context of timbre characterization, we use a single frequency band covering the whole frequency range. For
        tonal signals, the spectral flatness is close to 0( a peaky spectrum), whereas for noisy signals it is close to
        1 (flat spectrum).
        """
        if self._acoustic_pressures_pascals is None and self._frequencies is None:
            self._calculate_spectrum()

        if self.flatness is None:
            self.geometric_mean = np.exp((1 / len(self._frequencies)) * np.sum(np.log(self._acoustic_pressures_pascals),
                                                                               axis=0))
            self.arithmetic_mean = np.mean(self._acoustic_pressures_pascals, axis=0)
            self.flatness = self.geometric_mean / self.arithmetic_mean

        return self.flatness

    @property
    def spectral_crest(self):
        """
        The spectral crest measure is obtained by comparing the maximum value and arithmetical mean of the spectrum.
        """
        if self._acoustic_pressures_pascals is None and self._frequencies is None:
            self._calculate_spectrum()

        if self.arithmetic_mean is None:
            self.arithmetic_mean = np.mean(self._acoustic_pressures_pascals, axis=0)

        if self.crest is None:
            self.crest = np.max(self._acoustic_pressures_pascals, axis=0) / self.arithmetic_mean

        return self.crest

    @property
    def mean_center(self):
        if self._mean_center is None:
            self._calculate_mean_center()

        return self._mean_center

    @property
    def harmonic_energy(self):
        """
        This is the energy within the signal that is explained by the harmonic partial frequencies and amplitudes. It
        is the square of all the amplitudes determined for the harmonic frequencies.
        """

        if self.partial_frequencies_indices is None:
            if self.fundamental_frequency is None:
                self._calculate_fundamental_frequency()

                if self._noise_energy is np.nan:
                    self._harmonic_energy = np.nan
                    return
            self._calculate_partial_pressures()

        if self._harmonic_energy is not None:
            return self._harmonic_energy

        self._harmonic_energy = 0

        for idx in self.partial_frequencies_indices:
            self._harmonic_energy += self.pressures_pascals[idx] ** 2

        return self._harmonic_energy

    @property
    def noise_energy(self):
        """
        This is the energy of the signal not represented by the harmonic frequencies. It is simply the difference
        between the total energy and the energy explained by the harmonics.
        """
        if self.partial_frequencies_indices is None:
            if self.fundamental_frequency is None:
                self._calculate_fundamental_frequency()

                if self._noise_energy is np.nan:
                    self._noisiness = np.nan
                    return

            self._calculate_partial_pressures()

        if self._noise_energy is not None:
            return self._noise_energy

        self._noise_energy = self.spectral_energy - self.harmonic_energy

        return self._noise_energy

    @property
    def noisiness(self):
        """
        This is the ratio of the noise energy to the total energy. The higher the noisiness, the more noise-like the
        signal must be.
        """
        if self.partial_frequencies_indices is None:
            if self.fundamental_frequency is None:
                self._calculate_fundamental_frequency()

                if self.fundamental_frequency is np.nan:
                    self._noisiness = np.nan
                    return
            self._calculate_partial_pressures()

        if self._noisiness is not None:
            return self._noisiness

        self._noisiness = self.noise_energy / self.spectral_energy

        return self._noisiness

    @property
    def tri_stimulus(self):
        """
        This is a set of values that were first introduced by H. Pollard (Pollard, H. and Jansson, E. (1982) "A
        tristimulus method for the specification of musical timbre," Acustica 51, 162-171) as a timbral equivalent to
        visual color attributes. It is three different energy ratios based on the description of the fundamental
        frequency.
        """
        if self._tri_stimulus is None:
            if self.partial_frequencies_indices is None:
                if self.fundamental_frequency is None:
                    self._calculate_fundamental_frequency()

                    if self.fundamental_frequency is np.nan:
                        self._tri_stimulus = [np.nan, np.nan, np.nan]
                        return
                self._calculate_partial_pressures()

            harmonic_pressure_sum = np.sum(self.pressures_pascals[self.partial_frequencies_indices])
            t01 = self.pressures_pascals[self.partial_frequencies_indices[0]] / harmonic_pressure_sum

            t02 = np.sum(self.pressures_pascals[self.partial_frequencies_indices[1:4]]) / harmonic_pressure_sum
            t03 = np.sum(self.pressures_pascals[self.partial_frequencies_indices[4:]]) / harmonic_pressure_sum

            self._tri_stimulus = [t01, t02, t03]

        return self._tri_stimulus

    @property
    def harmonic_spectral_deviation(self):
        """
        This measures the deviation of the amplitudes of the partials from the harmonics from the global or smoothed
        spectral envelope.
        """
        if self._harmonic_spectral_deviation is None:
            if self.partial_frequencies_indices is None:
                if self.fundamental_frequency is None:
                    self._calculate_fundamental_frequency()

                if self.fundamental_frequency is np.nan:
                    self._harmonic_spectral_deviation = np.nan
                    return

                self._calculate_partial_pressures()

            self._harmonic_spectral_deviation = 0
            for h in range(1, len(self.partial_frequencies_indices) - 1):
                self._harmonic_spectral_deviation += self.pressures_pascals[self.partial_frequencies_indices[h]] - (
                        self.pressures_pascals[self.partial_frequencies_indices[h - 1]] +
                        self.pressures_pascals[self.partial_frequencies_indices[h]] +
                        self.pressures_pascals[self.partial_frequencies_indices[h + 1]]
                ) / 3

            self._harmonic_spectral_deviation /= len(self.partial_frequencies_indices)

        return self._harmonic_spectral_deviation

    @property
    def odd_even_ratio(self):
        """
        In musical instruments, certain signals contain mostly even (trumpet) or odd (clarinet) harmonics. This ratio
        determines where the system is mostly odd or even.
        """
        if self._odd_even_ratio is None:
            if self.partial_frequencies_indices is None:
                if self.fundamental_frequency is None:
                    self._calculate_fundamental_frequency()

                if self.fundamental_frequency is np.nan:
                    self._odd_even_ratio = np.nan
                    return

                self._calculate_partial_pressures()

            odd_energy = 0
            even_energy = 0
            for i in range(1, len(self.partial_frequencies_indices)):
                if (i + 1) % 2 == 0:
                    even_energy += self.pressures_pascals[self.partial_frequencies_indices[i]] ** 2
                else:
                    odd_energy += self.pressures_pascals[self.partial_frequencies_indices[i]] ** 2

            self._odd_even_ratio = odd_energy / (even_energy + sys.float_info.epsilon)

        return self._odd_even_ratio

    @property
    def inharmonicity(self):
        """
        This is a measure of the deviation of the partial frequencies from the purely harmonic frequency.
        """
        if self._inharmonicity is None:
            if self.partial_frequencies_indices is None:
                if self.fundamental_frequency is None:
                    self._calculate_fundamental_frequency()
                self._calculate_partial_pressures()

            f0 = self.fundamental_frequency

            if f0 is np.nan:
                self._inharmonicity = np.nan
            else:
                frequency_departure = 0
                for i in range(1, len(self.partial_frequencies_indices)):
                    frequency_departure += (self.frequencies[self.partial_frequencies_indices[i]] - (i + 1) * f0) * \
                                           self.pressures_pascals[self.partial_frequencies_indices[i]]

                self._inharmonicity = (2 / f0) * frequency_departure / np.sum(self.pressures_pascals[
                                                                                  self.partial_frequencies_indices] ** 2)

        return self._inharmonicity

    @property
    def fundamental_frequency(self):
        if self._fundamental_frequency is None:
            self._calculate_fundamental_frequency()

        return self._fundamental_frequency

    def calculate_engineering_unit_scale_factor(self, calibration_level: float = 94, calibration_frequency=1000):
        """
        This will take the data within the class and build the spectral time history and then determine the value of the
        scale factor to get a specific sound pressure level at a certain frequency.

        Parameters
        ----------
        calibration_level: float - the value of the acoustic level for the calibration
        calibration_frequency: float - the value of the frequency that is supposed to be used for the calibration

        Returns
        -------
        float - the engineering scale factor that can be directly applied to the acoustic data
        """

        if self.fractional_octave_bandwidth is None:
            raise ValueError("This analysis cannot be accomplished on a narrowband spectrum")

        #   Now determine the index of the band within the spectral time history that should be examined for the
        #   calculation of the engineering scaling units.

        idx = np.argmin(np.abs(self.frequencies - calibration_frequency))

        #   Now this may select the nearest band as the band just above the actual band.  So ensure that the lower band
        #   is below the desired center frequency
        #
        # if fob_tools.lower_frequency(3, idx + 10) > calibration_frequency:
        #     idx -= 1

        #   From the spectrum obtain the values of the frequency

        calibration_values = self.pressures_decibels[idx]

        #   Calculate the sensitivity of each time history spectra

        sens = calibration_level - calibration_values
        sens /= 20
        sens *= -1
        sens = 10.0 ** sens

        return sens

    def get_average_features(self, include_sq_metrics: bool = True, include_temporal_features: bool = True,
                             include_spectral_features: bool = True, include_harmonic_features: bool = True):
        """
        This will return a dict of the various elements within the spectrum and waveform (if it was used to create the
        spectrogram object) with any time variant elements averaged.
        """

        #   Create the dictionary that will hold the data
        features = dict()

        #   If there is a waveform inside the Spectrum object, and we desire the temporal statistics
        if self.waveform is not None and include_temporal_features:
            features = self.waveform.get_features(include_sq_metrics)
            features['zero_crossing_rate'] = np.mean(features['zero crossing rate'])
            auto_correlation_coefficients = np.mean(features['auto-correlation'], axis=0)

            if include_sq_metrics:
                features['loudness'] = np.mean(features['loudness'])
                features['sharpness'] = np.mean(features['sharpness'])
                features['roughness'] = np.mean(features['roughness'])

            for i in range(12):
                features['auto_correlation_{:02.0f}'.format(i)] = auto_correlation_coefficients[i]

            del features['zero crossing rate']
            del features['auto-correlation']

        #   If we desire the spectral statistics
        if include_spectral_features:
            features['spectral_centroid'] = np.mean(self.spectral_centroid)
            features['spectral_spread'] = np.mean(self.spectral_spread)
            features['spectral_skewness'] = np.mean(self.spectral_skewness)
            features['spectral_kurtosis'] = np.mean(self.spectral_kurtosis)
            features['spectral_slope'] = np.mean(self.spectral_slope)
            features['spectral_decrease'] = np.mean(self.spectral_decrease)
            features['spectral_roll_off'] = np.mean(self.spectral_roll_off)
            features['spectral_energy'] = np.mean(self.spectral_energy)
            features['spectral_flatness'] = np.mean(self.spectral_flatness)
            features['spectral_crest'] = np.mean(self.spectral_crest)

        if include_harmonic_features:
            features['fundamental_frequency'] = np.mean(self.fundamental_frequency)
            features['harmonic_energy'] = self.harmonic_energy
            features['noise_energy'] = self.noise_energy
            features['noisiness'] = self.noisiness
            features['tri_stimulus_01'] = self.tri_stimulus[0]
            features['tri_stimulus_02'] = self.tri_stimulus[1]
            features['tri_stimulus_03'] = self.tri_stimulus[2]
            features['harmonic_spectral_deviation'] = self.harmonic_spectral_deviation
            features['odd_even_ratio'] = self.odd_even_ratio
            features['inharmonicity'] = self.inharmonicity

        return features

    def get_feature_names(self, include_sq_metrics: bool = True, include_temporal_features: bool = True,
                          include_spectral_features: bool = True, include_harmonic_features: bool = True):
        return self.get_average_features(include_sq_metrics=include_sq_metrics,
                                         include_harmonic_features=include_harmonic_features,
                                         include_spectral_features=include_spectral_features,
                                         include_temporal_features=include_temporal_features).keys()

    def _calculate_normalized_distribution(self):
        if self._acoustic_pressures_pascals is None:
            self._calculate_spectrum()

        self.probability_distribution = self._acoustic_pressures_pascals
        self.probability_distribution /= np.sum(self._acoustic_pressures_pascals, axis=0)

        self.integration_variable = self.frequencies

    def _calculate_mean_center(self):
        if self._acoustic_pressures_pascals is None:
            self._calculate_spectrum()

        if self.probability_distribution is None or self.integration_variable is None:
            self._calculate_normalized_distribution()

        if self._mean_center is None:
            self._mean_center = self.integration_variable - self.spectral_centroid

        return self._mean_center

    def _calculate_fundamental_frequency(self):
        from .fundamental_frequency import FundamentalFrequencyCalculator

        calculator = FundamentalFrequencyCalculator(frequency_window_size=self._fft_size)

        f0 = list()
        f0.append(calculator.fundamental_swipe(self))
        # f0.append(calculator.fundamental_by_peaks(self))
        # if self._waveform is not None:
        #     f0.append(calculator.fundamental_by_time(self.waveform))

        #   Convert the list to an array and remove any Nan values
        f0 = np.asarray(f0)
        f0 = f0[np.logical_not(np.isnan(f0))]

        if len(f0) < 1:
            self._fundamental_frequency = np.nan
        else:
            self._fundamental_frequency = np.median(f0)

    def _calculate_partial_pressures(self):
        """
        We need to locate the partial pressure frequencies and amplitudes by calculating the index of each integer
        multiple of the fundamental frequency.
        """

        #   Determine the ratio of the frequencies to the fundamental frequencies. We want to keep only the values
        #   that are close to a whole integer multiple.
        f_ratio = self.frequencies / self.fundamental_frequency

        #   Using the last ratio, determine the maximum number of partial pressure that might exist within this spectrum
        max_partial_frequencies = int(np.floor(f_ratio[-1]))
        self.partial_frequencies_indices = np.zeros((max_partial_frequencies,), dtype=int)

        for i in range(0, max_partial_frequencies):
            self.partial_frequencies_indices[i] = np.where(f_ratio >= i + 1)[0][0]

    def _calculate_harmonic_features(self):
        from ..yin import yin
        # self.stft = STFT.STFT(sound, self.config)
        # self.t_support = self.stft.t_support
        # maxSwipepWinSize = self.stft.hop_size * np.ceil(
        #     2 ** (round(np.log2(8 * self.sound.reps['AudioSignal'].sampleRate / 50)) - 1) / self.stft.hop_size)
        # freqCorrs = np.linspace(-5, 5, 101)
        # nFreqCorrs = len(freqCorrs)
        # inharmCoeffs = np.linspace(0, 0.001, 21)
        # nInharmCoeffs = 21
        # tSupport = np.subtract(self.t_support, self.t_support[0])
        # tSize = len(tSupport)
        # distr = self.stft.value
        # signalChunk = a.value
        # pitchLims = np.array([50, 500])
        # estimated_pitches, estimated_times, estStrengths = self.swipep(signalChunk, self.sound.reps['AudioSignal'].sampleRate,
        #                                                  pitchLims, (self.stft.hop_size / self.sound.reps[
        #         'AudioSignal'].sampleRate), 1 / 48, 0.1, 0.2, -np.inf)

        estimated_pitches, estimated_times, estimated_pitch_strengths = yin(
            self.waveform.samples,
            self.waveform.sample_rate,
            F_max=10000,
            F_min=10,
            N=int(np.floor(self.sample_rate / 10)),
            H=int(np.floor(self.sample_rate / 10 / 4)))

        try:
            current_maximum = np.nanmax(estimated_pitch_strengths)
        except ValueError:
            current_maximum = np.max(estimated_pitch_strengths)
        nans = np.isnan(estimated_pitches)
        anyy = any(nans)
        if anyy:
            estimated_pitches[np.isnan(estimated_pitches)] = np.median(
                estimated_pitches[not np.isnan(estimated_pitches)])
        fundamental_frequencies = None
        if current_maximum > self.pitch_threshold:
            estimated_time_pitch_pairs = np.zeros((len(estimated_times), 2))
            estimated_time_pitch_pairs[:, 0] = estimated_times
            estimated_time_pitch_pairs[:, 1] = estimated_pitches
            fundamental_frequencies = Harmonic.Fevalbp(estimated_time_pitch_pairs, tSupport)
            fundamental_frequencies = np.transpose(fundamental_frequencies)
        else:
            logging.warning('Sound deemed not harmonic. Setting f0 estimate to 0.')
            self.partialFreqs = np.zeros((self.config['n_harms'], tSize))
            self.partialAmps = np.zeros((self.config['n_harms'], tSize))
            self.fundamentalFreqs = np.zeros((1, tSize))
            return
        a = np.empty((len(fundamental_frequencies), nFreqCorrs))
        for column in range(np.shape(a)[1]):
            a[:, column] = fundamental_frequencies
        b = np.empty((tSize, len(freqCorrs)))
        for row in range(np.shape(b)[0]):
            b[row, :] = freqCorrs
        corrFreqsTF = np.add(a, b)

        a = np.empty((self.config['n_harms'], nInharmCoeffs))
        for column in range(np.shape(a)[1]):
            a[:, column] = [*range(1, self.config['n_harms'] + 1)]
        b = np.power([*range(1, self.config['n_harms'] + 1)], 2)
        b1 = b[:, None]
        b2 = inharmCoeffs[None, :]
        c = np.matmul(b1, b2)
        d = np.add(1, c)
        inharmFactorsHI = np.multiply(a, np.sqrt(d))
        shape1 = np.reshape(corrFreqsTF, (tSize * nFreqCorrs, 1), order='F')
        shape2 = np.reshape(inharmFactorsHI, (1, self.config['n_harms'] * nInharmCoeffs), order='F')
        shape3 = np.reshape(np.multiply(shape1, shape2), (tSize, nFreqCorrs, self.config['n_harms'], nInharmCoeffs),
                            order='F')
        shape4 = np.divide(1, self.stft.bin_size)
        shape5 = np.multiply(shape4, shape3)
        shape6 = np.round(shape5)
        fSupIdcsTFHI = np.add(1, shape6)
        fSupIdcsTFHI[fSupIdcsTFHI > self.stft.f_size] = self.stft.f_size

        a = np.array([*range(0, tSize)])
        a2 = a[:, None, None, None]
        b = np.tile(a2, (1, nFreqCorrs, self.config['n_harms'], nInharmCoeffs))
        c = np.multiply(self.stft.f_size, b)
        d = np.add(fSupIdcsTFHI, c)
        e = d.astype(int)
        distrIdcsTFHI = np.subtract(e, 1)
        shape = np.shape(distrIdcsTFHI)

        _0 = distr.flatten('F')
        _1 = distrIdcsTFHI.flatten('F')
        _2 = np.take(_0, _1)

        a = np.reshape(_2, shape, order='F')
        totalErgTFI = np.sum(a, axis=2)

        scoreTI = np.max(totalErgTFI, 1)
        inharmCoeffIdcsT = np.argmax(scoreTI, 1)
        maxScoreTI = np.array([scoreTI[i, inharmCoeffIdcsT[i]] for i in range(len(inharmCoeffIdcsT))])
        a = np.subtract(maxScoreTI, scoreTI[:, 0])
        b = np.divide(a, scoreTI[:, 0])
        c = b <= 0.01
        inharmCoeffIdcsT[c] = 0
        tile1 = np.add([*range(1, tSize + 1)], np.multiply(tSize * nFreqCorrs, inharmCoeffIdcsT))
        repmat1 = np.tile(tile1, (nFreqCorrs, 1)).transpose()
        tile2 = [tSize * (x) for x in range(nFreqCorrs)]
        repmat2 = np.tile(tile2, (tSize, 1))
        colIdcs = np.reshape(np.add(repmat1, repmat2), (tSize * nFreqCorrs, 1), order='F')
        totalErgTFI_flat = totalErgTFI.flatten('F')
        totalErgTF = np.take(totalErgTFI_flat, np.subtract(colIdcs, 1))
        totalErgTF = np.reshape(totalErgTF, (tSize, nFreqCorrs), order='F')

        reshape1 = np.reshape(
            np.add([*range(1, tSize + 1)], np.multiply(tSize * nFreqCorrs * self.config['n_harms'], inharmCoeffIdcsT)),
            (tSize, 1, 1), order='F')
        repmat1 = np.tile(reshape1, (1, nFreqCorrs, self.config['n_harms']))
        reshape2 = np.reshape([*range(1, nFreqCorrs + 1)], (1, nFreqCorrs, 1), order='F')
        repmat2 = np.tile(reshape2, (tSize, 1, self.config['n_harms']))
        reshape3 = np.reshape([*range(1, self.config['n_harms'] + 1)], (1, 1, self.config['n_harms']), order='F')
        repmat3 = np.tile(reshape3, (tSize, nFreqCorrs, 1))

        a = np.subtract(repmat3, 1)
        b = np.multiply(nFreqCorrs, a)
        c = np.subtract(np.add(repmat2, b), 1)  # ???? Switch
        d = np.multiply(tSize, c)
        e = np.add(repmat1, d)
        colIdcs = np.reshape(e, (tSize * nFreqCorrs * self.config['n_harms'], 1), order='F')
        fSupIdcsTFHI_flat = fSupIdcsTFHI.flatten('F')
        fSupIdcsHTF = np.take(fSupIdcsTFHI_flat, np.subtract(colIdcs, 1))
        fSupIdcsHTF = np.reshape(fSupIdcsHTF, (tSize, nFreqCorrs, self.config['n_harms']), order='F')
        fSupIdcsHTF = np.transpose(fSupIdcsHTF, [2, 0, 1])
        freqCorrIdcsT = np.argmax(totalErgTF, 1)

        repmat1 = np.tile([*range(1, self.config['n_harms'] + 1)], (tSize, 1)).transpose()
        a = freqCorrIdcsT
        b = np.multiply(tSize, a)
        c = np.subtract(np.add([*range(1, tSize + 1)], b), 1)
        d = np.multiply(self.config['n_harms'], c)
        repmat2 = np.tile(d, (self.config['n_harms'], 1))
        colIdcs = np.reshape(np.add(repmat1, repmat2), (self.config['n_harms'] * tSize, 1), order='F')

        fSupIdcsHTF_flat = fSupIdcsHTF.flatten('F')
        fSup = np.take(fSupIdcsHTF_flat, np.subtract(colIdcs, 1)).astype(int)
        partialFreqs = np.take(self.stft.f_support, np.subtract(fSup, 1))
        partialFreqs = np.reshape(partialFreqs, (self.config['n_harms'], tSize), order='F')

        repmat1 = np.tile([*range(0, tSize)], (self.config['n_harms'], 1))
        reshape1 = np.reshape(repmat1, (self.config['n_harms'] * tSize, 1), order='F')
        aa = fSup
        bb = np.multiply(self.stft.f_size, reshape1)
        cc = np.add(aa, bb)
        distr_flat = distr.flatten('F')
        partialAmps = np.take(distr_flat, np.subtract(cc, 1))
        partialAmps = np.reshape(partialAmps, (self.config['n_harms'], tSize), order='F')
        aaa = np.concatenate((partialFreqs, partialAmps))
        self.fundamentalFreqs = aaa[0, :]
        self.partialFreqs = aaa[:self.config['n_harms'], :]
        self.partialAmps = aaa[self.config['n_harms']:(2 * self.config['n_harms']), :]
        self.value = aaa


class SpectrumByFFT(Spectrum):
    """
    This class is a specialization of the spectrum class that implements the way to define the spectrum. This is
    accomplished with the Fourier Transform, using a chunked overlapping representation of the data within the
    calculation.

    In this class the frequencies property represents the single-sided frequencies of the Fourier transform
    """

    def __init__(self, a: Waveform = None, fft_size: int = None):
        """
        Constructor - This constructor adds the ability of the class to define the specific size of the Fourier
        frequency bins. This also adds a number of elements that represent the double and single sided frequencies
        that originate with the Fourier transform methodologies.
        """
        #   Call the base constructor to define the waveform within the class
        super().__init__(a)

        #   Now define some information within the class related to the frequencies and the information generated
        #   specifically for the FFT methods
        self._fft_size = fft_size
        self._frequencies_double_sided = None
        self._frequencies_nb = None

        #   Define some other representations of the acoustic information that might be needed in various
        #   analyses.
        self._pressures_double_sided_complex = None

        if a is not None:
            #   There is no default value for the FFT size, so let's do some analysis to determine what the most optimal
            #   value of this should be if it is not provided.
            if self._fft_size is None:

                #   Set the default block size
                self._fft_size = int(2 ** np.floor(np.log2(len(self.waveform.samples))))

            elif self._fft_size > len(self.waveform.samples):
                raise ValueError('FFT block size cannot be greater than the total length of the signal.')

    def _calculate_spectrum(self):
        """
        This function generates the complex spectra using an FFT of multiple blocks of an input waveform,
        where the blocks have 50% overlap and are each weighted by a Hanning window.

        The FFT blocks are then scaled to contain the appropriate amount of energy for input into a power
        spectrum calculation.
        """

        #   Create the frequency arrays
        self._frequencies_double_sided = self.sample_rate * np.arange(0, self._fft_size) / self._fft_size
        self._frequencies_nb = self._frequencies_double_sided[:int(self._fft_size / 2)]
        df = self._frequencies_nb[1] - self._frequencies_nb[0]

        #   enforce a zero mean value
        x = self.waveform.samples - np.mean(self.waveform.samples)

        #   Generate a Hanning window
        ww = np.hanning(self._fft_size)
        W = np.mean(ww ** 2)

        #   Divide the total data into blocks with 50% overlap and Hanning window
        blocks = np.zeros(shape=(int(np.floor(2 * len(x) / self._fft_size - 1)), self._fft_size))

        for k in range(blocks.shape[0]):
            i = int(k * self._fft_size / 2)
            j = i + blocks.shape[1]
            blocks[k, :] = ww * x[i:j]

        #   Determine complex pressure amplitude
        self._pressures_double_sided_complex = np.sqrt(2 * df / self._fft_size /
                                                       self.sample_rate / W) * scipy.fft.fft(blocks, n=self._fft_size)

        #   Now assign the values for the acoustic pressures using this information, but only using the first hold of
        #   the frequency data.
        self._frequencies = self._frequencies_nb
        self._acoustic_pressures_pascals = self.auto_correlation_spectrum

    @property
    def frequency_increment(self):
        return self.frequencies[1] - self.frequencies[0]

    @property
    def frequencies_double_sided(self):
        """
        2-D Numpy array of double-sided frequencies from a Fourier transform of each block of a waveform
        with 50% overlap and a Hanning window in units of Pascals.
        """

        if self._frequencies_double_sided is None:
            self._calculate_spectrum()

        return self._frequencies_double_sided

    @property
    def pressures_complex_double_sided(self):
        """
        2-D Numpy array of double-sided complex pressures from a Fourier transform of each block of a waveform
        with 50% overlap and a Hanning window in units of Pascals.
        """
        if self._pressures_double_sided_complex is None:
            self._calculate_spectrum()

        return self._pressures_double_sided_complex

    @property
    def auto_correlation_spectrum(self):
        """
        Numpy array of single-sided real-valued pressures averaged over FFT of all blocks of a waveform with 50%
        overlap and a Hanning window.  Units of Pascals.
        """
        if self._pressures_double_sided_complex is None:
            self._calculate_spectrum()

        pressures_single_sided = self._pressures_double_sided_complex[:, :len(self._frequencies_nb)]
        return np.sqrt(np.mean((pressures_single_sided * np.conj(pressures_single_sided)).real, axis=0))

    @property
    def fft_size(self):
        return self._fft_size

    @property
    def power_spectral_density(self):
        """
        Numpy array of single-sided real-values. Pressures scaled by frequency, in units of Pascals / sqrt(Hz).
        """
        return self.pressures_pascals / np.sqrt(self.frequency_increment)

    @staticmethod
    def convert_nb_to_fob(frequencies_nb, pressures_pascals_nb, fob_band_width: int = 3, f0: float = 10,
                          f1: float = 10000):
        """
        This function converts the frequency and pressure arrays sampled in narrowband resolution to the fractional
        octave band resolution.

        Parameters
        ----------
        frequencies_nb: nd_array - the collection of narrowband frequencies that we want to convert
        pressures_pascals_nb: nd_array - the collection of pressures in units of pascals for the frequencies
        fob_band_width: int, default = 3 - the fractional octave band resolution that we desire
        f0: float, default = 10 - The start frequency of the output fractional octave frequencies
        f1: float, default = 10000 - The end frequency of the output fractional octave frequencies

        Returns
        -------
        frequencies_fob: nd_array - the collection of frequencies from f0 to f1 with the resolution of fob_band_width
        pressures_pascals_fob: nd_array - the fractional octave pressure in pascals at the associated frequencies
        """

        frequencies_fob = fob_tools.get_frequency_array(fob_band_width, f0, f1)

        #   Build the array of pressures that are the same size as the list of frequencies
        pressures_pascals_fob = np.zeros((len(frequencies_fob),))

        for i in range(len(frequencies_fob)):
            pressures_pascals_fob[i] = np.sqrt(sum(pressures_pascals_nb ** 2 *
                                                   fob_tools.filter_shape(fob_band_width, frequencies_fob[i],
                                                                          frequencies_nb)))

        return frequencies_fob, pressures_pascals_fob

    def to_fractional_octave_band(self, bandwidth: int = 3, f0: float = 10, f1: float = 10000):
        """
        This function will convert the spectrum from a narrowband resolution to a factional octave band resolution by
        applying the shape functions to the narrowband spectral values and determining the weighted value within the
        fractional octave band.

        Parameters
        ----------
        bandwidth: float, default = 3 - the fractional octave resolution that we will sample the frequency spectrum
        f0: float, default = 10 - the lowest frequency within the spectrum
        f1: float, default = 10000 - the heighest frequency within the spectrum

        Returns
        -------
        Spectrum - a spectrum object with the frequencies at the specified resolution and between the specified
        frequency values.
        """

        f_fob, p_fob = SpectrumByFFT.convert_nb_to_fob(self.frequencies, self.pressures_pascals, bandwidth, f0, f1)
        s = Spectrum()
        s.frequencies = f_fob
        s.pressures_pascals = p_fob
        s.start_fractional_octave_frequency = f0
        s.stop_fractional_octave_frequency = f1
        s.fractional_octave_bandwidth = bandwidth
        s._time0 = self.time

        return s


class SpectrumByDigitalFilters(Spectrum):
    """
    This class differs from the previous classes in that the determination of the spectrum is accomplished through an
    application of digital filters. A set of filters describing the collection of filters at the highest desired full
    octave band will be constructed. These coefficients will be applied as the signal is recursively down sampled at
    half the sample rate. The minimum number of elements required to generate the filtered data require three times
    the number of coefficients, doubled until we reach the maximum sample rate of the system.

    Development
    20221008 - FSM - Since we added the bandwidth, start and stop frequencies to the base class, this class no longer
        required a separate definition. All references were adjusted to use the base class values for these parameters.
    """

    def __init__(self, a: Waveform, fob_band_width: int = 3, f0: float = 10, f1: float = 10000):
        """
        The constructor - this will determine what the minimum number of samples required is to generate the lowest
        desired frequency.

        Parameters
        ----------
        a: Waveform - the audio signal that we want to process
        fob_band_width: int, default: 3 - the bandwidth of the fractional octave
        f0: float, default: 10 - the lowest frequency in Hz
        f1: float, default: 10000 - the highest frequency in the output
        """
        super().__init__(a)

        self._bandwidth = fob_band_width
        self._f0 = f0
        self._f1 = f1
        self._b_coefficients = list()
        self._a_coefficients = list()

        #   Build the filters for the highest desired full octave
        #
        #   Determine the center frequency of the highest octave
        full_band = int(np.floor(fob_tools.nearest_band(1, self.stop_fractional_octave_frequency)))
        f_full = fob_tools.center_frequency(1, full_band)
        f_lo = fob_tools.lower_frequency(1, full_band)
        f_hi = fob_tools.upper_frequency(1, full_band)

        #   Now that the know the center frequency of the highest band, determine the upper limit, and then the closest
        #   center frequency in the desired bandwidth
        f_band = int(np.floor(fob_tools.nearest_band(self.fractional_octave_bandwidth, f_hi)))
        nyquist = self.sample_rate / 2.0

        #   Loop through the frequencies within the highest octave band and create the associated digital filters for
        #   the element based on the calculated high and low frequencies.
        while fob_tools.lower_frequency(self.fractional_octave_bandwidth, f_band) >= f_lo * 0.90:
            #   Define the window for the bandpass filter
            upper = fob_tools.upper_frequency(self.fractional_octave_bandwidth, f_band)
            lower = fob_tools.lower_frequency(self.fractional_octave_bandwidth, f_band)
            window = np.array([lower, upper]) / nyquist

            #   Create the filter coefficients for this frequency band and add it to the list for each coefficient set
            b, a = scipy.signal.butter(
                3,
                window,
                btype='bandpass',
                analog=False,
                output='ba'
            )

            self._b_coefficients.append(b)
            self._a_coefficients.append(a)

            #   Decrement the band number to move to the next band down.
            f_band -= 1

        #   Convert the lists to arrays
        self._b_coefficients = np.asarray(self._b_coefficients)
        self._a_coefficients = np.asarray(self._a_coefficients)

    @property
    def settle_time(self):
        return self.settle_samples / self.sample_rate

    @property
    def settle_samples(self):
        """
        Based on requirements of Matlab filtering, you must have at least 3 times the number of coefficients to
        accurately filter data. So this will start with that minimum, and then move through the full octave frequency
        band numbers to determine the minimum number of samples that are required for the filter to adequately settle.
        """
        #   Determine the band number for the lowest band
        low_band = int(np.floor(fob_tools.nearest_band(1, self.start_fractional_octave_frequency)))
        hi_band = int(np.floor(fob_tools.nearest_band(1, self.stop_fractional_octave_frequency)))

        minimum_required_points = 3 * self._b_coefficients.shape[1]

        for band_index in range(low_band + 1, hi_band + 1):
            minimum_required_points *= 2

        return minimum_required_points

    def _calculate_spectrum(self):
        """
        This will take the waveform that exist within the class and calculate the fractional octave pressures within
        each band that is adequately covered by the length of the waveform.
        """

        #   Create the list that will hold the frequencies and band pressures
        pressures = list()
        frequency = list()

        #   Determine the octave bands that will need to be calculated to cover the desired frequency range.
        low_band = int(np.floor(fob_tools.nearest_band(1, self.start_fractional_octave_frequency)))
        hi_band = int(np.floor(fob_tools.nearest_band(1, self.stop_fractional_octave_frequency)))

        #   Get the index of the band at the top of the full octave filter
        fob_band_index = int(np.floor(fob_tools.nearest_band(self.fractional_octave_bandwidth,
                                                             fob_tools.upper_frequency(1, hi_band))))

        #   Make a copy of the waveform that can be decimated
        wfm = Waveform(pressures=self.waveform.samples.copy(),
                       sample_rate=self.sample_rate,
                       start_time=self.waveform.start_time)

        #   Loop through the frequencies in reverse order
        for band_index in range(hi_band, low_band - 1, -1):
            #   if there are insufficient number of points in the waveform, terminate the process now
            if len(wfm.samples) < 3 * self._b_coefficients.shape[1]:
                warnings.warn("The number of points within the Waveform are insufficient to calculate digital filters "
                              "lower than these frequencies")
                break

            #   Now loop through the filter definitions that are presented in decreasing frequency magnitude
            for filter_index in range(self._b_coefficients.shape[0]):
                filtered_waveform = wfm.apply_iir_filter(self._b_coefficients[filter_index, :],
                                                         self._a_coefficients[filter_index, :])

                frequency.append(fob_tools.center_frequency(self.fractional_octave_bandwidth, fob_band_index))
                pressures.append(np.std(filtered_waveform.samples))

                fob_band_index -= 1

            #   Decimate the waveform, halving the sample rate and making the filter definitions move down a full octave
            if len(wfm.samples) / 2 < 3 * self._b_coefficients.shape[1]:
                warnings.warn("The number of points within the Waveform are insufficient to calculate digital filters "
                              "lower than these frequencies")

                break

            wfm = Waveform(pressures=scipy.signal.decimate(wfm.samples, 2),
                           sample_rate=wfm.sample_rate,
                           start_time=wfm.start_time)

        #   Convert the information within the pressures and frequency arrays into the correct elements for the class
        frequency = np.asarray(frequency)[::-1]
        pressures = np.asarray(pressures)[::-1]

        idx0 = np.where(frequency > fob_tools.lower_frequency(self.fractional_octave_bandwidth,
                                                              fob_tools.nearest_band(
                                                                  self.fractional_octave_bandwidth,
                                                                  self.start_fractional_octave_frequency)))[0][0]
        idx1 = np.where(frequency < fob_tools.upper_frequency(self.fractional_octave_bandwidth,
                                                              fob_tools.nearest_band(
                                                                  self.fractional_octave_bandwidth,
                                                                  self.stop_fractional_octave_frequency)))[0][-1]
        self._frequencies = frequency[np.arange(idx0, idx1 + 1)]
        self._acoustic_pressures_pascals = pressures[np.arange(idx0, idx1 + 1)]
