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