# CodeAgent Specialist Reference

## Overview
`CodeAgent` is the specialist agent responsible for code generation, code analysis, code modification, compilation, test generation, test execution, error analysis, self-debugging, and structured output verification.

## Action Contract Protocol
`CodeAgent` accepts and produces structured Pydantic `CodeActionModel` contracts:
- `CREATE_FILE`: Creates a new file in the sandbox workspace.
- `UPDATE_FILE`: Updates an existing file and generates unified diff text.
- `READ_FILE`: Reads file content.
- `LIST_FILES`: Lists workspace files.
- `COMPILE`: Compiles C/C++ or other compiled entrypoints.
- `EXECUTE`: Executes code inside isolated sandbox.
- `RUN_TESTS`: Runs unit test suites.

## Self-Debugging Observation Loop
```
PLAN ──► WRITE CODE ──► COMPILE / RUN ──► OBSERVE STDOUT/STDERR
                                                 │
                             ┌───────────────────┴───────────────────┐
                             ▼                                       ▼
                       SUCCESS (Pass)                       ERROR (Compile/Runtime)
                             │                                       │
                             ▼                                       ▼
                     REVIEWER AGENT                         ANALYZE ERROR & FIX
                             │                                       │
                             ▼                                       ▼
                      DELIVER RESULT                       RETRY (up to 3 times)
```
- Maximum retries: `settings.CODE_MAX_RETRIES = 3`
- Every retry attempt is persisted in database and logged to event timeline.
