import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

import pygeohash as geohash


BRIGHTNESS_CLUSTERS = ['Moderate', 'High', 'Extreme']


def get_geo_clusters(dataset, min_samples, eps, n_jobs=-1,
                     filter_non_clusterized=True):
    fire_spots = dataset[['latitude', 'longitude']]
    model = DBSCAN(min_samples=min_samples, eps=eps, n_jobs=n_jobs)
    model.fit(fire_spots)
    fire_spots['cluster'] = model.labels_

    if filter_non_clusterized:
        fire_spots = fire_spots[fire_spots.cluster != -1]

    cluster_size_df = fire_spots.cluster.value_counts().reset_index()
    cluster_size_df.columns = ['cluster', 'n_reports']
    fire_spots = pd.merge(fire_spots, cluster_size_df, how='left', on='cluster')
    fire_spots = _add_color_column(fire_spots)

    return fire_spots


def _add_color_column(fire_spots):
    n_colors = fire_spots.n_reports.unique().shape[0]

    colors = MinMaxScaler().fit_transform(np.arange(n_colors).astype(float).reshape(-1, 1))
    colors = (colors - 1.0) * (-1.0)
    colors = np.hstack([colors, np.zeros(n_colors).reshape(-1, 1), colors])
    colors_df = pd.DataFrame(colors)

    colors = []
    for _, row in colors_df.iterrows():
        rgb_color = tuple((row.values * 255).astype(int))
        colors.append('#%02x%02x%02x' % rgb_color)

    cluster_freqs = list(fire_spots.groupby(['n_reports']).groups.keys())
    cluster_freqs = pd.DataFrame(sorted(cluster_freqs), columns=['n_reports'])

    colors_df = pd.DataFrame(colors, columns=['color'])
    cluster_colors = pd.concat([cluster_freqs, colors_df], axis=1)

    return pd.merge(fire_spots, cluster_colors, on='n_reports')


def get_brightness_clusters(dataset, clusters_names=BRIGHTNESS_CLUSTERS,
                            n_jobs=-1, random_state=2018):
    n_clusters = len(clusters_names)
    spots_brightness = dataset[['bright_ti4', 'bright_ti5']]

    model = KMeans(n_clusters=n_clusters, n_jobs=n_jobs,
                   random_state=random_state)
    model.fit(spots_brightness)

    spots_brightness['cluster'] = model.labels_
    spots_brightness = _map_id_to_intensity(spots_brightness, model.cluster_centers_,
                                            clusters_names)

    dataset = dataset[['latitude', 'longitude']]
    dataset['cluster'] = spots_brightness['cluster']
    
    return dataset


def _map_id_to_intensity(spots_brightness, centroids, clusters_names):
    centroids_intensity = [
        (cluster_id, np.linalg.norm(centroid - 0))
        for cluster_id, centroid in enumerate(centroids)
    ]
    clusters_sorted = sorted(centroids_intensity, key=lambda x: x[1])

    cluster_intensity_map = {
        centroid[0]: clusters_names[intensity]
        for intensity, centroid in enumerate(clusters_sorted)
    }

    cluster_mapper = lambda id_: cluster_intensity_map[id_]
    spots_brightness['cluster'] = spots_brightness.cluster.apply(cluster_mapper)

    return spots_brightness
