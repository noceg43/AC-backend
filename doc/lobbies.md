# Lobbies

The `lobbies` blueprint is responsible for managing lobbies in the AlphaConnect API. A lobby represents an event or a group where users can be matched. This document provides details on the custom logic and endpoints implemented in the `lobbies` blueprint.

## Custom Logic

The `lobbies` blueprint extends the `ResourceBlueprint` with custom logic for creating, updating, and deleting lobbies.

### Creating a Lobby

When a new lobby is created, the following custom logic is executed:

*   **Singleton Lobby:** The system checks if a lobby already exists. If a lobby already exists, a new one cannot be created. This ensures that there is only one active lobby at a time.
*   **Scheduling:** Upon successful creation, the new lobby is scheduled with the `LobbyScheduler`. The scheduler will trigger the matching process when the lobby's `preEventDate` is reached.

### Updating a Lobby

When a lobby is updated, the scheduler is also updated with the new lobby data. This ensures that any changes to the lobby's `preEventDate` are reflected in the schedule.

### Deleting a Lobby

When a lobby is deleted, the following actions are performed:

*   **Delete Matches:** All matches associated with the lobby are deleted.
*   **Remove Lobby from Members:** The lobby is removed from the `lobbies` array of all members who had joined it.
*   **Cancel Schedule:** The scheduled job for the lobby is canceled.
*   **Delete Lobby:** Finally, the lobby itself is deleted.

## Custom Endpoints

In addition to the standard CRUD endpoints, the `lobbies` blueprint provides the following custom endpoints:

### `POST /api/v0/collections/lobbies/join`

This endpoint allows a member to join a lobby. The request body must contain the `memberId` of the member who wants to join. If a `lobbyId` is provided, the member will be added to that lobby. Otherwise, the system will find the first available lobby and add the member to it.

### `POST /api/v0/collections/lobbies/quit`

This endpoint allows a member to quit a lobby. The request body must contain the `memberId` of the member who wants to quit and the `lobbyId` of the lobby they want to leave.

### `POST /api/v0/collections/lobbies/scheduler/refresh`

This endpoint manually refreshes the scheduler, causing it to fetch and schedule all existing lobbies.

### `POST /api/v0/collections/lobbies/<lobby_id>/scheduler/refresh`

This endpoint refreshes the schedule for a specific lobby.

### `DELETE /api/v0/collections/lobbies/<lobby_id>/scheduler/cancel`

This endpoint cancels the scheduled job for a specific lobby.

### `POST /api/v0/collections/lobbies/<lobby_id>/test-matching`

This is a temporary endpoint for testing the matching algorithm for a specific lobby. It should not be used in production.
