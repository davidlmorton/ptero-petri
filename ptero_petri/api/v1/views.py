from flask import g, request, url_for
from flask.ext.restful import Resource
import traceback
import logging

LOG = logging.getLogger(__name__)

class NetView(Resource):
    pass

class TokenListView(Resource):
    def post(self, net_key, place_idx):
        color = g.backend.create_token(net_key, place_idx)

        response_code = 201
        body = {'color': color}
        LOG.info("Responding %s to  %s", response_code, request.url)
        LOG.debug("Body: %s", body)

        return body, response_code

    def put(self, net_key, place_idx):
        color_group_idx = int(request.args['color_group'])
        color = int(request.args['color'])

        g.backend.put_token(net_key, place_idx, color_group_idx, color,
                data=request.json)

        response_code = 201
        body = {}
        LOG.info("Responding %s to  %s", response_code, request.url)
        LOG.debug("Body: %s", body)

        return body, response_code


class NetListView(Resource):
    def post(self):
        net_data = request.json
        net_data['entry_places'] = set(net_data['entry_places'])

        net_info = g.backend.create_net(net_data)

        entry_links = {}
        for place_name, place_idx in net_info['entry_place_info'].items():
            entry_links[place_name] = url_for('token-list',
                    net_key=net_info['net_key'],
                    place_idx=place_idx,
                    _external=True)

        response_code = 201
        body = {'net_key': net_info['net_key'], 'entry_links': entry_links}
        LOG.info("Responding %s to  %s", response_code, request.url)
        LOG.debug("Body: %s", body)

        return body, response_code
