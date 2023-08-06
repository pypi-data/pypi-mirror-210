import numpy as np

from .FRC_lib import radial_profile


# %%

def Reorder(data, inOrder: str, outOrder: str = 'rzxytc'):
    '''
    It reorders a dataset to match the desired order of dimensions.
    If some dimensions are missing, it adds new dimensions.

    Parameters
    ----------
    data : ndarray
        ISM dataset.
    inOrder : str
        Order of the dimension of the data.
        It can contain any letter of the outOrder string.
    outOrder : str, optional
        Order of the output. The default is 'rzxytc'.

    Returns
    -------
    data : ndarray
        ISM dataset reordered.

    '''

    if not (inOrder == outOrder):
        # adds missing dimensions
        Nout = len(outOrder)
        dataShape = np.shape(data)
        Ndim = len(dataShape)
        for i in range(Nout - Ndim):
            data = np.expand_dims(data, Ndim + i)

        # check order of dimensions
        order = []
        newdim = 0
        for i in range(Nout):
            dim = outOrder[i]
            if dim in inOrder:
                order.append(inOrder.find(dim))
            else:
                order.append(Ndim + newdim)
                newdim += 1
        data = np.transpose(data, order)

    return data


def CropEdge(dset, npx=10, edges='l', order: str = 'rzxytc'):
    '''
    It crops an ISM dataset along the specified edges of the xy plane.
    
    Parameters
    ----------
    dset : ndarray
        ISM dataset
    npx : int, optional
        Number of pixel to crop from each edge. The default is 10.
    edges : str, optional
        Cropped edges. The possible values are 'l' (left),'r' (right),
        'u' (up), and 'd' (down). Any combination is possible. The default is 'l'.
    order : str, optional
        Order of the dimensions of the dataset The default is 'rzxytc'.

    Returns
    -------
    dset_cropped : ndarray
        ISM dataset cropped

    '''

    dset_cropped = Reorder(dset, order)

    if 'l' in edges:
        dset_cropped = dset_cropped[..., npx:, :, :, :]

    if 'r' in edges:
        dset_cropped = dset_cropped[..., :-npx, :, :, :]

    if 'u' in edges:
        dset_cropped = dset_cropped[..., :, npx:, :, :]

    if 'd' in edges:
        dset_cropped = dset_cropped[..., :, :-npx, :, :]

    return np.squeeze(dset_cropped)


def DownSample(dset, ds: int = 2, order: str = 'rzxytc'):
    '''
    It downsamples an ISM dataset on the xy plane.
    
    Parameters
    ----------
    dset : ndarray
        ISM dataset.
    ds : int, optional
        Downsampling factor. The default is 2.
    order : str, optional
        Order of the dimensions of the dataset The default is 'rzxytc'.
        
    Returns
    -------
    dset_ds : ndarray
        ISM dataset downsampled.

    '''

    dset = Reorder(dset, order)

    dset_ds = dset[..., ::ds, ::ds, :, :]

    return np.squeeze(dset_ds)


def UpSample(dset, us: int = 2, npx: str = 'even', order: str = 'rzxytc'):
    '''
    It upsamples an ISM dataset on the xy plane.

    Parameters
    ----------
    dset : TYPE
        ISM dataset.
    us : int, optional
        Upsampling factor. The default is 2.. The default is 2.
    npx : str, optional
        Parity of the number of pixels on each axis. The default is 'even'.
    order : str, optional
        Order of the dimensions of the dataset The default is 'rzxytc'.

    Returns
    -------
    dset_us : ndarray
        ISM dataset upsampled.

    '''

    dset = Reorder(dset, order)

    sz = dset.shape

    if npx == 'even':
        sz_us = np.asarray(sz)
        sz_us[2] = sz_us[2] * us
        sz_us[3] = sz_us[3] * us
    elif npx == 'odd':
        sz_us = np.asarray(sz)
        sz_us[2] = sz_us[2] * us - 1
        sz_us[3] = sz_us[3] * us - 1

    dset_us = np.zeros(sz_us)
    dset_us[..., ::us, ::us, :, :] = dset

    return np.squeeze(dset_us)


def ArgMaxND(data):
    '''
    It finds the the maximum and the corresponding indeces of a N-dimensional array.

    Parameters
    ----------
    data : ndarray
        N-dimensional array.

    Returns
    -------
    arg : ndarray(int)
        indeces of the maximum.
    mx : float
        maximum value.

    '''

    idx = np.argmax(data)

    mx = np.array(data).ravel()[idx]

    arg = np.unravel_index(idx, np.array(data).shape)

    return arg, mx


def FWHM(x, y):
    '''
    It calculates the Full Width at Half Maximum of a 1D curve.

    Parameters
    ----------
    x : ndarray
        Horizontal axis.
    y : ndarray
        Curve.

    Returns
    -------
    FWHM: float
        Full Width at Half Maximum of the y curve.

    '''

    height = 0.5
    height_half_max = np.max(y) * height
    index_max = np.argmax(y)
    x_low = np.interp(height_half_max, y[:index_max], x[:index_max])
    x_high = np.interp(height_half_max, np.flip(y[index_max:]), np.flip(x[index_max:]))

    return x_high - x_low


def RadialSpectrum(img, pxsize: float = 1, normalize: bool = True):
    '''
    It calculates the radial spectrum of a 2D image.

    Parameters
    ----------
    img : ndarray
        2D image.
    pxsize : float, optional
        Pixel size. The default is 1.
    normalize : bool, optional
        If True, the result is divided by its maximum. The default is True.

    Returns
    -------
    ftR : ndarray
        Radial spectrum.
    space_f : ndarray
        Frequency axis.

    '''

    fft_img = np.fft.fftn(img, axes=[0, 1])
    fft_img = np.abs(np.fft.fftshift(fft_img, axes=[0, 1]))

    sx, sy = fft_img.shape
    c = (sx // 2, sy // 2)

    space_f = np.fft.fftfreq(sx, pxsize)[:c[0]]

    ftR = radial_profile(fft_img, c)

    ftR = ftR[0][:c[0]] / ftR[1][:c[0]]

    ftR = np.real(ftR)

    if normalize == True:
        ftR /= np.max(ftR)

    return ftR, space_f


# %%

import matplotlib.pyplot as plt

from matplotlib_scalebar.scalebar import ScaleBar
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import Normalize

import numbers


def ShowImg(image: np.ndarray, pxsize_x: float, clabel: str = None, vmin: float = None, vmax: float = None,
            fig: plt.Figure = None, ax: plt.axis = None, cmap: str = 'hot'):
    """
    It shows the input image with a scalebar and a colorbar.
    It returns the corresponding figure and axis.

    Parameters
    ----------
    image : np.ndarray
        Image (Nx x Ny).
    pxsize_x : float
        Pixel size in micrometers (um).
    clabel : str
        Label of the colorbar.
    vmin : float, optional
        Lower bound of the intensity axis.
        If None, is set to the minimum value of the image.
        The default is None.
    vmax : float, optional
        Upper bound of the intensity axis.
        If None, is set to the maximum value of the image.
        The default is None.
    fig : plt.Figure, optional
        Figure where to display the plot. If None, a new figure is created.
        The default is None.
    ax : plt.axis, optional
        Axis where to display the plot. If None, a new axis is created.
        The default is None.
    cmap : str, optional
        Colormap, to be chosen within the matplotlib list.
        The default is 'hot'.

    Returns
    -------
    fig : plt.Figure
        Matplotlib figure.
    ax : plt.axis
        Matplotlib axis.

    """

    if fig == None or ax == None:
        fig, ax = plt.subplots()

    im = ax.imshow(image, vmin=vmin, vmax=vmax, cmap=cmap)
    ax.axis('off')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(im, cax=cax, ticks=[])
    # ax.text(1.0,0.4, clabel, rotation=90, transform=ax.transAxes)

    # cbar.ax.set_ylabel(clabel, labelpad=-11, rotation=90)
    #
    # cbar.ax.text(1.02, 0.9, f'{int(np.floor(np.max(image)))}', rotation=90, transform=ax.transAxes)
    #
    # cbar.ax.text(1.02, 0.02, f'{int(np.floor(np.min(image)))}', rotation=90, transform=ax.transAxes, color='white')

    vmax = int(np.floor(np.max(image)))
    vmin = int(np.floor(np.min(image)))

    cbar.ax.text(0.6, 0.5, clabel, horizontalalignment='center', verticalalignment='center',
                 rotation='vertical', transform=cax.transAxes)
    cbar.ax.text(0.6, 0.98, f'{vmax}', horizontalalignment='center', verticalalignment='top',
                 rotation='vertical', transform=cax.transAxes)
    cbar.ax.text(0.6, 0.02, f'{vmin}', horizontalalignment='center', verticalalignment='bottom',
                 rotation='vertical', transform=cax.transAxes, color='white')

    scalebar = ScaleBar(
        pxsize_x, "um",  # default, extent is calibrated in meters
        box_alpha=0,
        color='w',
        length_fraction=0.25)

    ax.add_artist(scalebar)

    return fig, ax


def ShowDataset(dset: np.ndarray, cmap: str = 'hot', pxsize: float = None, normalize: bool = False,
                colorbar: bool = False, xlims: list = [None, None], ylims: list = [None, None],
                figsize: tuple = (6, 6)) -> plt.Figure:
    '''
    It displays all the images of the ISM dataset in a squared grid.
    It returns the corresponding figure.

    Parameters
    ----------
    dset : np.ndarray
        ISM dataset (Nx x Ny x Nch).
    cmap : str, optional
        Colormap, to be chosen within the matplotlib list. The default is 'hot'.
    pxsize : float, optional
        Pixel size in micrometers (um). The default is None.
    normalize : bool, optional
        If True, each image is normalized with respect to the whole dataset.
        If False, each image is normalized to itself.
        The default is False.
    colorbar : bool, optional
        If true, a colorbar is shown. The default is False.
    xlims : list, optional
        If given, only the region with the x-range is displayed. The default is [None, None].
    ylims : list, optional
        If given, only the region with the y-range is displayed. The default is [None, None].
    figsize : tuple, optional
        Size of the figure. The default is (6, 6).

    Returns
    -------
    fig : plt.Figure
        Matplotlib figure.
    '''

    N = int(np.sqrt(dset.shape[-1]))

    if normalize == True:
        vmin = np.min(dset)
        vmax = np.max(dset)
        norm = Normalize(vmin=vmin, vmax=vmax)

    fig, ax = plt.subplots(N, N, sharex=True, sharey=True, figsize=figsize)
    for i in range(N * N):
        idx = np.unravel_index(i, [N, N])
        if normalize == True:
            im = ax[idx].imshow(dset[:, :, i], norm=norm, cmap=cmap)
        else:
            im = ax[idx].imshow(dset[:, :, i], cmap=cmap)
        ax[idx].set_xlim(xlims)
        ax[idx].set_ylim(ylims)
        ax[idx].axis('off')

    if isinstance(pxsize, numbers.Number):
        scalebar = ScaleBar(
            pxsize, "um",  # default, extent is calibrated in meters
            box_alpha=0,
            color='w',
            location='lower right',
            length_fraction=0.5)

        ax[-1, -1].add_artist(scalebar)

    fig.tight_layout()
    if colorbar == True and normalize == True:
        y0 = ax[-1, -1].get_position().y0
        y1 = ax[0, 0].get_position().y1
        height = y1 - y0

        fig.subplots_adjust(right=0.92)
        cbar_ax = fig.add_axes([0.94, y0, 0.05, height])
        cbar = fig.colorbar(im, cax=cbar_ax, ticks=[])

        cbar.ax.text(0.3, 0.95, f'{int(np.floor(vmax))}', rotation=90, transform=cbar_ax.transAxes)

        cbar.ax.text(0.3, 0.02, f'{int(np.floor(vmin))}', rotation=90, transform=cbar_ax.transAxes, color='white')

    return fig


def PlotShiftVectors(shift_vectors: np.ndarray, pxsize: float = 1, labels: bool = True, color: np.ndarray = None,
                     cmap: str = 'summer_r', fig: plt.Figure = None, ax: plt.axis = None):
    """
    It plots the shift vectors in a scatter plot.
    It returns the corresponding figure and axis.

    Parameters
    ----------
    shift_vectors : np.ndarray
        Array of the coordinates of the shift vectors (Nch x 2).
    pxsize : float, optional
        Pixel size in micrometers (um). The default is 1.
    labels : bool, optional
        If true, the channel number is printed close to each point.
        The default is True.
    color : np.ndarray, optional
        Array defining the color value (Nch).
        The default is None.
    cmap : str, optional
        Colormap, to be chosen within the matplotlib list.
        The default is 'summer_r'.
    fig : plt.Figure, optional
        Figure where to display the plot. If None, a new figure is created.
        The default is None.
    ax : plt.axis, optional
        Axis where to display the plot. If None, a new axis is created.
        The default is None.

    Returns
    -------
    fig : plt.Figure
        Matplotlib figure.
    ax : plt.axis
        Matplotlib axis.

    """

    if fig == None or ax == None:
        fig, ax = plt.subplots()

    shift = shift_vectors * pxsize

    Nch = shift.shape[0]

    if color == 'auto':
        N = int(np.sqrt(Nch))
        x = np.arange(-(N // 2), N // 2 + 1)
        X, Y = np.meshgrid(x, x)
        R = np.sqrt(X ** 2 + Y ** 2)
        color = R

    ax.scatter(shift[:, 0], shift[:, 1], s=80, c=color, edgecolors='black', cmap=cmap)
    ax.set_aspect('equal', 'box')

    if labels == True:
        for n in range(Nch):
            ax.annotate(str(n), shift[n], xytext=(3, 3), textcoords='offset points')

    ax.set_xlabel(r'Shift$_x$ (nm)')
    ax.set_ylabel(r'Shift$_y$ (nm)')
    ax.set_title('Shift vectors')

    ax.set_aspect('equal')

    return fig, ax


def ShowFingerprint(dset: np.ndarray, cmap: str = 'hot', colorbar: bool = False, clabel: str = None, normalize: bool = False, fig: plt.Figure = None,
                    ax: plt.axis = None):
    """
    It calculates and shows the fingerprint of an ISM dataset.
    It returns the corresponding figure and axis.

    Parameters
    ----------
    dset : np.ndarray
        ISM dataset (Nx x Ny x Nch).
    cmap : str, optional
        Colormap, to be chosen within the matplotlib list. The default is 'hot'.
    colorbar : bool, optional
        If true, a colorbar is shown. The default is False
    clabel : str, optional
        Label of the colorbar. The default is None
    normalize : bool, optional
        If true, the fingerprint values are normalized between 0 and 1. The default is False
    fig : plt.Figure, optional
        Figure where to display the plot. If None, a new figure is created.
        The default is None.
    ax : plt.axis, optional
        Axis where to display the plot. If None, a new axis is created.
        The default is None.

    Returns
    -------
    fig : plt.Figure
        Matplotlib figure.
    ax : plt.axis
        Matplotlib axis.
    """

    if fig == None or ax == None:
        fig, ax = plt.subplots()

    N = int( np.sqrt(dset.shape[-1]) )
    fingerprint = dset.sum(axis=(0, 1)).reshape(N, N)
    if normalize == True:
        max_counts = np.max(fingerprint)
        fingerprint = fingerprint / max_counts
    im = ax.imshow(fingerprint, cmap=cmap)

    ax.axis('off')
    fig.tight_layout()

    if colorbar == True:

        vmax = int(np.floor(np.max(fingerprint)))
        vmin = int(np.floor(np.min(fingerprint)))

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        cbar = fig.colorbar(im, cax=cax, ticks=[])

        cbar.ax.text(0.6, 0.5, clabel, horizontalalignment='center', verticalalignment='center',
                     rotation='vertical', transform=cax.transAxes)
        cbar.ax.text(0.6, 0.98, f'{vmax}', horizontalalignment='center', verticalalignment='top',
                     rotation='vertical', transform=cax.transAxes)
        cbar.ax.text(0.6, 0.02, f'{vmin}', horizontalalignment='center', verticalalignment='bottom',
                     rotation='vertical', transform=cax.transAxes, color='white')

    return fig, ax
