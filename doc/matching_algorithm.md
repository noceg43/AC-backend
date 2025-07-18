# Matching Algorithm

The AlphaConnect API uses a sophisticated matching algorithm to pair users within a lobby based on their answers to a set of questions. This document provides an overview of the algorithm, the data it uses, and the steps it takes to create matches.

## Overview

The matching algorithm is implemented in the `AlphaConnectMatcher` class, which can be found in the `ml/MatchingAlgorithm.py` file. The goal of the algorithm is to create pairs of users with the minimum possible "disparity" between them. Disparity is a measure of how different two users' answers are.

The algorithm uses a combination of data preprocessing, dimensionality reduction, and a graph-based optimization algorithm to find the best possible pairings.

## Data

The algorithm takes as input a dictionary of user answers. This dictionary is fetched from the API by the `LobbyScheduler` when the matching process is triggered. The data is retrieved from the `/api/v0/collections/questions-with-match` endpoint, which returns a list of questions, each with a list of member answers.

The `AlphaConnectMatcher` class processes this data to create two key data structures:

*   **Weight Matrix:** A matrix that maps each answer to a numerical weight. This is used to convert the categorical answers into a numerical format that can be used by the algorithm.
*   **User DataFrame:** A dictionary that maps each user to a vector of their answers, represented by the weights from the weight matrix.

## Steps

The matching process consists of the following steps:

1.  **Data Preprocessing:** The raw user answers are processed to create the weight matrix and the user dataframe, as described above.

2.  **Dimensionality Reduction:** The user answer vectors are high-dimensional, which can make it difficult to compute distances between them. To address this, the algorithm uses Principal Component Analysis (PCA) to reduce the dimensionality of the data to 3 components.

3.  **Distance Calculation:** The algorithm calculates the pairwise distances between all users in the reduced-dimensional space. The result is a distance matrix where each entry `(i, j)` represents the distance between user `i` and user `j`.

4.  **Optimal Pairing:** The algorithm uses the Hungarian algorithm (implemented in `scipy.optimize.linear_sum_assignment`) to find the optimal pairing of users that minimizes the total distance. The Hungarian algorithm is a combinatorial optimization algorithm that solves the assignment problem in polynomial time.

5.  **Output:** The algorithm returns a list of pairs of users, sorted by their disparity value. Each pair includes the IDs of the two users and their disparity score.

## Technologies

The matching algorithm uses the following technologies:

*   **NumPy:** For numerical operations and array manipulation.
*   **scikit-learn:** For PCA, which is used for dimensionality reduction.
*   **SciPy:** For the Hungarian algorithm, which is used for optimal pairing, and for distance calculations.
