<!-- PAGE 1 -->

# DeepWalk: Online Learning of Social Representations

Bryan Perozzi  
Stony Brook University  
Department of Computer Science  

Rami Al-Rfou  
Stony Brook University  
Department of Computer Science  

Steven Skiena  
Stony Brook University  
Department of Computer Science  

{bperozzi, ralrfou, skiena}@cs.stonybrook.edu  

## ABSTRACT
We present DEEPWALK, a novel approach for learning latent representations of vertices in a network. These latent representations encode social relations in a continuous vector space, which is easily exploited by statistical models. DEEPWALK generalizes recent advancements in language modeling and unsupervised feature learning (or deep learning) from sequences of words to graphs: DEEPWALK uses local information obtained from truncated random walks to learn latent representations by treating walks as the equivalent of sentences. We demonstrate DEEPWALK's latent representations on several multi-label network classification tasks for social networks such as BlogCatalog, Flickr, and YouTube. Our results show that DEEPWALK outperforms challenging baselines which are allowed a global view of the network, especially in the presence of missing information. DEEPWALK's representations can provide significant improvements when labeled data is sparse. In some experiments, DEEPWALK's representations are able to outperform all baseline methods while using 60% less training data.

DEEPWALK is also scalable. It is an online learning algorithm which builds useful incremental results; and is trivially parallelizable. These qualities make it suitable for broad a class of real world applications such as network classification, and anomaly detection:

## Categories and Subject Descriptors
H.2.8 [Database Management]: Database Applications; Data Mining; I.2.6 [Artificial Intelligence]: Learning; I.5.1 [Pattern Recognition]: Model - Statistical

## 1. INTRODUCTION
The sparsity of a network representation is both a strength and a weakness. Sparsity enables the design of efficient discrete algorithms, but can make it harder to generalize in statistical learning. Machine learning applications in networks (such as network classification [15,37], content recommendation [11], anomaly detection [5], and missing link prediction [22]) must be able to deal with this sparsity in order to survive.

In this paper we introduce deep learning (unsupervised feature learning) techniques, which have proven successful in natural language processing, into network analysis for the first time. We develop an algorithm (DEEPWALK) that learns social representations of a graph's vertices by modeling a stream of short random walks. Social representations are latent features of the vertices that capture neighborhood similarity and community membership. These latent representations encode social relations in a continuous vector space with a relatively small number of dimensions. DEEPWALK generalizes neural language models to process a special language composed of a set of randomly-generated walks. These neural language models have been used to capture the semantic and syntactic structure of human language and even logical analogies.

DEEPWALK takes a graph as input and produces a latent representation as an output. The result of applying our method to the well-studied Karate network is shown in Figure 1. The graph, as typically presented by force-directed layouts, is shown in Figure 1a. Figure 1b shows the output of our method with 2 latent dimensions. Beyond the striking similarity, we note that linearly separable portions of (1b) correspond to clusters found through modularity maximization in the input graph (1a) (shown as vertex colors).

> Figure 1: Our proposed method learns a latent space representation of social interactions in R². The learned representation encodes community structure so it can be easily exploited by standard classification methods. Here, our method is used on Zachary's Karate network [44] to generate a latent representation in R². Note the correspondence between community structure in the input graph and the embedding: Vertex colors represent a modularity-based clustering of the input graph.

0.5
1.0

The authors, 2014. This is the author's draft of the work: It is posted here for your personal use. Not for redistribution: The definitive version was published in KDD' 14, http://dx.doi.org/10.1145/2623330_2623732


<!-- PAGE 2 -->

narios, we evaluate its performance on challenging multi-label network classification problems in large heterogeneous graphs. In the relational classification problem, the links between feature vectors violate the traditional i.i.d. assumption. Techniques to address this problem typically use approximate inference techniques [31, 35] to leverage the dependency information to improve classification results. We distance ourselves from these approaches by learning label-independent representations of the graph: Our representation quality is not influenced by the choice of labeled vertices, so they can be shared among tasks. **DEEP WALK** outperforms other latent representation methods for creating social dimensions [39,41], especially when labeled nodes are scarce. Strong performance with our representations is possible with very simple linear classifiers (e.g: logistic regression). Our representations are general, and can be combined with any classification method (including iterative inference methods). DEEPWALK achieves all of that while being an online algorithm that is trivially parallelizable.

Our contributions are as follows:

- We introduce deep learning as a tool to analyze graphs, to build robust representations that are suitable for statistical modeling: DEEPWALK learns structural regularities present within short random walks.
- We extensively evaluate our representations on multi-label classification tasks on several social networks. We show significantly increased classification performance in the presence of label sparsity, getting improvements of 5%-10% of Micro F1, on the sparsest problems we consider. DEEPWALK outperforms its competitors even when given 60% less training data.

We demonstrate the scalability of our algorithm by building representations of web-scale graphs, (such as YouTube) using a parallel implementation. Moreover, we describe the minimal changes necessary to build a streaming version of our approach.

The rest of the paper is arranged as follows. In Sections 2 and 3, we discuss the problem formulation of classification in data networks, and how it relates to our work. In Section 4 we present DEEPWALK, our approach for Social Representation Learning. We outline our experiments in Section 5, and present their results in Section 6. We close with a discussion of related work in Section 7, and our conclusions.

## 2. PROBLEM DEFINITION

We consider the problem of classifying members of a social network into one or more categories. More formally, let G = (V,E), where V are the members of the network; and E be its edges, E = (V x V). Given partially labeled social network G_L = (V, E, X, Y), with attributes X ∈ R^{|V| x s} where s is the size of the feature space for each attribute vector; and Y ∈ R^{|V| x |X|} is the set of labels. In a traditional machine learning classification setting, we aim to learn a hypothesis H that maps elements of X to the labels set Y. In our case, we can utilize the significant information about the dependence of the examples embedded in the structure of G to achieve superior performance.

In the literature, this is known as the relational classification (or the collective classification problem [37]). Traditional approaches to relational classification pose the problem as an inference in an undirected Markov network, and then use iterative approximate inference algorithms (such as the iterative classification algorithm [31], Gibbs Sampling [14], or label relaxation [18]) to compute the posterior distribution of labels given the network structure.

We propose a different approach to capture the network topology information. Instead of mixing the label space as part of the feature space, we propose an unsupervised method which learns features that capture the graph structure independent of the labels' distribution. This separation between the structural representation and the labeling task avoids cascading errors, which can occur in iterative methods [33]. Moreover, the same representation can be used for multiple classification problems concerning that network.

Our goal is to learn X_E ∈ R^{|V| x d} where d is a small number of latent dimensions. These low-dimensional representations are distributed; meaning each social phenomenon is expressed by a subset of the dimensions and each dimension contributes to a subset of the social concepts expressed by the space.

Using these structural features, we will augment the attributes space to help the classification decision. These features are general, and can be used with any classification algorithm (including iterative methods). However, we believe that the greatest utility of these features is their easy integration with simple machine learning algorithms. They scale appropriately in real-world networks, as we will show in Section 6.

## 3. LEARNING SOCIAL REPRESENTATIONS

We seek learning social representations with the following characteristics:

- **Adaptability**: Real social networks are constantly evolving; new social relations should not require repeating the learning process all over again.
- **Community aware**: The distance between latent dimensions should represent a metric for evaluating social similarity between the corresponding members of the network. This allows generalization in networks with homophily.
- **Low dimensional**: When labeled data is scarce, low-dimensional models generalize better, and speed up convergence and inference.
- **Continuous**: We require latent representations to model partial community membership in continuous space. In addition to providing a nuanced view of community membership, a continuous representation has smooth decision boundaries between communities which allows more robust classification.

Our method for satisfying these requirements learns representation for vertices from a stream of short random walks, using optimization techniques originally designed for language modeling. Here, we review the basics of both random walks and language modeling, and describe how their combination satisfies our requirements.


<!-- PAGE 3 -->

Frequency of Vertex Occurrence in Short Random Walks
10

## 3.1 103
"5 102 #
101
109
109

### 101

### Vertex visitation count
102 103 10"
(a) YouTube Social Graph

### 105

### 106
#### Frequency of Word Occurrence in Wikipedia
105
10'
1 103
102
101
109
109 101 102 103 10' 105 106 107
Word mention count
(b) Wikipedia Article Text

## Figure 2: The power-law distribution of vertices appearing in short random walks (2a) follows power-law, much like the distribution of words in natural language (2b).

### 3.1 Random Walks
We denote a random walk rooted at vertex \( U_i \) as \( W_{v_i} \). It is a stochastic process with random variables \( W_1, W_2, \ldots, W_k \) such that \( W_k \) is a vertex chosen at random from the neighbors of vertex \( U_k \). Random walks have been used as a similarity measure for a variety of problems in content recommendation [11] and community detection [1]. They are also the foundation of a class of output sensitive algorithms which use them to compute local community structure information in time sublinear to the size of the input graph [38]. It is this connection to local structure that motivates us to use a stream of short random walks as our basic tool for extracting information from a network. In addition to capturing community information, using random walks as the basis for our algorithm gives us two other desirable properties. First, local exploration is easy to parallelize: Several random walkers (in different threads, processes, or machines) can simultaneously explore different parts of the same graph. Secondly, relying on information obtained from short random walks makes it possible to accommodate small changes in the graph structure without the need for global recomputation. We can iteratively update the learned model with new random walks from the changed region in time sub-linear to the entire graph.

### 3.2 Connection: Power laws
Having chosen online random walks as our primitive for capturing graph structure, we now need a suitable method to capture this information: If the degree distribution of a connected graph follows a power law (is scale-free), we observe that the frequency with which vertices appear in the short random walks will also follow a power-law distribution. Word frequency in natural language follows a similar distribution, and techniques from language modeling account for this distributional behavior. To emphasize this similarity we show two different power-law distributions in Figure 2. The first comes from a series of short random walks on a scale-free graph, and the second comes from the text of 100,000 articles from the English Wikipedia. A core contribution of our work is the idea that techniques which have been used to model natural language (where the symbol frequency follows a power law distribution (or Zipf's law)) can be repurposed to model community structure in networks. We spend the rest of this section reviewing the growing work in language modeling, and transforming it to learn representations of vertices which satisfy our criteria.

### 3.3 Language Modeling
The goal of language modeling is to estimate the likelihood of a specific sequence of words appearing in a corpus. More formally, given a sequence of words

$$ W_n = (w_0, w_1, \ldots, w_n) $$
where \( w_i \in V \) (V is the vocabulary), we would like to maximize the \( Pr(w_n | w_0, U_1, \ldots, w_{n-1}) \) over all the training corpus.

Recent work in representation learning has focused on using probabilistic neural networks to build general representations of words which extend the scope of language modeling beyond its original goals. In this work, we present a generalization of language modeling to explore the graph through a stream of short random walks. These walks can be thought of as short sentences and phrases in a special language. The direct analog is to estimate the likelihood of observing vertex \( U_i \) given all the previous vertices visited so far in the random walk.

$$ Pr(w_n | (v_1, v_2, \ldots, v_{n-1})) $$
Our goal is to learn a latent representation, not only a probability distribution of node co-occurrences, and so we introduce a mapping function \( \phi: V \to \mathbb{R}^{l \times d} \). This mapping \( \phi \) represents the latent social representation associated with each vertex \( U \) in the graph. (In practice, we represent \( \phi \) by a \( |V| \times d \) matrix of free parameters, which will serve later on as our \( XE \).) The problem then, is to estimate the likelihood:

$$ \text{(1)} $$
However, as the walk length grows, computing this objective function becomes unfeasible. A recent relaxation in language modeling [26, 27] turns the prediction problem on its head. First, instead of using the context to predict a missing word, it uses one word to predict the context. Secondly, the context is composed of the words appearing to the right side of the given word as well as the left side. Finally, it removes the ordering constraint on the problem: Instead, the model is required to maximize the probability of any word appearing in the context without the knowledge of its offset from the given word:

In terms of vertex representation modeling, this yields the optimization problem:

$$ \text{minimize } \phi $$
$$ - \log Pr(t_i | (v_{i-1}, v_{i+1}, \ldots, v_{i+w})) | \phi(v_i) $$
We find these relaxations are particularly desirable for social representation learning: First, the order independence assumption better captures a sense of 'nearness' that is provided by random walks. Moreover, this relaxation is quite useful for speeding up the training time by building small models as one vertex is given at a time. Solving the optimization problem from Eq. (2) builds representations that capture the shared similarities in local graph structure between vertices. Vertices which have similar neighborhoods will acquire similar representations (encoding co-citation similarity), allowing generalization on machine learning tasks. By combining both truncated random walks and neural language models, we formulate a method which satisfies all.


<!-- PAGE 4 -->

Algorithm 1 DEEPWALK(G, d, γ, t)

**Input:** graph G(V, E)  
**window size** W  
**embedding size** d  
**walks per vertex** γ  
**walk length** t  

**Output:** matrix of vertex representations Φ ∈ ℝ|V|×d  
1: Initialization: Sample Φ from U|V|×d  
2: Build a binary Tree T from V  
3: for i = 0 to γ do  
4:  0 = Shuffle(Φ)  
5: for each v_i ∈ V do  
6:  W_vi = RandomWalk(G, v_i, t)  
7:  SkipGram(Φ, W_vi, w)  
8: end for  
9: end for  

---

of our desired properties. This method generates representations of social networks that are low-dimensional; and exist in a continuous vector space. Its representations encode latent forms of community membership, and because the method outputs useful intermediate representations, it can adapt to changing network topology:

## 4 METHOD  
In this section we discuss the main components of our algorithm. We also present several variants of our approach and discuss their merits.

### 4.1 Overview  
As in any language modeling algorithm, the only required input is a corpus and a vocabulary V. DEEPWALK considers a set of short truncated random walks its own corpus, and the graph vertices as its own vocabulary. It is beneficial to know the V and the frequency distribution of vertices in the random walks ahead of the training; it is not necessary for the algorithm to work as we will show in 4.2.2.

### 4.2 Algorithm: DEEPWALK  
The algorithm consists of two main components; first a random walk generator and second an update procedure. The random walk generator takes a graph G and samples uniformly random a vertex U_i as the root of the random walk W_vi. A walk samples uniformly from the neighbors of the last vertex visited until the maximum length (t) is reached. While we set the length of our random walks in the experiments to be fixed, there is no restriction for the random walks to be of the same length: These walks could have restarts (i.e. a teleport probability of returning back to their root), but our preliminary results did not show any advantage of using restarts: In practice, our implementation specifies a number of random walks Y of length t to start at each vertex. Lines 3-9 in Algorithm 1 shows the core of our approach: The outer loop specifies the number of times, Y, which we should start random walks at each vertex. We think of each iteration making a pass over the data and sample one walk per node during this pass. At the start of each pass we generate a random ordering to traverse the vertices. This is not strictly required, but is well-known to speed up the convergence of stochastic gradient descent.

### Algorithm 2 SkipGram(Φ, W_vi, w)  
1: for each v_j ∈ W_vi do  
2: for each U_k ∈ W_vi[j - w : j + w] do  
3:  J(Φ) = - log Pr(U_k | Φ(v_j))  
4:  Φ = Φ - α * ∂J(Φ)  
5: end for  
6: end for  

In the inner loop, we iterate over all the vertices of the graph. For each vertex v_i, we generate a random walk W_vi = t, and then use it to update our representations (Line 7). We use the SkipGram algorithm [26] to update these representations in accordance with our objective function in Eq. 2.

#### 4.2.1 SkipGram  
SkipGram is a language model that maximizes the co-occurrence probability among the words that appear within a window, W, in a sentence [26]. Algorithm 2 iterates over all possible collocations in random walk that appear within the window w (lines 1-2). For each, we map each vertex U_j to its current representation vector Φ(U_j) ∈ ℝ^d (See Figure 3b). Given the representation of U_j, we would like to maximize the probability of its neighbors in the walk (line 3). We can learn such posterior distribution using several choices of classifiers. For example, modeling the previous problem using logistic regression would result in a huge number of labels that is equal to |V| which could be in millions or billions. Such models require large amount of computational resources that could span a whole cluster of computers [3]. To speed the training time; Hierarchical Softmax [29,30] can be used to approximate the probability distribution.

#### 4.2.2 Hierarchical Softmax  
Given that U_k ∈ V, calculating Pr(U_k | Φ(v_i)) in line 3 is not feasible: Computing the partition function (normalization factor) is expensive. If we assign the vertices to the leaves of a binary tree, the prediction problem turns into maximizing the probability of a specific path in the tree (See Figure 3c). If the path to vertex U_k is identified by a sequence of tree nodes (b_0, b_1, ..., b_l, U_k), then

Pr(U_k | Φ(v_i)) = ∏_{i=1}^{l} Pr(b_i | Φ(v_i))

Now, Pr(b_i | Φ(v_i)) could be modeled by a binary classifier that is assigned to the parent of the node b_i. This reduces the computational complexity of calculating Pr(U_k | Φ(v_i)) from O(|V|) to O(log|V|): We can speed up the training process further, by assigning shorter paths to the frequent vertices in the random walks. Huffman coding is used to reduce the access time of frequent elements in the tree.

#### 4.2.3 Optimization  
The model parameter set is {d, T} where the size of each is O(d|V|): Stochastic gradient descent (SGD) [4] is used to optimize these parameters (Line 4, Algorithm 2). The derivatives are estimated using the back-propagation algorithm. The learning rate α for SGD is initially set to 2.5% at the beginning of the training and then decreased linearly.

> Shuffle(V)  
> W_vi = RandomWalk(G, V_i, t)  
> SkipGram(d, W_vi, w)

2 b[log |V|] , (b_0

[log |V|]


<!-- PAGE 5 -->

# 4.3 Parallelizability

As shown in Figure 2 the frequency distribution of vertices in random walks of social network and words in a language both follow a power law. This results in a long tail of infrequent vertices; therefore, the updates that affect $ will be sparse in nature. This allows us to use asynchronous version of stochastic gradient descent (ASGD), in the multi-worker case. Given that our updates are sparse and we do not acquire a lock to access the model shared parameters, ASGD will achieve an optimal rate of convergence [36]. While we run experiments on one machine using multiple threads, it has been demonstrated that this technique is highly scalable, and can be used in very large scale machine learning [8]. Figure 4 presents the effects of parallelizing DEEPWALK. It shows the speed up in processing BLOGCATALOG and FLICKR networks is consistent as we increase the number of workers to 8 (Figure 4a). It also shows that there is no loss of predictive performance relative to the running DEEPWALK serially (Figure 4b).

## 4.4 Algorithm Variants
Here we discuss some variants of our proposed method, which we believe may be of interest.

### 4.4.1 Streaming
One interesting variant of this method is a streaming approach, which could be implemented without knowledge of the entire graph. In this variant small walks from the graph are passed directly to the representation learning code, and the model is updated directly: Some modifications to the learning process will also be necessary: First, using a decaying learning rate will no longer be possible. Instead, we can initialize the learning rate to a small constant value. This will take longer to learn; but may be worth it in some applications. Second, we cannot necessarily build a tree of parameters any more. If the cardinality of V is known (or can be bounded), we can build the Hierarchical Softmax tree for that maximum value. Vertices can be assigned to one of the remaining leaves when they are first seen. If we have the ability to estimate the vertex frequency a priori, we can also still use Huffman coding to decrease frequent element access times.

### 4.4.2 Non-random walks
Some graphs are created as a by-product of agents interacting with a sequence of elements (e.g., users' navigation of pages on a website). When a graph is created by such a stream of non-random walks, we can use this process to feed the modeling phase directly: Graphs sampled in this way will not only capture information related to network structure, but also to the frequency at which paths are traversed. In our view this variant also encompasses language modeling: Sentences can be viewed as purposed walks through an appropriately designed language network, and language models like SkipGram are designed to capture this behavior. This approach can be combined with the streaming variant (Section 4.4.1) to train features on continually evolving network without ever explicitly constructing the entire graph. Maintaining representations with this technique could enable web-scale classification without the hassles of dealing with a web-scale graph.

# 5. EXPERIMENTAL DESIGN
In this section we provide an overview of the datasets and methods which we will use in our experiments. Code and data to reproduce our results will be available at the first author's website.

## 5.1 Datasets

(a) Random walk generation:

(b) Representation mapping:

(c) Hierarchical Softmax:

Figure 3: Overview of DEEPWALK. We slide a window of length 2w + 1 over the random walk Wv4, mapping the central vertex v1 to its representation $(v1). Hierarchical Softmax factors out Pr(v3 | (v1)) and Pr(v5 | (v1)) over sequences of probability distributions corresponding to the paths starting at the root and ending at v3 and vs. The representation Φ is updated to maximize the probability of v1 co-occurring with its context {v3, v5}.

Figure 4: Effects of parallelizing DEEPWALK.


<!-- PAGE 6 -->

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


