# config-joker
A package to ease usage of different configuration conditions in your projects.

## How to use in

Obs.: There are some examples in the [examples folder](https://github.com/joaopedromgoulart/config-joker/tree/main/examples)

Import the sources you'll use and the Config class:

    from config_joker Config, EnvironmentSource

Initialize the config class implementing the sources you want to use:

    config = Config(
            sources=[
                EnvironmentSource()
            ]
        )

Find the configurations you want to use:

    import os
    os.environ['env_variable'] = '1'
    number_one_from_env_source_as_int = config.required(key='env_variable', value_type=int)

The value stored in number_one_from_env_source_as_int will be the number one as an integer.

