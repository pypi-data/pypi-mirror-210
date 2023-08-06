import logging
from typing import List

import numpy as np
import tensorflow as tf
import xarray as xr

logger = logging.getLogger(__name__)


def chunk_result(img, input_shape, pad_mode="reflect"):
    """
    A function to create splits out of a particular size from a given image.
    images are split up row wise, i.e - row1 split up, row2 split up and so on

    NOTE - padding is added in case the image can't be split into equal parts
           padding is added on the right and the bottom of the image, padding type
           is reflected by default

    The function assumes that the input will always be of 4 dimensions which pertain to
    [channels, time-step, height, width]. Expand any missing dimensions as 1 before passing
    the data

    Args:
        img : image to be split up [C x T x H x W]
        input_shape : size of the split [size_h, size_w]
    Returns:
        splits : a list containing the split up images
    """
    img = img.dataset.to_array()
    h_idx, w_idx = 2, 3
    border_len_y = (0 - img.shape[h_idx]) % input_shape[0]
    border_len_x = (0 - img.shape[w_idx]) % input_shape[1]

    img_attrs = img.attrs
    # Padding removes metadata for some reason,
    # also note that in the docs it is stated that this is an experimental function
    # https://docs.xarray.dev/en/stable/generated/xarray.DataArray.pad.html
    img = img.pad(pad_width={"y": (0, border_len_y), "x": (0, border_len_x)}, mode=pad_mode)
    img.attrs = img_attrs

    splits = []

    for i in range(0, img.shape[h_idx], input_shape[0]):
        for j in range(0, img.shape[w_idx], input_shape[1]):
            splits.append(img[:, :, i : i + input_shape[0], j : j + input_shape[1]])

    return split_da_to_split_ds(splits)


def split_da_to_split_ds(splits):
    splits_ds = []

    for split in splits:
        data_array_dict = {}

        for var_idx, var_name in enumerate(split.coords["variable"].values):
            var_arr = split[var_idx, :, :, :]
            var_xr = xr.DataArray(
                var_arr, dims=["time", "y", "x"], coords={"time": split.time, "y": split.y, "x": split.x}
            )

            data_array_dict[var_name] = var_xr

        split_dataset = list(data_array_dict.values())[0].to_dataset(name=list(data_array_dict.keys())[0])

        for var_name in list(data_array_dict.keys())[1:]:
            split_dataset[var_name] = data_array_dict[var_name]

        split_dataset.attrs = split.attrs
        splits_ds.append(split_dataset)

    return splits_ds


def tf_bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy()  # BytesList won't unpack a string from an EagerTensor.

    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def tf_float_feature(value):
    """Returns a float_list from a float / double."""
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))


def tf_int64_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def create_tf_record(chunks: List[xr.Dataset], save_path: str, save_coords: bool = False, save_attrs: bool = False):
    """
    A function to save "chunked" results into the "tfrecord" format

    The function assumes that the input will always be of 4 dimensions which pertain to
    [channels, time-step, height, width]. Expand any missing dimensions as 1 before passing
    the data

    Args:
        chunks (list of xarray datasets) : List of xarray datasets with equal dimensions
        save_path (str) : Path to the directory to save the tfrecord file
        save_coords (bool) : Boolean to save coordinates from the datasets
        save_attrs (bool) : Boolean to save metadata and attributes from the datasets

    Returns:
        features_dict (dict) : Dictionary mapping feature name to the tf.io.FixedLenFeature as they are stored
        out_types_dict (dict) : Dictionary mapping feature name to the data type to which it needs to be decoded
        shapes_dict (dict) : Dictionary mapping feature name to the the shape it needs to be decoded to, empty tuple for scalar data
    """

    features_dict = {}
    out_types_dict = {}
    shapes_dict = {}

    writer = tf.io.TFRecordWriter(save_path)
    # img_id_counter = 0

    for chunk in chunks:
        chunk_tf_dict = {}

        # serialize the data tensors
        for data_var_name in list(chunk.data_vars.keys()):
            data_arr = chunk[data_var_name].values.astype("float64")
            chunk_tf_dict[data_var_name] = tf_bytes_feature(tf.io.serialize_tensor(data_arr))
            features_dict[data_var_name] = tf.io.FixedLenFeature([], tf.string)
            out_types_dict[data_var_name] = tf.float64
            shapes_dict[data_var_name] = data_arr.shape

        if save_coords:
            # serialize the coordinate tensors
            for coord_name in list(chunk.coords.keys()):
                coord_arr = chunk[coord_name].values

                if np.issubdtype(coord_arr.dtype, np.datetime64):
                    coord_arr = np.array(list(map(str, coord_arr)))
                    chunk_tf_dict["coord_" + coord_name] = tf_bytes_feature(tf.io.serialize_tensor(coord_arr))
                    features_dict["coord_" + coord_name] = tf.io.FixedLenFeature([], tf.string)
                    out_types_dict["coord_" + coord_name] = tf.string
                    shapes_dict["coord_" + coord_name] = coord_arr.shape

                else:
                    coord_arr = coord_arr.astype("float64")
                    chunk_tf_dict["coord_" + coord_name] = tf_bytes_feature(tf.io.serialize_tensor(coord_arr))
                    features_dict["coord_" + coord_name] = tf.io.FixedLenFeature([], tf.string)
                    out_types_dict["coord_" + coord_name] = tf.float64
                    shapes_dict["coord_" + coord_name] = coord_arr.shape

        if save_attrs:
            # serialize the attribute tensors
            for attr_name in list(chunk.attrs.keys()):
                attr = chunk.attrs[attr_name]

                if isinstance(attr, str):
                    chunk_tf_dict["attr_" + attr_name] = tf_bytes_feature(bytes(attr, "utf-8"))
                    features_dict["attr_" + attr_name] = tf.io.FixedLenFeature([], tf.string)
                    out_types_dict["attr_" + attr_name] = tf.string
                    shapes_dict["attr_" + attr_name] = ()

                elif isinstance(attr, np.ndarray):
                    attr_arr = attr.astype("float64")
                    chunk_tf_dict["attr_" + attr_name] = tf_bytes_feature(tf.io.serialize_tensor(attr_arr))
                    features_dict["attr_" + attr_name] = tf.io.FixedLenFeature([], tf.string)
                    out_types_dict["attr_" + attr_name] = tf.float64
                    shapes_dict["attr_" + attr_name] = attr_arr.shape

                else:
                    logger.info(
                        f"{type(attr_arr)} is not supported for saving currently, skipping saving attribute {attr_name}"
                    )

        message_feature = tf.train.Example(features=tf.train.Features(feature=chunk_tf_dict))
        writer.write(message_feature.SerializeToString())

    writer.close()

    return features_dict, out_types_dict, shapes_dict


def load_img(example_proto, features_dict, out_types_dict, shapes_dict):
    """
    Function to map data from a saved tfrecord to the accompanying saved dictionaries. This function is meant to be used in conjunction with the tf.data API when loading
    in the dataset as a tfrecord.

    Args:
        example_proto (str) : Single example (data sample) from the tfrecord
        features_dict (dict) : Dictionary mapping feature name to the tf.io.FixedLenFeature as they are stored
        out_types_dict (dict) : Dictionary mapping feature name to the data type to which it needs to be decoded
        shapes_dict (dict) : Dictionary mapping feature name to the the shape it needs to be decoded to, empty tuple for scalar data

    Example
    ----------
        >>> dataset = tf.data.TFRecordDataset(save_file_path)
        >>> dataset = dataset.map(
        >>>     lambda example_proto: ml_utils.load_img(
        >>>         example_proto, features_dict=features_dict, out_types_dict=out_types_dict, shapes_dict=shapes_dict
        >>>      )
        >>>  )
    """

    single_example = tf.io.parse_single_example(example_proto, features_dict)
    shapeless_feats = [feat_name for feat_name, feat_shape in shapes_dict.items() if len(feat_shape) == 0]

    example_data = {feat_name: single_example[feat_name] for feat_name in shapeless_feats}

    for feature in features_dict.keys():
        if feature in shapeless_feats:
            continue

        feature_data = tf.io.parse_tensor(single_example[feature], out_type=out_types_dict[feature])

        feature_data = tf.reshape(feature_data, shapes_dict[feature])
        example_data[feature] = feature_data

    return example_data


def combine_bands(example_data, input_bands, output_bands):
    """
    Function to stack the input and output bands from the tfrecord dataset.

    Args:
        example_data (str): Single example (data sample) from the tfrecord
        input_bands (list of strings): List of bands used as model inputs
        output_bands (list of strings): List of bands used as model outputs

    Example
    ----------
        >>> input_bands = ["S2_RED", "S2_GREEN", "S2_BLUE"]
        >>> output_bands = ["S2_SCL"]
        >>> dataset = dataset.map(lambda example_data: ml_utils.combine_bands(example_data, input_bands, output_bands))
    """
    input_data = tf.stack([example_data[ip_band] for ip_band in input_bands], axis=-1)

    if not output_bands:
        return input_data

    output_data = tf.stack([example_data[op_band] for op_band in output_bands], axis=-1)
    return input_data, output_data
