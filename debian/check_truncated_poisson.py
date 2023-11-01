
# based on TestTruncatedLFPoissonModel
import warnings

import numpy as np
from numpy.testing import assert_allclose, assert_equal

from statsmodels import datasets
from statsmodels.tools.tools import add_constant
from statsmodels.tools.testing import Holder
from statsmodels.tools.sm_exceptions import (
    ConvergenceWarning,
    )

from statsmodels.distributions.discrete import (
    truncatedpoisson,
    truncatednegbin,
    )
from statsmodels.discrete.truncated_model import (
    TruncatedLFPoisson,
    TruncatedLFNegativeBinomialP,
    HurdleCountModel,
    )

from statsmodels.discrete.tests.results.results_discrete import RandHIE


data = datasets.randhie.load()
exog = add_constant(np.asarray(data.exog)[:, :4], prepend=False)
mod = TruncatedLFPoisson(data.endog, exog, truncation=5)
res1 = mod.fit(method="newton", maxiter=500,warn_convergence=True)
print("newton500",res1.params,flush=True)
res3 = mod.fit(warn_convergence=True)
print("default",res3.params,flush=True)
rres3 = mod.fit(maxiter=500,warn_convergence=True)
print("default500",res3.params,flush=True)
res2 = RandHIE()
res2.truncated_poisson()
alpha1 = np.ones(len(res1.params))
print("expected",res2.params,flush=True)
for alpha in [0,1e-100,1e-12,1e-6,1e-5,1e-4,1e-3,.002,.005,.009,.01,.011,.02,.05,.1,.5,1,10,1e4]:
    res_reg = mod.fit_regularized(alpha=alpha*alpha1,disp=True,full_output=True)
    print("regularized",alpha,res_reg.params,res_reg.mle_retvals,flush=True)
    try:
        res_reg = mod.fit_regularized(alpha=alpha*alpha1,method='l1_cvxopt_cp',disp=True,full_output=True)
        print("regularized_cvx",alpha,res_reg.params,res_reg.mle_retvals,flush=True)
    except Exception as e:
        print("failed",e,flush=True)

