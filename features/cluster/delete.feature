# Copyright (C) 2016  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

Feature: Deleting A Cluster

  Scenario: Deleting a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
      when we delete the cluster honeynut
      then commissaire will deny access

  Scenario: Deleting a cluster with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
      when we delete the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
