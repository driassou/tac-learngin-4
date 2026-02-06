# Chore: Validate Full Bedrock Support and Architecture Review

## Chore Description
Conduct a comprehensive validation and architectural review of the AWS Bedrock authentication implementation across the entire codebase. This chore ensures that all Claude/Anthropic integrations properly support Bedrock authentication, verifies the architecture is sound and consistent, identifies any gaps or issues, and validates that both the ADW system (Claude Code CLI) and the web application (Natural Language SQL) work correctly with Bedrock credentials.

The review will cover:
1. **Consistency validation** - Ensure all Bedrock authentication implementations follow the same patterns
2. **Architecture assessment** - Verify the design decisions are appropriate and maintainable
3. **Credential flow verification** - Confirm environment variables are correctly propagated
4. **Error handling review** - Check that credential failures are properly handled
5. **Documentation completeness** - Ensure setup instructions are clear and accurate
6. **Testing coverage** - Verify tests properly mock Bedrock authentication
7. **Feature parity** - Confirm both authentication methods (API key fallback if needed) work correctly

## Relevant Files
Use these files to validate and review the Bedrock implementation:

### ADW System Files (Claude Code CLI Integration)
- **`adws/agent.py`** - Core agent that invokes Claude Code CLI. Contains `get_claude_env()` which passes `AWS_BEARER_TOKEN_BEDROCK`, `AWS_REGION`, `CLAUDE_CODE_USE_BEDROCK`, and `ANTHROPIC_MODEL` to the Claude Code subprocess. This is critical for ADW workflows to authenticate with Bedrock.

- **`adws/health_check.py`** - Health check script that validates environment setup. Checks for `AWS_BEARER_TOKEN_BEDROCK` and `AWS_REGION` as required variables. Tests Claude Code CLI functionality with a simple prompt to verify Bedrock authentication works end-to-end.

- **`adws/adw_plan_build.py`** - Main ADW workflow orchestrator. Relies on `agent.py` for Claude Code invocation with Bedrock credentials. Documentation mentions required Bedrock environment variables.

- **`adws/trigger_webhook.py`** - Webhook server that launches ADW workflows. Passes environment variables to background processes that run `adw_plan_build.py`.

- **`adws/trigger_cron.py`** - Cron-based ADW trigger. Similar to webhook, passes environment to ADW workflows.

### Web Application Files (Python SDK Integration)
- **`app/server/core/llm_processor.py`** - LLM integration for SQL generation. Contains `generate_sql_with_anthropic()` which creates `AnthropicBedrock` client with explicit AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`). Uses boto3-style authentication (different from Claude Code CLI's bearer token approach). Includes `has_bedrock_credentials()` helper function.

- **`app/server/tests/core/test_llm_processor.py`** - Comprehensive test suite for LLM processor. Mocks `AnthropicBedrock` client and tests credential validation, error handling, model selection, and provider fallback logic. Uses `BEDROCK_TEST_ENV` constant for consistent test credentials.

- **`app/server/pyproject.toml`** - Python dependencies. Includes `anthropic>=0.54.0` for AnthropicBedrock support and `boto3>=1.42.43` for AWS SDK (required by AnthropicBedrock).

- **`app/client/src/types.d.ts`** - TypeScript types for frontend. Defines `QueryRequest` with `llm_provider: "openai" | "anthropic"` to support provider selection.

### Claude Hooks (Git Hooks Integration)
- **`.claude/hooks/utils/llm/anth.py`** - Hook utility for LLM prompting. Uses `AnthropicBedrock` client with boto3's default credential chain (no explicit credentials passed). Uses `AWS_REGION` environment variable. Note: This differs from the explicit credential approach in `llm_processor.py`.

### Environment Configuration
- **`.env.sample`** - Root environment template for ADW system. Documents `AWS_BEARER_TOKEN_BEDROCK`, `AWS_REGION`, `ANTHROPIC_MODEL`, and `CLAUDE_CODE_USE_BEDROCK=true` for Claude Code CLI authentication.

- **`app/server/.env.sample`** - Server environment template for web application. Documents `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` for boto3-based AnthropicBedrock authentication. Also includes `OPENAI_API_KEY` as alternative provider.

### Documentation
- **`README.md`** - Root project documentation. Documents Bedrock setup for web application with AWS credentials via boto3's default credential chain.

- **`adws/README.md`** - ADW system documentation. Documents environment variables including Bedrock configuration for Claude Code CLI.

### Previous Implementation Plans
- **`specs/bedrock-authentication-migration.md`** - Original migration plan from API key to Bedrock authentication
- **`specs/fix-bedrock-credentials-not-found.md`** - Bug fix for boto3 credential resolution
- **`specs/fix-botocore-missing-dependency.md`** - Bug fix for missing boto3/botocore dependency

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Review Authentication Architecture
Analyze the two different Bedrock authentication approaches used in the codebase and verify they are appropriate for their contexts:
- **Claude Code CLI approach** (`adws/agent.py`): Uses `AWS_BEARER_TOKEN_BEDROCK` - a bearer token specifically for Claude Code CLI
- **Python SDK approach** (`app/server/core/llm_processor.py`): Uses standard AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) via boto3
- **Hooks approach** (`.claude/hooks/utils/llm/anth.py`): Uses boto3 default credential chain (env vars, ~/.aws/credentials, IAM role)
- Document why these approaches are necessary and whether they are optimal
- Identify any potential consolidation opportunities or issues

### Step 2: Validate Environment Variable Consistency
Check that environment variables are correctly documented and used across all components:
- Compare `.env.sample` vs `app/server/.env.sample` - ensure no conflicting variable names
- Verify `ANTHROPIC_MODEL` is used consistently (both ADW and server support it)
- Check that `AWS_REGION` has consistent defaults (currently "eu-west-3")
- Ensure optional vs required variables are clearly distinguished
- Validate that environment variables are actually loaded where needed (check `load_dotenv()` calls)

### Step 3: Review Credential Flow Through ADW System
Trace how Bedrock credentials flow through the ADW workflow:
- Start from `adws/trigger_webhook.py` or `adws/trigger_cron.py`
- Follow to `adws/adw_plan_build.py`
- Trace to `adws/agent.py` and `get_claude_env()`
- Verify subprocess environment passing is correct
- Check for any credential leakage in logs or error messages
- Confirm `CLAUDE_CODE_USE_BEDROCK=true` is set in subprocess environment

### Step 4: Review Error Handling and Validation
Examine error handling for missing or invalid credentials:
- Check `adws/health_check.py` validation logic - does it catch all credential issues?
- Review `app/server/core/llm_processor.py` error messages - are they clear and actionable?
- Verify test coverage for credential validation failures
- Check if error messages expose sensitive information
- Ensure graceful fallback when credentials are missing (if applicable)

### Step 5: Validate Test Coverage
Review test suite for Bedrock authentication:
- Examine `app/server/tests/core/test_llm_processor.py`
- Verify all Bedrock credential scenarios are tested (valid, missing, invalid)
- Check that mocks properly simulate `AnthropicBedrock` behavior
- Ensure test environment variables don't conflict with user's actual credentials
- Verify tests use `clear=True` in `patch.dict` where appropriate to avoid credential leakage
- Check if there are any untested edge cases

### Step 6: Review Documentation Accuracy
Validate that all documentation matches the actual implementation:
- Check `README.md` - is Bedrock setup documented correctly?
- Review `adws/README.md` - are environment variables accurate?
- Verify `.env.sample` files have correct comments and examples
- Check previous spec files for any unimplemented recommendations
- Ensure model ID format is documented (e.g., `us.anthropic.claude-3-haiku-20240307-v1:0`)
- Verify distinction between Claude Code CLI bearer token and boto3 credentials is explained

### Step 7: Check Hooks Implementation
Review the `.claude/hooks/utils/llm/anth.py` implementation:
- Verify it uses boto3 default credential chain correctly
- Check if it should use explicit credentials like `llm_processor.py` does
- Validate error handling when credentials are unavailable
- Consider if this needs to support `AWS_BEARER_TOKEN_BEDROCK` for consistency
- Review if hooks might fail silently and how that impacts user experience

### Step 8: Verify Feature Parity
Ensure both Claude Code CLI and web application support the same Bedrock features:
- Model selection via `ANTHROPIC_MODEL` environment variable
- Region configuration via `AWS_REGION`
- Error handling and messaging consistency
- Credential validation approach
- Check if both support cross-region inference profiles or custom model ARNs

### Step 9: Identify Architecture Issues and Improvements
Document any architectural concerns discovered:
- Credential duplication (bearer token vs AWS credentials)
- Inconsistent approaches between components
- Missing abstractions or helper functions
- Security concerns (credential exposure, logging)
- Maintainability issues (scattered authentication logic)
- Potential for configuration errors

### Step 10: Create Summary Report
Compile findings into a structured report:
- List all components using Bedrock authentication
- Document the authentication approach each component uses
- Highlight any inconsistencies or issues found
- Provide recommendations for improvements (if any)
- Confirm overall architecture is sound or suggest refactoring
- Note any missing tests or documentation

### Step 11: Run Validation Commands
Execute all validation commands to ensure zero regressions and verify Bedrock integration works.

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd app/server && uv run pytest tests/core/test_llm_processor.py -v` - Verify all LLM processor tests pass, including Bedrock authentication tests
- `cd app/server && uv run pytest -v` - Run full server test suite to ensure no regressions
- `cd app/server && uv run python -c "from anthropic import AnthropicBedrock; print('AnthropicBedrock import successful')"` - Verify AnthropicBedrock is available
- `cd app/server && uv run python -c "import boto3; print('boto3 version:', boto3.__version__)"` - Verify boto3 is installed
- `uv run adws/health_check.py` - Run ADW health check to validate environment configuration (may fail if credentials not set, which is expected)
- `cd app/client && npm run build` - Verify frontend builds without errors

## Notes
- The codebase uses **two different Bedrock authentication methods**:
  1. `AWS_BEARER_TOKEN_BEDROCK` for Claude Code CLI (ADW system)
  2. Standard AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) for Python SDK (web application)

- This is **by design** because:
  - Claude Code CLI has native support for bearer tokens via `CLAUDE_CODE_USE_BEDROCK=true`
  - The `anthropic` Python SDK's `AnthropicBedrock` class uses boto3, which requires standard AWS credentials

- The hooks utility (`.claude/hooks/utils/llm/anth.py`) uses boto3's default credential chain, which is flexible but may fail silently if credentials aren't configured

- Model IDs differ between standard Anthropic API and Bedrock:
  - Standard: `claude-3-haiku-20240307`
  - Bedrock: `us.anthropic.claude-3-haiku-20240307-v1:0`

- The previous bug fixes successfully addressed:
  - Missing `boto3` dependency → Added to `pyproject.toml`
  - Credentials not found → Updated to explicit credential passing in `llm_processor.py`

- Both environment sample files are well-documented and clear about which credentials are needed where

- The `generate_sql()` function in `llm_processor.py` implements smart provider selection:
  1. Priority to OpenAI if `OPENAI_API_KEY` exists
  2. Falls back to Bedrock if AWS credentials exist
  3. Uses request preference if neither or both are available

- Tests properly mock `AnthropicBedrock` and use `clear=True` to avoid credential pollution

- Health check validates Claude Code CLI authentication by running a simple test prompt

- Consider if the project needs a unified authentication abstraction layer in the future
