# Chore: Migrate Claude Authentication to AWS Bedrock

## Chore Description
Update all Claude/Anthropic authentication methods throughout the codebase to use AWS Bedrock environment variables instead of `ANTHROPIC_API_KEY`. This involves:
1. Updating environment variable templates to include Bedrock configuration
2. Modifying the Anthropic client initialization to use `AnthropicBedrock` client
3. Updating health checks to validate Bedrock credentials instead of API key
4. Updating Claude Code CLI invocation to pass Bedrock environment variables
5. Updating tests to mock Bedrock authentication

## Relevant Files
Use these files to resolve the chore:

- **`.env.sample`** - Root environment variable template. Needs Bedrock variables added (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `CLAUDE_CODE_USE_BEDROCK`). Currently has `ANTHROPIC_API_KEY`.
- **`app/server/.env.sample`** - Server environment variable template. Needs Bedrock variables for the LLM processor. Currently has `ANTHROPIC_API_KEY`.
- **`app/server/core/llm_processor.py`** - Contains `generate_sql_with_anthropic()` function that creates `Anthropic(api_key=api_key)` client. Must switch to `AnthropicBedrock` client.
- **`.claude/hooks/utils/llm/anth.py`** - Hook utility that uses `anthropic.Anthropic(api_key=api_key)`. Must switch to `AnthropicBedrock` client.
- **`adws/agent.py`** - Contains `get_claude_env()` function that passes `ANTHROPIC_API_KEY` to Claude Code subprocess. Must pass Bedrock env vars instead.
- **`adws/health_check.py`** - Contains `check_env_vars()` that validates `ANTHROPIC_API_KEY`. Must validate Bedrock credentials. Also `check_claude_code()` runs Claude Code which depends on the API key.
- **`app/server/tests/core/test_llm_processor.py`** - Contains tests that mock `Anthropic` class and `ANTHROPIC_API_KEY` env var. Must update to mock `AnthropicBedrock` and AWS credentials.
- **`README.md`** - Documents API key setup. Should mention Bedrock as an authentication option.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update Root Environment Variable Template
Update `.env.sample` to replace `ANTHROPIC_API_KEY` with Bedrock configuration:
- Remove or comment out `ANTHROPIC_API_KEY=`
- Add `AWS_ACCESS_KEY_ID=`
- Add `AWS_SECRET_ACCESS_KEY=`
- Add `AWS_SESSION_TOKEN=` (optional, for temporary credentials)
- Add `AWS_REGION=eu-west-3`
- Add `ANTHROPIC_MODEL=` (optional, for specifying model ARN)
- Add `CLAUDE_CODE_USE_BEDROCK=true`
- Update comments to explain Bedrock authentication

### Step 2: Update Server Environment Variable Template
Update `app/server/.env.sample` to add Bedrock configuration for the LLM processor:
- Add `AWS_ACCESS_KEY_ID=`
- Add `AWS_SECRET_ACCESS_KEY=`
- Add `AWS_SESSION_TOKEN=` (optional)
- Add `AWS_REGION=eu-west-3`
- Keep `OPENAI_API_KEY` as alternative provider
- Remove or comment out `ANTHROPIC_API_KEY`

### Step 3: Update LLM Processor for Bedrock
Modify `app/server/core/llm_processor.py`:
- Change import from `from anthropic import Anthropic` to `from anthropic import AnthropicBedrock`
- In `generate_sql_with_anthropic()`:
  - Replace API key check with AWS credentials check (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`)
  - Replace `Anthropic(api_key=api_key)` with:
    ```python
    client = AnthropicBedrock(
        aws_access_key=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        aws_region=os.environ.get("AWS_REGION", "eu-west-3"),
        aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
    )
    ```
  - Update model name from `claude-3-haiku-20240307` to a Bedrock-compatible model ID (e.g., `us.anthropic.claude-3-haiku-20240307-v1:0` or use env var `ANTHROPIC_MODEL`)
  - Update error message from "ANTHROPIC_API_KEY environment variable not set" to "AWS Bedrock credentials not set"
- In `generate_sql()`:
  - Replace `anthropic_key = os.environ.get("ANTHROPIC_API_KEY")` check with AWS credentials check

### Step 4: Update Claude Hooks Utility for Bedrock
Modify `.claude/hooks/utils/llm/anth.py`:
- Change import to use `AnthropicBedrock`
- In `prompt_llm()`:
  - Replace API key retrieval with AWS credentials retrieval
  - Replace `anthropic.Anthropic(api_key=api_key)` with `AnthropicBedrock(...)` client
  - Update model name to Bedrock-compatible model ID
  - Update error handling for missing AWS credentials

### Step 5: Update ADW Agent Environment Variables
Modify `adws/agent.py` in `get_claude_env()` function:
- Remove `"ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),`
- Add AWS Bedrock environment variables:
  ```python
  "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
  "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
  "AWS_SESSION_TOKEN": os.getenv("AWS_SESSION_TOKEN"),
  "AWS_REGION": os.getenv("AWS_REGION"),
  "CLAUDE_CODE_USE_BEDROCK": "true",
  "ANTHROPIC_MODEL": os.getenv("ANTHROPIC_MODEL"),
  ```
- Update comments to reflect Bedrock configuration

### Step 6: Update Health Check Script
Modify `adws/health_check.py`:
- In `check_env_vars()`:
  - Replace `"ANTHROPIC_API_KEY": "Anthropic API Key for Claude Code"` with:
    ```python
    "AWS_ACCESS_KEY_ID": "AWS Access Key ID for Bedrock",
    "AWS_SECRET_ACCESS_KEY": "AWS Secret Access Key for Bedrock",
    "AWS_REGION": "AWS Region for Bedrock (e.g., eu-west-3)",
    ```
  - Add `CLAUDE_CODE_USE_BEDROCK` to optional vars with note that it defaults to true
- In `run_health_check()`:
  - Update the condition `if os.getenv("ANTHROPIC_API_KEY"):` to check for AWS credentials instead
- Update any error messages that mention `ANTHROPIC_API_KEY`
- In `main()` next steps section, update the instruction from "Set ANTHROPIC_API_KEY" to "Set AWS Bedrock credentials"

### Step 7: Update Tests for Bedrock
Modify `app/server/tests/core/test_llm_processor.py`:
- Change mock decorator from `@patch('core.llm_processor.Anthropic')` to `@patch('core.llm_processor.AnthropicBedrock')`
- Update environment variable patches from `{'ANTHROPIC_API_KEY': 'test-key'}` to:
  ```python
  {
      'AWS_ACCESS_KEY_ID': 'test-key-id',
      'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
      'AWS_REGION': 'eu-west-3'
  }
  ```
- Update assertion messages that check for "ANTHROPIC_API_KEY environment variable not set" to check for AWS credentials error message
- Update `test_generate_sql_anthropic_fallback` and related tests to check for AWS credentials instead of `ANTHROPIC_API_KEY`

### Step 8: Update README Documentation
Update `README.md`:
- In Prerequisites section, change "Anthropic API key" to "AWS Bedrock access (or Anthropic API key)"
- In Environment Configuration section, add instructions for Bedrock setup:
  - Explain AWS credentials needed (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`)
  - Mention optional `AWS_SESSION_TOKEN` for temporary credentials
  - Reference the `CLAUDE_CODE_USE_BEDROCK=true` setting
- Keep OpenAI as an alternative option

### Step 9: Run Validation Commands
Execute all validation commands to ensure zero regressions.

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the chore is complete with zero regressions
- `cd app/server && uv run pytest tests/core/test_llm_processor.py -v` - Run LLM processor tests specifically to verify Bedrock authentication changes
- `uv run adws/health_check.py` - Run health check to verify Bedrock credential validation works
- `cd app/client && npm run build` - Verify frontend still builds (no breaking changes)

## Notes
- The `anthropic` Python SDK natively supports AWS Bedrock via the `AnthropicBedrock` class, so no additional dependencies are needed
- Bedrock model IDs differ from standard Anthropic model IDs. Use format like `us.anthropic.claude-3-haiku-20240307-v1:0` or ARN format
- For Claude Code CLI, setting `CLAUDE_CODE_USE_BEDROCK=true` environment variable enables Bedrock mode
- AWS credentials can come from environment variables, AWS credentials file, or IAM role (if running on AWS infrastructure)
- Consider adding support for both authentication methods (Bedrock and API key) with Bedrock as priority for flexibility
- The user already has Bedrock credentials in their `.env` file (`AWS_BEARER_TOKEN_BEDROCK`, `ANTHROPIC_MODEL`, `CLAUDE_CODE_USE_BEDROCK=true`, `AWS_REGION=eu-west-3`)
