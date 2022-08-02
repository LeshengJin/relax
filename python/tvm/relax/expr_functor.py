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
# pylint: disable=no-else-return, unidiomatic-typecheck, invalid-name, arguments-differ
"""The expression functor of Relax."""
from typing import Optional, Callable

import tvm
from tvm.runtime import Object
from tvm.ir import Op
from tvm.meta_schedule.utils import derived_object

from .expr import Type, Span, Expr
from .expr import Function, ExternFunc
from .expr import Constant, Var, DataflowVar
from .expr import ShapeExpr, RuntimeDepShape
from .expr import GlobalVar, SeqExpr, Tuple
from .expr import Call, If, TupleGetItem
from .expr import Binding, MatchShape, VarBinding
from .expr import BindingBlock, DataflowBlock
from ..relay import Id
from .block_builder import BlockBuilder
from . import _ffi_api

visitor = derived_object
"""
A decorator to wrap user-customized PyExprVisitor as TVM object _PyExprVisitor.

Parameters
----------
visitor_cls : PyExprVisitor
    The user-customized PyExprVisitor.

Returns
-------
cls : _PyExprVisitor
    The decorated TVM object _PyExprVisitor(ExprVisitor on the C++ side).

Example
-------
.. code-block:: python

    @relax.expr_functor.visitor
    class MyExprVisitor(PyExprVisitor):
        # customize visit function
        def visit_call_(self, op: Call) -> None:
            # just for demo purposes
            ...
    # myvisitor is now a special visitor that visit every Call with
    # user-customized visit_call_
    myvisitor = MyExprVisitor()
    # apply myvisitor to Expr/Binding/BindingBlock/VarDef
    myvisitor.visit_expr(expr)
    myvisitor.visit_binding(binding)
    myvisitor.visit_binding_block(bindingblock)
    myvisitor.visit_var_def(var)
"""

mutator = derived_object
"""
A decorator to wrap user-customized PyExprMutator as TVM object _PyExprMutator.
Note:  Cannot override visit function and post-order rewrite at the same time.

Parameters
----------
mutator_cls : PyExprMutator
    The user-customized PyExprMutator.

Returns
-------
cls : _PyExprMutator
    The decorated TVM object _PyExprMutator(ExprMutator on the C++ side).

Example
-------
.. code-block:: python

    @relax.expr_functor.mutator
    class MyExprMutator(PyExprMutator):
        # customize rewrite function
        def visit_tuple_(self, op: Tuple) -> Expr:
            # just for demo purposes
            ...

        # customize post-order rewrite function
        def rewrite_var_post_order(self, op: Expr) -> Expr:
            # just for demo purposes
            ...

    # mymutator is now a special mutator that rewrite every Tuple with
    # user-customized visit_tuple_, and rewrite every Var with user-customized
    # rewrite_var_post_order in the post order.
    mymutator = MyExprMutator()
    # apply mymutator to Expr/Binding/BindingBlock/VarDef
    mymutator.visit_expr(expr)
    mymutator.visit_binding(binding)
    mymutator.visit_binding_block(bindingblock)
    mymutator.visit_var_def(var)
    # Note: In this case, we cannot override rewrite_tuple_post_order in MyExprMutator.
"""


@tvm._ffi.register_object("expr_functor.PyExprVisitor")
class _PyExprVisitor(Object):
    """
    A TVM object to support customization of ExprVisitor on the python side.
    This is the decorated result returned from visitor decorator.

    WARNING: This is NOT the user facing class for method overwriting inheritance.

    See also: visitor, PyExprVisitor
    """

    def __init__(
        self,
        f_visit_expr: Callable = None,
        f_visit_constant_: Callable = None,
        f_visit_tuple_: Callable = None,
        f_visit_var_: Callable = None,
        f_visit_dataflow_var_: Callable = None,
        f_visit_shape_expr_: Callable = None,
        f_visit_runtime_dep_shape_: Callable = None,
        f_visit_extern_func_: Callable = None,
        f_visit_global_var_: Callable = None,
        f_visit_function_: Callable = None,
        f_visit_call_: Callable = None,
        f_visit_seq_expr_: Callable = None,
        f_visit_if_: Callable = None,
        f_visit_op_: Callable = None,
        f_visit_tuple_getitem_: Callable = None,
        f_visit_binding: Callable = None,
        f_visit_var_binding_: Callable = None,
        f_visit_match_shape_: Callable = None,
        f_visit_binding_block: Callable = None,
        f_visit_binding_block_: Callable = None,
        f_visit_dataflow_block_: Callable = None,
        f_visit_var_def: Callable = None,
        f_visit_var_def_: Callable = None,
        f_visit_dataflow_var_def_: Callable = None,
        f_visit_type: Callable = None,
        f_visit_span: Callable = None,
    ) -> None:
        """Constructor."""

        self.__init_handle_by_constructor__(
            _ffi_api.MakePyExprVisitor,
            f_visit_expr,
            f_visit_constant_,
            f_visit_tuple_,
            f_visit_var_,
            f_visit_dataflow_var_,
            f_visit_shape_expr_,
            f_visit_runtime_dep_shape_,
            f_visit_extern_func_,
            f_visit_global_var_,
            f_visit_function_,
            f_visit_call_,
            f_visit_seq_expr_,
            f_visit_if_,
            f_visit_op_,
            f_visit_tuple_getitem_,
            f_visit_binding,
            f_visit_var_binding_,
            f_visit_match_shape_,
            f_visit_binding_block,
            f_visit_binding_block_,
            f_visit_dataflow_block_,
            f_visit_var_def,
            f_visit_var_def_,
            f_visit_dataflow_var_def_,
            f_visit_type,
            f_visit_span,
        )

    def visit_expr(self, expr: Expr) -> None:
        """Generic dispatcher for Expr.

        Parameters
        ----------
        expr : Expr
            The expr to be visited.
        """
        return _ffi_api.PyExprVisitorVisitExpr(self, expr)

    def visit_binding(self, binding: Binding) -> None:
        """Generic dispatcher for Binding.

        Parameters
        ----------
        binding : Binding
            The binding to be visited.
        """
        return _ffi_api.PyExprVisitorVisitBinding(self, binding)

    def visit_binding_block(self, block: BindingBlock) -> None:
        """Generic dispatcher for BindingBlock.

        Parameters
        ----------
        block : BindingBlock
            The block to be visited.
        """
        return _ffi_api.PyExprVisitorVisitBindingBlock(self, block)

    def visit_var_def(self, var: Var) -> None:
        """Generic dispatcher for visiting the var definition site.
        Note that visit_var_() will only visit the usage site of an Var.

        Parameters
        ----------
        var : Var
            The var to be visited.
        """
        return _ffi_api.PyExprVisitorVisitVarDef(self, var)


class PyExprVisitor:
    """
    An abstract ExprVisitor with customized methods on the python-side.
    This is the user facing class for method overwriting inheritance.
    _tvm_metadata discribes the class to inherit("cls"), the methods
    that users can overwrite("methods").

    Note: @relax.expr_functor.visitor is required for proper usage of any inherited class.

    See also: visitor, _PyExprVisitor

    Example:
        @relax.expr_functor.visitor
        def MyExprVisitor(PyExprVisitor):
            ...
    """

    _tvm_metadata = {
        "cls": _PyExprVisitor,
        "methods": [
            "visit_expr",
            "visit_constant_",
            "visit_tuple_",
            "visit_var_",
            "visit_dataflow_var_",
            "visit_shape_expr_",
            "visit_runtime_dep_shape_",
            "visit_extern_func_",
            "visit_global_var_",
            "visit_function_",
            "visit_call_",
            "visit_seq_expr_",
            "visit_if_",
            "visit_op_",
            "visit_tuple_getitem_",
            "visit_binding",
            "visit_var_binding_",
            "visit_match_shape_",
            "visit_binding_block",
            "visit_binding_block_",
            "visit_dataflow_block_",
            "visit_var_def",
            "visit_var_def_",
            "visit_dataflow_var_def_",
            "visit_type",
            "visit_span",
        ],
    }

    def visit_expr(self, expr: Expr) -> None:
        """Generic dispatcher for Expr.
        Users can customized this function to overwrite VisitExpr(const Expr& expr) on the C++ side.

        Parameters
        ----------
        expr : Expr
            The expr to be visited.
        """
        # Using self._outer() to ref _PyExprVisitor
        return _ffi_api.PyExprVisitorVisitExpr(self._outer(), expr)

    def visit_binding(self, binding: Binding) -> None:
        """Generic dispatcher for Binding.
        Users can customized this function to overwrite VisitBinding(const Binding& binding)
        on the C++ side.

        Parameters
        ----------
        binding : Binding
            The binding to be visited.
        """
        # Using self._outer() to ref _PyExprVisitor
        return _ffi_api.PyExprVisitorVisitBinding(self._outer(), binding)

    def visit_binding_block(self, block: BindingBlock) -> None:
        """Generic dispatcher for BindingBlock.
        Users can customized this function to overwrite VisitBindingBlock(const BindingBlock& block)
        on the C++ side.

        Parameters
        ----------
        block : BindingBlock
            The block to be visited.
        """
        # Using self._outer() to ref _PyExprVisitor
        return _ffi_api.PyExprVisitorVisitBindingBlock(self._outer(), block)

    def visit_var_def(self, var: Var) -> None:
        """Generic dispatcher for visiting the var definition site.
        Users can customized this function to overwrite VisitVarDef(const Var& var) on the C++ side.
        Note that visit_var_() will only visit the usage site of an Var.

        Parameters
        ----------
        var : Var
            The var to be visited.
        """
        # Using self._outer() to ref _PyExprVisitor
        return _ffi_api.PyExprVisitorVisitVarDef(self._outer(), var)

    def visit_constant_(self, op: Constant) -> None:
        """Visit Constant.
        Users can customized this function to overwrite VisitExpr_(const ConstantNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Constant
            The Constant to be visited.
        """
        raise NotImplementedError

    def visit_tuple_(self, op: Tuple) -> None:
        """Visit Tuple.
        Users can customized this function to overwrite VisitExpr_(const TupleNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Tuple
            The Tuple to be visited.
        """
        raise NotImplementedError

    def visit_var_(self, op: Var) -> None:
        """Visit Var.
        Users can customized this function to overwrite VisitExpr_(const VarNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Var
            The Var to be visited.
        """
        raise NotImplementedError

    def visit_dataflow_var_(self, op: DataflowVar) -> None:
        """Visit DataflowVar.
        Users can customized this function to overwrite VisitExpr_(const DataflowVarNode* op)
        on the C++ side.

        Parameters
        ----------
        op : DataflowVar
            The DataflowVar to be visited.
        """
        raise NotImplementedError

    def visit_shape_expr_(self, op: ShapeExpr) -> None:
        """Visit ShapeExpr.
        Users can customized this function to overwrite VisitExpr_(const ShapeExprNode* op)
        on the C++ side.

        Parameters
        ----------
        op : ShapeExpr
            The ShapeExpr to be visited.
        """
        raise NotImplementedError

    def visit_runtime_dep_shape_(self, op: RuntimeDepShape) -> None:
        """Visit RuntimeDepShape.
        Users can customized this function to overwrite VisitExpr_(const RuntimeDepShapeNode* op)
        on the C++ side.

        Parameters
        ----------
        op : RuntimeDepShape
            The RuntimeDepShape to be visited.
        """
        raise NotImplementedError

    def visit_extern_func_(self, op: ExternFunc) -> None:
        """Visit ExternFunc.
        Users can customized this function to overwrite VisitExpr_(const ExternFuncNode* op)
        on the C++ side.

        Parameters
        ----------
        op : ExternFunc
            The ExternFunc to be visited.
        """
        raise NotImplementedError

    def visit_global_var_(self, op: GlobalVar) -> None:
        """Visit GlobalVar.
        Users can customized this function to overwrite VisitExpr_(const GlobalVarNode* op)
        on the C++ side.

        Parameters
        ----------
        op : GlobalVar
            The GlobalVar to be visited.
        """
        raise NotImplementedError

    def visit_function_(self, op: Function) -> None:
        """Visit Function.
        Users can customized this function to overwrite VisitExpr_(const FunctionNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Function
            The Function to be visited.
        """
        raise NotImplementedError

    def visit_call_(self, op: Call) -> None:
        """Visit Call.
        Users can customized this function to overwrite VisitExpr_(const CallNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Call
            The Call to be visited.
        """
        raise NotImplementedError

    def visit_seq_expr_(self, op: SeqExpr) -> None:
        """Visit SeqExpr.
        Users can customized this function to overwrite VisitExpr_(const SeqExprNode* op)
        on the C++ side.

        Parameters
        ----------
        op : SeqExpr
            The SeqExpr to be visited.
        """
        raise NotImplementedError

    def visit_if_(self, op: If) -> None:
        """Visit If.
        Users can customized this function to overwrite VisitExpr_(const IfNode* op)
        on the C++ side.

        Parameters
        ----------
        op : If
            The If to be visited.
        """
        raise NotImplementedError

    def visit_op_(self, op: Op) -> None:
        """Visit Op.
        Users can customized this function to overwrite VisitExpr_(const OpNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Op
            The Op to be visited.
        """
        raise NotImplementedError

    def visit_tuple_getitem_(self, op: TupleGetItem) -> None:
        """Visit TupleGetItem.
        Users can customized this function to overwrite VisitExpr_(const TupleGetItemNode* op)
        on the C++ side.

        Parameters
        ----------
        op : TupleGetItem
            The TupleGetItem to be visited.
        """
        raise NotImplementedError

    def visit_var_binding_(self, binding: VarBinding) -> None:
        """Visit VarBinding.
        Users can customized this function to overwrite VisitBinding_(const VarBindingNode* binding)
        on the C++ side.

        Parameters
        ----------
        binding : VarBinding
            The VarBinding to be visited.
        """
        raise NotImplementedError

    def visit_match_shape_(self, binding: MatchShape) -> None:
        """Visit MatchShape.
        Users can customized this function to overwrite VisitBinding_(const MatchShapeNode* binding)
        on the C++ side.

        Parameters
        ----------
        binding : MatchShape
            The MatchShape to be visited.
        """
        raise NotImplementedError

    def visit_binding_block_(self, block: BindingBlock) -> None:
        """Visit BindingBlock.
        Users can customized this function to overwrite VisitBindingBlock_(const BindingBlockNode*
        block) on the C++ side.

        Parameters
        ----------
        block : BindingBlock
            The BindingBlock to be visited.
        """
        raise NotImplementedError

    def visit_dataflow_block_(self, block: DataflowBlock) -> None:
        """Visit DataflowBlock.
        Users can customized this function to overwrite VisitBindingBlock_(const DataflowBlockNode*
        block) on the C++ side.

        Parameters
        ----------
        block : DataflowBlock
            The DataflowBlock to be visited.
        """
        raise NotImplementedError

    def visit_var_def_(self, var: Var) -> None:
        """Visit the Var definition site.
        Users can customized this function to overwrite VisitVarDef_(const VarNode* var)
        on the C++ side.

        Parameters
        ----------
        var : Var
            The Var to be visited.
        """
        raise NotImplementedError

    def visit_dataflow_var_def_(self, var: DataflowVar) -> None:
        """Visit the DataflowVar definition site.
        Users can customized this function to overwrite VisitVarDef_(const DataflowVarNode* var)
        on the C++ side.

        Parameters
        ----------
        var : DataflowVar
            The DataflowVar to be visited.
        """
        raise NotImplementedError

    def visit_type(self, t: Type) -> None:
        """Visit Type.
        Users can customized this function to overwrite VisitType(const Type& t) on the C++ side.

        Parameters
        ----------
        t : Type
            The Type to be visited.
        """
        raise NotImplementedError

    def visit_span(self, span: Span) -> None:
        """Visit Span.
        Users can customized this function to overwrite VisitSpan(const Span& span) on the C++ side.

        Parameters
        ----------
        span : Span
            The Span to be visited.
        """
        raise NotImplementedError


@tvm._ffi.register_object("expr_functor.PyExprMutator")
class _PyExprMutator(Object):
    """
    A TVM object to support customization of ExprMutator on the python side.
    This is the decorated result returned from mutator decorator.

    WARNING: This is NOT the user facing class for method overwriting inheritance.

    See also: mutator, PyExprmutator
    """

    def __init__(
        self,
        builder: BlockBuilder = None,
        f_visit_expr: Callable = None,
        f_visit_constant_: Callable = None,
        f_visit_tuple_: Callable = None,
        f_visit_var_: Callable = None,
        f_visit_dataflow_var_: Callable = None,
        f_visit_shape_expr_: Callable = None,
        f_visit_runtime_dep_shape_: Callable = None,
        f_visit_extern_func_: Callable = None,
        f_visit_global_var_: Callable = None,
        f_visit_function_: Callable = None,
        f_visit_call_: Callable = None,
        f_visit_seq_expr_: Callable = None,
        f_visit_if_: Callable = None,
        f_visit_op_: Callable = None,
        f_visit_tuple_getitem_: Callable = None,
        f_visit_binding: Callable = None,
        f_visit_var_binding_: Callable = None,
        f_visit_match_shape_: Callable = None,
        f_visit_binding_block: Callable = None,
        f_visit_binding_block_: Callable = None,
        f_visit_dataflow_block_: Callable = None,
        f_visit_var_def: Callable = None,
        f_visit_var_def_: Callable = None,
        f_visit_dataflow_var_def_: Callable = None,
        f_visit_type: Callable = None,
        f_visit_span: Callable = None,
        f_rewrite_constant_post_order: Callable = None,
        f_rewrite_tuple_post_order: Callable = None,
        f_rewrite_var_post_order: Callable = None,
        f_rewrite_dataflow_var_post_order: Callable = None,
        f_rewrite_shape_expr_post_order: Callable = None,
        f_rewrite_runtime_dep_shape_post_order: Callable = None,
        f_rewrite_extern_func_post_order: Callable = None,
        f_rewrite_global_var_post_order: Callable = None,
        f_rewrite_function_post_order: Callable = None,
        f_rewrite_call_post_order: Callable = None,
        f_rewrite_seq_expr_post_order: Callable = None,
        f_rewrite_if_post_order: Callable = None,
        f_rewrite_op_post_order: Callable = None,
        f_rewrite_tuple_getitem_post_order: Callable = None,
    ) -> None:
        """Constructor."""

        self.__init_handle_by_constructor__(
            _ffi_api.MakePyExprMutator,
            builder,
            f_visit_expr,
            f_visit_constant_,
            f_visit_tuple_,
            f_visit_var_,
            f_visit_dataflow_var_,
            f_visit_shape_expr_,
            f_visit_runtime_dep_shape_,
            f_visit_extern_func_,
            f_visit_global_var_,
            f_visit_function_,
            f_visit_call_,
            f_visit_seq_expr_,
            f_visit_if_,
            f_visit_op_,
            f_visit_tuple_getitem_,
            f_visit_binding,
            f_visit_var_binding_,
            f_visit_match_shape_,
            f_visit_binding_block,
            f_visit_binding_block_,
            f_visit_dataflow_block_,
            f_visit_var_def,
            f_visit_var_def_,
            f_visit_dataflow_var_def_,
            f_visit_type,
            f_visit_span,
            f_rewrite_constant_post_order,
            f_rewrite_tuple_post_order,
            f_rewrite_var_post_order,
            f_rewrite_dataflow_var_post_order,
            f_rewrite_shape_expr_post_order,
            f_rewrite_runtime_dep_shape_post_order,
            f_rewrite_extern_func_post_order,
            f_rewrite_global_var_post_order,
            f_rewrite_function_post_order,
            f_rewrite_call_post_order,
            f_rewrite_seq_expr_post_order,
            f_rewrite_if_post_order,
            f_rewrite_op_post_order,
            f_rewrite_tuple_getitem_post_order,
        )

    def visit_expr(self, expr: Expr) -> Expr:
        """Generic dispatcher for Expr.

        Parameters
        ----------
        expr : Expr
            The expr to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation.
        """
        return _ffi_api.PyExprMutatorVisitExpr(self, expr)

    def visit_binding(self, binding: Binding) -> None:
        """Generic dispatcher for Binding.

        Parameters
        ----------
        binding : Binding
            The binding to be visited.
        """
        return _ffi_api.PyExprMutatorVisitBinding(self, binding)

    def visit_binding_block(self, block: BindingBlock) -> BindingBlock:
        """Generic dispatcher for BindingBlock.

        Parameters
        ----------
        block : BindingBlock
            The block to be visited.

        Returns
        -------
        result : BindingBlock
            The binding block after transformation.
        """
        return _ffi_api.PyExprMutatorVisitBindingBlock(self, block)

    def visit_var_def(self, var: Var) -> Var:
        """Generic dispatcher for visiting the var definition site.
        Note that visit_var_() will only visit the usage site of an Var.

        Parameters
        ----------
        var : Var
            The var to be visited.

        Returns
        -------
        result : Var
            The var after post-order rewritten.
        """
        return _ffi_api.PyExprMutatorVisitVarDef(self, var)


class PyExprMutator:
    """
    An abstract ExprMutator with customized methods on the python-side.
    This is the user facing class for method overwriting inheritance.
    _tvm_metadata discribes the class to inherit("cls"), the methods that users can
    overwrite("methods"), the constructor's parameters("fields")

    Note: @relax.expr_functor.mutator is required for proper usage of any inherited class.

    See also: visitor, _PyExprVisitor

    Example:
        @relax.expr_functor.mutator
        def MyExprMutator(PyExprMutator):
            ...
    """

    _tvm_metadata = {
        "cls": _PyExprMutator,
        "fields": ["builder_"],
        "methods": [
            "visit_expr",
            "visit_constant_",
            "visit_tuple_",
            "visit_var_",
            "visit_dataflow_var_",
            "visit_shape_expr_",
            "visit_runtime_dep_shape_",
            "visit_extern_func_",
            "visit_global_var_",
            "visit_function_",
            "visit_call_",
            "visit_seq_expr_",
            "visit_if_",
            "visit_op_",
            "visit_tuple_getitem_",
            "visit_binding",
            "visit_var_binding_",
            "visit_match_shape_",
            "visit_binding_block",
            "visit_binding_block_",
            "visit_dataflow_block_",
            "visit_var_def",
            "visit_var_def_",
            "visit_dataflow_var_def_",
            "visit_type",
            "visit_span",
            "rewrite_constant_post_order",
            "rewrite_tuple_post_order",
            "rewrite_var_post_order",
            "rewrite_dataflow_var_post_order",
            "rewrite_shape_expr_post_order",
            "rewrite_runtime_dep_shape_post_order",
            "rewrite_extern_func_post_order",
            "rewrite_global_var_post_order",
            "rewrite_function_post_order",
            "rewrite_call_post_order",
            "rewrite_seq_expr_post_order",
            "rewrite_if_post_order",
            "rewrite_op_post_order",
            "rewrite_tuple_getitem_post_order",
        ],
    }

    def __init__(self) -> None:
        """Constructor"""
        self.builder_ = BlockBuilder()

    def visit_expr(self, expr: Expr) -> Expr:
        """Generic dispatcher for Expr.
        Users can customized this function to overwrite VisitExpr(const Expr& expr) on the C++ side.

        Parameters
        ----------
        expr : Expr
            The expr to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation.
        """
        # Using self._outer() to ref _PyExprMutator
        return _ffi_api.PyExprMutatorVisitExpr(self._outer(), expr)

    def visit_binding(self, binding: Binding) -> None:
        """Generic dispatcher for Binding.
        Users can customized this function to overwrite VisitBinding(const Binding& binding)
        on the C++ side.

        Parameters
        ----------
        binding : Binding
            The binding to be visited.
        """
        # Using self._outer() to ref _PyExprMutator
        return _ffi_api.PyExprMutatorVisitBinding(self._outer(), binding)

    def visit_binding_block(self, block: BindingBlock) -> BindingBlock:
        """Generic dispatcher for BindingBlock.
        Users can customized this function to overwrite VisitBindingBlock(const BindingBlock& block)
        on the C++ side.

        Parameters
        ----------
        block : BindingBlock
            The block to be visited.

        Returns
        -------
        result : BindingBlock
            The binding block after transformation.
        """
        # Using self._outer() to ref _PyExprMutator
        return _ffi_api.PyExprMutatorVisitBindingBlock(self._outer(), block)

    def visit_var_def(self, var: Var) -> Var:
        """Generic dispatcher for visiting the var definition site.
        Users can customized this function to overwrite VisitVarDef(const Var& var) on the C++ side.
        Note that visit_var_() will only visit the usage site of an Var.

        Parameters
        ----------
        var : Var
            The var to be visited.

        Returns
        -------
        result: Var
            The var after post-order rewritten.
        """
        # Using self._outer() to ref _PyExprMutator
        return _ffi_api.PyExprMutatorVisitVarDef(self._outer(), var)

    def visit_constant_(self, op: Constant) -> Expr:
        """Visit Constant.
        Users can customized this function to overwrite VisitExpr_(const ConstantNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Constant
            The Constant to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_tuple_(self, op: Tuple) -> Expr:
        """Visit Tuple.
        Users can customized this function to overwrite VisitExpr_(const TupleNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Tuple
            The Tuple to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_var_(self, op: Var) -> Expr:
        """Visit Var.
        Users can customized this function to overwrite VisitExpr_(const VarNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Var
            The Var to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_dataflow_var_(self, op: DataflowVar) -> Expr:
        """Visit DataflowVar.
        Users can customized this function to overwrite VisitExpr_(const DataflowVarNode* op)
        on the C++ side.

        Parameters
        ----------
        op : DataflowVar
            The DataflowVar to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_shape_expr_(self, op: ShapeExpr) -> Expr:
        """Visit ShapeExpr.
        Users can customized this function to overwrite VisitExpr_(const ShapeExprNode* op)
        on the C++ side.

        Parameters
        ----------
        op : ShapeExpr
            The ShapeExpr to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_runtime_dep_shape_(self, op: RuntimeDepShape) -> Expr:
        """Visit RuntimeDepShape.
        Users can customized this function to overwrite VisitExpr_(const RuntimeDepShapeNode* op)
        on the C++ side.

        Parameters
        ----------
        op : RuntimeDepShape
            The RuntimeDepShape to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_extern_func_(self, op: ExternFunc) -> Expr:
        """Visit ExternFunc.
        Users can customized this function to overwrite VisitExpr_(const ExternFuncNode* op)
        on the C++ side.

        Parameters
        ----------
        op : ExternFunc
            The ExternFunc to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_global_var_(self, op: GlobalVar) -> Expr:
        """Visit GlobalVar.
        Users can customized this function to overwrite VisitExpr_(const GlobalVarNode* op)
        on the C++ side.

        Parameters
        ----------
        op : GlobalVar
            The GlobalVar to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_function_(self, op: Function) -> Expr:
        """Visit Function.
        Users can customized this function to overwrite VisitExpr_(const FunctionNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Function
            The Function to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_call_(self, op: Call) -> Expr:
        """Visit Call.
        Users can customized this function to overwrite VisitExpr_(const CallNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Call
            The Call to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_seq_expr_(self, op: SeqExpr) -> Expr:
        """Visit SeqExpr.
        Users can customized this function to overwrite VisitExpr_(const SeqExprNode* op)
        on the C++ side.

        Parameters
        ----------
        op : SeqExpr
            The SeqExpr to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_if_(self, op: If) -> Expr:
        """Visit If.
        Users can customized this function to overwrite VisitExpr_(const IfNode* op)
        on the C++ side.

        Parameters
        ----------
        op : If
            The If to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_op_(self, op: Op) -> Expr:
        """Visit Op.
        Users can customized this function to overwrite VisitExpr_(const OpNode* op)
        on the C++ side.

        Parameters
        ----------
        op : Op
            The Op to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_tuple_getitem_(self, op: TupleGetItem) -> Expr:
        """Visit TupleGetItem.
        Users can customized this function to overwrite VisitExpr_(const TupleGetItemNode* op)
        on the C++ side.

        Parameters
        ----------
        op : TupleGetItem
            The TupleGetItem to be visited.

        Returns
        -------
        result : Expr
            The Expr after transformation
        """
        raise NotImplementedError

    def visit_var_binding_(self, binding: VarBinding) -> None:
        """Visit VarBinding.
        Users can customized this function to overwrite VisitBinding_(const VarBindingNode* binding)
        on the C++ side.

        Parameters
        ----------
        binding : VarBinding
            The VarBinding to be visited.
        """
        raise NotImplementedError

    def visit_match_shape_(self, binding: MatchShape) -> None:
        """Visit MatchShape.
        Users can customized this function to overwrite VisitBinding_(const MatchShapeNode* binding)
        on the C++ side.

        Parameters
        ----------
        binding : MatchShape
            The MatchShape to be visited.
        """
        raise NotImplementedError

    def visit_binding_block_(self, block: BindingBlock) -> BindingBlock:
        """Visit BindingBlock.
        Users can customized this function to overwrite VisitBindingBlock_(const BindingBlockNode*
        block) on the C++ side.

        Parameters
        ----------
        block : BindingBlock
            The BindingBlock to be visited.

        Returns
        -------
        result : BindingBlock
            The binding block after transformation
        """
        raise NotImplementedError

    def visit_dataflow_block_(self, block: DataflowBlock) -> BindingBlock:
        """Visit DataflowBlock.
        Users can customized this function to overwrite VisitBindingBlock_(const DataflowBlockNode*
        block) on the C++ side.

        Parameters
        ----------
        block : DataflowBlock
            The DataflowBlock to be visited.

        Returns
        -------
        result : BindingBlock
            The binding block after transformation
        """
        raise NotImplementedError

    def visit_var_def_(self, var: Var) -> Var:
        """Visit the Var definition site.
        Users can customized this function to overwrite VisitVarDef_(const VarNode* var)
        on the C++ side.

        Parameters
        ----------
        var : Var
            The Var to be visited.

        Returns
        -------
        result : Var
            The var after post-order rewritten.
        """
        raise NotImplementedError

    def visit_dataflow_var_def_(self, var: DataflowVar) -> Var:
        """Visit the DataflowVar definition site.
        Users can customized this function to overwrite VisitVarDef_(const DataflowVarNode* var)
        on the C++ side.

        Parameters
        ----------
        var : DataflowVar
            The DataflowVar to be visited.

        Returns
        -------
        result : Var
            The var after post-order rewritten.
        """
        raise NotImplementedError

    def visit_type(self, t: Type) -> Type:
        """Visit Type.
        Users can customized this function to overwrite VisitType(const Type& t) on the C++ side.

        Parameters
        ----------
        t : Type
            The Type to be visited.

        Returns
        -------
        result : Type
            The type after transformation.
        """
        raise NotImplementedError

    def visit_span(self, span: Span) -> Span:
        """Visit Span.
        Users can customized this function to overwrite VisitSpan(const Span& span) on the C++ side.

        Parameters
        ----------
        span : Span
            The Span to be visited.

        Returns
        -------
        result : Span
            The span after transformation.
        """
        raise NotImplementedError

    def rewrite_constant_post_order(self, op: Constant) -> Expr:
        """Rewrite Constant after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const ConstantNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : Constant
            The Constant to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_tuple_post_order(self, op: Tuple) -> Expr:
        """Rewrite Tuple after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const TupleNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : Tuple
            The Tuple to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_var_post_order(self, op: Var) -> Expr:
        """Rewrite Var after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const VarNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : Var
            The Var to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_dataflow_var_post_order(self, op: DataflowVar) -> Expr:
        """Rewrite DataflowVar after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const DataflowVarNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : DataflowVar
            The DataflowVar to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_shape_expr_post_order(self, op: ShapeExpr) -> Expr:
        """Rewrite ShapeExpr after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const ShapeExprNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : ShapeExpr
            The ShapeExpr to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_runtime_dep_shape_post_order(self, op: RuntimeDepShape) -> Expr:
        """Rewrite RuntimeDepShape after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const RuntimeDepShapeNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : RuntimeDepShape
            The RuntimeDepShape to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_extern_func_post_order(self, op: ExternFunc) -> Expr:
        """Rewrite ExternFunc after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const ExternFuncNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : ExternFunc
            The ExternFunc to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_global_var_post_order(self, op: GlobalVar) -> Expr:
        """Rewrite GlobalVar after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const GlobalVarNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : GlobalVar
            The GlobalVar to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_function_post_order(self, op: Function) -> Expr:
        """Rewrite Function after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const FunctionNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : Function
            The Function to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_call_post_order(self, op: Call) -> Expr:
        """Rewrite Call after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const CallNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : Call
            The Call to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_seq_expr_post_order(self, op: SeqExpr) -> Expr:
        """Rewrite SeqExpr after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const SeqExprNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : SeqExpr
            The SeqExpr to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_if_post_order(self, op: If) -> Expr:
        """Rewrite If after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const IfNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : If
            The If to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_op_post_order(self, op: Op) -> Expr:
        """Rewrite Op after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const OpNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : Op
            The Op to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def rewrite_tuple_getitem_post_order(self, op: TupleGetItem) -> Expr:
        """Rewrite TupleGetItem after post-order visit the node.
        The customization will work as
        .. code-block:: c++
            Expr VisitExpr_(const TupleGetItemNode* op){
                Expr expr = self->VisitExprPostOrder_(op);
                expr = USER_CUSTOMIZED_REWRITE_FUNC(expr);
                return expr;
            }

        Parameters
        ----------
        op : TupleGetItem
            The TupleGetItem to be rewritten, also the return value from the post-order visit.

        Returns
        -------
        result : Expr
            The Expr after rewritten.
        """
        raise NotImplementedError

    def set_var_remap(self, vid: Id, var: Var) -> None:
        """Remap a var to a new var in use-site.

        Parameters
        ----------
        vid : Id
            The vid of the old var.
        var : Var
            The new var.
        """
        # Using self._outer() to ref _PyExprMutator
        return _ffi_api.PyExprMutatorSetVarRemap(self._outer(), vid, var)

    def get_var_remap(self, vid: Id) -> Var:
        """Remap a var to a new var in use-site.

        Parameters
        ----------
        vid : Id
            The vid of the old var

        Returns
        -------
        var : Var
            The remapped var.
        """
        # Using self._outer() to ref _PyExprMutator
        return _ffi_api.PyExprMutatorGetVarRemap(self._outer(), vid)

    def visit_with_new_scope(self, expr: Expr) -> Expr:
        """Rewrite the expr with a new scope, used in a Function's body and the branches of If.

        Parameters
        ----------
        expr : Expr
            The expr to be visited.

        Returns
        -------
        var : Var
            The expr after visiting.
        """
        # Using self._outer() to ref _PyExprMutator
        return _ffi_api.PyExprMutatorVisitWithNewScope(self._outer(), expr)

    def lookup_binding(self, var: Var) -> Optional[Expr]:
        """Look up the value bound to a variable.
        Note: For function parameters, this function returns NullOpt.

        Parameters
        ----------
        var : Var
            The var to be looked up.

        Returns
        -------
        var : Var
            The value bound to the input var.
        """
        # Using self._outer() to ref _PyExprMutator
        return _ffi_api.PyExprMutatorLookupBinding(self._outer(), var)

    def with_shape_and_type(self, var: Var, shape: Optional[Object], t: Type) -> Var:
        """Create a new var with specified shape and type if the original var's shape or type does
        not match with the specified ones.

        Parameters
        ----------
        var : Var
            The var to be updated.
        shape : Optional[Object]
            The specified shape.
        t : Type
            The specified type.

        Returns
        -------
        var : Var
            The var filled with shape and type.
        """
        # Using self._outer() to ref _PyExprMutator
        return _ffi_api.PyExprMutatorWithShapeAndType(self._outer(), var, shape, t)
