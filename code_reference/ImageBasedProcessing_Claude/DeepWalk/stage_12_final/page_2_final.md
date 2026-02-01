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