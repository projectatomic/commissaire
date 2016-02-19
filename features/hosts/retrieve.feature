Feature: Retrieving Hosts

  Scenario: Retrieve existing host without authentication
     Given we are anonymous
       and we have a host at 10.2.0.2
      when we get the host 10.2.0.2
      then commissaire will deny access

  Scenario: Retrieve existing host with authentication
     Given we have a valid username and password
       and we have a host at 10.2.0.2
      when we get the host 10.2.0.2
      then commissaire will allow access
      and commissaire will return the single host

  Scenario: Retrieve nonexisting host with authentication
     Given we have a valid username and password
      when we get the host 10.9.9.9
      then commissaire will allow access
      and commissaire will return no host
