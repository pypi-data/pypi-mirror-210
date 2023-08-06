from ciohoudini.buttoned_scroll_panel import ButtonedScrollPanel
from ciohoudini.notice_grp import NoticeGrp
from ciocore import config
import urllib.parse

SUCCESS_CODES = [201, 204]


class ResponseTab(ButtonedScrollPanel):
    def __init__(self, dialog):
        super(ResponseTab, self).__init__(dialog, buttons=[("close", "Close")])

    def populate(self, responses):

        successes = [
            response for response in responses if response["response_code"] in SUCCESS_CODES
        ]
        failures = [
            response for response in responses if response["response_code"] not in SUCCESS_CODES
        ]

        title = "No submissions"
        status = "info"
        if successes and failures:
            title = "Some successes and some failures"
            status = "info"
        elif successes:
            title = "All submissions succeeded"
            status = "success"
        elif failures:
            title = "All submissions failed"
            status = "error"

        widget = NoticeGrp(title, status)
        self.layout.addWidget(widget)

        cfg = config.config().config

        for response in successes:
            node_name = response["node"].name()
            success_uri = response["response"]["uri"].replace("jobs", "job")
            url = urllib.parse.urljoin(cfg["url"], success_uri)
            message = f"Success! Node:{node_name}\nClick to go to the Dashboard.\n{url}"
            widget = NoticeGrp(message, "success", url)
            self.layout.addWidget(widget)
        for response in failures:
            node_name = response["node"].name()
            code = response["response_code"]
            text = response["response"]
            message = f"Failed with code:{code} {node_name}\n{text}"
            widget = NoticeGrp(message, "error")
            self.layout.addWidget(widget)

        self.layout.addStretch()

        self.configure_signals()

    def configure_signals(self):
        self.buttons["close"].clicked.connect(self.dialog.on_close)
