
def task_added_msg(task_name: str, task_id: str) -> dict:
    return {"type": "task_added", "task_id": task_id, "task_name": task_name}

def task_started_msg(task_id: str) -> dict:
    return {"type": "task_started", "task_id": task_id}


def module_started_msg(pid: int, task_id: str, module_id: str) -> dict:
    return {"type": "module_started", "task_id": task_id, "module_id": module_id,
            "pid": pid}

def error_msg(http_code: int, text: str, task_id: str = "", module_id: str = "") -> dict:
    msg = {"type": "error", "code": http_code, "text": text}
    if task_id:
        msg["task_id"] = task_id
    if module_id:
        msg["module_name"] = module_id
    return msg

def stdout_msg(text: str, module_id: str, task_id: str):
    return {"type": "stdout", "text": text, "module_id": module_id, "task_id": task_id}

def stderr_msg(text: str, module_id: str, task_id: str):
    return {"type": "stderr", "text": text, "module_id": module_id, "task_id": task_id}

def module_finished_msg(task_id: str, module_id: str, ret_code: int) -> dict:
    return {"type": "module_finished", "task_id": task_id, "module_id": module_id,
            "ret_code": ret_code}
