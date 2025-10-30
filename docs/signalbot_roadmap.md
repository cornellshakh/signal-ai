> **LEGACY DOCUMENT:** This roadmap is outdated and has been superseded by the new modular architecture. It is kept for historical purposes only.

---

# Signalbot Fork Implementation Roadmap (Swagger-Based)

This document outlines the plan for enhancing our `signalbot` fork to be a complete and high-level client for the `signal-cli-rest-api`, based on the provided `swagger.json`.

## Group Management Methods

The following methods will be added to the `signalbot.SignalBot` class to provide a complete and intuitive API for managing Signal groups.

### 1. `create_group`

- **Description:** Creates a new Signal group.
- **Endpoint:** `POST /v1/groups/{number}`
- **Request Body Schema (`api.CreateGroupRequest`):**
  - `name`: `string`
  - `members`: `List[str]`
  - `description`: `Optional[str]`
  - `permissions`: `Optional[api.GroupPermissions]`
  - `group_link`: `Optional[str]` (Enum: "disabled", "enabled", "enabled-with-approval")
  - `expiration_time`: `Optional[int]`
- **Response Schema (`api.CreateGroupResponse`):**
  - `id`: `string`
- **Method Signature:** `create_group(self, name: str, members: List[str], description: Optional[str] = None, permissions: Optional[Dict[str, str]] = None, group_link: Optional[str] = None, expiration_time: Optional[int] = None) -> Dict[str, Any]:`

### 2. `get_group`

- **Description:** Retrieves the details of a specific group.
- **Endpoint:** `GET /v1/groups/{number}/{groupid}`
- **Response Schema (`client.GroupEntry`):**
  - `id`: `string`
  - `name`: `string`
  - `description`: `string`
  - `members`: `List[str]`
  - `admins`: `List[str]`
  - `blocked`: `bool`
  - `internal_id`: `string`
  - `invite_link`: `string`
  - `pending_invites`: `List[str]`
  - `pending_requests`: `List[str]`
- **Method Signature:** `get_group(self, group_id: str) -> Dict[str, Any]:`

### 3. `add_group_members`

- **Description:** Adds one or more members to an existing Signal group.
- **Endpoint:** `POST /v1/groups/{number}/{groupid}/members`
- **Request Body Schema (`api.ChangeGroupMembersRequest`):**
  - `members`: `List[str]`
- **Method Signature:** `add_group_members(self, group_id: str, members: List[str]) -> None:`

### 4. `remove_group_members`

- **Description:** Removes one or more members from an existing Signal group.
- **Endpoint:** `DELETE /v1/groups/{number}/{groupid}/members`
- **Request Body Schema (`api.ChangeGroupMembersRequest`):**
  - `members`: `List[str]`
- **Method Signature:** `remove_group_members(self, group_id: str, members: List[str]) -> None:`

### 5. `add_group_admins`

- **Description:** Promotes one or more members to admins in an existing Signal group.
- **Endpoint:** `POST /v1/groups/{number}/{groupid}/admins`
- **Request Body Schema (`api.ChangeGroupAdminsRequest`):**
  - `admins`: `List[str]`
- **Method Signature:** `add_group_admins(self, group_id: str, admins: List[str]) -> None:`

### 6. `delete_group`

- **Description:** Deletes a Signal group.
- **Endpoint:** `DELETE /v1/groups/{number}/{groupid}`
- **Method Signature:** `delete_group(self, group_id: str) -> None:`

### 7. `update_group`

- **Description:** Updates the state of a Signal Group.
- **Endpoint:** `PUT /v1/groups/{number}/{groupid}`
- **Request Body Schema (`api.UpdateGroupRequest`):**
  - `name`: `Optional[str]`
  - `description`: `Optional[str]`
  - `base64_avatar`: `Optional[str]`
  - `expiration_time`: `Optional[int]`
  - `group_link`: `Optional[str]` (Enum: "disabled", "enabled", "enabled-with-approval")
  - `permissions`: `Optional[api.GroupPermissions]`
- **Method Signature:** `update_group(self, group_id: str, name: Optional[str] = None, description: Optional[str] = None, avatar: Optional[str] = None) -> None:`
