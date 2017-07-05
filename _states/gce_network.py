from __future__ import absolute_import
import libcloud
import logging

log = logging.getLogger(__name__)

# pylint: disable=import-error


def __virtual__():
    '''
    Only load if the cloud module is available in __salt__
    '''
    return 'cloud.action' in __salt__

def _show_network(**kwargs):

    provider = kwargs['provider']
    net={}

    try:
        network = __salt__['cloud.action'](fun='show_network',  **kwargs)[provider]['gce']
        log.debug("network found: {n}".format(n=network))
    except libcloud.common.google.ResourceNotFoundError as e:

        log.debug("network not found: {e}".format(e=e.args) )
        return net

    net['name'] = network['name']
    net['cidr'] = network['cidr']
    net['mode'] = network.get('extra:mode', None)
    net['created'] = network.get('extra:creationTimestamp', None)
    net['id'] = network['id']

    return net


def _create_network(**kwargs):

    provider = kwargs['provider']
    net={}

    e = None
    try:
        network = __salt__['cloud.action'](fun='create_network', **kwargs)[provider]['gce']
        log.error("create network: {n}".format(n=network))
    except Exception as e:

        log.error("Cannot create network: {e}".format(e=e.args) )
        return net,e

    # Simplify and sanitize from raw libcloud objects
    net['name'] = network['name']
    net['cidr'] = network['cidr']
    net['mode'] = network.get('extra:mode', None)
    net['created'] = network.get('extra:creationTimestamp', None]
    net['id'] = network['id']

    return net,e




def present(name, cidr=None, provider=None):

    """
    Creates new network

    newnet:
      gce_network:
        - present
        - name: newnet
        - cidr: 10.0.0.0/24
        - provider:  gce-provider

    :param name: Name of network
    :param cidr: Network mask
    :param provider:
    :return:
    """
    kwargs={'name': name, 'cidr': cidr, 'provider': provider}

    net = _show_network(**kwargs)

    if net == {}:
        net,e = _create_network(**kwargs)

        if e != None:
            ret = {'name': name, 'result': False, 'comment': 'Cannot create new network', 'changes': e.message}
            return  ret
        else:
            ret = {'name': name, 'result': True, 'comment': 'Created new network', 'changes': net}

            return  ret
    else:

        ret = {'name': name, 'result': True, 'comment': 'Network already present ', 'changes': {}}
        return ret
