from ciohoudini import frames, context


def resolve_payload(node, task_limit, **kwargs):
    """
    Resolve the task_data field for the payload.

    If we are in sim mode, we emit one task.
    """
    if node.parm("is_sim").eval():
        cmd = node.parm("task_template").eval()
        tasks = [{"command": cmd, "frames": "0"}] 
        return {"tasks_data": tasks}
 
    tasks = []
    sequence = frames.main_frame_sequence(node)
    chunks = sequence.chunks()
    for i, chunk in enumerate(chunks):
        if task_limit > -1 and i >= task_limit:
            break
        context.set_for_task(first=chunk.start, last=chunk.end, step=chunk.step)
        cmd = node.parm("task_template").eval()
        tasks.append({"command": cmd, "frames": str(chunk)})

    return {"tasks_data": tasks}
