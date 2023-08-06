import sys
import numpy as np


class FractionalOctaveBandTools:
    """
    A collection of static functions that provide some conversion and manipulative functions for the fractional octave
    band frequencies.
    """

    @staticmethod
    def nearest_band(resolution, frequency):
        """
        Determine the nearest band at a specific fractional octave resolution

        resolution : int
            the fractional octave resolution that will be used to determine the band number (currently only full, 1/3,
            and 1/12 are implemented)
        frequency : double
            the frequency to analyze within the selected resolution

        returns : double
            the nearest (floor) band number within the selected resolution that the frequency exists
        """

        band = 0.0

        if resolution == 1:
            band = np.log(frequency / 1000) / np.log(2.0)
        elif resolution == 3:
            band = np.log(frequency / 1000) / np.log(2.0)
            band *= 3.0
            band += 30
        elif resolution == 6:
            band = np.log(frequency / (1000 * 2.0 ** (1.0 / 12.0))) / np.log(2.0)
            band *= 6
        elif resolution == 12:
            band = np.log(frequency / (1000 * 2.0 ** (1.0 / 24.0))) / np.log(2.0)
            band *= 12
        elif resolution == 24:
            band = np.log(frequency / (1000 * 2.0 ** (1.0 / 48.0))) / np.log(2.0)
            band *= 24

        return band

    @staticmethod
    def center_frequency(resolution, band):
        """
        Using the resolution and band number, determine the center frequency of the acoustic band

        resolution : double/int
            the fractional octave band resolution to compute the center frequency (only full, 1/3, and 1/12 are
            implemented)
        band : double/int
            the band number within the fractional octave resolution that is to be calculated

        returns : double
            the frequency at the center of the band, units: Hz
        """
        frequency = 0
        if resolution == 1:
            frequency = 1000.0 * 2.0 ** band
        elif resolution == 3:
            frequency = 1000 * 2.0 ** ((band - 30.0) / 3.0)
        elif resolution == 6:
            frequency = 1000 * 2.0 ** (1 / 12) * 2.0 ** (band / 6)
        elif resolution == 12:
            frequency = 1000 * 2.0 ** (1.0 / 24.0) * 2.0 ** (band / 12)
        elif resolution == 24:
            frequency = 1000 * 2.0 ** (1 / 48) * 2.0 ** (band / 24)
        return frequency

    @staticmethod
    def lower_frequency(resolution, band):
        """
        Given the resolution and the band number, determine the center band frequency and then the lower frequency

        resolution : double/int
            the fractional octave band resolution to compute the center frequency (only full, 1/3, and 1/12 are
            implemented)
        band : double/int
            the band number within the fractional octave resolution that is to be calculated

        returns : double
            the lower frequency of this band
        """
        return 2.0 ** (-1.0 / (2.0 * resolution)) * FractionalOctaveBandTools.center_frequency(resolution, band)

    @staticmethod
    def upper_frequency(resolution, band):
        """
        Given the resolution and the band number, determine the center band frequency and then the upper frequency

        resolution : double/int
            the fractional octave band resolution to compute the center frequency (only full, 1/3, and 1/12 are
            implemented)
        band : double/int
            the band number within the fractional octave resolution that is to be calculated

        returns : double
            the upper frequency of this band
        """

        return 2.0 ** (+1.0 / (2.0 * resolution)) * FractionalOctaveBandTools.center_frequency(resolution, band)

    @staticmethod
    def band_width(resolution, band):
        """
        Given the resolution and the band number, determine the upper and lower frequencies of the band...thus
        calculating the width of the band

        resolution : double/int
            the fractional octave band resolution to compute the center frequency (only full, 1/3, and 1/12 are
            implemented)
        band : double/int
            the band number within the fractional octave resolution that is to be calculated

        returns : double
            difference between the upper and lower frequencies
        """

        return FractionalOctaveBandTools.upper_frequency(resolution, band) - FractionalOctaveBandTools.lower_frequency(
            resolution,
            band)

    @staticmethod
    def frequencies(start_band, end_band, resolution) -> list:
        """
        Generate the exact frequencies between the start and stop at the provided resolution

        start_band : int
            the starting band within the resolution to start the array
        end_band : int
            the ending band within the resolution to end the array
        resolution : int
            the resolution to calculate the center frequencies

        return : double, array-like
            the frequencies from the start to the stop bands at the selected resolution
        """
        if isinstance(start_band, int) and isinstance(end_band, int) and isinstance(resolution, int):
            f = []
            for index in range(start_band, end_band + 1):
                f.append(FractionalOctaveBandTools.center_frequency(resolution, index))
            return f
        else:
            raise ValueError("You must supply integer values for the start and stop bands, and the frequency "
                             "resolution")

    @staticmethod
    def min_audible_field(frequency):
        """
        This function calculates a curve fit to the minimum audible field according to an equation provided
        by NASA in the AUDIB code.  Reference USAAMRDL-TR-74-102A.

        @author: Gregory Bowers and Frank Mobley

        frequency : double
            the frequency to calculate the minimum audible field

        returns : double
            the minimum audible field at the selected frequency
        """

        log10f = np.log10(frequency)
        log10fpower = log10f
        result = 273.3674 - 584.1369 * log10fpower
        log10fpower *= log10f
        result += 860.3995 * log10fpower
        log10fpower *= log10f
        result -= 690.0302 * log10fpower
        log10fpower *= log10f
        result += 283.4491 * log10fpower
        log10fpower *= log10f
        result -= 56.89755 * log10fpower
        log10fpower *= log10f
        return result + 4.440361 * log10fpower

    @staticmethod
    def get_min_audible_fields():
        """
        Gather the minimum audible field values within the calculated frequencies from 10 Hz to 10 kHz

        returns : double, array-like
            the minimum audible field based on the NASA interpolation at the exact frequencies from 10 Hz to 10 kHz
        """

        results = []
        for f in FractionalOctaveBandTools.tob_frequencies():
            results.append(FractionalOctaveBandTools.min_audible_field(f))

        return np.array(results)

    @staticmethod
    def frequencies_ansi_preferred(f0: float = 10, f1: float = 10000, bandwidth: int = 3):
        """
        This function provides the list of accepted frequencies from the ANSI S1.6 definition of the shape of fractional
        octave bands.
        """
        import warnings

        warnings.warn("These should be used for labeling purposes only. All calculations relying on frequency band "
                      "centers or band limits should use the 'frequencies' object within the spectral class.",
                      UserWarning,
                      stacklevel=3)

        ansi_preferred_frequencies = np.array([1, 1.25, 1.6, 2, 2.5, 3.15, 4, 5, 6.3, 8])
        ansi_preferred_frequencies = np.concatenate((
            ansi_preferred_frequencies,
            ansi_preferred_frequencies * 10,
            ansi_preferred_frequencies * 100,
            ansi_preferred_frequencies * 1000,
            ansi_preferred_frequencies * 10000,
            ansi_preferred_frequencies * 100000
        ))

        #   If the data is octave, only sample every third element

        if bandwidth == 1:
            ansi_preferred_frequencies = ansi_preferred_frequencies[np.arange(0, len(ansi_preferred_frequencies), 3)]
        elif (bandwidth != 3) & (bandwidth != 1):
            raise ValueError("The ANSI standard only defines the correct frequencies for the full and one-third "
                             "octaves")

        return ansi_preferred_frequencies[np.where((ansi_preferred_frequencies >= f0) &
                                                   (ansi_preferred_frequencies <= f1))[0]]

    @staticmethod
    def tob_frequencies_ansi():
        """
        The accepted frequencies for the one-third-octave bands from 10 Hz to 10 kHz
        """
        output = [10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80
            , 100, 125, 160, 200, 250, 315, 400, 500, 630, 800
            , 1000, 1250, 1600, 2000, 2500, 3150, 4000
            , 5000, 6300, 8000, 10000]
        return output

    @staticmethod
    def tob_frequencies():
        """
        The exact frequencies from 10 Hz to 10 kHz using the center_frequency function at the one-third frequency
        resolution.
        """

        output = np.array([9.843133, 12.401571, 15.625, 19.686266, 24.803141
                              , 31.25, 39.372533, 49.606283, 62.5, 78.745066
                              , 99.212566, 125.0, 157.490131, 198.425131, 250.0, 314.980262
                              , 396.850263, 500.0, 629.960525, 793.700526
                              , 1000.0, 1259.92105, 1587.401052, 2000.0, 2519.8421, 3174.802104
                              , 4000.0, 5039.6842, 6349.604208, 8000.0, 10079.3684], dtype=float)

        return output

    @staticmethod
    def tob_to_erb(x, spl):
        """
        Convert the data form the one-third-octave bandwidth to the equivalent rectangular band bandwidth

        x : double/int
            the band frequency to convert (double) or the band index within the spectrum from 10 Hz t0 10 kHz (int)
        spl : double
            the sound pressure level at the selected frequency

        returns : double
            the sound pressure level adjusted for the difference between the TOB and ERB bandwidths
        """

        if isinstance(x, int):
            index = x - 10
            delta = 20 * np.log10(FractionalOctaveBandTools.center_frequency_to_erb(
                FractionalOctaveBandTools.tob_frequencies()[index]) / FractionalOctaveBandTools.band_width(3, x))
        elif isinstance(x, float):
            bandwidth = (np.power(2.0, 1.0 / 6.0) - np.power(2.0, -1.0 / 6.0)) * x
            delta = 20 * np.log10(FractionalOctaveBandTools.center_frequency_to_erb(x) / bandwidth)

        if delta > 0:
            return spl
        else:
            return spl + delta

    @staticmethod
    def center_frequency_to_erb(frequency):
        """
        This function converts the center frequency to the Equivalent Rectangular Band (ERB)

        frequency : double
            the center frequency of the one-third-octave band, Units: Hz

        returns : double
            the bandwidth of the ERB at the selected center frequency
        """
        return 24.7 * (0.00437 * frequency + 1)

    @staticmethod
    def erb_to_center_frequency(erb):
        return ((erb / 24.7) - 1) / 0.00437

    @staticmethod
    def get_frequency_array(band_width: int = 3, f0: float = 10, f1: float = 10000):

        # Build the collection of frequencies based on the input parameters from the argument list
        accepted_bandwidths = np.array([1, 3, 6, 12, 24], dtype=float)

        if band_width not in accepted_bandwidths:
            raise ValueError("You did not provide a valid bandwidth")

        band0 = int(np.floor(FractionalOctaveBandTools.nearest_band(band_width, f0)))

        freqs = list()

        f1_upper = f1 * 2 ** (1 / (2 * band_width))
        band_no = band0

        while FractionalOctaveBandTools.center_frequency(band_width, band_no) < f1_upper:
            freqs.append(FractionalOctaveBandTools.center_frequency(band_width, band_no))
            band_no += 1

        return np.asarray(freqs)

    @staticmethod
    def filter_shape(bandwidth: float = 3, center_frequency: float = 1000, narrowband_frequencies=None):
        """
        This function defines the shape of the one-third octave band based on the narrowband frequencies that are
        provided. This is based on the information from Matlab scripts provided by Brigham Young University researchers.
        """

        #   Define the band edges of the frequency band
        b = 2 * bandwidth
        f_low = center_frequency * 2 ** (-1 / b)
        f_high = center_frequency * 2 ** (1 / b)

        #   Get the ratio of the bandwidth to the frequency
        qr = center_frequency / (f_high - f_low)
        qd = (np.pi / b) / (np.sin(np.pi / b)) * qr
        qd = qd ** 6

        #   Define the squared weighted shape of the band at these frequencies
        delta_f_psd = narrowband_frequencies / (center_frequency + sys.float_info.epsilon)
        delta_f_fob = center_frequency / (narrowband_frequencies + sys.float_info.epsilon)
        frequency_delta = (delta_f_psd - delta_f_fob) ** 6

        return abs(1 / (1 + qd * frequency_delta))

    @staticmethod
    def ansi_band_limits(class_: int = 0, fc: float = 1000, nth_oct: int = 3):
        """
        This function will calculate the constant percentage bandwidth description of the accepted shape based on the
        ANSI S1.11 standard.

        Parameters
        ----------
        class_: int - the class of the filter that we are trying to design
        fc: float, default: 1000 - the center frequency of the band that we are plotting

        Returns
        -------
        frequency: float, array-like - the collection of frequencies
        shape_lo: float, array-like - the levels of the lower limit of the filter design
        shape_hi: float, array-like - the levels of the upper limit of the filter design
        """

        if nth_oct == 1:
            frequency = np.array([2 ** -4, 2 ** -3, 2 ** -2, 2 ** -1, 2 ** -0.5, 2 ** -(3 / 8), 2 ** -0.25,
                                  2 ** (-1 / 8), 2 ** 0, 2 ** (1 / 8), 2 ** 0.25, 2 ** (3 / 8), 2 ** 0.5, 2 ** 1,
                                  2 ** 2, 2 ** 3, 2 ** 4]) * fc
        elif nth_oct == 3:
            frequency = np.array([0.187, 0.32578, 0.52996, 0.77181, 0.89090, 0.91932, 0.94702, 0.97394, 1., 1.02676,
                                  1.05594, 1.08776, 1.12246, 1.29565, 1.88695, 3.06955, 5.43474]) * fc

        if class_ == 0:
            lo = np.array([-75, -62, -42.5, -18, -2.3, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, -2.3, -18, -42.5, -62,
                           -75])
            hi = np.array([-np.infty, -np.infty, -np.infty, -np.infty, -4.5, -1.1, -.4, -.2, -.15, -.2, -.4, -1.1, -4.5,
                           -np.infty, -np.infty, -np.infty, -np.infty])
        elif class_ >= 1:
            lo = []
            hi = []

        return frequency, lo, hi
