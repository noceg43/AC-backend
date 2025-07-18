# Questions and Answers

The `questions` and `answers` blueprints are responsible for managing the questions and answers used in the matching process. This document provides an overview of these blueprints and their role in the AlphaConnect API.

## `questions` Blueprint

The `questions` blueprint provides endpoints for managing questions. It extends the `ResourceBlueprint` and provides the standard CRUD endpoints for questions.

In addition to the standard endpoints, the `questions` blueprint provides the following custom endpoint:

### `GET /api/v0/collections/questions-with-match`

This endpoint retrieves all questions, along with the answers that members have submitted for each question. This data is used by the `LobbyScheduler` to feed the matching algorithm.

## `answers` Blueprint

The `answers` blueprint provides endpoints for managing the possible answers for each question. It is a simple `ResourceBlueprint` without any custom logic. It provides the standard CRUD endpoints for answers.

## `member_answers` Blueprint

The `member_answers` blueprint is responsible for storing the answers that members have submitted for each question. It provides the standard CRUD endpoints for member answers.

When a member answers a question, a new entry is created in the `member_answers` collection. This entry links the member, the question, and the chosen answer.

## Role in the Matching Process

The `questions`, `answers`, and `member_answers` blueprints work together to provide the necessary data for the matching process.

1.  **Questions and Answers:** The `questions` and `answers` collections define the set of questions that will be presented to the users and the possible answers for each question.
2.  **Member Answers:** The `member_answers` collection stores the answers that each member has submitted.
3.  **Data for Matching:** When the matching process is triggered, the `LobbyScheduler` calls the `/api/v0/collections/questions-with-match` endpoint to retrieve all questions and their member answers. This data is then passed to the `AlphaConnectMatcher` to perform the matching.
