#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "anthropic",
#     "python-dotenv",
# ]
# ///

import os
import sys
from dotenv import load_dotenv

# Default Bedrock model ID for Claude
DEFAULT_BEDROCK_MODEL = "us.anthropic.claude-3-5-haiku-20241022-v1:0"


def prompt_llm(prompt_text):
    """
    Base Anthropic LLM prompting method using fastest model via AWS Bedrock.
    Uses boto3's default credential chain for authentication.

    Args:
        prompt_text (str): The prompt to send to the model

    Returns:
        str: The model's response text, or None if error
    """
    load_dotenv()

    aws_region = os.getenv("AWS_REGION", "eu-west-3")

    try:
        from anthropic import AnthropicBedrock

        # Use boto3's default credential chain (env vars, ~/.aws/credentials, IAM role)
        client = AnthropicBedrock(aws_region=aws_region)

        # Get model from environment or use default
        model = os.getenv("ANTHROPIC_MODEL", DEFAULT_BEDROCK_MODEL)

        message = client.messages.create(
            model=model,
            max_tokens=100,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt_text}],
        )

        return message.content[0].text.strip()

    except Exception:
        return None


def generate_completion_message():
    """
    Generate a completion message using Anthropic LLM.

    Returns:
        str: A natural language completion message, or None if error
    """
    engineer_name = os.getenv("ENGINEER_NAME", "").strip()

    if engineer_name:
        name_instruction = f"Sometimes (about 30% of the time) include the engineer's name '{engineer_name}' in a natural way."
        examples = f"""Examples of the style:
- Standard: "Work complete!", "All done!", "Task finished!", "Ready for your next move!"
- Personalized: "{engineer_name}, all set!", "Ready for you, {engineer_name}!", "Complete, {engineer_name}!", "{engineer_name}, we're done!" """
    else:
        name_instruction = ""
        examples = """Examples of the style: "Work complete!", "All done!", "Task finished!", "Ready for your next move!" """

    prompt = f"""Generate a short, friendly completion message for when an AI coding assistant finishes a task.

Requirements:
- Keep it under 10 words
- Make it positive and future focused
- Use natural, conversational language
- Focus on completion/readiness
- Do NOT include quotes, formatting, or explanations
- Return ONLY the completion message text
{name_instruction}

{examples}

Generate ONE completion message:"""

    response = prompt_llm(prompt)

    # Clean up response - remove quotes and extra formatting
    if response:
        response = response.strip().strip('"').strip("'").strip()
        # Take first line if multiple lines
        response = response.split("\n")[0].strip()

    return response


def main():
    """Command line interface for testing."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--completion":
            message = generate_completion_message()
            if message:
                print(message)
            else:
                print("Error generating completion message")
        else:
            prompt_text = " ".join(sys.argv[1:])
            response = prompt_llm(prompt_text)
            if response:
                print(response)
            else:
                print("Error calling Anthropic API via Bedrock")
    else:
        print("Usage: ./anth.py 'your prompt here' or ./anth.py --completion")


if __name__ == "__main__":
    main()
