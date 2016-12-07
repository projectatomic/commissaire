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

@list
@cluster
Feature: Listing Clusters

  @anonymous
  Scenario: List all clusters without authentication
     Given we are anonymous
      when we list all clusters
      then commissaire will deny access

  Scenario: List all clusters with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
      when we list all clusters
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is ['honeynut']
