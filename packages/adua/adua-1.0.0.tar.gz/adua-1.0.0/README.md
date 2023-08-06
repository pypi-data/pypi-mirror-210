# Adua

Adua is a Python package that provides various functionalities, including web search, face recognition, audio processing, and more. It is designed to assist users with tasks and interactions using speech and text.

## Features

- Web search: Perform searches on popular search engines.
- Face recognition: Capture faces from video and perform facial recognition.
- Audio processing: Convert text to speech and speech to text.
- Wolfram Alpha integration: Get answers to queries using Wolfram Alpha.
- Image generation: Generate images based on queries.
- OpenAI GPT integration: Get answers to questions using OpenAI GPT.

## Installation

You can install Adua using pip:

```shell
pip install adua

Usage
Here's a quick example of how to use Adua in your Python code:
<code>
from adua import Adua

# Initialize Adua
adua = Adua()

# Perform a web search
adua.web_search('how to create Python package')

# Capture faces from video
faces, face_num, face_locations, face_encodings, frame = adua.Capture_face_vid()

# Convert text to speech
adua.speak('Hello, how are you?')

# Convert speech to text
query = adua.listen()
</code>
License
This project is licensed under the MIT License.