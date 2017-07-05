from __future__ import absolute_import

import logging
import libcloud

log = logging.getLogger(__name__)


# pylint: disable=import-error


def __virtual__():
    """
    Only load if the cloud module is available in __salt__
    """
    return 'cloud.action' in __salt__


def _show_address(**kwargs):
    provider = kwargs['provider']
    address = {}
    try:
        address_raw = __salt__['cloud.action'](fun='show_address', **kwargs)[provider]['gce']
        log.debug("address found: {a}".format(a=address_raw))
    except libcloud.common.google.ResourceNotFoundError as e:
        log.error("Address not found: {e}".format(e=e.args))
        return address

    # Simplify and sanitize from raw libcloud objects
    address['name'] = address_raw['name']
    address['address'] = address_raw['address']
    address['id'] = address_raw['id']
    address['created'] = address_raw['extra']['creationTimestamp']
    address['description'] = address_raw['extra']['description']
    address['region'] = address_raw['extra']['zone']
    address['status'] = address_raw['extra']['status']

    return address


def _create_address(**kwargs):
    provider = kwargs['provider']
    address = {}
    e = None
    try:
        address_raw = __salt__['cloud.action'](fun='create_address', **kwargs)[provider]['gce']
        log.debug("Address created: {a}".format(a=address_raw))
    except Exception as e:
        log.error("Cannot create Address rule: {e}".format(e=e.args))
        return address, e

    return _show_address(**kwargs), e


def present(name, **kwargs):
    """
    Creates static address

    firewall-rule:
      new_address:
        - present
        - name: new_address

    :param name: address name
    :param kwargs:
    :return:
    """
    kwargs['name'] = name
    address = _show_address(**kwargs)

    if address == {}:
        address, e = _create_address(**kwargs)
        if e != None:
            ret = {'name': name, 'result': False, 'comment': 'Cannot create new address', 'changes': e.message}
        else:
            ret = {'name': name, 'result': True, 'comment': 'New address created', 'changes': address}
        return ret
    else:

        ret = {'name': name, 'result': True, 'comment': 'address already present ', 'changes': {}}
        return ret
