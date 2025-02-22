# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for `tensorboard.backend.experiment_id`."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

import werkzeug
from werkzeug import test as werkzeug_test

from tensorboard import test as tb_test
from tensorboard.backend import experiment_id


class ExperimentIdMiddlewareTest(tb_test.TestCase):
  """Tests for `ExperimentIdMiddleware`."""

  def setUp(self):
    super(ExperimentIdMiddlewareTest, self).setUp()
    self.app = experiment_id.ExperimentIdMiddleware(self._echo_app)
    self.server = werkzeug_test.Client(self.app, werkzeug.BaseResponse)

  def _echo_app(self, environ, start_response):
    # https://www.python.org/dev/peps/pep-0333/#environ-variables
    data = {
        "eid": environ[experiment_id.WSGI_ENVIRON_KEY],
        "path": environ.get("PATH_INFO", ""),
        "script": environ.get("SCRIPT_NAME", ""),
    }
    body = json.dumps(data, sort_keys=True)
    start_response("200 OK", [("Content-Type", "application/json")])
    return [body]

  def _assert_ok(self, response, eid, path, script):
    self.assertEqual(response.status_code, 200)
    actual = json.loads(response.get_data())
    expected = dict(eid=eid, path=path, script=script)
    self.assertEqual(actual, expected)

  def test_no_experiment_empty_path(self):
    response = self.server.get("")
    self._assert_ok(response, eid="", path="", script="")

  def test_no_experiment_root_path(self):
    response = self.server.get("/")
    self._assert_ok(response, eid="", path="/", script="")

  def test_no_experiment_sub_path(self):
    response = self.server.get("/x/y")
    self._assert_ok(response, eid="", path="/x/y", script="")

  def test_with_experiment_empty_path(self):
    response = self.server.get("/experiment/123")
    self._assert_ok(response, eid="123", path="", script="/experiment/123")

  def test_with_experiment_root_path(self):
    response = self.server.get("/experiment/123/")
    self._assert_ok(response, eid="123", path="/", script="/experiment/123")

  def test_with_experiment_sub_path(self):
    response = self.server.get("/experiment/123/x/y")
    self._assert_ok(response, eid="123", path="/x/y", script="/experiment/123")


if __name__ == "__main__":
  tb_test.main()
