# Master Data Science

## Guidelines for a master's thesis

### A. General Goals

We define Data Science as a discipline where *methods from Computer Science and Statistics are applied to some domain to create added value from data*. Therefore, a master's thesis in the study program “Master Data Science” should ideally start from a **real-world problem** for which a solution is sought, or, alternatively, should develop a new **data-driven business model** by implementing a prototype, used to explore the feasibility of the business model.

Naturally, strong emphasis will be on the **data engineering** part, in particular the feature engineering, as the underlying assumption is that data scientists are most influential in identifying and transferring the information needed for the task from the domain into the algorithms. In contrast, model training, as part of solution engineering, is increasingly provided as a service and automated. Here, the task of data scientists is the **model selection** by critically comparing suitable candidates using appropriate performance measures.

Since the goal is to provide value to people and/or organizations, the task is never completed by having some prototype implemented in a notebook. The developed solution needs to be **deployed** in a suitable way – for example, as a service accessible through an interface, or as an interactive visualization on some web site. Whereas emphasis should clearly be given to the solution itself, it must additionally be investigated how the outcome can effectively be used in practice. Also, the thesis should assess the **impact** of the developed solution on some organization or the society – what are the concrete benefits, and also possible negative impacts. This could include economic, ethical, and regulatory aspects.

### B. Formal Aspects

The thesis consists of a **paper** (~9,000 words, i.e. ~25 net pages, excluding references) focusing on the essential parts of your work, complemented by an **Appendix** (of reasonable size, but no formal page limit), providing further details. Citation style is either Harvard or IEEE. The language can be English or German (English is clearly recommended). The FHTW template **must** be used. The thesis can be blocked from public view up to 5 years.

### C. Structure

The paper must follow the IMRaD structure and therefore consists of the sections **Introduction, Methodology, Results** and **Discussion**. These are preceded by title, author, abstract, and keywords, and followed by references (bibliography). Subsections: at most 1 level; up to 2 levels for results.

#### Abstract

A short summary of the paper, including the **results** – about half a page.

#### 1. Introduction (~15%)

##### 1.1. Motivation of the topic

Why is it important? Is it new? What approaches already exist? What will be added by this thesis (**“research gap”**)? This part will necessarily include literature research, provides an overview on the *relevant* work in the field, and should lead to concrete ...

##### 1.2. Research questions

One thesis will typically answer several research questions (as a rule of thumb: 3). Note that assessing the state-of-the-art is never a separate research question (or a trivial one at best), since this is a prerequisite for any research anyway. Deployment and impact *can* be addressed as separate research questions, if they are non-trivial and really researched within the thesis. For example, an innovative part of some solution could be a new big data or cloud architecture that needs to be developed and investigated. Or the benefits of some developed business model could require some deeper economic or financial analysis.

Since Data Science is an engineering discipline, the *main* research questions are typically not descriptive as, e.g., in natural sciences (“How is the state of the world?”) but should be **prescriptive** (“How should the world be?”) or **predictive** (“How will the world be?”). Also, yes/no-answers will typically not suffice. So, instead of: “Is it possible to find a model to predict *foo*?”, the thesis should investigate: “What is the best model to predict *foo*?”. But certainly, some exploratory analysis (e.g., cluster analysis) can be a good starting point to develop such models, and investigating non-trivial structures of some given data can be a valid research question to start with, as long as it can be expected that the findings could apply to similar data sets.

Research questions must have a **general scope** that goes beyond the requirements of, e.g., a specific company or private interests, but concrete enough so that they can realistically be answered within the scope and time frame of the master’s project.

> **Example:**
>
> **Title:** Predicting rail usage to reduce maintenance costs in public transport
>
> Possible **Research Questions** (along the “data science pipeline”):
>
> *Data Engineering:*
> - What are the main physical **influence factors** for rail usage, and how can these be **measured**?
> - How must typical sensor data in this context be **preprocessed**?
>
> *Solution Engineering:*
> - Which **predictive methods** can provide usable forecasts? How do they **perform**?
>
> *Deployment:*
> - How can the results be **communicated** (in particular: visualized)?
> - How can the forecasting techniques be **integrated** in existing IT workflows?
>
> *Evaluation:*
> - How can model forecasts be used to reduce maintenance costs?
> - What are the possible **cost savings**?

For each research question, the applied **research method** and the **type of expected results** should be mentioned. Research methods could include expert interviews, prototyping, reference modeling, benchmarking, etc. (Note that if a research question can be answered by literature review alone, it is typically not a valid research question, since it is already answered). The type of expected results, respectively, could be a list of requirements, the performance measurements based on some prototype, a technical and/or managerial concept on how to implement a solution, a comparison of methods in a benchmark study, etc.

Examples:

| Research question | Method | Type of expected result |
|---|---|---|
| What are typical influence factors for rail usage? | Expert Interviews | List of influence factors and typical measures |
| How must typical data be preprocessed? | Data Engineering. Data Analysis. | Preprocessing pipeline as a script. Results of data analysis to assess data quality. |
| What is the predictive performance of algorithms typically used? | Benchmarking | Comparison of machine learning algorithms M₁/M₂ on data sets D₁/D₂ using performance measures P₁/P₂ |
| How can the forecasting techniques be integrated in existing IT workflows? | Prototyping | Technical concept and implementation (at least as a prototype). |

Note that your main results can **not** be based on expert interviews alone – they provide **complementary** information (domain knowledge on methods and typical requirements; evaluation).

#### 2. Methodology (~20%)

The second chapter should explain the methods used for answering the research questions. This includes the process as well as all empirical and technical tools. The description will naturally be based on literature, in the sense that it will refer to it – but note that it **must not** be a summary of basics (such as: “What is a neural network?”) but precisely explain *how* the methods are used (for example: what kind of network architecture is used for this work, how it is trained, how the hyperparameters are tuned etc.) and *why* (what are the alternatives?). The description must be detailed enough to allow the reproduction of the results. Assume that the reader is familiar with everything taught in the courses of the data science study program. Standard methods should not be described at all, specialized methods only shortly, and references given.

#### 3. Results (~50%)

This will be the main part. It should address the research questions, in a suitable structure: for example, one section per research question, or following the data science pipeline (data engineering --> modeling --> benchmarking --> deployment etc.). The concrete structure will depend on your topic.

Avoid code details here, just explain the general structure of your approach: what has been done and why? Report the results of data analyses and model statistics and give interpretations. Code parts will be provided in the Appendix as commented notebooks.

As mentioned, a mandatory part of your results is a suitable **deployment**, at least as a concept.

#### 4. Discussion (~15%)

A particularly important chapter is the discussion of the approach and the results. The aim here is to critically investigate the **quality** of your solution: what are the **potentials**, and more importantly, what are the **limitations**? How do your findings relate to **previous work**? To what extent will your results **generalize**? In essence: what is the **impact** of your work?

##### 4.1. Main findings

Shortly summarize your main findings by answering **each research question in turn**.

##### 4.2. Comparison with previous work

An important part of this chapter is the **comparison** with existing solutions and approaches found in the literature. How do the findings of the thesis relate to existing approaches? Are the results plausible? Is the proposed solution better than existing approaches?

##### 4.3. Implications

Also, you should assess **impacts** on society and/or the company (whatever applies) – positive and negative ones. This could include **benefits** such as organizational improvements (cost reductions), increased benefits (for new business models), or **threats** such as loss of jobs, increase of faked information, biases in automated information handling, loss of privacy, legal/ethical issues, etc.

##### 4.4. Limitations

**Weaknesses** in the methodology should be listed (e.g., sample sizes, data quality, limited choice of models, non-systematic hyperparameter tuning, incomplete implementation of the deployment, performance limitations etc.) and the **impact** on the solution be discussed. Also, possible **improvements** should be suggested. It is **mandatory** to comment on possible bias in data and/or models (e.g., gender, ethnicity …).

Examples:

| Limitation | Impact | Possible improvement |
|---|---|---|
| Small sample size | Model parameters are not significant | Use more data or other methods |
| Low data quality | Models do not generalize | Other data sources; refined data engineering |
| Limited choice of models | Model selection bias | Use more models from different families |
| Non-systematic hyperparameter tuning | Models do underfit | Use systematic grid search |
| Performance limitations | Solution is not practical | Investigate better implementations |
| Incomplete deployment | The practicability of the solution cannot be assessed | Sketch a possible implementation, and how to test it |

(The paper should of course be more elaborate for each point).

##### 4.5. Further Research

What is still open? What should be investigated next?

#### Bibliography

#### Appendix A/B/C ...

The **Bibliography** is followed by **Appendices** that provide details on your work. This should at least include all **notebooks** used, i.e., commented (!) code, combined with explanations on what has been done and why. Note that the word “science” in “data science” essentially means that your work is reproducible. The quality of the notebooks will be an important part in grading your work. In the Appendix, you could also give details of some exploratory data analysis, which typically results in a lot of diagrams and tables which do not fit in the paper.

### D. Organizational Aspects

The **topic** must be defined until the end of the 2nd semester during the “scientific writing” course and **presented** at the end of June. After **approval** by the study director, students get assigned their supervisor and prepare their **proposal** until the end of August. The “data science project” course in the 3rd semester starts with the **presentation** of the proposal and includes intermediate and peer reviews of the practical part. This process is continued in the 4th semester in the “diploma seminar”. A **first version** of the thesis must be submitted end of April, and the **final version** end of Mai to meet the **master's exam** end of June. The thesis must be submitted at the latest by the end (i.e., May) of the next study year to finish the studies.
