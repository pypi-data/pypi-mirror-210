"""
OP2 parser based on Steve Doyle OP2
https://pynastran-git.readthedocs.io/en/latest/quick_start/op2_demo_numpy1.html
"""


import logging
import os
from collections import namedtuple

import numpy as np
import pandas as pd
from pyNastran.op2.op2 import read_op2
from pyNastran.utils import object_attributes, object_methods

from mystran_validation.parsers import subset

Resmap = namedtuple(
    "Result",
    ["attr", "discard", "index"],
    defaults=[["Type"], ["SubcaseID", "ElementID", "NodeID"]],
)


# -----------------------------------------------------------------------------
# General settings for accessing one OP2 result
RESMAP = {"reactions": Resmap(attr="spc_forces")}

# pynastran 2 femap-neutral-parser headers
HEADERS = {"fx": "t1", "fy": "t2", "fz": "t3", "mx": "r1", "my": "r2", "mz": "r3"}


class Parser:
    """ """

    def __init__(self, fpath, mode="nx"):
        self.op2 = read_op2(fpath, build_dataframe=False, debug=False, mode=mode)

    def _process(self, attribute, raw=False, **levels):
        """retrive OP2 attribute throughout all the LCIDS"""
        lcids = {}
        predef = RESMAP.get(
            attribute,
            Resmap(
                attr=attribute,
                discard=["Type"],
                index=["SubcaseID", "ElementID", "NodeID"],
            ),
        )
        attr = getattr(self.op2, predef.attr)
        for lcid, data in attr.items():
            data.build_dataframe()
            lcids[lcid] = data.data_frame
        if len(lcids) == 0:
            return
        df = pd.concat(lcids, names=["SubcaseID"])
        if raw:
            return df
        df.reset_index(inplace=True)
        # ---------------------------------------------------------------------
        # discard unwanted columns
        discard = predef.discard + [c for c in df.columns if c.startswith("level_")]
        discard = [c for c in discard if c in df.columns]
        df = df.drop(columns=discard)
        # ---------------------------------------------------------------------
        # set index
        index = predef.index
        if index is None:
            index = ["SubcaseID", "ElementID", "NodeID"]
        index = [i for i in index if i in df.columns]
        df = df.set_index(index)
        df = df.rename(columns=HEADERS)
        return df

    def get(self, vector, raw=False, **levels):
        # if vector == "reactions":
        #     breakpoint()
        df = self._process(vector, raw=raw)
        if levels:
            df = subset(df, **levels)
        return df
