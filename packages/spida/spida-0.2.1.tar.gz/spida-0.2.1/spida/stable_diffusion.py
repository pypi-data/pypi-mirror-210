import json
import numpy as np
import importlib.resources as impr
import os
import pprint

from . import utils

# initialize config variable
config = {}

# get config.json path
with impr.as_file(impr.files("spida").joinpath("data")) as data_path:
    config_path = data_path.joinpath("config.json")


def set_config(config_dict: dict = None):
    """
    Configures Spida.

    By default prompts the user to input configuration settings via the terminal,
    but will use config_dict instead if specified.

    Parameters
    ----------
    config_dict : dict
        A dictionary of configuration settings for Spida, by default None.

    Returns
    -------
    None
        This function does not return a value; it changes Spida's config.json file.
    """
    if config_dict is None:
        config["fail_message"] = "Local server not running, starting..."
        config["webui_path"] = input(
            "Please input Stable Diffusion WebUI folder path\n"
        )
        webui_startfile = input(
            "\nPlease input Stable Diffusion WebUI startfile\n(if ENTER defaults to webui-user.bat)\n"
        )
        config["webui_startfile"] = (
            webui_startfile if webui_startfile else "webui-user.bat"
        )
        url = input(
            "\nPlease input API url\n(if ENTER defaults to http://127.0.0.1:7860)\n"
        )
        config["url"] = url if url else "http://127.0.0.1:7860"
        print()
    else:
        config.update(config_dict)
    with open(config_path, "w") as f:
        json.dump(config, f)


with open(config_path, "r") as f:
    config.update(json.load(f))
    if not config:
        print("Running one time configuration...\n")
        set_config()
        print("One time configuration complete!\n")


# PRIMARY FUNCTIONS


def start():
    """
    Starts the local API by running the specified start file from the configuration.

    Changes the current working directory to the path specified in the configuration,
    starts the file specified in the configuration, and then changes back to the original directory.

    Returns
    -------
    None
        This function does not return a value; it initiates the local API.
    """
    cwd = os.getcwd()
    os.chdir(config["webui_path"])
    os.startfile(config["webui_startfile"])
    os.chdir(cwd)


def model(name: str, search: bool = True):
    """
    Sets the Stable Diffusion (SD) model to be used.

    Parameters
    ----------
    name : str
        The name of the Stable Diffusion model.
    search : bool, optional
        Whether to search for the model, by default True.

    Returns
    -------
    None
        This function does not return a value; it posts the model selection to the API.
    """
    if search:
        name_res = search_models(name)[0]
    else:
        name_res = name
    option_payload = {"sd_model_checkpoint": name_res}
    utils.net.post(
        url=f'{config["url"]}/sdapi/v1/options',
        json=option_payload,
        fail_action=start,
        fail_message=config["fail_message"],
    )


def txt2img(
    prompt: str,
    negative_prompt: str = None,
    sampling_method: str = "UniPC",
    steps: int = 20,
    shape: tuple = (512, 512),
    batch_count: int = 1,
    batch_size: int = 1,
    cfg_scale: float = 7.0,
    clip_skip: int = None,
    styles: list = None,
    restore_faces: bool = False,
    tiling: bool = False,
    seed: int = -1,
    override_settings: dict = None,
    cnet_settings: dict = None,
    verbose: bool = False,
    **kwargs: dict,
):
    """
    Generates AI-generated images from a text prompt using the Stable Diffusion (SD) model.

    Parameters
    ----------
    prompt : str
        The text prompt for generating the images.
    negative_prompt : str, optional
        An optional negative text prompt, by default None.
    sampling_method : str, optional
        The sampling method to use for image generation, by default "UniPC".
    steps : int, optional
        The number of steps for the diffusion process, by default 20.
    shape : tuple, optional
        The shape (height, width) of the generated images, by default (512, 512).
    batch_count : int, optional
        The number of image batches to generate, by default 1.
    batch_size : int, optional
        The number of images per batch, by default 1.
    cfg_scale : float, optional
        The CFG scale value for controlling the generation process, by default 7.0.
    clip_skip : int, optional
        The number of layers to skip in the CLIP model. If not specified, uses the default configuration value, by default None.
    styles : list, optional
        A list of styles to use for image generation, by default None.
    restore_faces : bool, optional
        Whether to restore faces in the generated images, by default False.
    tiling : bool, optional
        Whether to produce tileable images, by default False.
    seed : int, optional
        The seed value for reproducibility. If seed is -1 (default), uses a random seed, by default -1.
    override_settings : dict, optional
        Additional settings to override the default configuration, by default None.
    cnet_settings : dict, optional
        ControlNet settings for conditioning the generation process. If not specified, ControlNet is not used, by default None.
    verbose : bool, optional
        Whether to print verbose information, by default False.
    **kwargs : dict
        Additional keyword arguments to include in the payload.

    Returns
    -------
    numpy.ndarray
        An array of generated images.
    """
    override = {}
    if clip_skip is not None:
        override["CLIP_stop_at_last_layers"] = clip_skip
    if override_settings is not None:
        override.update(override_settings)
    alwayson_scripts = {}
    if cnet_settings is not None:
        alwayson_scripts["controlnet"] = {"args": [cnet_settings]}
    payload = {
        "batch_size": batch_size,
        "cfg_scale": cfg_scale,
        "height": shape[0],
        "n_iter": batch_count,
        "negative_prompt": negative_prompt,
        "override_settings": override,
        "prompt": prompt,
        "restore_faces": restore_faces,
        "sampler_name": sampling_method,
        "sampler_index": sampling_method,
        "seed": seed,
        "steps": steps,
        "styles": styles,
        "tiling": tiling,
        "width": shape[1],
        "alwayson_scripts": alwayson_scripts,
    }
    payload.update(kwargs)
    response = utils.net.post(
        url=f'{config["url"]}/sdapi/v1/txt2img',
        json=payload,
        fail_action=start,
        fail_message=config["fail_message"],
    )
    r = response.json()
    if verbose:
        pprint.pprint(r["parameters"])
    dsts_b64strs = r["images"]
    size = (len(dsts_b64strs), shape[0], shape[1], 3)
    dsts = np.empty(shape=size, dtype=np.uint8)
    for i, v in enumerate(dsts_b64strs):
        dsts[i] = utils.img.b64str2img(v)
    return dsts


def annotate(
    imgs: np.ndarray,
    annotator: str = "depth",
    resolution: int = None,
    thresholds: tuple = (None, None),
    search: bool = True,
):
    """
    Annotates a batch of images using a specified ControlNet module.

    Parameters
    ----------
    imgs : numpy.ndarray
        Batch of images to be annotated. These should be numpy arrays.
    annotator : str, optional
        The ControlNet module used for the annotation. Defaults to "depth".
    resolution : int, optional
        The resolution of the preprocessor. If not specified, uses the smaller dimension of the input images.
    thresholds : tuple, optional
        Parameters of the preprocessor. Defaults to (None, None).
    search : bool, optional
        Whether to search for the annotator. Defaults to True.

    Returns
    -------
    numpy.ndarray
        A numpy array of the annotated images.
    """
    if search:
        annotator_res = search_annotators(annotator)[0]
    else:
        annotator_res = annotator
    if resolution is None:
        resolution = min(imgs.shape[1:3])
    b64strs = utils.img.imgs2b64strs(imgs)
    payload = {
        "controlnet_module": annotator_res,
        "controlnet_input_images": b64strs,
        "controlnet_processor_res": resolution,
        "controlnet_threshold_a": thresholds[0],
        "controlnet_threshold_b": thresholds[1],
    }
    response = utils.net.post(
        url=f'{config["url"]}/controlnet/detect',
        json=payload,
        fail_action=start,
        fail_message=config["fail_message"],
    )
    r = response.json()
    dsts_b64strs = r["images"]
    dst = utils.img.b64str2img(dsts_b64strs[0])
    size = (len(dsts_b64strs), *dst.shape)
    dsts = np.empty(shape=size, dtype=dst.dtype)
    dsts[0] = dst
    for i, v in enumerate(dsts_b64strs[1:], start=1):
        dsts[i] = utils.img.b64str2img(v)
    return dsts


def cnet_settings(
    annotated_img: np.ndarray,
    annotator: str = "depth",
    model: str = None,
    weight: float = 1.0,
    resolution: int = None,
    thresholds: tuple = (None, None),
    control_mode: int = 0,
    resize_mode: int = 1,
    guidance_start: float = 0.0,
    guidance_end: float = 1.0,
    mask: np.ndarray = None,
    lowvram: bool = False,
    search: bool = True,
):
    """
    Generates the settings for a ControlNet unit.

    Parameters
    ----------
    annotated_img : numpy.ndarray
        Annotated image to be used as input for the ControlNet unit.
    annotator : str, optional
        Preprocessor to use on the input image. Defaults to "depth".
    model : str, optional
        Name of the model to use for conditioning in the unit. If not specified, searches for the appropriate model.
    weight : float, optional
        Weight of the unit. Defaults to 1.0.
    resolution : int, optional
        Resolution of the preprocessor. If not specified, uses the smaller dimension of the input image.
    thresholds : tuple, optional
        Parameters of the preprocessor. Defaults to (None, None).
    control_mode : int, optional
        Defines the control mode. Accepted values are 0 (balanced), 1 (prompt is more important), 2 (ControlNet is more important). Defaults to 0 (balanced).
    resize_mode : int, optional
        Defines how to resize the input image. Accepted values are 0 (Just Resize), 1 (Scale to Fit (Inner Fit)), 2 (Envelope (Outer Fit)). Defaults to 1 (Scale to Fit (Inner Fit)).
    guidance_start : float, optional
        Ratio of generation where the unit starts to have an effect. Defaults to 0.0.
    guidance_end : float, optional
        Ratio of generation where the unit stops having an effect. Defaults to 1.0.
    mask : numpy.ndarray, optional
        Mask to filter the input image. If not specified, no mask is applied.
    lowvram : bool, optional
        Whether to compensate for low GPU memory with processing time. Defaults to False.
    search : bool, optional
        Whether to search for the annotator. Defaults to True.

    Returns
    -------
    dict
        A dictionary containing the settings for a ControlNet unit.
    """
    if search:
        annotator_res = search_annotators(annotator)[0]
    else:
        annotator_res = annotator
    if model is None:
        model = search_cnet_models(annotator)[0]
    if resolution is None:
        resolution = min(annotated_img.shape[:2])
    if mask is None:
        mask_b64str = None
    else:
        mask_b64str = utils.img.img2b64str(mask)
    input_b64str = utils.img.img2b64str(annotated_img)
    return {
        "input_image": input_b64str,
        "mask": mask_b64str,
        "module": annotator_res,
        "model": model,
        "weight": weight,
        "resize_mode": resize_mode,
        "lowvram": lowvram,
        "processor_res": resolution,
        "threshold_a": thresholds[0],
        "threshold_b": thresholds[1],
        "guidance_start": guidance_start,
        "guidance_end": guidance_end,
        "control_mode": control_mode,
    }


# GETS AND SEARCHES


def get_models():
    """
    Retrieve the list of available Stable Diffusion (SD) models.

    Returns
    -------
    list
        A list of available SD models.
    """
    response = utils.net.get(
        url=f'{config["url"]}/sdapi/v1/sd-models',
        fail_action=start,
        fail_message=config["fail_message"],
    )
    r = response.json()
    return sorted([i["title"] for i in r])


def search_models(query: str):
    """
    Search for Stable Diffusion (SD) models that match the specified query.

    Parameters
    ----------
    query : str
        The search query.

    Returns
    -------
    list
        A list of SD models that match the query.
    """
    return utils.misc.search(query=query, lst=get_models())


def get_samplers():
    """
    Retrieve the list of available sampling methods for image generation.

    Returns
    -------
    list
        A list of available sampling methods.
    """
    response = utils.net.get(
        url=f'{config["url"]}/sdapi/v1/samplers',
        fail_action=start,
        fail_message=config["fail_message"],
    )
    r = response.json()
    return sorted([i["name"] for i in r])


def search_samplers(query: str):
    """
    Search for sampling methods that match the specified query.

    Parameters
    ----------
    query : str
        The search query.

    Returns
    -------
    list
        A list of sampling methods that match the query.
    """
    return utils.misc.search(query=query, lst=get_samplers())


def get_styles():
    """
    Retrieve the list of available prompt styles.

    Returns
    -------
    list
        A list of available prompt styles.
    """
    response = utils.net.get(
        url=f'{config["url"]}/sdapi/v1/prompt-styles',
        fail_action=start,
        fail_message=config["fail_message"],
    )
    r = response.json()
    return sorted([i["name"] for i in r])


def search_styles(query: str):
    """
    Search for prompt styles that match the specified query.

    Parameters
    ----------
    query : str
        The search query.

    Returns
    -------
    list
        A list of prompt styles that match the query.
    """
    return utils.misc.search(query=query, lst=get_styles())


def get_annotators():
    """
    Retrieve the list of available ControlNet modules.

    Returns
    -------
    list
        A list of available ControlNet modules.
    """
    response = utils.net.get(
        url=f'{config["url"]}/controlnet/module_list',
        fail_action=start,
        fail_message=config["fail_message"],
    )
    r = response.json()
    return sorted(r["module_list"])


def search_annotators(query: str):
    """
    Search for ControlNet modules that match the specified query.

    Parameters
    ----------
    query : str
        The search query.

    Returns
    -------
    list
        A list of ControlNet modules that match the query.
    """
    return utils.misc.search(query=query, lst=get_annotators())


def get_cnet_models():
    """
    Retrieve the list of available models for the ControlNet unit.

    Returns
    -------
    list
        A list of available ControlNet models.
    """
    response = utils.net.get(
        url=f'{config["url"]}/controlnet/model_list',
        fail_action=start,
        fail_message=config["fail_message"],
    )
    r = response.json()
    return sorted(r["model_list"])


def search_cnet_models(query: str):
    """
    Search for ControlNet models that match the specified query.

    Parameters
    ----------
    query : str
        The search query.

    Returns
    -------
    list
        A list of ControlNet models that match the query.
    """
    return utils.misc.search(query=query, lst=get_cnet_models())
