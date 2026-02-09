import matplotlib

import matplotlib.pyplot as plt
import torch

import borch
from borch import infer, distributions as dist


# gaussian random normal variable 
rvar = dist.Normal(0, 1)
print(rvar.tensor)

# can be treated as tensor
print(rvar * torch.randn(10))

# sample from a random varible
rvar.sample()
print(rvar)

# sample 1000 times and display as histogram
plt.hist([rvar.sample().item() for i in range(1000)])
plt.show()

# example of the model definition 

class Model(borch.Module):
    def __init__(self):
        module.weight1 = dist.Gamma(1, 1 / 2)
        module.weight2 = dist.Normal(loc=1, scale=2)
        module.weight3 = dist.Normal(loc=1, scale=2)

    def forward(module):
        mu = module.weight1 + module.weight2 + module.weight3
        module.obs = dist.Normal(mu, 1)
        return mu
    
def forward(module):
    module.weight1 = dist.Gamma(1, 1 / 2)
    module.weight2 = dist.Normal(loc=1, scale=2)
    module.weight3 = dist.Normal(loc=1, scale=2)
    mu = module.weight1 + module.weight2 + module.weight3
    module.obs = dist.Normal(mu, 1)
    return mu


module = borch.Module()
borch.sample(module) # this will sample all `RandomVariable`s in the network
forward(module)
optimizer = torch.optim.Adam(module.parameters())