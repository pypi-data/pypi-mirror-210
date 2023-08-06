# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from typing import Optional, Tuple, Union, List, Iterable
import logging
import copy
from dataclasses import dataclass

import numpy as np
import pandas as pd

from syne_tune.constants import (
    ST_TUNER_TIME,
)
from syne_tune.experiments.plotting import PlotParameters
from syne_tune.experiments.results_utils import (
    MapMetadataToSetup,
    DateTimeBounds,
    create_index_for_result_files,
    load_results_dataframe_per_benchmark,
    download_result_files_from_s3,
    SINGLE_BENCHMARK_KEY,
)
from syne_tune.try_import import try_import_visual_message
from syne_tune.util import is_increasing, is_positive_integer

try:
    import matplotlib.pyplot as plt
except ImportError:
    print(try_import_visual_message())

logger = logging.getLogger(__name__)


@dataclass
class MultiFidelityParameters:
    """
    Parameters configuring the multi-fidelity version of
    :class:`TrialsOfExperimentResults`.

    :param rung_levels: See above. Positive integers, increasing
    :param pause_resume_setups: Names of setups which are pause-and-resume
        methods (these are visualized differently). Must be contained in
        ``setups``
    """

    rung_levels: List[int]
    pause_resume_setups: Iterable[str]

    def check_params(self, setups: Iterable[str]):
        assert set(setups).issuperset(self.pause_resume_setups), (
            f"multi_fidelity_params.pause_resume_setups = {self.pause_resume_setups} "
            f"must be contained in setups = {setups}"
        )
        assert is_increasing(self.rung_levels) and is_positive_integer(
            self.rung_levels
        ), f"multi_fidelity_params.rung_levels = {self.rung_levels} must be increasing positive ints"


class TrialsOfExperimentResults:
    """
    This class loads, processes, and plots metric results for single experiments,
    where the curves for different trials have different colours.

    Compared to :class:`~syne_tune.experiments.ComparativeResults`, each subfigure
    uses data from a single experiment (one, benchmark, one seed, one setup). Both
    benchmark and seed need to be chosen in :meth:`plot`. If there are different
    setups, they give rise to subfigures (by default, one row with subfigures as
    columns, but can be configured).

    For ``plot_params``, we use the same
    :class:`~syne_tune.experiments.PlotParameters` as in
    :class:`~syne_tune.experiments.ComparativeResults`, but some fields are not
    used here (``title``, ``aggregate_mode``, ``show_one_trial``,
    ``subplots.legend_no``, ``subplots.xlims``).

    :param experiment_names: Tuple of experiment names (prefixes, without the
        timestamps)
    :param setups: Possible values of setup names
    :param metadata_to_setup: See above
    :param plot_params: Parameters controlling the plot. Can be overwritten
        in :meth:`plot`. See :class:`PlotParameters`
    :param multi_fidelity_params: If given, we use a special variant taylored
        to multi-fidelity methods (see :meth:`plot`).
    :param benchmark_key: Key for benchmark in metadata files. Defaults to
        "benchmark". If this is ``None``, there is only a single benchmark,
        and all results are merged together
    :param seed_key: Key for seed in metadata files. Defaults to "seed".
    :param with_subdirs: See above. Defaults to "*"
    :param datetime_bounds: See above
    :param download_from_s3: Should result files be downloaded from S3? This
        is supported only if ``with_subdirs``
    :param s3_bucket: Only if ``download_from_s3 == True``. If not given, the
        default bucket for the SageMaker session is used
    """

    def __init__(
        self,
        experiment_names: Tuple[str, ...],
        setups: Iterable[str],
        metadata_to_setup: MapMetadataToSetup,
        plot_params: Optional[PlotParameters] = None,
        multi_fidelity_params: Optional[MultiFidelityParameters] = None,
        benchmark_key: Optional[str] = "benchmark",
        seed_key: str = "seed",
        with_subdirs: Optional[Union[str, List[str]]] = "*",
        datetime_bounds: Optional[DateTimeBounds] = None,
        download_from_s3: bool = False,
        s3_bucket: Optional[str] = None,
    ):
        assert setups, "setups must not be empty"
        if multi_fidelity_params is not None:
            multi_fidelity_params.check_params(setups)
        assert seed_key is not None, "seed_key must not be None"
        if download_from_s3:
            assert (
                with_subdirs is not None
            ), "Cannot download files from S3 if with_subdirs=None"
            download_result_files_from_s3(experiment_names, s3_bucket)
        result = create_index_for_result_files(
            experiment_names=experiment_names,
            metadata_to_setup=metadata_to_setup,
            benchmark_key=benchmark_key,
            with_subdirs=with_subdirs,
            datetime_bounds=datetime_bounds,
            seed_key=seed_key,
        )
        self._reverse_index = result["index"]
        assert result["setup_names"] == set(setups), (
            f"Filtered results contain setup names {result['setup_names']}, "
            f"but should contain setup names {setups}"
        )
        self.setups = tuple(setups)
        self._default_plot_params = copy.deepcopy(plot_params)
        self._benchmark_key = benchmark_key
        if multi_fidelity_params is not None:
            self._pause_resume_setups = set(multi_fidelity_params.pause_resume_setups)
            # We need rung levels minus 1 below
            self._rung_levels = [
                level - 1 for level in multi_fidelity_params.rung_levels
            ]
        else:
            self._pause_resume_setups = None
            self._rung_levels = None

    def _plot_figure(
        self,
        df: pd.DataFrame,
        plot_params: PlotParameters,
        benchmark_name: Optional[str],
        seed: int,
    ):
        subplots = plot_params.subplots
        if subplots is not None:
            subplots_kwargs = subplots.kwargs
            nrows = subplots.nrows
            ncols = subplots.ncols
            assert ncols * nrows >= len(
                self.setups
            ), f"Error in subplots.kwargs: ncols times nrows must be >= {len(self.setups)} (number of setups)"
            subplots_kwargs = dict(
                dict() if subplots.kwargs is None else subplots.kwargs,
                nrows=nrows,
                ncols=ncols,
            )
            subplot_titles = subplots.titles
            title_each_figure = subplots.title_each_figure
        else:
            nrows = 1
            ncols = len(self.setups)
            subplots_kwargs = dict(nrows=nrows, ncols=ncols, sharey="all")
            subplot_titles = self.setups
            title_each_figure = False
        ylim = plot_params.ylim
        xlim = plot_params.xlim
        xlabel = plot_params.xlabel
        ylabel = plot_params.ylabel
        tick_params = plot_params.tick_params
        msg_prefix = f"seed = {seed}: "
        if benchmark_name is not None:
            msg_prefix = f"benchmark_name = {benchmark_name}, " + msg_prefix
        is_multi_fidelity = self._rung_levels is not None
        num_rungs = len(self._rung_levels) if is_multi_fidelity else 0

        plt.figure(dpi=plot_params.dpi)
        figsize = (5 * ncols, 4 * nrows)
        fig, axs = plt.subplots(**subplots_kwargs, squeeze=False, figsize=figsize)
        for setup_name, setup_df in df.groupby("setup_name"):
            # Check that there is a single experiment per setup
            tuner_names = list(setup_df.tuner_name.unique())
            assert len(tuner_names) == 1, (
                msg_prefix
                + f"For setup_name = {setup_name} found tuner_names = {tuner_names}"
            )
            logger.info(msg_prefix + f"setup_name = {setup_name}: {tuner_names[0]}")
            pause_resume = (
                setup_name in self._pause_resume_setups if is_multi_fidelity else False
            )
            subplot_no = self.setups.index(setup_name)
            row = subplot_no % nrows
            col = subplot_no // nrows
            ax = axs[row, col]
            current_color = [0] * (num_rungs + 1)
            for trial_id in setup_df.trial_id.unique():
                sub_df = setup_df[setup_df["trial_id"] == trial_id]
                y = np.array(sub_df[plot_params.metric])
                rt = np.array(sub_df[ST_TUNER_TIME])
                sz = y.size
                if is_multi_fidelity:
                    rungs_here = [x for x in self._rung_levels if x < sz]
                    col_ind = len(rungs_here)
                else:
                    rungs_here = None
                    col_ind = 0
                color = f"C{current_color[col_ind]}"
                current_color[col_ind] += 1
                if not pause_resume and sz > 1:
                    ax.plot(rt, y, "-", color=color)
                else:
                    # Pause and resume: Plot differences pieces
                    ranges = [
                        (a + 1, b + 1) for a, b in zip(rungs_here[:-1], rungs_here[1:])
                    ]
                    if len(rungs_here) < num_rungs:
                        a = rungs_here[-1] + 1
                        if a < sz - 1:
                            ranges.append((a, sz))
                    for a, b in ranges:
                        ax.plot(rt[a:b], y[a:b], "-", color=color)
                if is_multi_fidelity:
                    if rungs_here[-1] == sz - 1:
                        final_ind = [sz - 1]
                        rungs_here = rungs_here[:-1]
                        ax.plot(
                            rt[final_ind],
                            y[final_ind],
                            marker="D",
                            markeredgecolor=color,
                            color="none",
                            markersize=3,
                        )
                    ax.plot(
                        rt[rungs_here],
                        y[rungs_here],
                        marker="o",
                        markeredgecolor=color,
                        color="none",
                        markersize=3,
                    )
                else:
                    ax.plot(
                        rt[-1:],
                        y[-1:],
                        marker="o",
                        markeredgecolor=color,
                        color="none",
                        markersize=3,
                    )

            if xlim is not None:
                ax.set_xlim(*xlim)
            if ylim is not None:
                ax.set_ylim(*ylim)
            if xlabel is not None and row == nrows - 1:
                ax.set_xlabel(xlabel)
            if ylabel is not None and col == 0:
                ax.set_ylabel(ylabel)
            if tick_params is not None:
                ax.tick_params(**tick_params)
            if title_each_figure:
                ax.set_title(subplot_titles[subplot_no])
            elif row == 0:
                ax.set_title(subplot_titles[col])
            if plot_params.grid:
                ax.grid(True)
        plt.show()
        return fig, axs

    def plot(
        self,
        benchmark_name: Optional[str] = None,
        seed: int = 0,
        plot_params: Optional[PlotParameters] = None,
        file_name: Optional[str] = None,
    ):
        """
        Creates a plot, whose subfigures should metric data from single
        experiments. In general:

        * Each trial has its own color, which is cycled through periodically.
          The cycling depends on the largest rung level for the trial. This
          is to avoid neighboring curves to have the same color

        For single-fidelity methods (default, ``multi_fidelity_params`` not
        given):

        * The learning curve for a trial ends with 'o'. If it reports only
          once at the end, this is all that is shown for the trial

        For multi-fidelity methods:

        * Learning curves are plotted in contiguous chunks of execution. For
          pause and resume setups (those in
          ``multi_fidelity_params.pause_resume_setups), they are interrupted.
          Each chunk starts at the epoch after resume and ends at the epoch
          where the trial is paused
        * Values at rung levels are marked as 'o'. If this is the furthest
          the trial got to, the marker is 'D' (diamond)

        Results for different setups are plotted as subfigures, either using
        the setup in ``plot_params.subplots``, or as columns of a single row.

        :param benchmark_name: Name of benchmark for which to plot results.
            Not needed if there is only one benchmark
        :param seed: Seed number. Defaults to 0
        :param plot_params: Parameters controlling the plot. Values provided
            here overwrite values provided at construction.
        :param file_name: If given, the figure is stored in a file of this name
        """
        index_key = (
            SINGLE_BENCHMARK_KEY if self._benchmark_key is None else benchmark_name,
            seed,
        )
        assert (
            index_key in self._reverse_index
        ), f"{index_key} not found in index, contains: {list(self._reverse_index.keys())}"
        if plot_params is None:
            plot_params = PlotParameters()
        plot_params = plot_params.merge_defaults(self._default_plot_params)
        if benchmark_name is not None:
            logger.info(f"Load results for benchmark {benchmark_name}, seed {seed}")
        else:
            logger.info(f"Load results for seed {seed}")
        results_df = load_results_dataframe_per_benchmark(
            self._reverse_index[index_key]
        )
        fig, axs = self._plot_figure(
            df=results_df,
            plot_params=plot_params,
            benchmark_name=benchmark_name,
            seed=seed,
        )
        if file_name is not None:
            fig.savefig(file_name, dpi=plot_params.dpi)
