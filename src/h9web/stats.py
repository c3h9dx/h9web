import logging
import json
import jsonrpc
from ._version import __version__
from h9web.api import BaseAPIHandler
from h9web.event import Event

class Stats(BaseAPIHandler):
    stats = {
        'h9web': {
            'version': __version__
        },
        'h9d': {
            'version': None,
            'commit': None,
            'uptime': None,
            'bus': {
                'received_frames': None,
                'send_frames': None,
                'endpoints': {},
            },
            'tcp_clients': []
        }}

    async def get(self):
        self.return_success(Stats.stats)

    @classmethod
    def uptime2human(cls, uptime):
        day = uptime // (24 * 3600)
        uptime = uptime % (24 * 3600)
        hour = uptime // 3600
        uptime %= 3600
        minutes = uptime // 60
        uptime %= 60
        seconds = uptime

        ret = ''
        if day:
            ret += str(day) + ' days '

        if hour:
            ret += str(hour) + ' hours '

        if minutes:
            ret += str(minutes) + ' minutes '

        ret += str(seconds) + ' seconds'
        return ret

    @classmethod
    async def _refresh_base_stats(cls, h9d):
        try:
            rpc_req = jsonrpc.request("get_version")
            # logging.debug("### 1.1 ###")
            res = await h9d.call_request(rpc_req)
            # logging.debug("### 1.2 ###")
            cls.stats['h9d']['version'] = res['version']
            cls.stats['h9d']['commit'] = res['commit_sha']
        except Exception as e:
            # logging.error(e)
            cls.stats['h9d']['version'] = None
            cls.stats['h9d']['commit'] = None

        try:
            rpc_req = jsonrpc.request("get_tcp_clients")
            # logging.debug("### 3.1 ###")
            res = await h9d.call_request(rpc_req)
            # logging.debug("### 3.2 ###")
            cls.stats['h9d']['tcp_clients'] = res
        except Exception as e:
            # logging.error(e)
            cls.stats['h9d']['tcp_clients'] = []

    @classmethod
    async def refresh_base_stats(cls, h9d):
        await cls._refresh_base_stats(h9d)
        await Event.publish_to_all(Event.STATS_EVENT, cls.stats)

    @classmethod
    async def clean_stats(cls, h9d):
        cls.stats['h9d']['version'] = None
        cls.stats['h9d']['commit'] = None

        cls.stats['h9d']['tcp_clients'] = []

        cls.stats['h9d']['uptime'] = None
        cls.stats['h9d']['bus']['received_frames'] = None
        cls.stats['h9d']['bus']['send_frames'] = None
        cls.stats['h9d']['bus']['endpoints'] = {}

        await Event.publish_to_all(Event.STATS_EVENT, cls.stats)

    @classmethod
    async def refresh_stats_and_calc_rate(cls, h9d, period_ms):
        logging.debug("Refreshing stats...")

        await cls._refresh_base_stats(h9d)

        try:
            rpc_req = jsonrpc.request("get_stats")
            # logging.debug("### 2.1 ###")
            res = await h9d.call_request(rpc_req)
            # logging.debug("### 2.2 ###")
            cls.stats['h9d']['uptime'] = Stats.uptime2human(res['uptime'])
            cls.stats['h9d']['bus']['received_frames'] = res['bus']['received_frames']
            cls.stats['h9d']['bus']['send_frames'] = res['bus']['send_frames']
            for endpoint in res['bus']['endpoints']:
                endpoint_tmp = cls.stats['h9d']['bus']['endpoints'].get(endpoint['name'], {})

                last_received_frames = endpoint_tmp.get('received_frames', None)
                if last_received_frames is not None:
                    endpoint_tmp['received_frames_per_s'] = (endpoint['received_frames'] - last_received_frames) / period_ms / 1000
                else:
                    endpoint_tmp['received_frames_per_s'] = None

                last_send_frames = endpoint_tmp.get('send_frames', None)
                if last_send_frames is not None:
                    endpoint_tmp['send_frames_per_s'] = (endpoint['send_frames'] - last_send_frames) / period_ms / 1000
                else:
                    endpoint_tmp['send_frames_per_s'] = None

                endpoint_tmp['received_frames'] = endpoint['received_frames']
                endpoint_tmp['send_frames'] = endpoint['send_frames']

                cls.stats['h9d']['bus']['endpoints'][endpoint['name']] = endpoint_tmp
        except Exception as e:
            # logging.error(e)
            # raise e
            cls.stats['h9d']['uptime'] = None
            cls.stats['h9d']['bus']['received_frames'] = None
            cls.stats['h9d']['bus']['send_frames'] = None
            cls.stats['h9d']['bus']['endpoints'] = {}

        await Event.publish_to_all(Event.STATS_EVENT, cls.stats)
