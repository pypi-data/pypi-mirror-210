import pathlib
from typing import List, Union, Optional

import numpy as np
import pandas as pd

from icare import utils, check_errors, design_matrix


class CovariateModel:
    """A general-purpose covariate model."""
    age_start: Union[int, List[int]]
    age_interval_length: Union[int, List[int]]
    beta_estimates: np.ndarray
    profile: pd.DataFrame
    z_profile: pd.DataFrame  # z_profile is the design matrix generated from profile
    population_distribution: pd.DataFrame
    population_weights: np.ndarray

    def __init__(self,
                 formula_path: Union[str, pathlib.Path, None],
                 log_relative_risk_path: Union[str, pathlib.Path, None],
                 reference_dataset_path: Union[str, pathlib.Path, None],
                 profile_path: Union[str, pathlib.Path, None],
                 reference_dataset_weights_variable_name: Optional[str],
                 age_start: Union[int, List[int]],
                 age_interval_length: Union[int, List[int]]) -> None:
        parameters = [formula_path, log_relative_risk_path, reference_dataset_path, profile_path]
        any_parameter_missing = any([x is None for x in parameters])

        if any_parameter_missing:
            raise ValueError("ERROR: Either all or none of the covariate parameters— 'model_covariate_formula_path', "
                             "'model_log_relative_risk_path', 'model_reference_dataset_path', and "
                             "'apply_covariate_profile_path'— should be specified. If none of them are specified, "
                             "it implies the special option for a SNP-only model.")

        formula = utils.read_file_to_string(formula_path)
        log_relative_risk = utils.read_file_to_dict(log_relative_risk_path)
        reference_dataset = utils.read_file_to_dataframe(reference_dataset_path, allow_integers=False)

        self._set_population_distribution(formula, reference_dataset)
        self._set_population_weights(reference_dataset_weights_variable_name, reference_dataset)
        self._set_beta_estimates(log_relative_risk)

        profile = utils.read_file_to_dataframe_given_dtype(profile_path, dtype=reference_dataset.dtypes.to_dict())
        self._set_profile(profile)
        self._set_z_profile(formula, profile, reference_dataset)
        self.age_start, self.age_interval_length = utils.set_age_intervals(
            age_start, age_interval_length, len(self.z_profile), 'apply_covariate_profile_path')

    def _set_population_distribution(self, formula: str, reference_dataset: pd.DataFrame) -> None:
        check_errors.check_covariate_reference_dataset(reference_dataset)
        self.population_distribution = design_matrix.build_design_matrix(formula, reference_dataset)

    def _set_population_weights(self, reference_dataset_weights_name: Optional[str],
                                reference_dataset: pd.DataFrame) -> None:
        if reference_dataset_weights_name is None:
            self.population_weights = np.ones(len(self.population_distribution)) / len(self.population_distribution)
        else:
            check_errors.check_covariate_reference_dataset_weights_name(reference_dataset_weights_name,
                                                                        reference_dataset)
            reference_dataset_weights = reference_dataset.pop(reference_dataset_weights_name).values
            check_errors.check_population_weights(reference_dataset_weights, self.population_distribution)
            self.population_weights = reference_dataset_weights / np.sum(reference_dataset_weights)

    def _set_beta_estimates(self, log_relative_risk: dict) -> None:
        check_errors.check_covariate_log_relative_risk(log_relative_risk, self.population_distribution)
        self.beta_estimates = np.array([log_relative_risk[covariate] for covariate in self.population_distribution])

    def _set_profile(self, profile: pd.DataFrame) -> None:
        self.profile = profile

    def _set_z_profile(self, formula: str, profile: pd.DataFrame, reference_dataset: pd.DataFrame) -> None:
        check_errors.check_covariate_profile(reference_dataset, profile)
        self.z_profile = design_matrix.build_design_matrix_with_missing_values(formula, profile, reference_dataset)
        check_errors.check_covariate_profile_against_reference_population(self.z_profile, self.population_distribution)
