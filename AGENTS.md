# Agent entry points

If the user asks to install or update Slidev Studio from this repository URL, read [INSTALL.md](INSTALL.md) and execute the path for the current host; do not begin plugin development or add duplicate global skills. Report actual installation/verification results. 用户要求从仓库安装或更新时，先读 INSTALL.md 并执行适合当前宿主的路径，报告实际验证结果。

For development: maintain canonical skills under plugins/slidev-studio/skills. Do not edit installed caches or maintain a second global copy. Read README.md and docs/UPDATING.md before release changes. Run the Python tests, synchronize the single version with scripts/release.py, and validate/build archives. Keep user reference decks, template libraries, generated projects, credentials and host-specific paths out of releases. Full imported templates need native reusable layouts plus real build/visual evidence; extracted metadata alone is a draft.
