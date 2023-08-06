# This file is MACHINE GENERATED! Do not edit.
# Generated by: tensorflow/python/tools/api/generator/create_python_api.py script.
"""Image ops.

The `tf.image` module contains various functions for image
processing and decoding-encoding Ops.

Many of the encoding/decoding functions are also available in the
core `tf.io` module.

## Image processing

### Resizing

The resizing Ops accept input images as tensors of several types. They always
output resized images as float32 tensors.

The convenience function `tf.image.resize` supports both 4-D
and 3-D tensors as input and output.  4-D tensors are for batches of images,
3-D tensors for individual images.

Resized images will be distorted if their original aspect ratio is not the
same as size. To avoid distortions see tf.image.resize_with_pad.

*   `tf.image.resize`
*   `tf.image.resize_with_pad`
*   `tf.image.resize_with_crop_or_pad`

The Class `tf.image.ResizeMethod` provides various resize methods like
`bilinear`, `nearest_neighbor`.

### Converting Between Colorspaces

Image ops work either on individual images or on batches of images, depending on
the shape of their input Tensor.

If 3-D, the shape is `[height, width, channels]`, and the Tensor represents one
image. If 4-D, the shape is `[batch_size, height, width, channels]`, and the
Tensor represents `batch_size` images.

Currently, `channels` can usefully be 1, 2, 3, or 4. Single-channel images are
grayscale, images with 3 channels are encoded as either RGB or HSV. Images
with 2 or 4 channels include an alpha channel, which has to be stripped from the
image before passing the image to most image processing functions (and can be
re-attached later).

Internally, images are either stored in as one `float32` per channel per pixel
(implicitly, values are assumed to lie in `[0,1)`) or one `uint8` per channel
per pixel (values are assumed to lie in `[0,255]`).

TensorFlow can convert between images in RGB or HSV or YIQ.

*   `tf.image.rgb_to_grayscale`, `tf.image.grayscale_to_rgb`
*   `tf.image.rgb_to_hsv`, `tf.image.hsv_to_rgb`
*   `tf.image.rgb_to_yiq`, `tf.image.yiq_to_rgb`
*   `tf.image.rgb_to_yuv`, `tf.image.yuv_to_rgb`
*   `tf.image.image_gradients`
*   `tf.image.convert_image_dtype`

### Image Adjustments

TensorFlow provides functions to adjust images in various ways: brightness,
contrast, hue, and saturation.  Each adjustment can be done with predefined
parameters or with random parameters picked from predefined intervals. Random
adjustments are often useful to expand a training set and reduce overfitting.

If several adjustments are chained it is advisable to minimize the number of
redundant conversions by first converting the images to the most natural data
type and representation.

*   `tf.image.adjust_brightness`
*   `tf.image.adjust_contrast`
*   `tf.image.adjust_gamma`
*   `tf.image.adjust_hue`
*   `tf.image.adjust_jpeg_quality`
*   `tf.image.adjust_saturation`
*   `tf.image.random_brightness`
*   `tf.image.random_contrast`
*   `tf.image.random_hue`
*   `tf.image.random_saturation`
*   `tf.image.per_image_standardization`

### Working with Bounding Boxes

*   `tf.image.draw_bounding_boxes`
*   `tf.image.combined_non_max_suppression`
*   `tf.image.generate_bounding_box_proposals`
*   `tf.image.non_max_suppression`
*   `tf.image.non_max_suppression_overlaps`
*   `tf.image.non_max_suppression_padded`
*   `tf.image.non_max_suppression_with_scores`
*   `tf.image.pad_to_bounding_box`
*   `tf.image.sample_distorted_bounding_box`

### Cropping

*   `tf.image.central_crop`
*   `tf.image.crop_and_resize`
*   `tf.image.crop_to_bounding_box`
*   `tf.io.decode_and_crop_jpeg`
*   `tf.image.extract_glimpse`
*   `tf.image.random_crop`
*   `tf.image.resize_with_crop_or_pad`

### Flipping, Rotating and Transposing

*   `tf.image.flip_left_right`
*   `tf.image.flip_up_down`
*   `tf.image.random_flip_left_right`
*   `tf.image.random_flip_up_down`
*   `tf.image.rot90`
*   `tf.image.transpose`

## Image decoding and encoding

TensorFlow provides Ops to decode and encode JPEG and PNG formats.  Encoded
images are represented by scalar string Tensors, decoded images by 3-D uint8
tensors of shape `[height, width, channels]`. (PNG also supports uint16.)

Note: `decode_gif` returns a 4-D array `[num_frames, height, width, 3]`

The encode and decode Ops apply to one image at a time.  Their input and output
are all of variable size.  If you need fixed size images, pass the output of
the decode Ops to one of the cropping and resizing Ops.

*   `tf.io.decode_bmp`
*   `tf.io.decode_gif`
*   `tf.io.decode_image`
*   `tf.io.decode_jpeg`
*   `tf.io.decode_and_crop_jpeg`
*   `tf.io.decode_png`
*   `tf.io.encode_jpeg`
*   `tf.io.encode_png`


"""

import sys as _sys

from tensorflow.python.ops.array_ops import extract_image_patches
from tensorflow.python.ops.array_ops import extract_image_patches_v2 as extract_patches
from tensorflow.python.ops.gen_image_ops import decode_and_crop_jpeg
from tensorflow.python.ops.gen_image_ops import decode_bmp
from tensorflow.python.ops.gen_image_ops import decode_gif
from tensorflow.python.ops.gen_image_ops import decode_jpeg
from tensorflow.python.ops.gen_image_ops import decode_png
from tensorflow.python.ops.gen_image_ops import encode_jpeg
from tensorflow.python.ops.gen_image_ops import extract_jpeg_shape
from tensorflow.python.ops.gen_image_ops import hsv_to_rgb
from tensorflow.python.ops.gen_image_ops import resize_area
from tensorflow.python.ops.gen_image_ops import rgb_to_hsv
from tensorflow.python.ops.image_ops_impl import ResizeMethodV1 as ResizeMethod
from tensorflow.python.ops.image_ops_impl import adjust_brightness
from tensorflow.python.ops.image_ops_impl import adjust_contrast
from tensorflow.python.ops.image_ops_impl import adjust_gamma
from tensorflow.python.ops.image_ops_impl import adjust_hue
from tensorflow.python.ops.image_ops_impl import adjust_jpeg_quality
from tensorflow.python.ops.image_ops_impl import adjust_saturation
from tensorflow.python.ops.image_ops_impl import central_crop
from tensorflow.python.ops.image_ops_impl import combined_non_max_suppression
from tensorflow.python.ops.image_ops_impl import convert_image_dtype
from tensorflow.python.ops.image_ops_impl import crop_and_resize_v1 as crop_and_resize
from tensorflow.python.ops.image_ops_impl import crop_to_bounding_box
from tensorflow.python.ops.image_ops_impl import decode_image
from tensorflow.python.ops.image_ops_impl import draw_bounding_boxes
from tensorflow.python.ops.image_ops_impl import encode_png
from tensorflow.python.ops.image_ops_impl import extract_glimpse
from tensorflow.python.ops.image_ops_impl import flip_left_right
from tensorflow.python.ops.image_ops_impl import flip_up_down
from tensorflow.python.ops.image_ops_impl import generate_bounding_box_proposals
from tensorflow.python.ops.image_ops_impl import grayscale_to_rgb
from tensorflow.python.ops.image_ops_impl import image_gradients
from tensorflow.python.ops.image_ops_impl import is_jpeg
from tensorflow.python.ops.image_ops_impl import non_max_suppression
from tensorflow.python.ops.image_ops_impl import non_max_suppression_padded
from tensorflow.python.ops.image_ops_impl import non_max_suppression_with_overlaps as non_max_suppression_overlaps
from tensorflow.python.ops.image_ops_impl import non_max_suppression_with_scores
from tensorflow.python.ops.image_ops_impl import pad_to_bounding_box
from tensorflow.python.ops.image_ops_impl import per_image_standardization
from tensorflow.python.ops.image_ops_impl import psnr
from tensorflow.python.ops.image_ops_impl import random_brightness
from tensorflow.python.ops.image_ops_impl import random_contrast
from tensorflow.python.ops.image_ops_impl import random_flip_left_right
from tensorflow.python.ops.image_ops_impl import random_flip_up_down
from tensorflow.python.ops.image_ops_impl import random_hue
from tensorflow.python.ops.image_ops_impl import random_jpeg_quality
from tensorflow.python.ops.image_ops_impl import random_saturation
from tensorflow.python.ops.image_ops_impl import resize_bicubic
from tensorflow.python.ops.image_ops_impl import resize_bilinear
from tensorflow.python.ops.image_ops_impl import resize_image_with_crop_or_pad
from tensorflow.python.ops.image_ops_impl import resize_image_with_crop_or_pad as resize_with_crop_or_pad
from tensorflow.python.ops.image_ops_impl import resize_image_with_pad_v1 as resize_image_with_pad
from tensorflow.python.ops.image_ops_impl import resize_images
from tensorflow.python.ops.image_ops_impl import resize_images as resize
from tensorflow.python.ops.image_ops_impl import resize_nearest_neighbor
from tensorflow.python.ops.image_ops_impl import rgb_to_grayscale
from tensorflow.python.ops.image_ops_impl import rgb_to_yiq
from tensorflow.python.ops.image_ops_impl import rgb_to_yuv
from tensorflow.python.ops.image_ops_impl import rot90
from tensorflow.python.ops.image_ops_impl import sample_distorted_bounding_box
from tensorflow.python.ops.image_ops_impl import sobel_edges
from tensorflow.python.ops.image_ops_impl import ssim
from tensorflow.python.ops.image_ops_impl import ssim_multiscale
from tensorflow.python.ops.image_ops_impl import total_variation
from tensorflow.python.ops.image_ops_impl import transpose
from tensorflow.python.ops.image_ops_impl import transpose as transpose_image
from tensorflow.python.ops.image_ops_impl import yiq_to_rgb
from tensorflow.python.ops.image_ops_impl import yuv_to_rgb
from tensorflow.python.ops.random_crop_ops import random_crop