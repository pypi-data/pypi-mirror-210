# Changelog

## Version: 0.1.23

Release date: 25.05.2023

- Updated `ResponseCodes` method `to_string` messages.
- Moved UART baud rate enum from UART Open request to `dpa` submodule.

## Version: 0.1.22

Release date: 23.05.2023

- Fixed rcode value comparison condition in `ResponseCodes` method `to_string`

## Version: 0.1.21

Release date: 22.05.2023

### Changes

- Added check for values out of range to `ResponseCodes` method `to_string`
- Fixed missing return statements

## Version: 0.1.20

Release date: 20.05.2023

### Changes

- Added missing DPA error constants to `ResponseCodes`
- Added string representation of `ResponseCodes` values and `to_string` classmethod
- Used ResponseCodes constants throughout the library where unused

## Version: 0.1.19

Release date: 17.05.2023

### Changes

- Added Device Exploration (unfinished due to pending changes in IQRF Gateway Daemon), UART and Thermometer peripheral request, responses and response factories
- Added `terminate` method to `MqttTransport` to disconnect client and stop event loop peacefully
- MQTT transport initialization now waits for subscription confirmation instead of connection confirmation

## Version: 0.1.18

Release date: 10.05.2023

### Changes

- Added `is_connected` method to `MqttTransport`
- Fixed matching of sent requests and received responses in MQTT transport
- MQTT transport now distinguishes DPA request timeout without user-specified timeout, DPA request timeout with user-specified timeout, JSON request timeout

## Version: 0.1.17

Release date: 09.05.2023

### Changes

- Fixed validation of `IRequest` parameter `nadr`

## Version: 0.1.16

Release date: 03.05.2023

### Changes

- Added setters for EEPROM requests
- Fixed generation of random UUID message ID for requests
- Separated DPA and JSON timeout in MQTT transport
- Added optional timeout parameter to requests

## Version: 0.1.15

Release date: 02.05.2023

### Changes

- Fixed `peripherals` module submodule imports

## Version: 0.1.14

Release date: 27.04.2023

### Changes

- Changed module tree structure
  - `iqrfpy.messages.requests.<peripheral>` -> `iqrfpy.peripherals.<peripheral>.requests`
  - `iqrfpy.messages.responses.<peripheral>` -> `iqrfpy.peripherals.<peripheral>.responses`
- Moved `async_response`, `confirmation`, `irequest`, `iresponse` and `response_factory` submodules to `iqrfpy` module
- Renamed `peripheral_messages` submodule to `messages`
- Added specific peripheral submodule imports to `periphral` submodule
- Added missing submodule imports
- Added `send_and_receive` method overloads for individual requests and responses to `MqttTransport`

## Version: 0.1.13

Release date: 26.04.2023

### Changes

- Added EEPROM peripheral requests, responses and response factories
- Added EEPROM peripheral to `Common` class auxiliary methods
- Changed `response_factory` Coordinator response imports to named namespace import
- Added `iqrfpy.peripheral_messages` module containing imports and wildcard import for all available requests and responses
- Simplified validation of request parameters, deferring much of the work to the DPA layer

## Version: 0.1.12

Release date: 24.04.2023

### Changes

- Added LEDG peripheral requests, responses and response factories
- Fixed undefined variable warning when selecting a response factory
- Added wildcard imports to `iqrfpy.exceptions` module
- Added `iqrfpy.utils.validators` module containing validator classes for DPA and JSON responses
- Updated validation of DPA and JSON responses in factory methods
- Added optional timeout parameter to `receive` method of `MqttTransport`
- `MqttTransport` onmessage callback now checks if received JSON API response indicates DPA request timeout

## Version: 0.1.11

Release date: 20.04.2023

### Changes

- Added `LOCAL_DEVICE_ADDR` and `BROADCAST_ADDR` constants to `iqrfpy.utils.dpa` module
- Added `list_to_hex_string` auxiliary method to `Common` class
- Changed `IRequest` validation of `nadr` to include local device, temporary iqmesh and broadcast addresses
- Added `OsReadFlags` and `OsReadSlotLimits` dataclasses
- Added response data getters to OS `ReadResponse`

## Version: 0.1.10

Release date: 20.04.2023

### Changes

- Added missing wildcard imports to `response_factory` module
- Removed `synchronous` parameter from `MqttTransport`
- `MqttTransport` now passes received message to user-specified callback regardless of communication mode
- Implemented method `send_and_receive` of `MqttTransport`

## Version: 0.1.9

Release date: 20.04.2023

### Changes

- Added OS `ReadResponse` response factory
- Added synchronous MQTT transport communication
- Added `TransportNotConnectedError` and `MessageNotReceivedError` exceptions

## Version: 0.1.8

Release date: 19.04.2023

### Changes

- Unified class file name and class name cases
- Moved validation of `AuthorizeBondRequest` parameters to `AuthorizeBondParams` class
- Added validation of `AuthorizeBondParams` count to `AuthorizeBondRequest`
- Added LEDR peripheral requests, responses and response factories
- Added OS peripheral Read request and response
- Added exceptions for unsupported peripherals and peripheral commands
- `ResponseFactory` methods now throw relevant exceptions when an unknown or unsupported peripheral or peripheral command is processed
- Added method `send_and_receive` to `ITransport`
- Added abstract method decorators to `ITransport` methods
- Added `MqttTransportParams` dataclass and removed individual parameters from `MqttTransport` constructor
- Added asynchronous MQTT transport communication
- Added docstrings for enums

## Version: 0.1.7

Release date: 17.04.2023

### Changes

- Added `receive` and `confirmation` methods to `ITransport`

## Version: 0.1.6

Release date: 15.04.2023

### Changes

- Added module `iqrfpy.utils.dpa` containing DPA constants
- Replaced magical constants throughout the source code with named DPA constants
- Exposed request and response submodules imports

## Version: 0.1.5

Release date: 07.04.2023

### Changes

- Added module `iqrfpy.exceptions` containing custom exceptions
- Replaced generic Error types with custom exceptions

## Version: 0.1.4

Release date: 06.04.2023

### Changes

- `ITransport` methods now raise `NotImplementedError`
- Added `set_receive_callback` method to `ITransport`
- Removed `receive` and `receive_async` methods from `ITransport`

## Version: 0.1.3

Release date: 02.04.2023

### Changes

- Added `AuthorizeBondParams` dataclass for `AuthorizeBondRequest`
- Added validation of `AuthorizeBondRequest` parameters
- Added response factory for `AuthorizeBondResponse`

## Version: 0.1.2

Release date: 27.03.2023

### Changes

- Added wildcard imports for response factories

## Version: 0.1.1 (unreleased)

Release date: N/A

### Changes

- Unified module name cases
- Added typechecking for classes
- Added enum class `IntEnumMember` with `has_value` method
- Changed existing integer enums to extend `IntEnumMember`
- Added response factories to parse DPA and JSON responses into response objects
- Renamed `data` parameter to `dpa` in DPA response factory methods
- Renamed `data` parameter to `json` in JSON response factory methods
- Moved `IRequest` class to `requests` module
- Moved `AsyncResponse`, `Confirmation` and `IResponse` class to `responses` module
- Added more auxiliary methods to `Common` class

## Version: 0.1.0 (unreleased)

Release date: N/A

### Changes

- Basic project structure
- Added peripheral enums
- Added peripheral request and response command enums
- Added message type enums
- Added class Common providing auxiliary functions
- Added abstract classes for requests, responses and transports
- Added asynchronous responses
- Added confirmation message
- Added Coordinator peripheral requests and responses
- Added MQTT transport
- Added simple tests for Coordinator peripheral, enums and Common class
