from __future__ import annotations

BREAKING_CHANGES_HEADING = "Breaking changes"
BREAKING_CHANGES_EMOJI = "🚨"


TYPES: list[dict] = [
    dict(
        type="feat",
        description="A new feature",
        heading="New features",
        emoji="💫",
        bump="MINOR",
    ),
    # dict(
    #     type="security",
    #     description="A changeset fixing a security issue",
    #     heading="Security",
    #     emoji="🔒",
    #     aliases=["sec"],
    # ),
    dict(
        type="fix",
        description="A bug fix",
        heading="Bug fixes",
        emoji="🐛",
    ),
    dict(
        type="perf",
        description="A changeset improving performance",
        heading="Performance",
        emoji="📈",
        aliases=["performance"],
    ),
    dict(
        type="docs",
        description="Documentation only change",
        heading="Documentation",
        emoji="📖",
        aliases=["doc"],
    ),
    dict(
        type="build",
        description="Changes that affect the build system or external dependencies (ex: pip, docker, npm)",
        heading="Build",
        emoji="📦",
        aliases=["deps"],
    ),
    dict(
        type="style",
        description="Changes that do not affect the meaning of the code (white-space, formatting, …)",
        heading="Style",
        emoji="🎨",
        changelog=False,
    ),
    dict(
        type="test",
        description="Adding missing or correcting existing tests",
        heading="Testing",
        emoji="🚦",
        aliases=["tests"],
        changelog=False,
    ),
    dict(
        type="ci",
        description="Changes to CI configuration files and scripts",
        heading="Continous Integration",
        emoji="🛸",
        changelog=False,
    ),
    dict(
        type="refactor",
        description="A changeset neither fixing a bug nor adding a feature",
        heading="Refactorings",
        emoji="🔧",
        changelog=False,
    ),
    dict(
        type="i18n",
        description="A changeset related to languages and translations",
        heading="Internationalization",
        emoji="🌍",
        aliases=["locales", "l10n"],
    ),
    dict(
        type="release",
        description="A new release",
        heading="Release",
        emoji="🚀",
        aliases=["bump"],
        changelog=False,
    ),
    dict(
        type="chore",
        description="Changes not fitting in other categories",
        heading="Chores",
        emoji="🧹",
    ),
    dict(
        type="revert",
        description="Revert one or more commits",
        heading="Reverted",
        emoji="🔙",
        changelog=False,
    ),
    dict(
        type="wip",
        description="Work in progress",
        heading="Work in progress",
        emoji="🚧",
        changelog=False,
    ),
]
