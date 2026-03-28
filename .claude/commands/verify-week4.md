# /verify-week4

Use this command before considering `week4/` complete.

## Inputs
- Optional focus area in `$ARGUMENTS`, for example: `notes crud`, `validation`, or `writeup`.

## Verification Checklist
1. Review the affected backend routes, frontend flows, tests, and docs for the requested scope.
2. Run:
   - `make test`
   - `make lint`
3. Confirm `week4/docs/API.md` matches the implemented endpoints and payloads.
4. Confirm `week4/writeup.md` explains:
   - the automation design
   - how the automation was used on the starter app
   - the manual workflow vs automated workflow
5. Report one of:
   - `PASS`: all checks green
   - `BLOCKED`: exact failure and the file to inspect next

## Expected Output
- A short release-style verification report
- Any remaining gaps in tests, docs, or writeup
