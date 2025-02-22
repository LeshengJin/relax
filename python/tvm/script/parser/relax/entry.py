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
# pylint: disable=missing-docstring, invalid-name
import inspect
from typing import Any
from typing import Callable as _Callable
from typing import Dict, List, Optional, Set, TypeVar, Union

from tvm.relax import (
    Expr,
    FuncStructInfo,
    Function,
    ObjectStructInfo,
    PrimStructInfo,
    ShapeStructInfo,
    StructInfo,
    TensorStructInfo,
    TupleStructInfo,
)
from tvm.runtime import ObjectGeneric
from tvm.tir import PrimExpr

from .._core import parse, utils

FType = TypeVar("FType", bound=_Callable)

############################## R.function ##############################


def function(f: FType) -> Union[Function, FType]:
    if not inspect.isfunction(f):
        raise TypeError(f"Expect a function, but got: {f}")
    if utils.is_defined_in_class(inspect.stack(), f):
        return f
    return parse(f, utils.inspect_function_capture(f))


setattr(function, "dispatch_token", "relax")


############################# Struct Info ##############################


class StructInfoProxy(ObjectGeneric):
    def as_struct_info(self, dict_globals: Optional[Dict[str, Any]] = None) -> StructInfo:
        raise NotImplementedError()

    def get_symbolic_vars(self) -> Set[str]:
        return {}

    def asobject(self):
        return self.as_struct_info(None)


############################### R.Tensor ###############################


def _eval_shape(expr: Union[str, PrimExpr], dict_globals: Optional[Dict[str, Any]]) -> PrimExpr:
    if isinstance(expr, str):
        code = compile(expr, "<string>", "eval")
        return eval(code, dict_globals or {})  # pylint: disable=eval-used
    else:
        return expr


class TensorProxy(StructInfoProxy):
    shape: Optional[List[Union[str, PrimExpr]]]
    dtype: str
    ndim: int

    def __init__(
        self,
        shape: Optional[List[Union[PrimExpr, str]]] = None,
        dtype: Optional[str] = None,
        ndim: int = -1,
    ) -> None:
        self.shape = shape
        self.dtype = dtype
        self.ndim = ndim
        super().__init__()

    def get_symbolic_vars(self) -> Set[str]:
        if self.shape is None:
            return {}
        else:
            return {s for s in self.shape if isinstance(s, str) and s.isidentifier()}

    def as_struct_info(self, dict_globals: Optional[Dict[str, Any]] = None) -> TensorStructInfo:
        if self.shape is None:
            return TensorStructInfo(None, self.dtype, self.ndim)
        else:
            if dict_globals is None and any([isinstance(s, str) for s in self.shape]):
                raise ValueError(
                    "String-defined shape expr is only allowed when parsing function parameters "
                    "and return annotations for TVMScript."
                )
            shape = [_eval_shape(s, dict_globals) for s in self.shape]
            return TensorStructInfo(shape, self.dtype, self.ndim)


def Tensor(
    shape: Optional[List[Union[PrimExpr, str]]] = None,
    dtype: Optional[str] = None,
    ndim: int = -1,
) -> TensorProxy:
    # scalar tensor case
    if shape is not None and len(shape) == 0:
        shape = []
    if isinstance(shape, str) and dtype is None:
        dtype = shape
        shape = None

    if shape is not None and not isinstance(shape, (tuple, list)):
        raise ValueError(f"shape must be a list or tuple, but got: {shape}")
    return TensorProxy(shape, dtype, ndim)


############################## R.Callable ##############################


class CallableProxy(StructInfoProxy):
    params: List[StructInfoProxy]
    ret: StructInfoProxy
    """Function type.

    A function type consists of a list of type parameters to enable
    the definition of generic functions,
    a set of type constraints which we omit for the time being,
    a sequence of argument types, and a return type.

    Parameters
    ----------
    params : List[StructInfoProxy]
        The argument StructInfoProxy

    ret : StructInfoProxy
        The return StructInfoProxy.

    """

    def __init__(
        self,
        params: Union[StructInfoProxy, List[StructInfoProxy]],
        ret: StructInfoProxy,
    ) -> None:
        if not isinstance(params, (list, tuple)):
            params = [params]
        # convert `R.Tensor` to `R.Tensor()`
        self.params = [param() if callable(param) else param for param in params]
        self.ret = ret() if callable(ret) else ret

    def get_symbolic_vars(self) -> Set[str]:
        return set().union(*[p.get_symbolic_vars() for p in self.params])

    def as_struct_info(self, dict_globals: Optional[Dict[str, Any]] = None) -> FuncStructInfo:
        params = [param.as_struct_info(dict_globals) for param in self.params]
        ret = self.ret.as_struct_info(dict_globals)
        return FuncStructInfo(params, ret)


def Callable(
    params: Union[StructInfoProxy, List[StructInfoProxy]],
    ret: StructInfoProxy,
) -> CallableProxy:
    return CallableProxy(params, ret)


############################### R.Tuple ################################


class TupleProxy(StructInfoProxy):
    fields: List[StructInfoProxy]
    """The type of tuple values.

    Parameters
    ----------
    fields : List[StructInfoProxy]
        The fields in the tuple
    """

    def __init__(
        self,
        *fields: List[StructInfoProxy],
    ) -> None:
        if len(fields) == 1 and isinstance(fields[0], (tuple, list)):
            fields = fields[0]
        # convert `R.Tensor` to `R.Tensor()`
        self.fields = [field() if callable(field) else field for field in fields]

    def get_symbolic_vars(self) -> Set[str]:
        return set().union(*[f.get_symbolic_vars() for f in self.fields])

    def as_struct_info(self, dict_globals: Optional[Dict[str, Any]] = None) -> TupleStructInfo:
        fields = [field.as_struct_info(dict_globals) for field in self.fields]
        return TupleStructInfo(fields)


def Tuple(*fields: List[StructInfoProxy]) -> TupleProxy:
    return TupleProxy(*fields)


############################### R.Shape ################################


class ShapeProxy(StructInfoProxy):
    values: Optional[List[PrimExpr]]
    ndim: int
    """The type of shape values.

    Parameters
    ----------
    values : Optional[List[PrimExpr]]
       The symbolic shape values if known.

    ndim : Optional[int]
       The size of the shape.
    """

    def __init__(
        self,
        values: Optional[List[PrimExpr]] = None,
        ndim: int = -1,
    ) -> None:
        self.values = values
        self.ndim = ndim

    def get_symbolic_vars(self) -> Set[str]:
        if self.values is None:
            return {}
        else:
            return {v for v in self.values if isinstance(v, str) and v.isidentifier()}

    def as_struct_info(self, dict_globals: Optional[Dict[str, Any]] = None) -> ShapeStructInfo:
        values = [_eval_shape(v, dict_globals) for v in self.values] if self.values else None
        return ShapeStructInfo(values, self.ndim)


def Shape(values: Optional[List[PrimExpr]] = None, ndim: int = -1) -> ShapeProxy:
    return ShapeProxy(values, ndim)


############################### R.Object ################################


class ObjectProxy(StructInfoProxy):
    """The proxy fo ObjectStructInfo.

    Parameters
    ----------
    values : Optional[List[PrimExpr]]
       The symbolic shape values if known.

    ndim : Optional[int]
       The size of the shape.
    """

    def __init__(self) -> None:
        pass

    def get_symbolic_vars(self) -> Set[str]:
        return set()

    def as_struct_info(self, dict_globals: Optional[Dict[str, Any]] = None) -> ShapeStructInfo:
        return ObjectStructInfo()


def Object() -> ObjectProxy:
    return ObjectProxy()


################################ R.Prim ################################


class PrimProxy(StructInfoProxy):
    dtype: str
    """The type of shape values.

    Parameters
    ----------
    dtype : str
       The data type.
    """

    def __init__(self, dtype: str) -> None:
        self.dtype = dtype

    def get_symbolic_vars(self) -> Set[str]:
        return set()

    def as_struct_info(self, dict_globals: Optional[Dict[str, Any]] = None) -> ShapeStructInfo:
        return PrimStructInfo(self.dtype)


def Prim(dtype: str) -> PrimProxy:
    return PrimProxy(dtype)


############################ R.match_cast #############################
class MatchCastPair:
    value: Expr
    struct_info: StructInfo

    def __init__(self, value: Expr, struct_info: StructInfo) -> None:
        self.value = value
        self.struct_info = struct_info


def match_cast(value: Expr, struct_info: StructInfo):
    if value is None:
        raise ValueError("value of match_cast cannot be None")
    if struct_info is None:
        raise ValueError("struct_info of match_cast cannot be None")
    return MatchCastPair(value, struct_info)
