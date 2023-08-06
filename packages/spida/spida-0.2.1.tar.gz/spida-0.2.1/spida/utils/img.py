import io
import base64
from PIL import Image
from matplotlib import pyplot as plt
import math
import numpy as np
from tkinter import Tk, filedialog

from . import misc

Tk().withdraw()


def show(
    img: np.ndarray, use_matplot: bool = False, cmap: str = None, vmin=None, vmax=None
):
    """
    Display the image using matplotlib or PIL based on the parameter.

    Parameters
    ----------
    img : numpy.ndarray
        The image array to be displayed.

    use_matplot : bool, optional
        If True, matplotlib is used to display the image, otherwise PIL is used. Default is False.

    cmap : str, optional
        The Colormap instance or registered colormap name used for matplotlib. Default is None.

    vmin, vmax : scalar, optional
        When using scalar data and no explicit norm, vmin and vmax define the data range that the colormap covers. Default is None.
    """
    if use_matplot:
        plt.imshow(img, cmap, vmin=vmin, vmax=vmax)
        plt.show()
    else:
        Image.fromarray(img).show()


def save(img: np.ndarray, file_name: str = None):
    """
    Save the image to a file. If no filename is given, it will generate one.

    Parameters
    ----------
    img : numpy.ndarray
        The image array to be saved.

    file_name : str, optional
        The filename of the output file. If None, a file name will be automatically generated. Default is None.
    """
    if file_name is None:
        png_files = [i for i in misc.get_cwd_files() if i.endswith(".png")]
        if png_files:
            img_num = int(png_files[-1].split(".")[0].split("_")[-1])
            file_name = f"img_{img_num+1}.png"
        else:
            file_name = "img_0.png"
    Image.fromarray(img).save(file_name)


def open(path: str = None):
    """
    Open an image file and return the image array.

    Parameters
    ----------
    path : str, optional
        The path of the image file. If None, a file dialog will be opened to select a file. Default is None.

    Returns
    -------
    numpy.ndarray
        The image array.
    """
    if path is None:
        path = filedialog.askopenfilename()
    return plt.imread(path)


def grid_img(imgs: np.ndarray, grid_shape: tuple = None, fill_value: int = 255):
    """
    Creates a grid of images from a provided set of images.

    Parameters
    ----------
    imgs : numpy.ndarray
        An array of images. If 3D, the shape should be (number of images, image height, image width).
        If 4D, the shape should be (number of images, image height, image width, number of channels).
        All images should have the same shape.

    grid_shape : tuple, optional
        The desired shape of the output grid. If not provided or if (None, None), a square grid is created.
        If one dimension is provided, the other is calculated to fit all images.

    fill_value : int, optional
        The pixel intensity value used for filling areas in the grid where no image is present. By default, this is set to 255 (white).

    Returns
    -------
    numpy.ndarray
        A grid of images with dimensions depending on the provided parameters.
        For grayscale images, the dimensions are (grid height * image height, grid width * image width),
        and for color images, the dimensions are (grid height * image height, grid width * image width, number of channels).
    """
    num_imgs, *img_shape = imgs.shape
    if grid_shape is None or grid_shape == (None, None):
        grid_height = grid_width = math.ceil(num_imgs**0.5)
    else:
        grid_height, grid_width = grid_shape
        if grid_height is None:
            grid_height = math.ceil(num_imgs / grid_width)
        if grid_width is None:
            grid_width = math.ceil(num_imgs / grid_height)
    dst_shape = img_shape.copy()
    dst_shape[0] *= grid_height
    dst_shape[1] *= grid_width
    dst = np.full(shape=dst_shape, fill_value=fill_value, dtype=imgs.dtype)
    h, w = img_shape[:2]
    for i, (y, x) in enumerate(np.ndindex(grid_height, grid_width)):
        if i < num_imgs:
            dst[
                y * h : (y + 1) * h,
                x * w : (x + 1) * w,
            ] = imgs[i]
        else:
            break
    return dst


def img2b64str(img: np.ndarray):
    """
    Convert a single image array to base64 string.

    Parameters
    ----------
    img : numpy.ndarray
        The image array to be converted.

    Returns
    -------
    str
        The base64 string of the image.
    """
    with io.BytesIO() as output_bytes:
        Image.fromarray(img).save(output_bytes, format="PNG")
        bytes_data = output_bytes.getvalue()
    return base64.b64encode(bytes_data).decode(encoding="utf-8")


def imgs2b64strs(imgs: np.ndarray):
    """
    Convert multiple image arrays to a list of base64 strings.

    Parameters
    ----------
    imgs : list of numpy.ndarray
        The list of image arrays to be converted.

    Returns
    -------
    list of str
        The list of base64 strings of the images.
    """
    return list(map(img2b64str, imgs))


def b64str2img(b64str: str):
    """
    Convert a base64 string to an image array.

    Parameters
    ----------
    b64str : str
        The base64 string to be converted.

    Returns
    -------
    numpy.ndarray
        The image array.
    """
    return np.array(Image.open(io.BytesIO(base64.b64decode(b64str.split(",", 1)[0]))))


def gray2rgb(gray_img: np.ndarray):
    """
    Convert a grayscale image to a RGB image.

    Parameters
    ----------
    gray_img : numpy.ndarray
        The grayscale image array to be converted.

    Returns
    -------
    numpy.ndarray
        The RGB image array.
    """
    return np.repeat(gray_img[:, :, np.newaxis], 3, axis=2)
