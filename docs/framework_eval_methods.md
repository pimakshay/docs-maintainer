
# Framework Evaluation
This document outlines methods for evaluating the Documentation Maintainer framework. The framework allows users to enter natural language queries to identify and track necessary changes across documentation pages.
 
1. Ground-truth Evaluation
- Manually prepare 10-20 documentation snippets
- Create realistic changes and user queries
- Sample user queries generated using ChatGPT can be found here: [Sample User Queries](./sample_user_queries.md)

2. Unit test cases
- check if critical words from the user query are present in the suggested documents. For example: `as_tool`
- Check if user query matches semantically to the suggested documents.

3. Negative testing
- give random queries and test the responses. For ex: How to bake a cake?

4. Human-in-loop testing
- Ask testers to evaluate model performance. Log the metrics, check if retrieved documents are relevant and check if threshold score is suitable.