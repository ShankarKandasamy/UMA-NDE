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