from typing import Any
import pandas as pd
import pandera as pa
from pydantic import BaseModel
from pydantic import Field


class CRSProjectionModel(BaseModel):
    source_crs: str = "EPSG:4326"
    target_crs: str = "EPSG:2326"


class DataFramePivotFields(BaseModel):

    source_lat: str = "lat"
    source_lon: str = "lon"
    source_datetime: str = "datetime"
    source_vehicle_id: str = "plate_no"

    projected_date: str = "date"
    projected_lat: str = "y"
    projected_lon: str = "x"
    computed_velocity: str = "computed_velocity"
    computed_unixtime: str = "unixtime"

    clustering_output: str = "cluster_id"
    fragmentation_output: str = "is_clustering_candidate"
    classification_output: str = "type_of_activity"

    sjoin_valid_flag: str = "sjoin_valid_flag"
    sjoin_spatial_dist: str = "sjoin_spatial_dist"
    sjoin_temporal_dist: str = "sjoin_temporal_dist"
    sjoin_overall_dist: str = "sjoin_overall_dist"

    gps_pk: str = "gps_primary_key"
    clusters_pk: str = "cluster_primary_key"
    plans_pk: str = "plans_primary_key"

    @property
    def pandera_schema(self):
        """
        Returns pandera schema
        """
        schema = {
            self.source_lat: pa.Column(float, coerce=True, nullable=False, required=True),
            self.source_lon: pa.Column(float, coerce=True, nullable=False, required=True),
            self.source_datetime: pa.Column(pd.Timestamp, coerce=True, nullable=False, required=True),
            self.source_vehicle_id: pa.Column(str, coerce=True, nullable=False, required=True),
            self.projected_date: pa.Column(pd.Timestamp, coerce=True, nullable=False, required=False),
            self.projected_lat: pa.Column(float, coerce=True, nullable=False, required=False),
            self.projected_lon: pa.Column(float, coerce=True, nullable=False, required=False),
            self.clustering_output: pa.Column(int, coerce=True, nullable=False, required=False),
            self.computed_unixtime: pa.Column(float, coerce=True, nullable=False, required=False),
            self.fragmentation_output: pa.Column(bool, coerce=True, nullable=False, required=False),
            self.classification_output: pa.Column(str, coerce=True, nullable=False, required=False),
            self.sjoin_valid_flag: pa.Column(bool, coerce=True, nullable=False, required=False),
            self.sjoin_spatial_dist: pa.Column(float, coerce=True, nullable=False, required=False),
            self.sjoin_temporal_dist: pa.Column(int, coerce=True, nullable=False, required=False),
            self.sjoin_overall_dist: pa.Column(float, coerce=True, nullable=False, required=False),
            self.gps_pk: pa.Column(str, coerce=True, nullable=False, required=False),
            self.clusters_pk: pa.Column(str, coerce=True, nullable=False, required=False),
            self.plans_pk: pa.Column(str, coerce=True, nullable=False, required=False),
        }
        schema = pa.DataFrameSchema(schema)
        return schema


class DefaultValues(BaseModel):
    noise_gps_cluster_id: int = -1
    sjoin_gps_suffix: str = "gps"
    sjoin_plan_suffix: str = "plan"
    sjoin_cluster_suffix: str = "cluster"
    pk_delimiter: str = "_"
    sjoin_cov_stat_agg_column: str = Field(
        default="amt_records",
        description="Column name of output aggregation of coverage stats module",
    )
    sjoin_cov_stat_action_default: str = Field(
        default="Keep as is",
        description=(
            "Default action message of coverage statistics module,"
            " when vehicle-date pairs are listed in all data sources"
        ),
    )
    sjoin_cov_stat_action_required: str = Field(
        default="Remove vehicle-date pair from: ",
        description=(
            "Action message to coverage statistics module," " when vehicle-date pairs are't listed in all data sources"
        ),
    )
    sjoin_cov_stat_action_field: str = Field(
        default="action_required",
        description="Field name describing the action required to-do",
    )


class LinkerDataContainer(BaseModel):
    # NOTE: keys are needed to fabricate
    # instance with mandatory components
    gps: Any = Field(
        default=None,
        description="GPS records container used for manipulation",
    )
    plan: Any = Field(
        default=None,
        description="Plan records container is used for manipulation",
    )
    coverage_stats: Any = Field(
        default=None,
        description="Plan & GPS records vehicle-date overlap report",
    )
    clusters: Any = Field(
        default=None,
        description="Aggregated clusters of GPS records",
    )
    clusters_plan_join: Any = Field(
        default=None,
        description="Link table of primary keys between GPS & Plan",
    )
    full_gps_plan_join: Any = Field(
        default=None,
        description="Full table join of GPS & visit plan",
    )

    def validated_coverage_stats(self):
        """
        Coverage stats validation is needed to ensure that all incoming clusters and plans
        are overallping over the days. it prevents bias of recall & precisions.
        """
        if self.coverage_stats.isna().any().any():
            msg = "You provided vehicle-date which is not listed in both source."
            msg += " Please, look at coverage stats, follow specified "
            msg += "action and recalculate linkage!"
            raise ValueError(msg)

    def __preprocess_clusters(self, pivots: DataFramePivotFields):
        _columns = [
            pivots.source_vehicle_id,
            pivots.projected_date,
            pivots.clustering_output,
            pivots.source_lon,
            pivots.source_lat,
            pivots.clusters_pk,
        ]
        return self.clusters.loc[:, _columns]

    def __preprocess_plan(self, pivots: DataFramePivotFields):
        _columns = [
            pivots.source_vehicle_id,
            pivots.projected_date,
            pivots.source_lon,
            pivots.source_lat,
            pivots.plans_pk,
        ]
        plan = self.plan[_columns]
        plan = plan.rename(
            columns={
                pivots.source_lat: f"{pivots.source_lat}_plan",
                pivots.source_lon: f"{pivots.source_lon}_plan",
            },
        )
        return plan

    def join_gps_plan(self) -> pd.DataFrame:
        """
        Function left joins (route plan details, clusters) to gps records

        Returns:
        pd.DataFrame: concatenated gps
        """
        _pivots = DataFramePivotFields()
        _defaults = DefaultValues()
        clusters = self.__preprocess_clusters(_pivots)
        plan = self.__preprocess_plan(_pivots)
        self.full_gps_plan_join = (
            self.gps.merge(
                clusters,
                how="left",
                on=[
                    _pivots.source_vehicle_id,
                    _pivots.projected_date,
                    _pivots.clustering_output,
                ],
                suffixes=[
                    f"_{_defaults.sjoin_gps_suffix}",
                    f"_{_defaults.sjoin_cluster_suffix}",
                ],
            )
            .merge(self.clusters_plan_join, how="left", on=[_pivots.clusters_pk])
            .merge(
                plan,
                how="left",
                on=[_pivots.plans_pk],
                suffixes=["", f"_{_defaults.sjoin_plan_suffix}"],
            )
        )
