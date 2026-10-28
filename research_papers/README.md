# Foundational Research Papers Repository

This folder contains the complete academic papers from which all mathematical models, algorithms, and ranking formulas in **SmartBasket Neo** are derived. Each PDF is named after its corresponding system feature.

---

## Index of Research Papers

| # | Feature / File Name | Paper Title | Authors & Venue | Implemented In |
|---|---|---|---|---|
| **1** | [`Neural_Collaborative_Filtering_NCF.pdf`](./Neural_Collaborative_Filtering_NCF.pdf) | *Neural Collaborative Filtering* | Xiangnan He et al. (**ACM WWW 2017**) | `ml/recommendation/collaborative.py` |
| **2** | [`Matrix_Factorization_SVD.pdf`](./Matrix_Factorization_SVD.pdf) | *Matrix Factorization Techniques for Recommender Systems* | Yehuda Koren, Robert Bell, Chris Volinsky (**IEEE Computer 2009**) | `ml/recommendation/collaborative.py`, `backend/ml/engine.py` |
| **3** | [`Content_Based_TF_IDF_Vector_Space.pdf`](./Content_Based_TF_IDF_Vector_Space.pdf) | *A Vector Space Model for Automatic Indexing* | Gerard Salton, Anita Wong, Chung-Shu Yang (**CACM 1975**) | `ml/recommendation/content_based.py`, `backend/ml/engine.py` |
| **4** | [`CatBoost_Categorical_Gradient_Boosting.pdf`](./CatBoost_Categorical_Gradient_Boosting.pdf) | *CatBoost: Unbiased Boosting with Categorical Features* | Liudmila Prokhorenkova et al. (**NeurIPS 2018**) | `ml/forecasting/sales_forecaster.py`, `ml/churn/churn_predictor.py` |
| **5** | [`Contextual_Bandits_LinUCB.pdf`](./Contextual_Bandits_LinUCB.pdf) | *A Contextual-Bandit Approach to Personalized Recommendation* | Lihong Li, Wei Chu, John Langford, Robert E. Schapire (**ACM WWW 2010**) | `backend/ml/engine.py` (Curiosity Slot) |
| **6** | [`Maximal_Marginal_Relevance_MMR.pdf`](./Maximal_Marginal_Relevance_MMR.pdf) | *The Use of MMR, Diversity-Based Reranking for Reordering Documents and Producing Summaries* | Jaime Carbonell, Jade Goldstein (**ACM SIGIR 1998**) | `backend/ml/engine.py` (Diversity Re-ranking) |
| **7** | [`Two_Stage_Recommendation_Funnel_YouTube.pdf`](./Two_Stage_Recommendation_Funnel_YouTube.pdf) | *Deep Neural Networks for YouTube Recommendations* | Paul Covington, Jay Adams, Emre Sargin (**ACM RecSys 2016**) | Overall Funnel (Retrieval $\to$ Precision Scoring $\to$ Top-N) |

---

## Summary of Core Formulas Derived from These Papers

1. **TF-IDF & Cosine Similarity (`Content_Based_TF_IDF_Vector_Space.pdf`):**
   $$\text{TF-IDF}(t, d) = \text{TF}(t, d) \cdot \left[\ln\left(\frac{1 + N}{1 + \text{DF}(t)}\right) + 1\right], \quad \text{Sim}(A, B) = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\| + \epsilon}$$

2. **Matrix Factorization (`Matrix_Factorization_SVD.pdf`):**
   $$\hat{R} = U \Sigma V^T \approx U_k \Sigma_k V_k^T$$

3. **Neural Collaborative Filtering (`Neural_Collaborative_Filtering_NCF.pdf`):**
   $$\hat{y}_{ui} = \sigma\left(\mathbf{h}^T \text{MLP}([\mathbf{p}_u; \mathbf{q}_i])\right), \quad \text{Protocol: Leave-One-Out + 99 Distractors}$$

4. **Maximal Marginal Relevance (`Maximal_Marginal_Relevance_MMR.pdf`):**
   $$\text{MMR}(p) = \operatorname*{argmax}_{p \in C \setminus S} \left[ \lambda \cdot \text{Rel}(p) - (1 - \lambda) \max_{s \in S} \text{Sim}(p, s) \right]$$

5. **Contextual Bandit (`Contextual_Bandits_LinUCB.pdf`):**
   $$S_{\text{UCB}}(c) = A(c) + \alpha \sqrt{\frac{\ln(|C| + 1)}{n_c + 1}}$$
