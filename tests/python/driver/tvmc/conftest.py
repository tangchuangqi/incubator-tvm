# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import os
import pytest
import tarfile

import tvm.driver.tvmc.compiler

from tvm.contrib.download import download_testdata

from tvm.driver.tvmc.common import convert_graph_layout

# Support functions


def download_and_untar(model_url, model_sub_path, temp_dir):
    model_tar_name = os.path.basename(model_url)
    model_path = download_testdata(model_url, model_tar_name, module=["tvmc"])

    if model_path.endswith("tgz") or model_path.endswith("gz"):
        tar = tarfile.open(model_path)
        tar.extractall(path=temp_dir)
        tar.close()

    return os.path.join(temp_dir, model_sub_path)


def get_sample_compiled_module(target_dir):
    """Support function that retuns a TFLite compiled module"""
    base_url = "https://storage.googleapis.com/download.tensorflow.org/models"
    model_url = "mobilenet_v1_2018_08_02/mobilenet_v1_1.0_224_quant.tgz"
    model_file = download_and_untar(
        "{}/{}".format(base_url, model_url),
        "mobilenet_v1_1.0_224_quant.tflite",
        temp_dir=target_dir,
    )

    return tvmc.compiler.compile_model(model_file, targets=["llvm"])


# PyTest fixtures


@pytest.fixture(scope="session")
def tflite_mobilenet_v1_1_quant(tmpdir_factory):
    base_url = "https://storage.googleapis.com/download.tensorflow.org/models"
    model_url = "mobilenet_v1_2018_08_02/mobilenet_v1_1.0_224_quant.tgz"
    model_file = download_and_untar(
        "{}/{}".format(base_url, model_url),
        "mobilenet_v1_1.0_224_quant.tflite",
        temp_dir=tmpdir_factory.mktemp("data"),
    )

    return model_file


@pytest.fixture(scope="session")
def pb_mobilenet_v1_1_quant(tmpdir_factory):
    base_url = "https://storage.googleapis.com/download.tensorflow.org/models"
    model_url = "mobilenet_v1_2018_08_02/mobilenet_v1_1.0_224.tgz"
    model_file = download_and_untar(
        "{}/{}".format(base_url, model_url),
        "mobilenet_v1_1.0_224_frozen.pb",
        temp_dir=tmpdir_factory.mktemp("data"),
    )

    return model_file


@pytest.fixture(scope="session")
def keras_resnet50(tmpdir_factory):
    try:
        from tensorflow.keras.applications.resnet50 import ResNet50
    except ImportError:
        # not all environments provide TensorFlow, so skip this fixture
        # if that is that case.
        return ""

    model_file_name = "{}/{}".format(tmpdir_factory.mktemp("data"), "resnet50.h5")
    model = ResNet50(include_top=True, weights="imagenet", input_shape=(224, 224, 3), classes=1000)
    model.save(model_file_name)

    return model_file_name


@pytest.fixture(scope="session")
def onnx_resnet50():
    base_url = "https://github.com/onnx/models/raw/master/vision/classification/resnet/model"
    file_to_download = "resnet50-v2-7.onnx"
    model_file = download_testdata(
        "{}/{}".format(base_url, file_to_download), file_to_download, module=["tvmc"]
    )

    return model_file


@pytest.fixture(scope="session")
def tflite_compiled_module_as_tarfile(tmpdir_factory):
    target_dir = tmpdir_factory.mktemp("data")
    graph, lib, params, _ = get_sample_compiled_module(target_dir)

    module_file = os.path.join(target_dir, "mock.tar")
    tvmc.compiler.save_module(module_file, graph, lib, params)

    return module_file
