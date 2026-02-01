# 5. EXPERIMENTAL DESIGN

In this section we provide an overview of the datasets and methods which we will use in our experiments. Code and data to reproduce our results will be available at the first author's website.

## 5.1 Datasets

| Name       | BLOGCATALOG | FLICKR     | YouTUBE    |
|------------|--------------|------------|-------------|
| |V|        | 10,312       | 80,513     | 1,138,499   |
| |E|        | 333,983      | 5,899,882  | 2,990,443   |
| |D|        | 39           | 195        | 47          |
| Labels     | 1,138,499    | 47         |             |

> Table 1: Graphs used in our experiments.

An overview of the graphs we consider in our experiments is given in Figure 1.

- **BLOGCATALOG** [39] is a network of social relationships provided by blogger authors. The labels represent the topic categories provided by the authors.
- **FLICKR** [39] is a network of the contacts between users of the photo sharing website. The labels represent the interest groups of the users such as 'black and white photos'.
- **YouTUBE** [40] is a social network between users of the popular video sharing website. The labels here represent groups of viewers that enjoy common video genres (e.g: anime and wrestling).

## 5.2 Baseline Methods

To validate the performance of our approach we compare it against a number of baselines:

- **SpectralClustering** [41]: This method generates a representation in ℝ^d from the d-smallest eigenvectors of L; the normalized graph Laplacian of G. Utilizing the eigenvectors of L will be useful for classification.
- **Modularity** [39]: This method generates a representation in ℝ^d from the top-d eigenvectors of B, the Modularity matrix of G. The eigenvectors of B encode information about modular graph partitions of G [34]. Using them as features assumes that modular graph partitions will be useful for classification.
- **EdgeCluster** [40]: This method uses k-means clustering to cluster the adjacency matrix of G. It has been shown to perform comparably to the Modularity method, with the added advantage of scaling to graphs which are too large for spectral decomposition.
- **wvRN** [24]: The weighted-vote Relational Neighbor is a relational classifier. Given the neighborhood N_i of vertex U_i, wvRN estimates Pr(y_i|N_i) with the (appropriately normalized) weighted mean of its neighbors (i.e Pr(y_i|N_i) = 1/|N_i| ∑_{j∈N_i} w_j Pr(y_j|N_j)). It has shown surprisingly good performance in real networks, and has been advocated as a sensible relational classification baseline [25].
- **Majority**: This naive method simply chooses the most frequent labels in the training set.

## 6. EXPERIMENTS

In this section we present an experimental analysis of our method. We thoroughly evaluate it on a number of multi-label classification tasks, and analyze its sensitivity across several parameters.

### 6.1 Multi-Label Classification

To facilitate the comparison between our method and the relevant baselines, we use the exact same datasets and experimental procedure as in [39,40]. Specifically, we randomly sample a portion (TR) of the labeled nodes, and use them as training data. The rest of the nodes are used as test. We repeat this process 10 times; and report the average performance in terms of both Macro-F1 and Micro-F1. When possible we report the original results [39,40] here directly:

For all models we use a one-vs-rest logistic regression implemented by LibLinear [10] for classification. We present results for DEEPWALK with (γ = 80, W = 10, d = 128). The results for (SpectralClustering, Modularity, EdgeCluster) use Tang and Liu's preferred dimensionality; d = 500.

#### 6.1.1 BlogCatalog

In this experiment we increase the training ratio (TR) on the BLOGCATALOG network from 10% to 90%. Our results are presented in Table 2. Numbers in bold represent the highest performance in each column. DEEPWALK performs consistently better than EdgeCluster, Modularity, and wvRN. In fact, when trained with only 20% of the nodes labeled, DEEPWALK performs better than these approaches when they are given 90% of the data. The performance of SpectralClustering proves much more competitive, but DEEPWALK still outperforms when labeled data is sparse on both Macro-F1 (TR < 20%) and Micro-F1 (TR < 60%). This strong performance when only small fractions of the graph are labeled is a core strength of our approach: In the following experiments, we investigate the performance of our representations on even more sparsely labeled graphs.

#### 6.1.2 Flickr

In this experiment we vary the training ratio (TR) on the FLICKR network from 1% to 10%. This corresponds to having approximately 800 to 8,000 nodes labeled for classification in the entire network. Table 3 presents our results which are consistent with the previous experiment. DEEPWALK outperforms all baselines by at least 3% with respect to Micro-F1. Additionally, its Micro-F1 performance when only 3% of the graph is labeled beats all other methods even when they have been given 10% of the data: In other words, DEEPWALK can outperform the baselines with 60% less training data. It also performs quite well in Macro-F1, initially performing close to SpectralClustering, but distancing itself to a 1% improvement.

#### 6.1.3 YouTube

The YouTube network is considerably larger than the previous ones we have experimented on, and its size prevents two of our baseline methods (SpectralClustering and Modularity) from running on it. It is much closer to a real world graph than those we have previously considered: The results of varying the training ratio (TR) from 1% to 10% are presented in Table 4. They show that DEEPWALK significantly outperforms the scalable baseline for creating graph representations, EdgeCluster. When 1% of the labeled nodes are used for test, the Micro-F1 improves by 14%. The Macro-F1 shows corresponding 10% increase. This lead narrows as the training data increases, but DEEPWALK ends with a 3% lead in Micro-F1, and an impressive 5% improvement in Macro-F1.

> This experiment showcases the performance benefits that 1 O T71: 1

