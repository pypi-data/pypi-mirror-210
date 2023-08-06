import joblib
from typing import List
from livestream_monitor_classifier.helper.preprocess import Preprocess
from pathlib import Path

path = Path(__file__).parent/'model/sklearn_MNB.model'


class Classifier:
  def __init__(self):
    self.model = joblib.load(path)
    self.preprocess_get = Preprocess().get
    self.preprocess_get_list = Preprocess().get_list
    
  def predict(self, input: str):
    predicted_preprocessed = self.preprocess_get(input)
    predicted_tf = self.model.tf_vectorizer.transform([predicted_preprocessed])
    predicted_result = self.model.predict(predicted_tf)
    return predicted_result
    
  def predict_list(self, inputs: List[str]):
    predicted_preprocessed_list = self.preprocess_get_list(inputs)
    predicted_tf = self.model.tf.transform(predicted_preprocessed_list)
    predicted_result = self.model.predict(predicted_tf)
    return predicted_result
  