/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

/*!
 * \file src/relax/block_builder.cc
 */

#include <tvm/arith/analyzer.h>
#include <tvm/relax/block_builder.h>
#include <tvm/relax/op_attr_types.h>
#include <tvm/relax/type.h>
#include <tvm/relay/op.h>

namespace tvm {
namespace relax {

TVM_REGISTER_NODE_TYPE(BlockBuilderNode);

BlockBuilderNode::~BlockBuilderNode() {
  if (!block_stack_.empty()) {
    LOG(WARNING) << "BlockBuilder destroyed with remaining blocks!";
  }
}

BlockBuilder BlockBuilderNode::Create() {
  BlockBuilder ret(make_object<BlockBuilderNode>());
  return ret;
}

void BlockBuilderNode::BeginDataflowBlock() { this->block_stack_.push({{}, true}); }

void BlockBuilderNode::BeginBindingBlock() { this->block_stack_.push({{}, false}); }

BindingBlock BlockBuilderNode::EndBlock() {
  BlockFrame* cur_block = CurrentBlock();
  BindingBlock ret = cur_block->is_dataflow ? DataflowBlock(cur_block->bindings)
                                            : BindingBlock(cur_block->bindings);
  block_stack_.pop();
  return ret;
}

Optional<RelayExpr> InferShape(const Call& call, DiagnosticContext diag_ctx) {
  auto op_map = Op::GetAttrMap<FInferShape>("FInferShape");
  if (call->op.as<OpNode>()) {
    Op op = Downcast<Op>(call->op);
    if (op_map.count(op)) {
      return op_map[op](call, diag_ctx);
    }
  }
  return NullOpt;
}

Type InferType(const Call& call, DiagnosticContext diag_ctx) {
  auto op_map = Op::GetAttrMap<FInferType>("FInferType");
  if (call->op.as<OpNode>()) {
    Op op = Downcast<Op>(call->op);
    if (op_map.count(op)) {
      return op_map[op](call, diag_ctx);
    }
  }
  return Type();
}

Var BlockBuilderNode::Emit(const Expr& expr, std::string name_hint) {
  return Emit(expr, CurrentBlock()->is_dataflow, name_hint);
}

Var BlockBuilderNode::Emit(const Expr& expr, bool is_dataflow, std::string name_hint) {
  BlockFrame* cur_block = CurrentBlock();

  if (name_hint.empty()) {
    name_hint = is_dataflow ? "lv" : "gv";
  }
  Id vid = Id(name_table_->GetUniqueName(name_hint));
  Var var = is_dataflow ? DataflowVar(vid, NullOpt, NullOpt) : Var(vid, NullOpt, NullOpt);

  // do eager inference for Calls
  if (const CallNode* call_node = expr.as<CallNode>()) {
    // TypeInference::InferCall(...)
    const Call& call = GetRef<Call>(call_node);

    Optional<Expr> inferred_shape = InferShape(call, this->diag_ctx_);
    Type inferred_type = InferType(call, this->diag_ctx_);

    var->shape_ = inferred_shape;
    var->checked_type_ = inferred_type;

    Call new_call = Call(call->op, call->args, call->attrs, call->type_args, call->span);
    new_call->checked_type_ = inferred_type;
    new_call->shape_ = inferred_shape;

    cur_block->bindings.push_back(VarBinding(var, new_call));
    this->var_map_[var->vid] = new_call;
  } else {
    cur_block->bindings.push_back(VarBinding(var, expr));
    this->var_map_[var->vid] = expr;
  }

  return var;
}

Var BlockBuilderNode::Emit(const VarBinding& binding) {
  BlockFrame* cur_block = CurrentBlock();
  if (cur_block->is_dataflow) {
    ICHECK(binding->var.as<DataflowVarNode>());
  }
  cur_block->bindings.push_back(binding);
  this->var_map_[binding->var->vid] = binding->value;
  return binding->var;
}

Var BlockBuilderNode::EmitMatchShape(const Expr& value, const Array<PrimExpr>& pattern, std::string name_hint) {
  BlockFrame* cur_block = CurrentBlock();

  if (name_hint.empty()) {
    name_hint = cur_block->is_dataflow ? "lv" : "gv";
  }
  Id vid = Id(name_table_->GetUniqueName(name_hint));
  Var var = cur_block->is_dataflow ? DataflowVar(vid, NullOpt, NullOpt) : Var(vid, NullOpt, NullOpt);

  if (value->checked_type().as<ShapeTypeNode>()) {
    var->checked_type_ = ShapeType(Span());
  } else if (const DynTensorTypeNode* tty = value->checked_type().as<DynTensorTypeNode>()) {
    ShapeExpr shape = ShapeExpr(pattern);
    var->shape_ = shape;
    DataType dtype = tty->dtype;
    var->checked_type_ = DynTensorType(pattern.size(), dtype);
  } else {
    this->diag_ctx_.EmitFatal(
        Diagnostic::Error(value->span)
        << "The value passed to EmitMatchShape must be of DynTensorType or ShapeType.");
  }

  MatchShape match_shape = MatchShape(value, pattern, var);
  cur_block->bindings.push_back(match_shape);
  return var;
}

Var BlockBuilderNode::EmitMatchShape(const MatchShape& binding) {
  BlockFrame* cur_block = CurrentBlock();
  if (cur_block->is_dataflow) {
    ICHECK(!binding->var.as<DataflowVarNode>()) << "cannot bind DataflowVar outside dataflow block.";
  }
  cur_block->bindings.push_back(binding);
  return binding->var;
}

// TODO(@altanh, @yuchen): EmitMatchShape(MatchSHape)

// Var BlockBuilderNode::Emit(const Var& var, const Call& call) {
//   BlockFrame* cur_block = CurrentBlock();
//   Expr normalized_call = Normalize(call);
//   // Reuse the input var if the shape and type of the call matches the var
//   if (CanProveShapeEqual(var->shape(), call->shape()) &&
//       StructuralEqual()(var->checked_type(), call->checked_type())) {
//     cur_block->bindings.push_back(VarBinding(var, normalized_call));
//     this->var_map_[var->vid] = normalized_call;
//     return var;
//   } else {
//     Var new_var = Var(var->vid, NullOpt, var->type_annotation);
//     if (normalized_call->shape_.defined()) {
//       new_var->shape_ = normalized_call->shape_;
//     }
//     new_var->checked_type_ = normalized_call->checked_type_;
//     cur_block->bindings.push_back(VarBinding(new_var, normalized_call));
//     this->var_map_[new_var->vid] = normalized_call;
//     return new_var;
//   }
// }

Var BlockBuilderNode::EmitOutput(const Expr& output, std::string name_hint) {
  BlockFrame* cur_block = CurrentBlock();

  ICHECK(cur_block->is_dataflow) << "EmitOutput has to be called inside dataflow block.";

  return Emit(output, false, name_hint);
}

Var BlockBuilderNode::EmitOutput(const VarBinding& binding) {
  BlockFrame* cur_block = CurrentBlock();

  ICHECK(cur_block->is_dataflow) << "EmitOutput has to be called inside dataflow block.";
  ICHECK(!binding->var.as<DataflowVarNode>()) << "EmitOutput can only emit Var bindings.";

  cur_block->bindings.push_back(binding);
  this->var_map_[binding->var->vid] = binding->value;
  return binding->var;
}

// Var BlockBuilderNode::EmitOutput(const Expr& output) {
//   BlockFrame* cur_block = CurrentBlock();

//   if (!cur_block->is_dataflow) {
//     this->diag_ctx_.EmitFatal(Diagnostic::Error(output->span)
//                               << "EmitOutput has to be called inside dataflow block.");
//   }

//   Var ret = Var(Id(name_table_->GetUniqueName("gv")), NullOpt, NullOpt);
//   ret->shape_ = output->shape_;
//   ret->checked_type_ = output->checked_type_;
//   cur_block->bindings.push_back(VarBinding(ret, output));
//   this->var_map_[ret->vid] = output;

//   return ret;
// }

Expr BlockBuilderNode::LookupVar(const Var& var) {
  auto it = this->var_map_.find(var->vid);
  if (it == this->var_map_.end()) {
    this->diag_ctx_.EmitFatal(Diagnostic::Error(var->span)
                              << "The var to be looked up is not in the binding table.");
  }
  return it->second;
}

bool BlockBuilderNode::CanProveShapeEqual(const Expr& lhs, const Expr& rhs) {
  if (lhs == rhs) {
    return true;
  }
  const auto* lhs_shape = lhs.as<ShapeExprNode>();
  const auto* rhs_shape = rhs.as<ShapeExprNode>();
  if (lhs_shape && rhs_shape) {
    size_t lhs_ndim = lhs_shape->values.size();
    size_t rhs_ndim = rhs_shape->values.size();
    if (lhs_ndim != rhs_ndim) {
      return false;
    }
    arith::Analyzer analyzer;
    for (size_t i = 0; i < lhs_ndim; ++i) {
      PrimExpr lhs_dim = lhs_shape->values[i];
      PrimExpr rhs_dim = rhs_shape->values[i];
      if (!analyzer.CanProveEqual(lhs_dim, rhs_dim)) {
        return false;
      }
    }
    return true;
  }
  return false;
}

// TODO(@altanh, @yuchen): emit expr in ssa form
Expr BlockBuilderNode::Normalize(const Expr& expr) {
  if (expr.as<CallNode>()) {
    Call call = Downcast<Call>(expr);
    // Shape inference
    auto inferred_shape = InferShape(call, this->diag_ctx_);
    if (inferred_shape.defined()) {
      if (auto* shape_expr = inferred_shape.value().as<ShapeExprNode>()) {
        call->shape_ = GetRef<Expr>(shape_expr);
      }
    }
    // Type inference
    auto inferred_type = InferType(call, this->diag_ctx_);
    call->checked_type_ = inferred_type;
    return call;
  }
  return expr;
}

BlockBuilderNode::BlockFrame* BlockBuilderNode::CurrentBlock() {
  ICHECK(!block_stack_.empty()) << "no block is being built";
  return &block_stack_.top();
}

BlockBuilder::BlockBuilder(std::shared_ptr<NameTable> name_table) {
  ObjectPtr<BlockBuilderNode> n = make_object<BlockBuilderNode>();
  n->name_table_ = name_table;
  data_ = std::move(n);
}

TVM_REGISTER_GLOBAL("relax.BlockBuilderCreate").set_body_typed(BlockBuilderNode::Create);

TVM_REGISTER_GLOBAL("relax.BlockBuilderBeginDataflowBlock")
    .set_body_typed([](BlockBuilder builder) { builder->BeginDataflowBlock(); });

TVM_REGISTER_GLOBAL("relax.BlockBuilderBeginBindingBlock").set_body_typed([](BlockBuilder builder) {
  builder->BeginBindingBlock();
});

TVM_REGISTER_GLOBAL("relax.BlockBuilderEndBlock").set_body_typed([](BlockBuilder builder) {
  return builder->EndBlock();
});

TVM_REGISTER_GLOBAL("relax.BlockBuilderEmit")
    .set_body_typed([](BlockBuilder builder, const Call& call) { return builder->Emit(call); });

TVM_REGISTER_GLOBAL("relax.BlockBuilderEmitMatchShape")
    .set_body_typed([](BlockBuilder builder, const Expr& value, const Array<PrimExpr>& pattern) {
      return builder->EmitMatchShape(value, pattern);
    });

TVM_REGISTER_GLOBAL("relax.BlockBuilderEmitOutput")
    .set_body_typed([](BlockBuilder builder, const Expr& output) {
      return builder->EmitOutput(output);
    });

TVM_REGISTER_GLOBAL("relax.BlockBuilderNormalize")
    .set_body_typed([](BlockBuilder builder, const Expr& expr) {
      return builder->Normalize(expr);
    });

}  // namespace relax
}  // namespace tvm
