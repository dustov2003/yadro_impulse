from logging import getLogger

from fastapi import FastAPI
from uvicorn import run

from dag_service.utils import get_hostname

from .config import DefaultSettings, get_settings
from .endpoints import list_of_routes

logger = getLogger(__name__)


def bind_routes(application: FastAPI, setting: DefaultSettings) -> None:
    for route in list_of_routes:
        application.include_router(route, prefix=setting.PATH_PREFIX)


def get_app() -> FastAPI:
    description = "Cервис для работы с направленным ациклическим графом (DAG)"

    application = FastAPI(
        title="Url shortener",
        description=description,
        docs_url="/swagger",
        openapi_url="/openapi",
        version="1.0.0",
    )
    settings = get_settings()
    bind_routes(application, settings)
    application.state.settings = settings
    return application


app = get_app()


if __name__ == "__main__":
    settings_for_application = get_settings()
    run(
        "dag_service.__main__:app",
        host=get_hostname(settings_for_application.APP_HOST),
        port=settings_for_application.APP_PORT,
        reload=True,
        reload_dirs=["dag_service", "tests"],
        log_level="debug",
    )
