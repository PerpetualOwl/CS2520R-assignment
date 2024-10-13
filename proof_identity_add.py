from model import *
from example_add import add

env = Env()

# this function states that n + 0 = n which is the additive identity function
add_zero_right = Lambda(Var("n"), Nat(),
                        ElimNat(Lambda(Var("k"), Nat(), 
                                       Pi(Var("_"), App(App(add, Var("k")), Zero()),
                                          Var("k"))),
                                Lambda(Var("_"), App(App(add, Zero()), Zero()),
                                       Zero()),
                                Lambda(Var("k"), Nat(),
                                       Lambda(Var("ih"), Pi(Var("_"), App(App(add, Var("k")), Zero()),
                                                            Var("k")),
                                              Lambda(Var("_"), App(App(add, Succ(Var("k"))), Zero()),
                                                     Succ(Var("k"))))),
                                Var("n")))

if __name__ == "__main__":
    # Show that 2 + 0 = 2
    two = Succ(Succ(Zero()))
    proof_for_two = eval_full(App(add_zero_right, two))
    print(proof_for_two)