from . import validators
from flask import g, request
from flask_restful import Resource
from jsonschema import ValidationError
import base64
import uuid
from ptero_common import nicer_logging
from ptero_common.nicer_logging import logged_response
from ptero_common.server_info import get_server_info

LOG = nicer_logging.getLogger(__name__)


class NetView(Resource):

    @logged_response(logger=LOG)
    def put(self, net_key):
        LOG.info("Handling PUT of net <%s>",
                net_key, extra={'netKey': net_key})
        try:
            return _submit_net(net_key)
        except ValidationError as e:
            LOG.exception(
                "JSON body does not pass validation for PUT %s: %s",
                request.url, str(e))
            return {'error': e.message}, 400


class TokenListView(Resource):

    @logged_response(logger=LOG)
    def post(self, net_key, place_idx):
        g.backend.put_token.delay(net_key, place_idx)
        return {}, 201

    @logged_response(logger=LOG)
    def put(self, net_key, place_idx):
        color_group_idx = int(request.args['color_group'])
        color = int(request.args['color'])

        g.backend.put_token.delay(net_key=net_key, place_idx=place_idx,
                                  color=color, color_group_idx=color_group_idx,
                                  data=request.json)

        return {}, 201


class NetListView(Resource):

    @logged_response(logger=LOG)
    def post(self):
        net_key = _generate_net_key()
        LOG.info("Handling POST of net <%s>",
                net_key, extra={'netKey': net_key})
        try:
            return _submit_net(net_key)
        except ValidationError as e:
            LOG.exception("Net did not pass validation",
                    extra={'netKey': net_key})
            LOG.info("Responding 400 to submission of net <%s>",
                    net_key, extra={'netKey': net_key})
            return {'error': e.message}, 400


def _submit_net(net_key):
    net_data = validators.get_net_post_data()

    net_info = g.backend.create_net(net_data, net_key=net_key)

    LOG.info("Responding 201 to submission of net <%s>",
            net_key, extra={'netKey': net_key})
    return net_info, 201


def _generate_net_key():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2]


class ServerInfo(Resource):
    @logged_response(logger=LOG)
    def get(self):
        return get_server_info(
                'ptero_petri.implementation.celery_app'), 200
