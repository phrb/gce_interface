#!/usr/bin/env python

import argparse
import logging
import pickle

import opentuner
from opentuner.measurement import MeasurementInterface
from opentuner.measurement import MeasurementDriver
from opentuner.search.manipulator import ConfigurationManipulator
from opentuner.search.manipulator import FloatParameter

log = logging.getLogger(__name__)

parser = argparse.ArgumentParser(parents=opentuner.argparsers())
parser.add_argument('--dimensions', type=int, default=2,
                    help='dimensions for the Rosenbrock function')
parser.add_argument('--domain', type=float, default=1000,
                    help='bound for variables in each dimension')
parser.add_argument('--function', default='rosenbrock',
                    choices=('rosenbrock', 'sphere', 'beale'),
                    help='function to use')

class PicklerDriver(MeasurementDriver):
    def run_desired_result(self, desired_result,
                           compile_result=None,exec_id=None):
        super(PicklerDriver, self).run_desired_result(desired_result,
                                                      compile_result,
                                                      exec_id)

    def __init__(self, **kwargs):
        print "I'm here init driver"
        super(PicklerDriver, self).__init__(**kwargs)

class PicklerInterface(MeasurementInterface):
    def run_precompiled(self, desired_result, input, limit, compile_result, id):

        p = pickle.dumps(desired_result.configuration)
        i = pickle.dumps(input)
        t = pickle.loads(p)

        new_result = opentuner.resultsdb.models.Result(configuration = t)
        new_input = pickle.loads(i)

#        print input, limit

        return self.run(new_result, new_input, limit)

    def __init__(self, *args, **kwargs):
        print "I'm here init interface"
        super(PicklerInterface, self).__init__(*args, **kwargs)

class Rosenbrock(PicklerInterface):
    def run(self, desired_result, input, limit):
        cfg = desired_result.configuration.data
        val = 0.0
        x0 = cfg[0]
        x1 = cfg[1]
        val += 100.0 * (x1 - x0 ** 2) ** 2 + (x0 - 1) ** 2
        return opentuner.resultsdb.models.Result(time=val)

    def manipulator(self):
        manipulator = ConfigurationManipulator()
        for d in xrange(self.args.dimensions):
            manipulator.add_parameter(FloatParameter(d,
                                                     -self.args.domain,
                                                     self.args.domain))
        return manipulator

    def program_name(self):
        return self.args.function

    def program_version(self):
        return "%dx%d" % (self.args.dimensions, self.args.domain)

    def save_final_config(self, configuration):
        """
        called at the end of autotuning with the best resultsdb.models.Configuration
        """
        print "Final configuration", configuration.data

    @classmethod
    def main(cls, args, *pargs, **kwargs):
        from opentuner.tuningrunmain import TuningRunMain
        return TuningRunMain(cls(args, *pargs, **kwargs), args,
                             measurement_driver = PicklerDriver).main()


if __name__ == '__main__':
    args = parser.parse_args()
    if args.function == 'beale':
        # fixed for this function
        args.domain = 4.5
        args.dimensions = 2
    Rosenbrock.main(args)

