from .. import webhooks
from .base import BasicActionBase
from twisted.internet import defer


class CreateColorGroupAction(BasicActionBase):
    def execute(self, net, color_descriptor, active_tokens, service_interfaces):
        merged_data = self.get_merged_token_data(net, active_tokens)

        size = int(merged_data['color_group_size'])
        new_color_group = net.add_color_group(size=size,
                parent_color=color_descriptor.color,
                parent_color_group_idx=color_descriptor.group.idx)

        output_token = net.create_token(color=color_descriptor.color,
                color_group_idx=color_descriptor.group.idx,
                data={'color_group_idx': new_color_group.idx})

        if 'url' in self.args:
            webhooks.send_webhook(
                    url=self.notify_url,
                    response_data={
                        'color_descriptor': color_descriptor,
                        'net_key': net.key,
                        'response_places': self.response_places,
                    },
                    data={
                        'group': new_color_group.as_dict
                    }
            )


        return [output_token], defer.succeed(None)


    @property
    def notify_url(self):
        return self.args['url']
