"""frame range section in the UI."""

import hou

def resolve_payload(node):
    title = node.parm("title").eval().strip()
    return {"job_title": title}
