from dataclasses import dataclass
from typing import Optional, List, Union

@dataclass
class Var:
    name: str

@dataclass
class Star:
    pass

@dataclass
class Pi:
    var: Var
    domain: 'Expr'
    codomain: 'Expr'

@dataclass
class Lambda:
    var: Var
    domain: 'Expr'
    body: 'Expr'

@dataclass
class App:
    func: 'Expr'
    arg: 'Expr'

@dataclass
class Nat:
    pass

@dataclass
class Zero:
    pass

@dataclass
class Succ:
    n: 'Expr'

@dataclass
class ElimNat:
    target: 'Expr'
    motive: 'Expr'
    base: 'Expr'
    step: 'Expr'

Expr = Union[Var, Star, Pi, Lambda, App, Nat, Zero, Succ, ElimNat]

class Context:
    def __init__(self):
        self.vars = {}

    def add(self, var: Var, typ: Expr):
        self.vars[var.name] = typ

    def get(self, var: Var) -> Optional[Expr]:
        return self.vars.get(var.name)

def infer_type(ctx: Context, expr: Expr) -> Optional[Expr]:
    if isinstance(expr, Var):
        return ctx.get(expr)
    elif isinstance(expr, Star):
        return Star()
    elif isinstance(expr, Pi):
        domain_type = infer_type(ctx, expr.domain)
        if not (isinstance(domain_type, Star) or domain_type is None):
            return None
        new_ctx = Context()
        new_ctx.vars.update(ctx.vars)
        new_ctx.add(expr.var, expr.domain)
        codomain_type = infer_type(new_ctx, expr.codomain)
        if not (isinstance(codomain_type, Star) or codomain_type is None):
            return None
        return Star()
    elif isinstance(expr, Lambda):
        domain_type = infer_type(ctx, expr.domain)
        if domain_type is None:
            return None
        new_ctx = Context()
        new_ctx.vars.update(ctx.vars)
        new_ctx.add(expr.var, expr.domain)
        body_type = infer_type(new_ctx, expr.body)
        if body_type is None:
            return None
        return Pi(expr.var, expr.domain, body_type)
    elif isinstance(expr, App):
        func_type = infer_type(ctx, expr.func)
        if not isinstance(func_type, Pi):
            return None
        arg_type = infer_type(ctx, expr.arg)
        if arg_type != func_type.domain:
            return None
        return func_type.codomain
    elif isinstance(expr, Nat):
        return Star()
    elif isinstance(expr, Zero):
        return Nat()
    elif isinstance(expr, Succ):
        n_type = infer_type(ctx, expr.n)
        if not isinstance(n_type, Nat):
            return None
        return Nat()
    elif isinstance(expr, ElimNat):
        target_type = infer_type(ctx, expr.target)
        if not isinstance(target_type, Nat):
            return None
        motive_type = infer_type(ctx, expr.motive)
        if not isinstance(motive_type, Pi) or not isinstance(motive_type.codomain, Star):
            return None
        base_type = infer_type(ctx, expr.base)
        if base_type != App(expr.motive, Zero()):
            return None
        step_type = infer_type(ctx, expr.step)
        if not isinstance(step_type, Pi):
            return None
        n_var = Var("n")
        expected_step_type = Pi(n_var, Nat(), 
                                Pi(Var("ih"), App(expr.motive, n_var), 
                                   App(expr.motive, Succ(n_var))))
        if step_type != expected_step_type:
            return None
        return App(expr.motive, expr.target)
    return None
