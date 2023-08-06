import os
import re
import numpy as np
import anndata as ad
import scanpy as sc
import pandas as pd
from sklearn.metrics.cluster import normalized_mutual_info_score
from sklearn.metrics import roc_curve, auc
from scipy.optimize import linear_sum_assignment

def find_top_bottom_genes(array, topN_total, bottomN_total, N_total, step_size=1):
    topN = 0
    bottomN = 0
    zeroN = 0

    unique_top_genes = set()
    unique_bottom_genes = set()
    unique_zero_genes = set()

    update_top_genes = True
    update_bottom_genes = True
    update_zero_genes = True

    while (len(unique_top_genes) < topN_total) or (len(unique_bottom_genes) < bottomN_total):
        if update_top_genes:
            topN += step_size
        if update_bottom_genes:
            bottomN += step_size

        for row in array:
            sorted_indices = np.argsort(row)

            if update_top_genes:
                top_indices = sorted_indices[-topN:]
                unique_top_genes.update(top_indices)

            if update_bottom_genes:
                bottom_indices = sorted_indices[:bottomN]
                unique_bottom_genes.update(bottom_indices)

        if len(unique_top_genes) >= topN_total:
            update_top_genes = False
        if len(unique_bottom_genes) >= bottomN_total:
            update_bottom_genes = False

    # Remove top and bottom genes from the candidate list for zero genes
    remaining_indices = set(range(array.shape[1])) - unique_top_genes - unique_bottom_genes

    while len(unique_top_genes) + len(unique_bottom_genes) + len(unique_zero_genes) < N_total:
        zeroN += step_size

        for row in array:
            sorted_indices = np.argsort(row)

            zero_indices = [idx for idx in sorted_indices if idx in remaining_indices]
            zero_indices_sorted_by_distance = sorted(zero_indices, key=lambda x: abs(row[x]))
            zero_indices_closest_to_zero = zero_indices_sorted_by_distance[:zeroN]

            unique_zero_genes.update(zero_indices_closest_to_zero)

            # Check if the size of the three unique gene sets has reached N_total
            if len(unique_top_genes) + len(unique_bottom_genes) + len(unique_zero_genes) >= N_total:
                break

    return list(unique_top_genes), list(unique_bottom_genes), list(unique_zero_genes), topN, bottomN, zeroN

def find_directories(path, pattern):
    # Initialize an empty list to store matched directories
    # Initialize an empty list to store matched directories
    matched_directories = []

    # Initialize an empty list to store parsed results
    parsed_results = []

    # Iterate through the directories under the specified path
    for folder_name in os.listdir(path):
        match = re.match(pattern, folder_name)
        if match:
            matched_directories.append(folder_name)
            parsed_results.append(match.groups())

    # Convert the parsed results into a dataframe
    df = pd.DataFrame(parsed_results, columns=['method', 'ep', 'nlv', 'simseed', 'seed', 'N', 'G', 'T', 'topk', 'pip_full', 'pip', 'flip'])
    df['directory'] = matched_directories

    # Drop the pip_full column
    df = df.drop(columns=['pip_full'])

    # Replace None values in pip with NA
    df['pip'] = df['pip'].replace({None: np.nan})

    # Convert flip values to boolean
    df['flip'] = df['flip'].notna()

    return df 

def create_topic_label(N, T):
    cells_per_group = N // T

    # Create a list of cell type labels for each group
    cell_type_labels = list(range(1, T+1))

    # Create the topic_label array
    topic_label = np.zeros((N, T))

    for i, cell_type_label in enumerate(cell_type_labels):
        start = i * cells_per_group
        end = (i + 1) * cells_per_group
        topic_label[start:end, i] = cell_type_label

    return topic_label

def compute_nmi(topic_label, theta):
    # Convert both topic_label and theta into 1D arrays
    topic_label_1d = np.sum(topic_label, axis=1)
    topic_hat_1d = np.argmax(theta, axis=1)
    
    # Compute the normalized mutual information
    nmi = normalized_mutual_info_score(topic_label_1d, topic_hat_1d)
    
    return nmi

def compute_pca(adata, T):
    sc.pp.pca(adata, n_comps = T)
    weight_pca = adata.varm['PCs'].T
    pc_matrix = adata.obsm['X_pca']
    
    adata_unspliced = adata.copy()
    adata_unspliced.X = adata.obsm["unspliced_expression"].copy()
    adata_concat = ad.concat([adata, adata_unspliced])
    sc.pp.pca(adata_concat, n_comps = T)
    weight_pca_concat = adata_concat.varm['PCs'].T
    pc_matrix_concat = adata_concat.obsm['X_pca']
    
    return weight_pca, pc_matrix, weight_pca_concat, pc_matrix_concat

def calculate_common_entries(weights, betas, k=20):
    result = {}

    for weight_key, weight in weights.items():
        for beta_key, beta in betas.items():
            # Get the indices of the top and bottom K values for each row
            topk_idx = np.argpartition(weight, -k)[:, -k:] if weight.size != 0 else np.array([])
            bottomk_idx = np.argpartition(weight, k)[:, :k] if weight.size != 0 else np.array([])

            # Get the top and bottom K values from beta
            topk_beta = np.argpartition(beta, -k)[:, -k:] if beta.size != 0 else np.array([])
            bottomk_beta = np.argpartition(beta, k)[:, :k] if beta.size != 0 else np.array([])

            # Count the number of common entries for each pairwise combination of rows
            num_common_top = np.zeros([topk_idx.shape[0],topk_beta.shape[0]]) if weight.size != 0 and beta.size != 0 else np.array([])
            num_common_bottom = num_common_top.copy() if weight.size != 0 and beta.size != 0 else np.array([])
            
            if weight.size != 0 and beta.size != 0:
                for i in range(topk_idx.shape[0]):
                    for j in range(topk_beta.shape[0]):
                        common_top = np.intersect1d(topk_idx[i], topk_beta[j])
                        num_common_top[i,j] = len(common_top)
                        common_bottom = np.intersect1d(bottomk_idx[i], bottomk_beta[j])
                        num_common_bottom[i,j] = len(common_bottom)

            # Add the number of common entries for each pairwise combination of rows to the dictionary
            result[(weight_key, beta_key)] = [num_common_top, num_common_bottom]

    return result


def compute_auc(weight, weight_hat, K):
    
    # Prepare ground truth labels for weight
    #K = 30
    ground_truth = np.where(weight.argsort(axis=1) >= weight.shape[1] - K, 1, 0)
    # Initialize AUC matrix
    auc_matrix = np.zeros((weight.shape[0], weight_hat.shape[0]))

    # Nested loop to calculate AUC for each pairwise combination of rows
    for i in range(weight.shape[0]):
        for j in range(weight_hat.shape[0]):
            gt_row = ground_truth[i]
            weight_hat_row = weight_hat[j]

            # Calculate ROC curve and AUC
            fpr, tpr, _ = roc_curve(gt_row, weight_hat_row)
            roc_auc = auc(fpr, tpr)

            # Store AUC in the matrix
            auc_matrix[i, j] = roc_auc

    # Convert the maximization problem to a minimization problem
    minimization_matrix = np.max(auc_matrix) - auc_matrix

    # Perform the Hungarian algorithm
    row_indices, col_indices = linear_sum_assignment(minimization_matrix)

    # Compute the sum of matched entries
    sum_auc_matched = auc_matrix[row_indices, col_indices].sum()
    mean_auc_matched = sum_auc_matched / auc_matrix.shape[0]
    
    return mean_auc_matched, sum_auc_matched, auc_matrix, row_indices, col_indices

def create_dataframe_from_results(results):
    data = []
    data_col = []
    for keys, values in results.items():
        weight_key, beta_key = keys
        num_common_top, num_common_bottom = values

        if num_common_top.size != 0 and num_common_bottom.size != 0:
            max_top = np.max(num_common_top, axis=1)
            max_bottom = np.max(num_common_bottom, axis=1)

            for i in range(len(max_top)):
                data.append([weight_key, beta_key, "top", i, max_top[i]])
                data.append([weight_key, beta_key, "bottom", i, max_bottom[i]])

            max_top_col = np.max(num_common_top, axis=0)
            max_bottom_col = np.max(num_common_bottom, axis=0)
            
            for j in range(len(max_top_col)):
                data_col.append([weight_key, beta_key, "top", j, max_top_col[j]])
                data_col.append([weight_key, beta_key, "bottom", j, max_bottom_col[j]])
                
    df = pd.DataFrame(data, columns=["Weight", "Beta", "Type", "Row", "Max"])
    df_col = pd.DataFrame(data_col, columns=["Weight", "Beta", "Type", "Col", "Max"])
    return df, df_col