@DeleteRequest
Feature: Delete user in DB

  Background:
    * url baseURL
    * header Accept = 'application/json'
    * header x-api-key = 'reqres-free-v1'

  @UpdateUser
  Scenario: Delete Existing User
    Given path 'api/users/2'
    When method DELETE
    Then status 204
    And print response

