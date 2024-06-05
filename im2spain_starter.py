"""
The goal of this assignment is to predict GPS coordinates from image features using k-Nearest Neighbors.
Specifically, have featurized 28616 geo-tagged images taken in Spain split into training and test sets (27.6k and 1k).

The assignment walks students through:
    * visualizing the data
    * implementing and evaluating a kNN regression model
    * analyzing model performance as a function of dataset size
    * comparing kNN against linear regression

Images were filtered from Mousselly-Sergieh et al. 2014 (https://dl.acm.org/doi/10.1145/2557642.2563673)
and scraped from Flickr in 2024. The image features were extracted using CLIP ViT-L/14@336px (https://openai.com/clip/).
"""

import matplotlib.pyplot as plt
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from PIL import Image



def plot_data(train_feats, train_labels):
    """
    Input:
        train_feats: Training set image features
        train_labels: Training set GPS (lat, lon)

    Output:
        Displays plot of image locations, and first two PCA dimensions vs longitude
    """
    # Plot image locations (use marker='.' for better visibility)
    plt.scatter(train_labels[:, 1], train_labels[:, 0], marker=".")
    plt.title('Image Locations')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.show()

    # Run PCA on training_feats
    ##### TODO(a): Your Code Here #####
    transformed_feats = StandardScaler().fit_transform(train_feats)
    transformed_feats = PCA(n_components=2).fit_transform(transformed_feats)

    # Plot images by first two PCA dimensions (use marker='.' for better visibility)
    plt.scatter(transformed_feats[:, 0],     # Select first column
                transformed_feats[:, 1],     # Select second column
                c=train_labels[:, 1],
                marker='.')
    plt.colorbar(label='Longitude')
    plt.title('Image Features by Longitude after PCA')
    plt.show()


def grid_search(train_features, train_labels, test_features, test_labels, is_weighted=False, verbose=True):
    """
    Input:
        train_features: Training set image features
        train_labels: Training set GPS (lat, lon) coords
        test_features: Test set image features
        test_labels: Test set GPS (lat, lon) coords
        is_weighted: Weight prediction by distances in feature space

    Output:
        Prints mean displacement error as a function of k
        Plots mean displacement error vs k

    Returns:
        Minimum mean displacement error
    """
    # Evaluate mean displacement error (in miles) of kNN regression for different values of k
    # Technically we are working with spherical coordinates and should be using spherical distances, but within a small
    # region like Spain we can get away with treating the coordinates as cartesian coordinates.
    knn = NearestNeighbors(n_neighbors=100).fit(train_features)

    if verbose:
        print(f'Running grid search for k (is_weighted={is_weighted})')

    ks = list(range(1, 11)) + [20, 30, 40, 50, 100]
    mean_errors = []
    for k in ks:
        distances, indices = knn.kneighbors(test_features, n_neighbors=k)

        errors = []
        for i, nearest in enumerate(indices):
            # Evaluate mean displacement error in miles for each test image
            # Assume 1 degree latitude is 69 miles and 1 degree longitude is 52 miles
            y = test_labels[i]

            ##### TODO(d): Your Code Here #####
            if is_weighted:
                # Weight prediction by inverse of distances in feature space
                weights = 1 / (distances[i] + 1e-8)  # Adding a small value to avoid division by zero
                weighted_mean_coords = np.average(train_labels[nearest], axis=0, weights=weights)
                displacement_error = np.sqrt(np.sum((y - weighted_mean_coords) ** 2)) * np.array([69, 52])
            else:
                # Predict by averaging coordinates of nearest neighbors
                predicted_coords = np.mean(train_labels[nearest], axis=0)
                displacement_error = np.sqrt(np.sum((y - predicted_coords) ** 2)) * np.array([69, 52])

            errors.append(displacement_error)

        # Calculate the mean displacement error for the current value of k
        mean_error = np.mean(errors)
        mean_errors.append(mean_error)
        if verbose:
            print(f'{k}-NN mean displacement error (miles): {mean_error:.1f}')

    # Plot error vs k for k Nearest Neighbors
    if verbose:
        plt.plot(ks, mean_errors)
        plt.xlabel('k')
        plt.ylabel('Mean Displacement Error (miles)')
        plt.title('Mean Displacement Error (miles) vs. k in kNN')
        if is_weighted:
            plt.title('Mean Displacement Error (miles) vs. k in kNN with Distance Weighting')
        else:
            plt.title('Mean Displacement Error (miles) vs. k in kNN')
        plt.show()

    return min(mean_errors)


def main():
    print("Predicting GPS from CLIP image features\n")

    # Import Data
    print("Loading Data")
    data = np.load('im2spain_data.npz')

    train_features = data['train_features']  # [N_train, dim] array
    test_features = data['test_features']    # [N_test, dim] array
    train_labels = data['train_labels']      # [N_train, 2] array of (lat, lon) coords
    test_labels = data['test_labels']        # [N_test, 2] array of (lat, lon) coords
    train_files = data['train_files']        # [N_train] array of strings
    test_files = data['test_files']          # [N_test] array of strings

    # Data Information
    print('Train Data Count:', train_features.shape[0])

    # Part A: Feature and label visualization (modify plot_data method)
    plot_data(train_features, train_labels)

    # Part C: Find the 5 nearest neighbors of test image 53633239060.jpg
    knn = NearestNeighbors(n_neighbors=3).fit(train_features)
    
    #my code starts
    # Find the index of the test image file in the test files list
    test_index = None
    for i, file_name in enumerate(test_files):
        if file_name == '53633239060.jpg':
            test_index = i
            break

    # Use knn to get the 3 nearest neighbors of the features of the test image
    distances, indices = knn.kneighbors(test_features[test_index:test_index+1])

    nearest_indices = indices[0]

    print("3 Nearest Neighbors:")
    for i, neighbor_index in enumerate(nearest_indices):
        neighbor_image_path = train_files[neighbor_index]
        print(neighbor_image_path)
        neighbor_coords = train_labels[neighbor_index]
        print(f"   Coordinates: {neighbor_coords}")
        
      

    #my code ends
    # Use knn to get the k nearest neighbors of the features of image 53633239060.jpg
    ##### TODO(c): Your Code Here #####
    def constant_baseline(train_labels, test_features):
        """
        Input:
            train_labels: Training set GPS (lat, lon) coords
            test_features: Test set image features

        Output:
            Constant baseline prediction for every test image
        """
        # Calculate the centroid of the training set coordinates
        centroid = np.mean(train_labels, axis=0)

        # Repeat the centroid for every test image
        num_test_images = test_features.shape[0]
        baseline_predictions = np.tile(centroid, (num_test_images, 1))

        return baseline_predictions

    # Part D: establish a naive baseline of predicting the mean of the training set
    ##### TODO(d): Your Code Here #####
    baseline_predictions = constant_baseline(train_labels, test_features)
    # Calculate the mean displacement error (MDE) in miles
    mde = np.mean(np.sqrt(np.sum((test_labels - baseline_predictions) ** 2, axis=1)))
    print(f"Constant Baseline Mean Displacement Error (miles): {mde:.2f}")

    # Part E: complete grid_search to find the best value of k
    grid_search(train_features, train_labels, test_features, test_labels)

    # Parts G: rerun grid search after modifications to find the best value of k
    grid_search(train_features, train_labels, test_features, test_labels, is_weighted=True)

    # Part H: compare to linear regression for different # of training points
    mean_errors_lin = []
    mean_errors_nn = []
    ratios = np.arange(0.1, 1.1, 0.1)
    for r in ratios:
        num_samples = int(r * len(train_features))
        ##### TODO(h): Your Code Here #####
        # Select a subset of training data based on the current ratio
        train_features_subset = train_features[:num_samples]
        train_labels_subset = train_labels[:num_samples]

        # Train linear regression model
        lin_reg_model = LinearRegression()
        lin_reg_model.fit(train_features_subset, train_labels_subset)
        lin_reg_predictions = lin_reg_model.predict(test_features)

        # Calculate mean displacement error for linear regression
        lin_reg_mde = np.mean(np.sqrt(np.sum((test_labels - lin_reg_predictions) ** 2, axis=1)))
        mean_errors_lin.append(lin_reg_mde)

        # Train k-NN model and perform grid search to find the best value of k
        knn_mde = grid_search(train_features_subset, train_labels_subset, test_features, test_labels)
        mean_errors_nn.append(knn_mde)

        print(f'\nTraining set ratio: {r} ({num_samples})')
        print(f'Linear Regression mean displacement error (miles): {lin_reg_mde:.1f}')
        print(f'kNN mean displacement error (miles): {knn_mde:.1f}')

    # Plot error vs training set size
    plt.plot(ratios, mean_errors_lin, label='Linear Regression')
    plt.plot(ratios, mean_errors_nn, label='kNN')
    plt.xlabel('Training Set Ratio')
    plt.ylabel('Mean Displacement Error (miles)')
    plt.title('Mean Displacement Error (miles) vs. Training Set Ratio')
    plt.legend()
    plt.show()
       

if __name__ == '__main__':
    main()
