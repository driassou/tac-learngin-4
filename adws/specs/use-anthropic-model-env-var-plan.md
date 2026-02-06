# Chore: Use ANTHROPIC_MODEL Environment Variable for Model Configuration

## Chore Description
Ensure that the ANTHROPIC_MODEL environment variable is used consistently throughout the codebase wherever a model is specified. Currently, the code has hardcoded model values ("sonnet", "opus") in multiple places. This chore will:

1. Update all hardcoded model references to use the ANTHROPIC_MODEL environment variable
2. Provide sensible defaults when ANTHROPIC_MODEL is not set
3. Ensure the model configuration is centralized and configurable
4. Update data types to support flexible model specifications

The ANTHROPIC_MODEL environment variable should contain the full Bedrock model ARN (e.g., "us.anthropic.claude-3-5-haiku-20241022-v1:0" or "eu.anthropic.claude-sonnet-4-5-20250929-v1:0") and be used instead of the simplified "sonnet"/"opus" literals.

## Relevant Files
Use these files to resolve the chore:

- **adws/adw_plan_build.py** (Lines 126, 162, 188, 218, 250, 283, 310) - Contains 7 hardcoded `model="sonnet"` references in various agent template requests. These need to be updated to use ANTHROPIC_MODEL from the environment.

- **adws/data_types.py** (Lines 109, 129) - Defines model types as `Literal["sonnet", "opus"]` which restricts the model values. These type definitions need to be updated to accept any string value to support full Bedrock model ARNs.

- **adws/agent.py** (Line 108, 259) - Reads ANTHROPIC_MODEL from environment and passes it to Claude Code CLI. This file already handles ANTHROPIC_MODEL correctly, but we should verify it's being used properly.

- **adws/health_check.py** (Line 171) - Uses ANTHROPIC_MODEL with a default value of "us.anthropic.claude-3-5-haiku-20241022-v1:0". This is a good reference implementation.

- **README.md** (Lines 222-224) - Documentation mentions editing agent.py to change model. This documentation needs to be updated to reference the ANTHROPIC_MODEL environment variable instead.

### New Files
No new files need to be created for this chore.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Update data_types.py to Support Flexible Model Specification
- Change `model: Literal["sonnet", "opus"]` to `model: str` in `AgentPromptRequest` (line 109)
- Change `model: Literal["sonnet", "opus"]` to `model: str` in `AgentTemplateRequest` (line 129)
- Update default values from `"opus"` and `"sonnet"` to use a sensible Bedrock model ARN
- This removes the restriction on model values and allows full Bedrock model ARNs

### Step 2: Create Helper Function for Model Resolution
- Add a helper function `get_default_model()` in `adws/utils.py` that:
  - Reads ANTHROPIC_MODEL from environment
  - Returns a default Bedrock model ARN if not set (e.g., "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
  - Provides a single source of truth for model configuration
- This centralizes the model resolution logic

### Step 3: Update adw_plan_build.py to Use Environment Variable
- Import the helper function from utils.py
- Replace all 7 hardcoded `model="sonnet"` occurrences with `model=get_default_model()`
- This affects the following functions:
  - `classify_issue()` - line 126
  - `build_plan()` - line 162
  - `get_plan_file()` - line 188
  - `implement_plan()` - line 218
  - `git_branch()` - line 250
  - `git_commit()` - line 283
  - `pull_request()` - line 310

### Step 4: Update health_check.py for Consistency
- Import the helper function from utils.py
- Replace the hardcoded default in line 171 with a call to `get_default_model()`
- This ensures consistent model defaults across the codebase

### Step 5: Update README.md Documentation
- Update the "Model Selection" section (lines 222-224) to explain the ANTHROPIC_MODEL environment variable
- Remove references to editing agent.py directly
- Add documentation about setting ANTHROPIC_MODEL in the environment
- Include examples of valid Bedrock model ARNs
- Update the "Set Environment Variables" section to include ANTHROPIC_MODEL as an optional variable

### Step 6: Run Validation Commands
- Execute all validation commands to ensure no regressions
- Verify that the changes work correctly with different model configurations

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd /workspace/projects/Learning/tac-4/adws && python3 -m py_compile adws/data_types.py` - Validate data_types.py syntax
- `cd /workspace/projects/Learning/tac-4/adws && python3 -m py_compile adws/utils.py` - Validate utils.py syntax
- `cd /workspace/projects/Learning/tac-4/adws && python3 -m py_compile adws/adw_plan_build.py` - Validate adw_plan_build.py syntax
- `cd /workspace/projects/Learning/tac-4/adws && python3 -m py_compile adws/health_check.py` - Validate health_check.py syntax
- `cd /workspace/projects/Learning/tac-4/adws && python3 -m py_compile adws/agent.py` - Validate agent.py syntax
- `cd /workspace/projects/Learning/tac-4/adws && python3 -c "from data_types import AgentPromptRequest, AgentTemplateRequest; print('Data types import successfully')"` - Validate data types can be imported
- `cd /workspace/projects/Learning/tac-4/adws && python3 -c "from utils import get_default_model; print('Model:', get_default_model())"` - Validate the helper function works

## Notes
- The ANTHROPIC_MODEL environment variable is already being read by agent.py (line 108) and passed to the Claude Code CLI execution environment
- health_check.py already demonstrates the correct pattern for using ANTHROPIC_MODEL with a default fallback
- The change from Literal["sonnet", "opus"] to str is necessary because Bedrock model ARNs are full strings like "us.anthropic.claude-3-5-haiku-20241022-v1:0", not just "sonnet" or "opus"
- The helper function in utils.py will provide a single source of truth for model configuration and make future changes easier
- This change makes the system more flexible and allows users to specify any Bedrock model via environment variable
- After this chore is complete, users can control which model is used by setting ANTHROPIC_MODEL in their .env file, without needing to modify code
