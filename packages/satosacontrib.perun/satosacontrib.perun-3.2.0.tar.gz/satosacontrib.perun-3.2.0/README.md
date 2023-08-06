# satosacontrib.perun

Microservices for [SATOSA](https://github.com/IdentityPython/SATOSA) authentication proxy, made by the Perun team.

## Microservices

### Context attributes microservice

The microservice adds the target IdP data to attributes:

- display name
- logo
- target issuer

The [MetaInfoIssuer](https://github.com/SUNET/swamid-satosa/blob/main/src/swamid_plugins/metainfo/metainfo.py)
microservice needs to be run beforehand with the following [patch](https://github.com/SUNET/swamid-satosa/compare/main...kofzera:swamid-satosa:add_collector_metadata.patch).
Another [patch](https://github.com/IdentityPython/SATOSA/compare/master...kofzera:SATOSA:decorate_context_with_metadata.patch) is
also needed for the satosa package until they are incorporated into the upstream.

### Is banned microservice

The microservice connects to database storing user bans and redirects banned users to configured URL.

## Perun Microservices

Subpackage of microservices connecting to perun. These have to be allowed (or not denied) for
a given combination of requester/target_entity in order to run.
