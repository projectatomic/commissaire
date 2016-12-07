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
@hosts
Feature: Retrieving Hosts

  @anonymous
  Scenario: Retrieve existing host without authentication
     Given we are anonymous
       and a host already exists at 192.168.152.110
      when we get the host 192.168.152.110
      then commissaire will deny access

  Scenario: Retrieve existing host with authentication
     Given we have a valid username and password
       and a host already exists at 192.168.152.110
      when we get the host 192.168.152.110
      then commissaire will allow access
      and commissaire will return the single host

  Scenario: Retrieve nonexisting host with authentication
     Given we have a valid username and password
      when we get the host 192.168.152.254
      then commissaire will allow access
      and commissaire will return no host

  @ssh
  @anonymous
  Scenario: Retrieve existing host credentials without authentication
    Given we are anonymous
      and a host already exists at 192.168.152.110
     when we get host credentials for 192.168.152.110
     then commissaire will deny access

  @ssh
  Scenario: Retrieve existing host with authentication
    Given we have a valid username and password
      and a host already exists at 192.168.152.110
     when we get host credentials for 192.168.152.110
     then commissaire will allow access
     and commissaire will return the host credentials

  @anonymous
  @hoststatus
  Scenario: Retrieve existing host status status without authentication
     Given we are anonymous
       and a host already exists at 192.168.152.110
      when we get host status for 192.168.152.110
      then commissaire will deny access

  @hoststatus
  Scenario: Retrieve existing host status with authentication
     Given we have a valid username and password
       and a host already exists at 192.168.152.110
       and we have a cluster named honeynut
       and we add host 192.168.152.110 to the cluster honeynut
      when we get host status for 192.168.152.110
      then commissaire will allow access
      and commissaire will note success
      and commissaire will return the host status
