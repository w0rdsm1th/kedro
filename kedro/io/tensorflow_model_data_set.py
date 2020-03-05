# Copyright 2020 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
#     or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""``TensorflowModelDataset`` is a data set implementation which can save and load TensorFlow models.
"""
import copy
from pathlib import Path, PurePath
from typing import Any, Dict

import fsspec
import tensorflow as tf

from kedro.io import AbstractDataSet, AbstractVersionedDataSet, Version
from kedro.io.core import get_protocol_and_path


class TensorFlowModelDataset(AbstractDataSet):
    """``TensorflowModelDataset`` loads and saves TensorFlow models.

    The underlying functionality is supported by TensorFlow 2.X load_model and save_model methods, so it supports all
    allowed pandas options for loading and saving Excel files.

        Example:
    ::

        >>> from kedro.io import TensorFlowModelDataset
        >>> import tensorflow as tf
        >>> import numpy as np
        >>> data_set = TensorFlowModelDataset("saved_model_path")
        >>> model = tf.keras.Model()
        >>> predictions = model.predict([...])
        >>> data_set.save(model)
        >>> loaded_model = data_set.load()
        >>> new_predictions = loaded_model.predict([...])
        >>> np.testing.assert_allclose(predictions, new_predictions, rtol=1e-6, atol=1e-6)

    """

    DEFAULT_LOAD_ARGS = dict(custom_objects=None, compile=True)  # type: Dict[str, Any]

    DEFAULT_SAVE_ARGS = dict(
        overwrite=True,
        include_optimizer=True,
        save_format="tf",
        signatures=None,
        options=None,
    )  # type: Dict[str, Any]

    def __init__(
        self,
        filepath: str,
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
    ) -> None:
        """
        Args:
            filepath: Filepath to a TensorFlow model directory prefixed with a protocol like `s3://`.
                If prefix is not provided `file` protocol (local filesystem) will be used.
                The prefix should be any protocol supported by ``fsspec``.
                Note: `http(s)` doesn't support versioning.
            load_args: TensorFlow options for loading models.
                custom_objects: Optional dictionary mapping names (strings) to custom classes or functions to be
                considered during deserialization.
                compile: Boolean, whether to compile the model after loading.
                Here you can find all available arguments:
                https://www.tensorflow.org/api_docs/python/tf/keras/models/load_model
                All defaults are preserved.
            save_args: TensorFlow options for saving models.
                Here you can find all available arguments:
                https://www.tensorflow.org/api_docs/python/tf/keras/models/save_model
                All defaults are preserved, except for "index", which is set to False.
                In TF this defaults to 'tf' in TF 2.X, and 'h5' in TF 1.X.
        """
        super().__init__()

        self._filepath = filepath
        self._data = None

        # Handle default load and save arguments
        self._load_args = copy.deepcopy(self.DEFAULT_LOAD_ARGS)
        if load_args is not None:
            self._load_args.update(load_args)
        self._save_args = copy.deepcopy(self.DEFAULT_SAVE_ARGS)
        if save_args is not None:
            self._save_args.update(save_args)

    def _load(self) -> None:
        return tf.keras.models.load_model(self._filepath, **self._load_args)

    def _save(self, data: tf.keras.Model) -> None:
        tf.keras.models.save_model(data, self._filepath, **self._save_args)

    def _exists(self) -> bool:
        return Path(self._filepath).is_dir()

    def _describe(self) -> Dict[str, Any]:
        # todo(aleks) - could also expose model.summary()
        return dict(
            filepath=self._filepath,
            load_args=self._load_args,
            save_args=self._save_args,
        )


class TensorFlowModelVersionedDataset(AbstractVersionedDataSet):
    """``TensorflowModelVersionedDataset`` loads and saves TensorFlow models.

    The underlying functionality is supported by TensorFlow 2.X load_model and save_model methods, so it supports all
    allowed pandas options for loading and saving Excel files.

        Example:
    ::

        >>> from kedro.io import TensorFlowModelDataset
        >>> import tensorflow as tf
        >>> import numpy as np
        >>> data_set = TensorFlowModelVersionedDataset("saved_model_path")
        >>> model = tf.keras.Model()
        >>> predictions = model.predict([...])
        >>> data_set.save(model)
        >>> loaded_model = data_set.load()
        >>> new_predictions = loaded_model.predict([...])
        >>> np.testing.assert_allclose(predictions, new_predictions, rtol=1e-6, atol=1e-6)

    """

    DEFAULT_LOAD_ARGS = dict(custom_objects=None, compile=True,)  # type: Dict[str, Any]

    DEFAULT_SAVE_ARGS = dict(
        overwrite=True,
        include_optimizer=True,
        save_format="tf",
        signatures=None,
        options=None,
    )  # type: Dict[str, Any]

    def __init__(
        self,
        filepath: str,
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
        version: Version = None,
        credentials: Dict[str, Any] = None,
        fs_args: Dict[str, Any] = None,
    ) -> None:
        """
        Args:
            filepath: Filepath to a TensorFlow model directory prefixed with a protocol like `s3://`.
                If prefix is not provided `file` protocol (local filesystem) will be used.
                The prefix should be any protocol supported by ``fsspec``.
                Note: `http(s)` doesn't support versioning.
            load_args: TensorFlow options for loading models.
                custom_objects: Optional dictionary mapping names (strings) to custom classes or functions to be
                considered during deserialization.
                compile: Boolean, whether to compile the model after loading.
                Here you can find all available arguments:
                https://www.tensorflow.org/api_docs/python/tf/keras/models/load_model
                All defaults are preserved.
            save_args: TensorFlow options for saving models.
                Here you can find all available arguments:
                https://www.tensorflow.org/api_docs/python/tf/keras/models/save_model
                All defaults are preserved, except for "index", which is set to False.
                In TF this defaults to 'tf' in TF 2.X, and 'h5' in TF 1.X.
            version: If specified, should be an instance of
                ``kedro.io.core.Version``. If its ``load`` attribute is
                None, the latest version will be loaded. If its ``save``
                attribute is None, save version will be autogenerated.
            credentials: Credentials required to get access to the underlying filesystem.
                E.g. for ``GCSFileSystem`` it should look like `{'token': None}`.
            fs_args: Extra arguments to pass into underlying filesystem class.
                E.g. for ``GCSFileSystem`` class: `{project: 'my-project', ...}`
        """
        _fs_args = copy.deepcopy(fs_args) or {}
        _credentials = copy.deepcopy(credentials) or {}
        protocol, path = get_protocol_and_path(filepath, version)

        self._protocol = protocol
        self._fs = fsspec.filesystem(self._protocol, **_credentials, **_fs_args)
        super().__init__(
            PurePath(filepath), version, exists_function=lambda x: Path(x).is_dir(),
        )

        self._data = None

        # Handle default load and save arguments
        self._load_args = copy.deepcopy(self.DEFAULT_LOAD_ARGS)
        if load_args is not None:
            self._load_args.update(load_args)
        self._save_args = copy.deepcopy(self.DEFAULT_SAVE_ARGS)
        if save_args is not None:
            self._save_args.update(save_args)

    def _load(self) -> None:
        load_path = Path(self._get_load_path())
        return tf.keras.models.load_model(str(load_path), **self._load_args)

    def _save(self, data: tf.keras.Model) -> None:
        save_path = Path(self._get_save_path())
        tf.keras.models.save_model(data, str(save_path), **self._save_args)

    def _exists(self) -> bool:
        path = Path(self._get_load_path())
        return path.is_dir()

    def _describe(self) -> Dict[str, Any]:
        # todo(aleks) - could also expose model.summary()
        return dict(
            filepath=str(self._filepath),
            load_args=self._load_args,
            save_args=self._save_args,
            version=self._version,
        )
