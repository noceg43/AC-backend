# Members

The `members` blueprint is responsible for managing user profiles in the AlphaConnect API. Each user is represented as a "member" in the system. This document provides details on the custom logic and endpoints implemented in the `members` blueprint.

## Custom Logic

The `members` blueprint extends the `ResourceBlueprint` with custom logic for creating and deleting members.

### Creating a Member

When a new member is created, the following custom logic is executed:

*   **Duplicate Check:** The system checks if a member with the same `userId` already exists. If a member with the same `userId` already exists, a new one cannot be created. This ensures that each `userId` is unique.

### Deleting a Member

When a member is deleted, the following actions are performed:

*   **Delete Member Answers:** All answers submitted by the member are deleted.
*   **Delete Member:** Finally, the member itself is deleted.

## Custom Endpoints

In addition to the standard CRUD endpoints, the `members` blueprint provides the following custom endpoint:

### `GET /api/v0/collections/members/<memberId>/lobbyMatch`

This endpoint retrieves the lobby and match details for a specific member. The `memberId` in the URL should be the `userId` of the member, not the internal member ID.

The response will contain the lobby that the member has joined and the match that has been created for them, if any.
