import os

def custom_sink(message):
    var_name = message.record["extra"].get("abs_id", "default")
    level = message.record["level"].name
    # Здесь можно использовать любую логику для определения пути на основе сообщения или его уровня
    if level == "ERROR":
        directory = f"logs/{var_name}/errors"
    elif level == "INFO":
        directory = f"logs/{var_name}/info"
    else:
        directory = f"logs/{var_name}/other"
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filepath = os.path.join(directory, "logfile.log")
    with open(filepath, "a") as file:
        file.write(f"{message}")