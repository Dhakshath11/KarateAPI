@PostRequest
Feature: Create user in DB

  Background:
    * url baseURL
    * header Accept = 'application/json'
    * header x-api-key = 'reqres-free-v1'

  @CreateNewUser
  Scenario: Create New User
    Given path 'api/users'
    And request {"name": "morpheus", "job": "leader"}
    When method POST
    Then status 201
    And print response

  @RegisterNewUser
  Scenario: Register New User
    Given path 'api/register'
    And request {"email": "eve.holt@reqres.in", "password": "pistol"}
    When method POST
    Then status 200
    And print response

  @SuccessfulLogin
  Scenario: Login Successfully
    Given path 'api/login'
    And request {"email": "eve.holt@reqres.in", "password": "cityslicka"}
    When method POST
    Then status 200
    And print response

  @UnSuccessfulLogin
  Scenario: Login UnSuccessfully
    Given path 'api/login'
    And request {"email": "peter@klaven"}
    When method POST
    Then status 400
    And print response