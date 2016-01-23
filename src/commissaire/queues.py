# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://
"""
All global queues.
"""

from gevent.queue import Queue

#: Input queue for the investigator thread(s)
INVESTIGATE_QUEUE = Queue()


# ROUTER_QUEUE = Queue()
# QUEUES = {
#     "ALL": [Queue(), Queue()],
#     "10.2.0.2": [Queue()],
# }
