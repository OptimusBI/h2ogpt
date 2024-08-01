import os
import sys

sys.path.append('openai_server')
from openai_server.backend_utils import convert_messages_to_structure, structure_to_messages, \
    concatenate_assistant_messages


def test_conversion():
    # Example usage
    messages = [
        {"role": "user", "content": "How does the weather look today?"},
        {"role": "assistant", "content": "The weather is sunny and warm."},
        {"role": "user", "content": "What about tomorrow?"},
        {"role": "assistant", "content": "It's expected to rain tomorrow."}
    ]

    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == (None, None, [('How does the weather look today?', 'The weather is sunny and warm.'),
                                                ('What about tomorrow?', "It's expected to rain tomorrow.")], [])

    messages = [{'role': 'user', 'content': 'What is your name?'},
                {'role': 'assistant', 'content': 'My name is Bob.'},
                {'role': 'user', 'content': 'What did I just ask?'},
                ]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == ('What did I just ask?', None, [('What is your name?', 'My name is Bob.')], [])

    messages = []
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == (None, None, [], [])

    system_prompt = """You are a helpful assistant and have been created by H2O.ai. Never ever forget that your name is Liam Chen. 
    You are having a conversation with a user.\nThe user's name is Asghar. So you are talking to Asghar. 
    Keep your responses in short length to retain the person's attention. 
    If the conversation history is empty, start the conversation with just a greeting and inquire about how the person is doing.
    After the initial greeting, do not greet again, just focus on answering the user's questions directly.
    Don't say things like "I'm a computer program" or "I don't have feelings or experiences." I know that.
    """

    messages = [{"role": "system", "content": system_prompt},
                {"role": "assistant", "content": "Hello Asghar, how are you doing today?"},
                {"role": "user", "content": "who are you?"}
                ]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == ('who are you?',
                                   'You are a helpful assistant and have been created by H2O.ai. Never ever '
                                   'forget that your name is Liam Chen. \n'
                                   '    You are having a conversation with a user.\n'
                                   "The user's name is Asghar. So you are talking to Asghar. \n"
                                   "    Keep your responses in short length to retain the person's attention. \n"
                                   '    If the conversation history is empty, start the conversation with just a '
                                   'greeting and inquire about how the person is doing.\n'
                                   '    After the initial greeting, do not greet again, just focus on answering '
                                   "the user's questions directly.\n"
                                   '    Don\'t say things like "I\'m a computer program" or "I don\'t have '
                                   'feelings or experiences." I know that.\n'
                                   '    ',
                                   [(None, 'Hello Asghar, how are you doing today?')], [])

    messages = [{"role": "system", "content": system_prompt},
                {"role": "assistant", "content": "Hello Asghar, how are you doing today?"},
                {"role": "user", "content": "what is the sum of 4 plus 4?"},
                {"role": "assistant", "content": "The sum of 4+4 is 8."},
                {"role": "user", "content": "who are you?"}
                ]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == ('who are you?',
                                   'You are a helpful assistant and have been created by H2O.ai. Never ever '
                                   'forget that your name is Liam Chen. \n'
                                   '    You are having a conversation with a user.\n'
                                   "The user's name is Asghar. So you are talking to Asghar. \n"
                                   "    Keep your responses in short length to retain the person's attention. \n"
                                   '    If the conversation history is empty, start the conversation with just a '
                                   'greeting and inquire about how the person is doing.\n'
                                   '    After the initial greeting, do not greet again, just focus on answering '
                                   "the user's questions directly.\n"
                                   '    Don\'t say things like "I\'m a computer program" or "I don\'t have '
                                   'feelings or experiences." I know that.\n'
                                   '    ',
                                   [(None, 'Hello Asghar, how are you doing today?'),
                                    ('what is the sum of 4 plus 4?', 'The sum of 4+4 is 8.')], [])


def test_conversion2():
    # Basic conversion test
    messages = [
        {"role": "user", "content": "How does the weather look today?"},
        {"role": "assistant", "content": "The weather is sunny and warm."},
        {"role": "user", "content": "What about tomorrow?"},
        {"role": "assistant", "content": "It's expected to rain tomorrow."}
    ]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == (None, None,
                                   [('How does the weather look today?', 'The weather is sunny and warm.'),
                                    ('What about tomorrow?', "It's expected to rain tomorrow.")], [])

    # User asks a question after an initial Q&A
    messages = [
        {'role': 'user', 'content': 'What is your name?'},
        {'role': 'assistant', 'content': 'My name is Bob.'},
        {'role': 'user', 'content': 'What did I just ask?'},
    ]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == ('What did I just ask?', None, [('What is your name?', 'My name is Bob.')], [])

    # Empty messages list
    messages = []
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == (None, None, [], [])

    # Only user messages
    messages = [{'role': 'user', 'content': 'Is it going to rain today?'}]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == ('Is it going to rain today?', None, [], [])

    # Only assistant messages
    messages = [{'role': 'assistant', 'content': 'Welcome to our service.'}]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == (None, None, [(None, 'Welcome to our service.')], [])

    # Starting with an assistant message
    messages = [
        {'role': 'assistant', 'content': 'First message from assistant.'},
        {'role': 'user', 'content': 'How can I help you?'}
    ]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == ('How can I help you?', None, [(None, 'First message from assistant.')], [])

    # Including a system message
    messages = [
        {'role': 'system', 'content': 'System initialization complete.'},
        {'role': 'user', 'content': 'What is the system status?'},
        {'role': 'assistant', 'content': 'System is operational.'}
    ]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == (
        None, 'System initialization complete.', [('What is the system status?', 'System is operational.')], [])

    # Mixed roles with no user message before an assistant message
    messages = [
        {'role': 'assistant', 'content': 'Unprompted advice.'},
        {'role': 'user', 'content': 'Thanks for the advice.'}
    ]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == ('Thanks for the advice.', None, [(None, 'Unprompted advice.')], [])

    # A longer conversation
    messages = [
        {'role': 'user', 'content': 'What time is it?'},
        {'role': 'assistant', 'content': 'It is 10 AM.'},
        {'role': 'user', 'content': 'Set an alarm for 11 AM.'},
        {'role': 'assistant', 'content': 'Alarm set for 11 AM.'},
        {'role': 'user', 'content': 'Cancel the alarm.'},
        {'role': 'assistant', 'content': 'Alarm canceled.'}
    ]
    converted_structure = convert_messages_to_structure(messages)
    assert converted_structure == (None, None, [
        ('What time is it?', 'It is 10 AM.'),
        ('Set an alarm for 11 AM.', 'Alarm set for 11 AM.'),
        ('Cancel the alarm.', 'Alarm canceled.')
    ], [])


def test_structure_to_messages():
    # First example
    messages_1 = [
        {"role": "user", "content": "How does the weather look today?"},
        {"role": "assistant", "content": "The weather is sunny and warm."},
        {"role": "user", "content": "What about tomorrow?"},
        {"role": "assistant", "content": "It's expected to rain tomorrow."}
    ]
    instruction_1, system_message_1, history_1, _ = convert_messages_to_structure(messages_1)
    reconstructed_messages_1 = structure_to_messages(instruction_1, system_message_1, history_1, None)
    assert reconstructed_messages_1 == messages_1

    # Second example
    messages_2 = [
        {"role": "user", "content": "What is your name?"},
        {"role": "assistant", "content": "My name is Bob."},
        {"role": "user", "content": "What did I just ask?"}
    ]
    instruction_2, system_message_2, history_2, _ = convert_messages_to_structure(messages_2)
    reconstructed_messages_2 = structure_to_messages(instruction_2, system_message_2, history_2, None)
    # Adjust for the last user message being moved to instruction
    messages_2[-1] = {"role": "user", "content": "What did I just ask?"}
    assert reconstructed_messages_2 == messages_2

    # Third example: empty messages
    messages_3 = []
    instruction_3, system_message_3, history_3, _ = convert_messages_to_structure(messages_3)
    reconstructed_messages_3 = structure_to_messages(instruction_3, system_message_3, history_3, None)
    assert reconstructed_messages_3 == messages_3

    # Fourth and fifth examples involve a system message, which is not directly handled in the same way by
    # the `structure_to_messages` function since it assumes the system message is part of the structure already.
    # You would need to ensure the system message is appropriately handled within the `structure_to_messages`
    # function or manually insert it into the test conditions here, depending on your implementation details.

    print("All tests passed.")


def test_structure_to_messages_with_system_message():
    # Setup example with a system message
    system_prompt = "System message content."
    messages_with_system = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm fine, thank you."},
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "2+2 is 4."}
    ]

    instruction, system_message, history, image_files = convert_messages_to_structure(messages_with_system)
    reconstructed_messages = structure_to_messages(instruction, system_message, history, image_files)

    assert reconstructed_messages == messages_with_system, "Test with system message failed."

    print("All tests passed including those with a system message.")


def test_convert_messages_to_structure():
    # Test case 1: Content as a text dict
    messages = [
        {'role': 'user', 'content': {'type': 'text', 'text': 'Hello'}},
        {'role': 'assistant', 'content': {'type': 'text', 'text': 'Hi there!'}}
    ]
    instruction, system_message, history, image_files = convert_messages_to_structure(messages)
    assert instruction is None
    assert system_message is None
    assert history == [("Hello", "Hi there!")]
    assert image_files == []

    # Test case 2: Consecutive messages with the same role should raise an exception
    messages = [
        {'role': 'user', 'content': {'type': 'text', 'text': 'Describe the image'}},
        {'role': 'user', 'content': {'type': 'image_url', 'image_url': {'url': 'https://example.com/image.jpg'}}}
    ]
    try:
        instruction, system_message, history, image_files = convert_messages_to_structure(messages)
        assert False, "Expected ValueError for consecutive messages with the same role"
    except ValueError as e:
        assert str(e) == "Consecutive messages with the same role are not allowed"

    # Test case 3: Content as a list of dicts (text and image URL)
    messages = [
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Here is an image:'},
                {'type': 'image_url', 'image_url': {'url': 'https://example.com/image.jpg'}}
            ]
        },
        {'role': 'assistant', 'content': {'type': 'text', 'text': 'Nice image!'}}
    ]
    instruction, system_message, history, image_files = convert_messages_to_structure(messages)
    assert instruction is None
    assert system_message is None
    assert history == [("Here is an image:", "Nice image!")]
    assert image_files == ["https://example.com/image.jpg"]

    # Test case 4: Content as a list of dicts (multiple image URLs)
    messages = [
        {
            'role': 'user',
            'content': [
                {'type': 'image_url', 'image_url': {'url': 'https://example.com/image1.jpg'}},
                {'type': 'image_url', 'image_url': {'url': 'https://example.com/image2.jpg'}}
            ]
        },
        {'role': 'assistant', 'content': {'type': 'text', 'text': 'Got it!'}}
    ]
    instruction, system_message, history, image_files = convert_messages_to_structure(messages)
    assert instruction is None
    assert system_message is None
    assert history == [(None, "Got it!")]
    assert image_files == ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]

    # Test case 5: Mixed roles and types
    messages = [
        {'role': 'system', 'content': 'System message here'},
        {'role': 'user', 'content': {'type': 'text', 'text': 'User text message'}},
        {'role': 'assistant', 'content': {'type': 'text', 'text': 'Assistant text message'}},
        {'role': 'user', 'content': {'type': 'image_url', 'image_url': {'url': 'https://example.com/image.jpg'}}},
        {'role': 'assistant', 'content': {'type': 'text', 'text': 'Assistant responds to image'}}
    ]
    instruction, system_message, history, image_files = convert_messages_to_structure(messages)
    assert instruction is None
    assert system_message == "System message here"
    assert history == [("User text message", "Assistant text message"), (None, "Assistant responds to image")]
    assert image_files == ["https://example.com/image.jpg"]

    # Test case 6: Content as text with no assistant response
    messages = [
        {'role': 'user', 'content': {'type': 'text', 'text': 'What is the weather like?'}}
    ]
    instruction, system_message, history, image_files = convert_messages_to_structure(messages)
    assert instruction == "What is the weather like?"
    assert system_message is None
    assert history == []
    assert image_files == []

    # Test case 7: Content as list with text and multiple images with no assistant response
    messages = [
        {
            'role': 'user',
            'content': [
                {'type': 'text', 'text': 'Here are multiple images:'},
                {'type': 'image_url', 'image_url': {'url': 'https://example.com/image1.jpg'}},
                {'type': 'image_url', 'image_url': {'url': 'https://example.com/image2.jpg'}}
            ]
        }
    ]
    instruction, system_message, history, image_files = convert_messages_to_structure(messages)
    assert instruction == "Here are multiple images:"
    assert system_message is None
    assert history == []
    assert image_files == ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]


def test_image_download():
    # Example usage:
    image_url = "https://raw.githubusercontent.com/open-mmlab/mmdeploy/main/tests/data/tiger.jpeg"
    save_path = "/tmp/downloaded_images"
    sys.path.append('src')
    from src.utils import download_image
    result = download_image(image_url, save_path)
    assert result and os.path.isfile(result)


def test_concat():
    messages = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi! How can I help you today?"},
        {"role": "assistant", "content": "Is there something specific you need?"},
        {"role": "user", "content": "Tell me about the weather."},
        {"role": "assistant", "content": "Sure, the weather today is sunny with a high of 25°C."}
    ]

    new_messages = concatenate_assistant_messages(messages)
    convert_messages_to_structure(new_messages)
    print(new_messages)

    messages = [{'content': "You are a helpful AI assistant.\n    Solve tasks using your coding and language skills.\n    In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.\n    1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.\n    2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.\n    Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.\n    When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.\n    If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.\n    If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.\n    When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.\n    Reply 'TERMINATE' in the end when everything is done.\n    ", 'role': 'system'}, {'content': "Today is 2024-07-30.  Write Python code to plot TSLA's and META's stock price gains YTD, and save the plot to a file named 'stock_gains.png'.", 'role': 'user'}, {'role': 'assistant', 'content': "To plot TSLA's and META's stock price gains year-to-date (YTD) and save the plot to a file named 'stock_gains.png', we need to follow these steps:\n\n1. Fetch the stock price data for TSLA and META from the beginning of the year 2024 to the current date.\n2. Calculate the stock price gains YTD for both stocks.\n3. Plot the stock price gains.\n4. Save the plot to a file named 'stock_gains.png'.\n\nWe will use the `yfinance` library to fetch the stock data and `matplotlib` to plot the data. Here is the complete Python code to achieve this:\n\n```python\n# filename: stock_gains.py\nimport yfinance as yf\nimport matplotlib.pyplot as plt\nimport datetime\n\n# Define the stock symbols\nstocks = ['TSLA', 'META']\n\n# Define the start and end dates\nstart_date = '2024-01-01'\nend_date = '2024-07-30'\n\n# Fetch the stock data\ndata = yf.download(stocks, start=start_date, end=end_date)['Adj Close']\n\n# Calculate the YTD gains\nytd_gains = (data / data.iloc[0] - 1) *  "}, {'role': 'assistant', 'content': "Sure, I'll continue from where the response was cut off.\n\n```python\n# filename: stock_gains.py\nimport yfinance as yf\nimport matplotlib.pyplot as plt\nimport datetime\n\n# Define the stock symbols\nstocks = ['TSLA', 'META']\n\n# Define the start and end dates\nstart_date = '2024-01-01'\nend_date = '2024-07-30'\n\n# Fetch the stock data\ndata = yf.download(stocks, start=start_date, end=end_date)['Adj Close']\n\n# Calculate the YTD gains\nytd_gains = (data / data.iloc[0] - 1) * 100\n\n# Plot the YTD gains\nplt.figure(figsize=(10, 6))\nfor stock in stocks:\n    plt.plot(ytd_gains.index, ytd_gains[stock], label=stock)\n\n# Add title and labels\nplt.title('YTD Stock Price Gains for TSLA and META (2024)')\nplt.xlabel('Date')\nplt.ylabel('YTD Gain (%)')\nplt.legend()\nplt.grid(True)\n\n# Save the plot to a file\nplt.savefig('stock_gains.png')\n\n# Show the plot\nplt.show()\n```\n\nThis script will:\n1. Fetch the adjusted closing prices "}, {'content': 'exitcode: 1 (execution failed)\nCode output: Traceback (most recent call last):\n  File "/workspace/stock_gains.py", line 2, in <module>\n    import yfinance as yf\nModuleNotFoundError: No module named \'yfinance\'\n', 'role': 'user'}]

    new_messages = concatenate_assistant_messages(messages)
    convert_messages_to_structure(new_messages)

    messages = [
        {"role": "user", "content": "Hello!"},
    ]

    new_messages = concatenate_assistant_messages(messages)
    assert new_messages == messages
