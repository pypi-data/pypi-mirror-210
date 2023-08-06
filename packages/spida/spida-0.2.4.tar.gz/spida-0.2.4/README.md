# Spida: Stable Diffusion API Wrapper for Automatic1111 WebUI

[![PyPI Version](https://img.shields.io/pypi/v/spida.svg)](https://pypi.org/project/spida/)
[![License](https://img.shields.io/pypi/l/spida.svg)](https://github.com/h2see/spida/blob/master/LICENSE)

Spida is a Python package that serves as a wrapper for the Stable Diffusion API provided by the Automatic1111 WebUI. It simplifies the usage of the Stable Diffusion model for generating AI-generated images from text prompts. Spida also includes support for the ControlNet extension, allowing users to condition the generation process using ControlNet modules. Spida is an anagram of SDAPI (Stable Diffusion API).

## Dependencies

Spida requires the [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) with the [ControlNet Extension](https://github.com/Mikubill/sd-webui-controlnet). Spida was tested with Stable Diffusion WebUI git commit hash `89f9faa63388756314e8a1d96cf86bf5e0663045` and ControlNet Extension git commit hash `d831043cb81e97724ccf9f071da391d479440a77`.

**Note:** You must use the `--api` command line argument in the `webui_startfile`.

## Installation

You can install Spida using pip:

```shell
pip install spida
```

## Usage

### Quick Start

To use Spida in your python project, import it as shown here:

```python
import spida
```

The following code demonstrates a basic call to the `txt2img()` function. The code uses the prompt `"cow"` returns a numpy image array, `imgs`. Only one image is created, so `imgs[0]` is used to retrieve it. The image is then displayed using the `show()` function.

```python
imgs = spida.txt2img("cow")
spida.show(imgs[0])
```

For ControlNet functionality jump to: [Example](#using-controlnet-in-txt2img)

### Starting the Local API

Before using Spida, it is recommended to start the local API provided by the Automatic1111 WebUI. However, it is not required. This can be done using the `start()` function:

```python
spida.start()
```

### Selecting the Stable Diffusion Model

To set the Stable Diffusion model to be used, you can use the `model()` function:

```python
spida.model("model_name")
```

The `model_name` parameter should be the name of the desired Stable Diffusion model. `model_name` doesn't have to be an exact match. Spida will automatically search for the closest match by default.

### Generating Images from Text Prompts

Spida allows you to generate AI-generated images from text prompts using the Stable Diffusion model. The `txt2img()` function is used for this purpose:

```python
images = spida.txt2img("text_prompt")
```

The `text_prompt` parameter should be the desired text prompt for generating the images. You can also specify additional parameters such as the number of steps, image shape, batch size, and more. Spida provides options to control various aspects of the generation process.

### Using the ControlNet Extension

Spida supports the ControlNet extension, which allows for conditioning the generation process using ControlNet modules. You can use the `annotate()` function to annotate a batch of images using a specified ControlNet module:

```python
annotated_images = spida.annotate(images, annotator="controlnet_module")
```

The `controlnet_module` parameter should be the name of the ControlNet module to be used for annotation.

### Retrieving Info

Spida has multiple functions for retrieving information, they are listed here:

```python
# get functions
spida.get_models()
spida.get_samplers()
spida.get_annotators()
spida.get_cnet_models()
spida.get_styles()

# search functions
spida.search_models("model_name")
spida.search_samplers("sampler_name")
spida.search_annotators("annotator_name")
spida.search_cnet_models("cnet_model_name")
spida.search_styles("style_name")
```

### Utility Functions

Spida also provides the following utility functions:

```python
spida.open()
spida.show()
spida.save()
spida.grid_img()
```

## Examples

### Generating multiple images from a text prompt

```python
import spida

# Start the local API
spida.start()

# Set the Stable Diffusion model
spida.model("model_name")

# Generate multiple images from a text prompt
images = spida.txt2img("text_prompt", batch_count=4)

# Create an image grid from images and display it
img_grid = spida.grid_img(images)
spida.show(img_grid)
```

### Annotating images using ControlNet

```python
import spida

# Start the local API
spida.start()

# Set the Stable Diffusion model
spida.model("model_name")

# Generate images from a text prompt
images = spida.txt2img("text_prompt")

# Annotate the images using a ControlNet module
annotated_images = spida.annotate(images, annotator="controlnet_module")

# Create an image grid from images and display it
img_grid = spida.grid_img(annotated_images)
spida.show(img_grid)
```

### Using ControlNet in txt2img

```python
import spida
import numpy as np

# Start the local API
spida.start()

# Set the Stable Diffusion model
spida.model("model_name")

# Create an image to annotate
imgs = spida.txt2img("chair")

# Generate the settings for a ControlNet unit
cset = spida.cnet_settings(imgs[0])

# Use the settings for conditioning the generation process
results = spida.txt2img("chair", cnet_settings=cset)

# Create and display a grid showing each step of the process
grid = spida.grid_img(np.array([imgs[0], results[1], results[0]]), (1, None))
spida.show(grid)
```

## License

This project is licensed under the [MIT License](https://github.com/h2see/spida/blob/master/LICENSE).