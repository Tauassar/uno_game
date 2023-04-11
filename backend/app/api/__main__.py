import uvicorn

from ..core import conf
from ..core import log


def main():
    uvicorn.run(
        'app.api:app',
        host=conf.api.host,
        port=conf.api.port,
        debug=conf.debug,
        reload=conf.debug,
        log_config=log.setup_default_logging(),
    )


if __name__ == '__main__':
    main()
