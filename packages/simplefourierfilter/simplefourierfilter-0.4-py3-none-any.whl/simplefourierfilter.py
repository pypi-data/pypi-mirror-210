import numpy as np
from numpy import fft
import matplotlib.pyplot as plt

def fourierFilter(X,ratio=0.3,method="threshold",nopadding=False,zeropadding=False,plotting="data"):
    """
    Noise filter which utilises Fourier transform to remove unwanted frequency components
    :param X: numpy array
        Time sequence with equal spacing.
    :param ratio: float (default 0.2)
        ratio can be used to level of filtering 
    :param method: string (default "threshold")
        "threshold": Uses amplitude thresholding to remove noise
        "lowpass": Simple lowpass filter to remove high frequency noise
        "dist": Cauchy distribution based scaling method for smooth function
    :param nopadding: boolean (default value "False")
        Function uses padding on both sides by default. When using periodic data this can be turned off
    :param zeropadding: boolean (default value "False")
        Function uses first and last value of given vector as padding. Can be changed if zero padding is preferable 
    :param plotting: string (default value "data")
        "data" plots original data and filtered data
        "frequency" plots original frequency spectrum and filtering conditions
        "both" plots both of above
        "none" disables plotting
    :return: numpy array
        Time sequence of after noise reduction was applied.
    """ 
    N = len(X)
    X_nopadding = X

    ## PADDING
    N_padding = int(np.ceil(N/2))
    if not nopadding:
        if zeropadding:
            start_pad = np.zeros(shape=N_padding)
            end_pad = np.zeros(shape=N_padding)
        else:
            start_pad = X[0]*np.ones(shape=N_padding)
            end_pad = X[-1]*np.ones(shape=N_padding)
        X = np.concatenate((start_pad,X,end_pad))

    c_orig = fft.fft(X)

    ## Threshold
    if method == "threshold":
        c = np.copy(c_orig)
        # Calculate threshold from standardized value
        th = max(np.abs(c))*(1-ratio)
        # zero all coefficient under chosen threshold
        for ii in range(0, len(c)):
            if np.abs(c[ii]) <= th:
                c[ii] = 0
        X_f = np.real(fft.ifft(c))
        

    # Low-pass cut-off
    elif method == "lowpass":

        N_cutoff = round(ratio*len(c_orig)/2)

        c = fft.fftshift(c_orig)
        # Middle point of the frequency spectrum
        x_m = int(np.ceil(len(c) / 2))
        # Initialize array for new coefficients
        c_new = np.zeros(len(c), dtype=np.complex_)

        c_new[x_m - N_cutoff:x_m + N_cutoff + 1] = c[x_m - N_cutoff:x_m + N_cutoff + 1]
        # Because of rounding errors some insignificant imaginary parts can be overlooked
        X_f = np.real(fft.ifft(fft.ifftshift(c_new)))
    
    # Caychy distribution
    elif method == "dist":
        c = fft.fftshift(c_orig)
        gamma = ratio/(1-ratio)
        gamma2 = gamma**2
        t = np.linspace(-1,1,len(c))
        cauchy = gamma2/(gamma2+np.power(t,2))
        c_new = c*cauchy
        X_f = np.real(fft.ifft(fft.ifftshift(c_new)))


    

    if not nopadding:
        X_f = X_f[N_padding:N_padding+N]
    
    # Plotting
    if plotting == "data" or plotting == "both":
        if plotting == "both":
            plt.subplot(211)
        else:
            plt.figure
        plt.plot(X_nopadding)
        plt.plot(X_f)
        plt.legend(("Original data","Filtered data"))

    if plotting == "frequency" or plotting == "both":
        if plotting == "both":
            plt.subplot(212)
        else:
            plt.figure

        # Normalization
       
        c_orig_norm = normalise(c_orig)
        omega_plot = np.linspace(0,1,len(c_orig_norm))
        plt.plot(omega_plot,c_orig_norm)


        if method == "threshold":
            plt.axhline(y=1-ratio,color='r')
            plt.legend(("Frequency spectrum","Threshold"))

        elif method == "lowpass":
            plt.axvline(x = ratio,color = 'r')
            plt.legend(("Frequency spectrum","Cut-off frequency"))
            
        elif method == "dist":
            n_mid = round(len(cauchy)/2)
            plt.plot(omega_plot,cauchy[n_mid:n_mid+len(omega_plot)])
            plt.legend(("Frequency spectrum","Scaling distribution"))
    plt.show()
    return X_f


def spectralDensity(X,Fs=1):
    """
    Function used to plot normalised spectral density distribution from time seriers
    :param X: numpy array
        Time sequence with equal spacing.
    :param Fs: float
        Sampling rate of data
    """
    c = fft.fft(X)
    L = len(c)
    c_mid = int(np.floor(L/2))
    omega = Fs * np.arange(0,c_mid)/L
    c2 = np.abs(c/L)
    c1 = c2[0:c_mid]
    c1[1:-1] = 2*c1[1:-1] 
    return


def normalise(c):
    N = len(c)
    c_mid = int(np.floor(N/2))
    c_norm = np.abs(c[0:c_mid])
    c_norm = c_norm/max(c_norm)
    return c_norm