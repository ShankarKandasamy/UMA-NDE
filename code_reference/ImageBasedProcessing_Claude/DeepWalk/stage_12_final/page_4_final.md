# Algorithm 1 DEEPWALK(G, d, γ, t)

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