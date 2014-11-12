This plugin monitors RCGroups forums for activity.

Following configuration parameters can be used to alter behavior

Parameter      (default) - description
pollInterval   (60)      - Interval at which the check for activity (s)
postChannel    ("")      - Channel to post updates to
watchedThreads ("")      - whitespace separated list of thread IDs to follow

If either postChannel or watchedThreads is empty monitoring is effectively disabled.

This plugin uses Tapatalk API for communicating with the Forum.

https://tapatalk.com/api.php

Only get_thread method is currenrly used and implementation should be compatible with
API versions 3 and 4.
