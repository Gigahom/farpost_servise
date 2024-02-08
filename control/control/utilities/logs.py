import os


def custom_sink(message):
    var_name = message.record["extra"].get("abs_id", "default")
    login = message.record["extra"].get("login", "default")
    file_name = message.record["extra"].get("file_name", "default")
    level = message.record["level"].name
    # Здесь можно использовать любую логику для определения пути на основе сообщения или его уровня
    if level == "ERROR":
        directory = f"../logs/{login}/{var_name}/errors"
    elif level == "INFO":
        directory = f"../logs/{login}/{var_name}/info"
    elif level == "DEBUG":
        directory = f"../logs/{login}/{var_name}/debug"
    else:
        directory = f"../logs/{login}/{var_name}/other"

    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, f"{file_name}.log")
    with open(filepath, "a") as file:
        file.write(f"{message}")
