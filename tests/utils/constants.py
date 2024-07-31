"""Constants for testing modules"""

# * `process_survey`
TEST_CREATE_PARTICIPANT_CODE = "17c9d4zc"
TEST_CREATE_MONTH = 36
TEST_CREATE_VALUES = {
    "Quant Expectation": 10.0,
    "Quant Perception": 3.0,
    "Qual Expectation": 3.0,
    "Qual Perception": 2.0,
}

TEST_PIVOT_DF_LEN = 3454

TEST_CALCULATE_BIAS_PARTICIPANT_CODE = "01hv4wn4"
TEST_CALCULATE_BIAS_MONTH = 96
TEST_CALCULATE_BIAS_VALUES = {
    "Quant Expectation": 10.0,
    "Quant Perception": 15.0,
    "Actual": 26.85,
    "Upcoming": 55.49,
}
TEST_CALCULATE_BIAS_PERCEPTION = (
    TEST_CALCULATE_BIAS_VALUES["Actual"]
    - TEST_CALCULATE_BIAS_VALUES["Quant Perception"]
)

TEST_CALCULATE_BIAS_EXPECTATION = (
    TEST_CALCULATE_BIAS_VALUES["Upcoming"]
    - TEST_CALCULATE_BIAS_VALUES["Quant Expectation"]
)

TEST_CALCULATE_SENSITIVITY_MONTH = 96
TEST_CALCULATE_SENSITIVITY_PARTICIPANT_CODE = "k78vuxz0"
TEST_CALCULATE_SENSITIVITY_PERCEPTION_VALUE = 0
TEST_CALCULATE_SENSITIVITY_EXPECTATION_VALUE = -0.3626381

TEST_CALCULATE_SENSITIVITY_PARTICIPANT_CODE_NO_NANS = "3lkzrdod"
TEST_CALCULATE_SENSITIVITY_VALUE_NO_NANS = 0