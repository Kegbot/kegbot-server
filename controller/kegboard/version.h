#pragma once

// Version of the kegboard firmware. This is bumped whenever there's a
// significant new feature in the firmware.
//
// Version history:
//   v4 (2010-01-04)
//     Initial version number.
//   v5 (2010-01-10)
//     Fix issue that caused flow events to be reported too frequently.
//   v6 (2010-09-22)
//     Added auth_token message.
#define FIRMWARE_VERSION 6

#define BUILD_DATE __DATE__
#define BUILD_TIME __TIME__
