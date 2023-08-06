import enum
import re
from typing import Optional, Union

from pydantic import Field, constr, root_validator
from typing_extensions import Literal

from servicefoundry.auto_gen import models

# TODO (chiragjn): Setup a base class for auto_gen.models to make `extra = "forbid"` default


class CUDAVersion(str, enum.Enum):
    CUDA_9_2_CUDNN7 = "9.2-cudnn7"
    CUDA_10_0_CUDNN7 = "10.0-cudnn7"
    CUDA_10_1_CUDNN7 = "10.1-cudnn7"
    CUDA_10_1_CUDNN8 = "10.1-cudnn8"
    CUDA_10_2_CUDNN7 = "10.2-cudnn7"
    CUDA_10_2_CUDNN8 = "10.2-cudnn8"
    CUDA_11_0_CUDNN8 = "11.0-cudnn8"
    CUDA_11_1_CUDNN8 = "11.1-cudnn8"
    CUDA_11_2_CUDNN8 = "11.2-cudnn8"
    CUDA_11_3_CUDNN8 = "11.3-cudnn8"
    CUDA_11_4_CUDNN8 = "11.4-cudnn8"
    CUDA_11_5_CUDNN8 = "11.5-cudnn8"
    CUDA_11_6_CUDNN8 = "11.6-cudnn8"
    CUDA_11_7_CUDNN8 = "11.7-cudnn8"
    CUDA_11_8_CUDNN8 = "11.8-cudnn8"


class GPUType(str, enum.Enum):
    K80 = "K80"
    V100 = "V100"
    T4 = "T4"
    A10G = "A10G"
    A100_40GB = "A100_40GB"
    A100_80GB = "A100_80GB"


class DockerFileBuild(models.DockerFileBuild):
    class Config:
        extra = "forbid"

    type: constr(regex=r"dockerfile") = "dockerfile"


class PythonBuild(models.PythonBuild):
    class Config:
        extra = "forbid"

    type: constr(regex=r"tfy-python-buildpack") = "tfy-python-buildpack"

    @root_validator
    def validate_python_version_when_cuda_version(cls, values):
        if values.get("cuda_version"):
            python_version = values.get("python_version")
            if python_version and not re.match(r"^3\.\d+$", python_version):
                raise ValueError(
                    f'`python_version` must be 3.x (e.g. "3.9") when `cuda_version` field is '
                    f"provided but got {python_version!r}. If you are adding a "
                    f'patch version, please remove it (e.g. "3.9.2" should be "3.9")'
                )
        return values


class RemoteSource(models.RemoteSource):
    class Config:
        extra = "forbid"

    type: constr(regex=r"remote") = "remote"


class LocalSource(models.LocalSource):
    class Config:
        extra = "forbid"

    type: constr(regex=r"local") = "local"


class Build(models.Build):
    class Config:
        extra = "forbid"

    type: constr(regex=r"build") = "build"
    build_source: Union[
        models.RemoteSource, models.GitSource, models.LocalSource
    ] = Field(default_factory=LocalSource)


class Manual(models.Manual):
    class Config:
        extra = "forbid"

    type: constr(regex=r"manual") = "manual"


class Schedule(models.Schedule):
    class Config:
        extra = "forbid"

    type: constr(regex=r"scheduled") = "scheduled"


class GitSource(models.GitSource):
    class Config:
        extra = "forbid"

    type: constr(regex=r"git") = "git"


class HttpProbe(models.HttpProbe):
    class Config:
        extra = "forbid"

    type: constr(regex=r"http") = "http"


class BasicAuthCreds(models.BasicAuthCreds):
    class Config:
        extra = "forbid"

    type: constr(regex=r"basic_auth") = "basic_auth"


class TruefoundryModelRegistry(models.TruefoundryModelRegistry):
    class Config:
        extra = "forbid"

    type: constr(regex=r"tfy-model-registry") = "tfy-model-registry"


class HuggingfaceModelHub(models.HuggingfaceModelHub):
    class Config:
        extra = "forbid"

    type: constr(regex=r"hf-model-hub") = "hf-model-hub"


class HealthProbe(models.HealthProbe):
    class Config:
        extra = "forbid"


class Image(models.Image):
    class Config:
        extra = "forbid"

    type: constr(regex=r"image") = "image"


class Port(models.Port):
    class Config:
        extra = "forbid"


class Resources(models.Resources):
    class Config:
        extra = "forbid"


class Param(models.Param):
    class Config:
        extra = "forbid"


class CPUUtilizationMetric(models.CPUUtilizationMetric):
    class Config:
        extra = "forbid"

    type: Literal["cpu_utilization"] = "cpu_utilization"


class RPSMetric(models.RPSMetric):
    class Config:
        extra = "forbid"

    type: Literal["rps"] = "rps"


class Autoscaling(models.Autoscaling):
    class Config:
        extra = "forbid"


class BlueGreen(models.BlueGreen):
    class Config:
        extra = "forbid"

    type: Literal["blue_green"] = "blue_green"


class Canary(models.Canary):
    class Config:
        extra = "forbid"

    type: Literal["canary"] = "canary"


class Rolling(models.Rolling):
    class Config:
        extra = "forbid"

    type: Literal["rolling_update"] = "rolling_update"


class SecretMount(models.SecretMount):
    class Config:
        extra = "forbid"

    type: constr(regex=r"^secret$") = "secret"


class StringDataMount(models.StringDataMount):
    class Config:
        extra = "forbid"

    type: constr(regex=r"^string$") = "string"


class VolumeMount(models.VolumeMount):
    class Config:
        extra = "forbid"

    type: constr(regex=r"^volume$") = "volume"


class NodeSelector(models.NodeSelector):
    class Config:
        extra = "forbid"

    type: Literal["node_selector"] = "node_selector"
    gpu_type: Optional[Union[GPUType, str]] = None


class NodepoolSelector(models.NodepoolSelector):
    class Config:
        extra = "forbid"

    type: Literal["nodepool_selector"] = "nodepool_selector"
