

import openai
import time
import sys
import fitz  # PyMuPDF
import tiktoken
import os

def call_assistant_with_file(api_key,chunk):
    # Set the OpenAI API key
    openai.api_key = api_key
    
    # Create a new thread
    thread = openai.beta.threads.create()

        # Add a message from the user
    message = openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=chunk
        )

        # Create a run with the assistant
    run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id="asst_e4AK3QNJsqDWCU5tDjVioqsv"
        )

        # Retrieve the run's current state
    while True:
                run = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run.status == "completed":
                    break
                elif run.status == "failed":
                    raise Exception("The run failed to complete successfully.")
                # Wait for a short period before polling again
                time.sleep(2)

        # Retrieve and print messages from the thread
    messages = openai.beta.threads.messages.list(
            thread_id=thread.id
        )
        
    
    return messages.data[0].content[0].text.value