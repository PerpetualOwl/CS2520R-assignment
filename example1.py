from model import *

ctx = Context()
nat_plus = Lambda(Var("m"), Nat(), 
                  Lambda(Var("n"), Nat(), 
                         ElimNat(Var("m"), 
                                 Lambda(Var("_"), Nat(), Nat()), 
                                 Var("n"), 
                                 Lambda(Var("_"), Nat(), 
                                        Lambda(Var("rec"), Nat(), 
                                               Succ(Var("rec")))))))

result = infer_type(ctx, nat_plus)
print(result)  # Pi(Var(name='m'), Nat(), Pi(Var(name='n'), Nat(), Nat()))
