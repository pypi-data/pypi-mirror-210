from flxtrd.protocols.base import BaseAPI

class GrpcAPI(BaseAPI):
    """gRPC implementation of the client"""
    def make_request(self, method, endpoint, **kwargs):
        pass
        # url = self.base_url + endpoint
        # headers = kwargs.get('headers', {})
        # params = kwargs.get('params', {})
        # data = kwargs.get('data', {})

        # for plugin in self.plugins:
        #     plugin.before_request(method, url, headers, params, data)

        # # Make gRPC request using the appropriate generated client
        # channel = grpc.insecure_channel(url)
        # stub = GeneratedGRPCStub(channel)
        # response = stub.MakeRequest(data)

        # for plugin in self.plugins:
        #     plugin.after_request(response)

        # return response