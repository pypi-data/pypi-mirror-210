# **GPS activity** 🚛

![Python versions](https://img.shields.io/pypi/pyversions/gps_activity)
![Latest release](https://img.shields.io/github/v/release/WasteLabs/gps_activity)
![Latest release date](https://img.shields.io/github/release-date/WasteLabs/gps_activity)
![License](https://img.shields.io/github/license/WasteLabs/gps_activity)
[![CI test](https://github.com/WasteLabs/gps_activity/actions/workflows/ci-tests.yaml/badge.svg)](https://github.com/WasteLabs/gps_activity/actions/workflows/ci-tests.yaml)
[![codecov](https://codecov.io/gh/WasteLabs/gps_activity/branch/main/graph/badge.svg?token=58AY7B1YBB)](https://codecov.io/gh/WasteLabs/gps_activity)

A light-weight module for analysis of GPS activity. Package is designed to be trade-off solution for both researchers and developers in Waste Labs. Using `gps_activity` you can:

1. Cluster your time-series gps records to extract activity points
2. Join activity points with original plan or operation report
3. Estimate clustering performance

## Installation ☁️ -> 🖥️

Using pip:

```bash
pip3 install gps_activity
```

## **Python package modules** 📦

---

- **extraction**: clusters GPS records and extracts cluster activities ([checkout module structure]((https://github.com/WasteLabs/gps_activity/tree/main/docs/extraction/README.md)))
- **linker**: joins route plan and clustered gps records
- **metrics**: estimates clustering performance based on:
    1. internal source: ones that based on inter & intra cluster distances
    2. external source: joined route plan and clustered gps records (output of **linker** module)

![components](docs/diagrams/gps_activity_components.png)

## **Extraction modules** 🔵 🟣 ⚫️

---

Organized by preprocessing, fragmentation & clustering steps that ultimately are packed into `ActivityExtractionSession` object and orchestrated.

### ⚠️ `ActivityExtractionSession` assumptions and constrains

1. 1 vehicle = 1 session run: to avoid clusters overlap
1. No duplicated gps records over vehicle-timstamp: avoids division by zero during computing `velocity`

### 🚀 **VHFDBSCAN**: Velocity hardlimit fragmentation Density-based spatial clustering of applications with noise

- Fragmentation is performing by applying hardlimiting on velocity computed from `lat`, `lon` and `datetime` columns
- Clustering is performed by classical DBSCAN that considers non-cluster candidates as noise

```python
from gps_activity import ActivityExtractionSession
from gps_activity.extraction.factory.preprocessing import PreprocessingFactory
from gps_activity.extraction.factory.fragmentation import VelocityFragmentationFactory
from gps_activity.extraction.factory.clustering import FDBSCANFactory


preprocessing = PreprocessingFactory.factory_pipeline(
    source_lat_column="lat",
    source_lon_column="lon",
    source_datetime="datetime",
    source_vehicle_id="plate_no",
    source_crs="EPSG:4326",
    target_crs="EPSG:2326",
)

fragmentation = VelocityFragmentationFactory.factory_pipeline(max_velocity_hard_limit=4)
clustering = FDBSCANFactory.factory_pipeline(eps=30, min_samples=3)

activity_extraction = ActivityExtractionSession(
    preprocessing=preprocessing,
    fragmentation=fragmentation,
    clustering=clustering,
)

activity_extraction.predict(gps)
```

### 🚀 **VHFSTCM**: Velocity hardlimit fragmentation spatio-temporal clustering model

- Fragmentation is performing by applying hardlimiting on velocity computed from `lat`, `lon` and `datetime` columns
- Clustering is performed according steps:
    1. Generated adjacent proximity mask (if cluster pair distance <= `eps`)
    2. Clusters ID are generated according: proximity mask and fragmentation flag
    3. GPS records grouped by `cluster_id` and aggregated cluster time span
    4. Cluster is validated if time span >= `min_duration_sec`
    5. Validated cluster ids are set to original GPS records

```python
from gps_activity import ActivityExtractionSession
from gps_activity.extraction.factory.preprocessing import PreprocessingFactory
from gps_activity.extraction.factory.fragmentation import VelocityFragmentationFactory
from gps_activity.extraction.factory.clustering import STCMFactory


preprocessing = PreprocessingFactory.factory_pipeline(
    source_lat_column="lat",
    source_lon_column="lon",
    source_datetime="datetime",
    source_vehicle_id="plate_no",
    source_crs="EPSG:4326",
    target_crs="EPSG:2326",
)

fragmentation = VelocityFragmentationFactory.factory_pipeline(max_velocity_hard_limit=4)
clustering = STCMFactory.factory_pipeline(
    source_vehicle_id_column="plate_no",
    eps=30,
    min_duration_sec=60
)

stcm = ActivityExtractionSession(
    preprocessing=preprocessing,
    fragmentation=fragmentation,
    clustering=clustering,
)
```

## Linker module implementation 🔵 🟣 ⚫️

**[Overview linker module components](https://github.com/WasteLabs/gps_activity/tree/main/docs/linker/README.md)**

```python
# Initilize linkage components
from gps_activity import ActivityLinkageSession
from gps_activity.linker.factory import PreprocessingFactory
from gps_activity.linker.factory import ClusterAggregationFactory
from gps_activity.linker.factory import JoinValidatorFactory
from gps_activity.linker.factory import SpatialJoinerFactory
from gps_activity.linker.factory import CoverageStatisticsFactory


MAX_DISTANCE = 100
MAX_DAYS_DISTANCE = 1


gps_link_preprocess_pipeline = PreprocessingFactory.factory_pipeline(
    source_lat_column="lat",
    source_lon_column="lon",
    source_datetime="datetime",
    source_vehicle_id="plate_no",
    source_crs=WSG_84,
    target_crs=HK_CRS,
    generate_primary_key_for="gps",
    source_composite_keys=["plate_no", "datetime", "lat", "lon"],
)

plans_link_preprocess_pipeline = PreprocessingFactory.factory_pipeline(
    source_lat_column="lat",
    source_lon_column="lng",
    source_datetime="datetime",
    source_vehicle_id="re-assigned by Ricky",
    source_crs=WSG_84,
    target_crs=HK_CRS,
    generate_primary_key_for="plan",
    source_composite_keys=["CRN#"],
)

cluster_agg_pipeline = ClusterAggregationFactory.factory_pipeline(
    source_lat_column="lat",
    source_lon_column="lon",
    source_datetime="datetime",
    source_vehicle_id="plate_no",
    source_crs=WSG_84,
    target_crs=HK_CRS,
)

spatial_joiner = SpatialJoinerFactory.factory_pipeline(how="inner", max_distance=MAX_DISTANCE)
spatial_validator = JoinValidatorFactory.factory_pipeline(max_days_distance=MAX_DAYS_DISTANCE,
                                                          ensure_vehicle_overlap=True)
coverage_stats_extractor = CoverageStatisticsFactory.factory_pipeline()


gps_linker_session = ActivityLinkageSession(
    gps_preprocessor=gps_link_preprocess_pipeline,
    plan_preprocessor=plans_link_preprocess_pipeline,
    cluster_aggregator=cluster_agg_pipeline,
    spatial_joiner=spatial_joiner,
    spatial_validator=spatial_validator,
    coverage_stats_extractor=coverage_stats_extractor,
)


linker_results = gps_linker_session.transform({
    "gps": clustered_gps,
    "plan": plans,
})
```

## Metrics module implementation 📊

* **NOTE**: This module is highly experimental
* **NOTE**: This module depends on `linker` module

```python
from gps_activity.metrics import ActivityMetricsSession
from gps_activity.metrics.models import Metrics


metrics = ActivityMetricsSession(beta=2)
metrics = metrics.transform(linker_results)
```
