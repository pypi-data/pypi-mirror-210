import pandas as pd


from ... import abstract
from ... import models


class CoverageStatistics(abstract.AbstractNode):
    """
    Table describes how provided gps covers provided route plan and inverse
    """

    def __init__(self, pivots: models.DataFramePivotFields, defaults: models.DefaultValues):
        self.__group_params = [
            pivots.source_vehicle_id,
            pivots.projected_date,
        ]
        self.__agg_column = defaults.sjoin_cov_stat_agg_column
        self.__agg_params = {
            self.__agg_column: (pivots.source_vehicle_id, "count"),
        }

        self.__gps_suffix = f"{defaults.pk_delimiter}{defaults.sjoin_gps_suffix}"
        self.__plan_suffix = f"{defaults.pk_delimiter}{defaults.sjoin_plan_suffix}"

        self.__gps_key = f"{defaults.sjoin_gps_suffix}"
        self.__plan_key = f"{defaults.sjoin_plan_suffix}"

        self.__action_field = defaults.sjoin_cov_stat_action_field
        self.__default_message = defaults.sjoin_cov_stat_action_default
        self.__action_message = defaults.sjoin_cov_stat_action_required

    def fit(self, X: models.LinkerDataContainer, y=None):
        return self

    def __agg_data(self, X: pd.DataFrame):
        return X.groupby(self.__group_params).agg(**self.__agg_params).reset_index()

    def __add_action_recommendation(
        self,
        X: pd.DataFrame,
        source_suffix: str,
        target_suffix: str,
    ):
        drop_message = f"{self.__action_message} {target_suffix}"
        is_missing_gps = X[self.__agg_column + source_suffix].isna()
        X.loc[is_missing_gps, self.__action_field] = drop_message
        return X

    def __init_action_recommendation(
        self,
        X: pd.DataFrame,
    ):
        X[self.__action_field] = self.__default_message
        return X

    def transform(self, X: models.LinkerDataContainer):
        _gps_agg = self.__agg_data(X.gps)
        _plan_agg = self.__agg_data(X.plan)
        action_table = pd.merge(
            left=_gps_agg,
            right=_plan_agg,
            on=self.__group_params,
            how="outer",
            suffixes=[self.__gps_suffix, self.__plan_suffix],
        )
        action_table = self.__init_action_recommendation(action_table)
        action_table = self.__add_action_recommendation(
            action_table,
            source_suffix=self.__gps_suffix,
            target_suffix=self.__plan_key,
        )
        action_table = self.__add_action_recommendation(
            action_table,
            source_suffix=self.__plan_suffix,
            target_suffix=self.__gps_key,
        )
        return action_table
