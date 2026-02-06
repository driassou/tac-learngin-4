# Bug: Missing botocore Dependency for AWS Bedrock

## Bug Description
When making API requests that use the Anthropic Bedrock client, the server crashes with `ModuleNotFoundError: No module named 'botocore'`. The `AnthropicBedrock` client from the `anthropic` SDK requires `botocore` for AWS SigV4 authentication, but this dependency is not installed in the server's virtual environment.

**Symptoms:**
- Server starts successfully
- API queries fail with `No module named 'botocore'`
- Error occurs in `anthropic/lib/bedrock/_auth.py` when trying to import `SigV4Auth` from `botocore.auth`

**Expected behavior:** Anthropic Bedrock API calls should work correctly.

**Actual behavior:** API calls fail because `botocore` is not installed.

## Problem Statement
The `anthropic` SDK's `AnthropicBedrock` client has an implicit dependency on `botocore` (part of AWS SDK) for authentication, but this dependency is not declared in the server's `pyproject.toml`. When the code tries to use Bedrock authentication, it fails because `botocore` is missing.

## Solution Statement
Add `boto3` (which includes `botocore` as a dependency) to the server's `pyproject.toml` dependencies. This will ensure the AWS SDK components needed for Bedrock authentication are available.

## Steps to Reproduce
1. Run `bash scripts/start.sh`
2. Open `http://localhost:5173` in browser
3. Upload a data file
4. Submit a natural language query
5. Observe the error: `No module named 'botocore'`

## Root Cause Analysis
The root cause is a missing dependency:

1. The `anthropic` SDK provides `AnthropicBedrock` client for AWS Bedrock integration
2. This client uses AWS SigV4 authentication which requires `botocore`
3. The `anthropic` package lists `botocore` as an optional dependency (not installed by default)
4. The server's `pyproject.toml` doesn't include `boto3` or `botocore`
5. When `AnthropicBedrock` tries to authenticate, it fails to import `botocore`

## Relevant Files
Use these files to fix the bug:

- **`app/server/pyproject.toml`** - The project dependencies file that needs to include `boto3` to provide `botocore`

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add boto3 Dependency
- Open `app/server/pyproject.toml`
- Add `boto3` to the dependencies list
- Run `cd app/server && uv sync --all-extras` to install the new dependency

### Step 2: Run Validation Commands
- Execute the validation commands to confirm the fix works

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd app/server && uv add boto3` - Add boto3 dependency
- `cd app/server && uv sync --all-extras` - Sync dependencies
- `cd app/server && uv run pytest` - Run server tests to validate no regressions
- `cd app/server && uv run python -c "from botocore.auth import SigV4Auth; print('botocore installed')"` - Verify botocore is available

## Notes
- `boto3` automatically includes `botocore` as a dependency
- The `anthropic[bedrock]` extra could also be used, but adding `boto3` directly is more explicit
- No code changes required, only dependency addition
