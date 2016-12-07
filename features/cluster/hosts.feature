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

@cluster
Feature: Manipulating Hosts In A Cluster

  @anonymous
  Scenario: Examining hosts in a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
      when we get hosts in the cluster honeynut
      then commissaire will deny access

  @anonymous
  Scenario: Checking for a host in a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
      when we check for host 192.168.152.110 in the cluster honeynut
      then commissaire will deny access

  Scenario: Verifying hosts are not implicitly added to clusters (1)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
      when we get the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a dict
       and the provided cluster total hosts is 0
       and the provided cluster available hosts is 0
       and the provided cluster unavailable hosts is 0

  Scenario: Verifying hosts are not implicitly added to clusters (2)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
      when we get hosts in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is []

  Scenario: Verifying hosts are not implicitly added to clusters (3)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
      when we check for host 192.168.152.110 in the cluster honeynut
      then commissaire will allow access
       and commissaire will note it's not found

  @anonymous
  Scenario: Adding a host to a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
      when we add host 192.168.152.110 to the cluster honeynut
      then commissaire will deny access

  Scenario: Adding a host to a cluster with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
      when we add host 192.168.152.110 to the cluster honeynut
      then commissaire will allow access
       and commissaire will note success

  Scenario: Verifying a cluster after adding a host (1)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
      when we get the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a dict
       and the provided cluster total hosts is 1

  Scenario: Verifying a cluster after adding a host (2)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
      when we get hosts in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is ['192.168.152.110']

  Scenario: Verifying a cluster after adding a host (3)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
      when we check for host 192.168.152.110 in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success

  @anonymous
  Scenario: Removing a host from a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
      when we remove host 192.168.152.110 from the cluster honeynut
      then commissaire will deny access

  Scenario: Removing a host from a cluster with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
      when we remove host 192.168.152.110 from the cluster honeynut
      then commissaire will allow access
       and commissaire will note success

  Scenario: Verifying a cluster after adding and removing a host (1)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
       and we have removed host 192.168.152.110 from cluster honeynut
      when we get the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a dict
       and the provided cluster total hosts is 0

  Scenario: Verifying a cluster after adding and removing a host (2)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
       and we have removed host 192.168.152.110 from cluster honeynut
      when we get hosts in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is []

  Scenario: Verifying a cluster after adding and removing a host (3)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
       and we have removed host 192.168.152.110 from cluster honeynut
      when we check for host 192.168.152.110 in the cluster honeynut
      then commissaire will allow access
       and commissaire will note it's not found

  @anonymous
  Scenario: Directly setting a cluster host list without authentication
     Given we are anonymous
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
      when we set the host list for cluster honeynut to ["192.168.152.110"],
      then commissaire will deny access

  Scenario Outline: Directly setting a cluster host list
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
      when we set the host list for cluster honeynut to <json>
      then commissaire will allow access
       and commissaire will note <note>
       and the host 192.168.152.110 <will> be in the cluster honeynut

  Examples:
    | json                                    | note          | will     |
    | 'Part of this nutritious breakfast'     | a bad request | will not |
    | {'old': ['bogus'], 'new': ['192.168.152.110']} | a conflict    | will not |
    | {'old': [], 'new': ['192.168.152.110']}        | success       | will     |

  @delete
  Scenario: Deleting a host also removes it from its cluster (1)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
       and we have deleted host 192.168.152.110
      when we get the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a dict
       and the provided cluster total hosts is 0

  @delete
  Scenario: Deleting a host also removes it from its cluster (2)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
       and we have deleted host 192.168.152.110
      when we get hosts in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is []

  @delete
  Scenario: Deleting a host also removes it from its cluster (3)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and a host already exists at 192.168.152.110
       and we have added host 192.168.152.110 to cluster honeynut
       and we have deleted host 192.168.152.110
      when we check for host 192.168.152.110 in the cluster honeynut
      then commissaire will allow access
       and commissaire will note it's not found

   @create @slow
   Scenario: Creating a new host with an invalid cluster name
      Given we have a valid username and password
        and we set the cluster name to headache
       when we create the host at 192.168.152.110
       then commissaire will allow access
        and commissaire will note a conflict

   @slow @create
   Scenario: Creating a new host with a valid cluster name (1)
      Given we have a valid username and password
        and we have a cluster named honeynut
        and we set the cluster name to honeynut
        and we have a host at 192.168.152.110
       when we get the cluster honeynut
       then commissaire will allow access
        and commissaire will note success
        and commissaire will provide a dict
        and the provided cluster total hosts is 1

   @slow @create
   Scenario: Creating a new host with a valid cluster name (2)
      Given we have a valid username and password
        and we have a cluster named honeynut
        and we set the cluster name to honeynut
        and we have a host at 192.168.152.110
       when we get hosts in the cluster honeynut
       then commissaire will allow access
        and commissaire will note success
        and commissaire will provide a list
        and the provided data is ['192.168.152.110']

   @slow @create
   Scenario: Creating a new host with a valid cluster name (3)
      Given we have a valid username and password
        and we have a cluster named honeynut
        and we set the cluster name to honeynut
        and we have a host at 192.168.152.110
       when we check for host 192.168.152.110 in the cluster honeynut
       then commissaire will allow access
        and commissaire will note success
