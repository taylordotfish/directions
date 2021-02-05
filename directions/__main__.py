# Copyright (C) 2019 taylor.fish <contact@taylor.fish>
#
# This file is part of random-directions.
#
# random-directions is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# random-directions is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with random-directions. If not, see <https://www.gnu.org/licenses/>.

from . import directions
from .directions import CACHE_DIR, log
import os
import sys
import traceback

LOG_PATH = os.path.join(CACHE_DIR, "directions.log")


def main():
    with open(LOG_PATH, "a", encoding="utf8") as f:
        directions.set_log_file(f)
        try:
            directions.run()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
        except Exception:
            log(traceback.format_exc())
            sys.exit(1)
        directions.set_log_file(None)
    try:
        sys.stdout.close()
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
