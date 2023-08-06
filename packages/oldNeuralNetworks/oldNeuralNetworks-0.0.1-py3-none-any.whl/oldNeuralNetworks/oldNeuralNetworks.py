import numpy as np

class ARTNeuralNetwork:
    def __init__(self, num_input, vigilance_parameter, choice_parameter):
        self.num_input = num_input
        self.vigilance_parameter = vigilance_parameter
        self.choice_parameter = choice_parameter
        self.weights = None
        self.classes = []

    def train(self, data):
        self.classes = np.unique(data[:, -1])
        self.weights = np.zeros((len(self.classes), self.num_input))
        for sample in data:
            input_vector = sample[:-1]
            class_label = sample[-1]
            matching_unit = self._find_matching_unit(input_vector)
            if matching_unit is not None:
                self._update_weights(matching_unit, input_vector)
            else:
                self._create_new_category(input_vector, class_label)

    def predict(self, input_vector):
        matching_unit = self._find_matching_unit(input_vector)
        if matching_unit is not None:
            class_label = self.classes[matching_unit]
            return class_label
        else:
            return None

    def _find_matching_unit(self, input_vector):
        for i, weights in enumerate(self.weights):
            if np.all(input_vector >= self.choice_parameter * weights):
                return i
        return None

    def _update_weights(self, matching_unit, input_vector):
        self.weights[matching_unit] = np.maximum(
            self.weights[matching_unit], input_vector
        )

    def _create_new_category(self, input_vector, class_label):
        new_category = np.copy(input_vector)
        self.weights = np.vstack((self.weights, new_category))
        self.classes = np.append(self.classes, class_label)