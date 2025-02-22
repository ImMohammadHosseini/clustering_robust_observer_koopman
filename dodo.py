"""Define and automate tasks with ``doit``.

Actions associated with tasks defined here can be found in ``actions.py``.
"""

import pathlib

import doit
import numpy as np

import actions

# Directory containing ``dodo.py``
WD = pathlib.Path(__file__).parent.resolve()
K = 6
FEATURES_TO_CLUSTER = [['joint_vel', 'target_joint_vel']]
CLUSTERING_NUM = len(FEATURES_TO_CLUSTER)

def task_preprocess_experiments():
    """Preprocess raw data into pickle containing a dataframe."""
    raw_dataset = WD.joinpath("dataset", "raw", "batch_b")
    preprocessed_dataset = WD.joinpath("build", "dataset.pickle")
    return {
        "actions": [
            (
                actions.action_preprocess_experiments,
                (
                    raw_dataset,
                    preprocessed_dataset,
                ),
            )
        ],
        "targets": [preprocessed_dataset],
        "uptodate": [doit.tools.check_timestamp_unchanged(str(raw_dataset))],
        "clean": True,
    }

def task_one_step_clustering():
    """Task to perform time series clustering using DTW with K-means."""
    
    preprocessed_dataset = WD.joinpath("build", "dataset.pickle")
    cluster_centers = WD.joinpath("build", "DTW_K_means_clusters.pickle")
    cluster_preds = WD.joinpath("build", "cluster_preds.pickle")
    cluster_split_info = WD.joinpath("build", "cluster_split_info.pickle")
    
    return {
        "actions": [
            (
                actions.action_one_step_DTW_K_means_clustering,
                (
                    preprocessed_dataset,
                    cluster_centers,
                    cluster_preds,
                    cluster_split_info,
                    K,
                    FEATURES_TO_CLUSTER
                ),
            )
        ],
        "file_dep": [preprocessed_dataset],
        "targets": [cluster_centers, cluster_preds, cluster_split_info],
        "clean": True,
    }

def task_compute_cluster_phase():
    cluster_centers = WD.joinpath("build", "DTW_K_means_clusters.pickle")
    cluster_phase = WD.joinpath("build", "cluster_phase.pickle")
    return {
        "actions": [
            (
                actions.action_compute_cluster_phase,
                (
                    cluster_centers,
                    cluster_phase,
                ),
            )
        ],
        "file_dep": [cluster_centers],
        "targets": [cluster_phase],
        "clean": True,
    }

def task_compute_phase():
    """Compute phase offset."""
    preprocessed_dataset = WD.joinpath("build", "dataset.pickle")
    phase = WD.joinpath("build", "phase.pickle")
    return {
        "actions": [
            (
                actions.action_compute_phase,
                (
                    preprocessed_dataset,
                    phase,
                ),
            )
        ],
        "file_dep": [preprocessed_dataset],
        "targets": [phase],
        "clean": True,
    }

def task_cluster_id_models():
    cluster_centers = WD.joinpath("build", "DTW_K_means_clusters.pickle")
    cluster_phase = WD.joinpath("build", "cluster_phase.pickle")
    cluster_models_linear = WD.joinpath("build", "cluster_models_linear.pickle")
    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_cluster_id_models,
                (cluster_centers, cluster_phase, cluster_models_linear, "linear"),
            )
        ],
        "file_dep": [cluster_centers, cluster_phase],
        "targets": [cluster_models_linear],
        "clean": True,
    }
    cluster_models_koopman = WD.joinpath("build", "cluster_models_koopman.pickle")
    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_cluster_id_models,
                (cluster_centers, cluster_phase, cluster_models_koopman, "koopman"),
            )
        ],
        "file_dep": [cluster_centers, cluster_phase],
        "targets": [cluster_models_koopman],
        "clean": True,
    }


def task_id_models():
    """Identify linear and Koopman models."""
    preprocessed_dataset = WD.joinpath("build", "dataset.pickle")
    phase = WD.joinpath("build", "phase.pickle")
    models_linear = WD.joinpath("build", "models_linear.pickle")
    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_id_models,
                (preprocessed_dataset, phase, models_linear, "linear"),
            )
        ],
        "file_dep": [preprocessed_dataset, phase],
        "targets": [models_linear],
        "clean": True,
    }
    models_koopman = WD.joinpath("build", "models_koopman.pickle")
    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_id_models,
                (preprocessed_dataset, phase, models_koopman, "koopman"),
            )
        ],
        "file_dep": [preprocessed_dataset, phase],
        "targets": [models_koopman],
        "clean": True,
    }


def task_compute_residuals_for_clusters():
    """Compute residuals from linear and Koopman models for clusters."""
    models_linear = WD.joinpath("build", "models_linear.pickle")
    cluster_models_linear = WD.joinpath("build", "cluster_models_linear.pickle")
    cluster_preds = WD.joinpath("build", "cluster_preds.pickle")
    cluster_residuals_linear = WD.joinpath("build", "cluster_residuals_linear.pickle")
    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_compute_residuals_for_clusters,
                (models_linear, cluster_models_linear, cluster_preds,
                 cluster_residuals_linear),
            )
        ],
        "file_dep": [models_linear, cluster_models_linear, cluster_preds],
        "targets": [cluster_residuals_linear],
        "clean": True,
    }
    models_koopman = WD.joinpath("build", "models_koopman.pickle")
    cluster_models_koopman = WD.joinpath("build", "cluster_models_koopman.pickle")
    cluster_residuals_koopman = WD.joinpath("build", "cluster_residuals_koopman.pickle")
    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_compute_residuals_for_clusters,
                (models_koopman, cluster_models_koopman, cluster_preds, 
                 cluster_residuals_koopman),
            )
        ],
        "file_dep": [models_koopman, cluster_models_koopman, cluster_preds],
        "targets": [cluster_residuals_koopman],
        "clean": True,
    }
    
def task_compute_residuals():
    """Compute residuals from linear and Koopman models."""
    models_linear = WD.joinpath("build", "models_linear.pickle")
    residuals_linear = WD.joinpath("build", "residuals_linear.pickle")
    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_compute_residuals,
                (models_linear, residuals_linear),
            )
        ],
        "file_dep": [models_linear],
        "targets": [residuals_linear],
        "clean": True,
    }
    models_koopman = WD.joinpath("build", "models_koopman.pickle")
    residuals_koopman = WD.joinpath("build", "residuals_koopman.pickle")
    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_compute_residuals,
                (models_koopman, residuals_koopman),
            )
        ],
        "file_dep": [models_koopman],
        "targets": [residuals_koopman],
        "clean": True,
    }

def task_generate_uncertainty_weights_for_cluster_models():
    cluster_residuals_koopman = WD.joinpath(
        "build", "cluster_residuals_koopman.pickle"
    )
    orders_koopman = np.array(
        [
            [1, 3],
            [3, 3],
        ]
    )
    cluster_uncertainty_koopman = WD.joinpath(
        "build", "cluster_uncertainty_min_residual_koopman.pickle"
    )
    cluster_uncertainty_mimo_koopman = WD.joinpath(
        "build", "cluster_uncertainty_mimo_min_residual_koopman.png"
    )
    cluster_uncertainty_msv_koopman = WD.joinpath(
        "build", "cluster_uncertainty_msv_min_residual_koopman.png"
    )
    cluster_nominal = WD.joinpath("build", "cluster_nominal_min_residual.txt")
    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_generate_uncertainty_weights_for_cluster_models_min_residual,
                (
                    cluster_residuals_koopman,
                    cluster_nominal,
                    cluster_uncertainty_koopman,
                    cluster_uncertainty_mimo_koopman,
                    cluster_uncertainty_msv_koopman,
                    orders_koopman,
                    "koopman",
                ),
            )
        ],
        "file_dep": [cluster_residuals_koopman],
        "targets": [
            cluster_uncertainty_koopman,
            cluster_nominal,
            cluster_uncertainty_mimo_koopman,
            cluster_uncertainty_msv_koopman,
        ],
        "clean": True,
    }
    
    cluster_residuals_linear = WD.joinpath("build", "cluster_residuals_linear.pickle")
    orders_linear = np.array(
        [
            [1, 2],
            [1, 2],
        ]
    )
    cluster_uncertainty_linear = WD.joinpath("build", "cluster_uncertainty_min_residual_linear.pickle")
    cluster_uncertainty_mimo_linear = WD.joinpath(
        "build", "cluster_uncertainty_mimo_min_residual_linear.png"
    )
    cluster_uncertainty_msv_linear = WD.joinpath(
        "build", "cluster_uncertainty_msv_min_residual_linear.png"
    )
    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_generate_uncertainty_weights_for_cluster_models_min_residual,
                (
                    cluster_residuals_linear,
                    cluster_nominal,
                    cluster_uncertainty_linear,
                    cluster_uncertainty_mimo_linear,
                    cluster_uncertainty_msv_linear,
                    orders_linear,
                    "linear",
                ),
            )
        ],
        "file_dep": [cluster_residuals_linear, cluster_nominal],
        "targets": [
            cluster_uncertainty_linear,
            cluster_uncertainty_mimo_linear,
            cluster_uncertainty_msv_linear,
        ],
        "clean": True,
    }
    for cl in range(CLUSTERING_NUM):
        for c in range (K):
            cluster_uncertainty_koopman = WD.joinpath(
                "build", "cl_un/koopman/cluster_uncertainty_cl_"+str(cl)+"_center_"+str(c)+".pickle"
            )
            cluster_uncertainty_mimo_koopman = WD.joinpath(
                "build", "cl_un/koopman/cluster_uncertainty_mimo_cl_"+str(cl)+"_center_"+str(c)+".png"
            )
            cluster_uncertainty_msv_koopman = WD.joinpath(
                "build", "cl_un/koopman/cluster_uncertainty_msv_"+str(cl)+"_center_"+str(c)+".png"
            )
    
            yield {
                "name": "koopman",
                "actions": [
                    (
                        actions.action_generate_uncertainty_weights_for_cluster_models,
                        (
                            cluster_residuals_koopman,
                            cluster_uncertainty_koopman,
                            cluster_uncertainty_mimo_koopman,
                            cluster_uncertainty_msv_koopman,
                            orders_koopman,
                            cl,
                            c,
                            "koopman",
                        ),
                    )
                ],
                "file_dep": [cluster_residuals_koopman],
                "targets": [
                    cluster_uncertainty_koopman,
                    cluster_uncertainty_mimo_koopman,
                    cluster_uncertainty_msv_koopman,
                ],
                "clean": True,
            }
            
            
            cluster_uncertainty_linear = WD.joinpath(
                "build", "cl_un/linear/cluster_uncertainty_cl_"+str(cl)+"_center_"+str(c)+".pickle"
            )
            cluster_uncertainty_mimo_linear = WD.joinpath(
                "build", "cl_un/linear/cluster_uncertainty_mimo_cl_"+str(cl)+"_center_"+str(c)+".png"
            )
            cluster_uncertainty_msv_linear = WD.joinpath(
                "build", "cl_un/linear/cluster_uncertainty_msv_"+str(cl)+"_center_"+str(c)+".png"
            )
            yield {
                "name": "linear_noload",
                "actions": [
                    (
                        actions.action_generate_uncertainty_weights_for_cluster_models_min_residual,
                        (
                            cluster_residuals_linear,
                            cluster_uncertainty_linear,
                            cluster_uncertainty_mimo_linear,
                            cluster_uncertainty_msv_linear,
                            orders_linear,
                            cl,
                            c,
                            "linear",
                        ),
                    )
                ],
                "file_dep": [cluster_residuals_linear],
                "targets": [
                    cluster_uncertainty_linear,
                    cluster_uncertainty_mimo_linear,
                    cluster_uncertainty_msv_linear,
                ],
                "clean": True,
            }
    
def task_generate_uncertainty_weights():
    """Generate uncertainty weights models."""
    residuals_koopman = WD.joinpath("build", "residuals_koopman.pickle")
    orders_koopman = np.array(
        [
            [1, 3],
            [3, 3],
        ]
    )
    uncertainty_koopman_noload = WD.joinpath(
        "build", "uncertainty_koopman_noload.pickle"
    )
    uncertainty_mimo_koopman_noload = WD.joinpath(
        "build", "uncertainty_mimo_koopman_noload.png"
    )
    uncertainty_msv_koopman_noload = WD.joinpath(
        "build", "uncertainty_msv_koopman_noload.png"
    )
    nominal_noload = WD.joinpath("build", "nominal_noload.txt")
    yield {
        "name": "koopman_noload",
        "actions": [
            (
                actions.action_generate_uncertainty_weights,
                (
                    residuals_koopman,
                    nominal_noload,
                    uncertainty_koopman_noload,
                    uncertainty_mimo_koopman_noload,
                    uncertainty_msv_koopman_noload,
                    orders_koopman,
                    "koopman",
                    "noload",
                ),
            )
        ],
        "file_dep": [residuals_koopman],
        "targets": [
            uncertainty_koopman_noload,
            nominal_noload,
            uncertainty_mimo_koopman_noload,
            uncertainty_msv_koopman_noload,
        ],
        "clean": True,
    }
    uncertainty_koopman_load = WD.joinpath("build", "uncertainty_koopman_load.pickle")
    uncertainty_mimo_koopman_load = WD.joinpath(
        "build", "uncertainty_mimo_koopman_load.png"
    )
    uncertainty_msv_koopman_load = WD.joinpath(
        "build", "uncertainty_msv_koopman_load.png"
    )
    nominal_load = WD.joinpath("build", "nominal_load.txt")
    yield {
        "name": "koopman_load",
        "actions": [
            (
                actions.action_generate_uncertainty_weights,
                (
                    residuals_koopman,
                    nominal_load,
                    uncertainty_koopman_load,
                    uncertainty_mimo_koopman_load,
                    uncertainty_msv_koopman_load,
                    orders_koopman,
                    "koopman",
                    "load",
                ),
            )
        ],
        "file_dep": [residuals_koopman],
        "targets": [
            uncertainty_koopman_load,
            nominal_load,
            uncertainty_mimo_koopman_load,
            uncertainty_msv_koopman_load,
        ],
        "clean": True,
    }
    residuals_linear = WD.joinpath("build", "residuals_linear.pickle")
    orders_linear = np.array(
        [
            [1, 2],
            [1, 2],
        ]
    )
    uncertainty_linear_noload = WD.joinpath("build", "uncertainty_linear_noload.pickle")
    uncertainty_mimo_linear_noload = WD.joinpath(
        "build", "uncertainty_mimo_linear_noload.png"
    )
    uncertainty_msv_linear_noload = WD.joinpath(
        "build", "uncertainty_msv_linear_noload.png"
    )
    yield {
        "name": "linear_noload",
        "actions": [
            (
                actions.action_generate_uncertainty_weights,
                (
                    residuals_linear,
                    nominal_noload,
                    uncertainty_linear_noload,
                    uncertainty_mimo_linear_noload,
                    uncertainty_msv_linear_noload,
                    orders_linear,
                    "linear",
                    "noload",
                ),
            )
        ],
        "file_dep": [residuals_linear, nominal_noload],
        "targets": [
            uncertainty_linear_noload,
            uncertainty_mimo_linear_noload,
            uncertainty_msv_linear_noload,
        ],
        "clean": True,
    }
    uncertainty_linear_load = WD.joinpath("build", "uncertainty_linear_load.pickle")
    uncertainty_mimo_linear_load = WD.joinpath(
        "build", "uncertainty_mimo_linear_load.png"
    )
    uncertainty_msv_linear_load = WD.joinpath(
        "build", "uncertainty_msv_linear_load.png"
    )
    yield {
        "name": "linear_load",
        "actions": [
            (
                actions.action_generate_uncertainty_weights,
                (
                    residuals_linear,
                    nominal_load,
                    uncertainty_linear_load,
                    uncertainty_mimo_linear_load,
                    uncertainty_msv_linear_load,
                    orders_linear,
                    "linear",
                    "load",
                ),
            )
        ],
        "file_dep": [residuals_linear, nominal_load],
        "targets": [
            uncertainty_linear_load,
            uncertainty_mimo_linear_load,
            uncertainty_msv_linear_load,
        ],
        "clean": True,
    }

def task_synthesize_cluster_observer_design_phase():    
    cluster_models_linear = WD.joinpath("build", "cluster_models_linear.pickle")
    cluster_models_koopman = WD.joinpath("build", "cluster_models_koopman.pickle")
    for cl in range(CLUSTERING_NUM):
        for c in range (K):
            cluster_uncertainty_linear = WD.joinpath(
                "build", "cl_un/linear/cluster_uncertainty_cl_"+str(cl)+"_center_"+str(c)+".pickle"
            )
            cluster_observer_linear = WD.joinpath(
                "build", "cl_ob/linear/cluster_observer_cl_"+str(cl)+"_center_"+str(c)+".pickle"
            )
            cluster_weight_plot_linear = WD.joinpath(
                "build", "cl_ob/linear/cluster_observer_weight_cl_"+str(cl)+"_center_"+str(c)+".png"
            )
            yield {
                "name": "linear",
                "actions": [
                    (
                        actions.action_synthesize_cluster_observer_design_phase,
                        (
                            cluster_models_linear,
                            cluster_uncertainty_linear,
                            cluster_observer_linear,
                            cluster_weight_plot_linear,
                            cl,
                            c,
                            "linear",
                        ),
                    )
                ],
                "file_dep": [cluster_models_linear, cluster_uncertainty_linear],
                "targets": [
                    cluster_observer_linear,
                    cluster_weight_plot_linear
                ],
                "clean": True,
            }
            cluster_uncertainty_koopman = WD.joinpath(
                "build", "cl_un/koopman/cluster_uncertainty_cl_"+str(cl)+"_center_"+str(c)+".pickle"
            )
            cluster_observer_koopman = WD.joinpath(
                "build", "cl_ob/koopman/cluster_observer_cl_"+str(cl)+"_center_"+str(c)+".pickle"
            )
            cluster_weight_plot_koopman = WD.joinpath(
                "build", "cl_ob/koopman/cluster_observer_weight_cl_"+str(cl)+"_center_"+str(c)+".png"
            )
            yield {
                "name": "koopman",
                "actions": [
                    (
                        actions.action_synthesize_cluster_observer_design_phase,
                        (
                            cluster_models_koopman,
                            cluster_uncertainty_koopman,
                            cluster_observer_koopman,
                            cluster_weight_plot_koopman,
                            cl,
                            c,
                            "koopman",
                        ),
                    )
                ],
                "file_dep": [cluster_models_koopman, cluster_uncertainty_koopman],
                "targets": [
                    cluster_observer_koopman,
                    cluster_weight_plot_koopman
                ],
                "clean": True,
            }
            
def task_combine_uncertainties_observer():
    cluster_uncertainties_linear = WD.joinpath("build/cl_un/linear/")
    cluster_observers_linear = WD.joinpath("build/cl_ob/linear/")
    cluster_uncertainty_linear = WD.joinpath("build", "cluster_uncertainty_linear.pickle")
    cluster_observer_linear = WD.joinpath("build", "cluster_observer_linear.pickle")

    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_combine_uncertainties_observations,
                (
                    cluster_uncertainties_linear,
                    cluster_observers_linear,
                    cluster_uncertainty_linear,
                    cluster_observer_linear,
                    CLUSTERING_NUM,
                    K,
                ),
            )
        ],
        "file_dep": [cluster_uncertainties_linear, cluster_observers_linear],
        "targets": [
            cluster_uncertainty_linear,
            cluster_observer_linear
        ],
        "clean": True,
    }
    
    cluster_uncertainties_koopman = WD.joinpath("build/cl_un/koopman/")
    cluster_observers_koopman = WD.joinpath("build/cl_ob/koopman/")
    cluster_uncertainty_koopman = WD.joinpath("build", "cluster_uncertainty_koopman.pickle")
    cluster_observer_koopman = WD.joinpath("build", "cluster_observer_koopman.pickle")

    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_combine_uncertainties_observations,
                (
                    cluster_uncertainties_koopman,
                    cluster_observers_koopman,
                    cluster_uncertainty_koopman,
                    cluster_observer_koopman,
                    CLUSTERING_NUM,
                    K,
                ),
            )
        ],
        "file_dep": [cluster_uncertainties_koopman, cluster_observers_koopman],
        "targets": [
            cluster_uncertainty_koopman,
            cluster_observer_koopman
        ],
        "clean": True,
    }
    

def task_synthesize_cluster_observer_test_phase():
    
    
    dataset = WD.joinpath("build", "dataset.pickle")
    cluster_split_info = WD.joinpath("build", "cluster_split_info.pickle")
    cluster_centers = WD.joinpath("build", "DTW_K_means_clusters.pickle")
    cluster_models_linear = WD.joinpath("build", "cluster_models_linear.pickle")
    cluster_uncertainty_linear = WD.joinpath("build", "cluster_uncertainty_linear.pickle")
    cluster_observer_linear = WD.joinpath("build", "cluster_observer_linear.pickle")
    cluster_traj_plot_linear = WD.joinpath("build/cluster_observer_traj_linear")
    cluster_err_plot_linear = WD.joinpath("build/cluster_observer_err_linear")
    cluster_fft_plot_linear = WD.joinpath("build/cluster_observer_fft_linear")
    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_synthesize_cluster_observer_test_phase,
                (
                    dataset,
                    cluster_split_info,
                    cluster_centers,
                    cluster_models_linear,
                    cluster_uncertainty_linear,
                    cluster_observer_linear,
                    cluster_traj_plot_linear,
                    cluster_err_plot_linear,
                    cluster_fft_plot_linear,
                    FEATURES_TO_CLUSTER,
                    K,
                    "linear",
                ),
            )
        ],
        "file_dep": [dataset,
                     cluster_split_info,
                     cluster_centers,
                     cluster_models_linear,
                     cluster_uncertainty_linear,
                     cluster_observer_linear,
        ],
        "targets": [
            cluster_traj_plot_linear,
            cluster_err_plot_linear,
            cluster_fft_plot_linear,
        ],
        "clean": True,
    }
    
    cluster_models_koopman = WD.joinpath("build", "cluster_models_koopman.pickle")
    cluster_uncertainty_koopman = WD.joinpath("build", "cluster_uncertainty_koopman.pickle")
    cluster_observer_koopman = WD.joinpath("build", "cluster_observer_koopman.pickle")
    cluster_traj_plot_koopman = WD.joinpath("build/cluster_observer_traj_koopman")
    cluster_err_plot_koopman = WD.joinpath("build/cluster_observer_err_koopman")
    cluster_fft_plot_koopman = WD.joinpath("build/cluster_observer_fft_koopman")
    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_synthesize_cluster_observer_test_phase,
                (
                    dataset,
                    cluster_split_info,
                    cluster_centers,
                    cluster_models_koopman,
                    cluster_uncertainty_koopman,
                    cluster_observer_koopman,
                    cluster_traj_plot_koopman,
                    cluster_err_plot_koopman,
                    cluster_fft_plot_koopman,
                    FEATURES_TO_CLUSTER,
                    K,
                    "koopman",
                ),
            )
        ],
        "file_dep": [dataset,
                     cluster_split_info,
                     cluster_centers,
                     cluster_models_koopman,
                     cluster_uncertainty_koopman,
                     cluster_observer_koopman,
        ],
        "targets": [
            cluster_traj_plot_koopman,
            cluster_err_plot_koopman,
            cluster_fft_plot_koopman,
        ],
        "clean": True,
    }


def task_synthesize_observer():
    """Synthesize observer."""
    dataset = WD.joinpath("build", "dataset.pickle")
    models_linear = WD.joinpath("build", "models_linear.pickle")
    uncertainty_linear = WD.joinpath("build", "uncertainty_linear_noload.pickle")
    observer_linear = WD.joinpath("build", "observer_linear.pickle")
    weight_plot_linear = WD.joinpath("build", "observer_weight_linear.png")
    traj_plot_linear = WD.joinpath("build", "observer_traj_linear.png")
    err_plot_linear = WD.joinpath("build", "observer_err_linear.png")
    fft_plot_linear = WD.joinpath("build", "observer_fft_linear.png")
    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_synthesize_observer,
                (
                    dataset,
                    models_linear,
                    uncertainty_linear,
                    observer_linear,
                    weight_plot_linear,
                    traj_plot_linear,
                    err_plot_linear,
                    fft_plot_linear,
                    "linear",
                ),
            )
        ],
        "file_dep": [dataset, models_linear, uncertainty_linear],
        "targets": [
            observer_linear,
            weight_plot_linear,
            traj_plot_linear,
            err_plot_linear,
            fft_plot_linear,
        ],
        "clean": True,
    }
    models_koopman = WD.joinpath("build", "models_koopman.pickle")
    uncertainty_koopman = WD.joinpath("build", "uncertainty_koopman_noload.pickle")
    observer_koopman = WD.joinpath("build", "observer_koopman.pickle")
    weight_plot_koopman = WD.joinpath("build", "observer_weight_koopman.png")
    traj_plot_koopman = WD.joinpath("build", "observer_traj_koopman.png")
    err_plot_koopman = WD.joinpath("build", "observer_err_koopman.png")
    fft_plot_koopman = WD.joinpath("build", "observer_fft_koopman.png")
    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_synthesize_observer,
                (
                    dataset,
                    models_koopman,
                    uncertainty_koopman,
                    observer_koopman,
                    weight_plot_koopman,
                    traj_plot_koopman,
                    err_plot_koopman,
                    fft_plot_koopman,
                    "koopman",
                ),
            )
        ],
        "file_dep": [dataset, models_koopman, uncertainty_koopman],
        "targets": [
            observer_koopman,
            weight_plot_koopman,
            traj_plot_koopman,
            err_plot_koopman,
            fft_plot_koopman,
        ],
        "clean": True,
    }


def task_plot_fft():
    """Plot error FFT."""
    dataset = WD.joinpath("build", "dataset.pickle")
    error_fft = WD.joinpath("figures", "error_fft.pdf")
    return {
        "actions": [
            (
                actions.action_plot_fft,
                (
                    dataset,
                    error_fft,
                ),
            )
        ],
        "file_dep": [dataset],
        "targets": [error_fft],
        "clean": True,
    }


def task_plot_model_predictions():
    """Plot model predictions."""
    dataset = WD.joinpath("build", "dataset.pickle")
    models_linear = WD.joinpath("build", "models_linear.pickle")
    models_koopman = WD.joinpath("build", "models_koopman.pickle")
    pred_ref = WD.joinpath("figures", "model_predictions_ref.pdf")
    pred_traj = WD.joinpath("figures", "model_predictions_traj.pdf")
    pred_err = WD.joinpath("figures", "model_predictions_err.pdf")
    pred_fft = WD.joinpath("figures", "model_predictions_fft.pdf")
    return {
        "actions": [
            (
                actions.action_plot_model_predictions,
                (
                    dataset,
                    models_linear,
                    models_koopman,
                    pred_ref,
                    pred_traj,
                    pred_err,
                    pred_fft,
                ),
            )
        ],
        "file_dep": [dataset, models_linear, models_koopman],
        "targets": [pred_ref, pred_traj, pred_err, pred_fft],
        "clean": True,
    }


def task_plot_model_tfs():
    """Plot model transfer functions."""
    dataset = WD.joinpath("build", "dataset.pickle")
    models_linear = WD.joinpath("build", "models_linear.pickle")
    models_koopman = WD.joinpath("build", "models_koopman.pickle")
    tfs_msv_linear = WD.joinpath("figures", "model_tfs_msv_linear.pdf")
    tfs_msv_koopman = WD.joinpath("figures", "model_tfs_msv_koopman.pdf")
    tfs_mimo_linear = WD.joinpath("figures", "model_tfs_mimo_linear.pdf")
    tfs_mimo_koopman = WD.joinpath("figures", "model_tfs_mimo_koopman.pdf")
    return {
        "actions": [
            (
                actions.action_plot_model_tfs,
                (
                    dataset,
                    models_linear,
                    models_koopman,
                    tfs_msv_linear,
                    tfs_msv_koopman,
                    tfs_mimo_linear,
                    tfs_mimo_koopman,
                ),
            )
        ],
        "file_dep": [dataset, models_linear, models_koopman],
        "targets": [
            tfs_msv_linear,
            tfs_msv_koopman,
            tfs_mimo_linear,
            tfs_mimo_koopman,
        ],
        "clean": True,
    }


def task_plot_observer():
    """Plot observer."""
    dataset = WD.joinpath("build/dataset.pickle")
    uncertainty_linear = WD.joinpath("build", "uncertainty_linear_noload.pickle")
    uncertainty_koopman = WD.joinpath("build", "uncertainty_koopman_noload.pickle")
    models_linear = WD.joinpath("build", "models_linear.pickle")
    models_koopman = WD.joinpath("build", "models_koopman.pickle")
    observer_linear = WD.joinpath("build", "observer_linear.pickle")
    observer_koopman = WD.joinpath("build", "observer_koopman.pickle")
    obs_weights_linear = WD.joinpath("figures", "observer_weights_linear.pdf")
    obs_weights_koopman = WD.joinpath("figures", "observer_weights_koopman.pdf")
    obs_weights = WD.joinpath("figures", "observer_weights.pdf")
    obs_nom_noload_traj = WD.joinpath("figures", "observer_nominal_noload_traj.pdf")
    obs_nom_noload_err = WD.joinpath("figures", "observer_nominal_noload_err.pdf")
    obs_nom_noload_psd = WD.joinpath("figures", "observer_nominal_noload_psd.pdf")
    obs_nom_load_traj = WD.joinpath("figures", "observer_nominal_load_traj.pdf")
    obs_nom_load_err = WD.joinpath("figures", "observer_nominal_load_err.pdf")
    obs_nom_load_psd = WD.joinpath("figures", "observer_nominal_load_psd.pdf")
    obs_offnom_noload_traj = WD.joinpath(
        "figures", "observer_offnominal_noload_traj.pdf"
    )
    obs_offnom_noload_err = WD.joinpath("figures", "observer_offnominal_noload_err.pdf")
    obs_offnom_noload_psd = WD.joinpath("figures", "observer_offnominal_noload_psd.pdf")
    return {
        "actions": [
            (
                actions.action_plot_observer,
                (
                    dataset,
                    uncertainty_linear,
                    uncertainty_koopman,
                    models_linear,
                    models_koopman,
                    observer_linear,
                    observer_koopman,
                    obs_weights_linear,
                    obs_weights_koopman,
                    obs_weights,
                    obs_nom_noload_traj,
                    obs_nom_noload_err,
                    obs_nom_noload_psd,
                    obs_nom_load_traj,
                    obs_nom_load_err,
                    obs_nom_load_psd,
                    obs_offnom_noload_traj,
                    obs_offnom_noload_err,
                    obs_offnom_noload_psd,
                ),
            )
        ],
        "file_dep": [
            dataset,
            uncertainty_linear,
            uncertainty_koopman,
            models_linear,
            models_koopman,
            observer_linear,
            observer_koopman,
        ],
        "targets": [
            obs_weights_linear,
            obs_weights_koopman,
            obs_weights,
            obs_nom_noload_traj,
            obs_nom_noload_err,
            obs_nom_noload_psd,
            obs_nom_load_traj,
            obs_nom_load_err,
            obs_nom_load_psd,
            obs_offnom_noload_traj,
            obs_offnom_noload_err,
            obs_offnom_noload_psd,
        ],
        "clean": True,
    }


def task_plot_phase():
    """Plot phase."""
    phase_path = WD.joinpath("build", "phase.pickle")
    phase_plot_path = WD.joinpath("figures", "phase.pdf")
    phase_txt_path = WD.joinpath("figures", "phase.txt")
    return {
        "actions": [
            (
                actions.action_plot_phase,
                (
                    phase_path,
                    phase_plot_path,
                    phase_txt_path,
                ),
            )
        ],
        "file_dep": [phase_path],
        "targets": [phase_plot_path, phase_txt_path],
        "clean": True,
    }


def task_plot_uncertainty():
    """Plot uncertainty."""
    # Koopman action
    residuals_koopman_path = WD.joinpath("build", "residuals_koopman.pickle")
    uncertainty_koopman_path = WD.joinpath("build", "uncertainty_koopman_noload.pickle")
    nominal_path = WD.joinpath("build", "nominal_noload.txt")
    targets_koopman = [
        "uncertainty_bound_mimo_koopman.pdf",
        "uncertainty_bound_msv_koopman.pdf",
        "uncertainty_koopman_additive.pdf",
        "uncertainty_koopman_input_multiplicative.pdf",
        "uncertainty_koopman_inverse_additive.pdf",
        "uncertainty_koopman_inverse_input_multiplicative.pdf",
        "uncertainty_koopman_inverse_output_multiplicative.pdf",
        "uncertainty_koopman_output_multiplicative.pdf",
        "uncertainty_koopman.pdf",
    ]
    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_plot_uncertainty,
                (
                    residuals_koopman_path,
                    uncertainty_koopman_path,
                    nominal_path,
                    "koopman",
                ),
            )
        ],
        "file_dep": [residuals_koopman_path, uncertainty_koopman_path],
        "targets": [WD.joinpath("figures", t) for t in targets_koopman],
        "clean": True,
    }
    # Linear action
    residuals_linear_path = WD.joinpath("build", "residuals_linear.pickle")
    uncertainty_linear_path = WD.joinpath("build", "uncertainty_linear_noload.pickle")
    targets_linear = [
        "uncertainty_bound_mimo_linear.pdf",
        "uncertainty_bound_msv_linear.pdf",
        "uncertainty_linear_additive.pdf",
        "uncertainty_linear_input_multiplicative.pdf",
        "uncertainty_linear_inverse_additive.pdf",
        "uncertainty_linear_inverse_input_multiplicative.pdf",
        "uncertainty_linear_inverse_output_multiplicative.pdf",
        "uncertainty_linear_output_multiplicative.pdf",
        "uncertainty_linear.pdf",
    ]
    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_plot_uncertainty,
                (
                    residuals_linear_path,
                    uncertainty_linear_path,
                    nominal_path,
                    "linear",
                ),
            )
        ],
        "file_dep": [residuals_linear_path, uncertainty_linear_path],
        "targets": [WD.joinpath("figures", t) for t in targets_linear],
        "clean": True,
    }


def task_plot_outliers():
    """Plot outliers."""
    # Koopman action
    residuals_koopman_path = WD.joinpath("build", "residuals_koopman.pickle")
    uncertainty_koopman_path = WD.joinpath("build", "uncertainty_koopman_load.pickle")
    models_koopman_path = WD.joinpath("build", "models_koopman.pickle")
    nominal_path = WD.joinpath("build", "nominal_load.txt")
    targets_koopman = [
        "outliers_bound_mimo_koopman.pdf",
        "outliers_bound_msv_koopman.pdf",
        "outliers_koopman_additive.pdf",
        "outliers_koopman_input_multiplicative.pdf",
        "outliers_koopman_inverse_additive.pdf",
        "outliers_koopman_inverse_input_multiplicative.pdf",
        "outliers_koopman_inverse_output_multiplicative.pdf",
        "outliers_koopman_output_multiplicative.pdf",
    ]
    yield {
        "name": "koopman",
        "actions": [
            (
                actions.action_plot_outliers,
                (
                    residuals_koopman_path,
                    uncertainty_koopman_path,
                    models_koopman_path,
                    nominal_path,
                    "koopman",
                ),
            )
        ],
        "file_dep": [residuals_koopman_path, uncertainty_koopman_path],
        "targets": [WD.joinpath("figures", t) for t in targets_koopman],
        "clean": True,
    }
    # Linear action
    residuals_linear_path = WD.joinpath("build", "residuals_linear.pickle")
    uncertainty_linear_path = WD.joinpath("build", "uncertainty_linear_load.pickle")
    models_linear_path = WD.joinpath("build", "models_linear.pickle")
    targets_linear = [
        "outliers_bound_mimo_linear.pdf",
        "outliers_bound_msv_linear.pdf",
        "outliers_linear_additive.pdf",
        "outliers_linear_input_multiplicative.pdf",
        "outliers_linear_inverse_additive.pdf",
        "outliers_linear_inverse_input_multiplicative.pdf",
        "outliers_linear_inverse_output_multiplicative.pdf",
        "outliers_linear_output_multiplicative.pdf",
    ]
    yield {
        "name": "linear",
        "actions": [
            (
                actions.action_plot_outliers,
                (
                    residuals_linear_path,
                    uncertainty_linear_path,
                    models_linear_path,
                    nominal_path,
                    "linear",
                ),
            )
        ],
        "file_dep": [residuals_linear_path, uncertainty_linear_path],
        "targets": [WD.joinpath("figures", t) for t in targets_linear],
        "clean": True,
    }
