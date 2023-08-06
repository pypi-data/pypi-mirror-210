import json

from ciohoudini import (
    job_title,
    project,
    instances,
    software,
    environment,
    driver,
    frames,
    task,
    assets,
    miscellaneous,
)


def set_stats_panel(node, **kwargs):
    """Update the stats panel.

    Currently, only gets frames info, but will probably get other (non-payload) info like cost
    estimate. Example, when chunk size of frames change value.
    """
    frames.set_stats_panel(node, **kwargs)


def set_preview_panel(node, **kwargs):
    """Update the payload preview panel.

    Payload preview displays the JSON object that is submitted to Conductor. For optimization
    reasons, we don't always do a dependency scan or generate all tasks.

    User can set task_limit to -1 to see all tasks
    if user hits the display_assets button the assets list will include the result of a scan.
    """
    kwargs["task_limit"] = node.parm("display_tasks").eval()
    kwargs["do_asset_scan"] = kwargs.get("parm_name") == "do_asset_scan"

    payload = resolve_payload(node, **kwargs)

    node.parm("payload").set(json.dumps(payload, indent=2))
    

def resolve_payload(node, **kwargs):
    set_stats_panel(node, **kwargs)
    payload = {}
    payload.update(job_title.resolve_payload(node))
    payload.update(project.resolve_payload(node))
    payload.update(instances.resolve_payload(node))
    payload.update(software.resolve_payload(node))
    payload.update(environment.resolve_payload(node))
    payload.update(driver.resolve_payload(node))
    payload.update(miscellaneous.resolve_payload(node))
    payload.update(frames.resolve_payload(node))
    payload.update(task.resolve_payload(node, **kwargs))
    payload.update(assets.resolve_payload(node, **kwargs))


    return payload
