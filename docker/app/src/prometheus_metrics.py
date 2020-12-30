import prometheus_client
from singleton import Singleton



# NOTE: singleton class, only one instance of this class will ever be cread

class PrometheusMetrics(metaclass=Singleton):

    def __init__(self):
        self._occupancy_metrics_instruments = {
            'operation_duration_seconds'        : prometheus_client.Histogram( 
                'occupancy_operation_duration_seconds', 
                'Number of seconds for Occupancy API operations',

                # Labels
                [ 'api_operation' ]
            ),
            'operation_invocation_total'        : prometheus_client.Counter(
                'occupancy_endpoint_invocation_total', 
                'Cumulative count for number of times each endpoint has been called',

                # Labels
                [ 'api_operation' ]
            )
        }


    def get_metric( self, instrument_name ):
        return self._occupancy_metrics_instruments[ instrument_name ] 
