# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Mapping, Sequence, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.constants import MLTableDataLabel
from azureml.contrib.automl.dnn.forecasting.constants import ForecastConstant, DROP_COLUMN_LIST
from azureml.contrib.automl.dnn.forecasting._distributed._sharding._sharding_strategy_selector import \
    get_best_sharding_strategy
from azureml.contrib.automl.dnn.forecasting._distributed._sharding._download_shards import download_shards
from azureml.contrib.automl.dnn.forecasting._distributed._grain_summary import (
    GrainSummary,
    get_dataset_grain_summaries
)
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.data import TabularDataset
from azureml.training.tabular.featurization.timeseries._distributed.timeseries_data_profile import \
    AggregatedTimeSeriesDataProfile


logger = logging.getLogger(__name__)


@dataclass
class NumpyDatasetLoadConfig:
    train_data: np.ndarray
    valid_data: np.ndarray
    train_offsets: np.ndarray
    valid_offsets: np.ndarray
    num_replicas: Mapping[MLTableDataLabel, int]
    replica_id: Mapping[MLTableDataLabel, int]


def get_column_names(
    data_profile: AggregatedTimeSeriesDataProfile,
    time_column_name: str,
    grain_column_names: Sequence[str],
) -> Sequence[str]:
    """
    Get the Sequence of column names in the dataset. The target column will be in the end.

    :param data_profile: The data profile for the train and val datasets.
    :param time_column_name: The name of the time column.
    :param grain_column_names: The name of the grain columns.

    :returns: Sequence of columns with the target column in the end of the sequence.
    """
    columns = data_profile.get_column_names()
    # Remove the columns that we don't train on.
    columns = list(
        filter(lambda column: column not in DROP_COLUMN_LIST and column not in grain_column_names, columns)
    )
    # Remove the time column as well.
    columns.remove(time_column_name)
    # Move the target column to the end
    columns.append(ForecastConstant.time_series_internal.DUMMY_TARGET_COLUMN)
    return columns


def log_warning_for_gaps_in_train_val_dataset(
    data_profile: AggregatedTimeSeriesDataProfile,
    freq_offset: pd.DateOffset,
) -> None:
    """
    Log a warning if there is a gap between the training and validation datasets.

    :param data_profile: The data profile for the train and val datasets.
    :param freq_offset: Azure automl settings.
    """
    has_gaps = any(
        grain_data_profile.train_end_date + freq_offset != grain_data_profile.val_start_date
        for grain_data_profile in data_profile.profile_mapping.values()
    )
    if has_gaps:
        logger.warn(
            """Some grains have gaps in the training and validation dataset.
            To fix this, make sure that the starting date of every series in the validation
            dataset is equal to ending date of the corresponding series in the training
            dataset + frequency of the timeseries."""
        )


def get_grain_summary(
    train_featurized_dataset: TabularDataset,
    valid_featurized_dataset: TabularDataset,
    data_profile: AggregatedTimeSeriesDataProfile,
) -> Tuple[Sequence[GrainSummary], Sequence[GrainSummary]]:
    """
    Get the grain summaries for training and validation datasets.

    :param train_featurized_dataset: The train featurized TabularDataset.
    :param valid_featurized_dataset: The validation featurized TabularDataset.
    :param data_profile: The data profile for the train and val datasets.

    :return: The train and validation grain summaries.
    """
    with logging_utilities.log_activity(logger=logger, activity_name='FetchingGrainsSummaries'):

        train_grain_summaries = get_dataset_grain_summaries(train_featurized_dataset,
                                                            data_profile,
                                                            MLTableDataLabel.TrainData)
        valid_grain_summaries = get_dataset_grain_summaries(valid_featurized_dataset,
                                                            data_profile,
                                                            MLTableDataLabel.ValidData)
    return train_grain_summaries, valid_grain_summaries


def load_datasets(
    train_featurized_dataset: TabularDataset,
    valid_featurized_dataset: TabularDataset,
    train_grain_summaries: Sequence[GrainSummary],
    valid_grain_summaries: Sequence[GrainSummary],
    numericalized_grain_columns: Sequence[int],
    columns: Sequence[str],
    lookback: int,
    horizon: int,
    validation_step_size: int,
) -> NumpyDatasetLoadConfig:
    """
    Shard and download the training and validation datasets.

    :param train_featurized_dataset: The training featurized TabularDataset.
    :param valid_featurized_dataset: The validation featurized TabularDataset.
    :param train_grain_summaries: The Sequence of train grain summaries.
    :param valid_grain_summaries: The Sequence of validation grain summaries.
    :param numericalized_grain_columns: Index of numericalized grain columns.
    :param columns: The Sequence of columns to be downloaded.
    :param lookback: The lookback period.
    :param horizon: The forecast horizon.
    :param validation_step_size: The step size for the validation dataset.
    """
    shardingStrategy = get_best_sharding_strategy(
        train_grain_summaries,
        valid_grain_summaries,
        DistributedHelper.node_count(),
        lookback,
        horizon,
        validation_step_size
    )

    train_dataset_download_path = f"train{DistributedHelper.node_rank()}.npy"
    valid_dataset_download_path = f"valid{DistributedHelper.node_rank()}.npy"

    with logging_utilities.log_activity(logger=logger, activity_name="DownloadingTrainingDataset"):
        train_offsets = download_shards(
            shardingStrategy,
            train_featurized_dataset,
            valid_featurized_dataset,
            numericalized_grain_columns,
            columns,
            train_dataset_download_path,
            MLTableDataLabel.TrainData,
            DistributedHelper.is_local_master_node()
        )
    with logging_utilities.log_activity(logger=logger, activity_name="DownloadingValidationDataset"):
        valid_offsets = download_shards(
            shardingStrategy,
            train_featurized_dataset,
            valid_featurized_dataset,
            numericalized_grain_columns,
            columns,
            valid_dataset_download_path,
            MLTableDataLabel.ValidData,
            DistributedHelper.is_local_master_node()
        )
    DistributedHelper.wait_for_all_processes()

    train_memmap = np.lib.format.open_memmap(train_dataset_download_path, mode="r")
    valid_memmap = np.lib.format.open_memmap(valid_dataset_download_path, mode="r")

    return NumpyDatasetLoadConfig(
        train_data=train_memmap,
        valid_data=valid_memmap,
        train_offsets=train_offsets,
        valid_offsets=valid_offsets,
        num_replicas=shardingStrategy.num_of_processes_per_shard,
        replica_id=shardingStrategy.process_rank_in_shard
    )
