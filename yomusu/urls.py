# Copyright 2008 Google Inc.
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


from django.conf.urls.defaults import *

urlpatterns = patterns(
    '',
    (r'^mathlabo/$', 'mathlabo.mathviews.index'),
    (r'^mathlabo/add$', 'mathlabo.mathviews.add_formula'),
    (r'^mathlabo/get$', 'mathlabo.mathviews.get_formula'),
    (r'^mathlabo/del$', 'mathlabo.mathviews.delete_formula'),
    (r'^mathlabo/dispose$', 'mathlabo.mathviews.dispose_session'),
    (r'^mathlabo/manage$', 'mathlabo.mathviews.management_tool'),
    
    
    (r'^mathlabo/qr/$', 'mathlabo.qrviews.index'),
    (r'^mathlabo/qr/add$', 'mathlabo.qrviews.add_qrcode'),
    (r'^mathlabo/qr/get$', 'mathlabo.qrviews.get_qrcode'),
    (r'^mathlabo/qr/del$', 'mathlabo.qrviews.delete_qrcode'),

)
