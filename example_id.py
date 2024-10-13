from model import *

env = Env()
id = Lambda(
              Var("A"),
              Star(),
              Lambda(
                     Var("x"),
                     Var("A"),
                     Var("x")
              )
       )

if __name__ == "__main__":
       type = type_check(env, id)
       print(type)
       # We get the valid type:
       # Pi(var=Var(name='A'), domain=Star(), codomain=Pi(var=Var(name='x'), domain=Star(), codomain=Var(name='A')))