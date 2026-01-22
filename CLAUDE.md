# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This repository is a testing environment for comparing **oh-my-claudecode** plugin effectiveness. The same PRD document is used to test implementation with and without the plugin, enabling direct comparison and analysis.

## Directory Structure Rules

```
/docs/          - Reference documents (READ-ONLY during implementation)
  PRD.md        - Product Requirements Document for Formula Checker
  pythonWAI_README.md - WAI module documentation

/workplace/     - Implementation test folders
  with-omc/     - Implementation WITH oh-my-claudecode plugin
  without-omc/  - Implementation WITHOUT oh-my-claudecode plugin
```

## Critical Rules

1. **Never modify files in `/docs/`** - These are reference documents shared across all tests
2. **Each test must be isolated** - Create separate folders under `/workplace/` for each test run
3. **Follow PRD strictly** - Implementation must align with `docs/PRD.md` specifications
4. **Use WAI module conventions** - Follow patterns documented in `docs/pythonWAI_README.md`

## Implementation Context (from PRD)

Building a **Formula Checker** tool for validating Python-based calculation scripts (WAI module):
- Syntax validation for individual calculation scripts
- Integration testing with `exec()` based script composition
- Unity-independent calculation result reproduction

### Key Technical Requirements
- Python 3.12+
- Must handle three script types: Process, Structure, Equipment
- Required functions per script type:
  - **Structure**: `forward_calculate`, `reverse_calculate`, `level_calculate`
  - **Equipment**: `forward_calculate`
  - **Process**: No required functions (script form)

### WAI Container Types
- DCN (Design Conditions), DCR (Design Criteria), DCP (Design Parameters)
- DSP (Structure Params), DEP (Equipment Params)
- STC (Structure), EQP (Equipment), STD (Standard), INF (Info)

## Test Execution Notes

When starting a new test:
1. Create a new timestamped folder under `/workplace/with-omc/` or `/workplace/without-omc/`
2. Reference `/docs/PRD.md` for requirements
3. Reference `/docs/pythonWAI_README.md` for WAI module API
4. Document any deviations or decisions made during implementation

## Token Usage Tracking

For comparing plugin efficiency, track token usage for each test:

### During Session
- Use `/cost` command to check current session token usage

### After Session
- Record the final token count shown at session end
- Save to `workplace/{test-folder}/metrics.md`:
  ```
  ## Test Metrics
  - Date: YYYY-MM-DD
  - Plugin: with-omc / without-omc
  - Input tokens: XXX
  - Output tokens: XXX
  - Total tokens: XXX
  - Task completion: Yes/No
  - Notes: [any observations]
  ```

### Comparison Template
Create `workplace/comparison.md` to aggregate results across tests
