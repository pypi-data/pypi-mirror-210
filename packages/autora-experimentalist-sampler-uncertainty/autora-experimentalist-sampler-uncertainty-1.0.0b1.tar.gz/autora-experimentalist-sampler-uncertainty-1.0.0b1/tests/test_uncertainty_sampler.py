from autora.experimentalist.sampler.uncertainty_sampler import uncertainty_sampler
from sklearn.linear_model import LogisticRegression
import numpy as np

def test_output_dimensions():
    #Meta-Setup
    X = np.linspace(start=-3, stop=6, num=10).reshape(-1, 1)
    y = (X**2).reshape(-1)
    n = 5
    
    #Theorists
    lr_theorist = LogisticRegression()
    
    lr_theorist.fit(X,y)

    #Sampler
    X_new = uncertainty_sampler(X, lr_theorist, n)

    # Check that the sampler returns n experiment conditions
    assert X_new.shape == (n, X.shape[1])