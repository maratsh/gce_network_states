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


def _show_fwrule(**kwargs):
    provider = kwargs['provider']
    fwrule = {}
    try:
        firewall_rule = __salt__['cloud.action'](fun='show_fwrule', **kwargs)[provider]['gce']
        log.debug("Firewall rule found: {f}".format(f=firewall_rule))
    except libcloud.common.google.ResourceNotFoundError as e:
        log.error("Firewall not rule found: {e}".format(e=e.args))
        return fwrule

    # Simplify and sanitize from raw libcloud objects
    fwrule['name'] = firewall_rule['name']
    fwrule['src_tags'] = firewall_rule['source_tags']
    fwrule['dst_tags'] = firewall_rule['target_tags']
    fwrule['id'] = firewall_rule['id']
    fwrule['created'] = firewall_rule['extra']['creationTimestamp']
    fwrule['network'] = firewall_rule['extra']['network_name']
    fwrule['description'] = firewall_rule['extra']['description']

    return fwrule


def _create_fwrule(**kwargs):
    provider = kwargs['provider']
    fwrule = {}
    e = None
    try:
        firewall_rule = __salt__['cloud.action'](fun='create_fwrule', **kwargs)[provider]['gce']
        log.debug("Firewal rule created: {f}".format(f=firewall_rule))
    except Exception as e:
        log.error("Cannot create Firwall rule: {e}".format(e=e.args))
        return fwrule, e

    return _show_fwrule(**kwargs), e


def present(name, **kwargs):
    """
    Creates new firewall rule

    firewall-rule:
     gce_firewall:
       - present
       - name: firewall-rule
       - provider: gce-provider
       - network: newnet
       - allow: 10.0.0.0/24
       - src_tags: web
       - dst_tags: base
       - src_range: 10.0.0.1/24
       - require:
         - gce_network: newnet


    :param name: Name of a rule
    :param kwargs:
    :return:
    """
    kwargs['name'] = name
    fwrule = _show_fwrule(**kwargs)

    if fwrule == {}:
        fwrule, e = _create_fwrule(**kwargs)
        if e != None:
            ret = {'name': name, 'result': False, 'comment': 'Cannot create new firewall rule', 'changes': e.message}
        else:
            ret = {'name': name, 'result': True, 'comment': 'New firewall rule created', 'changes': fwrule}
        return ret
    else:

        ret = {'name': name, 'result': True, 'comment': 'Firewall rule already present ', 'changes': {}}
        return ret
