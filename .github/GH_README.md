# GitHub Configuration

This directory contains configuration files for GitHub-specific features:

## CLA (Contributor License Agreement)

- `CLA.md` - The actual CLA document that contributors must agree to
- `cla.json` - Tracks which contributors have signed the CLA
- `workflows/cla.yml` - GitHub Action that enforces CLA signing on pull requests

### How it works

1. When someone opens a PR, the CLA Assistant bot checks if they've signed the CLA
2. If not, it comments on the PR asking them to sign by commenting with the agreement text
3. Once signed, the signature is stored in `cla.json` and they won't be asked again
4. The PR can then proceed with review and merging

### Managing the CLA

- To add someone to the allowlist (e.g., bots), edit the `contributorWhitelist` in `cla.json`
- The CLA Assistant dashboard is available at: <https://cla-assistant.io/criteria-dev/gac>
- To require a new CLA version, update the document and increment the version in `cla.json`

### Why we use a CLA

The CLA allows us to:

- Maintain the flexibility to dual-license the project in the future if needed
- Ensure all contributions can be legally included in the project
- Protect both the project and contributors from legal issues

While the project is currently MIT licensed, the CLA preserves our options for sustainable development and potential
enterprise offerings in the future.
