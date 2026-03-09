# Glossary

## Arena
Component that orchestrates a full match: collects moves from players, applies rules, and returns a final `ScoreBoard`.

## Rules
Abstract game logic contract (`iarena.gaming.Rules.Rules`) defining legal movements, state transitions, terminal conditions, and scoring.

## Movement
Action object (`iarena.gaming.Movement.Movement`) applied to a `Position` to produce a next state.

## Player
Strategy component (`iarena.playing.Player.Player`) that chooses a `Movement` from a `Position`.

## PlayerIndex
Typed integer (`iarena.playing.PlayerIndex.PlayerIndex`) identifying a player in a match.

## Position
Game state object (`iarena.gaming.Position.Position`) that knows the next player and the associated rules.

## Score
Typed numeric value (`iarena.scoring.Score.Score`) representing one player's result.

## ScoreBoard
Container (`iarena.scoring.ScoreBoard.ScoreBoard`) mapping each `PlayerIndex` to its `Score`.
