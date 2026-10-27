# One source, one release

For agent-led installation/update from a repository URL, start with [INSTALL.md](../INSTALL.md). The verifier in `scripts/verify_install.py` checks the actual installed snapshot and executes its helpers.

Canonical code and both skills live in this repository. Installed caches are generated artifacts. User templates live in a project/library outside those caches.

## Maintainer release

1. Modify `plugins/slidev-studio/skills/` or the plugin tools. For upstream changes, run `python3 scripts/check_upstream.py`, inspect the official diff and merge deliberately. Never overwrite the customized skill with an upstream installer.
2. Run `python3 scripts/release.py sync X.Y.Z`. This updates VERSION, portable/Codex/Claude manifests, the Claude marketplace version, skill metadata, and content hashes together.
3. Run both test suites and `python3 scripts/release.py validate`. Build archives with `python3 scripts/release.py build`. Review their contents; user decks and libraries do not belong in this repository.
4. Commit, push, tag `vX.Y.Z`, and push the tag. The release workflow tests the tagged code, checks tag/version consistency, builds deterministic plugin and portable-skills ZIPs, and publishes them with SHA256SUMS.

There is no independent auto-updater rewriting skill files. Skill changes ship in the same plugin release as the code they depend on. The upstream-check workflow reports changes for review; it does not merge them or touch local user files.

## Codex update

```bash
codex plugin marketplace upgrade slidev-local
codex plugin add slidev-studio@slidev-local
codex plugin list --marketplace slidev-local --json
```

The first command refreshes the configured Git marketplace. Reinstalling resolves its current plugin version. Start a fresh chat/reload the host if needed. A marketplace pinned to an immutable tag stays on that version; change the ref deliberately to update.

## Claude Code update

Use Claude's native marketplace/plugin update commands for the `slidev-local` marketplace. This repo includes `.claude-plugin/marketplace.json` and the plugin's `.claude-plugin/plugin.json`; both load the same canonical `skills/` content.

## Cursor or generic Agent Skills

From an updated checkout:

```bash
git pull --ff-only
python3 scripts/install_agent.py --agent cursor --project /path/to/project
# Or --agent claude / --agent generic
```

The installer updates both skills as one snapshot and records version/content hashes. It preserves unrelated skills, refuses to overwrite local modifications, and rolls back if installation fails. Merge local customizations into source or archive them before updating. The generic skills ZIP can also be extracted into a project's `.agents/skills/` directory, but the managed installer is preferred for future updates.

## Template updates

Full templates have independent immutable template versions in their user library. Import a new template version explicitly and instantiate it into a new project. Plugin updates never modify existing decks, references or imported template packages.
