#!/bin/bash
#
# This file is part of Silverbot.
#
# Silverbot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Silverbot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Silverbot.  If not, see <http://www.gnu.org/licenses/>.
#

# Currently, this file is awaiting construction of the various components
# 1) Get current price (yahoo finance)
# 2) Collect recently-filled bids (gmail order fulfillment)
# 3) TWB:
#      Place offset asks
#      Place supporting bids

(cd price-tracker && sh run.sh &)
