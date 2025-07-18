# API Guide

This guide provides information on how to interact with the AlphaConnect API. It covers the general principles of the API and explains how to use the provided `.rest` files for testing.

## General Principles

The AlphaConnect API is a RESTful API that uses JSON for all requests and responses. The API is organized around resources, and each resource has a set of endpoints for performing CRUD (Create, Read, Update, Delete) operations.

The base URL for the API is `http://localhost:1111/`. All endpoints are prefixed with `/api/collections/`. For example, the endpoint for listing all lobbies is `/api/collections/lobbies`.

The API uses standard HTTP methods for all operations:

*   `GET`: Retrieve a resource or a list of resources.
*   `POST`: Create a new resource.
*   `PUT`: Update an existing resource (full replace).
*   `PATCH`: Update an existing resource (partial update).
*   `DELETE`: Delete an existing resource.

## Using the `.rest` Files

The `rest` directory contains a set of `.rest` files that can be used to test the API. These files are designed to be used with the [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) extension for Visual Studio Code.

Each `.rest` file corresponds to a specific resource or a flow of operations. For example, the `lobby.rest` file contains requests for creating, listing, and deleting lobbies.

To use these files, you need to have the REST Client extension installed in Visual Studio Code. Once the extension is installed, you can open any `.rest` file and click on the "Send Request" button that appears above each request.

### Variables

The `.rest` files use variables to store values that are used in multiple requests, such as the base URL, authentication tokens, and resource IDs. These variables are defined at the beginning of each file.

For example, the `lobby.rest` file might start with the following variable definitions:

```
@baseUrl = http://localhost:1111
@lobbyId = 5f9b3b3b3b3b3b3b3b3b3b3b
```

You can change the values of these variables to match your environment.

### Flows

The `rest/flows` directory contains `.rest` files that demonstrate a sequence of operations. These files are useful for understanding how the different resources interact with each other.

For example, the `1_invite.rest` file might show how to create a lobby and invite members to it. The `2_pre_event.rest` file might show how members can answer questions before the matching event.

By following the requests in these flow files, you can get a good understanding of how the application is intended to be used.
