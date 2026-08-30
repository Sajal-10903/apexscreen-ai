# Data Science Knowledge Base

## Statistics and Probability

### Descriptive Statistics

Measures of central tendency include mean (average), median (middle value), and mode (most frequent). Mean is sensitive to outliers; median is more robust. Standard deviation and variance measure data spread. Percentiles and quartiles describe data distribution. Interquartile range (IQR) is used for outlier detection.

### Probability Distributions

Normal distribution (Gaussian) is characterized by mean and standard deviation. The 68-95-99.7 rule describes data within 1, 2, and 3 standard deviations. Binomial distribution models the number of successes in n independent trials. Poisson distribution models the number of events in a fixed interval. Understanding distributions is crucial for choosing appropriate statistical tests and machine learning models.

### Hypothesis Testing

Hypothesis testing evaluates claims about populations using sample data. The null hypothesis (H0) assumes no effect or difference. The alternative hypothesis (H1) states the expected effect. P-value is the probability of observing results as extreme as the data under H0. Significance level (alpha, typically 0.05) is the threshold for rejecting H0. Type I error (false positive) is rejecting a true H0. Type II error (false negative) is failing to reject a false H0. Common tests include t-test, chi-square test, and ANOVA.

### Correlation and Causation

Pearson correlation measures linear relationship between two continuous variables (-1 to 1). Spearman correlation measures monotonic relationship (rank-based). Correlation does not imply causation. Confounding variables can create spurious correlations. Controlled experiments and causal inference methods (A/B testing, instrumental variables) establish causation.

### Bayesian Statistics

Bayes' theorem updates prior beliefs with observed evidence to produce posterior beliefs. Prior probability represents initial belief. Likelihood represents how well data fits a hypothesis. Posterior probability is the updated belief. Bayesian methods are useful when incorporating domain knowledge and handling uncertainty.

## Data Analysis

### Exploratory Data Analysis (EDA)

EDA examines data characteristics before modeling. Steps include examining data shape, types, and missing values. Summary statistics reveal distributions and outliers. Correlation matrices identify relationships between features. Data profiling tools (pandas-profiling, sweetviz) automate initial exploration.

### Data Cleaning

Data cleaning addresses quality issues. Handle missing values through deletion, imputation (mean, median, mode, KNN), or indicator variables. Detect and handle outliers using IQR, z-score, or domain knowledge. Standardize formats for dates, categories, and text. Remove duplicates and resolve inconsistencies. Document all cleaning decisions for reproducibility.

### Data Transformation

Feature scaling (standardization, normalization) ensures features have comparable ranges. Log transformation handles skewed distributions. Polynomial features capture non-linear relationships. One-hot encoding converts categorical variables. Target encoding uses the target variable to encode categories. Feature crosses create interaction features.

## Data Visualization

### Visualization Principles

Choose chart types based on data and purpose. Bar charts for categorical comparisons. Line charts for trends over time. Scatter plots for relationships between variables. Histograms for distributions. Box plots for distribution comparison. Heatmaps for correlation matrices. Use color purposefully and ensure accessibility.

### Python Visualization Libraries

Matplotlib provides low-level plotting control. Seaborn offers statistical visualizations with attractive defaults. Plotly creates interactive charts. Altair uses a declarative grammar of graphics. Folium creates interactive maps. Each library has strengths for different use cases.

## Machine Learning for Data Science

### Feature Selection

Filter methods (correlation, mutual information, chi-square) rank features independently of the model. Wrapper methods (recursive feature elimination, forward selection) use model performance to select features. Embedded methods (L1 regularization, tree-based importance) select features during training. Feature selection reduces overfitting, improves interpretability, and speeds up training.

### Model Interpretation

Feature importance shows how much each feature contributes to predictions. SHAP (SHapley Additive exPlanations) values provide consistent feature attribution based on game theory. LIME (Local Interpretable Model-agnostic Explanations) creates local linear approximations. Partial dependence plots show the marginal effect of features. Model interpretation is crucial for trust, debugging, and compliance.

### Ensemble Methods

Bagging trains models on random subsets and averages predictions (Random Forest). Boosting trains models sequentially, focusing on errors (XGBoost, LightGBM). Stacking uses one model's predictions as features for another. Ensembles typically outperform individual models by reducing variance (bagging) or bias (boosting).

## A/B Testing

### Experiment Design

A/B testing compares two variants (control and treatment) to measure the effect of a change. Random assignment ensures groups are comparable. Sample size calculation considers effect size, significance level, and statistical power. Run tests for sufficient duration to capture temporal patterns. Avoid peeking at results before the test is complete.

### Statistical Analysis of Experiments

Use appropriate statistical tests (t-test for continuous outcomes, chi-square for proportions). Calculate confidence intervals for the treatment effect. Consider multiple testing correction (Bonferroni, FDR) when testing multiple hypotheses. Bayesian A/B testing provides probability distributions of effect size. Practical significance may differ from statistical significance.

### Common Pitfalls

Simpson's paradox occurs when group-level trends reverse at aggregate level. Novelty effects cause temporary behavior changes. Selection bias from non-random assignment. Survivorship bias from analyzing only remaining subjects. Network effects when users interact with each other.

## SQL and Data Querying

### Advanced SQL

Window functions (ROW_NUMBER, RANK, LAG, LEAD, SUM OVER) perform calculations across rows related to the current row. CTEs (Common Table Expressions) improve query readability. Recursive CTEs handle hierarchical data. PIVOT and UNPIVOT reshape data. Analytical queries combine aggregation with row-level detail.

### Query Optimization

EXPLAIN ANALYZE shows query execution plan and actual timing. Index design matches query patterns. Avoid SELECT * in production queries. Use appropriate JOIN types. Minimize subqueries in favor of JOINs or CTEs. Partition large tables by date or other natural keys.

## Python for Data Science

### pandas

pandas DataFrames are the foundation of data manipulation in Python. Key operations include filtering, grouping, merging, pivoting, and applying functions. Method chaining creates readable transformation pipelines. Performance optimization includes using vectorized operations instead of loops, appropriate dtypes, and chunked reading for large files.

### numpy

numpy provides efficient multi-dimensional array operations. Broadcasting rules enable operations on arrays of different shapes. Linear algebra operations (matrix multiplication, eigenvalue decomposition, SVD) are fundamental. Random number generation for simulations and bootstrapping.

## Time Series Analysis

### Components

Time series data has trend (long-term direction), seasonality (periodic patterns), cyclical (non-fixed period patterns), and residual (random noise) components. Decomposition separates these components for analysis.

### Forecasting Methods

ARIMA (AutoRegressive Integrated Moving Average) models temporal dependencies. Seasonal ARIMA (SARIMA) handles seasonality. Exponential smoothing methods weight recent observations more heavily. Prophet (by Facebook) handles holidays and changepoints automatically. LSTM and transformer models capture complex temporal patterns.

### Stationarity

Stationarity means statistical properties (mean, variance) don't change over time. Many time series methods assume stationarity. The Augmented Dickey-Fuller test checks for stationarity. Differencing transforms non-stationary series to stationary.

## Data Pipelines

### ETL and ELT

ETL (Extract, Transform, Load) transforms data before loading into the target. ELT (Extract, Load, Transform) loads raw data first, then transforms in the target system. Modern data stacks favor ELT with tools like dbt for transformation. Apache Airflow orchestrates complex data workflows as directed acyclic graphs (DAGs).

### Data Quality

Data quality dimensions include accuracy, completeness, consistency, timeliness, and validity. Implement data validation checks at each pipeline stage. Great Expectations and dbt tests automate data quality checks. Data contracts define expectations between producers and consumers.
