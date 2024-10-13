from dataclasses import dataclass
from typing import Union, List, Optional

# Syntax
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
    motive: 'Expr'
    base: 'Expr'
    step: 'Expr'
    target: 'Expr'

Expr = Union[Var, Star, Pi, Lambda, App, Nat, Zero, Succ, ElimNat]

# Environment
class Env:
    def __init__(self):
        self.vars = {}

    def add(self, var: Var, typ: Expr):
        self.vars[var.name] = typ

    def get(self, var: Var) -> Optional[Expr]:
        return self.vars.get(var.name)

# Free Variables
def free_vars(expr: Expr) -> set[str]:
    match expr:
        case Var(name):
            return {name}
        case Star():
            return set()
        case Pi(var, domain, codomain):
            return free_vars(domain) | (free_vars(codomain) - {var.name})
        case Lambda(var, domain, body):
            return free_vars(domain) | (free_vars(body) - {var.name})
        case App(func, arg):
            return free_vars(func) | free_vars(arg)
        case Nat() | Zero():
            return set()
        case Succ(n):
            return free_vars(n)
        case ElimNat(motive, base, step, target):
            return free_vars(motive) | free_vars(base) | free_vars(step) | free_vars(target)

# Capture-avoiding substitution
def subst(expr: Expr, var: Var, replacement: Expr) -> Expr:
    match expr:
        case Var(name) if name == var.name:
            return replacement
        case Pi(v, domain, codomain) if v.name != var.name and v.name not in free_vars(replacement):
            return Pi(v, subst(domain, var, replacement), subst(codomain, var, replacement))
        case Lambda(v, domain, body) if v.name != var.name and v.name not in free_vars(replacement):
            return Lambda(v, subst(domain, var, replacement), subst(body, var, replacement))
        case App(func, arg):
            return App(subst(func, var, replacement), subst(arg, var, replacement))
        case Succ(n):
            return Succ(subst(n, var, replacement))
        case ElimNat(motive, base, step, target):
            return ElimNat(
                subst(motive, var, replacement),
                subst(base, var, replacement),
                subst(step, var, replacement),
                subst(target, var, replacement)
            )
        case _:
            return expr

# Type checking
def type_check(env: Env, expr: Expr) -> Optional[Expr]:
    match expr:
        case Var(name):
            return env.get(Var(name))
        case Star():
            return Star()
        case Pi(var, domain, codomain):
            if type_check(env, domain) == Star():
                new_env = Env()
                new_env.vars.update(env.vars)
                new_env.add(var, domain)
                if type_check(new_env, codomain) == Star():
                    return Star()
        case Lambda(var, domain, body):
            domain_type = type_check(env, domain)
            if domain_type == Star():
                new_env = Env()
                new_env.vars.update(env.vars)
                new_env.add(var, domain)
                body_type = type_check(new_env, body)
                if body_type:
                    return Pi(var, domain, body_type)
        case App(func, arg):
            func_type = type_check(env, func)
            if isinstance(func_type, Pi):
                arg_type = type_check(env, arg)
                if arg_type == func_type.domain:
                    return subst(func_type.codomain, func_type.var, arg)
        case Nat():
            return Star()
        case Zero():
            return Nat()
        case Succ(n):
            if type_check(env, n) == Nat():
                return Nat()
        case ElimNat(motive, base, step, target):
            motive_type = type_check(env, motive)
            if isinstance(motive_type, Pi) and motive_type.domain == Nat() and type_check(env, motive_type.codomain) == Star():
                base_type = type_check(env, base)
                if base_type == App(motive, Zero()):
                    step_type = type_check(env, step)
                    expected_step_type = Pi(Var("n"), Nat(), 
                                            Pi(Var("ih"), App(motive, Var("n")), 
                                               App(motive, Succ(Var("n")))))
                    if step_type == expected_step_type:
                        target_type = type_check(env, target)
                        if target_type == Nat():
                            return App(motive, target)
    return None

# Evaluation (single step)
def eval_step(expr: Expr) -> Optional[Expr]:
    match expr:
        case App(Lambda(var, _, body), arg):
            return subst(body, var, arg)
        case ElimNat(motive, base, step, Zero()):
            return base
        case ElimNat(motive, base, step, Succ(n)):
            return App(App(step, n), ElimNat(motive, base, step, n))
        case App(func, arg):
            new_func = eval_step(func)
            if new_func:
                return App(new_func, arg)
            new_arg = eval_step(arg)
            if new_arg:
                return App(func, new_arg)
        case Succ(n):
            new_n = eval_step(n)
            if new_n:
                return Succ(new_n)
        case ElimNat(motive, base, step, target):
            new_target = eval_step(target)
            if new_target:
                return ElimNat(motive, base, step, new_target)
    return None

# Full evaluation
def eval_full(expr: Expr) -> Expr:
    while True:
        new_expr = eval_step(expr)
        if not new_expr:
            return expr
        expr = new_expr