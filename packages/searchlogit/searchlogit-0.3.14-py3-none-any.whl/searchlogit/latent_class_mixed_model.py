"""Implements Latent Class Mixed Model."""

import itertools
import logging
import time

import numpy as np
from scipy.optimize import minimize

from ._device import device as dev
from .mixed_logit import MixedLogit

# define the computation boundary values not to be exceeded
min_exp_val = -700
max_exp_val = 700

max_comp_val = 1e+300
min_comp_val = 1e-300

logger = logging.getLogger(__name__)


class LatentClassMixedModel(MixedLogit):
    """Class for estimation of Latent Class Models.

    The design of this class is partly based on the LCCM package,
    https://github.com/ferasz/LCCM (El Zarwi, 2017).

    References
    ----------
    El Zarwi, F. (2017). lccm, a Python package for estimating latent
    class choice models using the Expectation Maximization (EM)
    algorithm to maximize the likelihood function.
    """
    def __init__(self):
        self.save_fitted_params = False  # speed-up computation
        self.start_time = time.time()
        super(LatentClassMixedModel, self).__init__()

    def fit(self, X, y, varnames=None, alts=None, isvars=None, num_classes=2,
            class_params_spec=None, member_params_spec=None,
            transvars=None,
            transformation=None, ids=None, weights=None, avail=None,
            avail_latent=None,  # TODO?: separate param needed?
            randvars=None, panels=None, base_alt=None,
            intercept_opts=None,
            init_coeff=None, init_class_betas=None, init_class_thetas=None,
            maxiter=2000, random_state=None, correlation=None,
            n_draws=1000, halton=True, verbose=1, batch_size=None,
            halton_opts=None, ftol=1e-5, ftol_lccmm=1e-4,
            gtol=1e-5, gtol_membership_func=1e-5,
            hess=True,
            grad=True, method="bfgs",
            validation=False,
            mxl_init=True):
        """Fit multinomial and/or conditional logit models.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_variables)
            Input data for explanatory variables in long format

        y : array-like, shape (n_samples,)
            Choices in long format

        varnames : list, shape (n_variables,)
            Names of explanatory variables that must match the number and
            order of columns in ``X``

        alts : array-like, shape (n_samples,)
            Alternative indexes in long format or list of alternative names

        isvars : list
            Names of individual-specific variables in ``varnames``

        num_classes: int
            Number of latent classes

        class_params_spec: array-like, shape (n_samples,)
            Array of lists containing names of variables for latent class

        member_params_spec: array-like, shape (n_samples,)
            Array of lists containing names of variables for class membership

        transvars: list, default=None
            Names of variables to apply transformation on

        ids : array-like, shape (n_samples,)
            Identifiers for choice situations in long format.

        transformation: string, default=None
            Name of transformation to apply on transvars

        randvars : dict
            Names (keys) and mixing distributions (values) of variables that
            have random parameters as coefficients. Possible mixing
            distributions are: ``'n'``: normal, ``'ln'``: lognormal,
            ``'u'``: uniform, ``'t'``: triangular, ``'tn'``: truncated normal

        weights : array-like, shape (n_variables,), default=None
            Weights for the choice situations in long format.

        avail: array-like, shape (n_samples,)
            Availability of alternatives for the choice situations. One when
            available or zero otherwise.

        base_alt : int, float or str, default=None
            Base alternative

        fit_intercept : bool, default=False
            Whether to include an intercept in the model.

        init_coeff : numpy array, shape (n_variables,), default=None
            Initial coefficients for estimation.

        maxiter : int, default=200
            Maximum number of iterations

        random_state : int, default=None
            Random seed for numpy random generator

        verbose : int, default=1
            Verbosity of messages to show during estimation. 0: No messages,
            1: Some messages, 2: All messages

        method: string, default="bfgs"
            specify optimisation method passed into scipy.optimize.minimize

        batch_size : int, default=None
            Size of batches of random draws used to avoid overflowing memory during computations.

        halton_opts : dict, default=None
            Options for generation of halton draws. The dictionary accepts the following options (keys):

                shuffle : bool, default=False
                    Whether the Halton draws should be shuffled

                drop : int, default=100
                    Number of initial Halton draws to discard to minimize correlations between Halton sequences

                primes : list
                    List of primes to be used as base for generation of Halton sequences.

        ftol : int, float, default=1e-5
            Sets the tol parameter in scipy.optimize.minimize - Tolerance for
            termination.

        gtol: int, float, default=1e-5
            Sets the gtol parameter in scipy.optimize.minimize(method="bfgs) -
            Gradient norm must be less than gtol before successful termination.

        grad : bool, default=True
            Calculate and return the gradient in _loglik_and_gradient

        hess : bool, default=True
            Calculate and return the gradient in _loglik_and_gradient

        scipy_optimisation : bool, default=False
            Use scipy_optimisation for minimisation. When false uses own
            bfgs method.

        Returns
        -------
        None.
        """
        self.ftol = ftol
        self.ftol_lccmm = ftol_lccmm
        self.gtol = gtol
        self.gtol_membership_func = gtol_membership_func
        self.num_classes = num_classes

        # default to using all varnames in each latent class if not specified
        if class_params_spec is None:
            if isvars is not None:
                class_vars = [var for var in varnames if var not in isvars]
            else:
                class_vars = varnames
            class_params_spec = np.array([])
            class_params_spec = np.vstack([class_vars for i in range(num_classes)])
        self.class_params_spec = class_params_spec

        self.membership_as_probability = True if member_params_spec is True else False
        if self.membership_as_probability:
            member_params_spec = np.vstack(['dummy' for i in range(num_classes-1)])
        if member_params_spec is None:
            if isvars is not None:
                member_vars = isvars
            else:
                member_vars = varnames
            member_params_spec = np.vstack([member_vars for i in range(num_classes-1)])

        self.member_params_spec = member_params_spec

        self.panels = panels
        self.init_df = X
        self.init_y = y
        self.ids = ids

        # TODO: MORE LOGIC
        batch_size = n_draws if batch_size is None else min(n_draws, batch_size)

        if '_inter' in np.concatenate(class_params_spec):
            fit_intercept = True
        else:
            fit_intercept = False

        if intercept_opts is None:
            intercept_opts = {}
        else:
            if 'class_intercept_alts' in intercept_opts:
                if len(intercept_opts['class_intercept_alts']) != num_classes:
                    raise ValueError("The key class_intercept_alts in "
                                     "intercept_opts must be the same length "
                                     "as num_classes")
        self.intercept_opts = intercept_opts

        if avail_latent is None:
            avail_latent = np.repeat(None, num_classes)
        self.avail_latent = avail_latent

        if mxl_init:
            init_class_betas = np.array(np.repeat('tmp', num_classes),
                                        dtype='object')
            for i in range(num_classes):
                mxl = MixedLogit()
                mxl_varnames = class_params_spec[i]
                X_mxl_idx = [ii for ii, name in enumerate(varnames) if name in mxl_varnames]
                X_mxl = np.array(X)[:, X_mxl_idx]
                mxl.fit(X_mxl, y, mxl_varnames, alts,
                        avail=avail,
                        transvars=transvars,
                        randvars=randvars,
                        panels=panels,
                        fit_intercept=fit_intercept,
                        correlation=correlation,
                        n_draws=n_draws,
                        gtol=gtol)
                init_class_betas[i] = mxl.coeff_ + np.random.normal(0, 0.01, len(mxl.coeff_))

        self.init_class_betas = init_class_betas
        self.init_class_thetas = init_class_thetas

        self.validation = validation

        self.ind_pred_prob_classes = []
        self.choice_pred_prob_classes = []

        save_fitted_params = False
        self.save_fitted_params = save_fitted_params

        super(LatentClassMixedModel, self).fit(X, y, varnames, alts, isvars,
                                               transvars, transformation, ids,
                                               weights, avail, randvars,
                                               panels, base_alt,
                                               fit_intercept, init_coeff,
                                               maxiter, random_state,
                                               correlation, n_draws, halton,
                                               self._expectation_maximisation_algorithm,
                                               verbose, batch_size,
                                               halton_opts, ftol, gtol,
                                               hess, grad, method,
                                               save_fitted_params)

    def _post_fit(self, optimization_res, coeff_names, sample_size,
                  hess_inv=None, verbose=1):
        if self.validation:
            return
        super(LatentClassMixedModel, self)._post_fit(optimization_res,
                                                     coeff_names,
                                                     sample_size)

    def _compute_probabilities_latent(self, betas, X, y, panel_info, draws,
                                      drawstrans, avail):
        """Compute the standard logit-based probabilities.

        Random and fixed coefficients are handled separately.
        """

        if dev.using_gpu:
            X, y = dev.to_gpu(X), dev.to_gpu(y)
            panel_info = dev.to_gpu(panel_info)
            draws = dev.to_gpu(draws)
            drawstrans = dev.to_gpu(drawstrans)
            if avail is not None:
                avail = dev.to_gpu(avail)

        beta_segment_names = ["Bf", "Br_b", "chol", "Br_w", "Bftrans",
                              "flmbda", "Brtrans_b", "Brtrans_w", "rlmda"]
        var_list = dict()
        # number of parameters for each corresponding segment
        iterations = [self.Kf, self.Kr, self.Kchol, self.Kbw, self.Kftrans,
                      self.Kftrans, self.Krtrans, self.Krtrans, self.Krtrans]

        i = 0
        for count, iteration in enumerate(iterations):
            prev_index = i
            i = int(i + iteration)
            var_list[beta_segment_names[count]] = betas[prev_index:i]

        Bf, Br_b, chol, Br_w, Bftrans, flmbda, Brtrans_b, Brtrans_w, rlmda = \
            var_list.values()
        if dev.using_gpu:
            Bf, Br_b, chol, Br_w, Bftrans, flmbda, Brtrans_b, \
                Brtrans_w, rlmda = \
                dev.to_gpu(Bf), dev.to_gpu(Br_b), dev.to_gpu(chol), \
                dev.to_gpu(Br_w), dev.to_gpu(Bftrans), dev.to_gpu(flmbda), \
                dev.to_gpu(Brtrans_b), dev.to_gpu(Brtrans_w), dev.to_gpu(rlmda)

        chol_mat = np.zeros((self.correlationLength, self.correlationLength))
        indices = np.tril_indices(self.correlationLength)
        if dev.using_gpu:
            chol = dev.to_cpu(chol)
            chol_mat[indices] = chol  # TODO? Better
        else:
            chol_mat[indices] = chol
        Kr_all = self.Kr + self.Krtrans
        chol_mat_temp = np.zeros((self.Kr, self.Kr))

        # TODO: Structure ... Kr first, Krtrans last, fill in for correlations
        # TODO: could do better
        rv_count = 0
        rv_count_all = 0
        rv_trans_count = 0
        rv_trans_count_all = 0
        chol_count = 0
        corr_indices = []

        # TODO: another bugfix
        # Know beforehand to order rvtrans correctly
        num_corr_rvtrans = 0
        for ii, var in enumerate(self.varnames):
            if self.rvtransidx[ii]:
                if hasattr(self, 'correlation') and self.correlation:
                    if hasattr(self.correlation, 'append'):
                        if var in self.correlation:
                            num_corr_rvtrans += 1
                    # else:
                    #     num_corr_rvtrans += 1

        num_rvtrans_total = self.Krtrans + num_corr_rvtrans

        if self.Kr > 0:
            for ii, var in enumerate(self.varnames):  # TODO: BUGFIX
                is_correlated = False
                if hasattr(self, 'correlation') and self.correlation:
                    if hasattr(self.correlation, 'append'):
                        if var in self.correlation:
                            is_correlated = True
                    else:
                        is_correlated = True
                if self.rvidx[ii]:
                    rv_val = chol[chol_count] if is_correlated else Br_w[rv_count]
                    chol_mat_temp[rv_count_all, rv_count_all] = rv_val
                    rv_count_all += 1
                    if is_correlated:
                        chol_count += 1
                    else:
                        rv_count += 1
                if self.rvtransidx[ii]:
                    if hasattr(self, 'correlation') and isinstance(self.correlation, bool):  # BUG FIX
                        is_correlated = False
                    rv_val = chol[chol_count] if is_correlated else Brtrans_w[rv_trans_count]
                    chol_mat_temp[-num_rvtrans_total + rv_trans_count_all, -num_rvtrans_total + rv_trans_count_all] = rv_val
                    rv_trans_count_all += 1
                    if is_correlated:
                        chol_count += 1
                    else:
                        rv_trans_count += 1
                if hasattr(self, 'correlation') and self.correlation:
                    if hasattr(self.correlation, 'append'):
                        if var in self.correlation:
                            if self.rvidx[ii]:
                                corr_indices.append(rv_count_all - 1)
                            else:
                                corr_indices.append(Kr_all - num_rvtrans_total + rv_trans_count_all - 1)   # TODO i think

            if hasattr(self, 'correlation') and isinstance(self.correlation, bool) and self.correlation:
                corr_pairs = list(itertools.combinations(np.arange(self.Kr), 2)) + [(i, i) for i in range(self.Kr)]
            else:
                corr_pairs = list(itertools.combinations(corr_indices, 2)) + [(idx, idx) for ii, idx in enumerate(corr_indices)]

            reversed_corr_pairs = [tuple(reversed(pair)) for ii, pair in enumerate(corr_pairs)]
            reversed_corr_pairs.sort(key=lambda x: x[0])

            chol_count = 0
            for _, corr_pair in enumerate(reversed_corr_pairs):
                # lower cholesky matrix
                chol_mat_temp[corr_pair] = chol[chol_count]
                chol_count += 1

            chol_mat = chol_mat_temp

        V = np.zeros((self.N, self.P, self.J, self.n_draws))

        Xf = X[:, :, :, self.fxidx]
        Xf = Xf.astype('float')
        Xftrans = X[:, :, :, self.fxtransidx]
        Xftrans = Xftrans.astype('float')
        Xr = X[:, :, :, self.rvidx]
        Xr = Xr.astype('float')
        Xrtrans = X[:, :, :, self.rvtransidx]
        Xrtrans = Xrtrans.astype('float')

        if dev.using_gpu:
            V = dev.to_gpu(V)
            Xf = dev.to_gpu(Xf)
            Xr = dev.to_gpu(Xr)
            Xftrans = dev.to_gpu(Xftrans)
            Xrtrans = dev.to_gpu(Xrtrans)
            chol_mat = dev.to_gpu(chol_mat)

        if self.Kf != 0:
            XBf = np.einsum('npjk,k -> npj', Xf, Bf, dtype=np.float64)
            V += XBf[:, :, :, None]
        if self.Kr != 0:
            Br = Br_b[None, :, None] + np.matmul(chol_mat, draws)
            Br = self._apply_distribution(Br, self.rvdist)
            self.Br = Br  # save Br to use later
            XBr = dev.cust_einsum('npjk,nkr -> npjr', Xr, Br)  # (N, P, J, R)
            V += XBr
        #  transformation
        #  transformations for variables with fixed coeffs
        if self.Kftrans != 0:
            Xftrans_lmda = self.transFunc(Xftrans, flmbda)
            Xftrans_lmda[np.isneginf(Xftrans_lmda)] = -max_comp_val
            Xftrans_lmda[np.isposinf(Xftrans_lmda)] = max_comp_val
            # Estimating the linear utility specificiation (U = sum XB)
            Xbf_trans = np.einsum('npjk,k -> npj', Xftrans_lmda, Bftrans, dtype=np.float64)
            # combining utilities
            V += Xbf_trans[:, :, :, None]

        # transformations for variables with random coeffs
        if self.Krtrans != 0:
            # creating the random coeffs
            Brtrans = Brtrans_b[None, :, None] + \
                    drawstrans[:, 0:self.Krtrans, :] * Brtrans_w[None, :, None]
            Brtrans = self._apply_distribution(Brtrans, self.rvtransdist)
            # applying transformation
            Xrtrans_lmda = self.transFunc(Xrtrans, rlmda)
            Xrtrans_lmda[np.isposinf(Xrtrans_lmda)] = 1e+30
            Xrtrans_lmda[np.isneginf(Xrtrans_lmda)] = -1e+30

            Xbr_trans = np.einsum('npjk, nkr -> npjr', Xrtrans_lmda, Brtrans, dtype=np.float64)  # (N, P, J, R)
            # combining utilities
            V += Xbr_trans  # (N, P, J, R)

        if avail is not None:
            if self.panels is not None:
                V = V*avail[:, :, :, None]  # Acommodate availablity of alts with panels
            else:
                V = V*avail[:, None, :, None]  # Acommodate availablity of alts.

        # Thresholds to avoid overflow warnings
        V[np.where(V > max_exp_val)] = max_exp_val
        V[np.where(V < -max_exp_val)] = -max_exp_val
        eV = dev.np.exp(V)
        sum_eV = dev.np.sum(eV, axis=2, keepdims=True)
        sum_eV[np.where(sum_eV < min_comp_val)] = min_comp_val
        p = np.divide(eV, sum_eV, out=np.zeros_like(eV))

        if panel_info is not None:
            p = p*panel_info[:, :, None, None]
        p = y*p

        # collapse on alts
        pch = np.sum(p, axis=2)  # (N, P, R)

        if hasattr(self, 'panel_info'):
            pch = self._prob_product_across_panels(pch, self.panel_info)
        else:
            pch = np.mean(pch, axis=1)  # (N, R)
        pch = np.mean(pch, axis=1)  # (N)
        return pch.flatten()

    def _posterior_est_latent_class_probability(self, class_thetas):
        """Get the prior estimates of the latent class probabilities

        Args:
            class_thetas (array-like): (number of latent classes) - 1 array of
                                       latent class vectors
            X (array-like): Input data for explanatory variables in wide format

        Returns:
            H [array-like]: Prior estimates of the class probabilities
        """
        class_thetas_original = class_thetas
        if class_thetas.ndim == 1:
            new_class_thetas = np.array(np.repeat('tmp', self.num_classes-1),
                                        dtype='object')
            j = 0
            for ii, member_params in enumerate(self.member_params_spec):
                num_params = len(member_params)
                tmp = class_thetas[j:j+num_params]
                j += num_params
                new_class_thetas[ii] = tmp

            class_thetas = new_class_thetas

        class_thetas_base = np.zeros(len(class_thetas[0]))
        # coeff_names_without_intercept = self.global_varnames[(self.J-2):]
        base_X_idx = self._get_member_X_idx(0)
        member_df = np.transpose(self.short_df[:, base_X_idx])

        member_N = member_df.shape[1]

        eZB = np.zeros((self.num_classes, member_N))

        if '_inter' in self.member_params_spec[0]:
            member_df = np.vstack((np.ones((1, member_N)),
                                   np.transpose(self.short_df[:, base_X_idx])))

        if self.membership_as_probability:
            H = np.tile(np.concatenate([1 - np.sum(class_thetas),
                                        class_thetas_original]), (member_N, 1))
            H = np.transpose(H)
        else:
            zB_q = np.dot(class_thetas_base[None, :],
                          member_df)

            eZB[0, :] = np.exp(zB_q)

            for i in range(0, self.num_classes-1):
                class_X_idx = self._get_member_X_idx(i)
                member_df = np.transpose(self.short_df[:, class_X_idx])
                # add in columns of ones for class-specific const (_inter)
                if '_inter' in self.member_params_spec[i]:
                    member_df = np.vstack((np.ones((1, member_N)),
                                           np.transpose(self.short_df[:, class_X_idx])))

                zB_q = np.dot(class_thetas[i].reshape((1, -1)),
                              member_df)
                zB_q[np.where(max_exp_val < zB_q)] = max_exp_val
                eZB[i+1, :] = np.exp(zB_q)

            H = eZB/np.sum(eZB, axis=0, keepdims=True)

        # store to display in summary
        self.class_freq = np.mean(H, axis=1)

        return H

    def _class_member_func(self, class_thetas, weights, X):
        """Used in Maximisaion step. Used to find latent class vectors that
           minimise the negative loglik where there is no observed dependent
           variable (H replaces y).

        Args:
            class_thetas (array-like): (number of latent classes) - 1 array of
                                       latent class vectors
            weights (array-like): weights is prior probability of class by the
                                  probability of y given the class.
            X (array-like): Input data for explanatory variables in wide format
        Returns:
            ll [np.float64]: Loglik
        """
        H = self._posterior_est_latent_class_probability(class_thetas)

        H[np.where(H < 1e-30)] = 1e-30
        weight_post = np.multiply(np.log(H), weights)
        ll = -np.sum(weight_post)

        tgr = H - weights
        gr = np.array([])
        for i in range(1, self.num_classes):
            member_idx = self._get_member_X_idx(i-1)
            membership_df = self.short_df[:, member_idx]

            if '_inter' in self.member_params_spec[i-1]:
                membership_df = np.hstack((np.ones((self.short_df.shape[0], 1)),
                                           membership_df))
            if self.membership_as_probability:
                membership_df = np.ones((self.short_df.shape[0], 1))

            gr_i = np.dot(np.transpose(membership_df), tgr[i, :])
            gr = np.concatenate((gr, gr_i))

        return ll, gr.flatten()

    def _get_class_X_idx2(self, class_num, coeff_names=None, **kwargs):
        """Get indices for X dataset for class parameters.

        Args:
            class_num (int): latent class number

        Returns:
            X_class_idx [np.ndarray]: indices to retrieve relevant
                                        explantory params of specified
                                        latent class
        """
        #  below line: return indices of that class params in Xnames
        #  pattern matching for isvars

        tmp_varnames = None
        if coeff_names is None:
            tmp_varnames = self.global_varnames.copy()
        else:
            tmp_varnames = coeff_names.copy()

        for ii, varname in enumerate(tmp_varnames):
            # remove lambda so can get indices correctly
            if varname.startswith('lambda.'):
                tmp_varnames[ii] = varname[7:]
            if varname.startswith('sd.'):
                tmp_varnames[ii] = varname[3:]

        X_class_idx = np.array([], dtype='int32')
        for var in self.class_params_spec[class_num]:
            for ii, var2 in enumerate(tmp_varnames):
                if 'inter' in var and coeff_names is not None:  # only want to use summary func
                    if 'inter' in var2:
                        if 'class_intercept_alts' in self.intercept_opts:
                            alt_num = int(var2.split('.')[-1])
                            if alt_num not in self.intercept_opts['class_intercept_alts'][class_num]:
                                continue
                if var in var2:
                    X_class_idx = np.append(X_class_idx, ii)

        # isvars handled if pass in full coeff names
        X_class_idx = np.unique(X_class_idx)
        X_class_idx = np.sort(X_class_idx)
        X_class_idx_tmp = np.array([], dtype='int')
        counter = 0

        if coeff_names is not None:
            return X_class_idx
        for idx_pos in range(len(self.global_varnames)):
            if idx_pos in self.ispos:
                # fix bug of not all alts checked intercept
                for i in range(self.J - 1):
                    if idx_pos in X_class_idx:
                        if self.global_varnames[idx_pos] == '_inter' and 'class_intercept_alts' in self.intercept_opts:
                            if i+2 not in self.intercept_opts['class_intercept_alts'][class_num]:
                                counter += 1
                                continue
                        X_class_idx_tmp = np.append(X_class_idx_tmp, int(counter))
                    counter += 1
            else:
                if idx_pos in X_class_idx:
                    X_class_idx_tmp = np.append(X_class_idx_tmp, counter)
                counter += 1

        X_class_idx = X_class_idx_tmp

        return X_class_idx

    def _get_class_X_idx(self, class_num, coeff_names=None):
        """Get indices for X dataset based on which parameters have been
            specified for the latent class

        Args:
            class_num (int): latent class number

        Returns:
            X_class_idx [np.ndarray]: indices to retrieve relevant
                                        explantory params of specified
                                        latent class
        """
        #  below line: return indices of that class params in Xnames
        #  pattern matching for isvars

        if coeff_names is None:
            coeff_names = self.global_varnames.copy()

        tmp_varnames = coeff_names.copy()
        for ii, varname in enumerate(tmp_varnames):
            # remove lambda so can get indices correctly
            if varname.startswith('lambda.'):
                tmp_varnames[ii] = varname[7:]
            if varname.startswith('sd.'):
                tmp_varnames[ii] = varname[3:]

        X_class_idx = np.array([], dtype="int")
        for var in self.class_params_spec[class_num]:
            for ii, var2 in enumerate(tmp_varnames):
                if 'inter' in var and coeff_names is not None:  # only want to use summary func
                    if 'inter' in var2:
                        if 'class_intercept_alts' in self.intercept_opts:
                            alt_num = int(var2.split('.')[-1])
                            if alt_num not in self.intercept_opts['class_intercept_alts'][class_num]:
                                continue
                if var in var2:
                    X_class_idx = np.append(X_class_idx, ii)

        X_class_idx = np.unique(X_class_idx)
        X_class_idx = np.sort(X_class_idx)

        return X_class_idx

    def _get_member_X_idx(self, class_num, coeff_names=None):
        """Get indices for X dataset based on which parameters have been
            specified for the latent class membership

        Args:
            class_num (int): latent class number

        Returns:
            X_class_idx [np.ndarray]: indices to retrieve relevant
                                        explantory params of specified
                                        latent class
        """
        if coeff_names is None:
            if '_inter' in self.global_varnames and self.J > 2:
                coeff_names = self.global_varnames[(self.J-2):].copy()
            else:
                coeff_names = self.global_varnames.copy()
        tmp_varnames = coeff_names.copy()
        for ii, varname in enumerate(tmp_varnames):
            # remove lambda so can get indices correctly
            if varname.startswith('lambda.'):
                tmp_varnames[ii] = varname[7:]

        X_class_idx = np.array([], dtype='int32')
        for var in self.member_params_spec[class_num]:
            for ii, var2 in enumerate(tmp_varnames):
                if var in var2 and var != '_inter':
                    X_class_idx = np.append(X_class_idx, ii)

        X_class_idx = np.sort(X_class_idx)

        return X_class_idx

    def _get_kchol(self, specs):
        randvars_specs = [param for param in specs if param in self.randvars]
        Kchol = 0
        if (self.correlation):
            if (isinstance(self.correlation, list)):
                corvars_in_spec = [corvar for corvar in self.correlation if corvar in randvars_specs]
                # Kchol, permutations of specified params in correlation list
                Kchol = int((len(corvars_in_spec) *
                            (len(corvars_in_spec)+1))/2)
                self.correlationLength = len(corvars_in_spec)
            else:
                # i.e. correlation = True, Kchol permutations of rand vars
                Kchol = int((len(randvars_specs) *
                            (len(randvars_specs)+1))/2)
                self.correlationLength = len(randvars_specs)
        return Kchol

    def _get_betas_length(self, class_num):
        """Get betas length (parameter vectors) for the specified latent class

        Args:
            class_num (int): latent class number

        Returns:
            betas_length (int): number of betas for latent class
        """
        class_idx = self._get_class_X_idx(class_num)
        self._set_bw(class_idx)
        class_params_spec = self.class_params_spec[class_num]
        class_isvars = [x for x in class_params_spec if x in self.isvars]
        class_asvars = [x for x in class_params_spec if x in self.asvars]
        class_randvars = [x for x in class_params_spec if x in self.randvars]
        class_transvars = [x for x in class_params_spec if x in self.transvars]

        has_intercept = True if 'intercept' in class_params_spec else False
        betas_length = ((len(self.alternatives)-1)*(len(class_isvars)) +
                        len(class_asvars) + len(class_randvars)
                        if not has_intercept
                        else (len(self.alternatives)-1)*(len(class_isvars)+1) +
                        len(class_asvars) + len(class_randvars))
        # copied from choice model logic for Kchol
        Kchol = self._get_kchol(class_params_spec)
        betas_length += Kchol
        betas_length += len(class_transvars)*2
        betas_length += sum(self.rvtransidx)  # random trans vars
        betas_length += self.Kbw

        return betas_length

    def _make_short_df(self, X):
        """Make an shortened dataframe average over alts, used in latent
        class estimation.
        """
        short_df = np.mean(np.mean(X, axis=2), axis=1)  # 2... over alts

        # Remove intercept columns
        if self.fit_intercept:
            short_df = short_df[:, (self.J-2):]
            short_df[:, 0] = 1

        if dev.using_gpu:
            short_df = dev.to_cpu(short_df)

        self.short_df = short_df

    def _set_bw(self, specs):
        """Logic copied from _choice_model class"""
        specs = self.global_varnames[specs]
        self.varnames = specs
        randvars_specs = [param for param in specs if param in self.randvars]
        Kr = len(randvars_specs)
        self.Kbw = Kr
        self.Kr = Kr
        self.Kftrans = sum(self.fxtransidx)
        self.Krtrans = sum(self.rvtransidx)
        self.rvdist = [dist for ii, dist in enumerate(self.global_rvdist)
                       if self.randvars[ii] in randvars_specs]

        # set up length of betas required to estimate correlation and/or
        # random variable standard deviations, useful for cholesky matrix
        if (self.correlation):
            if (isinstance(self.correlation, list)):
                corvars_in_spec = [corvar for corvar in self.correlation if corvar in randvars_specs]
                self.correlationLength = len(corvars_in_spec)
                self.Kbw = Kr - self.correlationLength
            else:
                self.correlationLength = Kr
                self.Kbw = 0

    def _expectation_maximisation_algorithm(self, tmp_fn, tmp_betas, args,
                                            class_betas=None,
                                            class_thetas=None,
                                            validation=False,
                                            **kwargs):
        """Run the EM algorithm by iterating between computing the
           posterior class probabilities and re-estimating the model parameters
           in each class by using a probability weighted loglik function

        Args:
            X (array-like): Input data for explanatory variables in wide format
            y (array-like):  Choices (outcome) in wide format
            weights (array-like): weights is prior probability of class by the
                                  probability of y given the class.
            avail (array-like): Availability of alternatives for the
                                choice situations. One when available or
                                zero otherwise.

        Returns:
            optimisation_result (dict): Dictionary mimicking the optimisation
                                        result in scipy.optimize.minimize
        """
        X, y, panel_info, draws, drawstrans, weights, avail, batch_size = args
        self.global_varnames = self.varnames
        if '_inter' in self.global_varnames:
            for i in range(self.J - 2):
                self.global_varnames = np.concatenate((np.array(['_inter'], dtype='<U64'), self.global_varnames))
        if X.ndim != 4:
            X = X.reshape(self.N, self.P, self.J, -1)
            y = y.reshape(self.N, self.P, self.J, -1)

        converged = False
        self.global_rvdist = self.rvdist

        if self.membership_as_probability:
            class_thetas = np.array([1/(self.num_classes) for i in range(0, self.num_classes-1)])

        if class_betas is None and self.init_class_betas is not None:
            class_betas = self.init_class_betas

        if class_thetas is None and self.init_class_thetas is not None:
            class_thetas = self.init_class_thetas

        if class_betas is None:
            class_betas = [-0.1 * np.random.rand(self._get_betas_length(i))
                           for i in range(self.num_classes)]

        if class_thetas is None:
            # class membership probability
            len_class_thetas = [len(self._get_member_X_idx(i)) for i in range(0, self.num_classes-1)]
            for ii, len_class_thetas_ii in enumerate(len_class_thetas):
                if '_inter' in self.member_params_spec[ii]:
                    len_class_thetas[ii] = len_class_thetas[ii] + 1
            class_thetas = np.concatenate([
                np.zeros(len_class_thetas[i])
                for i in range(0, self.num_classes-1)], axis=0)

        # used for _get_class_X_idx
        self.trans_pos = [ii for ii, var in enumerate(self.varnames) if var in self.transvars]

        log_lik_old = 0

        self._make_short_df(X)

        max_iter = 2000
        max_time = 3600  # seconds in an hour
        iter_num = 0
        class_betas_sd = [np.repeat(.99, len(betas))
                          for betas in class_betas]
        class_thetas_sd = np.repeat(.01, class_thetas.size)

        class_idxs = []
        class_fxidxs = []
        class_fxtransidxs = []
        class_rvidxs = []
        class_rvtransidxs = []
        global_fxidx = self.fxidx
        global_fxtransidx = self.fxtransidx
        global_rvidx = self.rvidx
        global_rvtransidx = self.rvtransidx
        for class_num in range(self.num_classes):
            X_class_idx = self._get_class_X_idx(class_num)
            class_idxs.append(X_class_idx)
            # deal w/ fix indices
            class_fx_idx = [fxidx for ii, fxidx in enumerate(global_fxidx)
                            if ii in X_class_idx]
            class_fxtransidx = [fxtransidx for ii, fxtransidx in enumerate(global_fxtransidx)
                                 if ii in X_class_idx]
            # class_fxtransidx = np.repeat(False, len(X_class_idx))
            class_fxidxs.append(class_fx_idx)
            class_fxtransidxs.append(class_fxtransidx)
            # deal w/ random indices
            class_rv_idx = [rvidx for ii, rvidx in enumerate(global_rvidx)
                            if ii in X_class_idx]
            class_rvtransidx = [rvtransidx for ii, rvtransidx in enumerate(global_rvtransidx)
                                 if ii in X_class_idx]
            # class_rvtransidx = np.repeat(False, len(X_class_idx))
            class_rvidxs.append(class_rv_idx)
            class_rvtransidxs.append(class_rvtransidx)

        while not converged and iter_num < max_iter:
            curr_time = time.time()
            time_elapsed = curr_time - self.start_time
            if time_elapsed > max_time:
                logger.info('Time limit reached. Stopping EM algorithm.')
                raise Exception("Time limit reached. Stopping EM algorithm.")

            # Expectation step
            self.ind_pred_prob_classes = []
            self.choice_pred_prob_classes = []
            # reset Kf, Kr in case weird isvars/intercept issues
            self.Kf = sum(class_fxidxs[0])
            self.Kr = sum(class_rvidxs[0])
            self.fxidx = class_fxidxs[0]
            self.fxtransidx = class_fxtransidxs[0]
            self.rvidx = class_rvidxs[0]
            self.rvtransidx = class_rvtransidxs[0]
            self._set_bw(class_idxs[0])  # sets sd. and corr length params
            self.Kchol = self._get_kchol(self.global_varnames[class_idxs[0]])
            rand_idx = [ii for ii, param in enumerate(self.randvars)
                        if param in self.global_varnames[class_idxs[0]]]
            randtrans_idx = [ii for ii, param in enumerate(self.randtransvars)
                        if param in self.global_varnames[class_idxs[0]]]
            p = self._compute_probabilities_latent(class_betas[0],
                                                   X[:, :, :, class_idxs[0]],
                                                   y,
                                                   panel_info,
                                                   draws[:, rand_idx, :],
                                                   drawstrans[:, randtrans_idx, :],
                                                   avail
                                                   )

            # k = np.atleast_2d(self.member_params_spec)[0].size
            H = self._posterior_est_latent_class_probability(class_thetas)
            self.H = H  # save individual-level probabilities for class membership
            for class_i in range(1, self.num_classes):
                self.Kf = sum(class_fxidxs[class_i])
                self.Kr = sum(class_rvidxs[class_i])
                self.fxidx = class_fxidxs[class_i]
                self.fxtransidx = class_fxtransidxs[class_i]
                self.rvidx = class_rvidxs[class_i]
                self.rvtransidx = class_rvtransidxs[class_i]
                self._set_bw(class_idxs[class_i])  # sets sd. and corr length
                self.Kchol = self._get_kchol(self.global_varnames[class_idxs[class_i]])
                rand_idx = [ii for ii, param in enumerate(self.randvars)
                            if param in self.global_varnames[class_idxs[class_i]]]
                randtrans_idx = [ii for ii, param in enumerate(self.randtransvars)
                            if param in self.global_varnames[class_idxs[class_i]]]

                new_p = self._compute_probabilities_latent(class_betas[class_i],
                                                    X[:, :, :, class_idxs[class_i]],
                                                    y,
                                                    panel_info,
                                                    draws[:, rand_idx, :],
                                                    drawstrans[:, randtrans_idx, :],
                                                    avail
                                                    )
                p = np.vstack((p, new_p))

            if dev.using_gpu:
                p = dev.to_cpu(p)
                H = dev.to_cpu(H)

            weights = np.multiply(p, H)
            weights[weights == 0] = min_comp_val

            log_lik = np.log(np.sum(weights, axis=0))  # sum over classes

            log_lik_new = np.sum(log_lik)

            if self.validation:
                self.loglikelihood = log_lik_new
                num_params = 0
                num_params += sum([len(betas) for betas in class_betas])
                num_params += len(class_thetas)
                self.aic = -2 * log_lik_new + 2 * num_params
                self.bic = -2 * log_lik_new + num_params * np.log(self.sample_size)
                return log_lik_new

            weights_individual = weights
            weights_individual = np.divide(weights_individual,
                                 np.tile(np.sum(weights_individual, axis=0),
                            (self.num_classes, 1)))

            weights = np.divide(weights,
                                np.tile(np.sum(weights, axis=0),
                                        (self.num_classes, 1)))

            # Maximisation step
            optimsation_convergences = True
            opt_res = minimize(self._class_member_func,
                               class_thetas,
                               jac=True,
                               args=(weights_individual, X),
                               method='BFGS',
                               tol=self.ftol,
                               options={'gtol': self.gtol_membership_func}
                               )
            if opt_res['success']:
                class_thetas = opt_res['x']
                prev_tmp_thetas_sd = class_thetas_sd
                tmp_thetas_sd = np.sqrt(np.diag(opt_res['hess_inv']))
                # in scipy.optimse if "initial guess" is close to optimal
                # solution it will not build up a guess at the Hessian inverse
                # this if statement prevents this case
                # Ad-hoc prevention
                for ii, tmp_theta_sd in enumerate(tmp_thetas_sd):
                    # NOTE: adhoc
                    if prev_tmp_thetas_sd[ii] < 0.25 * tmp_theta_sd and prev_tmp_thetas_sd[ii] != 0.01:
                        tmp_thetas_sd[ii] = prev_tmp_thetas_sd[ii]
                    if np.isclose(tmp_thetas_sd[ii], 1.0):
                        tmp_thetas_sd[ii] = prev_tmp_thetas_sd[ii]
                class_thetas_sd = tmp_thetas_sd
            else:
                optimsation_convergences = False
            self.pred_prob_all = np.array([])
            global_transvars = self.transvars.copy()
            if not hasattr(self, 'panel_info'):
                self.panel_info = None
            for s in range(0, self.num_classes):
                class_X_idx = self._get_class_X_idx(s)
                self.Kf = sum(class_fxidxs[s])
                self.Kr = sum(class_rvidxs[s])
                self.fxidx = class_fxidxs[s]
                self.fxtransidx = class_fxtransidxs[s]
                self.rvidx = class_rvidxs[s]
                self.rvtransidx = class_rvtransidxs[s]

                self._set_bw(class_X_idx)  # sets sd. and corr length params
                self.Kchol = self._get_kchol(self.global_varnames[class_idxs[s]])
                rand_idx = [ii for ii, param in enumerate(self.randvars)
                            if param in self.global_varnames[class_idxs[s]]]
                randtrans_idx = [ii for ii, param in enumerate(self.randtransvars)
                            if param in self.global_varnames[class_idxs[s]]]
                jac = True if self.grad else False
                self.total_fun_eval = 0
                opt_res = minimize(self._loglik_gradient,
                                   class_betas[s],
                                   jac=jac,
                                   args=(
                                         X[:, :, :, class_X_idx],
                                         y,
                                         self.panel_info,
                                         draws[:, rand_idx, :],
                                         drawstrans[:, randtrans_idx, :],
                                         weights[s, :],
                                         avail,
                                         batch_size),
                                   method="BFGS",
                                   tol=self.ftol,
                                   options={'gtol': self.gtol}
                                   )
                # save predicted and observed probabilities to display in summary
                p = self._compute_probabilities(opt_res['x'], X[:, :, :, class_X_idx], panel_info, draws[:, rand_idx, :],
                                                drawstrans[:, randtrans_idx, :], avail,
                                                self.var_list,
                                                self.chol_mat)

                self.choice_pred_prob = np.mean(p, axis=3)
                self.ind_pred_prob = np.mean(self.choice_pred_prob, axis=1)
                self.pred_prob = np.mean(self.ind_pred_prob, axis=0)
                self.prob_full = p

                self.transvars = global_transvars
                self.pred_prob_all = np.append(self.pred_prob_all,
                                               self.pred_prob)
                self.ind_pred_prob_classes.append(self.ind_pred_prob)
                self.choice_pred_prob_classes.append(self.choice_pred_prob)
                if opt_res['success']:
                    class_betas[s] = opt_res['x']
                    prev_class_betas_sd = class_betas_sd
                    tmp_calc = np.sqrt(np.diag(opt_res['hess_inv']))
                    # in scipy.optimse if "initial guess" is close to optimal
                    # solution it will not build up a guess at the Hessian inverse
                    # this if statement prevents this case
                    # Ad-hoc prevention
                    for ii, tmp_beta_sd in enumerate(tmp_calc):
                        if prev_class_betas_sd[s][ii] < 0.25 * tmp_beta_sd:
                            tmp_calc[ii] = prev_class_betas_sd[s][ii]
                    class_betas_sd[s] = tmp_calc
                else:
                    optimsation_convergences = False

            self.varnames = self.global_varnames
            converged = np.abs(log_lik_new - log_lik_old) < self.ftol_lccmm
            if self.verbose > 1:
                print('class betas: ', class_betas)
                print('class_thetas: ', class_thetas)
                print(f'Loglik: {log_lik_new:.4f}')
            log_lik_old = log_lik_new
            iter_num += 1
            class_thetas = class_thetas.reshape((self.num_classes-1, -1))

        x = np.array([])
        for betas in class_betas:
            betas = np.array(betas)
            x = np.concatenate((x, betas))

        stderr = np.concatenate(class_betas_sd)

        optimisation_result = {'x': x,
                               'success': optimsation_convergences,
                               'fun': -log_lik_new,
                               'nit': iter_num,
                               'stderr': stderr,
                               'is_latent_class': True,
                               'class_x': class_thetas.flatten(),
                               'class_x_stderr': class_thetas_sd,
                               'hess_inv': opt_res['hess_inv']
                               }

        self.fxidx = global_fxidx
        self.fxtransidx = global_fxtransidx
        self.rvidx = global_rvidx
        self.rvtransidx = global_rvtransidx

        p_class = np.mean(H, axis=1)
        pred_prob_tmp = np.zeros(self.J)

        if dev.using_gpu:
            self.pred_prob_all = dev.to_cpu(self.pred_prob_all)
        for i in range(self.num_classes):
            pred_prob_tmp += p_class[i] * self.pred_prob_all[i*self.J:(i*self.J)+self.J]
        self.pred_prob = pred_prob_tmp

        return optimisation_result

    def validation_loglik(self, validation_X, validation_Y, ids=None,
                          panel_info=None, avail=None, weights=None, betas=None,
                          batch_size=None, alts=None, panels=None):
        """Computes the log-likelihood on the validation set using
        the betas fitted using the training set.
        """
        if panels is not None:
            N = len(np.unique(panels))
        else:
            N = self.N
        validation_X, Xnames = self._setup_design_matrix(validation_X)
        self.N = N

        # X, y, panels = self._arrange_long_format(validation_X, validation_Y,
        #   ids, alts, panel_info)
        # N, K = validation_X.shape
        # # N = int(N/self.J)
        # self.init_df = validation_X
        # # validation_X = validation_X.reshape((-1, self.J, K))
        # validation_X, _ = self._setup_design_matrix(validation_X)
        if len(np.unique(panels)) != (N/self.J):
            # N = len(np.unique(ids))
            X, y, avail, panel_info = self._balance_panels(validation_X, validation_Y, avail, panels)
            validation_X = X.reshape((N, self.P, self.J, -1))
            validation_Y = y.reshape((N, self.P, self.J, -1))
        else:
            validation_X = validation_X.reshape(N, self.P, self.J, -1)
            validation_Y = validation_Y.reshape(N, self.P, -1)

        batch_size = self.n_draws
        self.N = N  # store for use in EM alg
        # self.ids = ids

        draws, drawstrans = self._generate_draws(N, self.n_draws)  # (N,Kr,R)

        class_betas = []
        counter = 0
        for ii, param_spec in enumerate(self.class_params_spec):
            # count + add coeff_
            idx = counter + self._get_betas_length(0)
            class_betas.append(self.coeff_[counter:idx])
            counter = idx

        counter = 0
        for ii, param_spec in enumerate(self.member_params_spec):
            # count + add coeff_
            idx = counter + len(param_spec)
            class_betas.append(self.coeff_[counter:idx])
            counter = idx

        tmp_fn = None
        tmp_betas = class_betas
        args = (validation_X, validation_Y, panel_info, draws, drawstrans,
                weights, avail, batch_size)
        res = self._expectation_maximisation_algorithm(tmp_fn, tmp_betas, args,
                                                       validation=True)

        loglik = -res
        return loglik

    def _bfgs_optimization(self, betas, X, y, weights, avail, maxiter):
        """Override bfgs function in multinomial logit to use EM."""
        opt_res = self._expectation_maximisation_algorithm(X, y, avail, validation=self.validation)
        return opt_res
