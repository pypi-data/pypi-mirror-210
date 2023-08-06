#  Copyright 2022 The FeatHub Authors
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from pyflink.table import (
    TableResult,
    Table as NativeFlinkTable,
    TableDescriptor as NativeFlinkTableDescriptor,
)

from feathub.processors.flink.table_builder.source_sink_utils_common import (
    get_schema_from_table,
)


def insert_into_print_sink(table: NativeFlinkTable) -> TableResult:
    return table.execute_insert(
        NativeFlinkTableDescriptor.for_connector("print")
        .schema(get_schema_from_table(table))
        .build()
    )
