from sklearn.pipeline import Pipeline

from .. import nodes as local_nodes
from ... import models
from ...abstract import AbstractPipelineFactory


class CoverageStatisticsFactory(AbstractPipelineFactory):
    @staticmethod
    def factory_pipeline() -> Pipeline:
        """
        Function creating instance of coverage statistics estimator
        instance pipeline of linker module

        Returns:
        sklear.pipeline.Pipeline: Scikit-learn pipeline
        """
        pivots = models.DataFramePivotFields()
        defaults = models.DefaultValues()
        return Pipeline(
            [
                (
                    "coverage_stats_estimator",
                    local_nodes.CoverageStatistics(pivots=pivots, defaults=defaults),
                ),
            ],
        )
