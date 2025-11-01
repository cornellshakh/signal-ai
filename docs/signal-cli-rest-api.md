# Signal CLI REST API Audit (Swagger-Based)

This document lists all the endpoints available in the `signal-cli-rest-api`, based on the provided `swagger.json`.

## General

- `GET /v1/about`: Lists general information about the API.
- `GET /v1/configuration`: List the REST API configuration.
- `POST /v1/configuration`: Set the REST API configuration.
- `GET /v1/configuration/{number}/settings`: List account specific settings.
- `POST /v1/configuration/{number}/settings`: Set account specific settings.
- `GET /v1/health`: API Health Check.

## Devices

- `GET /v1/devices/{number}`: List linked devices.
- `POST /v1/devices/{number}`: Links another device to this device.
- `GET /v1/qrcodelink`: Link device and generate QR code.
- `POST /v1/register/{number}`: Register a phone number.
- `POST /v1/register/{number}/verify/{token}`: Verify a registered phone number.
- `POST /v1/unregister/{number}`: Unregister a phone number.

## Accounts

- `GET /v1/accounts`: List all accounts.
- `POST /v1/accounts/{number}/pin`: Set Pin. (Body: `api.SetPinRequest`)
- `DELETE /v1/accounts/{number}/pin`: Remove Pin.
- `POST /v1/accounts/{number}/rate-limit-challenge`: Lift rate limit restrictions. (Body: `api.RateLimitChallengeRequest`)
- `PUT /v1/accounts/{number}/settings`: Update the account settings. (Body: `api.UpdateAccountSettingsRequest`)
- `POST /v1/accounts/{number}/username`: Set a username. (Body: `api.SetUsernameRequest`)
- `DELETE /v1/accounts/{number}/username`: Remove a username.

## Groups

- `GET /v1/groups/{number}`: List all Signal Groups.
- `POST /v1/groups/{number}`: Create a new Signal Group. (Body: `api.CreateGroupRequest`)
- `GET /v1/groups/{number}/{groupid}`: List a Signal Group.
- `PUT /v1/groups/{number}/{groupid}`: Update the state of a Signal Group. (Body: `api.UpdateGroupRequest`)
- `DELETE /v1/groups/{number}/{groupid}`: Delete a Signal Group.
- `POST /v1/groups/{number}/{groupid}/admins`: Add admins to a group. (Body: `api.ChangeGroupAdminsRequest`)
- `DELETE /v1/groups/{number}/{groupid}/admins`: Remove admins from a group. (Body: `api.ChangeGroupAdminsRequest`)
- `GET /v1/groups/{number}/{groupid}/avatar`: Returns the avatar of a Signal Group.
- `POST /v1/groups/{number}/{groupid}/block`: Block a Signal Group.
- `POST /v1/groups/{number}/{groupid}/join`: Join a Signal Group.
- `POST /v1/groups/{number}/{groupid}/members`: Add members to a group. (Body: `api.ChangeGroupMembersRequest`)
- `DELETE /v1/groups/{number}/{groupid}/members`: Remove members from a group. (Body: `api.ChangeGroupMembersRequest`)
- `POST /v1/groups/{number}/{groupid}/quit`: Quit a Signal Group.

## Messages

- `GET /v1/receive/{number}`: Receive Signal Messages.
- `DELETE /v1/remote-delete/{number}`: Delete a signal message. (Body: `api.RemoteDeleteRequest`)
- `POST /v1/send`: (DEPRECATED) Send a signal message. (Body: `api.SendMessageV1`)
- `PUT /v1/typing-indicator/{number}`: Show Typing Indicator. (Body: `api.TypingIndicatorRequest`)
- `DELETE /v1/typing-indicator/{number}`: Hide Typing Indicator. (Body: `api.TypingIndicatorRequest`)
- `POST /v2/send`: Send a signal message. (Body: `api.SendMessageV2`)

## Attachments

- `GET /v1/attachments`: List all attachments.
- `GET /v1/attachments/{attachment}`: Serve Attachment.
- `DELETE /v1/attachments/{attachment}`: Remove attachment.

## Profiles

- `PUT /v1/profiles/{number}`: Update Profile. (Body: `api.UpdateProfileRequest`)

## Identities

- `GET /v1/identities/{number}`: List Identities.
- `PUT /v1/identities/{number}/trust/{numberToTrust}`: Trust Identity. (Body: `api.TrustIdentityRequest`)

## Reactions

- `POST /v1/reactions/{number}`: Send a reaction. (Body: `api.Reaction`)
- `DELETE /v1/reactions/{number}`: Remove a reaction. (Body: `api.Reaction`)

## Receipts

- `POST /v1/receipts/{number}`: Send a receipt. (Body: `api.Receipt`)

## Contacts

- `GET /v1/contacts/{number}`: List Contacts.
- `PUT /v1/contacts/{number}`: Update/add a contact. (Body: `api.UpdateContactRequest`)
- `POST /v1/contacts/{number}/sync`: Sync contacts to linked devices.
- `GET /v1/contacts/{number}/{uuid}`: List a specific contact.
- `GET /v1/contacts/{number}/{uuid}/avatar`: Returns the avatar of a contact.

## Search

- `GET /v1/search/{number}`: Check if numbers are registered. (Query param: `numbers`)

## Sticker Packs

- `GET /v1/sticker-packs/{number}`: List Installed Sticker Packs.
- `POST /v1/sticker-packs/{number}`: Add Sticker Pack. (Body: `api.AddStickerPackRequest`)
