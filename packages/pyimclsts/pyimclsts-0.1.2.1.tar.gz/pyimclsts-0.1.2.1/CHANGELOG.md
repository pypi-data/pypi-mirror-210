# Change log:

## Version 0.1.2.1

### Changed
    - _peers table now keeps track of entity of unknown vehicles and waits for their announcement to "upgrade" their entry.
### Fixed
    - Fixed wrong subscription in .update_peers()

## Version 0.1.2

### Added
    - subscriber now has a method called .print_information()
    - subscriber now has a method called .stop()
    - .subscribe_async() can subscribe to categories of messages

### Changed
    - Rename _base_templates.py to _base.py
    - messages' Attributes do not use immutable_attribute anymore and are now simply a class attribute -> saves memory and works with autocomplete.
    - subscriber also update peers using EntityInfo
    
### Fixed
    - Fixed broken annotations

## Version 0.1.1.7

### Added
    - Messages now have a method called .get_timestamp(). It returns None if the message does not have a header yet.

### Changed
    - Extract messages that have categories to different files, but re-exports them in the messages.py file.
    
### Fixed

### Version 0.1.1.5
    - Fix .block_outgoing() bug

## Version 0.1.1.6

### Added
    
### Changed
    - Delay message deserialization
        - Now messages are deserialized only when passed to functions by the subscriber, so they are kept as bytes as long as possible.
    - Better error message when deserializing unknown inlined message
    - Cleaner example
    
### Fixed
    - Fix unknown_message
        - Remove unnecessary attributes