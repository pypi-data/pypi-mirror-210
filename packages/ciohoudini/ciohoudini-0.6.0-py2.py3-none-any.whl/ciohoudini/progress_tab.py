# PROGRESS TAB NOT YET IMPLEMENTED
# 
from ciohoudini.buttoned_scroll_panel import ButtonedScrollPanel
from ciohoudini.notice_grp import NoticeGrp
class ProgressTab(ButtonedScrollPanel):

    def __init__(self, dialog):
        super(ProgressTab, self).__init__(dialog,
            buttons=[("cancel", "Cancel submission")])

    def populate(self):

        message = "Progress!\nSorry progress bar is not yet implemented.\nPlease wait.\n"
        
        widget = NoticeGrp(message, "info")

        self.layout.addWidget(widget)
        self.layout.addStretch()

        self.configure_signals()

    def configure_signals(self):
        self.buttons["cancel"].clicked.connect(self.dialog.on_close)
