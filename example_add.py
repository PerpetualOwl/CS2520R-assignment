from model import *

env = Env()
add = Lambda(Var("m"), Nat(),
                 Lambda(Var("n"), Nat(),
                        ElimNat(Lambda(Var("_"), Nat(), Nat()),
                                Var("n"),
                                Lambda(Var("_"), Nat(),
                                       Lambda(Var("rec"), Nat(),
                                              Succ(Var("rec")))),
                                Var("m"))))

three = Succ(Succ(Succ(Zero())))
two = Succ(Succ(Zero()))
one = Succ(Zero())

if __name__ == "__main__":
    result = eval_full(App(App(add, two), one))
    print(result == three)
    # We get the expected result that 1 + 2 = 3