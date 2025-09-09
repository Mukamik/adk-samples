# Pricing Predictor

This agent functions as an automated cost-estimation layer specifically designed to predict and track the approximate costs of agentic workflows that use Large Language Models (LLMs). Its primary role is to bring financial transparency to agent development by systematically analyzing LLM API calls and applying a detailed pricing model to produce a report on projected costs.

## Overview
This agent evaluates and predicts the costs of agentic workflows that use LLMs. Its primary purpose is to serve as an automated cost-prediction layer, analyzing LLM usage against a configurable pricing model to enhance budget predictability.

*   Orchestrates a sequence of sub-agents to execute a complete, multi-modal workflow.
*   Inspects the `usage_metadata` from each LLM call made by the sub-agents.
*   Calculates the total cost based on a detailed, tiered pricing model that distinguishes between input and output tokens.
*   Produces a clear breakdown listing the total input/output tokens and the final estimated cost.

This sample agent enables a user to run a multi-step, multi-modal workflow and receive a cost estimation for the entire process.

## Agent Details

The key features of the Pricing Predictor include:

| Feature | Description |
| --- | --- |
| **Interaction Type** | Workflow |
| **Complexity**  | Easy |
| **Agent Type**  | Multi Agent |
| **Components**  | None |
| **Vertical**  | Horizontal |

### Agent architecture:

The `root_agent` is a custom `PricingSequentialAgent` that acts as an orchestrator. It takes a user's request (a video file path) and manages a workflow by calling two specialized sub-agents in sequence. After the workflow is complete, it uses the `PricingEngine` to calculate the total cost.

<img src="https://storage.googleapis.com/gemini-hosted-assets/adk/pricing_predictor_architecture.png" alt="Pricing Predictor Architecture" width="800"/>

## Setup and Installation

1.  **Prerequisites**

    *   Python 3.10+
    *   Poetry
        *   For dependency management and packaging. Please follow the
            instructions on the official
            [Poetry website](https://python-poetry.org/docs/) for installation.
    *   Google ADK
        *   For running the agent using the `adk` command-line tool.
        ```bash
        pip install google-adk
        ```
    *   A project on Google Cloud Platform
    *   Google Cloud CLI
        *   For installation, please follow the instruction on the official
            [Google Cloud website](https://cloud.google.com/sdk/docs/install).

2.  **Installation**

    ```bash
    # Navigate to the sample directory.
    # From the root of the adk-samples repository:
    cd python/agents/pricing-predictor
    # Install the package and dependencies.
    poetry install
    ```

3.  **Configuration**

    *   Set up Google Cloud credentials.

        *   You may set the following environment variables in your shell, or in
            a `.env` file instead.

        ```bash
        export GOOGLE_GENAI_USE_VERTEXAI=true
        export GOOGLE_CLOUD_PROJECT=<your-project-id>
        export GOOGLE_CLOUD_LOCATION=<your-project-location>
        ```

    *   Authenticate your GCloud account.

        ```bash
        gcloud auth application-default login
        gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
        ```

## Running the Agent

**Using `adk`**

The ADK CLI provides a convenient way to bring up agents locally and interact with them.

On a web interface:
```bash
# From the python/agents/pricing-predictor directory:
adk web
```

The command will start a web server on your machine and print the URL. You may open the URL, select an agent from the "Select App" dropdown in the top-left menu, and the UI will appear.

You can choose between two agents:
1.  **Pricing Predictor**: The main workflow.
2.  **View Pricing Models**: A simple agent to display the current pricing data.

For the **Pricing Predictor**, you will need to provide:

*   `prompt`: The question you want to ask about the video (e.g., "is there a dog in this video?", "what color is the car?").
*   `video_file_path`: The **absolute path** to a video file on your local machine.

### Example Interaction

Below is an example interaction with the Pricing Predictor. Note that the exact output of the agent may be different every time.

```
user: 
video_file_path: /Users/me/Desktop/cat_video.mp4

[pricing_predictor]: 
Video Analysis Result: A fluffy white cat with blue eyes is seen playing with a red ball of yarn.
Audio Analysis Result: A faint meow is heard in the background audio.

--- Pricing Summary ---
Model: models/gemini-2.5-pro
Total Input Tokens: 250
Total Output Tokens: 75
Total Tokens: 325
Total Estimated Cost: $0.000594
```

## Running Tests

For running tests, first install the dev dependencies:

```bash
# From the python/agents/pricing-predictor directory:
poetry install --with dev
```

Then the tests can be run from the `pricing-predictor` directory using the `pytest` module. The test will make real API calls and may incur costs.

```bash
python3 -m pytest
```

## Customization

The Pricing Predictor can be customized to better suit your requirements. For example:

1.  **Substitute the Agent Workflow:** Modify the `sub_agents` list in `pricing_predictor/agent.py` to call your own sequence of agents.
2.  **Customize Pricing Models:** Modify the `pricing_predictor/pricing_models.json` file to define pricing for different models or to add your own tiered pricing based on prompt size.
3.  **Enhance the Orchestrator:** The `PricingSequentialAgent` in `orchestrator.py` can be extended to handle more complex logic, such as passing different media types between steps or adding conditional logic.

## Disclaimer

This agent sample is provided for illustrative purposes only and is not intended for production use. It serves as a basic example of an agent and a foundational starting point for individuals or teams to develop their own agents.

This sample has not been rigorously tested, may contain bugs or limitations, and does not include features or optimizations typically required for a production environment. Users are solely responsible for any further development, testing, security hardening, and deployment of agents based on this sample.
