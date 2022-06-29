from tom_alerts.alerts import GenericQueryForm, GenericAlert, GenericBroker
from tom_alerts.models import BrokerQuery
from tom_targets.models import Target
from urllib.parse import urlencode
from dateutil.parser import parse

from django import forms
import requests

broker_url = 'https://mars.lco.global/?format=json'
MARS_URL = 'https://mars.lco.global'

class MyBrokerForm(GenericQueryForm):
    target_name = forms.CharField(required=True)

class MyBroker:
    name = 'MyBroker'
    form = MyBrokerForm

    def _clean_parameters(self, parameters):
        return {k: v for k, v in parameters.items() if v and k != 'page'}

    def _request_alerts(self, parameters):
        if not parameters.get('page'):
            parameters['page'] = 1
        args = urlencode(self._clean_parameters(parameters))
        url = '{0}/?page={1}&format=json&{2}'.format(
            MARS_URL,
            parameters['page'],
            args
        )
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def fetch_alerts(self, parameters):
        response = self._request_alerts(parameters)
        alerts = response['results']
        if response['has_next'] and parameters['page'] < 10:
            parameters['page'] += 1
            alerts += self.fetch_alerts(parameters)
        return iter(alerts)


    def to_generic_alert(self, alert):
        timestamp = parse(alert['candidate']['wall_time'])
        url = '{0}/{1}/'.format(MARS_URL, alert['lco_id'])

        return GenericAlert(
            timestamp=timestamp,
            url=url,
            id=alert['lco_id'],
            name=alert['objectId'],
            ra=alert['candidate']['ra'],
            dec=alert['candidate']['dec'],
            mag=alert['candidate']['magpsf'],
            score=alert['candidate']['rb']
        )

    @classmethod
    def to_target(clazz, alert):
        return Target(
            identifier=alert['id'],
            name=alert['name'],
            type='SIDEREAL',
            designation='MY ALERT',
            ra=alert['ra'],
            dec=alert['dec'],
        )