###
# Copyright (c) 2014, Kari Hautio
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.schedule as schedule
import supybot.world as world

from xmlrpclib import ServerProxy
import time

APIURL = "http://www.rcgroups.com/forums/mobiquo/mobiquo.php"
POSTURL = "http://www.rcgroups.com/forums/showthread.php?"

class RCGroups(callbacks.Plugin):
    """The behaviour is set via configuration parameters"""
    threaded = False

    def __init__(self, irc):
        self.__parent = super(RCGroups, self)
        self.__parent.__init__(irc)
        self.xmlrpc = ServerProxy(APIURL)
        self.lastseen = {}
        self.irc = irc
        # following is workaround for hanging timer
        try:
            schedule.removeEvent(name=self.name())
        except:
            pass
        self._schedule_next_event()

    def _poll(self):
        tochannel = self.registryValue('postChannel')
        if tochannel:
            irc = self.irc
            server = self.xmlrpc
            lastseen = self.lastseen
            if tochannel in irc.state.channels:
                for rcgthread in self.registryValue('watchedThreads').split():
                    response = server.get_thread(rcgthread, 0, 0)
                    lastpost = response.get('total_post_num')
                    if rcgthread in lastseen:
                        if lastpost > lastseen[rcgthread]:
                            response = server.get_thread(rcgthread, lastseen[rcgthread], lastpost)
                            for post in response.get('posts'):
                                message = "New post in '%s' by %s: %sp=%s" % (response.get('topic_title').data, post.get('post_author_name').data, POSTURL, post.get('post_id'))
                                irc.queueMsg(ircmsgs.privmsg(tochannel, message))
                            lastseen[rcgthread] = lastpost
                    else:
                        lastseen[rcgthread] = lastpost
        self._schedule_next_event()

    def _schedule_next_event(self):
        period = self.registryValue('pollInterval')
        if period > 0:
            schedule.addEvent(self._poll, time.time() + period,
                              name=self.name())

Class = RCGroups

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
