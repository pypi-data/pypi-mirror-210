# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cassandra.metadata import maybe_escape_name
from cqlshlib import helptopics
from cqlshlib.cqlhandling import CqlParsingRuleSet, Hint
import traceback
import cassandra


def print_recreate_keyspace(self, ksdef, out):
    out.write(ksdef.export_as_string())
    out.write('called from a diff file')
    out.write("\n")

def print_recreate_columnfamily(self, ksname, cfname, out):
    """
    Output CQL commands which should be pasteable back into a CQL session
        to recreate the given table.
        Writes output to the given out stream.
    """
    out.write(self.get_table_meta(ksname, cfname).export_as_string())
    out.write("\n")

def get_keyspace_names(self):
        return list(self.conn.metadata.keyspaces.keys())

def get_columnfamily_names(self, ksname=None):
        if ksname is None:
            ksname = self.current_keyspace

        return list(self.get_keyspace_meta(ksname).tables.keys())