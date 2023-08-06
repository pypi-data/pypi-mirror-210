from typing import Any, ClassVar, List

from typing import overload
import flags
import numpy
import pydrake.common.value
import pydrake.systems.framework
import pydrake.systems.sensors

class BaseField:
    __members__: ClassVar[dict] = ...  # read-only
    __entries: ClassVar[dict] = ...
    _pybind11_del_orig: ClassVar[None] = ...
    kNone: ClassVar[BaseField] = ...
    kNormals: ClassVar[BaseField] = ...
    kRGBs: ClassVar[BaseField] = ...
    kXYZs: ClassVar[BaseField] = ...
    def __init__(self, value: int) -> None: ...
    def __and__(self, other: object) -> object: ...
    def __del__(self, *args, **kwargs) -> Any: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __int__(self) -> int: ...
    def __invert__(self) -> object: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __or__(self, other: object) -> object: ...
    def __rand__(self, other: object) -> object: ...
    def __ror__(self, other: object) -> object: ...
    def __rxor__(self, other: object) -> object: ...
    def __setstate__(self, state: int) -> None: ...
    def __xor__(self, other: object) -> object: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class DepthImageToPointCloud(pydrake.systems.framework.LeafSystem):
    def __init__(self, camera_info: pydrake.systems.sensors.CameraInfo, pixel_type: pydrake.systems.sensors.PixelType = ..., scale: float = ..., fields: int = ...) -> None: ...
    def camera_pose_input_port(self) -> pydrake.systems.framework.InputPort: ...
    def color_image_input_port(self) -> pydrake.systems.framework.InputPort: ...
    def depth_image_input_port(self) -> pydrake.systems.framework.InputPort: ...
    def point_cloud_output_port(self) -> pydrake.systems.framework.OutputPort: ...

class Fields:
    _pybind11_del_orig: ClassVar[None] = ...
    __hash__: ClassVar[None] = ...
    def __init__(self, base_fields: int) -> None: ...
    def base_fields(self) -> int: ...
    def has_base_fields(self) -> bool: ...
    def __and__(self, arg0: Fields) -> Fields: ...
    def __del__(self, *args, **kwargs) -> Any: ...
    def __eq__(self, arg0: Fields) -> bool: ...
    def __ne__(self, arg0: Fields) -> bool: ...
    def __or__(self, arg0: Fields) -> Fields: ...

class PointCloud:
    class C(numpy.unsignedinteger):
        @classmethod
        def __init__(cls, *args, **kwargs) -> None: ...
        @overload
        def bit_count(self) -> int: ...
        @overload
        def bit_count(self) -> Any: ...
        def __abs__(self) -> Any: ...
        def __add__(self, other) -> Any: ...
        def __and__(self, other) -> Any: ...
        def __bool__(self) -> Any: ...
        @classmethod
        def __class_getitem__(cls, *args, **kwargs) -> Any: ...
        def __divmod__(self, other) -> Any: ...
        def __eq__(self, other) -> Any: ...
        def __float__(self) -> Any: ...
        def __floordiv__(self, other) -> Any: ...
        def __ge__(self, other) -> Any: ...
        def __gt__(self, other) -> Any: ...
        def __hash__(self) -> Any: ...
        def __index__(self) -> Any: ...
        def __int__(self) -> Any: ...
        def __invert__(self) -> Any: ...
        def __le__(self, other) -> Any: ...
        def __lshift__(self, other) -> Any: ...
        def __lt__(self, other) -> Any: ...
        def __mod__(self, other) -> Any: ...
        def __mul__(self, other) -> Any: ...
        def __ne__(self, other) -> Any: ...
        def __neg__(self) -> Any: ...
        def __or__(self, other) -> Any: ...
        def __pos__(self) -> Any: ...
        def __pow__(self, other) -> Any: ...
        def __radd__(self, other) -> Any: ...
        def __rand__(self, other) -> Any: ...
        def __rdivmod__(self, other) -> Any: ...
        def __rfloordiv__(self, other) -> Any: ...
        def __rlshift__(self, other) -> Any: ...
        def __rmod__(self, other) -> Any: ...
        def __rmul__(self, other) -> Any: ...
        def __ror__(self, other) -> Any: ...
        def __rpow__(self, other) -> Any: ...
        def __rrshift__(self, other) -> Any: ...
        def __rshift__(self, other) -> Any: ...
        def __rsub__(self, other) -> Any: ...
        def __rtruediv__(self, other) -> Any: ...
        def __rxor__(self, other) -> Any: ...
        def __sub__(self, other) -> Any: ...
        def __truediv__(self, other) -> Any: ...
        def __xor__(self, other) -> Any: ...

    class D(numpy.floating):
        @classmethod
        def __init__(cls, *args, **kwargs) -> None: ...
        @overload
        def as_integer_ratio(self) -> Any: ...
        @overload
        def as_integer_ratio(self) -> Any: ...
        @overload
        def as_integer_ratio(self) -> Any: ...
        @overload
        def is_integer(self) -> bool: ...
        @overload
        def is_integer(self) -> Any: ...
        @overload
        def is_integer(self) -> Any: ...
        def __abs__(self) -> Any: ...
        def __add__(self, other) -> Any: ...
        def __bool__(self) -> Any: ...
        @classmethod
        def __class_getitem__(cls, *args, **kwargs) -> Any: ...
        def __divmod__(self, other) -> Any: ...
        def __eq__(self, other) -> Any: ...
        def __float__(self) -> Any: ...
        def __floordiv__(self, other) -> Any: ...
        def __ge__(self, other) -> Any: ...
        def __gt__(self, other) -> Any: ...
        def __hash__(self) -> Any: ...
        def __int__(self) -> Any: ...
        def __le__(self, other) -> Any: ...
        def __lt__(self, other) -> Any: ...
        def __mod__(self, other) -> Any: ...
        def __mul__(self, other) -> Any: ...
        def __ne__(self, other) -> Any: ...
        def __neg__(self) -> Any: ...
        def __pos__(self) -> Any: ...
        def __pow__(self, other) -> Any: ...
        def __radd__(self, other) -> Any: ...
        def __rdivmod__(self, other) -> Any: ...
        def __rfloordiv__(self, other) -> Any: ...
        def __rmod__(self, other) -> Any: ...
        def __rmul__(self, other) -> Any: ...
        def __rpow__(self, other) -> Any: ...
        def __rsub__(self, other) -> Any: ...
        def __rtruediv__(self, other) -> Any: ...
        def __sub__(self, other) -> Any: ...
        def __truediv__(self, other) -> Any: ...

    class T(numpy.floating):
        @classmethod
        def __init__(cls, *args, **kwargs) -> None: ...
        @overload
        def as_integer_ratio(self) -> Any: ...
        @overload
        def as_integer_ratio(self) -> Any: ...
        @overload
        def as_integer_ratio(self) -> Any: ...
        @overload
        def is_integer(self) -> bool: ...
        @overload
        def is_integer(self) -> Any: ...
        @overload
        def is_integer(self) -> Any: ...
        def __abs__(self) -> Any: ...
        def __add__(self, other) -> Any: ...
        def __bool__(self) -> Any: ...
        @classmethod
        def __class_getitem__(cls, *args, **kwargs) -> Any: ...
        def __divmod__(self, other) -> Any: ...
        def __eq__(self, other) -> Any: ...
        def __float__(self) -> Any: ...
        def __floordiv__(self, other) -> Any: ...
        def __ge__(self, other) -> Any: ...
        def __gt__(self, other) -> Any: ...
        def __hash__(self) -> Any: ...
        def __int__(self) -> Any: ...
        def __le__(self, other) -> Any: ...
        def __lt__(self, other) -> Any: ...
        def __mod__(self, other) -> Any: ...
        def __mul__(self, other) -> Any: ...
        def __ne__(self, other) -> Any: ...
        def __neg__(self) -> Any: ...
        def __pos__(self) -> Any: ...
        def __pow__(self, other) -> Any: ...
        def __radd__(self, other) -> Any: ...
        def __rdivmod__(self, other) -> Any: ...
        def __rfloordiv__(self, other) -> Any: ...
        def __rmod__(self, other) -> Any: ...
        def __rmul__(self, other) -> Any: ...
        def __rpow__(self, other) -> Any: ...
        def __rsub__(self, other) -> Any: ...
        def __rtruediv__(self, other) -> Any: ...
        def __sub__(self, other) -> Any: ...
        def __truediv__(self, other) -> Any: ...
    kDefaultValue: ClassVar[float] = ...
    @overload
    def __init__(self, new_size: int = ..., fields: Fields = ...) -> None: ...
    @overload
    def __init__(self, other: PointCloud) -> None: ...
    def Crop(self, lower_xyz: numpy.ndarray[numpy.float32[3,1]], upper_xyz: numpy.ndarray[numpy.float32[3,1]]) -> PointCloud: ...
    def EstimateNormals(self, radius: float, num_closest: int, parallelize: bool = ...) -> bool: ...
    def FlipNormalsTowardPoint(self, p_CP: numpy.ndarray[numpy.float32[3,1]]) -> None: ...
    def IsDefaultValue(self, *args, **kwargs) -> Any: ...
    def IsInvalidValue(self, *args, **kwargs) -> Any: ...
    def SetFields(self, new_fields: Fields, skip_initialize: bool = ...) -> None: ...
    def SetFrom(self, other: PointCloud) -> None: ...
    def VoxelizedDownSample(self, voxel_size: float, parallelize: bool = ...) -> PointCloud: ...
    def fields(self) -> Fields: ...
    def has_normals(self) -> bool: ...
    def has_rgbs(self) -> bool: ...
    def has_xyzs(self) -> bool: ...
    def mutable_normal(self, i: int) -> numpy.ndarray[numpy.float32[3,1],flags.writeable]: ...
    def mutable_normals(self) -> numpy.ndarray[numpy.float32[3,n],flags.writeable,flags.f_contiguous]: ...
    def mutable_rgb(self, i: int) -> numpy.ndarray[numpy.uint8[3,1],flags.writeable]: ...
    def mutable_rgbs(self) -> numpy.ndarray[numpy.uint8[3,n],flags.writeable,flags.f_contiguous]: ...
    def mutable_xyz(self, i: int) -> numpy.ndarray[numpy.float32[3,1],flags.writeable]: ...
    def mutable_xyzs(self) -> numpy.ndarray[numpy.float32[3,n],flags.writeable,flags.f_contiguous]: ...
    def normal(self, i: int) -> numpy.ndarray[numpy.float32[3,1]]: ...
    def normals(self) -> numpy.ndarray[numpy.float32[3,n],flags.f_contiguous]: ...
    def resize(self, new_size: int) -> None: ...
    def rgb(self, i: int) -> numpy.ndarray[numpy.uint8[3,1]]: ...
    def rgbs(self) -> numpy.ndarray[numpy.uint8[3,n],flags.f_contiguous]: ...
    def size(self) -> int: ...
    def xyz(self, i: int) -> numpy.ndarray[numpy.float32[3,1]]: ...
    def xyzs(self) -> numpy.ndarray[numpy.float32[3,n],flags.f_contiguous]: ...

class PointCloudToLcm(pydrake.systems.framework.LeafSystem):
    def __init__(self, frame_name: str = ...) -> None: ...

class _TemporaryName_N5drake5ValueINS_10perception10PointCloudEEE(pydrake.common.value.AbstractValue):
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    @overload
    def __init__(self, arg0: PointCloud) -> None: ...
    @overload
    def __init__(self, *args, **kwargs) -> Any: ...
    def get_mutable_value(self) -> PointCloud: ...
    def get_value(self) -> PointCloud: ...
    def set_value(self, arg0: PointCloud) -> None: ...

def Concatenate(clouds: List[PointCloud]) -> PointCloud: ...
