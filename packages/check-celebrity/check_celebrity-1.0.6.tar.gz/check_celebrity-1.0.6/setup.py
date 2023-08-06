from setuptools import setup

setup(
    name='check_celebrity',
    version='1.0.6',
    description='Celebrity check Package',
    packages=['check_celebrity'],
    install_requires=[
        'Deepface',
        'mtcnn',
        'keras',
        'Tensorflow',
        'numpy',
        'opencv-python',
        'Flask',
        'keras-vggface',
    ],
)