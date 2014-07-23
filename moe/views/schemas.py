# -*- coding: utf-8 -*-
"""Base level schemas for the response/request schemas of each MOE REST endpoint.

.. Warning:: Outputs of colander schema serialization/deserialization should be treated as
  READ-ONLY. It appears that "missing=" and "default=" value are weak-copied (by reference).
  Thus changing missing/default fields in the output dict can modify the schema!

TODO(GH-291): make sure previous warning is moved to the schemas/__init__.py file

"""
import colander

from moe.optimal_learning.python.constant import GRADIENT_DESCENT_OPTIMIZER, TENSOR_PRODUCT_DOMAIN_TYPE, SQUARE_EXPONENTIAL_COVARIANCE_TYPE, NULL_OPTIMIZER, NEWTON_OPTIMIZER, DOMAIN_TYPES, OPTIMIZER_TYPES, COVARIANCE_TYPES, CONSTANT_LIAR_METHODS, DEFAULT_MAX_NUM_THREADS, MAX_ALLOWED_NUM_THREADS, DEFAULT_EXPECTED_IMPROVEMENT_MC_ITERATIONS, LIKELIHOOD_TYPES, LOG_MARGINAL_LIKELIHOOD, DEFAULT_CONSTANT_LIAR_METHOD, DEFAULT_CONSTANT_LIAR_LIE_NOISE_VARIANCE, DEFAULT_KRIGING_NOISE_VARIANCE, DEFAULT_KRIGING_STD_DEVIATION_COEF


class StrictMappingSchema(colander.MappingSchema):

    """A ``colander.MappingSchema`` that raises exceptions when asked to serialize/deserialize unknown keys.

    .. Note:: by default, colander.MappingSchema ignores/throws out unknown keys.

    """

    def schema_type(self, **kw):
        """Set MappingSchema to raise ``colander.Invalid`` when serializing/deserializing unknown keys.

        This overrides the staticmethod of the same name in ``colander._SchemaNode``.
        ``schema_type`` encodes the same information as the ``typ`` ctor argument to
        ``colander.SchemaNode``
        See: http://colander.readthedocs.org/en/latest/api.html#colander.SchemaNode

        .. Note:: Passing ``typ`` or setting ``schema_type`` in subclasses will ***override*** this!

        This solution follows: https://github.com/Pylons/colander/issues/116

        .. Note:: colander's default behavior is ``unknown='ignore'``; the other option
          is ``'preserve'. See: http://colander.readthedocs.org/en/latest/api.html#colander.Mapping

        """
        return colander.Mapping(unknown='raise')


class PositiveFloat(colander.SchemaNode):

    """Colander positive (finite) float."""

    schema_type = colander.Float
    title = 'Positive Float'

    def validator(self, node, cstruct):
        """Raise an exception if the node value (cstruct) is non-positive or non-finite.

        :param node: the node being validated (usually self)
        :type node: colander.SchemaNode subclass instance
        :param cstruct: the value being validated
        :type cstruct: float
        :raise: colander.Invalid if cstruct value is bad

        """
        if not 0.0 < cstruct < float('inf'):
            raise colander.Invalid(node, msg='Value = {0:f} must be positive and finite.'.format(cstruct))


class ListOfPositiveFloats(colander.SequenceSchema):

    """Colander list of positive floats."""

    float_in_list = PositiveFloat()


class ListOfFloats(colander.SequenceSchema):

    """Colander list of floats."""

    float_in_list = colander.SchemaNode(colander.Float())


class SinglePoint(StrictMappingSchema):

    """A point object.

    Contains:

        * point - ListOfFloats
        * value - float
        * value_var - float >= 0.0

    """

    point = ListOfFloats()
    value = colander.SchemaNode(colander.Float())
    value_var = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=0.0),
            missing=0.0,
            )


class PointsSampled(colander.SequenceSchema):

    """A list of SinglePoint objects."""

    point_sampled = SinglePoint()


class DomainCoordinate(StrictMappingSchema):

    """A single domain interval."""

    min = colander.SchemaNode(colander.Float())
    max = colander.SchemaNode(colander.Float())


class Domain(colander.SequenceSchema):

    """A list of domain interval DomainCoordinate objects."""

    domain_coordinates = DomainCoordinate()


class DomainInfo(StrictMappingSchema):

    """The domain info needed for every request.

    **Required fields**

        :dim: the dimension of the domain (int)

    **Optional fields**

        :domain_type: the type of domain to use in ``moe.optimal_learning.python.python_version.constant.DOMAIN_TYPES`` (default: TENSOR_PRODUCT_DOMAIN_TYPE)

    """

    domain_type = colander.SchemaNode(
            colander.String(),
            validator=colander.OneOf(DOMAIN_TYPES),
            missing=TENSOR_PRODUCT_DOMAIN_TYPE,
            )
    dim = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=0),
            )


class BoundedDomainInfo(DomainInfo):

    """The domain info needed for every request, along with bounds for optimization.

    **Required fields**

        All required fields from :class:`~moe.views.schemas.DomainInfo`
        :domain_bounds: the bounds of the domain of type :class:`moe.views.schemas.Domain`

    """

    domain_bounds = Domain()


class GradientDescentParametersSchema(StrictMappingSchema):

    """Parameters for the gradient descent optimizer.

    See :class:`moe.optimal_learning.python.cpp_wrappers.optimization.GradientDescentParameters`

    """

    max_num_steps = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=1),
            )
    max_num_restarts = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=1),
            )
    num_steps_averaged = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=0),
            )
    gamma = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=0.0),
            )
    pre_mult = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=0.0),
            )
    max_relative_change = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=0.0, max=1.0),
            )
    tolerance = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=0.0),
            )


class NewtonParametersSchema(StrictMappingSchema):

    """Parameters for the newton optimizer.

    See :class:`moe.optimal_learning.python.cpp_wrappers.optimization.NewtonParameters`

    """

    max_num_steps = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=1),
            )
    gamma = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=1.0),
            )
    time_factor = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=1.0e-16),
            )
    max_relative_change = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=0.0, max=1.0),
            )
    tolerance = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=0.0),
            )


class NullParametersSchema(StrictMappingSchema):

    """Parameters for the null optimizer."""

    pass


class CovarianceInfo(StrictMappingSchema):

    """The covariance info needed for every request.

    **Required fields**

        :covariance_type: a covariance type in ``moe.optimal_learning.python.python_version.constant.COVARIANCE_TYPES``
        :hyperparameters: the hyperparameters corresponding to the given covariance_type

    """

    covariance_type = colander.SchemaNode(
            colander.String(),
            validator=colander.OneOf(COVARIANCE_TYPES),
            missing=SQUARE_EXPONENTIAL_COVARIANCE_TYPE,
            )
    # TODO(GH-216): Improve hyperparameter validation. All > 0 is ok for now but eventually individual covariance objects should
    # provide their own validation.
    hyperparameters = ListOfPositiveFloats(
            missing=None,
            )


class GpHistoricalInfo(StrictMappingSchema):

    """The Gaussian Process info needed for every request.

    Contains:

        * points_sampled - PointsSampled

    """

    points_sampled = PointsSampled()


class ListOfPointsInDomain(colander.SequenceSchema):

    """A list of lists of floats."""

    point_in_domain = ListOfFloats()


class ListOfExpectedImprovements(colander.SequenceSchema):

    """A list of floats all geq 0.0."""

    expected_improvement = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=0),
            )


class MatrixOfFloats(colander.SequenceSchema):

    """A 2d list of floats."""

    row_of_matrix = ListOfFloats()


OPTIMIZER_TYPES_TO_SCHEMA_CLASSES = {
        NULL_OPTIMIZER: NullParametersSchema,
        NEWTON_OPTIMIZER: NewtonParametersSchema,
        GRADIENT_DESCENT_OPTIMIZER: GradientDescentParametersSchema,
        }


class OptimizerInfo(StrictMappingSchema):

    """Schema specifying the behavior of the multistarted optimizers in the optimal_learning library.

    .. Warning:: this schema does not provide default values for its fields. These defaults
      ***DO EXIST***; see ``moe.optimal_learning.python.constants``. However the defaults are
      dependent on external factors (like whether we're computing EI, log marginal, etc.) and
      are not known statically.

      See ``moe.views.optimizable_gp_pretty_view.OptimizableGpPrettyView.get_params_from_request``
      for an example of how this schema is used.

    .. Warning:: the field ``optimizer_parameters`` is ***NOT VALIDATED***. Users of this
      schema are responsible for passing its contents through the appropriate schema using
      the ``OPTIMIZER_TYPES_TO_SCHEMA_CLASSES`` dict provided above.

    TODO(GH-303): Try schema bindings as a way to automate setting validators and missing values.

    **Optional fields**

        :optimizer_type: a string defining the optimization type from `moe.optimal_learning.python.constant.OPTIMIZER_TYPES` (default: GRADIENT_DESCENT_OPTIMIZER)
        :num_multistarts: number of locations from which to start optimization runs
        :num_random_samples: number of random search points to use if multistart optimization fails
        :optimizer_parameters: a dict corresponding the the parameters of the optimization method

    """

    optimizer_type = colander.SchemaNode(
            colander.String(),
            validator=colander.OneOf(OPTIMIZER_TYPES),
            missing=None,
            )
    num_multistarts = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=1),
            missing=None,
            )
    num_random_samples = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=0),
            missing=None,
            )
    # TODO(GH-303): Use schema binding to set up missing/default and validation dynamically
    optimizer_parameters = colander.SchemaNode(
            colander.Mapping(unknown='preserve'),
            missing=None,
            )


class GpNextPointsRequest(StrictMappingSchema):

    """A ``gp_next_points_*`` request colander schema.

    **Required fields**

        :gp_historical_info: a :class:`moe.views.schemas.GpHistoricalInfo` dict of historical data
        :domain_info: a :class:`moe.views.schemas.BoundedDomainInfo` dict of domain information

    **Optional fields**

        :num_to_sample: number of next points to generate (default: 1)
        :mc_iterations: number of Monte Carlo (MC) iterations to perform in numerical integration to calculate EI
        :max_num_threads: maximum number of threads to use in computation
        :covariance_info: a :class:`moe.views.schemas.CovarianceInfo` dict of covariance information
        :optimizer_info: a :class:`moe.views.schemas.OptimizerInfo` dict of optimizer information
        :points_being_sampled: list of points in domain being sampled in concurrent experiments (default: [])

    **General Timing Results**

    Here are some "broad-strokes" timing results for EI optimization.
    These tests are not complete nor comprehensive; they're just a starting point.
    The tests were run on a Sandy Bridge 2.3 GHz quad-core CPU. Data was generated
    from a Gaussian Process prior. The optimization parameters were the default
    values (see ``moe.optimal_learning.python.constant``) as of sha
    ``c19257049f16036e5e2823df87fbe0812720e291``.

    Below, ``N = num_sampled``, ``MC = num_mc_iterations``, and ``q = num_to_sample``

    .. Note:: constant liar, kriging, and EPI (with ``num_to_sample = 1``) all fall
      under the ``analytic EI`` name.

    .. Note:: EI optimization times can vary widely as some randomly generated test
      cases are very "easy." Thus we give rough ranges.

    =============  =======================
     Analytic EI
    --------------------------------------
      dim, N           Gradient Descent
    =============  =======================
      3, 20               0.3 - 0.6s
      3, 40               0.5 - 1.4s
      3, 120              0.8 - 2.9s
      6, 20               0.4 - 0.9s
      6, 40              1.25 - 1.8s
      6, 120              2.9 - 5.0s
    =============  =======================

    We expect this to scale as ``~ O(dim)`` and ``~ O(N^3)``. The ``O(N^3)`` only happens
    once per multistart. Per iteration there's an ``O(N^2)`` dependence but as you can
    see, the dependence on ``dim`` is stronger.

    =============  =======================
     MC EI (``N = 20``, ``dim = 3``)
    --------------------------------------
      q, MC           Gradient Descent
    =============  =======================
      2, 10k                50 - 80s
      4, 10k              120 - 180s
      8, 10k              400 - 580s
      2, 40k              230 - 480s
      4, 40k              600 - 700s
    =============  =======================

    We expect this to scale as ``~ O(q^2)`` and ``~ O(MC)``. Scaling with ``dim`` and ``N``
    should be similar to the analytic case.

    **Example Minimal Request**

    .. sourcecode:: http

        Content-Type: text/javascript

        {
            "num_to_sample": 1,
            "gp_historical_info": {
                "points_sampled": [
                        {"value_var": 0.01, "value": 0.1, "point": [0.0]},
                        {"value_var": 0.01, "value": 0.2, "point": [1.0]}
                    ],
                },
            "domain_info": {
                "dim": 1,
                "domain_bounds": [
                    {"min": 0.0, "max": 1.0},
                    ],
                },
        }

    **Example Full Request**

    .. sourcecode:: http

        Content-Type: text/javascript

        {
            "num_to_sample": 1,
            "points_being_sampled": [[0.2], [0.7]],
            "mc_iterations": 10000,
            "max_num_threads": 1,
            "gp_historical_info": {
                "points_sampled": [
                        {"value_var": 0.01, "value": 0.1, "point": [0.0]},
                        {"value_var": 0.01, "value": 0.2, "point": [1.0]}
                    ],
                },
            "domain_info": {
                "domain_type": "tensor_product"
                "dim": 1,
                "domain_bounds": [
                    {"min": 0.0, "max": 1.0},
                    ],
                },
            "covariance_info": {
                "covariance_type": "square_exponential",
                "hyperparameters": [1.0, 1.0],
                },
            "optimizer_info": {
                "optimizer_type": "gradient_descent_optimizer",
                "num_multistarts": 200,
                "num_random_samples": 4000,
                "optimizer_parameters": {
                    "gamma": 0.5,
                    ...
                    },
                },
        }

    """

    num_to_sample = colander.SchemaNode(
            colander.Int(),
            missing=1,
            validator=colander.Range(min=1),
            )
    mc_iterations = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=1),
            missing=DEFAULT_EXPECTED_IMPROVEMENT_MC_ITERATIONS,
            )
    max_num_threads = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=1, max=MAX_ALLOWED_NUM_THREADS),
            missing=DEFAULT_MAX_NUM_THREADS,
            )
    gp_historical_info = GpHistoricalInfo()
    domain_info = BoundedDomainInfo()
    covariance_info = CovarianceInfo(
            missing=CovarianceInfo().deserialize({}),
            )
    optimizer_info = OptimizerInfo(
            missing=OptimizerInfo().deserialize({}),
            )
    points_being_sampled = ListOfPointsInDomain(
            missing=[],
            )


class GpNextPointsConstantLiarRequest(GpNextPointsRequest):

    """Extends the standard request :class:`moe.views.gp_next_points_pretty_view.GpNextPointsRequest` with a lie value.

    **Required fields**

        :gp_historical_info: a :class:`moe.views.schemas.GpHistoricalInfo` dict of historical data
        :domain_info: a :class:`moe.views.schemas.BoundedDomainInfo` dict of domain information

    **Optional fields**

        :num_to_sample: number of next points to generate (default: 1)
        :lie_method: a string from `CONSTANT_LIAR_METHODS` representing the liar method to use (default: 'constant_liar_min')
        :lie_value: a float representing the 'lie' the Constant Liar heuristic will use (default: None). If `lie_value` is not None the algorithm will use this value instead of one calculated using `lie_method`.
        :lie_noise_variance: a positive (>= 0) float representing the noise variance of the 'lie' value (default: 0.0)
        :covariance_info: a :class:`moe.views.schemas.CovarianceInfo` dict of covariance information
        :optimiaztion_info: a :class:`moe.views.schemas.OptimizerInfo` dict of optimization information

    **General Timing Results**

    See the ``Analytic EI`` table :class:`moe.views.schemas.GpNextPointsRequest` for
    rough timing numbers.

    **Example Request**

    .. sourcecode:: http

        Content-Type: text/javascript

        {
            "num_to_sample": 1,
            "lie_value": 0.0,
            "lie_noise_variance": 1e-12,
            "gp_historical_info": {
                "points_sampled": [
                        {"value_var": 0.01, "value": 0.1, "point": [0.0]},
                        {"value_var": 0.01, "value": 0.2, "point": [1.0]}
                    ],
                },
            "domain_info": {
                "dim": 1,
                "domain_bounds": [
                    {"min": 0.0, "max": 1.0},
                    ],
                },
        }

    """

    lie_method = colander.SchemaNode(
            colander.String(),
            missing=DEFAULT_CONSTANT_LIAR_METHOD,
            validator=colander.OneOf(CONSTANT_LIAR_METHODS),
            )
    lie_value = colander.SchemaNode(
            colander.Float(),
            missing=None,
            )
    lie_noise_variance = colander.SchemaNode(
            colander.Float(),
            missing=DEFAULT_CONSTANT_LIAR_LIE_NOISE_VARIANCE,
            validator=colander.Range(min=0.0),
            )


class GpNextPointsKrigingRequest(GpNextPointsRequest):

    """Extends the standard request :class:`moe.views.gp_next_points_pretty_view.GpNextPointsRequest` with kriging parameters.

    **Required fields**

        :gp_historical_info: a :class:`moe.views.schemas.GpHistoricalInfo` dict of historical data
        :domain_info: a :class:`moe.views.schemas.BoundedDomainInfo` dict of domain information

    **Optional fields**

        :num_to_sample: number of next points to generate (default: 1)
        :std_deviation_coef: a float used in Kriging, see Kriging implementation docs (default: 0.0)
        :kriging_noise_variance: a positive (>= 0) float used in Kriging, see Kriging implementation docs (default: 0.0)
        :covariance_info: a :class:`moe.views.schemas.CovarianceInfo` dict of covariance information
        :optimiaztion_info: a :class:`moe.views.schemas.OptimizerInfo` dict of optimization information

    **General Timing Results**

    See the ``Analytic EI`` table :class:`moe.views.schemas.GpNextPointsRequest` for
    rough timing numbers.

    **Example Request**

    .. sourcecode:: http

        Content-Type: text/javascript

        {
            "num_to_sample": 1,
            "std_deviation_coef": 0.0,
            "kriging_noise_variance": 0.0,
            "gp_historical_info": {
                "points_sampled": [
                        {"value_var": 0.01, "value": 0.1, "point": [0.0]},
                        {"value_var": 0.01, "value": 0.2, "point": [1.0]}
                    ],
                },
            "domain_info": {
                "dim": 1,
                "domain_bounds": [
                    {"min": 0.0, "max": 1.0},
                    ],
                },
        }

    """

    std_deviation_coef = colander.SchemaNode(
            colander.Float(),
            missing=DEFAULT_KRIGING_STD_DEVIATION_COEF,
            )
    kriging_noise_variance = colander.SchemaNode(
            colander.Float(),
            missing=DEFAULT_KRIGING_NOISE_VARIANCE,
            validator=colander.Range(min=0.0),
            )


class GpNextPointsStatus(StrictMappingSchema):

    """A gp_next_points_* status schema.

    **Output fields**

        :expected_improvement: EI evaluated at ``points_to_sample`` (:class:`moe.views.schemas.ListOfExpectedImprovements`)
        :optimizer_success: Whether or not the optimizer converged to an optimal set of ``points_to_sample``

    """

    expected_improvement = colander.SchemaNode(
            colander.Float(),
            validator=colander.Range(min=0.0),
            )
    optimizer_success = colander.SchemaNode(
        colander.Mapping(unknown='preserve'),
        default={'found_update': False},
    )


class GpNextPointsResponse(StrictMappingSchema):

    """A ``gp_next_points_*`` response colander schema.

    **Output fields**

        :endpoint: the endpoint that was called
        :points_to_sample: list of points in the domain to sample next (:class:`moe.views.schemas.ListOfPointsInDomain`)
        :status: a :class:`moe.views.schemas.GpNextPointsStatus` dict indicating final EI value and
          optimization status messages (e.g., success)

    **Example Response**

    .. sourcecode:: http

        {
            "endpoint": "gp_ei",
            "points_to_sample": [["0.478332304526"]],
            "status": {
                "expected_improvement": "0.443478498868",
                "optimizer_success": {
                    'gradient_descent_tensor_product_domain_found_update': True,
                    },
                },
        }

    """

    endpoint = colander.SchemaNode(colander.String())
    points_to_sample = ListOfPointsInDomain()
    status = GpNextPointsStatus()


class GpHyperOptRequest(StrictMappingSchema):

    """A gp_hyper_opt request colander schema.

    **Required fields**

        :gp_historical_info: a :class:`moe.views.schemas.GpHistoricalInfo` object of historical data
        :domain_info: a :class:`moe.views.schemas.DomainInfo` dict of domain information for the GP
        :hyperparameter_domain_info: a :class:`moe.views.schemas.BoundedDomainInfo` dict of domain information for the hyperparameter optimization

    **Optional fields**

        :max_num_threads: maximum number of threads to use in computation
        :covariance_info: a :class:`moe.views.schemas.CovarianceInfo` dict of covariance information, used as a starting point for optimization
        :optimizer_info: a :class:`moe.views.schemas.OptimizerInfo` dict of optimizer information

    **General Timing Results**

    Here are some "broad-strokes" timing results for hyperparameter optimization.
    These tests are not complete nor comprehensive; they're just a starting point.
    The tests were run on a Sandy Bridge 2.3 GHz quad-core CPU. Data was generated
    from a Gaussian Process prior. The optimization parameters were the default
    values (see ``moe.optimal_learning.python.constant``) as of sha
    ``c19257049f16036e5e2823df87fbe0812720e291``.

    Below, ``N = num_sampled``.

    ======== ===================== ========================
    Scaling with dim (N = 40)
    -------------------------------------------------------
      dim     Gradient Descent             Newton
    ======== ===================== ========================
      3           85s                      3.6s
      6           80s                      7.2s
      12         108s                     19.5s
    ======== ===================== ========================

    GD scales ``~ O(dim)`` and Newton ``~ O(dim^2)`` although these dim values
    are not large enough to show the asymptotic behavior.

    ======== ===================== ========================
    Scaling with N (dim = 3)
    -------------------------------------------------------
      N       Gradient Descent             Newton
    ======== ===================== ========================
      20        14s                       0.72s
      40        85s                        3.6s
      120       2100s                       60s
    ======== ===================== ========================

    Both methods scale as ``~ O(N^3)`` which is clearly shown here.

    **Example Request**

    .. sourcecode:: http

        Content-Type: text/javascript

        {
            "max_num_threads": 1,
            "gp_historical_info": {
                "points_sampled": [
                        {"value_var": 0.01, "value": 0.1, "point": [0.0]},
                        {"value_var": 0.01, "value": 0.2, "point": [1.0]}
                    ],
                },
            "domain_info": {
                "dim": 1,
                },
            "covariance_info": {
                "covariance_type": "square_exponential",
                "hyperparameters": [1.0, 1.0],
                },
            "hyperparameter_domain_info": {
                "dim": 2,
                "domain_bounds": [
                    {"min": 0.1, "max": 2.0},
                    {"min": 0.1, "max": 2.0},
                    ],
                },
            "optimizer_info": {
                "optimizer_type": "newton_optimizer",
                "num_multistarts": 200,
                "num_random_samples": 4000,
                "optimizer_parameters": {
                    "gamma": 1.2,
                    ...
                    },
                },
            "log_likelihood_info": "log_marginal_likelihood"
        }

    """

    max_num_threads = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=1, max=MAX_ALLOWED_NUM_THREADS),
            missing=DEFAULT_MAX_NUM_THREADS,
            )
    gp_historical_info = GpHistoricalInfo()
    domain_info = DomainInfo()
    covariance_info = CovarianceInfo(
            missing=CovarianceInfo().deserialize({}),
            )
    hyperparameter_domain_info = BoundedDomainInfo()
    optimizer_info = OptimizerInfo(
            missing=OptimizerInfo().deserialize({}),
            )
    log_likelihood_info = colander.SchemaNode(
            colander.String(),
            validator=colander.OneOf(LIKELIHOOD_TYPES),
            missing=LOG_MARGINAL_LIKELIHOOD,
            )


class GpHyperOptStatus(StrictMappingSchema):

    """A gp_hyper_opt status schema.

    **Output fields**

        :log_likelihood: The log likelihood at the new hyperparameters
        :grad_log_likelihood: The gradient of the log likelihood at the new hyperparameters
        :optimizer_success: Whether or not the optimizer converged to an optimal set of hyperparameters

    """

    log_likelihood = colander.SchemaNode(colander.Float())
    grad_log_likelihood = ListOfFloats()
    optimizer_success = colander.SchemaNode(
        colander.Mapping(unknown='preserve'),
        default={'found_update': False},
    )


class GpHyperOptResponse(StrictMappingSchema):

    """A gp_hyper_opt response colander schema.

    **Output fields**

        :endpoint: the endpoint that was called
        :covariance_info: a :class:`moe.views.schemas.CovarianceInfo` dict of covariance information
        :status: a :class:`moe.views.schemas.GpHyperOptStatus` dict indicating final log likelihood value/gradient and
          optimization status messages (e.g., success)

    **Example Response**

    .. sourcecode:: http

        {
            "endpoint":"gp_hyper_opt",
            "covariance_info": {
                "covariance_type": "square_exponential",
                "hyperparameters": ["0.88", "1.24"],
                },
            "status": {
                "log_likelihood": "-37.3279872",
                "grad_log_likelihood: ["-3.8897e-12", "1.32789789e-11"],
                "optimizer_success": {
                        'newton_found_update': True,
                    },
                },
        }

    """

    endpoint = colander.SchemaNode(colander.String())
    covariance_info = CovarianceInfo()
    status = GpHyperOptStatus()


class GpMeanVarRequest(StrictMappingSchema):

    """A gp_mean_var request colander schema.

    **Required fields**

        :points_to_sample: list of points in domain to calculate the Gaussian Process (GP) mean and covariance at (:class:`moe.views.schemas.ListOfPointsInDomain`)
        :gp_historical_info: a :class:`moe.views.schemas.GpHistoricalInfo` object of historical data

    **Optional fields**

        :covariance_info: a :class:`moe.views.schemas.CovarianceInfo` dict of covariance information

    **Example Minimal Request**

    .. sourcecode:: http

        Content-Type: text/javascript

        {
            "points_to_sample": [[0.1], [0.5], [0.9]],
            "gp_historical_info": {
                "points_sampled": [
                        {"value_var": 0.01, "value": 0.1, "point": [0.0]},
                        {"value_var": 0.01, "value": 0.2, "point": [1.0]}
                    ],
                },
            "domain_info": {
                "dim": 1,
                },
        }

    **Example Full Request**

    .. sourcecode:: http

        Content-Type: text/javascript

        {
            "points_to_sample": [[0.1], [0.5], [0.9]],
            "gp_historical_info": {
                "points_sampled": [
                        {"value_var": 0.01, "value": 0.1, "point": [0.0]},
                        {"value_var": 0.01, "value": 0.2, "point": [1.0]}
                    ],
                },
            "domain_info": {
                "domain_type": "tensor_product"
                "dim": 1,
                },
            "covariance_info": {
                "covariance_type": "square_exponential",
                "hyperparameters": [1.0, 1.0],
                },
        }

    """

    points_to_sample = ListOfPointsInDomain()
    gp_historical_info = GpHistoricalInfo()
    domain_info = DomainInfo()
    covariance_info = CovarianceInfo(
            missing=CovarianceInfo().deserialize({}),
            )


class GpEndpointResponse(StrictMappingSchema):

    """A base schema for the endpoint name.

    **Output fields**

        :endpoint: the endpoint that was called

    **Example Response**

    .. sourcecode:: http

        {
            "endpoint":"gp_mean_var",
        }

    """

    endpoint = colander.SchemaNode(colander.String())


class GpMeanMixinResponse(StrictMappingSchema):

    """A mixin response colander schema for the mean of a gaussian process.

    **Output fields**

        :mean: list of the means of the GP at ``points_to_sample`` (:class:`moe.views.schemas.ListOfFloats`)

    **Example Response**

    .. sourcecode:: http

        {
            "mean": ["0.0873832198661","0.0130505261903","0.174755506336"],
        }

    """

    mean = ListOfFloats()


class GpVarMixinResponse(StrictMappingSchema):

    """A mixin response colander schema for the [co]variance of a gaussian process.

    **Output fields**

        :variance: matrix of covariance of the GP at ``points_to_sample`` (:class:`moe.views.schemas.MatrixOfFloats`)

    **Example Response**

    .. sourcecode:: http

        {
            "var": [
                    ["0.228910114429","0.0969433771923","0.000268292907969"],
                    ["0.0969433771923","0.996177332647","0.0969433771923"],
                    ["0.000268292907969","0.0969433771923","0.228910114429"]
                ],
        }

    """

    var = MatrixOfFloats()


class GpVarDiagMixinResponse(StrictMappingSchema):

    """A mixin response colander schema for the variance of a gaussian process.

    **Output fields**

        :variance: list of variances of the GP at ``points_to_sample``; i.e., diagonal of the ``variance`` response from gp_mean_var (:class:`moe.views.schemas.ListOfFloats`)

    **Example Response**

    .. sourcecode:: http

        {
            "var": ["0.228910114429","0.996177332647","0.228910114429"],
        }

    """

    var = ListOfFloats()


class GpMeanResponse(GpEndpointResponse, GpMeanMixinResponse):

    """A gp_mean response colander schema.

    **Output fields**

        :endpoint: the endpoint that was called
        :mean: list of the means of the GP at ``points_to_sample`` (:class:`moe.views.schemas.ListOfFloats`)

    **Example Response**

    See composing members' docstrings.

    """

    pass


class GpVarResponse(GpEndpointResponse, GpVarMixinResponse):

    """A gp_var response colander schema.

    **Output fields**

        :endpoint: the endpoint that was called
        :variance: matrix of covariance of the GP at ``points_to_sample`` (:class:`moe.views.schemas.MatrixOfFloats`)

    **Example Response**

    See composing members' docstrings.

    """

    pass


class GpVarDiagResponse(GpEndpointResponse, GpVarDiagMixinResponse):

    """A gp_var_diag response colander schema.

    **Output fields**

        :endpoint: the endpoint that was called
        :variance: list of variances of the GP at ``points_to_sample``; i.e., diagonal of the ``variance`` response from gp_mean_var (:class:`moe.views.schemas.ListOfFloats`)

    **Example Response**

    See composing members' docstrings.

    """

    pass


class GpMeanVarResponse(GpMeanResponse, GpVarMixinResponse):

    """A gp_mean_var response colander schema.

    **Output fields**

        :endpoint: the endpoint that was called
        :mean: list of the means of the GP at ``points_to_sample`` (:class:`moe.views.schemas.ListOfFloats`)
        :variance: matrix of covariance of the GP at ``points_to_sample`` (:class:`moe.views.schemas.MatrixOfFloats`)

    **Example Response**

    See composing members' docstrings.

    """

    pass


class GpMeanVarDiagResponse(GpMeanResponse, GpVarDiagMixinResponse):

    """A gp_mean_var_diag response colander schema.

    **Output fields**

        :endpoint: the endpoint that was called
        :mean: list of the means of the GP at ``points_to_sample`` (:class:`moe.views.schemas.ListOfFloats`)
        :variance: list of variances of the GP at ``points_to_sample``; i.e., diagonal of the ``variance`` response from gp_mean_var (:class:`moe.views.schemas.ListOfFloats`)

    **Example Response**

    .. sourcecode:: http

    See composing members' docstrings.

    """

    pass


class GpEiRequest(StrictMappingSchema):

    """A gp_ei request colander schema.

    **Required fields**

        :points_to_evaluate: list of points in domain to calculate Expected Improvement (EI) at (:class:`moe.views.schemas.ListOfPointsInDomain`)
        :gp_historical_info: a :class:`moe.views.schemas.GpHistoricalInfo` object of historical data

    **Optional fields**

        :points_being_sampled: list of points in domain being sampled in concurrent experiments (default: []) (:class:`moe.views.schemas.ListOfPointsInDomain`)
        :mc_iterations: number of Monte Carlo (MC) iterations to perform in numerical integration to calculate EI
        :max_num_threads: maximum number of threads to use in computation (default: 1)
        :covariance_info: a :class:`moe.views.schemas.CovarianceInfo` dict of covariance information

    **Example Minimal Request**

    .. sourcecode:: http

        Content-Type: text/javascript

        {
            "points_to_evaluate": [[0.1], [0.5], [0.9]],
            "gp_historical_info": {
                "points_sampled": [
                        {"value_var": 0.01, "value": 0.1, "point": [0.0]},
                        {"value_var": 0.01, "value": 0.2, "point": [1.0]}
                    ],
                },
            "domain_info": {
                "dim": 1,
                },
        }

    **Example Full Request**

    .. sourcecode:: http

        Content-Type: text/javascript

        {
            "points_to_evaluate": [[0.1], [0.5], [0.9]],
            "points_being_sampled": [[0.2], [0.7]],
            "mc_iterations": 10000,
            "max_num_threads": 1,
            "gp_historical_info": {
                "points_sampled": [
                        {"value_var": 0.01, "value": 0.1, "point": [0.0]},
                        {"value_var": 0.01, "value": 0.2, "point": [1.0]}
                    ],
                },
            "domain_info": {
                "domain_type": "tensor_product"
                "dim": 1,
                },
            "covariance_info": {
                "covariance_type": "square_exponential",
                "hyperparameters": [1.0, 1.0],
                },
        }

    """

    points_to_evaluate = ListOfPointsInDomain()
    points_being_sampled = ListOfPointsInDomain(
            missing=[],
            )
    mc_iterations = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=1),
            missing=DEFAULT_EXPECTED_IMPROVEMENT_MC_ITERATIONS,
            )
    max_num_threads = colander.SchemaNode(
            colander.Int(),
            validator=colander.Range(min=1, max=MAX_ALLOWED_NUM_THREADS),
            missing=DEFAULT_MAX_NUM_THREADS,
            )
    gp_historical_info = GpHistoricalInfo()
    domain_info = DomainInfo()
    covariance_info = CovarianceInfo(
            missing=CovarianceInfo().deserialize({}),
            )


class GpEiResponse(StrictMappingSchema):

    """A gp_ei response colander schema.

    **Output fields**

        :endpoint: the endpoint that was called
        :expected_improvement: list of calculated expected improvements (:class:`moe.views.schemas.ListOfExpectedImprovements`)

    **Example Response**

    .. sourcecode:: http

        {
            "endpoint":"gp_ei",
            "expected_improvement":["0.197246898375","0.443163755117","0.155819546878"]
        }

    """

    endpoint = colander.SchemaNode(colander.String())
    expected_improvement = ListOfExpectedImprovements()
