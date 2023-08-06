class SimilarWebLoggerMock():
    def info(self, msg):
        print(f"[info] {msg}")

    def error(self, err):
        print(f"[err] {err}")
