Feature: Manipulating Hosts In A Cluster

  Scenario: Examining hosts in a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
      when we get hosts in the cluster honeynut
      then commissaire will deny access

  Scenario: Checking for a host in a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
      when we check for host 10.2.0.2 in the cluster honeynut
      then commissaire will deny access

  Scenario: Verifying hosts are not implicitly added to clusters (1)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
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
       and we have a host at 10.2.0.2
      when we get hosts in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is []

  Scenario: Verifying hosts are not implicitly added to clusters (3)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
      when we check for host 10.2.0.2 in the cluster honeynut
      then commissaire will allow access
       and commissaire will note it's not found

  Scenario: Adding a host to a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
      when we add host 10.2.0.2 to the cluster honeynut
      then commissaire will deny access

  Scenario: Adding a host to a cluster with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
      when we add host 10.2.0.2 to the cluster honeynut
      then commissaire will allow access
       and commissaire will note success

  Scenario: Verifying a cluster after adding a host (1)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
      when we get the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a dict
       and the provided cluster total hosts is 1

  Scenario: Verifying a cluster after adding a host (2)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
      when we get hosts in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is ['10.2.0.2']

  Scenario: Verifying a cluster after adding a host (3)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
      when we check for host 10.2.0.2 in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success

  Scenario: Removing a host from a cluster without authentication
     Given we are anonymous
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
      when we remove host 10.2.0.2 from the cluster honeynut
      then commissaire will deny access

  Scenario: Removing a host from a cluster with authentication
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
      when we remove host 10.2.0.2 from the cluster honeynut
      then commissaire will allow access
       and commissaire will note success

  Scenario: Verifying a cluster after adding and removing a host (1)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
       and we have removed host 10.2.0.2 from cluster honeynut
      when we get the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a dict
       and the provided cluster total hosts is 0

  Scenario: Verifying a cluster after adding and removing a host (2)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
       and we have removed host 10.2.0.2 from cluster honeynut
      when we get hosts in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is []

  Scenario: Verifying a cluster after adding and removing a host (3)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
       and we have removed host 10.2.0.2 from cluster honeynut
      when we check for host 10.2.0.2 in the cluster honeynut
      then commissaire will allow access
       and commissaire will note it's not found

  Scenario: Directly setting a cluster host list without authentication
     Given we are anonymous
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
      when we set the host list for cluster honeynut to ["10.2.0.2"],
      then commissaire will deny access

  Scenario Outline: Directly setting a cluster host list
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
      when we set the host list for cluster honeynut to <json>
      then commissaire will allow access
       and commissaire will note <note>
       and the host 10.2.0.2 <will> be in the cluster honeynut

  Examples:
    | json                                    | note          | will     |
    | 'Part of this nutritious breakfast'     | a bad request | will not |
    | {'old': ['bogus'], 'new': ['10.2.0.2']} | a conflict    | will not |
    | {'old': [], 'new': ['10.2.0.2']}        | success       | will     |

  Scenario: Deleting a host also removes it from its cluster (1)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
       and we have deleted host 10.2.0.2
      when we get the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a dict
       and the provided cluster total hosts is 0

  Scenario: Deleting a host also removes it from its cluster (2)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
       and we have deleted host 10.2.0.2
      when we get hosts in the cluster honeynut
      then commissaire will allow access
       and commissaire will note success
       and commissaire will provide a list
       and the provided data is []

  Scenario: Deleting a host also removes it from its cluster (3)
     Given we have a valid username and password
       and we have a cluster named honeynut
       and we have a host at 10.2.0.2
       and we have added host 10.2.0.2 to cluster honeynut
       and we have deleted host 10.2.0.2
      when we check for host 10.2.0.2 in the cluster honeynut
      then commissaire will allow access
       and commissaire will note it's not found

   Scenario: Creating a new host with an invalid cluster name
      Given we have a valid username and password
        and we set the cluster name to headache
       when we create the host 10.2.0.2
       then commissaire will allow access
        and commissaire will note a conflict

   Scenario: Creating a new host with a valid cluster name (1)
      Given we have a valid username and password
        and we have a cluster named honeynut
        and we set the cluster name to honeynut
        and we have a host at 10.2.0.2
       when we get the cluster honeynut
       then commissaire will allow access
        and commissaire will note success
        and commissaire will provide a dict
        and the provided cluster total hosts is 1

   Scenario: Creating a new host with a valid cluster name (2)
      Given we have a valid username and password
        and we have a cluster named honeynut
        and we set the cluster name to honeynut
        and we have a host at 10.2.0.2
       when we get hosts in the cluster honeynut
       then commissaire will allow access
        and commissaire will note success
        and commissaire will provide a list
        and the provided data is ['10.2.0.2']

   Scenario: Creating a new host with a valid cluster name (3)
      Given we have a valid username and password
        and we have a cluster named honeynut
        and we set the cluster name to honeynut
        and we have a host at 10.2.0.2
       when we check for host 10.2.0.2 in the cluster honeynut
       then commissaire will allow access
        and commissaire will note success
