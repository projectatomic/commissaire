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

@retrieve
@status
Feature: Retrieving Status

  @anonymous
  Scenario: Retrieve status without authentication
     Given we are anonymous
      when we get status
      then commissaire will deny access

  Scenario: Retrieve status with authentication
     Given we have a valid username and password
      when we get status
      then commissaire will allow access
      and commissaire will return status

  @clientcert
  Scenario: Retrieve status with client certificate
     Given we have client as a client certificate
      when we get status
      then commissaire will allow access
      and commissaire will return status

  @clientcert
  Scenario: Retrieve status with invalid client certificate
     Given we have self-client as a client certificate
      when we get status
      then commissaire ssl will error

  @clientcert
  Scenario: Retrieve status with mismatched client certificate
     Given we have other as a client certificate
      when we get status
      then commissaire will deny access
