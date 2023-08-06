from setuptools import setup

setup(
    name='adua',  # Replace with your package name
    version='1.0.0',
    author='Abhay Bairagi',
    author_email='abhaynarayanbairagi@gmail.com',
    description='You can use this to create your own assistant',
    packages=['adua'],  # List all the packages you want to include
    install_requires=[
        'face_recognition',
        'opencv-python',
        'pyttsx3',
        'wikipedia',
        'wolframalpha',
        'SpeechRecognition',
        'openai',
        'numpy',
        'dlib'
    ],
)
