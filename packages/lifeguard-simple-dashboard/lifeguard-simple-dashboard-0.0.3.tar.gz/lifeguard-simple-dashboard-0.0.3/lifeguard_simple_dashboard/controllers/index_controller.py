import pathlib
import traceback
from os.path import join

from lifeguard.controllers import Response
from lifeguard.logger import lifeguard_logger as logger
from lifeguard.repositories import ValidationRepository

from lifeguard_simple_dashboard.settings import LIFEGUARD_DASHBOARD_PREFIX_PATH

SEARCHPATH = str(join(pathlib.Path(__file__).parent.parent.absolute(), "templates"))


def render_template(template, data=None):
    response = Response()
    response.template = template
    response.template_searchpath = SEARCHPATH
    response.data = data
    return response


def send_status(status):
    response = Response()
    response.status = status
    return response


def send_file(path, content_type):
    absolute_path = pathlib.Path(__file__).parent.parent.absolute()
    with open(join(absolute_path, "public", path), "r") as file:
        response = Response()
        response.content = file.read()
        response.content_type = content_type
        return response


def dashboard_send_css(path):
    try:
        logger.info("returning css %s", path)
        return send_file("css/{}".format(path), "text/css")
    except:
        return send_status(404)


def index():
    try:
        logger.info("rendering index")
        validations = ValidationRepository().fetch_all_validation_results()
        return render_template(
            "dashboard.html",
            {
                "validations": validations,
                "LIFEGUARD_DASHBOARD_PREFIX_PATH": LIFEGUARD_DASHBOARD_PREFIX_PATH,
            },
        )
    except Exception as error:
        logger.error(
            "error on render dashboard index: %s",
            error,
            extra={"traceback": traceback.format_exc()},
        )
