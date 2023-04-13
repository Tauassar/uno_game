import logging
import os
import pathlib

import toml


logger = logging.getLogger(__name__)


_APP_PREFIX = 'app'
_DEFAULT_OPTIONS = {
    'debug': True,
    'postgres': {
        'host': 'db',
        'port': 5432,
        'user': 'uno',
        'password': 'uno',
        'db': 'uno',
        'uri': '_build_postgres_uri:callable',
        'pool_size': 5,
        'connect_timeout': 2,
        'command_timeout': 2,
    },
    'security': {
        'secret_key': 'secret_key',
        'token_expires_in_seconds': 1800,
        'min_password_length': 8,
    },
    'log': {
        'internal': {
            'format': '[%(process)s] [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s',
        },
        'level': 'debug',
    },
    'api': {
        'host': '0.0.0.0',
        'port': 5001,
        'log_level': 'info',
        'pagination': {
            'limit': 20,
            'limit_min': 10,
            'limit_max': 100,
        },
    },
    'dummy': {
        'log_level': 'info',
    },
}
_IGNORED_OPTIONS = []
_DEFAULT_CONFIG_PATHS = [
    str(pathlib.Path(__file__).resolve(strict=True).parent.parent.parent / '.config.toml'),
    str(
        pathlib.Path(
            __file__,
        ).resolve(strict=True).parent.parent.parent / 'config/config.toml',
    ),
]


class ConfigurationError(Exception):
    """Raises on configuration related errors."""
    pass


def _merge_configs(original, patch):
    """Recursively merge two configs, patch overrides original values.

    >>> _merge_configs(
    ...     Config({'one': {'two': 2, 'three': 3}}),
    ...     Config({'one': {'two': 5}}),
    ... )
    {'one': {'two': 5, 'three': 3}}
    """
    for k, _ in patch.items():
        if (k in original and isinstance(original[k], Config)
                and isinstance(patch[k], Config)):
            _merge_configs(original[k], patch[k])
        else:
            original[k] = patch[k]

    return original


class Config(dict):
    """Dict subclass with attribute-like key access.

    :raises AttributeError: if the config option wasn't found.
    """

    def __init__(self, defaults=_DEFAULT_OPTIONS):
        super().__init__(defaults or {})

        if isinstance(defaults, dict):
            for k, v in defaults.items():
                if not isinstance(v, dict):
                    self[k] = v
                else:
                    self.__setattr__(k, Config(v))

    def merge(self, config):
        return _merge_configs(self, config)

    def load_from_env(self, app_prefix):
        prefix = app_prefix.upper() + '_'
        for option_key, option_value in os.environ.items():
            if option_key.startswith(prefix) and option_key not in _IGNORED_OPTIONS:
                _, key = option_key.split(prefix, 1)

                if not key:
                    continue

                # Try to cast the value to int or float
                try:
                    option_value = int(option_value)
                except (TypeError, ValueError):
                    try:
                        option_value = float(option_value)
                    except (TypeError, ValueError):
                        pass

                # Cast boolean values
                if isinstance(option_value, str):
                    if option_value.lower() in ['true', 'yes']:
                        option_value = True
                    elif option_value.lower() in ['false', 'no']:
                        option_value = False

                # Each part represent separate dictionary
                patch = option_value
                for part in reversed(key.lower().split('_')):
                    patch = {part: patch}

                # Merge in the patch
                self.merge(Config(patch))

    def load_from_file(self, path):
        try:
            with open(path) as infile:
                self.merge(Config(toml.load(infile)))
                logger.info(f'Configuration successfully loaded from {path!r}')
        except OSError as e:
            logger.debug(f'Could not read configuration file: {path!r} {e!r}')
            raise ConfigurationError from e
        except toml.TomlDecodeError as e:
            logger.error(f'Could not load configuration file {path!r}: {e!r}')
            raise ConfigurationError from e

    def load(self, paths=_DEFAULT_CONFIG_PATHS, app_prefix=_APP_PREFIX):
        """Loads configuration from JSON configuration file and from environment.

        Environment variables has higher priority.
        """
        for path in paths:
            try:
                logger.debug(f'Try path: {path!r}')
                self.load_from_file(path)
                self.load_from_env(app_prefix)
                return
            except ConfigurationError:
                logger.debug(f'Ignore path: {path!r}')
                continue

        logger.warning(f'No valid configuration file found in: {", ".join(paths)!r}')

        self.load_from_env(app_prefix)

    def _resolve_option(self, option):
        # Only string options may contain resolve markers
        if not isinstance(option, str):
            return option

        # We expect two-element tuple with (option_value, marker)
        option_parts = option.split(':')

        # If the option was marked as a callable
        if len(option_parts) == 2 and option_parts[1] == 'callable':
            # Try to find the callable in the globals and return its result
            try:
                return globals()[option_parts[0]](self)
            except (TypeError, KeyError) as e:
                raise ConfigurationError(
                    f'Could not find appropriate resolve callable: {option!r}') from e

        return option

    def __getattr__(self, attr):
        try:
            return self._resolve_option(self[attr])
        except KeyError:
            raise AttributeError(f'No option found: {attr!r}')

    def __setattr__(self, attr, value):
        self[attr] = value


def __getattr__(name):
    return getattr(_global_config, name)


_global_config = Config()
_global_config.load()


def _build_postgres_uri(pg):
    return f'postgresql+asyncpg://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.db}'


def _build_redis_uri(redis):
    auth_part = ''

    if redis.password is not None:
        user = redis.user or ''
        auth_part = f'{user}:{redis.password}@'

    return f'redis://{auth_part}{redis.host}:{redis.port}/{redis.db}'
