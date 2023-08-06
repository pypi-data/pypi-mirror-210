import copy
import datetime
import logging
import math
import os
import sys
import time
from collections import UserDict

import matplotlib.pyplot as plt
import numpy as np

from ._device import device as dev
from .latent_class_mixed_model import LatentClassMixedModel
from .latent_class_model import LatentClassModel
from .mixed_logit import MixedLogit
from .multinomial_logit import MultinomialLogit

logger = logging.getLogger(__name__)

boxc_l = ['L1', 'L2']

class Solution(UserDict):
    """
    A custom dictionary-based class to represent a DCM solution.
    """
    sol_counter = 0  # Counter used to track solution through search

    def __init__(self, *args, **kwargs):
        # self.data = {}
        super(Solution, self).__init__(*args, **kwargs)
        self.data.setdefault('bic', 10000000.0)
        self.data.setdefault('multi_val', 10000000.0)
        self.data.setdefault('loglik', -10000000.0)
        self.data.setdefault('asvars', [])
        self.data.setdefault('isvars', [])
        self.data.setdefault('randvars', {})
        self.data.setdefault('bcvars', [])
        self.data.setdefault('corvars', [])
        self.data.setdefault('bctrans', [])
        self.data.setdefault('cor', False)
        self.data.setdefault('class_params_spec', None)
        self.data.setdefault('member_params_spec', None)
        self.data.setdefault('asc_ind', False)
        self.data.setdefault('is_initial_sol', False)

        # Update sol_counter and sol_num
        self.data['sol_num'] = Solution.sol_counter
        Solution.sol_counter += 1
        # TODO? Temp fix... when cor set to False when there is corvars
        if not self.data['cor'] and len(self.data['corvars']) > 0:
            self.data['cor'] = True

    # def __setitem__(self, key, item):
    #     self.data[str(key)] = item

    def add_objective(self,
                      bic: float,
                      multi_val: float = -10000000.0,
                      loglik: float = -10000000.0) -> None:
        """
        Add objective function values to the solution.

        Args:
            bic (float): The Bayesian Information Criterion (BIC) value.
            multi_val (float, optional): The multi_val value. Defaults to -10000000.0.
            loglik (float, optional): The log-likelihood value. Defaults to -10000000.0.

        """
        self.data['bic'] = bic
        self.data['multi_val'] = multi_val
        self.data['loglik'] = loglik

    def add_is_init(self):
        self.data['is_initial_sol'] = True


class Search():
    """Class for the IGHS search algorithm for choice models.

    Attributes
    ----------
    df : pandas.DataFrame
        Dataframe for training data.

    df_test : pandas.DataFrame
        Dateframe for testing data.

    varnames : list-like, shape (n_variables,)
        Names of explanatory variables.

    dist : list, default=None
        Random distributions to select from.

    code_name : str, default="search"
        Name for the search, used in save files.

    avail : array-like, shape (n_samples*n_alts,), default=None
        Availability of alternatives for the choice situations. One
        when available or zero otherwise.

    test_av  array-like, default=None
        Availability of alternatives for the choice situations of
        the testing dataset.

    weights : array-like, shape(n_samples,), default=None
        Sample weights in long format.

    test_weight_var : array-like, shape(n_samples,), default=None
        Sample weights in long format for test dataset.

    choice_set : list of str, default=None
        Alternatives in the choice set.

    choice_var : array-like, default=None
        Choice variable for each observation.

    test_choice_var : array-like, default=None
        Choice variable for each observation of the test dataframe.

    alt_var : array_like, default=None
        Alternative for each row of the training dataframe.

    test_alt_var : array_like, default=None
        Alternative for each row of the testing dataframe.

    choice_id : array_like, default=None
        Custom ids (i.e. choice id) for the training dataframe.

    test_choice_id : array_like, default=None
        Custom ids (i.e. choice id) for the testing dataframe.

    ind_id : array_like, default=None
        Individual ids for the training dataframe.

    test_ind_id : array_like, default=None
        Individual ids for the testing dataframe.

    isvarnames : list, default=None
        Individual-specific variables in varnames.

    asvarnames : list, default=None
        Alternative-specific variables in varnames.

    trans_asvars : list, default=None  # TODO? remove?
        List of asvars manually transformed.

    ftol : float, default=1e-5
        Sets the tol parameter in scipy.optimize.minimize - Tolerance
        for termination. Also tol parameter for EM algorithm for
        latent classes.

    gtol : float, default=1e-5
        Sets the gtol parameter in scipy.optimize.minimize -
        Gradient norm must be less than gtol before successful
        termination.

    latent_class : bool, default=False
        Option to use latent class models in the search algorithm.

    num_classes : int, default-2
        Sets the number of classes if using latent class models.

    maxiter : int, default=200
        Maximum number of iterations.

    multi_objective : bool, default=False
        Option to use the multi-objective heuristic (training BIC
        and out of sample MAE) or single-objective (training BIC).

    p_val : float, default=0.05
        P-value used to test for non-significance of model coefficients.

    chosen_alts_test: array-like, default=True
        Array of alts of each choice.

    allow_latent_random : bool, default=True  # TODO? temporary - another prespecified approach?
        Allow random variables to be included in the model.

    allow_latent_bcvars : bool, default=True  # TODO? temporary - another prespecified approach?
        Allow transformation variables to be included in the model.

    base_alt : int, float, or str, default=None
        Base alternative.
    """
    def __init__(self, df, varnames, df_test=None, dist=None, code_name="search",
                 avail=None, test_av=None, avail_latent=None,
                 test_avail_latent=None, weights=None,
                 choice_set=None,
                 choice_var=None, test_choice_var=None,
                 alt_var=None, test_alt_var=None,
                 choice_id=None, test_choice_id=None, ind_id=None,
                 test_ind_id=None, isvarnames=None,
                 asvarnames=None, trans_asvars=None, ftol=1e-5, gtol=1e-5,
                 gtol_membership_func=1e-5,
                 ftol_lccm=1e-4,
                 ftol_lccmm=1e-4,
                 latent_class=False, num_classes=2, maxiter=200, n_draws=1000,
                 multi_objective=False,
                 multi_objective_variable='BIC',
                 p_val=0.05,
                 chosen_alts_test=None,
                 test_weight_var=None,
                 allow_latent_random=True,  # TODO: latent only?
                 allow_latent_bcvars=True,
                 allow_latent_corvars=True,
                 intercept_opts=None, base_alt=None,
                 val_share=0.25,
                 logger_level=None,
                 seed=None):
        """Initialise the search class.

        """
        if dist is None:
            logger.debug("Dist not specifying. Allowing all random distributions.")
            dist = ['n', 'ln', 'tn', 'u', 't']  # NOTE: removed 'f'

        self.dist = dist  # List of random distributions to select from
        self.code_name = code_name
        self.current_date = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")

        logger_name = "logs/" + code_name + "_" + self.current_date + ".log"
        try:
            os.makedirs("logs/", exist_ok=True)
        except Exception as e:
            print('e: ', e)
            logger_name = code_name + "_" + self.current_date + ".log"
        if logger_level is None:
            logger_level = logging.INFO
        logging.basicConfig(filename=logger_name, level=logger_level)
        self.logger_name = logger_name

        self.df = df
        self.varnames = varnames

        self.val_share = val_share

        random_state = None
        if seed:
            random_state = np.random.RandomState(seed)
        random_state = random_state or np.random
        self.random_state = random_state
        if df_test is None and multi_objective:
            # create test dataset
            if ind_id is not None:
                N = len(np.unique(ind_id))
                training_size = int((1-val_share)*N)
                ids = random_state.choice(np.unique(ind_id), training_size, replace=False)
                train_idx = [ii for ii, id_val in enumerate(ind_id) if id_val in ids]
                test_idx = [ii for ii, id_val in enumerate(ind_id) if id_val not in ids]

            else:
                try:
                    N = len(np.unique(df['id'].values))
                    id_key = 'id'
                except KeyError:
                    N = len(np.unique(df['ID'].values))
                    id_key = 'ID'
                training_size = int(val_share*N)
                ids = random_state.choice(N, training_size, replace=False)
                train_idx = [ii for ii, id_val in enumerate(df[id_key]) if id_val in ids]
                test_idx = [ii for ii, id_val in enumerate(df[id_key]) if id_val not in ids]

                train_idx = [ii for ii, id_val in enumerate(df['id']) if id_val in ids]
                test_idx = [ii for ii, id_val in enumerate(df['id']) if id_val not in ids]

            df_train = df.loc[train_idx, :]
            df_test = df.loc[test_idx, :]

            self.df = df_train

            if avail is not None:
                test_av = avail[test_idx]
                avail = avail[train_idx]

            if avail_latent is not None:
                avail_latent_original = avail_latent
                J = len(np.unique(alt_var))
                avail_latent = [np.zeros((int(len(train_idx)/J), J)) for i in range(num_classes)]
                test_avail_latent = [np.zeros((int(len(test_idx)/J), J)) for i in range(num_classes)]
                for ii, avail_l in enumerate(avail_latent_original):
                    if avail_l is None:
                        avail_latent[ii] = None
                        test_avail_latent[ii] = None
                    else:
                        row = avail_latent_original[ii][0, :]  # TODO? Make more flexible
                        avail_latent[ii] = np.tile(row, ((int(len(train_idx)/J), 1)))
                        test_avail_latent[ii] = np.tile(row, ((int(len(test_idx)/J), 1)))

            if weights is not None:
                test_weight_var = weights[test_idx]
                weights = weights[train_idx]

            if choice_id is not None:
                test_choice_id = choice_id[test_idx]
                choice_id = choice_id[train_idx]

            if ind_id is not None:
                test_ind_id = ind_id[test_idx]
                ind_id = ind_id[train_idx]

            if alt_var is not None:
                test_alt_var = alt_var[test_idx]
                alt_var = alt_var[train_idx]

            if choice_var is not None:
                test_choice_var = choice_var[test_idx]
                choice_var = choice_var[train_idx]

        self.df_test = df_test

        if isvarnames is None:
            isvarnames = []
        self.isvarnames = isvarnames

        if asvarnames is None:
            asvarnames = []
        self.asvarnames = asvarnames

        if trans_asvars is None:
            trans_asvars = []
        self.trans_asvars = trans_asvars
        self.ftol = ftol
        self.ftol_lccm = ftol_lccm
        self.ftol_lccmm = ftol_lccmm
        self.gtol = gtol
        self.gtol_membership_func = gtol_membership_func
        self.latent_class = latent_class
        self.num_classes = num_classes
        self.maxiter = maxiter
        self.n_draws = n_draws
        self.multi_objective = multi_objective
        if (multi_objective_variable == 'loglik' or
            multi_objective_variable == 'loglikelihood'):
            # Rename to LL
            multi_objective_variable = 'LL'
        multi_objective_variable = multi_objective_variable.upper()
        if (multi_objective_variable != 'BIC' and
            multi_objective_variable != 'AIC' and
            multi_objective_variable != 'MAE' and
            multi_objective_variable != 'LL'):
            raise ValueError('Must select BIC, AIC, LL or MAE for multi-objective')
        self.multi_objective_variable = multi_objective_variable
        self.p_val = p_val

        self.avail = avail
        self.avail_latent = avail_latent
        self.weights = weights
        self.choice_set = choice_set
        self.choice_var = choice_var
        self.alt_var = alt_var
        self.choice_id = choice_id
        self.ind_id = ind_id

        self.test_av = test_av
        self.test_avail_latent = test_avail_latent
        self.test_weight_var = test_weight_var
        self.test_choice_id = test_choice_id
        self.test_ind_id = test_ind_id
        self.test_alt_var = test_alt_var
        self.test_choice_var = test_choice_var

        self.allow_latent_random = allow_latent_random
        self.allow_latent_bcvars = allow_latent_bcvars
        self.allow_latent_corvars = allow_latent_corvars

        self.intercept_opts = intercept_opts
        self.base_alt = base_alt

        if chosen_alts_test is None and self.multi_objective:
            try:
                chosen_alts_test = test_alt_var[test_choice_var == 1]
            except Exception as e:
                logger.error("Exception: {}".format(e))
                # make lowercase choice if only uppercase, stop further bugs
                self.df_test['choice'] = self.df_test['CHOICE']
                chosen_alts_test = df_test.query('CHOICE == True')['alt']

        self.obs_freq = None
        if self.multi_objective:
            J = len(np.unique(alt_var))
            obs_freq = np.zeros(J)
            for ii, alt in enumerate(np.unique(alt_var)):
                alt_sum = np.sum(chosen_alts_test == alt)
                obs_freq[ii] = alt_sum
            self.obs_freq = obs_freq/(df_test.shape[0]/len(choice_set))

        # Default pre-specifications
        # To specify - set after search is initiated

        psasvar_ind, psisvar_ind, pspecdist_ind, ps_bcvar_ind, ps_corvar_ind = \
            self._prep_inputs(asvarnames=self.asvarnames, isvarnames=self.isvarnames)

        ps_asvars, ps_isvars, ps_randvars, ps_bcvars, ps_corvars, ps_bctrans, \
            ps_cor, ps_interaction, ps_intercept = \
            self.prespec_features(psasvar_ind, psisvar_ind, pspecdist_ind,
                                  ps_bcvar_ind, ps_corvar_ind, self.isvarnames,
                                  self.asvarnames)
        self.ps_asvars = ps_asvars
        self.ps_isvars = ps_isvars
        self.ps_intercept = ps_intercept
        self.ps_randvars = ps_randvars
        self.ps_corvars = ps_corvars
        self.ps_bctrans = ps_bctrans
        self.ps_cor = ps_cor
        self.ps_bcvars = ps_bcvars
        self.ps_interaction = ps_interaction

        # all_estimated_solutions used to avoid generating same sol twice
        self.all_estimated_solutions = []

    def prespec_features(self, ind_psasvar, ind_psisvar, ind_pspecdist,
                         ind_psbcvar, ind_pscorvar, isvarnames, asvarnames):
        """
        Generates lists of features that are predetermined by the modeller for
        the model development
        Inputs:
        (1) ind_psasvar - indicator list for prespecified asvars
        (2) ind_psisvar - indicator list for prespecified isvars
        (3) ind_pspecdist - indicator list for vars with prespecified coefficient distribution
        (4) ind_psbcvar - indicator list for vars with prespecified transformation
        (5) ind_pscorvar - indicator list for vars with prespecified correlation
        """
        # prespecified alternative-specific variables
        ps_asvar_pos = [i for i, x in enumerate(ind_psasvar) if x == 1]
        ps_asvars = [var for var in asvarnames if asvarnames.index(var) in ps_asvar_pos]

        # prespecified individual-specific variables
        ps_isvar_pos = [i for i, x in enumerate(ind_psisvar) if x == 1]
        ps_isvars = [var for var in isvarnames if isvarnames.index(var) in ps_isvar_pos]

        # prespecified coeff distributions for variables
        ps_rvar_ind = dict(zip(asvarnames, ind_pspecdist))
        ps_randvars = {k: v for k, v in ps_rvar_ind.items() if v != "any"}

        # prespecified non-linear transformed variables
        ps_bcvar_pos = [i for i, x in enumerate(ind_psbcvar) if x == 1]
        ps_bcvars = [var for var in asvarnames if asvarnames.index(var) in ps_bcvar_pos]

        # prespecified correlated variables
        ps_corvar_pos = [i for i, x in enumerate(ind_pscorvar) if x == 1]
        ps_corvars = [var for var in asvarnames if asvarnames.index(var) in ps_corvar_pos]

        ps_bctrans = None
        ps_cor = None
        ps_interaction = None
        ps_intercept = None

        return (ps_asvars, ps_isvars, ps_randvars, ps_bcvars, ps_corvars,
                ps_bctrans, ps_cor, ps_interaction, ps_intercept)

    def avail_features(self):
        """
        Generates lists of features that are available to select from for model development
        Inputs:
        (1) asvars_ps - list of prespecified asvars
        (2) isvars_ps - list of prespecified isvars
        (3) rvars_ps - list of vars and their prespecified coefficient distribution
        (4) bcvars_ps - list of vars that include prespecified transformation
        (5) corvars_ps - list of vars with prespecified correlation
        """
        # available alternative-specific variables for selection
        avail_asvars = [var for var in self.asvarnames if var not in self.ps_asvars]

        # available individual-specific variables for selection
        avail_isvars = [var for var in self.isvarnames if var not in self.ps_isvars]

        # available variables for coeff distribution selection
        avail_rvars = [var for var in self.asvarnames if var not in self.ps_randvars.keys()]

        # available alternative-specific variables for transformation
        avail_bcvars = [var for var in self.asvarnames if var not in self.ps_bcvars]

        # available alternative-specific variables for correlation
        avail_corvars = [var for var in self.asvarnames if var not in self.ps_corvars]

        return (avail_asvars, avail_isvars, avail_rvars, avail_bcvars, avail_corvars)

    def df_coeff_col(self, asvars):
        """
        This function creates dummy dataframe columns for variables
        which are randomly selected to be estimated with
        alternative-specific coefficients.
        Inputs:
            asvars: list of variable names to be considered
            choice_set: list of available alternatives
            var_alt: dataframe column consisting of alternative variable
        Output:
            List of alternative-specific variables considered for
            model development
        """
        # Generate a random boolean array with the same length as asvars
        rand_arr = self.random_state.choice([True, False], len(asvars))

        # Initialize a list for storing new alternative-specific variables
        asvars_new = []

        # Extract variables randomly chosen to have alternative-specific coefficients
        alt_spec_vars = [var for ii, var in enumerate(asvars) if rand_arr[ii]]

        # Create dummy columns for the selected variables
        for alt_var in alt_spec_vars:
            for choice in self.choice_set:
                col_name = f"{alt_var}_{choice}"
                self.df[col_name] = self.df[alt_var] * (self.alt_var == choice)
                if self.multi_objective:
                    self.df_test[col_name] = self.df_test[alt_var] * (self.alt_var == choice)
                asvars_new.append(col_name)

        # Add the remaining variables that were not selected for alternative-specific coefficients
        asvars_new.extend([var for ii, var in enumerate(asvars) if not rand_arr[ii]])
        return asvars_new

    # Removing redundancy if the same variable is included in the model with and without transformation
    # or with a combination of alt-spec and generic coefficients
    def remove_redundant_asvars(self, asvar_list, transasvars, asvarnames):
        redundant_asvars = [s for s in asvar_list if any(xs in s for xs in transasvars)]
        unique_vars = [var for var in asvar_list if var not in redundant_asvars]

        # When transformations are not applied, the redundancy is created if a variable has both generic & alt-spec co-effs
        if len(transasvars) == 0:
            gen_var_select = [var for var in asvar_list if var in asvarnames]
            alspec_final = [var for var in asvar_list if var not in gen_var_select]
        else:
            gen_var_select = []
            alspec_final = []
            for var in transasvars:
                redun_vars = [item for item in asvar_list if var in item]
                gen_var = [var for var in redun_vars if var in asvarnames]
                if gen_var:
                    gen_var_select.append(self.random_state.choice(gen_var))
                alspec_redun_vars = [item for item in asvar_list
                                     if var in item and item not in asvarnames]
                trans_alspec = [i for i in alspec_redun_vars
                                if any(bc_l for bc_l in boxc_l if bc_l in i)]
                lin_alspec = [var for var in alspec_redun_vars
                              if var not in trans_alspec]
                if self.random_state.randint(2):
                    alspec_final.extend(lin_alspec)
                else:
                    alspec_final.extend(trans_alspec)

        if len(gen_var_select) and len(alspec_final) != 0:
            if self.random_state.randint(2):
                final_asvars = gen_var_select
                final_asvars.extend(unique_vars)
            else:
                final_asvars = alspec_final
                final_asvars.extend(unique_vars)

        elif len(gen_var_select) != 0:
            final_asvars = gen_var_select
            final_asvars.extend(unique_vars)
        else:
            final_asvars = alspec_final
            final_asvars.extend(unique_vars)

        final_asvars = list(dict.fromkeys(final_asvars))

        return final_asvars

    def generate_sol(self):
        """
        Generates list of random model features considering prespecifications
        Inputs:
        (2) asvars_avail - list of available asvars for random selection
        (3) isvars_avail - list of available isvars for random selection
        (4) rvars_avail - list of available vars for randomly selected coefficient distribution
        (5) bcvars_avail - list of available vars for random selection of transformation
        (6) corvars_avail - list of available vars for random selection of correlation
        ## Prespecification information
        (1) asvars_ps - list of prespecified asvars
        (2) isvars_ps - list of prespecified isvars
        (3) rvars_ps - list of vars and their prespecified coefficient distribution
        (4) bcvars_ps - list of vars that include prespecified transformation
        (5) corvars_ps - list of vars with prespecified correlation
        (6) bctrans_ps - prespecified transformation boolean
        (7) cor_ps - prespecified correlation boolean
        (8) intercept_ps - prespecified intercept boolean

        """
        # Randomly select alternative-specific variables and include prespecs
        ind_availasvar = []
        for i in range(len(self.avail_asvars)):
            ind_availasvar.append(self.random_state.randint(2))
        asvar_select_pos = [i for i, x in enumerate(ind_availasvar) if x == 1]
        asvars_1 = [var for var in self.avail_asvars if self.avail_asvars.index(var)
                    in asvar_select_pos]
        asvars_1.extend(self.ps_asvars)

        asvars_new = self.remove_redundant_asvars(asvars_1, self.trans_asvars,
                                                  self.asvarnames)
        asvars = asvars_new

        # Randomly select individual-specific variables and include prespecs
        ind_availisvar = []
        for i in range(len(self.avail_isvars)):
            ind_availisvar.append(self.random_state.randint(2))
        isvar_select_pos = [i for i, x in enumerate(ind_availisvar) if x == 1]
        isvars = [var for var in self.avail_isvars if self.avail_isvars.index(var) in isvar_select_pos]
        isvars.extend(self.ps_isvars)

        # Determine if the model should include an intercept
        if self.ps_intercept is None:
            asc_ind = self.random_state.rand() < 0.5
        else:
            asc_ind = self.ps_intercept

        # Prepare class and member variables for latent class models
        asc_var = ['_inter'] if asc_ind else []  # Add intercept to class param
        class_vars = self.avail_asvars + asc_var
        member_vars = ['_inter'] + self.avail_isvars
        class_params_spec = None
        member_params_spec = None

        # Generate class and member variable specifications for latent class models
        if self.latent_class:
            class_params_spec = np.array(np.repeat('tmp', self.num_classes),
                                         dtype='object')

            member_params_spec = np.array(np.repeat('tmp', self.num_classes-1),
                                          dtype='object')

            for i in range(self.num_classes):
                tmp_class_spec = np.array([])
                for var in class_vars:
                    # NOTE: 0.6 is arbitrary here... kept high...
                    if self.random_state.uniform() < 0.6:  # prob of accepting asvar
                        tmp_class_spec = np.append(tmp_class_spec, var)
                class_params_spec[i] = np.sort(tmp_class_spec)

            tmp_member_spec = np.array([])
            for var in member_vars:
                # NOTE: 0.6 is arbitrary here... kept high...
                if self.random_state.uniform() < 0.6:  # prob of accepting asvar
                    tmp_member_spec = np.append(tmp_member_spec, var)
            for i in range(self.num_classes-1):
                member_params_spec[i] = np.sort(tmp_member_spec)

        # Determine random coefficient distributions for selected variables
        r_dist = []
        avail_rvar = [var for var in asvars if var in self.avail_rvars]

        if class_params_spec is not None:
            class_vars = np.unique(np.concatenate(class_params_spec))
            avail_rvar = [a_rvar for a_rvar in avail_rvar if a_rvar in class_vars]

        for i in range(len(avail_rvar)):
            r_dist.append(self.random_state.choice(self.dist))

        rvars = dict(zip(avail_rvar, r_dist))
        rvars.update(self.ps_randvars)

        rand_vars = {k: v for k, v in rvars.items() if v != "f" and k in asvars}
        r_dis = [dis for dis in self.dist if dis != "f"]
        for var in self.ps_corvars:
            if var in asvars and var not in rand_vars.keys():
                rand_vars.update({var: self.random_state.choice(r_dis)})

        rand_vars = dict(sorted(rand_vars.items()))  # sort randvars
        if not self.avail_rvars:  # additional safety point
            rand_vars = {}

        # Determine if the model should include Box-Cox transformations
        if self.ps_bctrans is None:
            bctrans = self.random_state.rand() < 0.5
        else:
            bctrans = self.ps_bctrans

        # Randomly select variables for Box-Cox transformations and include prespecified ones
        if bctrans and self.allow_latent_bcvars:
            ind_availbcvar = []
            for i in range(len(self.avail_bcvars)):
                ind_availbcvar.append(self.random_state.randint(2))
            bcvar_select_pos = [i for i, x in enumerate(ind_availbcvar) if x == 1]
            bcvars = [var for var in self.avail_bcvars if self.avail_bcvars.index(var) in bcvar_select_pos]
            bcvars.extend(self.ps_bcvars)
            bc_vars = [var for var in bcvars if var in asvars and var not in self.ps_corvars]
        else:
            bc_vars = []

        # Determine if the model should include correlated random parameters
        if self.ps_cor is None:
            cor = self.random_state.rand() < 0.5
        else:
            cor = self.ps_cor

        # Randomly select variables for correlated random parameters and include prespecified ones
        if cor:
            ind_availcorvar = []
            for i in range(len(self.avail_corvars)):
                ind_availcorvar.append(self.random_state.randint(2))
            corvar_select_pos = [i for i, x in enumerate(ind_availcorvar)
                                 if x == 1]
            corvars = [var for var in self.avail_corvars if self.avail_corvars.index(var)
                       in corvar_select_pos]
            corvars.extend(self.ps_corvars)
            corvars = [var for var in corvars if var in rand_vars.keys()
                       and var not in bc_vars]
            if len(corvars) < 2:
                cor = False
                corvars = []
        else:
            corvars = []

        # Create Solution object with generated and prespecified model features
        sol = Solution(asvars=asvars, isvars=isvars, bcvars=bc_vars,
                       corvars=corvars, bctrans=bctrans, cor=cor,
                       randvars=rand_vars,
                       class_params_spec=class_params_spec,
                       member_params_spec=member_params_spec,
                       asc_ind=asc_ind)
        return sol

    def fit_model(self, sol):
        """Fit model specified in the solution."""
        rand_vars = sol['randvars']
        sig_member = []

        sol_already_generated = self.check_sol_already_generated(sol)
        if sol_already_generated:
            bic, loglik, multi_val = 10000000.0, None, None
            asvars, isvars, randvars, bcvars, corvars = [], [], {}, [], []
            conv, sig, coefs = False, [], []
            return (bic, loglik, multi_val, asvars, isvars, randvars, bcvars, corvars,
                    conv, sig, sig_member, coefs)

        if bool(rand_vars):
            if self.latent_class:
                try:
                    bic, loglik, multi_val, asvars, isvars, randvars, bcvars, corvars, \
                        conv, sig, sig_member, coefs = self.fit_lccmm(sol)
                except Exception as e:
                    logger.debug("Exception during fit_lccmm: {}".format(e))
                    raise e
            else:
                logger.debug("estimating an MXL model")
                bic, loglik, multi_val, asvars, isvars, randvars, bcvars, corvars, \
                    conv, sig, coefs = self.fit_mxl(sol)
        else:
            if self.latent_class:
                try:
                    bic, loglik, multi_val, asvars, isvars, randvars, bcvars, corvars, \
                        conv, sig, sig_member, coefs = self.fit_lccm(sol)
                except Exception as e:
                    logger.debug("Exception during fit_lccm: {}".format(e))
                    raise e
            else:
                logger.debug("estimating an MNL model")
                bic, loglik, multi_val, asvars, isvars, randvars, bcvars, corvars, \
                    conv, sig, coefs = self.fit_mnl(sol)

        self.all_estimated_solutions.append(sol)
        logger.info(f'Model converged: {conv}')
        return (bic, loglik, multi_val, asvars, isvars, randvars, bcvars,
                corvars, conv, sig, sig_member, coefs)

    def fit_mnl(self, sol):
        """
        Estimates multinomial model for the generated solution.

        Parameters
        ----------
        sol : Solution
            Solution object containing the model specification.

        Returns
        """
        as_vars = sol['asvars']
        is_vars = sol['isvars']
        asc_ind = sol['asc_ind']
        bcvars = sol['bcvars']
        neg_bcvar = [x for x in bcvars if any(self.df[x].values < 0)]
        bcvars = [x for x in bcvars if x not in neg_bcvar]
        try:
            all_vars = as_vars + is_vars

            X = self.df[all_vars].values
            y = self.choice_var
            seed = self.random_state.randint(2**31 - 1)

            model = MultinomialLogit()
            model.fit(X, y, varnames=all_vars, isvars=is_vars,
                      alts=self.alt_var,
                      ids=self.choice_id, fit_intercept=asc_ind,
                      transformation="boxcox", transvars=bcvars,
                      maxiter=self.maxiter, ftol=self.ftol, gtol=self.gtol,
                      avail=self.avail,
                      weights=self.weights, base_alt=self.base_alt,
                      random_state=seed)

            bic = round(model.bic)
            ll = round(model.loglikelihood)
            multi_val = None
            def_vals = model.coeff_

            rand_vars = {}
            corvars = []
            bc_vars = [var for var in bcvars if var not in self.isvarnames]

            old_stdout = sys.stdout
            log_file = open(self.logger_name, "a")
            sys.stdout = log_file
            model.summary()
            sys.stdout = old_stdout
            log_file.close()

            conv = model.convergence
            pvals = model.pvalues
            coef_names = model.coeff_names

            # Validation
            if self.multi_objective:
                X_test = self.df_test[all_vars].values
                y_test = self.test_choice_var
                seed = self.random_state.randint(2**31 - 1)

                # Calculating MAE
                model = MultinomialLogit()
                model.fit(X_test, y_test, varnames=all_vars, isvars=is_vars,
                          alts=self.alt_var, ids=self.test_choice_id,
                          fit_intercept=asc_ind,
                          transformation="boxcox", transvars=bcvars,
                          maxiter=0, init_coeff=def_vals, gtol=self.gtol,
                          avail=self.test_av, weights=self.test_weight_var,
                          base_alt=self.base_alt, random_state=seed)

                # Choice frequecy obtained from estimated model applied on testing sample
                predicted_probabilities_val = model.pred_prob * 100
                obs_freq = model.obs_prob * 100

                MAE = round((1/len(self.choice_set)) * (np.sum(np.abs(predicted_probabilities_val - obs_freq))), 2)
                logger.info(f"MAE: {MAE}")
                logger.info(f"Out of sample log-likelihood: {model.loglikelihood}")
                if self.multi_objective_variable == "MAE":
                    multi_val = MAE
                if self.multi_objective_variable == "LL":
                    multi_val = model.loglikelihood
                if self.multi_objective_variable == "BIC":
                    multi_val = model.bic
                if self.multi_objective_variable == "AIC":
                    multi_val = model.aic
        except Exception as e:
            logger.error("Exception in fit_mnl: {}".format(str(e)))
            bic = 1000000
            multi_val = 10000000.0
            ll = 1000000
            as_vars = []
            is_vars = []
            rand_vars = {}
            bc_vars = []
            corvars = []
            conv = False
            pvals = []
            coef_names = []

        logger.debug("model BIC: {}".format(bic))
        logger.debug("model LL: {}".format(ll))
        if self.multi_objective:
            logger.debug("multi_val: {}".format(multi_val))
        logger.debug("model convergence: {}".format(conv))
        logger.debug("dof: {}".format(len(coef_names)))

        if any(coef_name for coef_name in coef_names if coef_name.startswith("lambda.")):
            logger.debug("model type is nonlinear MNL")
        else:
            logger.debug("model type is MNL")

        return (bic, ll, multi_val, as_vars, is_vars, rand_vars, bc_vars,
                corvars, conv, pvals, coef_names)

    def fit_mxl(self, sol):
        """
        Estimates the model for the generated solution
        Inputs:
        (1) dat: dataframe in csv
        (2) as_vars: list of alternative-specific variables
        (3) is_vars: list of individual-specific variables
        (4) bcvars: list of box-cox variables
        (5) choice: df column with choice variable
        (6) corvars: list of variables allowed to correlate
        (7) alt: df column with alternative variables
        (8) choice_id: df column with choice situation id
        (9) id_val: df column with individual id
        (10) asc_ind: boolean for fit_intercept
        """
        as_vars = sol['asvars']
        is_vars = sol['isvars']
        asc_ind = sol['asc_ind']
        bcvars = sol['bcvars']
        rand_vars = sol['randvars']
        corvars = sol['corvars']
        all_vars = as_vars + is_vars
        X = self.df[all_vars]
        y = self.choice_var
        seed = self.random_state.randint(2**31 - 1)

        bcvars = [var for var in bcvars if var not in self.isvarnames]
        neg_bcvar = [x for x in bcvars if any(self.df[x].values < 0)]
        bcvars = [x for x in bcvars if x not in neg_bcvar]

        try:
            model = MixedLogit()
            model.fit(X,
                      y,
                      varnames=all_vars,
                      alts=self.alt_var,
                      isvars=is_vars,
                      ids=self.choice_id,
                      panels=self.ind_id,
                      randvars=rand_vars,
                      n_draws=self.n_draws,
                      fit_intercept=asc_ind,
                      correlation=corvars,
                      transformation="boxcox",
                      transvars=bcvars,
                      maxiter=self.maxiter,
                      avail=self.avail,
                      ftol=self.ftol,
                      gtol=self.gtol,
                      weights=self.weights,
                      base_alt=self.base_alt,
                      random_state=seed,
                      save_fitted_params=False  # speed-up computation
                      )
            bic = round(model.bic)
            ll = round(model.loglikelihood)
            multi_val = None
            def_vals = model.coeff_
            old_stdout = sys.stdout
            log_file = open(self.logger_name, "a")
            sys.stdout = log_file
            model.summary()
            conv = model.convergence
            pvals = model.pvalues
            coef_names = model.coeff_names

            sys.stdout = old_stdout
            log_file.close()
            if self.multi_objective:
                # Validation
                X_test = self.df_test[all_vars].values
                y_test = self.test_choice_var

                # MAE
                model = MixedLogit()
                model.fit(X_test, y_test, varnames=all_vars,
                          alts=self.test_alt_var,
                          isvars=is_vars,
                          ids=self.test_choice_id, panels=self.test_ind_id,
                          randvars=rand_vars, n_draws=self.n_draws,
                          fit_intercept=asc_ind, correlation=corvars,
                          transformation="boxcox",
                          transvars=bcvars, avail=self.test_av, maxiter=0,
                          init_coeff=def_vals, gtol=self.gtol,
                          weights=self.test_weight_var,
                          base_alt=self.base_alt, random_state=seed,
                          save_fitted_params=False  # speed-up computation
                          )
                # Calculating MAE
                # Choice frequecy obtained from estimated model applied on testing sample
                if dev.using_gpu:
                    pred_prob = dev.to_cpu(model.pred_prob)
                else:
                    pred_prob = model.pred_prob
                predicted_probabilities_val = pred_prob * 100
                obs_freq = model.obs_prob * 100

                MAE = round((1/len(self.choice_set))*(np.sum(abs(predicted_probabilities_val -
                                                        obs_freq))), 2)
                logger.info(f"MAE: {MAE}")
                logger.info(f"Out of sample log-likelihood: {model.loglikelihood}")
                if self.multi_objective_variable == "MAE":
                    multi_val = MAE
                if self.multi_objective_variable == "BIC":
                    multi_val = model.bic
                if self.multi_objective_variable == "LL":
                    multi_val = model.loglikelihood
                if self.multi_objective_variable == "AIC":
                    multi_val = model.aic
        except Exception as e:
            logger.error("Exception in fit_mxl: {}".format(str(e)))
            bic = 1000000
            multi_val = 1000000
            ll = 1000000
            as_vars = []
            is_vars = []
            rand_vars = {}
            bcvars = []
            corvars = []
            conv = False
            pvals = []
            coef_names = []

        if any(l for l in coef_names if l.startswith("chol.")):
            if any(l for l in coef_names if l.startswith("lambda.")):
                logger.debug("model type is nonlinear correlated MXL")
            else:
                logger.debug("model type is linear correlated MXL")
        elif any(l for l in coef_names if l.startswith("lambda.")):
            logger.debug("model type is nonlinear MXL")
        else:
            logger.debug("model type is MXL")

        logger.debug("model BIC: {}".format(bic))
        logger.debug("model LL: {}".format(ll))
        if self.multi_objective:
            logger.debug("multi_val: {}".format(multi_val))
        logger.debug("model convergence: {}".format(conv))
        logger.debug("dof: {}".format(len(coef_names)))
        return (bic, ll, multi_val, as_vars, is_vars, rand_vars, bcvars,
                corvars, conv, pvals, coef_names)

    def fit_lccm(self, sol):
        """Estimates multinomial model for the generated solution.
        Inputs:
        (1) dat in csv
        (2) as_vars: list of alternative-specific variables
        (3) is_vars: list of individual-specific variables
        (4) num_classes: number of latent classes
        (5) bcvars: list of box-cox variables
        (6) choice: df column with choice variable
        (7) alt: df column with alternative variables
        (8) choice_id: df column with choice situation id
        """
        bcvars = sol['bcvars']

        neg_bcvar = [x for x in bcvars if any(self.df[x].values < 0)]
        bcvars = [x for x in bcvars if x not in neg_bcvar]

        corvars = sol['corvars']
        class_params_spec = sol['class_params_spec']
        member_params_spec = sol['member_params_spec']

        logger.debug('bcvars: {}'.format(bcvars))
        logger.debug('class_params_spec: {}'.format(class_params_spec))
        logger.debug('member_params_spec: {}'.format(member_params_spec))

        class_vars = list(np.concatenate(class_params_spec))
        member_vars = list(np.concatenate(member_params_spec))
        all_vars = class_vars + member_vars

        transvars = [var for var in bcvars if var in class_vars]
        if transvars != bcvars:
            logger.warning("Model transvar not in class_params_spec")

        # remove _inter
        all_vars = [var_name for var_name in all_vars if var_name != '_inter']
        all_vars = np.unique(all_vars)
        X = self.df[all_vars]
        y = self.choice_var
        seed = self.random_state.randint(2**31 - 1)
        model = LatentClassModel()
        if self.num_classes is None:
            optimal_num, model = \
                model.optimal_class_fit(X,
                                        y,
                                        varnames=all_vars,
                                        alts=self.alt_var,
                                        ids=self.choice_id,
                                        transformation="boxcox",
                                        transvars=transvars,
                                        maxiter=self.maxiter,
                                        gtol=self.gtol,
                                        avail=self.avail,
                                        weights=self.weights,
                                        num_classes=self.num_classes,
                                        avail_latent=self.avail_latent,
                                        intercept_opts=self.intercept_opts,
                                        random_state=seed)
        else:
            logger.debug('num_classes: {}'.format(self.num_classes))
            model.fit(X, y, varnames=all_vars,
                      class_params_spec=class_params_spec,
                      member_params_spec=member_params_spec,
                      num_classes=self.num_classes,
                      alts=self.alt_var,
                      ids=self.choice_id,
                      transformation="boxcox",
                      transvars=transvars,
                      maxiter=self.maxiter,
                      ftol_lccm=self.ftol_lccm,
                      gtol=self.gtol,
                      gtol_membership_func=self.gtol_membership_func,
                      avail=self.avail,
                      avail_latent=self.avail_latent,
                      intercept_opts=self.intercept_opts,
                      weights=self.weights,
                      random_state=seed)
        bic = round(model.bic)
        ll = round(model.loglikelihood)
        multi_val = None
        init_class_betas = []
        count = 0
        for ii, class_betas in enumerate(class_params_spec):
            class_len = model._get_betas_length(ii)
            init_class_betas.append(model.coeff_[count:count+class_len])
            count += class_len
        rand_vars = {}
        corvars = []

        old_stdout = sys.stdout
        log_file = open(self.logger_name, "a")
        sys.stdout = log_file
        model.summary()
        conv = model.convergence
        pvals = model.pvalues
        pvals_member = model.pvalues_member
        coef_names = model.coeff_names
        member_names = model.coeff_names_member
        logger.debug("model convergence: {}".format(conv))
        sys.stdout = old_stdout
        log_file.close()

        val = model.loglikelihood
        if self.multi_objective:
            def_vals = model.coeff_
            X_test = self.df_test[all_vars].values
            y_test = self.test_choice_var.values

            model.fit(X_test,
                      y_test,
                      varnames=all_vars,
                      alts=self.test_alt_var,
                      class_params_spec=class_params_spec,
                      member_params_spec=member_params_spec,
                      num_classes=self.num_classes,
                      ids=self.test_choice_id,
                      transformation="boxcox",
                      transvars=bcvars,
                      avail=self.test_av,
                      maxiter=0,
                      init_class_betas=init_class_betas,
                      init_class_thetas=model.class_x,
                      init_coeff=def_vals,
                      gtol=self.gtol,
                      weights=self.test_weight_var,
                      validation=True)

            # Choice frequecy obtained from estimated model applied on testing sample
            predicted_probabilities_val = model.pred_prob * 100
            obs_freq = model.obs_prob * 100

            MAE = round((1/len(self.choice_set))*(np.sum(abs(predicted_probabilities_val -
                                                    obs_freq))), 2)
            logger.info(f"MAE: {MAE}")
            logger.info(f"Out of sample log-likelihood: {model.loglikelihood}")

            if self.multi_objective_variable == 'MAE':
                multi_val = MAE
            if self.multi_objective_variable == 'LL':
                multi_val = model.loglikelihood
            if self.multi_objective_variable == 'BIC':
                multi_val = model.bic
            if self.multi_objective_variable == 'AIC':
                multi_val = model.aic
        else:
            logger.debug("Log-likelihood: {}".format(val))

        # default opts for asvars and isvars
        as_vars = []
        is_vars = []
        coef_names = np.concatenate((coef_names, member_names))
        return (bic, ll, multi_val, as_vars, is_vars, rand_vars, transvars,
                corvars, conv, pvals, pvals_member, coef_names)

    def fit_lccmm(self, sol):
        bcvars = sol['bcvars']
        rand_vars = sol['randvars']
        corvars = sol['corvars']
        class_params_spec = sol['class_params_spec']
        member_params_spec = sol['member_params_spec']
        logger.debug("estimating lccmm")
        logger.debug('rand_vars: {}'.format(rand_vars))
        logger.debug('bcvars: {}'.format(bcvars))
        logger.debug('corvars: {}'.format(corvars))

        class_vars = list(np.concatenate(class_params_spec))
        member_vars = list(np.concatenate(member_params_spec))
        all_vars = class_vars + member_vars

        bcvars = [var for var in bcvars if var not in self.isvarnames]
        neg_bcvar = [x for x in bcvars if any(self.df[x].values < 0)]
        bcvars = [x for x in bcvars if x not in neg_bcvar]
        bcvars = [var for var in bcvars if var in class_vars]

        # remove _inter
        all_vars = [var_name for var_name in all_vars if var_name != '_inter']
        all_vars = np.unique(all_vars)

        X = self.df[all_vars]
        y = self.choice_var
        seed = self.random_state.randint(2**31 - 1)

        model = LatentClassMixedModel()
        if self.num_classes is None:
            optimal_num, model = model.fit(X,
                                           y,
                                           varnames=all_vars,
                                           alts=self.alt_var,
                                           ids=self.choice_id,
                                           panels=self.ind_id,
                                           randvars=rand_vars,
                                           n_draws=self.n_draws,
                                           correlation=corvars,
                                           transformation="boxcox",
                                           transvars=bcvars,
                                           maxiter=self.maxiter,
                                           avail=self.avail,
                                           gtol=self.gtol,
                                           weights=self.weights,
                                           grad=True,
                                           num_classes=self.num_classes,
                                           random_state=seed)
        else:
            model.fit(X,
                      y,
                      varnames=all_vars,
                      alts=self.alt_var,
                      class_params_spec=class_params_spec,
                      member_params_spec=member_params_spec,
                      num_classes=self.num_classes,
                      ids=self.choice_id,
                      panels=self.ind_id,
                      randvars=rand_vars,
                      n_draws=self.n_draws,
                      correlation=corvars,
                      transformation="boxcox",
                      transvars=bcvars,
                      maxiter=self.maxiter,
                      avail=self.avail,
                      ftol=self.ftol,
                      ftol_lccmm=self.ftol_lccmm,
                      gtol=self.gtol,
                      gtol_membership_func=self.gtol_membership_func,
                      weights=self.weights,
                      grad=True,
                      random_state=seed,
                      )
        bic = round(model.bic)
        ll = round(model.loglikelihood)
        multi_val = None
        init_class_betas = []
        count = 0
        for ii, class_betas in enumerate(class_params_spec):
            class_len = model._get_betas_length(ii)
            init_class_betas.append(model.coeff_[count:count+class_len])
            count += class_len

        old_stdout = sys.stdout
        log_file = open(self.logger_name, "a")
        sys.stdout = log_file
        model.summary()
        conv = model.convergence
        pvals = model.pvalues
        pvals_member = model.pvalues_member
        coef_names = model.coeff_names
        member_names = model.coeff_names_member

        logger.debug("model convergence: {}".format(model.convergence))
        sys.stdout = old_stdout
        log_file.close()
        if self.multi_objective:
            # Validation
            X_test = self.df_test[all_vars].values
            y_test = self.test_choice_var.values

            model.fit(X_test,
                      y_test,
                      varnames=all_vars,
                      alts=self.test_alt_var,
                      class_params_spec=class_params_spec,
                      member_params_spec=member_params_spec,
                      num_classes=self.num_classes,
                      ids=self.test_choice_id,
                      panels=self.test_ind_id,
                      randvars=rand_vars,
                      n_draws=self.n_draws,
                      correlation=corvars,
                      transformation="boxcox",
                      transvars=bcvars,
                      avail=self.test_av,
                      maxiter=0,
                      init_class_betas=init_class_betas,
                      init_class_thetas=model.class_x,
                      gtol=self.gtol,
                      weights=self.test_weight_var,
                      grad=True,
                      validation=True)

            # Choice frequecy obtained from estimated model applied on testing sample
            predicted_probabilities_val = model.pred_prob * 100
            obs_freq = model.obs_prob * 100

            # Calculate MAE
            MAE = round((1/len(self.choice_set))*(np.sum(abs(predicted_probabilities_val -
                                                    obs_freq))), 2)
            logger.info("MAE: {}".format(MAE))
            logger.info(f"Out of sample log-likelihood: {model.loglikelihood}")

            if self.multi_objective_variable == 'MAE':
                multi_val = MAE
            if self.multi_objective_variable == 'BIC':
                multi_val = model.bic
            if self.multi_objective_variable == 'LL':
                multi_val = model.loglikelihood
            if self.multi_objective_variable == 'AIC':
                multi_val = model.aic
        # default opts for asvars and isvars
        as_vars = []
        is_vars = []
        coef_names = np.concatenate((coef_names, member_names))
        return (bic, ll, multi_val, as_vars, is_vars, rand_vars, bcvars,
                corvars, conv, pvals, pvals_member, coef_names)

    def evaluate_objective_function(self, sol):
        """
        (1) Evaluates the objective function (estimates the model and BIC) for
        a given list of variables (estimates the model coefficeints, LL and BIC)
        (2) If the solution generated in (1) contains statistically insignificant variables,
        a new model is generated by removing such variables and the model is re-estimated
        (3) the functions returns estimated solution only if it converges
        Inputs: lists of variable names, individual specific variables,
        variables with random coefficients,
        name of the choice variable in df, list of alternatives, choice_id,
        individual_id(for panel data) and fit intercept bool
        """

        as_vars = sol['asvars']
        is_vars = sol['isvars']
        rand_vars = sol['randvars']
        bc_vars = sol['bcvars']
        corvars = sol['corvars']
        asc_ind = sol['asc_ind']
        class_params_spec = sol['class_params_spec']
        member_params_spec = sol['member_params_spec']

        all_vars = as_vars + is_vars

        convergence = False

        # default model variables
        sig = None
        sig_member = None
        coefs = []

        if not corvars:
            corvars = []

        logger.debug('class_params_spec: {}'.format(class_params_spec))
        logger.debug('member_params_spec: {}'.format(member_params_spec))

        # Estimate model if input variables are present in specification
        if all_vars:
            logger.debug(("features for round 1: asvars: {}, isvars: {}, "
                          "rand_vars: {}, bc_vars: {}, corvars: {}, "
                          "asc_ind: {}, class_params_spec: {}, "
                          "member_params_spec: {}").format(as_vars, is_vars,
                                                           rand_vars, bc_vars,
                                                           corvars, asc_ind,
                                                           class_params_spec,
                                                           member_params_spec))

            try:
                bic, loglik, multi_val, asvars, isvars, randvars, \
                    bcvars, corvars, convergence, sig, sig_member, coefs = self.fit_model(sol)
                # fix bug when bcvar changed in fit_model
                if bcvars != sol['bcvars']:
                    sol['bcvars'] = bcvars
            except Exception as e:
                logger.warning("Exception fitting model: {}".format(e))
                return (Solution(), False)

            if convergence:
                if not corvars:
                    corvars = []
                logger.debug("solution converged in first round")
                if self.multi_objective:
                    sol.add_objective(bic, loglik=loglik, multi_val=multi_val)
                else:
                    sol.add_objective(bic, loglik=loglik)

                sig_all = sig
                if self.latent_class:
                    sig_all = np.concatenate((sig, sig_member))
                if all(v for v in sig_all <= self.p_val):
                    logger.debug("solution has all sig-values in first  round")
                    return (sol, convergence)
                else:
                    while any([v for v in sig_all if v > self.p_val]):
                        logger.debug("solution contains insignificant coeffs")
                        # create dictionary of {coefficient_names: p_values}
                        logger.debug('sig_all top: {}'.format(sig_all))
                        p_vals = dict(zip(coefs, sig_all))

                        r_dist = [dis for dis in self.dist if dis != 'f']  # list of random distributions
                        # create list of variables with insignificant coefficients
                        non_sig = [k for k, v in p_vals.items()
                                   if v > self.p_val]  # list of non-significant coefficient names
                        logger.debug("non-sig coeffs are: {}".format(non_sig))
                        # keep only significant as-variables
                        asvars_round2 = [var for var in asvars if var not in non_sig]  # as-variables with significant p-vals
                        asvars_round2.extend(self.ps_asvars)
                        logger.debug("asvars_round2 for round 2: {}".format(asvars_round2))
                        # replace non-sig alt-spec coefficient with generic coefficient
                        nsig_altspec = []
                        for var in self.asvarnames:
                            ns_alspec = [x for x in non_sig if x.startswith(var)]
                            nsig_altspec.extend(ns_alspec)
                            nsig_altspec_vars = [var for var in nsig_altspec
                                                 if var not in self.asvarnames]
                            logger.debug("nsig_altspec_vars: {}".format(nsig_altspec_vars))

                        rem_asvars = []
                        # Replacing non-significant alternative-specific coeffs with generic coeffs estimation
                        if not self.latent_class:
                            if nsig_altspec_vars:
                                gen_var = []
                                for i in range(len(nsig_altspec_vars)):
                                    gen_var.extend(nsig_altspec_vars[i].split("_"))
                                gen_coeff = [var for var in self.asvarnames if var
                                             in gen_var]
                                if asvars_round2:
                                    redund_vars = [s for s in gen_coeff if any(s
                                                   in xs for xs in asvars_round2)]
                                    logger.debug("redund_vars for round 2: {}".format(redund_vars))
                                    asvars_round2.extend([var for var in gen_coeff
                                                          if var not in redund_vars])
                                    # rem_asvars = remove_redundant_asvars(asvars_round2,trans_asvars)
                                    logger.debug("asvars_round2 before removing redundancy: {}".format(asvars_round2))
                                    # rem_asvars = remove_redundant_asvars(asvars_round2,trans_asvars)
                                    # checking if remove_redundant_asvars is needed or not
                                    rem_asvars = sorted(list(set(asvars_round2)))
                                else:
                                    rem_asvars = gen_coeff
                            else:
                                rem_asvars = sorted(list(set(asvars_round2)))
                            logger.debug("rem_asvars = {}".format(rem_asvars))

                        rem_class_params_spec = copy.deepcopy(class_params_spec)
                        rem_member_params_spec = copy.deepcopy(member_params_spec)

                        if self.latent_class:
                            i = 0
                            for ii, class_params in enumerate(class_params_spec):
                                tmp_class_params = class_params.copy()
                                delete_idx = []
                                for jj, class_param in enumerate(class_params):
                                    num_coeffs = 1
                                    if class_param == '_inter':
                                        if (hasattr(self, 'intercept_opts') and
                                            self.intercept_opts and
                                            self.intercept_opts['class_intercept_alts']):
                                            num_coefs = 0
                                            for int_opt in self.intercept_opts['class_intercept_alts']:
                                                num_coefs += len(int_opt)
                                        else:
                                            J = len(self.choice_set)
                                            num_coeffs = J - 1
                                    # if class_param.startswith("lambda."):
                                    for k in range(num_coeffs):
                                        if sig[i] > self.p_val:  # assumes sig in class_param_spec order
                                            delete_idx.append(jj)
                                        i += 1
                                    if class_param in bcvars:
                                        if sig[i] > self.p_val:  # assumes sig in class_param_spec order
                                            bcvars = [bc_var for bc_var in bcvars if bc_var not in class_param]
                                        i += 1
                                tmp_class_params = np.delete(tmp_class_params, delete_idx)
                                rem_class_params_spec[ii] = tmp_class_params

                        if self.latent_class:
                            i = 0
                            # pass through to record all significant params
                            for ii, member_params in enumerate(member_params_spec):
                                tmp_member_params = member_params.copy()
                                # delete_idx = []
                                significant_params = []
                                for jj, member_param in enumerate(member_params):
                                    if sig_member[i] < self.p_val:
                                        significant_params.append(member_param)
                                    i += 1

                            # delete variables not significant for any class
                            i = 0
                            for ii, member_params in enumerate(member_params_spec):
                                tmp_member_params = member_params.copy()
                                delete_idx = []
                                for jj, member_param in enumerate(member_params):
                                    if member_param not in significant_params:
                                        delete_idx.append(jj)
                                    i += 1
                                tmp_member_params = np.delete(tmp_member_params, delete_idx)
                                rem_member_params_spec[ii] = tmp_member_params

                        logger.debug("rem_class_params_spec: {}".format(str(rem_class_params_spec)))
                        logger.debug("rem_member_params_spec: {}".format(str(rem_member_params_spec)))

                        # remove insignificant is-variables
                        ns_isvars = []
                        for isvar in self.isvarnames:
                            ns_isvar = [x for x in non_sig if
                                        x.startswith(isvar)]
                            ns_isvars.extend(ns_isvar)
                        remove_isvars = []
                        for i in range(len(ns_isvars)):
                            remove_isvars.extend(ns_isvars[i].split("."))

                        remove_isvar = [var for var in remove_isvars if var
                                        in isvars]
                        most_nsisvar = {x: remove_isvar.count(x) for x
                                        in remove_isvar}
                        rem_isvar = [k for k, v in most_nsisvar.items()
                                     if v == (len(self.choice_set)-1)]
                        isvars_round2 = [var for var in is_vars if var
                                         not in rem_isvar]  # individual specific variables with significant p-vals
                        isvars_round2.extend(self.ps_isvars)

                        rem_isvars = sorted(list(set(isvars_round2)))
                        logger.debug('rem_isvars: {}'.format(rem_isvars))
                        # remove intercept if not significant and not prespecified
                        ns_intercept = [x for x in non_sig if
                                        '_intercept.' in x]  # non-significant intercepts

                        new_asc_ind = asc_ind

                        if self.ps_intercept is None:
                            if len(ns_intercept) == len(self.choice_set)-1:
                                new_asc_ind = False
                        else:
                            new_asc_ind = self.ps_intercept

                        # bug fix when old class params in while loop
                        class_params_spec = copy.deepcopy(rem_class_params_spec)
                        member_params_spec = copy.deepcopy(rem_member_params_spec)

                        # remove insignificant random coefficients
                        ns_sd = [x for x in non_sig if x.startswith('sd.')]  # non-significant standard deviations
                        ns_sdval = [str(i).replace('sd.', '') for i in ns_sd]  # non-significant random variables

                        # non-significant random variables that are not pre-included
                        remove_rdist = [x for x in ns_sdval if x not in
                                        self.ps_randvars.keys() or x not in rem_asvars]
                        # random coefficients for significant variables
                        rem_rand_vars = {k: v for k, v in randvars.items()
                                         if k in rem_asvars and k not in
                                         remove_rdist}
                        rem_rand_vars.update({k: v for k, v in self.ps_randvars.items()
                                              if k in rem_asvars and v != 'f'})
                        logger.debug("rem_rand_vars = {}".format(rem_rand_vars))
                        # including ps_corvars in the model if they are included in rem_asvars
                        for var in self.ps_corvars:
                            if var in rem_asvars and var not in rem_rand_vars.keys():
                                rem_rand_vars.update({var: self.random_state.choice(r_dist)})

                        # remove transformation if not significant and non prespecified
                        ns_lambda = [x for x in non_sig if x.startswith('lambda.')]  # insignificant transformation coefficient
                        ns_bctransvar = [str(i).replace('lambda.', '')
                                         for i in ns_lambda]  # non-significant transformed var
                        rem_bcvars = [var for var in bcvars if var in
                                      rem_asvars and var not in ns_bctransvar
                                      and var not in self.ps_corvars]

                        # remove insignificant correlation
                        ns_chol = [x for x in non_sig if x.startswith('chol.')]  # insignificant cholesky factor
                        ns_cors = [str(i).replace('chol.', '') for i in ns_chol]  # insignicant correlated variables
                        # create a list of variables whose correlation coefficient is insignificant
                        if ns_cors:
                            ns_corvar = []
                            for i in range(len(ns_cors)):
                                ns_corvar.extend(ns_cors[i].split("."))
                            most_nscorvars = {x: ns_corvar.count(x)
                                              for x in ns_corvar}
                            logger.debug('most_nscorvars: {}'.format(most_nscorvars))
                            # check frequnecy of variable names in non-significant coefficients
                            nscorvars = [k for k, v in most_nscorvars.items()
                                         if v >= int(len(corvars)*0.75)]
                            logger.debug('nscorvars: {}'.format(nscorvars))
                            nonps_nscorvars = [var for var in nscorvars
                                               if var not in self.ps_corvars]
                            # if any variable has insignificant correlation
                            # with all other variables, their correlation is
                            # removed from the solution
                            if nonps_nscorvars:
                                # list of variables allowed to correlate
                                rem_corvars = [var for var in
                                               rem_rand_vars.keys() if var
                                               not in nonps_nscorvars and
                                               var not in rem_bcvars]
                            else:
                                rem_corvars = [var for var in
                                               rem_rand_vars.keys() if var
                                               not in rem_bcvars]

                            # need atleast two variables in the list to
                            # estimate correlation coefficients
                            if len(rem_corvars) < 2:
                                rem_corvars = []
                        else:
                            rem_corvars = [var for var in corvars if var in
                                           rem_rand_vars.keys() and var not in
                                           rem_bcvars]
                            if len(rem_corvars) < 2:
                                rem_corvars = []

                        # Evaluate objective function with significant feautures from round 1

                        rem_alvars = rem_asvars + rem_isvars
                        if rem_alvars:
                            if (set(rem_alvars) != set(all_vars) or
                                set(rem_rand_vars) != set(rand_vars) or
                                set(rem_bcvars) != set(bcvars) or
                                set(rem_corvars) != set(corvars) or
                                    new_asc_ind != asc_ind):
                                logger.debug("not same as round 1 model")
                            else:
                                logger.debug("model 2 same as round 1 model")
                                return (sol, convergence)
                            old_sol = copy.deepcopy(sol)
                            sol = Solution(asvars=rem_asvars,
                                           isvars=rem_isvars,
                                           randvars=rem_rand_vars,
                                           bcvars=rem_bcvars,
                                           corvars=rem_corvars,
                                           asc_ind=new_asc_ind,
                                           class_params_spec=rem_class_params_spec,
                                           member_params_spec=rem_member_params_spec
                                           )
                            try:
                                bic, loglik, multi_val, asvars, isvars, randvars, \
                                    bcvars, corvars, convergence, sig, sig_member, coefs = self.fit_model(sol)
                            except Exception as e:
                                logger.warning("Exception fitting model: {}".format(e))
                                return (Solution(), False)
                            sig_all = sig
                            if self.latent_class:
                                sig_all = np.concatenate((sig, sig_member))
                            logger.debug('sig_all - post fit {}'.format(sig_all))
                            if convergence:
                                if self.multi_objective:
                                    sol.add_objective(bic, loglik=loglik, multi_val=multi_val)
                                else:
                                    sol.add_objective(bic, loglik=loglik)

                                if all([v for v in sig_all if v <= self.p_val]):
                                    break
                                if self.latent_class:  # TODO: QUICK FIX INF LOOP
                                    return (sol, convergence)
                                # if only some correlation coefficients or
                                # intercept values are insignificant, we accept
                                # the solution
                                p_vals = dict(zip(coefs, sig_all))
                                non_sig = [k for k, v in p_vals.items()
                                           if v > self.p_val]
                                logger.debug("non_sig in round 2: {}".format(non_sig))

                                sol['asvars'] = [var for var in sol['asvars'] if var not in
                                                 non_sig or var in self.ps_asvars]  # keep only significant vars

                                # Update other features of solution based on sol[1]
                                sol['randvars'] = {k: v for k, v in sol['randvars'].items() if k in sol['asvars']}
                                sol['bcvars'] = [var for var in sol['bcvars'] if var in sol['asvars'] and var not in self.ps_corvars]
                                if sol['corvars']:
                                    sol['corvars'] = [var for var in sol['corvars'] if var in sol['randvars'].keys() and var not in sol['bcvars']]

                                # fit_intercept = False if all intercepts are insignificant
                                if len([var for var in non_sig if var in
                                       ['_intercept.' + var for var
                                        in self.choice_set]]) == len(non_sig):
                                    if len(non_sig) == len(self.choice_set)-1:
                                        sol['asc_ind'] = False
                                        return (sol, convergence)

                                all_ns_int = [x for x in non_sig if x.startswith('_intercept.')]
                                all_ns_cors = [x for x in non_sig if x.startswith('chol.')]

                                all_ns_isvars = []
                                for isvar in self.isvarnames:
                                    ns_isvar = [x for x in non_sig if x.startswith(isvar)]
                                    all_ns_isvars.extend(ns_isvar)

                                irrem_nsvars = all_ns_isvars + all_ns_int + all_ns_cors
                                if all(nsv in irrem_nsvars for nsv in non_sig):
                                    logger.debug("non-significant terms cannot be further eliminated")
                                    return (sol, convergence)

                                if (non_sig == all_ns_cors or
                                    non_sig == all_ns_int or
                                    non_sig == list(set().union(all_ns_cors,
                                                                all_ns_int))):
                                    logger.debug("only correlation coefficients or intercepts are insignificant")
                                    return (sol, convergence)

                                if all([var in self.ps_asvars or var in self.ps_isvars or
                                        var in self.ps_randvars.keys() for var in non_sig]):
                                    logger.debug("non-significant terms are pre-specified")
                                    return (sol, convergence)

                                if (len([var for var in non_sig if var in
                                        ['sd.' + var for var
                                         in self.ps_randvars.keys()]]) == len(non_sig)):
                                    logger.debug("non-significant terms are pre-specified random coefficients")
                                    return (sol, convergence)
                            else:
                                logger.debug("convergence not reached in round 2 so final sol is from round 1")
                                return (old_sol, convergence)
                        else:
                            logger.debug("no vars for round 2")
                            return (sol, convergence)
            else:
                convergence = False
                logger.debug("convergence not reached in round 1")
                return (sol, convergence)
        else:
            logger.debug("no vars when function called first time")
        return (sol, convergence)

    def check_sol_already_generated(self, sol):
        new_har_mem = []

        for sol_i in self.all_estimated_solutions:
            tmp_sol_i = sol_i.copy()
            tmp_sol_i.pop('sol_num', None)
            tmp_sol_i.pop('bic', None)
            tmp_sol_i.pop('multi_val', None)
            tmp_sol_i.pop('loglik', None)
            if self.latent_class:
                tmp_sol_i.pop('asvars', None)
                tmp_sol_i.pop('isvars', None)

            new_har_mem.append(tmp_sol_i)

        sol_i = sol.copy()
        sol_i.pop('sol_num', None)
        sol_i.pop('bic', None)
        sol_i.pop('multi_val', None)
        sol_i.pop('loglik', None)
        if self.latent_class:  # not relevant for latent class models
            sol_i.pop('asvars', None)
            sol_i.pop('isvars', None)

        for har_mem_sol in new_har_mem:
            bool_arr = []
            for sol_k, sol_v in sol_i.items():
                # for object-arrays (e.g. class_params_spec) need a different
                if (hasattr(har_mem_sol[sol_k], 'dtype') and
                   har_mem_sol[sol_k].dtype == 'O'):
                    obj_arr1 = np.concatenate(har_mem_sol[sol_k])
                    obj_arr2 = np.concatenate(sol_v)
                    if (len(obj_arr1) == len(obj_arr2) and
                       np.all(obj_arr1 == obj_arr2)):
                        bool_arr.append(True)
                    else:
                        bool_arr.append(False)
                else:
                    if np.all(har_mem_sol[sol_k] == sol_v):
                        bool_arr.append(True)
                    else:
                        bool_arr.append(False)
            if np.all(bool_arr):
                logger.debug("Sol already generated. Skipping estimation.")
                return True

        return False

    def increase_sol_by_one_class(self, sol):
        if sol['class_params_spec'] is None:
            # solution is mixed/multinomial -> convert to 2 class latent
            asvars = np.array(sol['asvars'])
            isvars = np.array(sol['isvars'])
            num_classes = 2
            class_params_spec = np.array(np.repeat('tmp', num_classes),
                                         dtype='object')
            member_params_spec = np.array(np.repeat('tmp', num_classes-1),
                                dtype='object')

            for i in range(num_classes):
                class_params_spec[i] = asvars
            member_params_spec[0] = isvars
            sol['class_params_spec'] = class_params_spec
            sol['member_params_spec'] = member_params_spec
        else:
            # solution is latent class with n classes -> convert n+1 classes
            class_params_spec = sol['class_params_spec']
            member_params_spec = sol['member_params_spec']

            class_params_spec = np.append(class_params_spec, 'tmp')
            member_params_spec = np.append(member_params_spec, 'tmp')
            class_params_spec[-1] = copy.deepcopy(class_params_spec[-2])
            member_params_spec[-1] = copy.deepcopy(member_params_spec[-2])

            sol['class_params_spec'] = class_params_spec
            sol['member_params_spec'] = member_params_spec

        return sol

    # Initialize harmony memory and opposite harmony memory of size HMS with random slutions
    def initialize_memory(self, HMS):
        """
        Creates two lists (called the harmony memory and opposite harmony memory)
        harmony memory - containing the initial randomly generated solutions
        opposite harmony memory - containing random solutions that include variables not included in harmony memory
        Inputs: harmony memory size (int), all variable names, individual-specific variable, prespecifications provided by user
        """
        HM = []
        opp_HM = []
        # base_model = Solution()

        # HM.append(base_model)

        # Add an MXL with full covriance structure

        # Create initial harmony memory
        unique_HM = []
        dummy_iter = 0  # prevent stuck in while loop
        while dummy_iter < 30000:
            dummy_iter += 1
            logger.info("Initializing harmony at iteration {}".format(dummy_iter))
            sol = self.generate_sol()
            sol, conv = self.evaluate_objective_function(sol)

            if conv:
                HM.append(sol)
                # keep only unique solutions in memory
                used = set()
                unique_HM = [used.add(x['bic']) or x for x in HM
                             if x['bic'] not in used]
                unique_HM = sorted(unique_HM, key=lambda x: x['bic'])
                logger.debug("harmony memory for iteration: {}, is: {}".format(dummy_iter, str(unique_HM)))

            logger.debug("estimating opposite harmony memory")

            # create opposite harmony memory
            # (i.e. solutions that include variables not included in sol)

            opp_sol = self.generate_sol()
            sol_keys = ['asvars', 'isvars', 'randvars', 'bcvars', 'corvars',
                        'bctrans', 'cor']
            for sol_key in sol_keys:
                if not opp_sol[sol_key]:
                    continue
                if isinstance(opp_sol[sol_key], bool):
                    continue
                prespec_name = 'ps_' + sol_key
                if getattr(self, prespec_name):
                    continue
                opp_sol[sol_key] = [v for v in opp_sol[sol_key] if v not in sol[sol_key]]

                if self.ps_intercept is None:
                    opp_sol['asc_ind'] = not sol['asc_ind']

            opp_sol['randvars'] = {k: self.random_state.choice(self.dist)
                                   for k in opp_sol['randvars']
                                   if k in opp_sol['asvars']}

            if not self.avail_rvars:
                opp_sol['randvars'] = {}

            opp_sol['corvars'] = [corvar for corvar in opp_sol['corvars'] if corvar in opp_sol['randvars']]

            opp_sol['bcvars'] = [bcvar for bcvar in opp_sol['bcvars'] if bcvar in opp_sol['asvars']
                                                                      and bcvar not in opp_sol['corvars']]

            if not self.avail_bcvars:
                opp_sol['bcvars'] = []

            if opp_sol['class_params_spec'] is not None and sol['class_params_spec'] is not None:
                # remove randvars not in class params
                for ii, class_param in enumerate(opp_sol['class_params_spec']):
                    opp_sol['class_params_spec'][ii] = np.array([param_i for param_i in class_param
                                                        if param_i not in sol['class_params_spec'][ii]])

            if opp_sol['member_params_spec'] is not None and sol['member_params_spec'] is not None:
                for ii, member_param in enumerate(opp_sol['member_params_spec']):
                    opp_sol['member_params_spec'][ii] = np.array([param_i for param_i in member_param
                                                        if param_i not in sol['member_params_spec'][ii]])

            opp_sol, opp_conv = self.evaluate_objective_function(opp_sol)

            unique_opp_HM = []
            if opp_conv:
                opp_HM.append(opp_sol)
                opp_used = set()
                unique_opp_HM = [opp_used.add(x['bic']) or x for x in opp_HM
                                 if x['bic'] not in opp_used]
                unique_opp_HM = sorted(unique_opp_HM, key=lambda x: x['bic'])
                logger.debug("unique_opp_HM is for iteration: {} is: {}".format(dummy_iter, str(unique_opp_HM)))

            # Final Initial Harmony
            Init_HM = unique_HM + unique_opp_HM

            unique = set()
            unique_Init_HM = [unique.add(x['bic']) or x for x in Init_HM
                              if x['bic'] not in unique]
            unique_Init_HM = [init_sol for _, init_sol in enumerate(unique_Init_HM)
                              if np.abs(init_sol['bic']) < 1000000]

            if len(unique_Init_HM) >= HMS:
                unique_Init_HM = unique_Init_HM[:HMS]
                return unique_Init_HM

        return unique_Init_HM

    def harmony_consideration(self, har_mem, HMCR_itr, itr, HM):
        """
        If a generated random number is less than or equal to the harmony memory consideration rate (HMCR)
        then 90% of a solution already in memory will be randomly selected to build the new solution.
        Else a completely new random solution is generated
        Inputs: harmony memory, HMCR for the current interation, iteration number
        """
        new_sol = Solution()

        Fronts = None
        Pareto = None
        if self.multi_objective:
            har_mem = self.non_dominant_sorting(har_mem)
            Fronts = self.get_fronts(har_mem)
            Pareto = self.pareto(Fronts, har_mem)

        if self.random_state.rand() <= HMCR_itr:
            logger.debug("harmony consideration")
            # randomly choose the position of any one solution in harmony memory
            m_pos = self.random_state.choice(len(har_mem))
            select_new_asvars_index = self.random_state.choice([0, 1],
                                                       size=len(har_mem[m_pos]['asvars']),
                                                       p=[1-HMCR_itr, HMCR_itr])
            select_new_asvars = [i for (i, v) in zip(har_mem[m_pos]['asvars'],
                                                     select_new_asvars_index)
                                                     if v]
            select_new_asvars = list(self.random_state.choice(har_mem[m_pos]['asvars'],
                                                      int((len(har_mem[m_pos]['asvars']))*HMCR_itr),
                                                      replace=False))  # randomly select 90% of the variables from solution at position m_pos in harmony memory
            n_asvars = sorted(list(set().union(select_new_asvars, self.ps_asvars)))
            new_asvars = self.remove_redundant_asvars(n_asvars, self.trans_asvars,
                                                      self.asvarnames)
            new_sol['asvars'] = new_asvars
            logger.debug("new_asvars: {}".format(new_asvars))

            select_new_isvars_index = self.random_state.choice([0, 1],
                                                       size=len(har_mem[m_pos]['isvars']),
                                                       p=[1-HMCR_itr, HMCR_itr])
            select_new_isvars = [i for (i, v) in zip(har_mem[m_pos]['isvars'], select_new_isvars_index) if v]

            new_isvars = sorted(list(set().union(select_new_isvars, self.ps_isvars)))
            logger.debug("new_isvars: {}".format(new_isvars))
            new_sol['isvars'] = new_isvars

            # include distributions for the variables in new solution based on the solution at m_pos in memory
            r_pos = {k: v for k, v in har_mem[m_pos]['randvars'].items() if k
                    in new_asvars}
            logger.debug("r_pos: {}".format(r_pos))
            new_sol['randvars'] = r_pos

            new_bcvars = [var for var in har_mem[m_pos]['bcvars'] if var in new_asvars
                          and var not in self.ps_corvars]
            new_sol['bcvars'] = new_bcvars

            new_corvars = har_mem[m_pos]['corvars']
            if new_corvars:
                new_corvars = [var for var in har_mem[m_pos]['corvars'] if var
                            in r_pos.keys() and var not in new_bcvars]
            new_sol['corvars'] = new_corvars

            # Take fit_intercept from m_pos solution in memory
            intercept = har_mem[m_pos]['asc_ind']
            new_sol['asc_ind'] = intercept

            if har_mem[m_pos]['class_params_spec'] is not None:
                class_params_spec = copy.deepcopy(har_mem[m_pos]['class_params_spec'])
                for ii, class_params in enumerate(class_params_spec):
                    class_params_index = self.random_state.choice([0, 1],
                                                        size=len(class_params),
                                                        p=[1-HMCR_itr, HMCR_itr])
                    class_params_spec[ii] = np.array([i for (i, v) in zip(class_params, class_params_index) if v], dtype=class_params.dtype)
                new_sol['class_params_spec'] = class_params_spec

            if har_mem[m_pos]['member_params_spec'] is not None:
                member_params_spec = copy.deepcopy(har_mem[m_pos]['member_params_spec'])
                for ii, member_params in enumerate(member_params_spec):
                    member_params_index = self.random_state.choice([0, 1],
                                                        size=len(member_params),
                                                        p=[1-HMCR_itr, HMCR_itr])
                    member_params_spec[ii] = np.array([i for (i, v) in zip(member_params, member_params_index) if v], dtype=member_params.dtype)
                new_sol['member_params_spec'] = member_params_spec

            logger.debug("new sol after HMC-1: {}".format(str(new_sol)))
        else:
            logger.debug("harmony not considered")
            # if harmony memory consideration is not conducted, then a new solution is generated

            new_sol = self.generate_sol()
            logger.debug("new sol after HMC-2: {}".format(new_sol))
        return new_sol

    def add_new_asfeature(self, solution):
        """
        Randomly selects an as variable, which is not already in solution.
        Inputs: solution list containing all features generated from harmony consideration
        """
        new_asvar = [var for var in self.asvarnames if var not in solution['asvars']]
        logger.debug('new_asvar: {}'.format(new_asvar))
        if new_asvar:
            n_asvar = list(self.random_state.choice(new_asvar, 1))
            solution['asvars'].extend(n_asvar)
            solution['asvars'] = self.remove_redundant_asvars(solution['asvars'],
                                                       self.trans_asvars,
                                                       self.asvarnames)
            solution['asvars'] = sorted(list(set(solution['asvars'])))
            logger.debug("new sol: {}".format(str(solution['asvars'])))

            # randvar logic for selected asvar
            r_vars = {}
            if self.avail_rvars:
                for i in solution['asvars']:
                    if i in solution['randvars'].keys():
                        r_vars.update({k: v for k, v in solution['randvars'].items()
                                       if k == i})
                        logger.debug("r_vars: {}".format(r_vars))
                    else:
                        if i in self.ps_randvars.keys():
                            r_vars.update({i: self.ps_randvars[i]})
                            logger.debug("r_vars: {}".format(r_vars))
                        # else:
                        #     if len(self.dist) > 0:
                        #         r_vars.update({i: self.random_state.choice(self.dist)})
                        #     logger.debug("r_vars: {}".format(r_vars))
                solution['randvars'] = {k: v for k, v in r_vars.items() if k
                                        in solution['asvars'] and v != 'f'}

        if solution['corvars']:
            solution['corvars'] = [var for var in solution['corvars']
                                   if var in solution['randvars'].keys()
                                   and var not in solution['bcvars']]
        if self.ps_intercept is None:
            solution['asc_ind'] = bool(self.random_state.randint(2))
        logger.debug('solution: {}'.format(solution))

        return solution

    def add_new_isfeature(self, solution):
        """
        Randomly selects an is variable, which is not already in solution
        Inputs: solution list containing all features generated from harmony consideration
        """
        if solution['isvars']:
            new_isvar = [var for var in self.isvarnames if var
                         not in solution['isvars']]
            if new_isvar:
                n_isvar = list(self.random_state.choice(new_isvar, 1))
                solution['isvars'] = sorted(list(set(solution['isvars']).union(n_isvar)))
        return solution

    def add_new_bcfeature(self, solution, PAR_itr):
        """
        Randomly selects a variable to be transformed, which is not already in solution
        Inputs: solution list containing all features generated from harmony consideration
        """
        if self.ps_bctrans is None:
            bctrans = bool(self.random_state.randint(2, size=1))
        else:
            bctrans = self.ps_bctrans

        if bctrans and self.avail_bcvars:
            select_new_bcvars_index = self.random_state.choice([0, 1],
                                                       size=len(solution['asvars']),
                                                       p=[1-PAR_itr, PAR_itr])
            new_bcvar = [i for (i, v) in zip(solution['asvars'],
                                             select_new_bcvars_index) if v]
            solution['bcvars'] = sorted(list(set(solution['bcvars']).union(new_bcvar)))
            solution['bcvars'] = [var for var in solution['bcvars'] if var
                                  not in self.ps_corvars]
            class_params = []
            if solution['class_params_spec'] is not None:
                class_params = list(np.concatenate(solution['class_params_spec']))

                solution['bcvars'] = [var for var in solution['bcvars']
                                      if var in class_params]
        else:
            solution['bcvars'] = []

        if not solution['corvars']:
            solution['corvars'] = []
        if self.avail_bcvars:
            # Remove corvars that are now included in bcvars
            solution['corvars'] = [var for var in solution['corvars'] if var not in solution['bcvars']]
        return solution

    def add_new_randfeature(self, solution):
        """
        Randomly selects randvar which is not already in solution
            Inputs: solution list containing all features generated from harmony consideration
        """
        if self.ps_randvars is not None:
            rand_vars = self.ps_randvars
        else:
            rand_vars = solution['randvars']
        if rand_vars:
            randvar_options = [var for var in self.asvars if var not in solution['randvars'].keys()]
            new_randvar = self.random_state.choice(randvar_options)
            rand_dist = self.random_state.choice(self.dist)
            if new_randvar:
                solution['randvars'][new_randvar] = rand_dist
                solution['randvars'] = dict(sorted(solution['randvars'].items()))
        return solution

    def add_new_corfeature(self, solution):
        """
        Randomly selects variables to be correlated, which is not already in solution
        Inputs: solution list containing all features generated from harmony consideration
        """
        if self.ps_cor is None:
            cor = bool(self.random_state.randint(2, size=1))
        else:
            cor = self.ps_cor
        if cor:
            new_corvar = [var for var in solution['randvars'].keys() if var
                          not in solution['bcvars']]
            solution['corvars'] = sorted(list(set(solution['corvars']).union(new_corvar)))
        else:
            solution['corvars'] = []
        if len(solution['corvars']) < 2:
            solution['corvars'] = []
        solution['bcvars'] = [var for var in solution['bcvars'] if var not in solution['corvars']]
        return solution

    def add_new_class_paramfeature(self, solution):
        """
        Randomly selects variables to be added to class_params_spec, which is not already in solution
        Inputs: solution list containing all features generated from harmony consideration
        """
        class_params_spec = solution['class_params_spec']
        class_params_spec_new = copy.deepcopy(class_params_spec)
        all_vars = self.asvarnames
        ii = self.random_state.randint(0, len(class_params_spec))
        class_i = class_params_spec[ii]

        new_params = [var for var in all_vars if var not in class_i]
        new_param = []
        if len(new_params) > 0:
            new_param = np.array([])
            class_params_spec = class_i

            if len(new_params) > 0:
                new_param = self.random_state.choice(new_params, 1)

                new_class_spec = np.sort(np.append(class_i, new_param))

            class_params_spec_new[ii] = new_class_spec
        else:
            class_params_spec_new[ii] = class_i

        solution['class_params_spec'] = class_params_spec_new
        if new_param not in solution['asvars']:
            solution['asvars'] = sorted(list(set(solution['asvars']).union(new_param)))

        return solution

    def add_new_member_paramfeature(self, solution):
        """
        Randomly selects variables to be added to member_params_spec, which is not already in solution
        Inputs: solution list containing all features generated from harmony consideration
        """
        member_params_spec = solution['member_params_spec']
        member_params_spec_new = copy.deepcopy(member_params_spec)
        all_vars = self.isvarnames + ['_inter']

        curr_member_params = member_params_spec[0]  # now all should be same
        new_params = np.array([var for var in all_vars if var not in curr_member_params])
        new_param = []
        if len(new_params) > 0:
            new_param = self.random_state.choice(new_params, 1)
        for ii, member_params in enumerate(member_params_spec):
            new_member_spec = np.sort(np.append(member_params, new_param))

            member_params_spec_new[ii] = new_member_spec

        solution['member_params_spec'] = member_params_spec_new
        if new_param not in solution['isvars']:
            solution['isvars'] = sorted(list(set(solution['isvars']).union(new_param)))

        return solution

    def remove_asfeature(self, solution):
        """
        Randomly excludes an as variable from solution generated from harmony consideration
        Inputs: solution list containing all features
        """
        if solution['asvars']:
            rem_asvar = list(self.random_state.choice(solution['asvars'], 1))
            solution['asvars'] = [var for var in solution['asvars'] if var not in rem_asvar]
            solution['asvars'] = sorted(list(set(solution['asvars']).union(self.ps_asvars)))
            solution['randvars'] = {k: v for k, v in solution['randvars'].items() if k
                                    in solution['asvars']}
            solution['bcvars'] = [var for var in solution['bcvars'] if var in solution['asvars']
                                  and var not in self.ps_corvars]
            solution['corvars'] = [var for var in solution['corvars'] if var in solution['asvars']
                                   and var not in self.ps_bcvars]
        return solution

    def remove_isfeature(self, solution):
        """
        Randomly excludes an is variable from solution generated from harmony consideration
        Inputs: solution list containing all features
        """
        if solution['isvars']:
            rem_isvar = list(self.random_state.choice(solution['isvars'], 1))
            solution['isvars'] = [var for var in solution['isvars'] if var not in rem_isvar]
            solution['isvars'] = sorted(list(set(solution['isvars']).union(self.ps_isvars)))
        return solution

    def remove_bcfeature(self, solution):
        """
        Randomly excludes a variable transformation from solution generated from harmony consideration
        Inputs: solution list containing all features
        """
        if solution['bcvars']:
            rem_bcvar = list(self.random_state.choice(solution['bcvars'], 1))
            rem_nps_bcvar = [var for var in rem_bcvar if var
                             not in self.ps_bcvars]
            solution['bcvars'] = [var for var in solution['bcvars'] if var in solution['asvars']
                                  and var not in rem_nps_bcvar]
            solution['corvars'] = [var for var in solution['corvars'] if var not in solution['bcvars']]
            solution['bcvars'] = [var for var in solution['bcvars'] if var not in solution['corvars']]
        return solution

    def remove_randfeature(self, solution):
        """
        Randomly excludes a random variable from solution generated from
        harmony consideration.
        """
        if solution['randvars']:
            rem_randvar = list(self.random_state.choice(list(solution['randvars'].keys()), 1))
            rem_nps_randvar = [var for var in rem_randvar if var
                               not in self.ps_randvars]
            solution['randvars'] = {k: v for k, v in solution['randvars'].items() if k
                                    in solution['asvars'] and k not in rem_nps_randvar}
            solution['corvars'] = [var for var in solution['corvars'] if var not in rem_nps_randvar]

        return solution

    def remove_corfeature(self, solution):
        """
        Randomly excludes correlaion feature from solution generated from harmony consideration
        Inputs: solution list containing all features
        """
        if solution['corvars']:
            rem_corvar = list(self.random_state.choice(solution['corvars'], 1))
            rem_nps_corvar = [var for var in rem_corvar if var
                              not in self.ps_corvars]
            solution['corvars'] = [var for var in solution['corvars'] if var
                                   in solution['randvars'].keys()
                                   and var not in rem_nps_corvar]
            if len(solution['corvars']) < 2:
                solution['corvars'] = []
        return solution

    def remove_class_paramfeature(self, solution):
        """
        Randomly excludes class_param_spec feature from solution generated from harmony consideration.
        Inputs: solution list containing all features
        """
        class_params_spec = copy.deepcopy(solution['class_params_spec'])
        rem_asvar = []
        if solution['class_params_spec'] is not None:
            # Select class to remove var from
            ii = self.random_state.randint(0, len(class_params_spec))
            class_i = class_params_spec[ii]
            if len(class_i) > 1:
                rem_asvar = self.random_state.choice(class_i)
                tmp_class_i = [var for var in class_i if var not in rem_asvar]
                class_params_spec[ii] = np.array(tmp_class_i)

        solution['class_params_spec'] = class_params_spec
        if rem_asvar not in np.concatenate(class_params_spec):
            solution['asvars'] = [var for var in solution['asvars']
                                  if var != rem_asvar]
            solution['randvars'] = {k: v for k, v in solution['randvars'].items()
                                    if k != rem_asvar}
            solution['bcvars'] = [var for var in solution['bcvars']
                                  if var != rem_asvar]
            solution['corvars'] = [var for var in solution['corvars']
                                   if var != rem_asvar]
        return solution

    def remove_member_paramfeature(self, solution):
        """
        Randomly excludes class_param_spec feature from solution generated from harmony consideration.
        Inputs: solution list containing all features
        """
        member_params_spec = copy.deepcopy(solution['member_params_spec'])
        rem_member_param = []
        if solution['member_params_spec'] is not None:
            curr_member_params = member_params_spec[0]
            if len(curr_member_params) > 1:
                rem_member_param = self.random_state.choice(curr_member_params)
                for ii, member_params in enumerate(member_params_spec):
                    tmp_member_ii = [var for var in member_params if var not in rem_member_param]
                    member_params_spec[ii] = np.array(tmp_member_ii)
        solution['member_params_spec'] = member_params_spec
        if rem_member_param not in np.concatenate(member_params_spec):
            solution['isvars'] = [var for var in solution['isvars']
                                  if var != rem_member_param]

        return solution

    def change_random_distribution(self, solution):
        if solution['randvars']:
            randvar_options = [randvar for randvar in solution['randvars']
                               if randvar not in self.ps_randvars]
            selected_randvar = self.random_state.choice(randvar_options)
            dist_tmp = self.dist.copy()
            # remove current dist for selected_randvar from options
            dist_tmp.remove(solution['randvars'][selected_randvar])
            new_dist = self.random_state.choice(dist_tmp)
            solution['randvars'][selected_randvar] = new_dist
            if selected_randvar in solution['corvars'] and new_dist != 'n':
                # corvars need to be normally distributed
                solution['corvars'] = [var for var in solution['corvars']
                                       if var != selected_randvar]
        return solution


    def assess_sol(self, solution, har_mem):
        """
        (1) Evaluates the objective function of a given solution
        (2) Evaluates if the solution provides an improvement in BIC by atleast a threshold value compared to any other solution in memory
        (3) Checks if the solution is unique to other solutions in memory
        (4) Replaces the worst solution in memory, if (2) and (3) are true
        Inputs: solution list containing all features, harmony memory
        """
        # data = self.df.copy()

        # Stop bug where _inter in class params but intercept is false
        # asc_ind = solution['asc_ind']

        improved_sol, conv = self.evaluate_objective_function(solution)

        if conv:
            improved_sol_copy = copy.deepcopy(improved_sol)
            har_mem.append(improved_sol_copy)

        seen = set()
        seen_add = seen.add
        val_key = 'multi_val' if self.multi_objective else 'loglik'

        new_hm = [x for x in har_mem if tuple([x['bic'], x[val_key]]) not in seen and
                  not seen_add(tuple([x['bic'], x[val_key]]))]

        new_har_mem = new_hm
        # sort harmony memory
        if self.multi_objective:
            # fronts = self.get_fronts(new_hm)
            new_har_mem = self.non_dominant_sorting(new_hm)
        else:
            new_har_mem = sorted(new_hm, key=lambda x: x['bic'])

        logger.debug("new_har_mem: {}".format(str(new_har_mem)))
        return (new_har_mem, improved_sol)

    def pitch_adjustment(self, sol, har_mem, PAR_itr, itr, HMS):
        """
        (1) A random binary indicator is generated. If the number is 1,
            then a new feature is added to the solution
            generated in the Harmony Memory consideration step.
            Else a feature is randomly excluded from the solution
        (2) The objective function of a given solution is evaluated.
        (3) The worst solution in harmony memory is repalced with the solution,
            if it is unique and provides an improved BIC

        Inputs:
        solution list generated from harmony consideration step
        harmony memory
        Pitch adjustment rate for the given iteration
        """
        # improved_harmony = har_mem
        # if self.random_state.rand() <= PAR_itr:
        pa_sol = copy.deepcopy(sol)
        if self.random_state.rand() <= PAR_itr:
            if self.random_state.rand() <= 0.5:
                logger.debug("pitch adjustment adding as variables")
                pa_sol = self.add_new_asfeature(sol)
            else:
                if self.asvarnames or sol['asvars']:
                    logger.debug("pitch adjustment by removing as variables")
                    pa_sol = self.remove_asfeature(sol)

        if self.random_state.rand() <= PAR_itr:
            if self.isvarnames:
                if self.random_state.rand() <= 0.5:
                    logger.debug("pitch adjustment adding is variables")
                    pa_sol = self.add_new_isfeature(pa_sol)
                else:
                    if sol['isvars']:
                        logger.debug("pitch adjustment by removing is variables")
                        pa_sol = self.remove_isfeature(pa_sol)

        if self.random_state.rand() <= PAR_itr:
            if self.asvarnames:
                if self.random_state.rand() <= 0.5:
                    logger.debug("pitch adjustment adding random variable")
                    pa_sol = self.add_new_randfeature(pa_sol)
                else:
                    if sol['randvars']:
                        logger.debug("pitch adjustment by removing random variables")
                        pa_sol = self.remove_randfeature(pa_sol)

        if self.random_state.rand() <= PAR_itr:
            pa_sol = self.change_random_distribution(pa_sol)

        if self.random_state.rand() <= PAR_itr:
            if self.ps_bctrans is None or self.ps_bctrans:
                if self.random_state.rand() <= 0.5:
                    logger.debug("pitch adjustment adding bc variables")
                    pa_sol = self.add_new_bcfeature(pa_sol, PAR_itr)
                else:
                    logger.debug("pitch adjustment by removing bc variables")
                    pa_sol = self.remove_bcfeature(pa_sol)

        if self.random_state.rand() <= PAR_itr:
            if self.ps_cor is None or self.ps_cor:
                if self.random_state.rand() <= 0.5:
                    logger.debug("pitch adjustment adding cor variables")
                    pa_sol = self.add_new_corfeature(pa_sol)
                else:
                    logger.debug("pitch adjustment by removing cor variables")
                    pa_sol = self.remove_corfeature(pa_sol)

        if self.random_state.rand() <= PAR_itr:
            if pa_sol['class_params_spec'] is not None:
                if self.random_state.rand() <= 0.5:
                    logger.debug("pitch adjustment adding class param variables")
                    pa_sol = self.add_new_class_paramfeature(pa_sol)
                else:
                    logger.debug("pitch adjustment by removing class param variables")
                    pa_sol = self.remove_class_paramfeature(pa_sol)

        if self.random_state.rand() <= PAR_itr:
            if pa_sol['member_params_spec'] is not None:
                if self.random_state.rand() <= 0.5:
                    logger.debug("pitch adjustment adding member param variables")
                    pa_sol = self.add_new_member_paramfeature(pa_sol)
                else:
                    logger.debug("pitch adjustment by removing member param variables")
                    pa_sol = self.remove_member_paramfeature(pa_sol)

        improved_harmony, pa_sol = self.assess_sol(pa_sol, har_mem)
        return (improved_harmony, pa_sol)

    def best_features(self, har_mem):
        """
        Generates lists of best features in harmony memory
        Inputs:
        Harmony memory
        """
        HM = self.find_bestsol(har_mem)
        best_asvars = HM['asvars'].copy()
        best_isvars = HM['isvars'].copy()
        best_randvars = HM['randvars'].copy()
        best_bcvars = HM['bcvars'].copy()
        best_corvars = HM['corvars'].copy()
        asc_ind = HM['asc_ind']
        best_class_params_spec = None
        best_member_params_spec = None
        if HM['class_params_spec'] is not None:
            best_class_params_spec = HM['class_params_spec'].copy()
        if HM['member_params_spec'] is not None:
            best_member_params_spec = HM['member_params_spec'].copy()

        return (best_asvars, best_isvars, best_randvars, best_bcvars,
                best_corvars, asc_ind, best_class_params_spec,
                best_member_params_spec)

    def local_search(self, improved_harmony, itr, PAR_itr):
        """
        Initiate Artificial Bee-colony optimization
        Check if finetuning the best solution in harmony improves solution's BIC
        Inputs: improved memory after harmony consideration and pitch adjustment
        """
        # For plots (BIC vs. iterations)

        # Select best solution features
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec \
                = self.best_features(improved_harmony)

        logger.debug(("first set of best features input for local search - "
                     "as_vars: {}, is_vars: {}, rand_vars: {}, bc_vars: {}, "
                     "corvars: {}, best_class_params_spec: {}, "
                     "best_member_params_spec: {}").format(best_asvars,
                                                           best_isvars,
                                                           best_randvars,
                                                           best_bcvars,
                                                           best_corvars,
                                                           best_class_params_spec,
                                                           best_member_params_spec))
        # for each additional feature to the best solution, the objective function is tested

        # Check if changing coefficient distributions of best solution improves the solution BIC
        solution_1 = Solution(asvars=best_asvars, isvars=best_isvars,
                              randvars=best_randvars, bcvars=best_bcvars,
                              corvars=best_corvars, asc_ind=asc_ind,
                              class_params_spec=best_class_params_spec,
                              member_params_spec=best_member_params_spec)

        solution_1 = self.change_random_distribution(solution_1)

        best_randvars = {key: val for key, val in best_randvars.items()
                         if key in best_asvars and val != 'f'}
        best_bcvars = [var for var in best_bcvars if var in best_asvars
                       and var not in self.ps_corvars]
        best_corvars = [var for var in best_randvars.keys() if var
                        not in best_bcvars]
        solution_1 = Solution(asvars=best_asvars, isvars=best_isvars,
                              randvars=best_randvars, bcvars=best_bcvars,
                              corvars=best_corvars, asc_ind=asc_ind,
                              class_params_spec=best_class_params_spec,
                              member_params_spec=best_member_params_spec)
        logger.debug('solution_1: {}'.format(solution_1))
        improved_harmony, current_sol = self.assess_sol(solution_1,
                                                        improved_harmony)
        logger.debug('sol after local search step 1: {}'.format(str(improved_harmony[0])))

        # check if having a full covariance matrix has an improvement in BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        best_bcvars = [var for var in best_asvars if var in self.ps_bcvars]
        if self.ps_cor is None or self.ps_cor:
            best_corvars = [var for var in best_randvars.keys() if var
                            not in best_bcvars]
        elif len(best_corvars) < 2:
            best_corvars = []
        else:
            best_corvars = []
        solution_2 = Solution(asvars=best_asvars, isvars=best_isvars,
                              randvars=best_randvars, bcvars=best_bcvars,
                              corvars=best_corvars, asc_ind=asc_ind,
                              class_params_spec=best_class_params_spec,
                              member_params_spec=best_member_params_spec)
        improved_harmony, current_sol = self.assess_sol(solution_2,
                                                        improved_harmony)
        logger.debug("sol after local search step 2: {}".format(str(improved_harmony[0])))

        # check if having a all the variables transformed has an improvement in BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        if self.ps_bctrans is None or self.ps_bctrans:
            best_bcvars = [var for var in best_asvars if var
                           not in self.ps_corvars]
        else:
            best_bcvars = []
        best_corvars = [var for var in best_randvars.keys() if var
                        not in best_bcvars]
        solution_3 = Solution(asvars=best_asvars, isvars=best_isvars,
                              randvars=best_randvars, bcvars=best_bcvars,
                              corvars=best_corvars, asc_ind=asc_ind,
                              class_params_spec=best_class_params_spec,
                              member_params_spec=best_member_params_spec)
        improved_harmony, current_sol = self.assess_sol(solution_3,
                                                        improved_harmony)
        logger.debug("sol after local search step 3: {}".format(str(improved_harmony[0])))

        if len(best_asvars) < len(self.asvarnames):
            logger.debug("local search by adding variables")
            solution = Solution(asvars=best_asvars, isvars=best_isvars,
                                randvars=best_randvars, bcvars=best_bcvars,
                                corvars=best_corvars, asc_ind=asc_ind,
                                class_params_spec=best_class_params_spec,
                                member_params_spec=best_member_params_spec)
            solution_4 = self.add_new_asfeature(solution)
            improved_harmony, current_sol = self.assess_sol(solution_4,
                                                            improved_harmony)
            logger.debug("sol after local search step 4: {}".format(str(improved_harmony[0])))

        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        solution = Solution(asvars=best_asvars, isvars=best_isvars,
                            randvars=best_randvars, bcvars=best_bcvars,
                            corvars=best_corvars, asc_ind=asc_ind,
                            class_params_spec=best_class_params_spec,
                            member_params_spec=best_member_params_spec)
        solution_5 = self.add_new_isfeature(solution)
        improved_harmony, current_sol = self.assess_sol(solution_5,
                                                        improved_harmony)
        logger.debug("sol after local search step 5: {}".format(str(improved_harmony[0])))

        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        solution = Solution(asvars=best_asvars, isvars=best_isvars,
                            randvars=best_randvars, bcvars=best_bcvars,
                            corvars=best_corvars, asc_ind=asc_ind,
                            class_params_spec=best_class_params_spec,
                            member_params_spec=best_member_params_spec)
        if self.avail_bcvars:
            if self.random_state.rand() < 0.5:
                solution_6 = self.remove_bcfeature(solution)
            else:
                solution_6 = self.add_new_bcfeature(solution, PAR_itr)
            improved_harmony, current_sol = self.assess_sol(solution_6,
                                                            improved_harmony)
            logger.debug("sol after local search step 6: {}".format(str(improved_harmony[0])))

        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        solution = Solution(asvars=best_asvars, isvars=best_isvars,
                            randvars=best_randvars, bcvars=best_bcvars,
                            corvars=best_corvars, asc_ind=asc_ind,
                            class_params_spec=best_class_params_spec,
                            member_params_spec=best_member_params_spec)

        if self.avail_rvars:
            if self.random_state.rand() < 0.5:
                solution_7 = self.remove_corfeature(solution)
            else:
                solution_7 = self.add_new_corfeature(solution)

            improved_harmony, current_sol = self.assess_sol(solution_7,
                                                            improved_harmony)

            # NOTE: noticed no add/remove of randfeatures
            if self.random_state.rand() < 0.5:
                solution_7 = self.remove_randfeature(solution_7)
            else:
                solution_7 = self.add_new_randfeature(solution)

            improved_harmony, current_sol = self.assess_sol(solution_7,
                                                            improved_harmony)


            logger.debug("sol after local search step 7: {}".format(str(improved_harmony[0])))

        # Sort unique harmony memory from min.BIC to max. BIC

        # Check if changing coefficient distributions of best solution improves the solution BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)

        for var in best_randvars.keys():
            if var not in self.ps_randvars:
                rm_dist = [dis for dis in self.dist if dis != best_randvars[var]]
                best_randvars[var] = self.random_state.choice(rm_dist)
        best_randvars = {key: val for key, val in best_randvars.items()
                         if key in best_asvars and val != 'f'}
        best_bcvars = [var for var in best_bcvars if var in best_asvars and
                       var not in self.ps_corvars]
        if self.ps_cor is None or self.ps_cor:
            best_corvars = [var for var in best_randvars.keys() if var
                            not in best_bcvars]
        if self.ps_cor is False:
            best_corvars = []
        if len(best_corvars) < 2:
            best_corvars = []
        solution = Solution(asvars=best_asvars, isvars=best_isvars,
                            randvars=best_randvars, bcvars=best_bcvars,
                            corvars=best_corvars, asc_ind=asc_ind,
                            class_params_spec=best_class_params_spec,
                            member_params_spec=best_member_params_spec)
        improved_harmony, current_sol = self.assess_sol(solution,
                                                        improved_harmony)
        logger.debug("sol after local search step 8: {}".format(str(improved_harmony[0])))

        # check if having a full covariance matrix has an improvement in BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        best_bcvars = [var for var in best_asvars if var in self.ps_bcvars]
        if self.ps_cor is None or self.ps_cor:
            best_corvars = [var for var in best_randvars.keys() if var not in best_bcvars]
        else:
            best_corvars = []
        if len(best_corvars) < 2:
            best_corvars = []
        solution = Solution(asvars=best_asvars, isvars=best_isvars,
                            randvars=best_randvars, bcvars=best_bcvars,
                            corvars=best_corvars, asc_ind=asc_ind,
                            class_params_spec=best_class_params_spec,
                            member_params_spec=best_member_params_spec)
        improved_harmony, current_sol = self.assess_sol(solution, improved_harmony)
        logger.debug("sol after local search step 9: {}".format(str(improved_harmony[0])))

        # check if having all the variables transformed has an improvement in BIC
        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        if self.ps_bctrans is None or self.ps_bctrans:
            best_bcvars = [var for var in best_asvars if var not in self.ps_corvars]  # TODO: DEBUG HERE
        else:
            best_bcvars = []
        if self.ps_cor is None or self.ps_cor:
            best_corvars = [var for var in best_randvars.keys()
                            if var not in best_bcvars]
        else:
            best_corvars = []

        if len(best_corvars) < 2:
            best_corvars = []
        solution = Solution(asvars=best_asvars, isvars=best_isvars,
                            randvars=best_randvars, bcvars=best_bcvars,
                            corvars=best_corvars, asc_ind=asc_ind,
                            class_params_spec=best_class_params_spec,
                            member_params_spec=best_member_params_spec)
        improved_harmony, current_sol = self.assess_sol(solution,
                                                        improved_harmony)
        logger.debug("sol after local search step 10: {}".format(str(improved_harmony[0])))

        if current_sol['class_params_spec'] is not None:
            if self.random_state.rand() < 0.5:
                solution = self.add_new_class_paramfeature(current_sol)
            else:
                solution = self.remove_class_paramfeature(current_sol)

        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        solution = Solution(asvars=best_asvars, isvars=best_isvars,
                            randvars=best_randvars, bcvars=best_bcvars,
                            corvars=best_corvars, asc_ind=asc_ind,
                            class_params_spec=best_class_params_spec,
                            member_params_spec=best_member_params_spec)
        improved_harmony, current_sol = self.assess_sol(solution,
                                                        improved_harmony)

        if current_sol['member_params_spec'] is not None:
            if self.random_state.rand() < 0.5:
                solution = self.add_new_member_paramfeature(current_sol)
            else:
                solution = self.remove_member_paramfeature(current_sol)

        best_asvars, best_isvars, best_randvars, best_bcvars, best_corvars, \
            asc_ind, best_class_params_spec, best_member_params_spec = self.best_features(improved_harmony)
        solution = Solution(asvars=best_asvars, isvars=best_isvars,
                            randvars=best_randvars, bcvars=best_bcvars,
                            corvars=best_corvars, asc_ind=asc_ind,
                            class_params_spec=best_class_params_spec,
                            member_params_spec=best_member_params_spec)
        improved_harmony, current_sol = self.assess_sol(solution,
                                                        improved_harmony)

        # Sort unique harmony memory from min.BIC to max. BIC
        final_harmony_sorted = improved_harmony
        return (final_harmony_sorted, current_sol)

    # Function to conduct harmony memory consideraion, pitch adjustment and local search
    def improvise_harmony(self, HCR_max, HCR_min, PR_max, PR_min, har_mem,
                          max_itr, threshold, itr_prop, HM):
        itr = 0

        # for BIC vs. iteration plots
        best_bic_points = []
        current_bic_points = []
        best_val_points = []

        while itr < max_itr:
            itr += 1
            logger.info("Improvising harmony at iteration {}".format(itr))
            # Estimate dynamic HMCR and PCR values for each iteration
            HMCR_itr = (HCR_min + ((HCR_max-HCR_min)/max_itr)*itr) * max(0, np.sign(math.sin(itr)))
            PAR_itr = (PR_min + ((PR_max-PR_min)/max_itr)*itr) * max(0, np.sign(math.sin(itr)))

            # Conduct Harmony Memory Consideration
            hmc_sol = self.harmony_consideration(har_mem, HMCR_itr, itr, HM)
            logger.debug("solution after HMC at iteration {}, is: {}".format(itr, str(hmc_sol)))
            # Conduct Pitch Adjustment
            pa_hm, current_sol = self.pitch_adjustment(hmc_sol, har_mem,
                                                       PAR_itr, itr,
                                                       self.HMS)
            logger.debug("best solution after HMC & PA at iteration: {}, is - {}" .format(itr, str(pa_hm[0])))
            current_bic_points.append(current_sol['bic'])
            # Sort unique harmony memory from min.BIC to max. BIC
            har_mem = pa_hm

            # check iteration to initiate local search
            if itr > int(itr_prop * max_itr):
                logger.debug("HM before starting local search: {}".format(str(har_mem)))
                har_mem = [sol for _, sol in enumerate(har_mem) if np.abs(sol['bic']) < 1000000]
                har_mem, current_sol = self.local_search(har_mem, itr, PAR_itr)
                # Sort unique harmony memory from min.BIC to max. BIC

                logger.debug("final harmony in current iteration {}, is - {} ".format(itr, str(har_mem)))

                best_bic_points.append(har_mem[0]['bic'])
                current_bic_points.append(current_sol['bic'])
                logger.debug(har_mem[0]['bic'])

                logger.debug(har_mem[0]['bic'])

            if itr == max_itr:  # Plot on final iteration
                val_key = 'multi_val' if self.multi_objective else 'loglik'
                valid_har_mem = [har_mem_ii for _, har_mem_ii in enumerate(har_mem)
                                 if np.abs(har_mem_ii['bic']) < 1e+7
                                 and np.abs(har_mem_ii[val_key]) < 1e+7]

                har_mem_iteration_order = sorted(valid_har_mem,
                                                 key=lambda sol: sol['sol_num'])

                all_bic_points = [har_mem_sol['bic'] for _, har_mem_sol in enumerate(har_mem_iteration_order)]
                all_val_points = [har_mem_sol[val_key] for _, har_mem_sol in enumerate(har_mem_iteration_order)]

                best_bic_points = []
                best_val_points = []
                min_bic = 1e+30
                min_val = 1e+30
                max_val = -1e+30

                for ii, bic in enumerate(all_bic_points):
                    if bic < min_bic:
                        min_bic = bic
                    best_bic_points.append(min_bic)

                for ii, val in enumerate(all_val_points):
                    if self.multi_objective:
                        if val < min_val:
                            min_val = val
                        best_val_points.append(min_val)
                    else:
                        if val > max_val:
                            max_val = val
                        best_val_points.append(max_val)

                all_bic = all_bic_points
                all_val = all_val_points

                logger.debug('best_bic_points: {}'.format(best_bic_points))
                logger.debug('best_val_points: {}'.format(best_val_points))

                if self.generate_plots:
                    if self.multi_objective:  # Plot for MOOF
                        Fronts = self.get_fronts(har_mem)
                        Pareto = self.pareto(Fronts, har_mem)
                        fig, ax = plt.subplots()

                        pareto_bic = np.array([pareto['bic'] for _, pareto in enumerate(Pareto)])
                        pareto_val = np.array([pareto['multi_val'] for _, pareto in enumerate(Pareto)])
                        if self.multi_objective_variable == 'MAE':
                            pareto_val = np.log(pareto_val)
                            all_val = np.log(all_val)

                        lns1 = ax.scatter(all_bic, all_val, label="All solutions", marker='o')

                        init_sols = [init_sol for _, init_sol in enumerate(HM) if np.abs(init_sol['bic']) < 1000000]
                        init_bic = [init_sol['bic'] for _, init_sol in enumerate(init_sols)]
                        init_val = [init_sol['multi_val'] for _, init_sol in enumerate(init_sols)]
                        lns2 = ax.scatter(init_bic, init_val, label="Initial solutions",  marker='x')

                        if self.multi_objective_variable == 'MAE':
                            init_val = np.log(init_val)

                        Pareto = [pareto for _, pareto in enumerate(Pareto) if np.abs(pareto['bic']) < 1000000]
                        logger.info('Final Pareto: {}'.format(str(Pareto)))

                        pareto_idx = np.argsort(pareto_bic)
                        # lns3 = ax.scatter(pareto_bic, pareto_val, label="Pareto Front", marker='o')
                        lns4 = ax.plot(pareto_bic[pareto_idx], pareto_val[pareto_idx], color="r", label="Pareto Front")
                        lns = (lns1, lns2, lns4[0])
                        labs = [l_pot.get_label() for l_pot in lns]
                        log_str = 'log' if self.multi_objective_variable == 'MAE' else ''
                        ax.set_xlabel("BIC - training dataset")
                        ax.set_ylabel(f"{log_str} {self.multi_objective_variable} - testing dataset")
                        lgd = ax.legend(lns, labs, loc='upper right', bbox_to_anchor=(0.5, -0.1))
                        current_time = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
                        latent_info = "_" + str(self.num_classes) + "_classes_" if (self.num_classes > 1) else "_"
                        plot_filename = self.code_name + "_" + latent_info + current_time + "_MOOF.png"
                        plt.savefig(plot_filename,
                                    bbox_extra_artists=(lgd,), bbox_inches='tight')
                    else:  # Plot for SOOF
                        fig, ax1 = plt.subplots()
                        ax2 = ax1.twinx()
                        ax1.xaxis.get_major_locator().set_params(integer=True)
                        lns1 = ax1.plot(np.arange(len(all_bic)), all_bic, label="BIC of solution estimated at current iteration")
                        lns2 = ax1.plot(np.arange(len(best_bic_points)), best_bic_points, label="BIC of best solution in memory at current iteration", linestyle="dotted")
                        lns3 = ax2.plot(np.arange(len(best_val_points)), best_val_points, label="In-sample LL of best solution in memory at current iteration", linestyle="dashed")
                        lns = lns1 + lns2 + lns3
                        labs = [l_pot.get_label() for l_pot in lns]
                        handles, _ = ax1.get_legend_handles_labels()
                        lgd = ax1.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.1))
                        ax1.set_xlabel("Iterations")
                        ax1.set_ylabel("BIC")
                        ax2.set_ylabel("LL")
                        current_time = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")

                        latent_info = "_" + str(self.num_classes) + "_classes_" if (self.num_classes > 1) else "_"
                        plot_filename = self.code_name + "_" + latent_info + current_time + "_SOOF.png"
                        plt.savefig(plot_filename,
                                    bbox_extra_artists=(lgd,), bbox_inches='tight')

                pass

            if itr == max_itr+1:
                break

        return (har_mem, best_bic_points, current_bic_points)

    def _prep_inputs(self, asvarnames=[], isvarnames=[]):
        """Include modellers' model prerequisites if any."""
        # pre-included alternative-sepcific variables
        # binary indicators representing alternative-specific variables
        # that are prespecified by the user
        psasvar_ind = [0] * len(asvarnames)

        # binary indicators representing individual-specific variables prespecified by the user
        psisvar_ind = [0] * len(isvarnames)

        # pre-included distributions
        # pspecdist_ind = ["f"]* 9 + ["any"] * (len(asvarnames)-9)
        # variables whose coefficient distribution have been prespecified by the modeller
        pspecdist_ind = ["any"] * len(asvarnames)

        # prespecification on transformations
        # indicators representing variables with prespecified transformation by the modeller
        ps_bcvar_ind = [0] * len(asvarnames)

        # prespecification on estimation of correlation
        # [1,1,1,1,1] indicators representing variables with prespecified correlation by the modeller
        ps_corvar_ind = [0] * len(asvarnames)

        # prespecified interactions
        return (psasvar_ind, psisvar_ind, pspecdist_ind, ps_bcvar_ind,
                ps_corvar_ind)

    def run_search(self, HMS=10, HMCR_min=0.6, HMCR_max=0.9, PAR_max=0.85,
                   PAR_min=0.3, itr_max=30, v=0.8, threshold=15,
                   generate_plots=True, existing_sols=None):
        """Run the IGHS algorithm

        Parameters
        ----------
            HMS : int, optional
                Harmony memory size. The number of models randomly
                generated when initialising the search. Defaults to 10.
            HMCR_min : float, optional
                Minimum harmony memory consideration rate. Defaults to
                0.6.
            HMCR_max : float, optional
                Maximum harmony memory consideration rate. Defaults to
                0.9.
            PAR_max : float, optional
                Maximum pitch adjustment rate. Defaults to 0.85.
            PAR_min : float, optional
                Minimum pitch adjustment. Defaults to 0.3.
            itr_max : int, optional:
                Number of iterations to mprovise the harmony.
                Defaults to 30.
            v : float, optional
                Proportion of iterations without local search.
                Defaults to 0.8.
            threshold : int, optional
                Threshold to compare new solution with worst solution in
                memory. Defaults to 15.
            val_share : float, optional
                _description_. Defaults to 0.25.

        Returns
        -------
            improved_harmony : list of solutions
        """
        n_gpus = dev.get_device_count()
        gpu_txt = "" if n_gpus > 0 else "not "
        logger.debug("{} GPU device(s) available. searchlogit will {} use GPU processing".format(n_gpus, gpu_txt))

        avail_asvars, avail_isvars, avail_rvars, avail_bcvars, avail_corvars = \
            self.avail_features()

        self.avail_asvars = avail_asvars
        self.avail_isvars = avail_isvars

        self.generate_plots = generate_plots

        self.avail_rvars = avail_rvars
        self.avail_bcvars = avail_bcvars
        self.avail_corvars = avail_corvars

        if self.latent_class:
            if not self.allow_latent_random:
                self.avail_rvars = []
            if not self.allow_latent_corvars:
                self.avail_corvars = []
            if not self.allow_latent_bcvars:
                self.avail_bcvars = []

        asvars_new = self.df_coeff_col(self.asvarnames)

        asvars_new = self.remove_redundant_asvars(asvars_new,
                                                  self.trans_asvars,
                                                  self.asvarnames)

        existing_HMS = []
        if existing_sols is not None:
            for sol in existing_sols:
                new_sol = copy.deepcopy(sol)
                new_sol = self.increase_sol_by_one_class(new_sol)
                new_sol.pop('class_num')
                new_sol, conv = self.evaluate_objective_function(new_sol)
                if conv:
                    existing_HMS.append(new_sol)
        Init_HM = self.initialize_memory(HMS)
        Init_HM = Init_HM + existing_HMS

        for sol in Init_HM:
            sol.add_is_init()

        # Remove duplicate solutions if present
        unique = set()
        unique_HM = [unique.add(x['bic']) or x for x in Init_HM if x['bic'] not in unique]

        # Sort unique harmony memory from min.BIC to max. BIC
        if self.multi_objective:
            HM_sorted = self.non_dominant_sorting(unique_HM)
        else:
            HM_sorted = sorted(unique_HM, key=lambda x: x['bic'])

        # Trim the Harmony memory's size as per the harmony memory size
        HM = HM_sorted[:HMS]
        logger.info("Initial harmony memory: {}".format(str(HM)))
        hm = HM.copy()

        self.HMS = HMS

        initial_harmony = hm.copy()
        new_HM, best_BICs, current_BICs = \
            self.improvise_harmony(HMCR_max, HMCR_min, PAR_max, PAR_min,
                                   initial_harmony, itr_max,
                                   threshold, v, HM)
        improved_harmony = new_HM.copy()

        logger.info("Improved harmony: {}".format(improved_harmony))

        if self.multi_objective:
            hm = self.non_dominant_sorting(improved_harmony)
            improved_harmony = hm.copy()
            best_sol = improved_harmony[0]
        else:  # single objective - bic, the 0-th index
            improved_harmony.sort(key=lambda x: x['bic'])
            best_sol = improved_harmony[0]
        logger.info("Search ended at: {}".format(str(time.ctime())))
        best_asvarnames = best_sol['asvars']
        best_isvarnames = best_sol['isvars']
        best_randvars = best_sol['randvars']
        best_bcvars = best_sol['bcvars']
        best_corvars = best_sol['corvars']
        best_intercept = best_sol['asc_ind']
        best_class_params_spec = best_sol['class_params_spec']
        best_member_params_spec = best_sol['member_params_spec']

        if self.latent_class:
            class_vars = list(np.concatenate(best_class_params_spec))
            member_vars = list(np.concatenate(best_member_params_spec))
            all_vars = class_vars + member_vars + best_isvarnames
            best_varnames = np.unique(all_vars)
        else:
            best_varnames = best_asvarnames + best_isvarnames

        # delete '_inter' bug fix
        if '_inter' in best_varnames:
            best_varnames = np.delete(best_varnames, np.argwhere(best_varnames == '_inter'))
        logger.info("Estimating best solution with entire dataset.")
        df_all = self.df
        if self.multi_objective:
            df_all = self.df.append(self.df_test)

        X = df_all[best_varnames]
        y = self.choice_var.append(self.test_choice_var)
        seed = self.random_state.randint(2**31 - 1)

        avail_all = self.avail
        avail_latent_all = self.avail_latent
        weights_all = self.weights
        alt_var_all = self.alt_var
        choice_id_all = self.choice_id
        ind_id_all = self.ind_id

        if self.multi_objective:
            if self.avail is not None:
                avail_all = np.row_stack((self.avail, self.test_av))
            if self.avail_latent is not None:
                avail_latent_all = [None] * self.num_classes
                for ii, avail_latent_ii in enumerate(self.avail_latent):
                    if avail_latent_ii is not None:
                        avail_latent_all[ii] = np.row_stack((avail_latent_ii, self.test_avail_latent[ii]))
            if self.weights is not None:
                weights_all = np.concatenate((self.weights, self.test_weight_var))
            if self.alt_var is not None:
                alt_var_all = np.concatenate((self.alt_var, self.test_alt_var))
            if self.choice_id is not None:
                choice_id_all = np.concatenate((self.choice_id, self.test_choice_id))
            if self.ind_id is not None:
                ind_id_all = np.concatenate((self.ind_id, self.test_ind_id))
        try:
            if bool(best_randvars):
                if self.latent_class:
                    model = LatentClassMixedModel()
                    model.fit(X,
                              y,
                              varnames=best_varnames,
                              isvars=best_isvarnames,
                              class_params_spec=best_class_params_spec,
                              member_params_spec=best_member_params_spec,
                              num_classes=self.num_classes,
                              alts=alt_var_all,
                              ids=choice_id_all,
                              panels=ind_id_all,
                              transformation="boxcox",
                              transvars=best_bcvars,
                              randvars=best_randvars,
                              correlation=best_corvars,
                              maxiter=self.maxiter,
                              gtol=self.gtol,
                              avail=avail_all,
                              weights=weights_all)
                else:
                    model = MixedLogit()
                    model.fit(X=X,
                              y=y,
                              varnames=best_varnames,
                              isvars=best_isvarnames,
                              alts=alt_var_all,
                              ids=choice_id_all,
                              panels=ind_id_all,
                              randvars=best_randvars,
                              transformation="boxcox",
                              transvars=best_bcvars,
                              fit_intercept=best_intercept,
                              correlation=best_corvars,
                              n_draws=self.n_draws)
            else:
                if self.latent_class:
                    model = LatentClassModel()
                    model.fit(X, y, varnames=best_varnames,
                              # isvars=best_isvarnames,
                              class_params_spec=best_class_params_spec,
                              member_params_spec=best_member_params_spec,
                              num_classes=self.num_classes, alts=alt_var_all,
                              ids=choice_id_all,
                              transformation="boxcox",
                              transvars=best_bcvars,
                              #   randvars=best_randvars,
                              #   correlation=best_corvars,
                              maxiter=self.maxiter, gtol=self.gtol,
                              gtol_membership_func=self.gtol_membership_func,
                              avail=avail_all,
                              avail_latent=avail_latent_all,
                              intercept_opts=self.intercept_opts,
                              weights=weights_all, random_state=seed)
                else:
                    model = MultinomialLogit()
                    model.fit(X, y,
                              varnames=best_varnames, isvars=best_isvarnames,
                              alts=alt_var_all, ids=choice_id_all,
                              transformation="boxcox", transvars=best_bcvars,
                              fit_intercept=best_intercept)
            old_stdout = sys.stdout
            log_file = open(self.logger_name, "a")
            sys.stdout = log_file
            logger.info("Best model")
            model.summary()
            sys.stdout = old_stdout
            log_file.close()
        except Exception as e:
            logger.warning("Error in fitting best model: {}".format(e))
            pass

        if not self.multi_objective:
            logger.info("best_BICs: {}".format(best_BICs))
            logger.info("current_BICs: {}".format(current_BICs))

        return improved_harmony

    def run_search_latent(self, HMS=10, min_classes=1, max_classes=10,
                          HMCR_min=0.6, HMCR_max=0.9, PAR_max=0.85,
                          PAR_min=0.3, itr_max=30, v=0.8, threshold=15,
                          termination_override=False):
        prev_bic = 1e+30
        best_model_idx = 0
        all_harmony = []
        search_harmony = []
        for q in range(min_classes, max_classes+1):
            if q == 1:
                self.latent_class = False
                self.num_classes = q
            else:
                self.latent_class = True
                self.num_classes = q
            logger.info("Starting search with {} classes".format(q))
            search_harmony = self.run_search(HMS=HMS, HMCR_min=HMCR_min,
                                             HMCR_max=HMCR_max, PAR_max=PAR_max,
                                             PAR_min=PAR_min, itr_max=itr_max, v=v,
                                             threshold=threshold, generate_plots=False,
                                             existing_sols=search_harmony)
            for sol_i in search_harmony:
                sol_i['class_num'] = q
            all_harmony = all_harmony + search_harmony

            if self.multi_objective:
                all_harmony = self.non_dominant_sorting(all_harmony)
                Fronts = self.get_fronts(all_harmony)
                Pareto = self.pareto(Fronts, all_harmony)
                stop_run = True
                pareto_class_nums = [sol['class_num'] for sol in Pareto]
                if max(pareto_class_nums) == q:  # i.e. a solution with q classes is in the Pareto front
                    stop_run = False
                if stop_run and not termination_override:
                    logger.info(f"Stopping search at {q} classes")
                    break
                else:
                    logger.info(f"Solutions in Pareto front for {q} classes")
                    for ii, sol in enumerate(Pareto):
                        logger.info(f'Pareto solution with {q} classes - {ii}')
                        for k, v in sol.items():
                            logger.info(f"{k}: {v}")
                    logger.info(f'Best solution with {q} classes')
                    for k, v in all_harmony[0].items():
                        logger.info(f"{k}: {v}")
                best_model_idx += 1
            else:
                search_harmony = sorted(search_harmony, key=lambda sol: sol['bic'])
                solution = search_harmony[0]  # assume already sorted
                if solution['bic'] < prev_bic or termination_override:
                    best_model_idx += 1
                    prev_bic = solution['bic']
                    best_search_sols = search_harmony[:HMS]
                    for ii, sol in enumerate(best_search_sols):
                        logger.info(f"Best solution with {q} classes - {ii}")
                        for k, v in sol.items():
                            logger.info(f"{k}: {v}")
                else:
                    logger.info(f"Best solution with {q} classes had a worse BIC than {q-1} classes")
                    logger.info(f"Stopping search at {q} classes")
                    break

        # Remove default solutions
        all_harmony_valid = [sol for _, sol in enumerate(all_harmony)
                             if sol['bic']< 1e+7]
        all_harmony = sorted(all_harmony_valid,
                             key=lambda sol: sol['sol_num'])

        # Plot all solutions together
        num_classes_considered = q - min_classes + 1
        all_bic_classes = []
        all_val_classes = []
        for i in range(num_classes_considered):
            num_classes = i + min_classes
            val_key = 'multi_val' if self.multi_objective else 'loglik'
            all_bic = [sol['bic'] for sol in all_harmony if sol['class_num'] == num_classes]
            all_val = [sol[val_key] for sol in all_harmony if sol['class_num'] == num_classes]
            if self.multi_objective_variable == 'MAE':
                all_val = np.log(all_val)
            all_bic_classes.append(all_bic)
            all_val_classes.append(all_val)

        best_bic_points = []
        best_val_points = []
        min_bic = 1e+30
        min_val = 1e+30
        max_val = -1e+30

        for _, all_bic in enumerate(all_bic_classes):
            for ii, bic in enumerate(all_bic):
                if bic < min_bic:
                    min_bic = bic
                best_bic_points.append(min_bic)

        for _, all_val in enumerate(all_val_classes):
            for ii, val in enumerate(all_val):
                if val == 1000000:
                    val = -1e+30
                if self.multi_objective:
                    if val < min_val:
                        min_val = val
                    best_val_points.append(min_val)
                else:
                    if val > max_val:
                        max_val = val
                    best_val_points.append(max_val)

        if self.multi_objective:
            Fronts = self.get_fronts(all_harmony)
            Pareto = self.pareto(Fronts, all_harmony)
            fig, ax = plt.subplots()
            lns_all = []
            for i in range(num_classes_considered):
                class_label = "All solutions - " + str(i+min_classes) + " classes"
                if i + min_classes == 1:
                    class_label = "All solutions - " + str(i+min_classes) + " class"
                lns = ax.scatter(all_bic_classes[i], all_val_classes[i], label=class_label, marker='o')
                lns_all.append(lns)
            init_sols = [init_sol for _, init_sol in enumerate(all_harmony) if np.abs(init_sol['bic']) < 1000000 and init_sol['is_initial_sol']]
            init_bic = [init_sol['bic'] for _, init_sol in enumerate(init_sols)]
            init_val = [init_sol['multi_val'] for _, init_sol in enumerate(init_sols)]
            if self.multi_objective_variable == 'MAE':
                init_val = np.log(init_val)

            lns2 = ax.scatter(init_bic, init_val, label="Initial solutions",  marker='x', color='black')

            Pareto = [pareto for _, pareto in enumerate(Pareto) if np.abs(pareto['bic']) < 1000000]
            logger.info('Final Pareto: {}'.format(str(Pareto)))

            pareto_bic = np.array([pareto['bic'] for _, pareto in enumerate(Pareto)])
            pareto_val = np.array([pareto['multi_val'] for _, pareto in enumerate(Pareto)])
            log_str = ''
            if self.multi_objective_variable == 'MAE':
                pareto_val = np.log(pareto_val)
                log_str = 'log'
            pareto_idx = np.argsort(pareto_bic)
            lns4 = ax.plot(pareto_bic[pareto_idx], pareto_val[pareto_idx], color="r", label="Pareto Front")
            lns = (*lns_all, lns2, lns4[0])
            labs = [l_pot.get_label() for l_pot in lns]
            ax.set_xlabel("BIC - training dataset")
            ax.set_ylabel(f"{log_str} {self.multi_objective_variable} - testing dataset")
            lgd = ax.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.1))
            current_time = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
            plot_filename = self.code_name + "_" + current_time + "_MOOF.png"
            plt.savefig(plot_filename,
                        bbox_extra_artists=(lgd,), bbox_inches='tight')
        else:  # Plot for SOOF
            fig, ax1 = plt.subplots()
            ax2 = ax1.twinx()
            ax1.xaxis.get_major_locator().set_params(integer=True)

            counter = 0
            max_bic = np.max(all_bic)
            for i in range(num_classes_considered):
                num_sols_in_class = len(all_bic_classes[i])
                num_class = i + min_classes
                ax1.axvline(x=counter, color='r', linestyle='--')
                line_text = str(num_class) + ' classes'
                if num_class == 1:
                    line_text = '1 class'
                ax1.text(counter, max_bic, line_text)
                counter += num_sols_in_class
            all_bic = np.concatenate(np.array(all_bic_classes))
            lns1 = ax1.plot(np.arange(len(all_bic)), all_bic, label="BIC of solution estimated at current iteration")
            lns2 = ax1.plot(np.arange(len(best_bic_points)), best_bic_points, label="BIC of best solution in memory at current iteration", linestyle="dotted")
            lns3 = ax2.plot(np.arange(len(best_val_points)), best_val_points, label="In-sample LL of best solution in memory at current iteration", linestyle="dashed")

            lns = lns1 + lns2 + lns3

            labs = [l_pot.get_label() for l_pot in lns]
            handles, _ = ax1.get_legend_handles_labels()
            lgd = ax1.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.1))
            ax1.set_xlabel("Iterations")
            ax1.set_ylabel("BIC")
            ax2.set_ylabel("LL")
            current_time = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")

            plot_filename = self.code_name + "_" + current_time + "_SOOF.png"
            plt.savefig(plot_filename,
                        bbox_extra_artists=(lgd,), bbox_inches='tight')

        best_sols = None
        if self.multi_objective:
            all_harmony = self.non_dominant_sorting(all_harmony)
            best_sols = Pareto.copy()
        else:
            all_harmony = sorted(all_harmony, key=lambda sol: sol['bic'])
            best_sols = all_harmony[:HMS]

        if self.multi_objective:
            logger.info("Models in Pareto front had at most {} classes".format(q-1))
            logger.info("Best models in Pareto front")
            for ii, sol in enumerate(Pareto):
                logger.info(f'Best solution - {ii}')
                for k, v in sol.items():
                    logger.info(f"{k}: {v}")
            logger.info(f"Best solution with {all_harmony[0]['class_num']} classes")
            for k, v in all_harmony[0].items():
                logger.info(f"{k}: {v}")

        else:
            best_sol = best_sols[0]
            logger.info("Model with best BIC had {} classes".format(q-1))
            logger.info("Best solution")
            for k, v in best_sol.items():
                logger.info(f"{k}: {v}")

        return all_harmony, best_sols

    def check_dominance(self, obj1, obj2):
        """
        Function checks dominance between solutions for two objective functions
        Inputs: obj1 - List containing values of the two objective functions for solution 1
                obj2 - List containing values of the two objective functions for solution 2
        Output: Returns True if solution 1 dominates 2, False otherwise
        """
        indicator = False
        for a, b in zip(obj1, obj2):
            if a < b:
                indicator = True
            # if one of the objectives is dominated, then return False
            elif a > b:
                return False
        return indicator

    # Final Pareto-front identifier
    def get_fronts(self, HM):
        """
        Funtion for non-dominant sorting of the given set of solutions
        ni - the number of solutions which dominate the solution i
        si - a set of solutions which the solution i dominates

        Inputs: List containing set of solutions

        Output: Dict with keys indicating the Pareto rank and values containing indices of solutions in Input
        """
        si = {}
        ni = {}
        val_key = 'multi_val' if self.multi_objective else 'loglik'
        for i in range(len(HM)):
            sp_i = []
            np_i = 0
            for j in range(len(HM)):
                if i != j:
                    dominance = self.check_dominance([HM[i]['bic'], HM[i][val_key]],
                                                     [HM[j]['bic'], HM[j][val_key]])
                    if dominance:
                        sp_i.append(j)
                    else:
                        dominance = self.check_dominance([HM[j]['bic'], HM[j][val_key]],
                                                         [HM[i]['bic'], HM[i][val_key]])
                        if dominance:
                            np_i += 1
            si.update({i: sp_i})
            ni.update({i: np_i})
        # Identify solutions in each front
        Fronts = {}
        itr = 0
        for k in range(max(ni.keys())+1):
            Fi_idx = [key for key, val in ni.items() if val == k]
            if len(Fi_idx) > 0:
                Fronts.update({'F_{}'.format(itr): Fi_idx})
                itr += 1
        logger.debug("Fronts: {}".format(str(Fronts)))
        return Fronts

    def crowding_dist(self, Fronts, HM):
        """
        Function to estimate crowding distance between 2 solutions
        Inputs:
        Fronts-Dict with keys indicating Pareto rank and values indicating indices of solutions belonging to the rank
        HM - List of solutions
        """
        v_dis = {}
        val_key = 'multi_val' if self.multi_objective else 'loglik'

        for v in Fronts.values():
            v.sort(key=lambda x: HM[x]['bic'])
            for i in v:
                v_dis.update({i: 0})
        # Calculate crowding distance based on first objective
        for v in Fronts.values():
            for j in v:
                if v[0] == j or v[-1] == j:
                    v_dis.update({j: 1000000})
                else:
                    dis = abs(v_dis.get(j) +
                              ((HM[v[v.index(j) + 1]]['bic'] -
                                HM[j]['bic']) / (max(HM[x]['bic'] for x in
                                                 range(len(HM))) -
                                             min(HM[x]['bic'] for x in
                                                 range(len(HM))))))
                    v_dis.update({j: dis})

        # Calculate crowding distance based on second objective
        q_dis = {}
        for v in Fronts.values():
            v.sort(key=lambda x: HM[x][val_key])
            for k in v:
                q_dis.update({k: 0})
        for v in Fronts.values():
            for k in v:
                if v[0] == k or v[-1] == k:
                    q_dis.update({k: 1000000})
                else:
                    dis = abs(q_dis.get(k) + ((HM[v[v.index(k)+1]][val_key] -
                                               HM[k][val_key])
                                               / (max(HM[x][val_key] for x
                                                     in range(len(HM))) -
                                                 min(HM[x][val_key] for x in
                                                     range(len(HM))))))
                    q_dis.update({k: dis})
        # Adding crowding distance from both objectives
        crowd = {k: q_dis[k] + v_dis[k] for k in v_dis.keys()}
        return crowd

    def pareto(self, Fronts, HM):
        Pareto_front_id = []
        for k, v in Fronts.items():
            if len(v) > 0:
                Pareto_front_id = Fronts.get(k)
                break
        Pareto_front = [HM[x] for x in Pareto_front_id]
        return Pareto_front

    def sort_InitHM(self, Fronts, v_dis, HM):
        """
        Function to sort memory from best solution to worst solution
        Inputs:
        Fronts-Dict with keys indicating Pareto rank and values indicating indices of solutions belonging to the rank
        v_dis - Dict with keys indicating index of solution in memory and value indicating crowding distance
        Output:
        Sorted_HM - Sorted list of solutions
        """
        Sorted_HM_id = []
        for k, v in Fronts.items():
            pareto_sols = {key: val for key, val in v_dis.items() if key
                           in Fronts.get(k)}
            Sorted_HM_id.extend([ke for ke, va in
                                sorted(pareto_sols.items(),
                                       key=lambda item: item[1],
                                       reverse=True)])

            # Sorted_HM_id.extend([ke for ke, va in sorted(pareto_sols.items(), key=lambda item: item[1])])
            if len(Sorted_HM_id) >= self.HMS:
                break
        Sorted_HM = [HM[x] for x in Sorted_HM_id]
        return Sorted_HM

    def sort_HM(self, Fronts, v_dis, HM):
        """
        Function to sort memory from best solution to worst solution
        Inputs:
        Fronts-Dict with keys indicating Pareto rank and values indicating indices of solutions belonging to the rank
        v_dis - Dict with keys indicating index of solution in memory and value indicating crowding distance
        Output:
        Sorted_HM - Sorted list of solutions
        """
        Sorted_HM_id = []
        for k, v in Fronts.items():
            pareto_sols = {key: val for key, val in v_dis.items()
                           if key in Fronts.get(k)}
            Sorted_HM_id.extend([ke for ke, va in
                                 sorted(pareto_sols.items(),
                                        key=lambda item: item[1])])

        Sorted_HM = [HM[x] for x in Sorted_HM_id]
        return Sorted_HM

    def non_dominant_sorting(self, HM):
        Front = self.get_fronts(HM)
        crowd = self.crowding_dist(Front, HM)
        Final_HM = self.sort_HM(Front, crowd, HM)
        return Final_HM

    def find_bestsol(self, HM):
        max_obj1 = max(HM[x]['bic'] for x in range(len(HM)))
        min_obj1 = min(HM[x]['bic'] for x in range(len(HM)))
        weights_obj1 = [(HM[x]['bic']-min_obj1)/(max_obj1-min_obj1) for x in range(len(HM))]

        if self.multi_objective:
            max_obj2 = max(HM[x]['multi_val'] for x in range(len(HM)))
            min_obj2 = min(HM[x]['multi_val'] for x in range(len(HM)))
            weights_obj2 = [(HM[x]['multi_val']-min_obj2)/(max_obj2-min_obj2) for x in range(len(HM))]

            weights = [weights_obj1[x] + weights_obj2[x] for x in range(len(HM))]
        else:
            weights = weights_obj1
        best_solid = weights.index(min(weights))
        logger.debug("best sol for local search: {}".format(HM[best_solid]))
        return HM[best_solid]
