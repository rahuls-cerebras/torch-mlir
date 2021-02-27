# -*- Python -*-
# This file is licensed under a pytorch-style license
# See frontends/pytorch/LICENSE for license information.

import typing

import torch
import torch_mlir

# RUN: %PYTHON %s | npcomp-opt | FileCheck %s

mb = torch_mlir.ModuleBuilder()


# Function names in the Torch compilation unit are systematic -- they
# are effectively Python dotted paths. E.g. a Python module "foo" with a class
# "bar" with a method "baz" will result in a function in the compilation unit
# called "foo.bar.baz" when it gets `torch.jit.script`'ed.
# (with the exception that `__main__` is replaced with `__torch__`).
#
# Given how systematic this is, we don't treat the symbol names as opaque (i.e.
# we don't need to capture their names when FileCheck testing).

# CHECK-LABEL:     func private @__torch__.TestModule.forward
# CHECK-SAME:        (%[[SELF:.*]]: !torch.nn.Module<"__torch__.TestModule">, %[[X:.*]]: !numpy.ndarray<*:!numpy.any_dtype>) -> !numpy.ndarray<*:!numpy.any_dtype> {
# CHECK:             return %[[X]] : !numpy.ndarray<*:!numpy.any_dtype>
# CHECK:           }
#
# CHECK-LABEL:   torch.class_type @__torch__.TestModule  {
# CHECK:           torch.method "forward", @__torch__.TestModule.forward
# CHECK:         }

class TestModule(torch.nn.Module):
  def __init__(self):
    super().__init__()
  def forward(self, x):
    return x

test_module = TestModule()
recursivescriptmodule = torch.jit.script(test_module)
# TODO: Automatically handle unpacking Python class RecursiveScriptModule into the underlying ScriptModule.
mb.import_module(recursivescriptmodule._c)
mb.module.operation.print()
