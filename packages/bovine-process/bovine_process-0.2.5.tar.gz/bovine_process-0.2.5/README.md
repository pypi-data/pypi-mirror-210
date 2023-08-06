# bovine_process

`bovine_process` consists of the side effect logic of Activity objects. This means it contains the code, the logic that for an incoming object, one executes:

- Store object in bovine_store
- Add reference to inbox
- Perform side effects
- Enque object for bovine_pubsub

And a similar list of effects for outgoing objects, i.e

- Store object in bovine_store
- Add reference to outbox
- Perform side effects
- Send objects to follower's inbox
- Enque object for bovine_pubsub

The behavior defined in this package corresponds to [6. Client to Server Interactions](https://www.w3.org/TR/activitypub/#client-to-server-interactions) and [7. Server to Server Interactions](https://www.w3.org/TR/activitypub/#server-to-server-interactions) of the ActivityPub specification. However, only a small subset of side effects is implemented.

## Implemented Side Effects

- Create, Update, Delete. Deletes are handled by replacing the object with a Tombstone. Various checks are performed to ensure only appropriate Updates happen.
- [ ] Specify Update checks
- Follow and Accept
  - Outgoing Accept of Follow adds to followers
  - Incoming Accept of Follows adds to following
- [ ] Implement other side effects, in particular Like, Announce, and inReplyTo
- [ ] Authority checks.

That's it. Currently, no collections for replies and likes are kept in bovine_store, so implementing these side effects cannot happen yet:

- [ ] Announce -> add to share collection
- [ ] Like -> add to likes collection
- [ ] Create with inReplyTo -> add to replies collection

## Tests

The folder `tests/data` contains test cases what side effects happen in the database for certain cases.
