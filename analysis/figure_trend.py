# Kmax
# Copyright (C) 2012-2015 Paul Gazzillo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from collections import defaultdict
import cPickle as pickle
import locale
import kmaxdata
import numpy
import csv
import string
import math
from pychart import *

use_cached_data = False
if len(sys.argv) > 1 and sys.argv[1] == "--cache":
  use_cached_data = True

datapath = "/mnt/wd20earx/paul/scratch/kmax/data/hpc/"

versions = [
  ("2.6.0",12,2003),
  ("2.6.1",1,2004),
  ("2.6.11",3,2005),
  ("2.6.12",6,2005),
  ("2.6.13",8,2005),
  ("2.6.14",10,2005),
  ("2.6.15",1,2006),
  ("2.6.16",3,2006),
  ("2.6.17",6,2006),
  ("2.6.18",9,2006),
  ("2.6.19",11,2006),
  ("2.6.20",2,2007),
  ("2.6.21",4,2007),
  ("2.6.22",7,2007),
  ("2.6.23",10,2007),
  ("2.6.24",1,2008),
  # ("2.6.25",4,2008),
  ("2.6.26",7,2008),
  ("2.6.27",10,2008),
  ("2.6.28",12,2008),
  ("2.6.29",3,2009),
  ("2.6.30",6,2009),
  ("2.6.31",9,2009),
  ("2.6.32",12,2009),
  ("2.6.33",2,2010),
  ("2.6.34",5,2010),
  ("2.6.35",8,2010),
  ("2.6.36",10,2010),
  ("2.6.37",1,2011),
  ("2.6.38",3,2011),
  ("2.6.39",5,2011),
  ("3.0",7,2011),
  ("3.1",10,2011),
  ("3.2",1,2012),
  ("3.3",3,2012),
  ("3.4",5,2012),
  ("3.5",7,2012),
  ("3.6",9,2012),
  ("3.7",12,2012),
  ("3.8",2,2013),
  ("3.9",4,2013),
  ("3.10",6,2013),
  ("3.11",9,2013),
  ("3.12",11,2013),
  ("3.13",1,2014),
  ("3.14",3,2014),
  ("3.15",6,2014),
  ("3.16",8,2014),
  ("3.17",10,2014),
  ("3.18",12,2014),
  ("3.19",2,2015),
]

data = []

if use_cached_data:
  with open("tmp_data", "rb") as f:
    data = pickle.load(f)
else:
  for version, month, year in versions:
    datafiles = kmaxdata.buildsystem_datafiles(version, path=datapath)
    sys.stderr.write("%s\n" % (datafiles))
    if len(datafiles) == 0:
      continue
    buildsystemdata = {}
    for datafile in datafiles:
      with open(datafile, "rb") as f:
        inputdata = pickle.load(f)
        if inputdata.version == version:
          sys.stderr.write("%s %s\n" % (inputdata.version, inputdata.arch))
          buildsystemdata[inputdata.arch] = inputdata

    allconfigs = set()
    allunits = set()
    compunits = set()
    libunits = set()
    archunits = defaultdict(set)
    for arch in buildsystemdata.keys():
      allconfigs.update(buildsystemdata[arch].config_vars)
      allunits.update(buildsystemdata[arch].compilation_units['compilation_units'])
      allunits.update(buildsystemdata[arch].compilation_units['library_units'])
      compunits.update(buildsystemdata[arch].compilation_units['compilation_units'])
      libunits.update(buildsystemdata[arch].compilation_units['library_units'])
      archunits[arch].update(buildsystemdata[arch].compilation_units['compilation_units'])
      archunits[arch].update(buildsystemdata[arch].compilation_units['library_units'])

    with open(kmaxdata.everycfile_datafile(version, path=datapath), "rb") as f:
      allcfiles = len(f.readlines())

    shared_units = set(allunits)
    archdir_units = [x for x in set(allunits) if x.startswith("arch/")]
    for arch in archunits.keys():
      shared_units.intersection_update(archunits[arch])
    shared_configs = set(allconfigs)
    for arch in archunits.keys():
      shared_configs.intersection_update(buildsystemdata[arch].config_vars)

    minunits = min([len(archunits[x]) for x in archunits.keys()])
    maxunits = max([len(archunits[x]) for x in archunits.keys()])
    minconfigs = min([len(buildsystemdata[x].config_vars) for x in buildsystemdata.keys()])
    maxconfigs = max([len(buildsystemdata[x].config_vars) for x in buildsystemdata.keys()])

    # convert month/year to a decimal year
    year_axis = float(year) + (float(month) - 1) / 12
    data.append((version,
                 year_axis,
                 len(allunits),
                 len(compunits),
                 len(libunits),
                 len(shared_units),
                 len(archdir_units),
                 len(allunits) - len(shared_units) - len(archdir_units),
                 len(allconfigs),
                 len(shared_configs),
                 allcfiles,))

  with open("tmp_data", "wb") as f:
    pickle.dump(data, f)
 
sys.stderr.write("%s\n" % (data))

locale.setlocale(locale.LC_ALL, 'en_US.utf8')

gen_interval = lambda interval: lambda min, max: [int(math.floor(min))]+range(int((min + interval) / interval) * interval, int((max + interval) / interval) * interval, interval)+[int(math.ceil(max))]

width = 180
height = 111
            
# xmax = max([x for x,_ in cdf if x < 20] + [20])

can = canvas.init(None, 'pdf')
size = (width, height)

minyear = min([x for _, x, _, _, _, _, _, _, _, _, _ in data])
maxyear = max([x for _, x, _, _, _, _, _, _, _, _, _ in data])
# minyear = 2010
# maxyear = 2015

max_y = max([max(x, y) for _, _, x, _, _, _, _, _, y, _, _ in data])
max_y = 25000
min_y = 0

sys.stderr.write("%d\n" % (minyear))
sys.stderr.write("%d\n" % (maxyear))

ar = area.T(size = size,
            x_range = (minyear, maxyear),
            x_axis = axis.X(format="%d", label="Year",
                            tic_len = 4,
                            tic_interval = 2,
                          ),
            # # x_axis2 = axis.X(label=None,
            # #                  format=lambda x: "",
            # #                  offset = height,
            # #                  draw_tics_above = True,
            # #                  tic_len = -4,
            # #                  minor_tic_len = -2,
            # #                  tic_label_offset = (0, 7),
            # #                  tic_interval=gen_interval(5),
            # #                  minor_tic_interval=gen_interval(1)),
            # x_grid_style = None,
            y_range = (min_y, max_y),
            y_axis = axis.Y(label="Count",
                            # format="%d",
                            format=lambda x: locale.format("%d", x, grouping=True),
                            tic_len = 4,
                            tic_label_offset = (-4, 2),
                            tic_interval=gen_interval(5000)
                          ),
            y_grid_style = None,
            legend=legend.T(loc=[14,93]),
            )

plotdata_ct = [[x, y] for _, x, _, _, _, _, _, _, _, _, y in data]
plotdata_cu = [[x, y] for _, x, y, _, _, _, _, _, _, _, _ in data]
plotdata_cv = [[x, y] for _, x, _, _, _, _, _, _, y, _, _ in data]
sys.stderr.write("%s\n" % (plotdata_ct))
sys.stderr.write("%s\n" % (plotdata_cu))
sys.stderr.write("%s\n" % (plotdata_cv))
plot_ct = line_plot.T(data=plotdata_ct, label="C Files")
plot_cu = line_plot.T(data=plotdata_cu, label="Compilation Units")
plot_cv = line_plot.T(data=plotdata_cv, label="Configuration Variables")
ar.add_plot(plot_ct, plot_cu, plot_cv)
# ar.add_plot(line_plot.T(data=[[x, y] for _, x, y, _, _, _, _, _, _, _ in data]))
# ar.add_plot(line_plot.T(data=[[x, y] for _, x, _, y, _, _, _, _, _, _ in data]))
# ar.add_plot(line_plot.T(data=[[x, y] for _, x, _, _, y, _, _, _, _, _ in data]))
# ar.add_plot(line_plot.T(data=[[x, y] for _, x, _, _, _, y, _, _, _, _ in data]))
# ar.add_plot(line_plot.T(data=[[x, y] for _, x, _, _, _, _, y, _, _, _ in data]))
# ar.add_plot(line_plot.T(data=[[x, y] for _, x, _, _, _, _, _, y, _, _ in data]))
# ar.add_plot(line_plot.T(data=[[x, y] for _, x, _, _, _, _, _, _, y, _ in data]))
# ar.add_plot(line_plot.T(data=[[x, y] for _, x, _, _, _, _, _, _, _, y in data]))

ar.draw()
