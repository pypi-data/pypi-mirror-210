class StdLogger:
    def info(self, message):
        print(f"INFO - {message}")

    def warn(self, message):
        print(f"WARNING - {message}")

    def error(self, message):
        print(f"ERROR - {message}")
