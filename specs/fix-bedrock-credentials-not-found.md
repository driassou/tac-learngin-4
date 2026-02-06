# Bug: AWS Bedrock Credentials Not Found in Server

## Bug Description
When making natural language queries in the web application, the server fails with `RuntimeError: could not resolve credentials from session`. The `AnthropicBedrock` client is using boto3's default credential chain but no AWS credentials are configured in the server's environment.

**Symptoms:**
- Server starts successfully
- Schema retrieval works
- API queries fail with "could not resolve credentials from session"
- Error occurs in `anthropic/lib/bedrock/_auth.py` when trying to get AWS credentials

**Expected behavior:** Anthropic Bedrock API calls should authenticate successfully.

**Actual behavior:** API calls fail because boto3 cannot find AWS credentials in its default credential chain.

## Problem Statement
The `AnthropicBedrock` client in `llm_processor.py` is configured to use boto3's default credential chain (`AnthropicBedrock(aws_region=aws_region)`), but the server environment doesn't have AWS credentials configured. The user has `AWS_BEARER_TOKEN_BEDROCK` in the root `.env` (for Claude Code CLI), but the `AnthropicBedrock` Python SDK requires standard AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

## Solution Statement
Update `llm_processor.py` to explicitly read AWS credentials from environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) and pass them to the `AnthropicBedrock` client. Also update `app/server/.env.sample` to document these required variables.

## Steps to Reproduce
1. Run `bash scripts/start.sh`
2. Open `http://localhost:5173` in browser
3. Upload a data file (e.g., sample users)
4. Submit a natural language query like "show all users"
5. Observe the error: "could not resolve credentials from session"

## Root Cause Analysis
The root cause is a mismatch between authentication methods:

1. The root `.env` uses `AWS_BEARER_TOKEN_BEDROCK` for Claude Code CLI (which supports this)
2. The `AnthropicBedrock` Python SDK requires standard AWS credentials via boto3
3. The current `llm_processor.py` uses `AnthropicBedrock(aws_region=aws_region)` which relies on boto3's default credential chain
4. No AWS credentials are available in the server's environment (no `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, no `~/.aws/credentials`, no IAM role)

## Relevant Files
Use these files to fix the bug:

- **`app/server/core/llm_processor.py`** - Contains the `AnthropicBedrock` client initialization that needs to explicitly use AWS credentials from environment variables
- **`app/server/.env.sample`** - Needs to document `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as required for Bedrock

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update llm_processor.py to Use Explicit Credentials
- Modify `generate_sql_with_anthropic()` to read `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from environment
- Pass these credentials explicitly to `AnthropicBedrock()` constructor
- Update `has_bedrock_credentials()` to check for `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (not just `AWS_REGION`)

### Step 2: Update Server Environment Sample
- Update `app/server/.env.sample` to include `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` placeholders
- Add clear documentation that these are required for Bedrock

### Step 3: Update Tests
- Update tests in `test_llm_processor.py` to include `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the test environment

### Step 4: Run Validation Commands
- Execute the validation commands to confirm the fix works

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate no regressions

## Notes
- The `AnthropicBedrock` SDK uses boto3 for AWS authentication, which requires standard AWS credentials
- `AWS_BEARER_TOKEN_BEDROCK` is only supported by Claude Code CLI, not the Python SDK
- Users need to set up both authentication methods:
  - `AWS_BEARER_TOKEN_BEDROCK` in root `.env` for Claude Code CLI / ADW
  - `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in `app/server/.env` for the web application
- If users don't have AWS credentials, they should use `OPENAI_API_KEY` instead
