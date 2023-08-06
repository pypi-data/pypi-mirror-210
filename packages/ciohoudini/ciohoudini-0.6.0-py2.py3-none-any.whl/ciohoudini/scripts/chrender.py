#!/usr/bin/env hython

"""Script to render a ROP.

# Task template should resolve to something like: 
# hython "/Users/julian/Conductor/houdini/ciohoudini/scripts/chrender.py" -f 2 2 1 -d /out/mantra1 "/path/to/aaa_MantraOnly.hip"
"""

import sys
import re
import argparse
from string import ascii_uppercase
import hou

SIM_TYPES = ("baketexture", "geometry", "output", "dop")

DRIVE_LETTER_RX = re.compile(r"^[a-zA-Z]:")


def error(msg):
    if msg:
        sys.stderr.write("\n")
        sys.stderr.write("Error: %s\n" % msg)
        sys.stderr.write("\n")
        sys.exit(1)


def usage(msg=""):
    sys.stderr.write(
        """Usage:

    hython /path/to/chrender.py -d driver -f start end step hipfile
    All flags/args are required

    -d driver:          Path to the output driver that will be rendered
    -f range:           The frame range specification (see below)
    hipfile             The hipfile containing the driver to render
    """
    )
    error(msg)


def prep_ifd(node):
    """Prepare the IFD (Mantra) ROP for rendering."""
    print("Preparing Mantra ROP node {}".format(node.name()))
    node.parm("vm_verbose").set(3)
    print("Set loglevel to 3")
    node.parm("vm_alfprogress").set(True)
    print("Turn on Alfred style progress")
    node.parm("soho_mkpath").set(True)
    print("Make intermediate directories if needed")


def prep_baketexture(node):
    """Prepare the BAKETEXTURE ROP for rendering."""
    pass


def prep_arnold(node):
    """Prepare the Arnold ROP for rendering."""
    node.parm("ar_abort_on_license_fail").set(True)
    node.parm("ar_abort_on_error").set(True)
    node.parm("ar_log_verbosity").set('debug')
    node.parm("ar_log_console_enable").set(True)

def prep_ris(node):
    """Prepare the RIS (Renderman) ROP for rendering."""
    print("Preparing Ris ROP node {}".format(node.name()))
    node.parm("loglevel").set(4)
    print("Set loglevel to 4")
    node.parm("progress").set(True)
    print("Turn progress on")
    num_displays = node.parm("ri_displays").eval()
    for i in range(num_displays):
        print("Set display {} to make intermediate directories if needed".format(i))
        node.parm("ri_makedir_{}".format(i)).set(True)


def prep_vray_renderer(node):
    """Prepare the V-Ray ROP for rendering."""
    print("Preparing V-Ray ROP node {}".format(node.name()))
    # I couldn't find a parameter to increase verbosity or set progress format.
    print("Nothing to do")


def prep_geometry(node):
    """Prepare the geometry ROP for rendering."""
    pass


def prep_output(rop_node):
    """Prepare the output ROP for rendering."""
    pass


def prep_dop(node):
    """Prepare the DOP ROP for rendering."""
    node.parm("trange").set(1)
    node.parm("mkpath").set(True)
    node.parm("alfprogress").set(True)


def prep_opengl(node):
    """Prepare the OpenGL ROP for rendering."""
    pass


def run_driver_prep(rop_node):
    """
    Run the driver prep function for this ROP based on its type.

    The prep function can be used to increase log verbosity, set the progress format, etc.
    If the ROP type is not handled, then do nothing.
    """

    rop_type = rop_node.type().name().split(":")[0]
    try:
        fn = globals()["prep_{}".format(rop_type)]
    except KeyError:
        return
    try:
        fn(rop_node)
    except:
        sys.stderr.write(
            "Failed to run prep function for ROP type: {}. Skipping.\n".format(rop_type)
        )
        return


def is_sim(rop):
    return rop.type().name().startswith(SIM_TYPES)


def parse_args():
    """Parse args and error if any are missing or extra."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-d", dest="driver", required=True)
    parser.add_argument("-f", dest="frames", nargs=3, type=int)
    parser.add_argument("hipfile", nargs=1)

    args, unknown = parser.parse_known_args()

    if unknown:
        usage("Unknown argument(s): %s" % (" ".join(unknown)))

    return args


def ensure_posix_paths():

    refs = hou.fileReferences()

    for parm, value in refs:
        if not parm:
            continue

        try:
            node_name = parm.node().name()
            parm_name = parm.name()
            node_type = parm.node().type().name()
        except:
            print("Failed to get parm info")
            continue
        ident = "[{}]{}.{}".format(node_type, node_name, parm_name)
        if node_type.startswith("conductor::job"):
            continue

        if not DRIVE_LETTER_RX.match(value):
            print("Not a drive letter. Skipping")
            continue

        print("{} Found a drive letter in path: {}. Stripping".format(ident, value))
        value = DRIVE_LETTER_RX.sub("", value).replace("\\", "/")
        print("{} Setting value to {}".format(ident, value))
        try:
            parm.set(value)
        except hou.OperationFailed as ex:
            print("{} Failed to set value for parm {}. Skipping".format(ident, value))
            print(ex)
            continue
        print("{} Successfully set value {}".format(ident, value))


def render(args):
    """Render the specified ROP.

    If there are only load warnings, print them and carry on.  The scene is likely to contain
    unknown assets such as the conductor job which were used to ship the scene but are not needed to
    render.
    """

    hipfile = args.hipfile[0]
    driver = args.driver
    frames = args.frames

    print("hipfile: '{}'".format(hipfile))
    print("driver: '{}'".format(driver))
    print("frames: 'From: {} to: {}'by: {}".format(*frames))

    try:
        hou.hipFile.load(hipfile)
    except hou.LoadWarning as e:
        sys.stderr.write("Error: %s\n" % e)

    rop = hou.node(driver)
    if not rop:
        usage("Rop does not exist: '{}'".format(driver))

    print("Ensure POSIX paths")
    ensure_posix_paths()

    run_driver_prep(rop)

    if is_sim(rop):
        rop.render(verbose=True, output_progress=True)
    else:
        rop.render(
            frame_range=tuple(args.frames),
            verbose=True,
            output_progress=True,
            method=hou.renderMethod.FrameByFrame,
        )


render(parse_args())
