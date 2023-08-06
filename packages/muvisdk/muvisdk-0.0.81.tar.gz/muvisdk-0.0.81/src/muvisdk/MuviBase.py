class MuviBase:
    def __init__(self, processor):
        self.processor = processor

    def ok(self, response, status=200):
        response['processor'] = self.processor
        return {
            'status': status,
            'response': response
        }

    def error(self, response: dict = None, message: str = None, status: int = 400):
        if not response:
            response = {}
        if message:
            response['message'] = message
        if 'status' not in response:
            response['status'] = status
        response['processor'] = self.processor
        return {
            'status': status,
            'response': response
        }
