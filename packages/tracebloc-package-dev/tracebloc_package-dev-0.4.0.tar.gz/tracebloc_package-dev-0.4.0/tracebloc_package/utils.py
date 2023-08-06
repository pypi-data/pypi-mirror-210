import tensorflow_datasets as tfds
import tensorflow as tf
import torch
import torchvision
import torchvision.transforms as transforms
import numpy as np
from tensorflow_datasets.testing import mock_data
from importlib.machinery import SourceFileLoader
import base64
import ast


TENSORFLOW_FRAMEWORK = "tensorflow"
PYTORCH_FRAMEWORK = "pytorch"
CONSTANT = "constant"
STANDARD = "standard"
ADAPTIVE = "adaptive"
CUSTOM = "custom"
TYPE = "type"
FUNCTION = "function"
VALUE = "value"

def check_MyModel(filename, path):
    try:
        # check if file contains the MyModel function
        model = SourceFileLoader(filename, f"{path}").load_module()
        model.MyModel(input_shape=(500, 500, 3), classes=10)
        return True, model

    except AttributeError:
        return (
            False,
            "Model file not provided as per docs: No function with name MyModel",
        )
    except TypeError:
        return (
            False,
            "Model file not provided as per docs: MyModel function receives no arguments",
        )
    except ValueError:
        return False, "Layers shape is not compatible with model input shape"


def is_model_supported(model_obj):
    tensorflow_supported_apis = (tf.keras.models.Sequential, tf.keras.Model)
    supported = isinstance(model_obj, tensorflow_supported_apis)
    if supported:
        # check if it of subclassing
        try:
            # Note that the `input_shape` property is only available for Functional and Sequential models.
            input_shape = model_obj.input_shape
            return True
        except AttributeError:
            return False


# function to check if layers used in tensorflow are supported
def layer_instance_check(model):
    model_layers = model.layers
    for layer in model_layers:
        if not isinstance(layer, tf.keras.layers.Layer):
            return False, []
    return True, model_layers


def mock_dataset(classes):
    num_examples = 5

    def as_dataset(self, *args, **kwargs):
        return tf.data.Dataset.from_generator(
            lambda: (
                {
                    "image": np.ones(shape=(500, 500, 3), dtype=np.uint8),
                    "label": classes,
                }
                for i in range(num_examples)
            ),
            output_types=self.info.features.dtype,
            output_shapes=self.info.features.shape,
        )

    with mock_data(as_dataset_fn=as_dataset):
        (ds_train, ds_test), ds_info = tfds.load(
            "beans",
            split=["train", "test"],
            shuffle_files=True,
            as_supervised=True,
            with_info=True,
        )

    ds_train = ds_train.map(normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    ds_train = ds_train.batch(128)
    ds_train = ds_train.prefetch(tf.data.AUTOTUNE)

    return ds_train


def normalize_img(image, label):
    """Normalizes images: `uint8` -> `float32`."""
    return tf.cast(image, tf.float32) / 255.0, label


def small_training_loop(model, training_dataset):
    # try:
    print("in training loop", training_dataset)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
    )
    model.summary()
    history = model.fit(training_dataset, epochs=1, verbose=1)
    #     return True
    # except Exception as e:
    #     print("exception in training small loop: e")
    #     return False


def is_valid_method(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return False
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        return False
    return True


def get_base64_encoded_code(code):
    if not is_valid_method(code):
        raise ValueError("Input is not a valid Python method")
    code_bytes = code.encode("utf-8")
    return base64.b64encode(code_bytes).decode("utf-8")


def getImagesCount(images_count):
    count = 0
    for key in images_count.keys():
        count += images_count[key]
    return count


def mock_dataset(classes):
    num_examples = 3

    def as_dataset(self, *args, **kwargs):
        return tf.data.Dataset.from_generator(  # pragma: no cover
            lambda: (
                {
                    "image": np.ones(shape=(256, 256, 3), dtype=np.uint8),
                    "label": classes,
                }
                for i in range(num_examples)
            ),
            output_types=self.info.features.tf_dtype,
            output_shapes=self.info.features.shape,
        )

    with mock_data(as_dataset_fn=as_dataset):
        (ds_train, ds_test), ds_info = tfds.load(
            "deep_weeds",
            split=["train", "test"],
            shuffle_files=True,
            as_supervised=True,
            with_info=True,
        )

    ds_train = ds_train.map(normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    ds_train = ds_train.batch(8)
    ds_train = ds_train.prefetch(tf.data.AUTOTUNE)
    return ds_train


def normalize_img(image, label):
    """Normalizes images: `uint8` -> `float32`."""
    return tf.cast(image, tf.float32) / 255.0, label  # pragma: no cover


def test_code():
    main_method = "MyModel"
    input_shape = "input_shape"
    output_classes = "output_classes"

    def MyModel(input_shape=(224, 224, 3), output_classes=3):
        base_mobilenet_model = MobileNet(
            input_shape=input_shape, include_top=False, weights=None
        )
        multi_disease_model = Sequential()
        multi_disease_model.add(base_mobilenet_model)
        multi_disease_model.add(GlobalAveragePooling2D())
        multi_disease_model.add(Dropout(0.5))
        multi_disease_model.add(Dense(output_classes, activation="sigmoid"))
        return multi_disease_model
