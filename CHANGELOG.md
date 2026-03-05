# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Documentation
- CI/CD workflows with GitHub Actions
- New `GoldMine` reference game with modular classes, orchestrator, and tests
- New generic `playing` module with `RandomPlayer` and `TerminalPlayer`
- New `arening` module with `GenericArena`, `TerminalArena`, composable limits,
  history recording, and `ArenaFactory`
- New stop-control behavior in arenas: stop conditions now raise
  `ArenaStoppedError` by default, with optional `raise_on_stop=False` fallback
- New thread timeout utility in `utilizing.threadinging` to run/interrupt player
  turns with exception propagation to arena main thread

[Unreleased]: https://github.com/jparisu/iarena/compare/v0.1.0...HEAD
