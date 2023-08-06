"""
All communication with the HDA and routing is done through this module.
"""

import hou
import os
import re

from ciohoudini import (
    driver,
    instances,
    project,
    software,
    frames,
    environment,
    errors,
    context,
    assets,
    payload,
    submit,
    miscellaneous
)

from ciocore import data as coredata

# Set the task context to its current frame when frame changes. This is so that the user can copy
# the task, set to render the current frame, to the clipboard and then to run it locally in a shell.
# def currrentFrameContext(event_type, frame):
#     if event_type == hou.playbarEvent.FrameChanged:
#         context.set_for_task(first=frame,last=frame,step=1)

# hou.playbar.addEventCallback(currrentFrameContext)
# TURNED OFF FOR NOW.


fixtures_dir = os.path.expanduser(os.path.join("~", "conductor_fixtures"))
coredata.init("houdini")
coredata.set_fixtures_dir("")

# Set the task context to its default (first:1, last:1, step:1)
context.set_for_task()

MULTI_PARM_RE = re.compile(r"^([a-zA-Z0-9_]+_)\d+$")

# A list of parms that affect the payload. Only needed to update the payload panel. On submission,
# the payload is always regenerated.
AFFECTS_PAYLOAD = (
    "connect",
    "title",
    "project",
    "instance_type_family",
    "instance_type",
    "preemptible",
    "retries",
    "host_version",
    "driver_version",
    "chunk_size",
    "frame_range",
    "use_custom_frames",
    "use_scout_frames",
    "scout_frames",
    "add_hdas",
    "display_tasks",
    "do_asset_scan",
    "environment_kv_pairs",
    "env_key_",
    "env_value_",
    "env_excl_",
    "do_email",
    "email_addresses",
    "clear_all_assets",
    "browse_files",
    "browse_folder",
    "location_tag",
    "use_daemon",
    "add_variable",
    "add_existing_variable",
    "add_plugin",
    "extra_plugins",
    "extra_plugin_",
    "copy_script",

)


#: A dictionary of menu callbacks.
MENUS = {
    "instance_type": instances.populate_menu,
    "project": project.populate_menu,
    "host_version": software.populate_host_menu,
    "driver_version": software.populate_driver_menu,
    "extra_plugin_": software.populate_extra_plugin_menu,
}

LOCK_ON_CREATE = ["asset_regex", "render_script", "asset_excludes"]

# List of parms with expressions that need an event callback. in order to update the payload preview
# See on_loaded.
NEEDS_PAYLOAD_CALLBACK =  ["output_folder", "task_template", "frame_range", "title"]

def connect(node, **kwargs):
    """
    Connect to Conductor data.

    Get projects, hardware, software.
    """
    force = kwargs.get("force", True)
    with errors.show():

        coredata.data(force=force)
        project.ensure_valid_selection(node)
        instances.ensure_valid_selection(node)
        software.ensure_valid_selection(node)



def on_created(node, **kwargs):
    """Initialize state when a node is created.

    See on_loaded()
    """
    for parm in LOCK_ON_CREATE:
        node.parm(parm).lock(True)

    # Some default values don't seem to get set on creation. This is a hack to set them.
    node.parm("scout_frames").set("auto:3")
    node.parm("preemptible").set(True)

    on_loaded(node, **kwargs)


def on_loaded(node, **kwargs):
    """Initialize state when a node is loaded.

    Steps:
        1. Parms with expressions do not trigger callbacks that are set up in the HDA parameter
           interface. Therefore we have to add them using addParmCallback in order to keep the stats
           panel and payload preview up to date.
        2. If coredata is valid (another node previously connected to Conductor), then we must
           ensure the values the projects, inst-types, and software string parms are valid according
           to the options in coredata before updating the preview node. Otherwise the menus
           might look valid, but the value could be "notset", and that would show up in
           the preview.
        3. Refresh the preview and stats panels.
    """
    kwargs["force"] = False
    node.addParmCallback(payload.set_preview_panel, NEEDS_PAYLOAD_CALLBACK)
    project.ensure_valid_selection(node)
    instances.ensure_valid_selection(node)
    software.ensure_valid_selection(node)

    payload.set_preview_panel(node, **kwargs)


def populate_menu(node, parm, **kwargs):
    """Call method to populate any menu dynamically.

    Menu populate methods are defined in MENUS dict.
    We handle single and multi parms. 
    In the case of multi parms, the handler key has no index. It just ends in an underscore.
    """
    with errors.show():
        
        menu_key = parm.name()
        match = MULTI_PARM_RE.match(menu_key)
        if match:
            menu_key = match.group(1)
        return MENUS.get(menu_key, noop )(node)


def on_input_changed(node, **kwargs):
    """
    Make changes based on input connecion make/break.

    Input means driver: arnold, mantra, sim dop simulation etc.
    """
    with errors.show():
        driver.update_input_node(node)
        software.ensure_valid_selection(node)

    payload.set_preview_panel(node, **kwargs)

PARM_HANDLERS = {
    "connect": connect,
    "instance_type_family":instances.ensure_valid_selection,
    "use_custom_frames": frames.on_use_custom,
    "clear_all_assets": assets.clear_all_assets ,
    "browse_files": assets.browse_files ,
    "browse_folder": assets.browse_folder,
    "add_hdas":  assets.add_hdas,
    "submit": submit.invoke_submission_dialog,
    "export_script": submit.export_script,
    "add_variable": environment.add_variable,
    "add_existing_variable": environment.add_existing_variables,
    "add_plugin": software.add_plugin,
    "copy_script": miscellaneous.copy_render_script
}

def noop(node, **kwargs):
    pass

def on_change(node, **kwargs):
    """Routing for all HDA parameter callbacks.
    
    handler can be a callback or a list of callbacks
    """
    parm_name = kwargs["parm_name"]
    with errors.show():
        # All parms invoke one or more handler functions from the PARM_HANDLERS dict.
        funcs = PARM_HANDLERS.get(parm_name, noop)
        if not isinstance(funcs, list):
            funcs = [funcs]
        for func in funcs:
            func(node, **kwargs)

        if parm_name.startswith(AFFECTS_PAYLOAD):
            payload.set_preview_panel(node, **kwargs)


def on_action_button(node, **kwargs):
    """
    Callback for any action button.

    Action buttons are the little buttons ion the right hand side that can be associated with any
    parm.

    """
    with errors.show():
        parmtuple = kwargs["parmtuple"]
        if parmtuple.name().startswith("extra_asset_"):
            index = kwargs["script_multiparm_index"]
            assets.remove_asset(node, index)
            payload.set_preview_panel(node,  **kwargs)
            return

        if parmtuple.name().startswith("env_excl_"):
            index = kwargs["script_multiparm_index"]
            environment.remove_variable(node, index)
            payload.set_preview_panel(node,  **kwargs)
            return

        if parmtuple.name().startswith("extra_plugin_"):
            index = kwargs["script_multiparm_index"]
            software.remove_plugin(node, index)
            payload.set_preview_panel(node, **kwargs)
            return