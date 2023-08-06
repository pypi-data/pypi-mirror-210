from typing import Any, ClassVar

from typing import overload
import numpy
import pydrake.autodiffutils
import pydrake.common.cpp_template
import pydrake.common.value
import pydrake.symbolic
AngleAxis_: pydrake.common.cpp_template.TemplateClass
Isometry3_: pydrake.common.cpp_template.TemplateClass
Quaternion_: pydrake.common.cpp_template.TemplateClass

class AngleAxis:
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, angle: float, axis: numpy.ndarray[numpy.float64[3,1]]) -> None: ...
    @overload
    def __init__(self, quaternion: Quaternion) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[numpy.float64[3,3]]) -> None: ...
    @overload
    def __init__(self, other: AngleAxis) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def angle(self) -> float: ...
    def axis(self) -> numpy.ndarray[numpy.float64[3,1]]: ...
    def cast𝓣AutoDiffXd𝓤(self, *args, **kwargs) -> Any: ...
    def cast𝓣Expression𝓤(self, *args, **kwargs) -> Any: ...
    def cast𝓣float𝓤(self) -> AngleAxis: ...
    def inverse(self) -> AngleAxis: ...
    def multiply(self, other: AngleAxis) -> Quaternion: ...
    def quaternion(self) -> Quaternion: ...
    def rotation(self) -> numpy.ndarray[numpy.float64[3,3]]: ...
    def set_angle(self, angle: float) -> None: ...
    def set_axis(self, axis: numpy.ndarray[numpy.float64[3,1]]) -> None: ...
    def set_quaternion(self, q: Quaternion) -> None: ...
    def set_rotation(self, rotation: numpy.ndarray[numpy.float64[3,3]]) -> None: ...
    def __copy__(self) -> AngleAxis: ...
    def __deepcopy__(self, arg0: dict) -> AngleAxis: ...
    def __getstate__(self) -> tuple: ...
    def __matmul__(self, *args, **kwargs) -> Any: ...
    def __setstate__(self, arg0: tuple) -> None: ...

class AngleAxis_𝓣AutoDiffXd𝓤:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, angle: pydrake.autodiffutils.AutoDiffXd, axis: numpy.ndarray[object[3,1]]) -> None: ...
    @overload
    def __init__(self, quaternion: Quaternion_𝓣AutoDiffXd𝓤) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def __init__(self, other: AngleAxis_𝓣AutoDiffXd𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def angle(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def axis(self) -> numpy.ndarray[object[3,1]]: ...
    def cast𝓣AutoDiffXd𝓤(self) -> AngleAxis_𝓣AutoDiffXd𝓤: ...
    def inverse(self) -> AngleAxis_𝓣AutoDiffXd𝓤: ...
    def multiply(self, other: AngleAxis_𝓣AutoDiffXd𝓤) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def quaternion(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_angle(self, angle: pydrake.autodiffutils.AutoDiffXd) -> None: ...
    def set_axis(self, axis: numpy.ndarray[object[3,1]]) -> None: ...
    def set_quaternion(self, q: Quaternion_𝓣AutoDiffXd𝓤) -> None: ...
    def set_rotation(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    def __copy__(self) -> AngleAxis_𝓣AutoDiffXd𝓤: ...
    def __deepcopy__(self, arg0: dict) -> AngleAxis_𝓣AutoDiffXd𝓤: ...
    def __getstate__(self) -> tuple: ...
    def __matmul__(self, *args, **kwargs) -> Any: ...
    def __setstate__(self, arg0: tuple) -> None: ...

class AngleAxis_𝓣Expression𝓤:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, angle: pydrake.symbolic.Expression, axis: numpy.ndarray[object[3,1]]) -> None: ...
    @overload
    def __init__(self, quaternion: Quaternion_𝓣Expression𝓤) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def __init__(self, other: AngleAxis_𝓣Expression𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def angle(self) -> pydrake.symbolic.Expression: ...
    def axis(self) -> numpy.ndarray[object[3,1]]: ...
    def cast𝓣Expression𝓤(self) -> AngleAxis_𝓣Expression𝓤: ...
    def inverse(self) -> AngleAxis_𝓣Expression𝓤: ...
    def multiply(self, other: AngleAxis_𝓣Expression𝓤) -> Quaternion_𝓣Expression𝓤: ...
    def quaternion(self) -> Quaternion_𝓣Expression𝓤: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_angle(self, angle: pydrake.symbolic.Expression) -> None: ...
    def set_axis(self, axis: numpy.ndarray[object[3,1]]) -> None: ...
    def set_quaternion(self, q: Quaternion_𝓣Expression𝓤) -> None: ...
    def set_rotation(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    def __copy__(self) -> AngleAxis_𝓣Expression𝓤: ...
    def __deepcopy__(self, arg0: dict) -> AngleAxis_𝓣Expression𝓤: ...
    def __getstate__(self) -> tuple: ...
    def __matmul__(self, *args, **kwargs) -> Any: ...
    def __setstate__(self, arg0: tuple) -> None: ...

class Isometry3:
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, matrix: numpy.ndarray[numpy.float64[4,4]]) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[numpy.float64[3,3]], translation: numpy.ndarray[numpy.float64[3,1]]) -> None: ...
    @overload
    def __init__(self, other: Isometry3) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣AutoDiffXd𝓤(self, *args, **kwargs) -> Any: ...
    def cast𝓣Expression𝓤(self, *args, **kwargs) -> Any: ...
    def cast𝓣float𝓤(self) -> Isometry3: ...
    def inverse(self) -> Isometry3: ...
    def matrix(self) -> numpy.ndarray[numpy.float64[4,4]]: ...
    def quaternion(self, *args, **kwargs) -> Any: ...
    def rotation(self) -> numpy.ndarray[numpy.float64[3,3]]: ...
    def set_matrix(self, arg0: numpy.ndarray[numpy.float64[4,4]]) -> None: ...
    def set_quaternion(self, *args, **kwargs) -> Any: ...
    def set_rotation(self, arg0: numpy.ndarray[numpy.float64[3,3]]) -> None: ...
    def set_translation(self, arg0: numpy.ndarray[numpy.float64[3,1]]) -> None: ...
    def translation(self) -> numpy.ndarray[numpy.float64[3,1]]: ...
    def __copy__(self) -> Isometry3: ...
    def __deepcopy__(self, arg0: dict) -> Isometry3: ...
    def __getstate__(self) -> numpy.ndarray[numpy.float64[4,4]]: ...
    def __setstate__(self, arg0: numpy.ndarray[numpy.float64[4,4]]) -> None: ...

class Isometry3_𝓣AutoDiffXd𝓤:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, matrix: numpy.ndarray[object[4,4]]) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]], translation: numpy.ndarray[object[3,1]]) -> None: ...
    @overload
    def __init__(self, other: Isometry3_𝓣AutoDiffXd𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣AutoDiffXd𝓤(self) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def inverse(self) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def matrix(self) -> numpy.ndarray[object[4,4]]: ...
    def quaternion(self, *args, **kwargs) -> Any: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_matrix(self, arg0: numpy.ndarray[object[4,4]]) -> None: ...
    def set_quaternion(self, *args, **kwargs) -> Any: ...
    def set_rotation(self, arg0: numpy.ndarray[object[3,3]]) -> None: ...
    def set_translation(self, arg0: numpy.ndarray[object[3,1]]) -> None: ...
    def translation(self) -> numpy.ndarray[object[3,1]]: ...
    def __copy__(self) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def __deepcopy__(self, arg0: dict) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def __getstate__(self) -> numpy.ndarray[object[4,4]]: ...
    def __setstate__(self, arg0: numpy.ndarray[object[4,4]]) -> None: ...

class Isometry3_𝓣Expression𝓤:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, matrix: numpy.ndarray[object[4,4]]) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]], translation: numpy.ndarray[object[3,1]]) -> None: ...
    @overload
    def __init__(self, other: Isometry3_𝓣Expression𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣Expression𝓤(self) -> Isometry3_𝓣Expression𝓤: ...
    def inverse(self) -> Isometry3_𝓣Expression𝓤: ...
    def matrix(self) -> numpy.ndarray[object[4,4]]: ...
    def quaternion(self, *args, **kwargs) -> Any: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_matrix(self, arg0: numpy.ndarray[object[4,4]]) -> None: ...
    def set_quaternion(self, *args, **kwargs) -> Any: ...
    def set_rotation(self, arg0: numpy.ndarray[object[3,3]]) -> None: ...
    def set_translation(self, arg0: numpy.ndarray[object[3,1]]) -> None: ...
    def translation(self) -> numpy.ndarray[object[3,1]]: ...
    def __copy__(self) -> Isometry3_𝓣Expression𝓤: ...
    def __deepcopy__(self, arg0: dict) -> Isometry3_𝓣Expression𝓤: ...
    def __getstate__(self) -> numpy.ndarray[object[4,4]]: ...
    def __setstate__(self, arg0: numpy.ndarray[object[4,4]]) -> None: ...

class Quaternion:
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, wxyz: numpy.ndarray[numpy.float64[4,1]]) -> None: ...
    @overload
    def __init__(self, w: float, x: float, y: float, z: float) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[numpy.float64[3,3]]) -> None: ...
    @overload
    def __init__(self, other: Quaternion) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣AutoDiffXd𝓤(self, *args, **kwargs) -> Any: ...
    def cast𝓣Expression𝓤(self, *args, **kwargs) -> Any: ...
    def cast𝓣float𝓤(self) -> Quaternion: ...
    def conjugate(self) -> Quaternion: ...
    def inverse(self) -> Quaternion: ...
    def rotation(self) -> numpy.ndarray[numpy.float64[3,3]]: ...
    def set_rotation(self, arg0: numpy.ndarray[numpy.float64[3,3]]) -> None: ...
    @overload
    def set_wxyz(self, wxyz: numpy.ndarray[numpy.float64[4,1]]) -> None: ...
    @overload
    def set_wxyz(self, w: float, x: float, y: float, z: float) -> None: ...
    def slerp(self, t: float, other: Quaternion) -> Quaternion: ...
    def w(self) -> float: ...
    def wxyz(self) -> numpy.ndarray[numpy.float64[4,1]]: ...
    def x(self) -> float: ...
    def xyz(self) -> numpy.ndarray[numpy.float64[3,1]]: ...
    def y(self) -> float: ...
    def z(self) -> float: ...
    def __copy__(self) -> Quaternion: ...
    def __deepcopy__(self, arg0: dict) -> Quaternion: ...
    def __getstate__(self) -> object: ...
    def __setstate__(self, arg0: object) -> None: ...

class Quaternion_𝓣AutoDiffXd𝓤:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, wxyz: numpy.ndarray[object[4,1]]) -> None: ...
    @overload
    def __init__(self, w: pydrake.autodiffutils.AutoDiffXd, x: pydrake.autodiffutils.AutoDiffXd, y: pydrake.autodiffutils.AutoDiffXd, z: pydrake.autodiffutils.AutoDiffXd) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def __init__(self, other: Quaternion_𝓣AutoDiffXd𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣AutoDiffXd𝓤(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def conjugate(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def inverse(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_rotation(self, arg0: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def set_wxyz(self, wxyz: numpy.ndarray[object[4,1]]) -> None: ...
    @overload
    def set_wxyz(self, w: pydrake.autodiffutils.AutoDiffXd, x: pydrake.autodiffutils.AutoDiffXd, y: pydrake.autodiffutils.AutoDiffXd, z: pydrake.autodiffutils.AutoDiffXd) -> None: ...
    def slerp(self, t: float, other: Quaternion_𝓣AutoDiffXd𝓤) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def w(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def wxyz(self) -> numpy.ndarray[object[4,1]]: ...
    def x(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def xyz(self) -> numpy.ndarray[object[3,1]]: ...
    def y(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def z(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def __copy__(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def __deepcopy__(self, arg0: dict) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def __getstate__(self) -> object: ...
    def __setstate__(self, arg0: object) -> None: ...

class Quaternion_𝓣Expression𝓤:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, wxyz: numpy.ndarray[object[4,1]]) -> None: ...
    @overload
    def __init__(self, w: pydrake.symbolic.Expression, x: pydrake.symbolic.Expression, y: pydrake.symbolic.Expression, z: pydrake.symbolic.Expression) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def __init__(self, other: Quaternion_𝓣Expression𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣Expression𝓤(self) -> Quaternion_𝓣Expression𝓤: ...
    def conjugate(self) -> Quaternion_𝓣Expression𝓤: ...
    def inverse(self) -> Quaternion_𝓣Expression𝓤: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_rotation(self, arg0: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def set_wxyz(self, wxyz: numpy.ndarray[object[4,1]]) -> None: ...
    @overload
    def set_wxyz(self, w: pydrake.symbolic.Expression, x: pydrake.symbolic.Expression, y: pydrake.symbolic.Expression, z: pydrake.symbolic.Expression) -> None: ...
    def slerp(self, t: float, other: Quaternion_𝓣Expression𝓤) -> Quaternion_𝓣Expression𝓤: ...
    def w(self) -> pydrake.symbolic.Expression: ...
    def wxyz(self) -> numpy.ndarray[object[4,1]]: ...
    def x(self) -> pydrake.symbolic.Expression: ...
    def xyz(self) -> numpy.ndarray[object[3,1]]: ...
    def y(self) -> pydrake.symbolic.Expression: ...
    def z(self) -> pydrake.symbolic.Expression: ...
    def __copy__(self) -> Quaternion_𝓣Expression𝓤: ...
    def __deepcopy__(self, arg0: dict) -> Quaternion_𝓣Expression𝓤: ...
    def __getstate__(self) -> object: ...
    def __setstate__(self, arg0: object) -> None: ...

class _MangledName:
    UNICODE_COMMA: ClassVar[str] = ...
    UNICODE_LEFT_BRACKET: ClassVar[str] = ...
    UNICODE_PERIOD: ClassVar[str] = ...
    UNICODE_RIGHT_BRACKET: ClassVar[str] = ...
    def demangle(self, *args, **kwargs) -> Any: ...
    def mangle(self, name) -> Any: ...
    def module_getattr(self, 
module_name = ..., module_globals = ..., name = ...) -> Any: ...

class _TemporaryName_N5Eigen10QuaternionIN5drake8symbolic10ExpressionELi0EEE:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, wxyz: numpy.ndarray[object[4,1]]) -> None: ...
    @overload
    def __init__(self, w: pydrake.symbolic.Expression, x: pydrake.symbolic.Expression, y: pydrake.symbolic.Expression, z: pydrake.symbolic.Expression) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def __init__(self, other: Quaternion_𝓣Expression𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣Expression𝓤(self) -> Quaternion_𝓣Expression𝓤: ...
    def conjugate(self) -> Quaternion_𝓣Expression𝓤: ...
    def inverse(self) -> Quaternion_𝓣Expression𝓤: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_rotation(self, arg0: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def set_wxyz(self, wxyz: numpy.ndarray[object[4,1]]) -> None: ...
    @overload
    def set_wxyz(self, w: pydrake.symbolic.Expression, x: pydrake.symbolic.Expression, y: pydrake.symbolic.Expression, z: pydrake.symbolic.Expression) -> None: ...
    def slerp(self, t: float, other: Quaternion_𝓣Expression𝓤) -> Quaternion_𝓣Expression𝓤: ...
    def w(self) -> pydrake.symbolic.Expression: ...
    def wxyz(self) -> numpy.ndarray[object[4,1]]: ...
    def x(self) -> pydrake.symbolic.Expression: ...
    def xyz(self) -> numpy.ndarray[object[3,1]]: ...
    def y(self) -> pydrake.symbolic.Expression: ...
    def z(self) -> pydrake.symbolic.Expression: ...
    def __copy__(self) -> Quaternion_𝓣Expression𝓤: ...
    def __deepcopy__(self, arg0: dict) -> Quaternion_𝓣Expression𝓤: ...
    def __getstate__(self) -> object: ...
    def __setstate__(self, arg0: object) -> None: ...

class _TemporaryName_N5Eigen10QuaternionINS_14AutoDiffScalarINS_6MatrixIdLin1ELi1ELi0ELin1ELi1EEEEELi0EEE:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, wxyz: numpy.ndarray[object[4,1]]) -> None: ...
    @overload
    def __init__(self, w: pydrake.autodiffutils.AutoDiffXd, x: pydrake.autodiffutils.AutoDiffXd, y: pydrake.autodiffutils.AutoDiffXd, z: pydrake.autodiffutils.AutoDiffXd) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def __init__(self, other: Quaternion_𝓣AutoDiffXd𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣AutoDiffXd𝓤(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def conjugate(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def inverse(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_rotation(self, arg0: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def set_wxyz(self, wxyz: numpy.ndarray[object[4,1]]) -> None: ...
    @overload
    def set_wxyz(self, w: pydrake.autodiffutils.AutoDiffXd, x: pydrake.autodiffutils.AutoDiffXd, y: pydrake.autodiffutils.AutoDiffXd, z: pydrake.autodiffutils.AutoDiffXd) -> None: ...
    def slerp(self, t: float, other: Quaternion_𝓣AutoDiffXd𝓤) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def w(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def wxyz(self) -> numpy.ndarray[object[4,1]]: ...
    def x(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def xyz(self) -> numpy.ndarray[object[3,1]]: ...
    def y(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def z(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def __copy__(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def __deepcopy__(self, arg0: dict) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def __getstate__(self) -> object: ...
    def __setstate__(self, arg0: object) -> None: ...

class _TemporaryName_N5Eigen9AngleAxisIN5drake8symbolic10ExpressionEEE:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, angle: pydrake.symbolic.Expression, axis: numpy.ndarray[object[3,1]]) -> None: ...
    @overload
    def __init__(self, quaternion: Quaternion_𝓣Expression𝓤) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def __init__(self, other: AngleAxis_𝓣Expression𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def angle(self) -> pydrake.symbolic.Expression: ...
    def axis(self) -> numpy.ndarray[object[3,1]]: ...
    def cast𝓣Expression𝓤(self) -> AngleAxis_𝓣Expression𝓤: ...
    def inverse(self) -> AngleAxis_𝓣Expression𝓤: ...
    def multiply(self, other: AngleAxis_𝓣Expression𝓤) -> Quaternion_𝓣Expression𝓤: ...
    def quaternion(self) -> Quaternion_𝓣Expression𝓤: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_angle(self, angle: pydrake.symbolic.Expression) -> None: ...
    def set_axis(self, axis: numpy.ndarray[object[3,1]]) -> None: ...
    def set_quaternion(self, q: Quaternion_𝓣Expression𝓤) -> None: ...
    def set_rotation(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    def __copy__(self) -> AngleAxis_𝓣Expression𝓤: ...
    def __deepcopy__(self, arg0: dict) -> AngleAxis_𝓣Expression𝓤: ...
    def __getstate__(self) -> tuple: ...
    def __matmul__(self, *args, **kwargs) -> Any: ...
    def __setstate__(self, arg0: tuple) -> None: ...

class _TemporaryName_N5Eigen9AngleAxisINS_14AutoDiffScalarINS_6MatrixIdLin1ELi1ELi0ELin1ELi1EEEEEEE:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, angle: pydrake.autodiffutils.AutoDiffXd, axis: numpy.ndarray[object[3,1]]) -> None: ...
    @overload
    def __init__(self, quaternion: Quaternion_𝓣AutoDiffXd𝓤) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    @overload
    def __init__(self, other: AngleAxis_𝓣AutoDiffXd𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def angle(self) -> pydrake.autodiffutils.AutoDiffXd: ...
    def axis(self) -> numpy.ndarray[object[3,1]]: ...
    def cast𝓣AutoDiffXd𝓤(self) -> AngleAxis_𝓣AutoDiffXd𝓤: ...
    def inverse(self) -> AngleAxis_𝓣AutoDiffXd𝓤: ...
    def multiply(self, other: AngleAxis_𝓣AutoDiffXd𝓤) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def quaternion(self) -> Quaternion_𝓣AutoDiffXd𝓤: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_angle(self, angle: pydrake.autodiffutils.AutoDiffXd) -> None: ...
    def set_axis(self, axis: numpy.ndarray[object[3,1]]) -> None: ...
    def set_quaternion(self, q: Quaternion_𝓣AutoDiffXd𝓤) -> None: ...
    def set_rotation(self, rotation: numpy.ndarray[object[3,3]]) -> None: ...
    def __copy__(self) -> AngleAxis_𝓣AutoDiffXd𝓤: ...
    def __deepcopy__(self, arg0: dict) -> AngleAxis_𝓣AutoDiffXd𝓤: ...
    def __getstate__(self) -> tuple: ...
    def __matmul__(self, *args, **kwargs) -> Any: ...
    def __setstate__(self, arg0: tuple) -> None: ...

class _TemporaryName_N5Eigen9TransformIN5drake8symbolic10ExpressionELi3ELi1ELi0EEE:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, matrix: numpy.ndarray[object[4,4]]) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]], translation: numpy.ndarray[object[3,1]]) -> None: ...
    @overload
    def __init__(self, other: Isometry3_𝓣Expression𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣Expression𝓤(self) -> Isometry3_𝓣Expression𝓤: ...
    def inverse(self) -> Isometry3_𝓣Expression𝓤: ...
    def matrix(self) -> numpy.ndarray[object[4,4]]: ...
    def quaternion(self, *args, **kwargs) -> Any: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_matrix(self, arg0: numpy.ndarray[object[4,4]]) -> None: ...
    def set_quaternion(self, *args, **kwargs) -> Any: ...
    def set_rotation(self, arg0: numpy.ndarray[object[3,3]]) -> None: ...
    def set_translation(self, arg0: numpy.ndarray[object[3,1]]) -> None: ...
    def translation(self) -> numpy.ndarray[object[3,1]]: ...
    def __copy__(self) -> Isometry3_𝓣Expression𝓤: ...
    def __deepcopy__(self, arg0: dict) -> Isometry3_𝓣Expression𝓤: ...
    def __getstate__(self) -> numpy.ndarray[object[4,4]]: ...
    def __setstate__(self, arg0: numpy.ndarray[object[4,4]]) -> None: ...

class _TemporaryName_N5Eigen9TransformINS_14AutoDiffScalarINS_6MatrixIdLin1ELi1ELi0ELin1ELi1EEEEELi3ELi1ELi0EEE:
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    multiply: ClassVar[function] = ...
    __matmul__: ClassVar[function] = ...
    cast: Any
    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, matrix: numpy.ndarray[object[4,4]]) -> None: ...
    @overload
    def __init__(self, rotation: numpy.ndarray[object[3,3]], translation: numpy.ndarray[object[3,1]]) -> None: ...
    @overload
    def __init__(self, other: Isometry3_𝓣AutoDiffXd𝓤) -> None: ...
    def Identity(self, *args, **kwargs) -> Any: ...
    def cast𝓣AutoDiffXd𝓤(self) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def inverse(self) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def matrix(self) -> numpy.ndarray[object[4,4]]: ...
    def quaternion(self, *args, **kwargs) -> Any: ...
    def rotation(self) -> numpy.ndarray[object[3,3]]: ...
    def set_matrix(self, arg0: numpy.ndarray[object[4,4]]) -> None: ...
    def set_quaternion(self, *args, **kwargs) -> Any: ...
    def set_rotation(self, arg0: numpy.ndarray[object[3,3]]) -> None: ...
    def set_translation(self, arg0: numpy.ndarray[object[3,1]]) -> None: ...
    def translation(self) -> numpy.ndarray[object[3,1]]: ...
    def __copy__(self) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def __deepcopy__(self, arg0: dict) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def __getstate__(self) -> numpy.ndarray[object[4,4]]: ...
    def __setstate__(self, arg0: numpy.ndarray[object[4,4]]) -> None: ...

class _TemporaryName_N5drake5ValueIN5Eigen9TransformINS1_14AutoDiffScalarINS1_6MatrixIdLin1ELi1ELi0ELin1ELi1EEEEELi3ELi1ELi0EEEEE(pydrake.common.value.AbstractValue):
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    @overload
    def __init__(self, arg0: Isometry3_𝓣AutoDiffXd𝓤) -> None: ...
    @overload
    def __init__(self, *args, **kwargs) -> Any: ...
    def get_mutable_value(self) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def get_value(self) -> Isometry3_𝓣AutoDiffXd𝓤: ...
    def set_value(self, arg0: Isometry3_𝓣AutoDiffXd𝓤) -> None: ...

class _TemporaryName_N5drake5ValueIN5Eigen9TransformINS_8symbolic10ExpressionELi3ELi1ELi0EEEEE(pydrake.common.value.AbstractValue):
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    @overload
    def __init__(self, arg0: Isometry3_𝓣Expression𝓤) -> None: ...
    @overload
    def __init__(self, *args, **kwargs) -> Any: ...
    def get_mutable_value(self) -> Isometry3_𝓣Expression𝓤: ...
    def get_value(self) -> Isometry3_𝓣Expression𝓤: ...
    def set_value(self, arg0: Isometry3_𝓣Expression𝓤) -> None: ...

class _TemporaryName_N5drake5ValueIN5Eigen9TransformIdLi3ELi1ELi0EEEEE(pydrake.common.value.AbstractValue):
    _original_name: ClassVar[str] = ...
    _original_qualname: ClassVar[str] = ...
    @overload
    def __init__(self, arg0: Isometry3) -> None: ...
    @overload
    def __init__(self, *args, **kwargs) -> Any: ...
    def get_mutable_value(self) -> Isometry3: ...
    def get_value(self) -> Isometry3: ...
    def set_value(self, arg0: Isometry3) -> None: ...
