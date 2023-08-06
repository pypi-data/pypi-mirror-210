from setuptools import setup


with open('./requirements.txt') as f:
    required = f.read().splitlines()

setup(name='tensorairspace',
        version='0.1.1',
        install_requires=required,
        packages=['tensorairspace'],
        python_requires=">=3.7",
        author_email="mr8bit@yandex.ru",
        description="TensorAeroSpace! - RL for Aerospace.",
        url="https://github.com/TensorAirSpace/TensorAirSpace",
        keywords="reinforcement-learning machine-learning gym openai aerospace toolbox python data-science",
      )
