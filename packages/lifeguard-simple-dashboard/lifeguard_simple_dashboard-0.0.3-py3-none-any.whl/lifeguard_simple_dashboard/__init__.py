from lifeguard.controllers import register_custom_controller

from lifeguard_simple_dashboard.controllers.index_controller import (
    index,
    dashboard_send_css,
)
from lifeguard_simple_dashboard.settings import LIFEGUARD_DASHBOARD_PREFIX_PATH


class LifeguardSimpleDashboardPlugin:
    def __init__(self, lifeguard_context):
        self.lifeguard_context = lifeguard_context
        register_custom_controller(
            "{}/simple-dashboard-css/<path:path>".format(
                LIFEGUARD_DASHBOARD_PREFIX_PATH
            ),
            dashboard_send_css,
            {"methods": ["GET"]},
        )
        register_custom_controller(
            "{}/".format(LIFEGUARD_DASHBOARD_PREFIX_PATH), index, {"methods": ["GET"]}
        )


def init(lifeguard_context):
    LifeguardSimpleDashboardPlugin(lifeguard_context)
