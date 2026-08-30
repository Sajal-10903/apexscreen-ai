# Machine Learning and AI Engineering Knowledge Base

## Supervised Learning

Supervised learning is a type of machine learning where the model is trained on labeled data. The algorithm learns a mapping function from input features to output labels. The goal is to learn a general rule that maps inputs to outputs.

### Classification vs Regression

Classification problems involve predicting discrete labels (e.g., spam vs not spam), while regression problems involve predicting continuous values (e.g., house prices). Common classification algorithms include Logistic Regression, Decision Trees, Random Forests, Support Vector Machines, and Neural Networks. Common regression algorithms include Linear Regression, Polynomial Regression, Ridge Regression, and Lasso Regression.

### Logistic Regression

Logistic Regression is a classification algorithm that uses the sigmoid function to model the probability of a binary outcome. Despite its name, it is used for classification, not regression. The decision boundary is linear in the feature space. Logistic Regression is often used as a baseline model due to its simplicity and interpretability. It works well for linearly separable data and can be extended to multi-class classification using one-vs-rest or softmax approaches.

### Decision Trees and Random Forests

Decision Trees partition the feature space using a series of if-then rules. They are easy to interpret but prone to overfitting. Random Forests are an ensemble method that builds multiple decision trees and combines their predictions through majority voting (classification) or averaging (regression). This reduces overfitting and improves generalization. Feature importance can be derived from Random Forests by measuring how much each feature contributes to reducing impurity across all trees.

### Support Vector Machines (SVM)

SVMs find the hyperplane that maximizes the margin between classes. The kernel trick allows SVMs to handle non-linearly separable data by mapping features to a higher-dimensional space. Common kernels include linear, polynomial, and RBF (Radial Basis Function). SVMs are effective in high-dimensional spaces but can be computationally expensive for large datasets.

### Gradient Boosting

Gradient Boosting builds an ensemble of weak learners (typically decision trees) sequentially, where each new tree corrects the errors of the previous ones. XGBoost, LightGBM, and CatBoost are popular implementations that include regularization, handling of missing values, and efficient computation. These methods often achieve state-of-the-art results on tabular data.

## Unsupervised Learning

Unsupervised learning involves training on data without labels. The goal is to discover hidden patterns, groupings, or representations in the data.

### Clustering

K-Means clustering partitions data into K clusters by minimizing the within-cluster sum of squares. The algorithm iteratively assigns points to the nearest centroid and updates centroids. Choosing the optimal K can be done using the elbow method or silhouette score. DBSCAN is a density-based clustering algorithm that can find clusters of arbitrary shape and identify noise points. Hierarchical clustering builds a tree of clusters using agglomerative (bottom-up) or divisive (top-down) approaches.

### Dimensionality Reduction

PCA (Principal Component Analysis) finds orthogonal directions of maximum variance in the data. It projects data onto a lower-dimensional subspace while preserving as much variance as possible. t-SNE and UMAP are non-linear dimensionality reduction techniques used primarily for visualization. They preserve local structure in the data and are useful for exploring high-dimensional datasets.

## Model Evaluation

### Metrics for Classification

Accuracy is the ratio of correct predictions to total predictions. However, accuracy can be misleading for imbalanced datasets. Precision measures the ratio of true positives to all predicted positives. Recall (sensitivity) measures the ratio of true positives to all actual positives. F1-Score is the harmonic mean of precision and recall. AUC-ROC measures the ability of the model to distinguish between classes across all threshold values. Confusion matrix provides a detailed breakdown of true positives, true negatives, false positives, and false negatives.

### Cross-Validation

K-Fold Cross-Validation divides the dataset into K folds, trains on K-1 folds and validates on the remaining fold, rotating through all folds. This provides a more robust estimate of model performance than a single train-test split. Stratified K-Fold ensures each fold has the same proportion of classes as the full dataset.

### Bias-Variance Tradeoff

Bias refers to errors from overly simplistic assumptions in the model (underfitting). Variance refers to errors from sensitivity to small fluctuations in the training set (overfitting). The goal is to find the right balance. High bias models are too simple; high variance models are too complex. Regularization techniques (L1 Lasso, L2 Ridge) help control model complexity.

## Feature Engineering

Feature engineering is the process of creating, transforming, and selecting features to improve model performance. It is often the most impactful step in a machine learning pipeline.

### Common Techniques

Numerical features can be scaled using StandardScaler (zero mean, unit variance) or MinMaxScaler (range 0-1). Categorical features can be encoded using one-hot encoding, label encoding, or target encoding. Missing values can be handled through imputation (mean, median, mode, or model-based). Feature creation involves combining existing features (polynomial features, interactions) or extracting features from text, dates, or other complex data types.

### Text Feature Engineering

TF-IDF (Term Frequency-Inverse Document Frequency) converts text into numerical features by measuring word importance relative to a document corpus. Bag of Words counts word occurrences. Word embeddings (Word2Vec, GloVe, FastText) represent words as dense vectors capturing semantic meaning. These can be used as features for downstream models.

## Natural Language Processing

NLP is the field of AI dealing with the interaction between computers and human language. Key tasks include text classification, named entity recognition, sentiment analysis, machine translation, and question answering.

### Text Preprocessing

Tokenization splits text into words or subwords. Stemming reduces words to their root form. Lemmatization reduces words to their dictionary form. Stop word removal eliminates common words that don't carry much meaning. Regular expressions can be used for pattern-based text cleaning.

### Text Classification

Text classification assigns categories to text documents. Common approaches include TF-IDF with Logistic Regression, Naive Bayes, and deep learning models like CNNs and RNNs for text. Transfer learning with pre-trained models (BERT, RoBERTa) has become the standard approach for text classification tasks. Fine-tuning these models on domain-specific data typically yields the best results.

### Named Entity Recognition

NER identifies and classifies named entities (persons, organizations, locations, etc.) in text. Approaches include rule-based methods, CRF (Conditional Random Fields), and transformer-based models. SpaCy provides pre-trained NER models for common entity types.

### Sentiment Analysis

Sentiment analysis determines the emotional tone of text (positive, negative, neutral). It can be approached as a classification problem using bag-of-words features, LSTM networks, or fine-tuned transformer models. Aspect-based sentiment analysis goes further by identifying sentiment toward specific aspects of the text.

## Deep Learning

### Neural Network Fundamentals

Artificial neural networks consist of layers of interconnected neurons. Each connection has a weight that is learned during training. The forward pass computes the output, and backpropagation computes gradients for weight updates. Activation functions (ReLU, sigmoid, tanh, softmax) introduce non-linearity. Optimization algorithms (SGD, Adam, RMSprop) update weights to minimize the loss function. Dropout, batch normalization, and weight decay are regularization techniques to prevent overfitting.

### Convolutional Neural Networks (CNNs)

CNNs are designed for grid-like data (images, time series). Convolutional layers apply learnable filters that detect features like edges, textures, and patterns. Pooling layers reduce spatial dimensions. Common architectures include LeNet, AlexNet, VGG, ResNet, and EfficientNet. Transfer learning with pre-trained CNNs is a standard approach for computer vision tasks.

### Recurrent Neural Networks (RNNs) and LSTMs

RNNs process sequential data by maintaining a hidden state. They suffer from vanishing/exploding gradient problems for long sequences. LSTMs (Long Short-Term Memory) address this with a gating mechanism that controls information flow. GRUs (Gated Recurrent Units) are a simplified variant. These architectures are used for time series, text, and speech processing.

### Transformers

The Transformer architecture, introduced in "Attention is All You Need" (2017), uses self-attention mechanisms to process sequences in parallel. Multi-head attention allows the model to attend to different aspects of the input simultaneously. Positional encoding provides sequence order information. The encoder-decoder architecture is used for sequence-to-sequence tasks.

BERT (Bidirectional Encoder Representations from Transformers) pre-trains on masked language modeling and next sentence prediction. It can be fine-tuned for various NLP tasks. GPT (Generative Pre-trained Transformer) is a decoder-only model trained on next token prediction, excelling at text generation.

## Large Language Models (LLMs)

LLMs are large transformer-based models trained on massive text corpora. They exhibit emergent capabilities like in-context learning, chain-of-thought reasoning, and instruction following. Key models include GPT-4, Claude, Llama, and Gemini.

### Prompt Engineering

Effective prompting includes clear instructions, examples (few-shot learning), chain-of-thought prompting, and system prompts. Temperature controls randomness in generation. Output format specification (JSON, markdown) helps in structured output.

### Fine-tuning

Fine-tuning adapts a pre-trained LLM to specific tasks or domains. Full fine-tuning updates all parameters. LoRA (Low-Rank Adaptation) is a parameter-efficient fine-tuning method that adds small trainable matrices to attention layers, significantly reducing computational cost while maintaining performance.

## Retrieval-Augmented Generation (RAG)

RAG combines retrieval systems with generative models. Documents are chunked, embedded, and stored in a vector database. At query time, relevant chunks are retrieved using similarity search and provided as context to the LLM. This grounds the generation in factual content and reduces hallucination.

### Chunking Strategies

Document chunking must balance between preserving context and maintaining manageable chunk sizes. Strategies include fixed-size chunking, sentence-based chunking, paragraph-based chunking, and semantic chunking. Overlap between chunks helps maintain context across boundaries.

### Embedding Models

Embedding models convert text into dense vector representations. Sentence-transformers (like all-MiniLM-L6-v2) provide efficient sentence-level embeddings. These embeddings capture semantic meaning, enabling similarity-based retrieval. The choice of embedding model affects retrieval quality.

### Vector Databases

Vector databases (ChromaDB, Pinecone, Weaviate, Qdrant, Milvus) store and index embedding vectors for efficient similarity search. They support approximate nearest neighbor search algorithms (HNSW, IVF) that trade some accuracy for speed. Metadata filtering allows combining semantic search with structured queries.

## Model Deployment

### MLOps

MLOps applies DevOps principles to machine learning. It includes version control for models and data, automated training pipelines, continuous integration/deployment for models, monitoring model performance in production, and data drift detection. Tools include MLflow for experiment tracking, DVC for data versioning, and Kubeflow for ML pipelines.

### Model Serving

Models can be served via REST APIs (FastAPI, Flask), gRPC, or dedicated serving platforms (TensorFlow Serving, Triton Inference Server). Containerization with Docker ensures reproducibility. Batch inference processes data in bulk, while online inference handles real-time requests. Model optimization techniques include quantization, pruning, and distillation.

### Monitoring and Maintenance

Production models require monitoring for data drift (change in input distribution), concept drift (change in the relationship between inputs and outputs), and performance degradation. Automated retraining pipelines trigger when performance drops below thresholds. A/B testing compares model versions in production.
