"""
Manage 3 software categories:

1. Remote Houdini version.
2. Plugin for the connected driver.
3. Extra plugins.


"""

import hou

from ciocore import data as coredata
from ciohoudini import driver


def populate_host_menu(node):
    """Populate houdini version menu.

    This is called by the UI whenever the user clicks the Houdini Version button.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]

    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()

    # hostnames will have the platform specifier (houdini 19.0 linux). We want to strip the platform.
    return [el for i in host_names for el in (i," ".join(i.split()[:2]).capitalize() )]



def populate_driver_menu(node):
    """Populate renderer/driver type menu.
    """
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]

    return [el for i in _get_compatible_plugin_versions(node) for el in (i,i)]

def populate_extra_plugin_menu(node):
    if not coredata.valid():
        return ["not_connected", "-- Not connected --"]

    _get_all_plugin_versions
    return [el for i in _get_all_plugin_versions(node) for el in (i,i)]

def ensure_valid_selection(node):
    """
    If connected, ensure the value of this parm is valid.
    """
    if not coredata.valid():
        return

    software_data = coredata.data()["software"]
    host_names = software_data.supported_host_names()
    selected_host = node.parm("host_version").eval()

    if not host_names:
        node.parm("host_version").set("no_houdini_packages")
        node.parm('driver_version').set("no_drivers")
        num_plugins = node.parm("extra_plugins").eval()
        for i in range(1, num_plugins+1):
            node.parm("extra_plugin_{}".format(i)).set("no_plugins")
        return

    if selected_host not in host_names:
        selected_host = host_names[-1]
    
    node.parm("host_version").set(selected_host)
    
    update_driver_selection(node)
    update_plugin_selections(node)


    driver_names = _get_compatible_plugin_versions(node)

    if not driver_names:
        node.parm('driver_version').set("no_drivers")
        return

    selected_driver = node.parm('driver_version').eval()


    if selected_driver not in driver_names:
        selected_driver = driver_names[-1]
    
    node.parm('driver_version').set(selected_driver)

def _get_compatible_plugin_versions(node):
    
    driver_data = driver.get_driver_data(node)
    if driver_data["conductor_product"].lower().startswith(("built-in", "unknown")):
        return [driver_data["conductor_product"]]

    if not coredata.valid():
        return []
    software_data = coredata.data().get("software")
    selected_host = node.parm("host_version").eval()
    plugins = software_data.supported_plugins(selected_host)
    plugin_names = [plugin["plugin"] for plugin in plugins]

    if driver_data["conductor_product"] not in plugin_names:
        return ["No plugins available for {}".format(driver_data["conductor_product"])]

    plugin_versions = []
    for plugin in plugins:
        if plugin["plugin"] == driver_data["conductor_product"]:
            for version in plugin["versions"]:
                plugin_versions.append("{} {}".format(
                    plugin["plugin"], version))
            break
    
    return plugin_versions



def _get_all_plugin_versions(node):
    
    if not coredata.valid():
        return []
    software_data = coredata.data().get("software")
    selected_host = node.parm("host_version").eval()
    plugins = software_data.supported_plugins(selected_host)

    plugin_versions = []
    for plugin in plugins:
        for version in plugin["versions"]:
            plugin_versions.append("{} {}".format(
                plugin["plugin"], version))

    return plugin_versions

def update_driver_selection(node, **kwargs):

    selected_plugin = node.parm('driver_version').eval()
    plugin_names = _get_compatible_plugin_versions(node)
    if not plugin_names:
         node.parm('driver_version').set("no_plugins_available")
         return
    if selected_plugin not in plugin_names:
        node.parm('driver_version').set(plugin_names[0])

def update_plugin_selections(node, **kwargs):

    plugin_names = _get_all_plugin_versions(node)
    num_plugins = node.parm("extra_plugins").eval()
    for i in range(1, num_plugins+1):
        parm = node.parm("extra_plugin_{}".format(i))
        selected_plugin = parm.eval()
        if not plugin_names:
            parm.set("no_plugins_available")
            continue
        if selected_plugin not in plugin_names:
            parm.set(plugin_names[0])


def resolve_payload(node):
    """Resolve the package IDs section of the payload for the given node."""
    ids = set()
 
    for package in packages_in_use(node):
        ids.add(package["package_id"])

    return {"software_package_ids": list(ids)}

def packages_in_use(node):
    """Return a list of packages as specified by names in the software dropdowns.
    """
    if not coredata.valid():
        return []
    tree_data = coredata.data().get("software")
    if not tree_data:
        return []

    platform = list(coredata.platforms())[0]
    host = node.parm("host_version").eval()
    driver = "{}/{} {}".format(host, node.parm("driver_version").eval(), platform)
    paths = [host, driver]

    num_plugins = node.parm("extra_plugins").eval()
    for i in range(1, num_plugins+1):
        parm = node.parm("extra_plugin_{}".format(i))
        paths.append("{}/{} {}".format(host, parm.eval(), platform))

    return list(filter(None, [tree_data.find_by_path(path) for path in paths if path]))


def add_plugin(node, **kwargs):
    """Add a new variable to the UI.
    
    This is called by the UI when the user clicks the Add Variable button.
    """
    num_exist = node.parm("extra_plugins").eval()
    node.parm("extra_plugins").set(num_exist+1)
    update_plugin_selections(node)


def remove_plugin(node, index ):
    """Remove a variable from the UI.
    
    Remove the entry at the given index and shift all subsequent entries down.
    """
    curr_count =  node.parm("extra_plugins").eval()
    for i in range(index+1, curr_count+1):

        from_parm = node.parm("extra_plugin_{}".format(i))
        to_parm = node.parm("extra_plugin_{}".format(i-1))
        to_parm.set(from_parm.rawValue())
    node.parm("extra_plugins").set(curr_count-1)
