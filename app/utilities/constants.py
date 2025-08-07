

class Constants:

    @staticmethod
    def endpoint_url(endpoint: str) -> str:
        return f"/api/v0/collections/{endpoint}/"