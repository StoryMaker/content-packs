#!/usr/bin/env python

import os

#os.system("tx pull -l ru,ar,bs_BA,sr,es,fa,de,mk,ko,fr,rw,vi --minimum-perc=80") # pulling out bs_BA until the scripts deal with renaming the files appropriately ... or does the app handle it?
#os.system("tx pull -l ru,ar,sr,es,fa,de,mk,ko,fr,rw,vi --minimum-perc=80")
os.system("tx pull -l ru,ar,sr,es,fa_IR,de,mk,ko,fr,rw,vi,om,am_ET --minimum-perc=80")
