# Frequency of Vertex Occurrence in Short Random Walks
10

## 103
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
# 102
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
Our goal is to learn a latent representation, not only a probability distribution of node co-occurrences, and so we introduce a mapping function \( \phi: V 	o \mathbb{R}^{l 	imes d} \). This mapping \( \phi \) represents the latent social representation associated with each vertex \( U \) in the graph. (In practice, we represent \( \phi \) by a \( |V| 	imes d \) matrix of free parameters, which will serve later on as our \( XE \).) The problem then, is to estimate the likelihood:

$$	ext{(1)}$$
However, as the walk length grows, computing this objective function becomes unfeasible. A recent relaxation in language modeling [26, 27] turns the prediction problem on its head. First, instead of using the context to predict a missing word, it uses one word to predict the context. Secondly, the context is composed of the words appearing to the right side of the given word as well as the left side. Finally, it removes the ordering constraint on the problem: Instead, the model is required to maximize the probability of any word appearing in the context without the knowledge of its offset from the given word:

In terms of vertex representation modeling, this yields the optimization problem:

$$	ext{minimize } \phi $$
$$ - \log Pr(t_i | (v_{i-1}, v_{i+1}, \ldots, v_{i+w})) | \phi(v_i) $$
We find these relaxations are particularly desirable for social representation learning: First, the order independence assumption better captures a sense of 'nearness' that is provided by random walks. Moreover, this relaxation is quite useful for speeding up the training time by building small models as one vertex is given at a time. Solving the optimization problem from Eq. (2) builds representations that capture the shared similarities in local graph structure between vertices. Vertices which have similar neighborhoods will acquire similar representations (encoding co-citation similarity), allowing generalization on machine learning tasks. By combining both truncated random walks and neural language models, we formulate a method which satisfies all.