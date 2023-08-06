

import numpy as np

def euclidean_distance(x1, x2):
    return np.sqrt(np.sum((x1 - x2) ** 2))

class KMeans:
    def __init__(self, max_distance, max_iters=100):
        self.max_distance = max_distance
        self.max_iters = max_iters
    
    def initialize_clusters(self, X):
        n_samples, _ = X.shape
        centroid = X[np.random.choice(n_samples)]
        return [centroid]
    
    def assign_clusters(self, X, centroids):
        clusters = [[] for _ in range(len(centroids))]
        for i, x in enumerate(X):
            distances = [euclidean_distance(x, centroid) for centroid in centroids]
            if np.min(distances) <= self.max_distance:
                cluster_idx = np.argmin(distances)
                clusters[cluster_idx].append(i)
            else:
                centroids.append(x)
                clusters.append([i])
        return clusters
    
    def update_centroids(self, X, clusters):
        centroids = []
        for cluster in clusters:
            cluster_points = X[cluster]
            cluster_mean = np.mean(cluster_points, axis=0)
            centroids.append(cluster_mean)
        return centroids
    
    def predict(self, X):
        centroids = self.initialize_clusters(X)
        for _ in range(self.max_iters):
            clusters = self.assign_clusters(X, centroids)
            prev_centroids = centroids
            centroids = self.update_centroids(X, clusters)
#             print(centroids, prev_centroids)
            try:
                if np.all(prev_centroids == centroids):
                    break
            except:
                print(type(centroids), type(prev_centroids))
                return clusters, centroids
        return clusters, centroids