# Research & Analysis Documentation

This directory contains the assets used for the systematic evaluation of the language models used in the chatbot application.

## `analysis_script.py`

This file is a Python script designed to be run in a Jupyter-compatible environment (like VS Code's Notebook editor or Google Colab). It contains the code and analysis for a performance comparison between different Ollama models.

### Purpose

The primary goal of this analysis is to satisfy the "Research & Analysis" section of the project rubric. It provides a methodical and data-driven approach to model selection, moving beyond subjective "feel" to objective metrics.

### Methodology

The script performs a simple but effective experiment:

1.  **Models Tested:** `gemma3:8b` and `qwen3:8b`.
2.  **Endpoint Tested:** The simple, non-agentic `/api/chat` endpoint.
3.  **Metrics Collected:**
    *   **Latency:** The time from sending a request to receiving a complete response. This is a direct measure of the model's speed and its impact on user experience.
    *   **Success Rate:** A simple binary check to ensure the model returned a non-empty response.

### How to Run the Experiment

1.  **Start the Backend Server:** Before running the analysis, you must have the main application's backend server running.
    ```bash
    make run
    ```
2.  **Open the Script as a Notebook:** Open the `research/analysis_script.py` file in a compatible editor like Visual Studio Code. The editor should automatically recognize the `# %%` cell markers and render it as a Jupyter Notebook.
3.  **Run All Cells:** Execute all the cells in the notebook from top to bottom. The script will:
    *   Install its own dependencies (`httpx`, `pandas`, etc.).
    *   Send a series of predefined questions to the running server.
    *   Collect the latency and success data for each model.
    *   Generate plots to visualize the results.

### Interpreting the Results

The script generates two key visualizations:

1.  **Model Latency by Question:** This bar chart shows how long each model took to answer each question. Lower bars are better, indicating a faster response.
2.  **Overall Success Rate per Model:** This bar chart shows the percentage of questions each model successfully answered.

Use these charts to draw a conclusion about which model provides the best performance for the simple chat use case. The "Conclusion" section at the end of the notebook is pre-filled with a hypothetical analysis that you should edit to reflect the actual results you observe.
