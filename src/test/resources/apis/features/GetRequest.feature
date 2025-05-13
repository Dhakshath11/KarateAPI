@GetRequest
Feature: Get user from DB

  Background:
    * url baseURL
    * header Accept = 'application/json'
    * header x-api-key = 'reqres-free-v1'

#  @Get_Example
#  Scenario: Retrieve user list
#    Given url 'https://reqres.in/api/users?page=2'
#    Then status 200
#    And print response

  @GetExistingUser
  Scenario: Retrieve existing user information
    Given path 'api/users/2'
    When method GET
    Then status 200
    And print response

  @GetNonExistingUser
  Scenario: Retrieve non-existing user information
    Given path 'api/users/23'
    When method GET
    Then status 404
    And print response

  @GetExistingUserList
  Scenario: Retrieve existing user list
    Given path 'api/users'
    And param page = 2
    When method GET
    Then status 200
    And print response

  @GetDelayedResponse
  Scenario: Retrieve delayed response
    Given path 'api/users'
    And param delay = 3
    When method GET
    Then status 200
    And print response