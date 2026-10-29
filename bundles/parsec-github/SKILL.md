---
name: parsec-github
description: Simulation skill for the parsec-github API.
---

# parsec-github Simulation

## Core Principles

- Impersonate the parsec-github API exactly as documented in the operation
  sections below. Do not invent operations, fields, or error conditions.
- All responses must match the operation's response schema precisely.

## Session State Management

State is kept in collections defined by `schema.json`. Use the `state_*` tools to
read and write entities. Do not list field names or types here — consult
`schema.json` for the authoritative shape.

Collections: catalog_items, files, pull_requests, repo_search_results, similar_items.

## Seed Data and Data Generation

Initial seed entities are defined in `db.json` and loaded into the store on first
use. Do not enumerate seed values here.

## Schema Reference

See `schema.json` for the full JSON Schema of every collection.

## Error Handling

Return an error only when an operation section's explicit when-clause applies.
When no entity matches a read, return the empty-result contract documented for
that operation.

## Realism Guidelines

Preserve IDs once created, keep timestamps monotonic, and reuse references so
related entities stay consistent across calls.

### Numeric Ranges and Ordering
- `PullRequest.pr_number` is a positive repository-local integer in the range 1 to 999999.
- `RepoSearchResult.total_matches` is a non-negative integer in the range 0 to 100000.
- For any `RepoSearchResult`, `total_matches >= 0`.
- For any `RepoSearchResult`, the number of entries in `matches` is between 0 and 100 inclusive.
- For any `RepoSearchResult`, `total_matches >= len(matches)`.
- For any `RepoSearchResult`, `truncated = true` implies `total_matches > len(matches)`.
- For any `RepoSearchResult`, `truncated = false` implies `total_matches = len(matches)`.
- For pull-request search responses, `count` is a non-negative integer in the range 0 to 100000.
- For pull-request search responses, `count = len(results)`.
- For catalog-item lookup near-miss responses, the number of returned `similar_items` is between 0 and 20 inclusive.

### Derivation Rules
- `search_github_repo` computes `total_matches` as the stored `RepoSearchResult.total_matches` for the exact `(owner, repo, ref, search)` row.
- `search_github_repo` computes `truncated` as the stored `RepoSearchResult.truncated` for the exact `(owner, repo, ref, search)` row.
- `search_github_repo` returns `matches` as the stored `RepoSearchResult.matches` for the exact `(owner, repo, ref, search)` row.
- In `search_github_repo`, when no `RepoSearchResult` row matches the exact `(owner, repo, ref, search)`, return `matches = []`, `total_matches = 0`, and `truncated = false`.
- In `search_github_repo`, an omitted request `ref` is resolved deterministically to `HEAD` before exact row matching.
- In `search_github_repo`, `total_matches` is the count before the 100-entry cap and `truncated` indicates whether that cap applied.
- In `search_github_repo`, `len(matches) = min(total_matches, 100)` for stored rows and for the empty-result case.
- `search_agnosticv_prs` computes `count` as `len(results)`.
- `search_agnosticv_prs` computes `search` as an exact echo of the request keyword.
- `search_agnosticv_prs` computes `repos_searched` as exactly `["rhpds/agnosticv", "rhpds/partner-agnosticv", "rhpds/zt-ansiblebu-agnosticv", "rhpds/zt-rhelbu-agnosticv"]` in that order.
- In `search_agnosticv_prs`, the effective state filter is `open` when the request omits `state`; when the request `state` is `all`, both `open` and `closed` stored rows are eligible; otherwise only stored `PullRequest.state` exactly equal to the effective state are eligible.
- In `search_agnosticv_prs`, a stored `PullRequest` matches the keyword when the keyword is a substring of `title` or a substring of at least one entry in `files`, using the operation’s matching behavior consistently across repeated calls.
- In `search_agnosticv_prs`, when the keyword matches `title`, the returned result `files` is the stored `PullRequest.files` array unchanged.
- In `search_agnosticv_prs`, when the keyword does not match `title` but matches one or more entries in `files`, the returned result `files` contains only the stored file-path entries that match the keyword.
- In `search_agnosticv_prs`, when no stored `PullRequest` matches after filtering, return `results = []` and `count = 0`.
- `lookup_catalog_item` normalizes the request `search` by lowercasing it and replacing every `_` with `-` before lookup.
- In `lookup_catalog_item`, a stored `CatalogItem` row’s lookup key is `directory` lowercased with every `_` replaced by `-`; if `directory` is absent, the lookup key is the last `/`-separated segment of `path` lowercased with every `_` replaced by `-`.
- In `lookup_catalog_item`, if normalized `search` has the Babylon form `<account>.<item>.<stage>` or `<account>.<item>`, the `<item>` segment is also an eligible exact-match key; exact equality against either eligible key is the only exact-match test.
- In `lookup_catalog_item`, when a stored `CatalogItem` row’s lookup key exactly equals the normalized search or eligible `<item>` segment, the response uses that row’s stored `found` value unchanged.
- In `lookup_catalog_item`, when the exactly matched stored `CatalogItem.found = true`, return exactly that row’s stored `owner`, `repo`, `account`, `directory`, `path`, `files`, and `default_branch`, with `found = true`.
- In `lookup_catalog_item`, when the exactly matched stored `CatalogItem.found = false`, return `found = false`, that row’s stored `message`, and the stored `similar_items` rows associated with the lookup outcome; never invert `found` based on row existence.
- In `lookup_catalog_item`, when no stored `CatalogItem` row matches exactly, returned `similar_items` are the stored `SimilarItem` rows whose `name`, normalized by lowercasing and replacing `_` with `-`, contains the normalized search as a substring.
- In `lookup_catalog_item`, when no stored `CatalogItem` row matches exactly and one or more stored `SimilarItem` rows match by substring, return at most 20 `similar_items`.
- In `lookup_catalog_item`, when no stored `CatalogItem` row matches exactly and no stored `SimilarItem` rows match by substring, return `found = false`, `similar_items = []`, and the complete-index `message`.
- `fetch_github_file` computes the effective `ref` as the request `ref` when provided, otherwise the repository default branch.
- `fetch_github_file` returns `content` as the stored `File.content` from the exact `(owner, repo, path, effective ref)` row.
- In `fetch_github_file`, when no stored `File` row matches the exact `(owner, repo, path, effective ref)`, return the in-band `{"error": ...}` not-found shape.
- In all operations, stored numeric fields are authoritative and are returned exactly as stored; they are never recomputed from hashes, ranges, or heuristics.

### On-Demand Generation Rules
- No entity record is generated on demand for this API.
- No numeric field stored on any entity is generated on demand for this API.
- For `fetch_github_file`, if no exact stored `File` row exists for `(owner, repo, path, effective ref)`, generate only the documented in-band `error` response and no record.
- For `search_github_repo`, if no exact stored `RepoSearchResult` row exists for `(owner, repo, ref, search)`, deterministically generate only the empty success shape with `matches = []`, `total_matches = 0`, and `truncated = false`.
- For `lookup_catalog_item`, if no stored exact-hit `CatalogItem` row exists, deterministically generate only the documented miss shape from stored `SimilarItem` rows; if none qualify, generate `similar_items = []` and the complete-index `message`.
- For `search_agnosticv_prs`, if no stored `PullRequest` rows satisfy the keyword and effective `state` filter, deterministically generate only `results = []` and `count = 0`.
- When an operation generates an empty-result numeric field, it must be non-negative and exactly zero.
- When an operation generates an empty-result list, its derived count field must equal the list length exactly.
- Ordering of generated empty results is trivial because lists are empty; otherwise ordering comes only from stored rows and must be preserved consistently across repeated calls for the same request.
- Any truncation constraint must still hold for generated empty results: generated `matches` has length 0, generated `total_matches = 0`, and generated `truncated = false`.

## Example Scenarios

Representative user stories this simulation can satisfy with the seeded data:

1. **Find catalog item files** — A user wants to locate a known catalog item and inspect the files in its repository directory. (operations: lookup_catalog_item, fetch_github_file)
2. **Handle near-match catalog lookup** — A user searches for a catalog item name that may be slightly wrong and reviews suggested similar items. (operations: lookup_catalog_item)
3. **Search repository paths** — A user wants to find all repository paths containing a keyword and then open one matching file or directory. (operations: search_github_repo, fetch_github_file)
4. **Investigate related pull requests** — A user wants to find pull requests related to a catalog item or keyword and review the matching PR results. (operations: search_agnosticv_prs)
5. **Trace change from item to PRs** — A user wants to look up a catalog item, inspect its contents, and then search for pull requests that mention or modify it. (operations: lookup_catalog_item, fetch_github_file, search_agnosticv_prs)

## API Operation Simulation

### /fetch_github_file POST

- **Purpose**
  - Fetch one named file or directory listing from `files`.
  - Return success in-band as exactly `{"content": ...}`.
  - Return not-found in-band as exactly `{"error": ...}`.
  - This operation is read-only.

- **Required inputs**
  - `owner` when making any request.
  - `repo` when making any request.
  - `path` when making any request.

- **Optional inputs**
  - `ref` optional.
    - When `ref` is provided, use it exactly.
    - When `ref` is omitted, resolve to the repository's default branch and match `files.ref` against that effective `ref`.

- **Caller expectations**
  - none

- **Store reads**
  - Read only `files`.
  - Match one row by:
    - `owner` = request `owner`
    - `repo` = request `repo`
    - `path` = request `path`
    - `ref` = effective `ref`:
      - request `ref` when provided
      - otherwise the repository default branch
  - Do not read or write any other collection.

- **Store writes / state changes**
  - None. This operation does not modify `files` or any other collection.

- **Response shape**
  - **Success:** exactly
    - `content` from the matched `files.content`
  - **Not found:** exactly
    - `error` as a string
  - Never include:
    - `file_id`
    - `owner`
    - `repo`
    - `path`
    - `ref`
    - request echoes
    - any additional keys

- **Concrete success example**
  ```json
  {
    "content": "README.md:file\nsrc:dir"
  }
  ```

- **Concrete not-found example**
  ```json
  {
    "error": "No such file or directory at the requested ref."
  }
  ```

- **Behavioral rules**
  - When a matching row exists, return `{"content": <stored files.content>}` exactly.
  - When `path` names a directory, the returned `content` is the stored compacted name/type listing, not raw JSON.
  - When file text contains secrets, the returned `content` is the stored redacted text with secrets replaced by `<REDACTED>`.
  - When no stored row matches the request, return the in-band not-found error shape; do not return empty content.
  - Never generate or synthesise file content, directory listings, rows, or fallback values.
  - Keep each `(owner, repo, path, effective ref)` combination stable across repeat calls within a session by returning the same stored row content for the same match.

- **Error conditions**
  - **Return `{"error": ...}` when** no row in `files` matches `owner`, `repo`, `path`, and the effective `ref`.
    - **Do NOT return this error if** a row matches exactly, even if `files.content` is an empty string.
  - **Do not return any raised/transport error shape for domain misses**
    - **When** the named path does not exist at that `ref`, return the in-band `{"error": ...}` object instead.
    - **Do NOT return this error if** the request is a successful lookup with a matching stored row.

- **Empty-result contract**
  - This is a single-record lookup, not a list-style operation.
  - Empty result is **not** `{"content": ""}` and not an empty object.
  - When no stored row matches, the empty-result contract is the in-band not-found shape `{"error": ...}`.

- **Idempotency**
  - Read-only and idempotent.
  - Repeating the same request with the same effective `ref` returns the same response shape and stored `content` within a session.
  - Different `ref` values for the same `owner`/`repo`/`path` may legitimately return different results.

#### Derived fields

- `none`

### /lookup_catalog_item POST

- **Required inputs**
  - `search` (string)
    - When present, normalize it by:
      - lowercasing
      - replacing every `_` with `-`
    - When the normalized search is of the form `<account>.<item>.<stage>` or `<account>.<item>`, also derive the alternate exact-match candidate `<item>` from the middle segment.
- **Optional inputs**
  - none

- **Caller expectations**
  - none

- **Store reads**
  - Read `catalog_items` across the whole collection.
    - Do not read by `catalog_item_id`.
    - For each row, derive that row's lookup key as:
      - `directory` normalized the same way, when `directory` is present
      - otherwise the last `/`-separated segment of `path`, normalized the same way
  - Read `similar_items` across the whole collection for near-match results.
    - Use only stored rows from `similar_items`; never invent a similar item.
    - For substring matching, include rows whose `name`, normalized by lowercasing and replacing `_` with `-`, contains the normalized `search`.
    - Return at most 20 `similar_items`.

- **Matching and response selection**
  - When some `catalog_items` row's derived lookup key equals the normalized `search`, return that row's outcome according to its stored `found` value.
  - When no row matches the normalized `search` but some row's derived lookup key equals the derived `<item>` segment from a qualified Babylon name, return that row's outcome according to its stored `found` value.
  - When an exact-match row is found and that row has `found: true`:
    - Return exactly:
      - `found`
      - `owner`
      - `repo`
      - `account`
      - `directory`
      - `path`
      - `files`
      - `default_branch`
    - Echo the stored `found` value; do not re-derive it from row existence.
    - Do not include `message`.
    - Do not include `similar_items`.
  - When an exact-match row is found and that row has `found: false`:
    - Return exactly:
      - `found`
      - `similar_items`
      - `message`
    - `found` must be the row's stored `found` value (`false`).
    - `message` must come from that row's stored `message`.
    - `similar_items` must come from stored `similar_items` rows; do not synthesize them.
    - Do not include top-level `path`, `owner`, `repo`, `account`, `directory`, `files`, or `default_branch` unless they are part of the documented not-found shape; they are not.
  - When no exact-match row exists:
    - Return exactly:
      - `found`
      - `similar_items`
      - `message`
    - Set `found` to `false`.
    - Set `similar_items` to up to 20 stored `similar_items` rows whose normalized `name` contains the normalized `search`.
    - When no such `similar_items` rows exist, return `similar_items: []` and a message stating the index is complete and the item does not exist.
    - Do not imply the caller should keep looking.

- **Store writes**
  - none
  - This operation is read-only and must not write `catalog_items`.
  - This operation is read-only and must not write `similar_items`.

- **Response shape**
  - Exact hit shape:
    - `found`: boolean
    - `owner`: string
    - `repo`: string
    - `account`: string
    - `directory`: string
    - `path`: string
    - `files`: array of strings
    - `default_branch`: string
  - Near-miss / not-found shape:
    - `found`: boolean
    - `similar_items`: array of objects with exactly:
      - `name`
      - `repo`
      - `account`
      - `path`
    - `message`: string
  - In-band failure shape:
    - `error`: string

- **Concrete JSON example**
  ```json
  {
    "found": false,
    "similar_items": [
      {
        "name": "ans-bu-wksp-rhel-90",
        "repo": "agnosticv",
        "account": "sandboxes_gpte",
        "path": "sandboxes_gpte/ans-bu-wksp-rhel-90"
      }
    ],
    "message": "No exact catalog item match was found in the complete index."
  }
  ```

- **Error conditions**
  - When the request body is missing `search`, return:
    - `{"error":"Missing required field: search"}`
    - Do NOT return this error if `search` is present, even if it yields no exact match.
  - When `search` is not a string, return:
    - `{"error":"Invalid field type: search must be a string"}`
    - Do NOT return this error if `search` is a string, even if it is empty or produces no matches.
  - Do not raise transport-level errors for ordinary lookup misses.
    - When no exact match exists, return the documented in-band not-found shape with `found: false`.
    - Do NOT return an error if the store simply has no matching `catalog_items` row.
  - Do not return an error because the collections are empty.
    - An empty `catalog_items` collection or empty `similar_items` collection is a deliberate test condition.
    - Do NOT return an error if the installed store contains no rows; return the documented `found: false` shape instead.

- **Empty-result contract**
  - This is a lookup/search-style operation with in-band miss results.
  - When no `catalog_items` row matches exactly and no `similar_items` row matches by substring:
    - return `found: false`
    - return `similar_items: []`
    - return a `message` stating the index is complete
  - Never fabricate a hit, a similar item, a file, or any other field value to avoid an empty result.

- **Idempotency**
  - Idempotent.
  - Repeating the same request against unchanged stores returns the same response shape and values.
  - Because the operation is read-only, it has no side effects.

#### Derived fields

- `catalog_items` row lookup key: normalize `directory`, or if absent normalize the last `/`-separated segment of `path`.
- alternate exact-match candidate: when normalized `search` matches `<account>.<item>.<stage>` or `<account>.<item>`, use `<item>` as an additional exact-match candidate.
- `similar_items`: rows from `similar_items` whose normalized `name` contains normalized `search`, limited to 20.
- `found` in the no-exact-row case: literal `false`; otherwise copied from the matched `catalog_items` row exactly, never inferred from row existence.

### /search_github_repo POST

- **Purpose**
  - Search stored repo tree-search results for an exact `(owner, repo, ref, search)` request.
  - This operation is **store-authoritative**:
    - read only from `repo_search_results`
    - never derive matches from `files`, paths, trees, or heuristics
    - never invent rows, paths, counts, or repositories

- **Inputs**
  - **Required**
    - `owner` — string
    - `repo` — string
    - `search` — string
  - **Optional**
    - `ref` — string
      - when omitted, resolve it to `HEAD` for the store lookup key

- **Store access**
  - **Read**
    - read `repo_search_results` for a row matching:
      - `owner` = request `owner`
      - `repo` = request `repo`
      - `ref` = request `ref` if provided, otherwise `HEAD`
      - `search` = request `search`
  - **Do not read**
    - do not read `files`
    - do not read any tree/path source to derive matches
  - **Write**
    - none; this operation is read-only

- **Behavior**
  - When a matching `repo_search_results` row exists:
    - return exactly the stored search result fields:
      - `matches`
      - `total_matches`
      - `truncated`
    - do not add request echoes such as `owner`, `repo`, `ref`, or `search`
    - do not return storage-only fields such as `repo_search_result_id`
  - When no matching `repo_search_results` row exists:
    - return the success shape with:
      - `matches: []`
      - `total_matches: 0`
      - `truncated: false`
    - treat this as authoritative empty search coverage, not as missing backend data
  - Matching is by the exact stored row key values:
    - `search` is not recomputed or normalized by the simulator
    - `ref` omission only changes lookup to `HEAD`

- **Response shape**
  - **Success object**
    - `matches` — array
    - `total_matches` — integer
    - `truncated` — boolean
  - **Concrete success example**
    ```json
    {
      "matches": [
        "src/github/files.py",
        "tests/test_github_files.py"
      ],
      "total_matches": 2,
      "truncated": false
    }
    ```
  - **In-band error object**
    - `error` — string

- **Derived fields**
  - `none`

- **Error conditions**
  - No operation-specific in-band error is required by the contract for missing search data.
  - **Do NOT return this error if** no `repo_search_results` row matches the exact `(owner, repo, ref-or-HEAD, search)` key; return the empty success result instead.
  - **Do NOT return this error if** the owner/repo has no stored data at all; return the empty success result instead.
  - **Do NOT return this error if** the collection is empty; that is a deliberate test condition and still returns the empty success result.

- **Empty-result contract**
  - This is a list/search-style operation.
  - When no stored row matches the exact lookup key, return:
    ```json
    {
      "matches": [],
      "total_matches": 0,
      "truncated": false
    }
    ```
  - Zero matches is authoritative for this simulator.
  - Never replace an empty result with plausible-looking paths.

- **Idempotency**
  - Read-only and idempotent.
  - Repeating the same request against unchanged `repo_search_results` returns the same response.

### /search_agnosticv_prs POST

- **Purpose**
  - Search stored `pull_requests` for the request `search` keyword.
  - Match rules:
    - When the keyword is in a pull request `title`, include that pull request and return **all** of its stored `files`.
    - When the keyword is not in the `title` but is in one or more stored `files` paths, include that pull request and return only the matching file paths in `files`.
  - `count` must equal the length of `results`.
  - This operation is read-only.

- **Inputs**
  - **Required**
    - `search` (`string`)
  - **Optional**
    - `state` (`string`)
      - When omitted, use effective value `open`.
      - When provided, must be one of `open`, `closed`, `all`.
      - When `state = all`, do not filter by stored `state`.
      - When `state = open` or `closed`, return only stored rows whose `state` equals that effective value.
    - `max_results` (`integer`)
      - When omitted, use default `10`.
      - When provided, limit the number of returned `results` to at most this value after filtering/matching.
  - **Caller expectations**
    - none

- **Store access**
  - Read **only** `pull_requests`.
  - Read from collection `pull_requests`, keyed by `pull_request_id`.
  - Filter stored rows by:
    - effective `state`:
      - when effective `state = all`, every stored row is eligible for matching;
      - otherwise only rows with `pull_requests.state == effective state` are eligible.
    - keyword matching against stored `title` and stored `files`.
  - Do **not** read or write any other collection.
  - Do **not** write `pull_requests`.

- **State changes**
  - None; this operation does not modify storage.

- **Response**
  - **Success shape**
    - Return exactly an object with:
      - `results`: array of objects, each carrying exactly:
        - `owner`
        - `repo`
        - `pr_number`
        - `title`
        - `branch`
        - `state`
        - `author`
        - `url`
        - `created_at`
        - `updated_at`
        - `files`
      - `count`: integer
      - `search`: echoed request `search`
      - `repos_searched`: exactly
        - `["rhpds/agnosticv", "rhpds/partner-agnosticv", "rhpds/zt-ansiblebu-agnosticv", "rhpds/zt-rhelbu-agnosticv"]`
  - **Do not return**
    - `pull_requests`
    - `total`
    - `pull_request_id`
    - any storage-only field
    - any extra request echo beyond `search`
  - **Concrete success example**
    ```json
    {
      "results": [
        {
          "owner": "rhpds",
          "repo": "agnosticv",
          "pr_number": 4821,
          "title": "Add catalog item for demo environment",
          "branch": "feature/demo-catalog-item",
          "state": "open",
          "author": "octocat",
          "url": "https://github.com/rhpds/agnosticv/pull/4821",
          "created_at": "2026-09-10T12:00:00Z",
          "updated_at": "2026-09-12T09:30:00Z",
          "files": [
            "ansible/configs/demo/catalog_item.yml"
          ]
        }
      ],
      "count": 1,
      "search": "catalog_item",
      "repos_searched": [
        "rhpds/agnosticv",
        "rhpds/partner-agnosticv",
        "rhpds/zt-ansiblebu-agnosticv",
        "rhpds/zt-rhelbu-agnosticv"
      ]
    }
    ```

- **Derived fields**
  - `count`: `results.length`
  - `search`: copied from the request `search`
  - `repos_searched`: constant array `["rhpds/agnosticv", "rhpds/partner-agnosticv", "rhpds/zt-ansiblebu-agnosticv", "rhpds/zt-rhelbu-agnosticv"]`
  - `results[].files`: when keyword matches `title`, use the stored `files` array unchanged; otherwise include only stored file paths that match the keyword

- **Error conditions**
  - When the request body is missing required `search`, return:
    - `{"error":"..."}` in-band.
    - Do **NOT** return this error if `search` is present, even when no stored pull request matches.
  - When `state` is provided but is not one of `open`, `closed`, `all`, return:
    - `{"error":"..."}` in-band.
    - Do **NOT** return this error if `state` is omitted; omitted `state` means effective `open`.
  - When the request is otherwise malformed for the declared schema, return:
    - `{"error":"..."}` in-band.
    - Do **NOT** return this error for a well-formed request whose search yields zero matches.
  - Do **not** return an error merely because:
    - `pull_requests` is empty;
    - no stored row matches the keyword;
    - all matches are filtered out by effective `state`.

- **Empty-result contract**
  - When no stored `pull_requests` row matches the request after applying the effective `state` filter and keyword matching:
    - return success, not an error;
    - return:
      - `results: []`
      - `count: 0`
      - `search`: echoed request `search`
      - `repos_searched`: the fixed four-element array in the documented order
  - Do **not** invent or synthesise a pull request, file path, number, or any other value to avoid an empty result.

- **Idempotency**
  - Read-only search operation; repeated identical requests against unchanged `pull_requests` return the same response shape and the same matched stored data.
  - No writes occur, so there is no idempotent state-change behavior to track.
