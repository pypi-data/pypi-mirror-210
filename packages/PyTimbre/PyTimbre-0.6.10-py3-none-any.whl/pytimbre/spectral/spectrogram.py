import operator
import pandas
from .time_histories import TimeHistory, Spectrum, Waveform, WaveFile
import numpy as np
import warnings

class Spectrogram (TimeHistory):
    """
    This class represents the Short Time Fourier Transform method for calculating the spectral variations with time. The
    code calculates the spectrogram using the same methods present in the STFT representation of the original Matlab 
    code.
    """

    def __init__(self, a: Waveform = None, integration_time: float = 0.25, nfft=4096):
        """
        Construct the information within the class from the waveform that is passed into the constructor
        
        :param a: Waveform - the acoustic information that we are interested in using for the timbre analysis.
        :param nfft: int - the resolution of the frequency analysis
        """
        super().__init__(a, integration_time)

        self._waveform = a

        self._levels = None
        self._frequencies = None
        self._times = None
        if a is not None:
            self._sample_rate = self._waveform.sample_rate
        else:
            self._sample_rate = 48000

        self._fft_size = nfft

        self._window_size_seconds = 0.0232
        self._hop_size_seconds = 0.0058
        self._window_size = self._window_size_seconds * self._sample_rate
        self._hop_size = self._hop_size_seconds * self._sample_rate

    # -------------------------------------------- Properties ----------------------------------------------------------

    @property
    def fft_size(self):
        return self._fft_size

    # -------------------------------------------- Protected Methods----------------------------------------------------

    def _calculate_spectrogram(self):
        import scipy.signal
        import scipy.fft

        # TODO: Correct indexing error in Spectrogram.pressures_pascals
        warnings.warn('Test for Spectrum.pressures_pascals is failing due to an indexing error. Use at your own risk.')

        # TODO: Determine desired precision for mean center calculation and correct calculation
        warnings.warn('Test for mean center calculation does not pass with desired precision. Use at your own risk.')

        #   If the window is centered at t, this is the starting index at which to loop up the signal which you want
        #   to multiply by the window.  It is a negative number because (almost) half of the window will be before
        #   time t and half after.  In fact, if the length of the window N is an even number, it is set up so this
        #   number equals -1 * (N / 2 -1).  If the length of the window is od, this number equals -1 * (N - 1) / 2
        left_hand_window_size = int(np.ceil(-(self._window_size - 1) / 2))

        #   This is the last index at which to look up signal values and is equal to (N - 1) / 2 if the length N of
        #   the window is odd and N / 2 if the length of the window is even.  This means that in the even case, the
        #   window has an unequal number of past and future values, i.e., time t is not the center of the window,
        #   but slightly to the left of the center of the window (before it).
        right_hand_window_size = int(np.ceil((self._window_size - 1) / 2))

        #   pre-pad the signal and calculate the hilbert transform
        signal = np.concatenate((np.zeros((-left_hand_window_size,)), self.signal))
        signal = scipy.signal.hilbert(signal)
        last_index = np.floor((len(self.signal) -
                               (right_hand_window_size + 1)) / self._hop_size) * self._hop_size + 1

        #   Define some support vectors
        index = np.arange(0, last_index, self._hop_size, dtype=int) - left_hand_window_size
        size_x = len(index)
        size_y = self.fft_size / 2
        self._times = np.arange(0, size_x) / (self.waveform_sample_rate / self._hop_size)
        normalized_frequency = np.arange(0, size_y) / size_y / 2

        #   Create the windowed signal
        window = np.hamming(int(self._window_size + 1))
        distribution_pts = np.zeros((self.fft_size, size_x), dtype='complex')
        for i in range(size_x):
            rng = np.arange(0, int(self._window_size + 1), dtype=int) + (index[i] + left_hand_window_size)

            distribution_pts[:int(self._window_size + 1), i] = signal[rng] * window

        #   Calculate the FFT
        distribution_pts = scipy.fft.fft(distribution_pts, n=self.fft_size, axis=0)

        #   Apply the specific scaling for the analysis
        distribution_pts = abs(distribution_pts)
        distribution_pts /= np.sum(abs(window))

        #   Only keep the first half of the spectrum
        levels = distribution_pts[:int(round(self.fft_size / 2)), :]

        #   Now build the collection of Spectrum objects.
        self._spectra = np.empty((len(self._times),), dtype=Spectrum)

        for i in range(len(self._times)):
            s = Spectrum()
            #   TODO: Insert the distribution_pts into the Spectrum class?
            s.frequencies = normalized_frequency
            s.pressures_pascals = levels[:, i]
            s._time0 = self._times[i]
            #s._waveform = distribution_pts[:, i]

            self._spectra[i] = s

    @staticmethod
    def from_data(levels, frequencies, times):
        """
        This function constructs the Spectrogram object from information obtained from the users and sets up an object
        that can be compared with external data without concern for differences in the methods to calculate the
        spectrogram data.

        :param levels: array-like - the 2-D levels with shape = [len(times), len(frequencies)]
        :param frequencies: array-like - the collection of frequencies that define one dimension of the levels matrix
        :param times: array-like - the collection of times within the spectrogram that define the second dimension
        :returns: Spectrogram object
        """

        s = Spectrogram()

        s._spectra = np.empty((len(times),), dtype=Spectrum)

        for i in range(len(times)):
            spec = Spectrum()
            spec._time_past_midnight = times[i]
            spec.frequencies = frequencies
            spec.pressures_pascals = levels[:, i]

            s._spectra[i] = spec

        return s

    # TODO: Implemenet Spectogram.calculate_normalized_distribution feature
    def calculate_normalized_distribution(self):
        warnings.warn('Spectogram.calculate_normalized_distribution feature not yet implemented.')